#!/usr/bin/env python3
"""Run the three balanced JQL-Edu regression heads on a langid-32 Parquet sample.

Output CSV columns are exactly: id, language, ratings.
The ratings cell is a JSON object containing the three independent head scores.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config

import pandas as pd
import torch
import torch.nn as nn
from huggingface_hub import HfApi, hf_hub_download
from transformers import AutoConfig, AutoModel, AutoTokenizer

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(path: Path, manifest: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class RegressionHead(nn.Module):
    """Architecture from JQL-AI/JQL-Annotation-Pipeline."""
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.layer1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x)))


def load_head(path: str, device: torch.device, jql_cfg: dict) -> nn.Module:
    model = RegressionHead(jql_cfg["embedding_dimension"], jql_cfg["head_hidden_dimension"])
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    state = checkpoint.get("state_dict", checkpoint)
    # Lightning checkpoints from the upstream project use these unprefixed keys.
    model.load_state_dict(state, strict=True)
    return model.to(device).eval()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path, help="Input Parquet")
    ap.add_argument("--output", required=True, type=Path, help="Output CSV")
    ap.add_argument("--batch-size", type=int, default=None)
    ap.add_argument("--max-length", type=int, default=None)
    ap.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default="auto")
    ap.add_argument("--max-rows", type=int, default=None, help="Optional smoke-test row limit")
    ap.add_argument("--torch-threads", type=int, default=None, help="CPU intra-op threads")
    ap.add_argument("--max-seconds", type=int, default=None, help="Maximum inference time for this resumable batch")
    ap.add_argument("--resume", action="store_true", help="Append to an existing ratings CSV and skip completed IDs")
    ap.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    ap.add_argument("--head-repo", default=None)
    args = ap.parse_args()
    jql_cfg = load_config(args.config)["jql"]
    args.batch_size = args.batch_size if args.batch_size is not None else jql_cfg["inference_batch_size"]
    args.max_length = args.max_length if args.max_length is not None else jql_cfg["max_token_length"]
    args.torch_threads = args.torch_threads if args.torch_threads is not None else jql_cfg["cpu_torch_threads"]
    args.max_rows = args.max_rows if args.max_rows is not None else jql_cfg["max_rows"]
    args.max_seconds = args.max_seconds if args.max_seconds is not None else int(jql_cfg["max_seconds"])
    args.head_repo = args.head_repo or jql_cfg["head_repository"]
    embedder_id = jql_cfg["embedder_model"]
    head_checkpoints = jql_cfg["head_checkpoints"]
    embedder_revision_requested = str(jql_cfg.get("embedder_revision", "main"))
    head_revision_requested = str(jql_cfg.get("head_repository_revision", "main"))

    if args.batch_size < 1:
        raise SystemExit("--batch-size must be positive")
    if args.torch_threads < 1:
        raise SystemExit("--torch-threads must be positive")
    if args.max_seconds < 1:
        raise SystemExit("--max-seconds must be positive")
    torch.set_num_threads(args.torch_threads)
    if not args.input.is_file():
        raise SystemExit(f"Input not found: {args.input}")

    if args.device == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    else:
        if args.device == "cuda" and not torch.cuda.is_available():
            raise SystemExit("CUDA requested but unavailable")
        if args.device == "mps" and not (
            getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
        ):
            raise SystemExit("MPS requested but unavailable")
        device = torch.device(args.device)

    frame = pd.read_parquet(args.input, columns=["id", "lang", "sentence"])
    if args.max_rows:
        frame = frame.head(args.max_rows)
    input_rows = int(len(frame))
    if frame.empty:
        raise SystemExit("Input Parquet contains no rows")
    if frame[["id", "lang", "sentence"]].isna().any().any():
        raise SystemExit("Input contains null id/lang/sentence values")

    # float32 is the portable CPU/MPS baseline. The model card's published
    # embedding recipe is CLS pooling followed by L2 normalization.
    # Resolve floating references once, then use only immutable commit SHAs for all downloads.
    api = HfApi()
    embedder_revision = api.model_info(embedder_id, revision=embedder_revision_requested).sha
    head_revision = api.model_info(args.head_repo, revision=head_revision_requested).sha
    if not embedder_revision or not head_revision:
        raise SystemExit("Could not resolve immutable Hugging Face model revisions")

    dtype = torch.float32
    tokenizer = AutoTokenizer.from_pretrained(embedder_id, revision=embedder_revision)
    # The Arctic Embed remote implementation otherwise selects an xformers-only
    # memory-efficient attention path. Native PyTorch SDPA works on CPU and MPS.
    config = AutoConfig.from_pretrained(
        embedder_id, trust_remote_code=True, revision=embedder_revision
    )
    config.use_memory_efficient_attention = False
    config.unpad_inputs = False
    embedder = AutoModel.from_pretrained(
        embedder_id,
        config=config,
        trust_remote_code=True,
        revision=embedder_revision,
        torch_dtype=dtype,
        add_pooling_layer=False,
        attn_implementation="sdpa",
    ).to(device).eval()

    heads = {}
    checkpoint_hashes = {}
    for name in jql_cfg["judges"]:
        checkpoint_path = Path(hf_hub_download(
            repo_id=args.head_repo,
            filename=head_checkpoints[name],
            revision=head_revision,
        ))
        checkpoint_hashes[name] = sha256_file(checkpoint_path)
        heads[name] = load_head(str(checkpoint_path), device, jql_cfg)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    provenance = {
        "input_sha256": sha256_file(args.input),
        "models": {
            "embedder_repository": embedder_id,
            "embedder_revision_requested": embedder_revision_requested,
            "embedder_revision_resolved": embedder_revision,
            "head_repository": args.head_repo,
            "head_revision_requested": head_revision_requested,
            "head_revision_resolved": head_revision,
        },
        "head_checkpoint_sha256": checkpoint_hashes,
        "scoring": {
            "judges": list(jql_cfg["judges"]),
            "embedding_dimension": int(jql_cfg["embedding_dimension"]),
            "head_hidden_dimension": int(jql_cfg["head_hidden_dimension"]),
            "max_token_length": args.max_length,
            "inference_batch_size": args.batch_size,
            "dtype": "float32",
            "pooling": "CLS",
            "normalization": "L2",
        },
    }
    if args.resume and args.output.is_file():
        if not manifest_path.is_file():
            raise SystemExit("Cannot resume ratings without their model/input provenance manifest")
        previous_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key, value in provenance.items():
            if previous_manifest.get(key) != value:
                raise SystemExit(f"Resume provenance mismatch for {key}")
    completed_ids = set()
    if args.resume and args.output.is_file():
        with args.output.open(encoding="utf-8", newline="") as existing:
            reader = csv.DictReader(existing)
            if reader.fieldnames != ["id", "language", "ratings"]:
                raise SystemExit("Existing ratings CSV has an unexpected schema")
            for row in reader:
                row_id = str(row["id"])
                if not row_id or row_id in completed_ids:
                    raise SystemExit("Existing ratings CSV contains an empty or duplicate ID")
                scores = json.loads(row["ratings"])
                if set(scores) != set(jql_cfg["judges"]):
                    raise SystemExit(f"Existing ratings row {row_id} is incomplete")
                completed_ids.add(row_id)
        frame = frame.loc[~frame["id"].astype(str).isin(completed_ids)].copy()
    if frame.empty:
        manifest = {**provenance, "schema_version": 1, "input_rows": input_rows,
                    "scored_rows": len(completed_ids), "updated_at": datetime.now(timezone.utc).isoformat()}
        write_manifest(manifest_path, manifest)
        print(f"All requested rows already have ratings in {args.output}")
        return 0

    mode = "a" if args.resume and args.output.is_file() else "w"
    with args.output.open(mode, encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "language", "ratings"])
        if mode == "w":
            writer.writeheader()
        texts = frame["sentence"].astype(str).tolist()
        ids = frame["id"].astype(str).tolist()
        languages = frame["lang"].astype(str).tolist()
        batch_started = time.monotonic()

        for start in range(0, len(texts), args.batch_size):
            if time.monotonic() - batch_started >= args.max_seconds:
                stream.flush()
                os.fsync(stream.fileno())
                manifest = {**provenance, "schema_version": 1,
                            "input_rows": input_rows,
                            "scored_rows": len(completed_ids),
                            "updated_at": datetime.now(timezone.utc).isoformat()}
                write_manifest(manifest_path, manifest)
                print(f"Batch time limit reached; completed {start}/{len(texts)} remaining rows", flush=True)
                raise SystemExit(75)
            batch_texts = texts[start:start + args.batch_size]
            tokens = tokenizer(
                batch_texts,
                max_length=args.max_length,
                padding="longest",
                truncation=True,
                return_tensors="pt",
            ).to(device)
            with torch.inference_mode():
                output = embedder(**tokens)
                embeddings = torch.nn.functional.normalize(
                    output.last_hidden_state[:, 0], p=2, dim=1
                )
                batch_scores = {
                    name: head(embeddings).squeeze(1).detach().cpu().tolist()
                    for name, head in heads.items()
                }

            for offset, (row_id, lang) in enumerate(zip(
                ids[start:start + len(batch_texts)],
                languages[start:start + len(batch_texts)],
            )):
                ratings = {name: round(float(batch_scores[name][offset]), jql_cfg["score_decimal_places"])
                           for name in jql_cfg["judges"]}
                writer.writerow({
                    "id": row_id,
                    "language": lang,
                    "ratings": json.dumps(ratings, separators=(",", ":")),
                })
            stream.flush()
            os.fsync(stream.fileno())
            completed_ids.update(ids[start:start + len(batch_texts)])
            manifest = {**provenance, "schema_version": 1,
                        "input_rows": input_rows,
                        "scored_rows": len(completed_ids),
                        "updated_at": datetime.now(timezone.utc).isoformat()}
            write_manifest(manifest_path, manifest)
            print(f"Scored {min(start + len(batch_texts), len(texts))}/{len(texts)} remaining rows",
                  flush=True)

    print(f"Wrote {len(completed_ids)} ratings to {args.output}")
    return 0


if __name__ == "__main__":
    main()
