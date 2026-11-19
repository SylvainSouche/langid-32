#!/usr/bin/env python3
"""Run the three balanced JQL-Edu regression heads on a langid-32 Parquet sample.

Output CSV columns are exactly: id, language, ratings.
The ratings cell is a JSON object containing the three independent head scores.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
from huggingface_hub import hf_hub_download
from transformers import AutoModel, AutoTokenizer

EMBEDDER_ID = "Snowflake/snowflake-arctic-embed-m-v2.0"
HEAD_REPO = "JQL-AI/JQL-Edu-Heads"
HEADS = {
    "gemma": "checkpoints/edu-gemma-snowflake-balanced.ckpt",
    "mistral": "checkpoints/edu-mistral-snowflake-balanced.ckpt",
    "llama": "checkpoints/edu-llama-snowflake-balanced.ckpt",
}


class RegressionHead(nn.Module):
    """Architecture from JQL-AI/JQL-Annotation-Pipeline."""
    def __init__(self, input_dim: int = 768, hidden_dim: int = 1000):
        super().__init__()
        self.layer1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        return self.layer2(self.relu(self.layer1(x)))


def load_head(path: str, device: torch.device) -> nn.Module:
    model = RegressionHead()
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    state = checkpoint.get("state_dict", checkpoint)
    # Lightning checkpoints from the upstream project use these unprefixed keys.
    model.load_state_dict(state, strict=True)
    return model.to(device).eval()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path, help="Input Parquet")
    ap.add_argument("--output", required=True, type=Path, help="Output CSV")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--max-length", type=int, default=8192)
    ap.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default="auto")
    ap.add_argument("--max-rows", type=int, default=0, help="Optional smoke-test row limit")
    ap.add_argument("--head-repo", default=HEAD_REPO)
    args = ap.parse_args()

    if args.batch_size < 1:
        raise SystemExit("--batch-size must be positive")
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
    if frame.empty:
        raise SystemExit("Input Parquet contains no rows")
    if frame[["id", "lang", "sentence"]].isna().any().any():
        raise SystemExit("Input contains null id/lang/sentence values")

    # float32 is the portable CPU/MPS baseline. The model card's published
    # embedding recipe is CLS pooling followed by L2 normalization.
    dtype = torch.float32
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDER_ID)
    embedder = AutoModel.from_pretrained(
        EMBEDDER_ID,
        trust_remote_code=True,
        torch_dtype=dtype,
        add_pooling_layer=False,
    ).to(device).eval()

    heads = {}
    for name, filename in HEADS.items():
        checkpoint_path = hf_hub_download(repo_id=args.head_repo, filename=filename)
        heads[name] = load_head(checkpoint_path, device)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "language", "ratings"])
        writer.writeheader()
        texts = frame["sentence"].astype(str).tolist()
        ids = frame["id"].astype(str).tolist()
        languages = frame["lang"].astype(str).tolist()

        for start in range(0, len(texts), args.batch_size):
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
                ratings = {name: round(float(batch_scores[name][offset]), 6)
                           for name in ("gemma", "mistral", "llama")}
                writer.writerow({
                    "id": row_id,
                    "language": lang,
                    "ratings": json.dumps(ratings, separators=(",", ":")),
                })
            stream.flush()
            print(f"Scored {min(start + len(batch_texts), len(texts))}/{len(texts)}",
                  flush=True)

    print(f"Wrote {len(texts)} ratings to {args.output}")


if __name__ == "__main__":
    main()
