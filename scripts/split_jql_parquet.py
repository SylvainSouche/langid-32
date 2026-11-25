#!/usr/bin/env python3
"""Split a JQL assessment Parquet into deterministic, balanced row shards."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config

import pyarrow.parquet as pq


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--shards", type=int, default=None)
    ap.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    args = ap.parse_args()
    args.shards = args.shards if args.shards is not None else load_config(args.config)["jql"]["shard_count"]
    if args.shards < 1:
        ap.error("--shards must be at least 1")
    if not args.input.is_file():
        ap.error(f"Input not found: {args.input}")

    table = pq.read_table(args.input, columns=["id", "lang", "sentence"])
    rows = table.num_rows
    if rows == 0:
        ap.error("Input Parquet is empty")
    ids = table.column("id").to_pylist()
    if any(value is None for value in ids) or len(set(ids)) != rows:
        ap.error("Input IDs must be non-null and unique")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    base, extra = divmod(rows, args.shards)
    manifest = {
        "schema_version": 1,
        "input": args.input.name,
        "input_sha256": sha256(args.input),
        "rows": rows,
        "shards": args.shards,
        "files": [],
    }
    start = 0
    for index in range(args.shards):
        count = base + (1 if index < extra else 0)
        shard = table.slice(start, count)
        name = f"shard-{index:02d}.parquet"
        path = args.output_dir / name
        pq.write_table(shard, path, compression="zstd", use_dictionary=True)
        manifest["files"].append({
            "index": index, "file": name, "rows": count,
            "first_id": ids[start] if count else None,
            "last_id": ids[start + count - 1] if count else None,
            "sha256": sha256(path),
        })
        start += count

    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"rows": rows, "shards": args.shards,
                      "shard_rows": [x["rows"] for x in manifest["files"]]}))


if __name__ == "__main__":
    main()
