#!/usr/bin/env python3
"""Add non-filtering JQL-Edu-Heads QA annotations to Leipzig JSONL records.

Every input row is preserved. Scores are sidecar annotations only and never
influence selection, exclusion, ranking, or replacement.
"""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path

import torch
import torch.nn as nn
from huggingface_hub import HfApi, hf_hub_download
from transformers import AutoModel, AutoTokenizer

EMBEDDER_ID = "Snowflake/snowflake-arctic-embed-m-v2.0"
HEAD_REPO = "JQL-AI/JQL-Edu-Heads"
HEADS = {
    "gemma": "checkpoints/edu-gemma-snowflake-balanced.ckpt",
    "mistral": "checkpoints/edu-mistral-snowflake-balanced.ckpt",
    "llama": "checkpoints/edu-llama-snowflake-balanced.ckpt",
}

class RegressionHead(nn.Module):
    def __init__(self, input_dim: int = 768, hidden_dim: int = 1000):
        super().__init__()
        self.layer1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x)))

def row_key(row: dict) -> str:
    p = row.get("provenance") or {}
    return "|".join(str(x or "") for x in (
        row.get("language"), row.get("source"), p.get("data_id"),
        p.get("sentence_id"), row.get("text")
    ))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--max-seconds", type=int, default=3600)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--max-rows", type=int, default=0, help="0 means no row cap")
    ap.add_argument("--max-length", type=int, default=512)
    ap.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default="auto")
    a = ap.parse_args()

    src, dst = Path(a.input), Path(a.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not src.is_file():
        raise SystemExit(f"Input not found: {src}")

    completed = set()
    if dst.exists():
        with dst.open(encoding="utf-8") as f:
            for line in f:
                try: completed.add(row_key(json.loads(line)))
                except Exception: continue

    if a.device == "auto":
        device = "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
    else:
        device = a.device
    if device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requested but CUDA is unavailable")
    if device == "mps" and not (getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()):
        raise SystemExit("--device mps requested but MPS is unavailable")
    dtype = (torch.bfloat16 if device == "cuda" and torch.cuda.is_bf16_supported()
             else (torch.float16 if device == "cuda" else torch.float32))
    print(json.dumps({"event":"initializing","device":device,"dtype":str(dtype),"batch_size":a.batch_size}), flush=True)

    api = HfApi()
    embedder_revision = api.model_info(EMBEDDER_ID).sha
    heads_revision = api.model_info(HEAD_REPO).sha
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDER_ID, revision=embedder_revision)
    embedder = AutoModel.from_pretrained(
        EMBEDDER_ID, revision=embedder_revision, trust_remote_code=True,
        torch_dtype=dtype
    ).to(device).eval()

    models = {}
    for name, filename in HEADS.items():
        checkpoint = hf_hub_download(HEAD_REPO, filename, revision=heads_revision)
        payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
        state = payload.get("state_dict", payload)
        model = RegressionHead()
        model.load_state_dict(state, strict=True)
        models[name] = model.to(device=device, dtype=dtype).eval()

    metadata = {
        "annotator": "JQL-Edu-Heads",
        "annotator_repo": HEAD_REPO,
        "annotator_revision": heads_revision,
        "embedder": EMBEDDER_ID,
        "embedder_revision": embedder_revision,
        "heads": list(HEADS),
        "head_checkpoints": HEADS,
        "score_scale": "raw model regression output; nominal 0-5",
        "selection_effect": "none; annotation only",
    }
    start = time.monotonic()
    rated = 0
    seen = 0
    batch = []
    out = dst.open("a", encoding="utf-8")

    def score(rows):
        nonlocal rated
        texts = [r["text"] for r in rows]
        tokens = tokenizer(
            texts, max_length=a.max_length, padding=True, truncation=True,
            return_tensors="pt"
        ).to(device)
        with torch.inference_mode():
            hidden = embedder(**tokens).last_hidden_state[:, 0]
            hidden = torch.nn.functional.normalize(hidden, p=2, dim=1)
            predictions = {name: model(hidden).float().squeeze(1).cpu().tolist()
                           for name, model in models.items()}
        for i, row in enumerate(rows):
            vals = {name: float(predictions[name][i]) for name in HEADS}
            values = list(vals.values())
            row["jql_edu"] = {
                **metadata,
                "scores": vals,
                "mean": sum(values) / len(values),
                "range": max(values) - min(values),
                "annotated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        out.flush()
        os.fsync(out.fileno())
        rated += len(rows)
        elapsed = time.monotonic() - start
        print(json.dumps({"event":"batch_complete","rated_this_batch":len(rows),
                          "rated_total_this_run":rated,"elapsed_seconds":round(elapsed,1),
                          "rate_per_hour":round(rated*3600/max(elapsed,1),1)}), flush=True)

    try:
        with src.open(encoding="utf-8") as f:
            for line in f:
                if time.monotonic() - start >= a.max_seconds:
                    break
                if a.max_rows and seen >= a.max_rows:
                    break
                seen += 1
                row = json.loads(line)
                if row_key(row) in completed:
                    continue
                if not isinstance(row.get("text"), str) or not row["text"].strip():
                    continue
                batch.append(row)
                if len(batch) >= a.batch_size:
                    score(batch)
                    batch = []
            if batch and time.monotonic() - start < a.max_seconds:
                score(batch)
    finally:
        out.close()

    elapsed = time.monotonic() - start
    summary = {
        **metadata, "input": str(src), "output": str(dst),
        "rows_scanned": seen, "rows_already_annotated": len(completed),
        "rows_rated_this_run": rated, "elapsed_seconds": round(elapsed, 2),
        "rated_per_hour": round(rated * 3600 / max(elapsed, 1), 2),
        "time_limit_seconds": a.max_seconds, "device": device,
        "batch_size": a.batch_size, "max_length": a.max_length,
        "complete_input_scanned": seen == sum(1 for _ in src.open(encoding="utf-8")),
        "all_rows_preserved": True, "scores_are_non_filtering_annotations": True,
    }
    dst.with_name("jql_run_summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"event":"run_summary", **summary}, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
