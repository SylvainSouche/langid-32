#!/usr/bin/env python3
"""Stream a full JQL assessment Parquet into deterministic, balanced row shards."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config


COLUMNS = ("id", "lang", "sentence")


def shard_sizes(rows: int, shards: int) -> list[int]:
    if rows < 1 or shards < 1 or rows < shards:
        raise ValueError("assessment rows and shard count must be positive, with at least one row per shard")
    base, extra = divmod(rows, shards)
    return [base + (1 if index < extra else 0) for index in range(shards)]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--shards", type=int, default=None)
    ap.add_argument("--batch-rows", type=int, default=8192)
    ap.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    args = ap.parse_args()
    args.shards = args.shards if args.shards is not None else load_config(args.config)["jql"]["shard_count"]
    if args.batch_rows < 1:
        ap.error("--batch-rows must be positive")
    if not args.input.is_file():
        ap.error(f"Input not found: {args.input}")

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("Install pyarrow") from exc

    parquet = pq.ParquetFile(args.input)
    rows = int(parquet.metadata.num_rows)
    try:
        sizes = shard_sizes(rows, int(args.shards))
    except ValueError as exc:
        ap.error(str(exc))
    schema = pa.schema([parquet.schema_arrow.field(name) for name in COLUMNS])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for old in args.output_dir.glob("shard-*.parquet"):
        old.unlink()
    (args.output_dir / "manifest.json").unlink(missing_ok=True)
    state_path = args.output_dir / ".ids.sqlite"
    state_path.unlink(missing_ok=True)

    writers = []
    shard_paths = [args.output_dir / f"shard-{index:02d}.parquet" for index in range(args.shards)]
    written = [0] * args.shards
    first_ids: list[str | None] = [None] * args.shards
    last_ids: list[str | None] = [None] * args.shards
    current_shard = 0
    successful = False
    db = sqlite3.connect(state_path)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE ids (id TEXT PRIMARY KEY) WITHOUT ROWID")
    try:
        writers = [
            pq.ParquetWriter(path, schema, compression="zstd", use_dictionary=True)
            for path in shard_paths
        ]
        for batch in parquet.iter_batches(batch_size=args.batch_rows, columns=list(COLUMNS)):
            if any(batch.column(batch.schema.get_field_index(name)).null_count for name in COLUMNS):
                raise SystemExit("Assessment contains null id/lang/sentence values")
            ids = [str(value) for value in batch.column(batch.schema.get_field_index("id")).to_pylist()]
            if any(not value for value in ids):
                raise SystemExit("Assessment contains an empty ID")
            cursor = db.executemany(
                "INSERT OR IGNORE INTO ids(id) VALUES (?)",
                [(value,) for value in ids],
            )
            if cursor.rowcount != len(ids):
                raise SystemExit("Assessment IDs must be globally unique")
            table = pa.Table.from_batches([batch], schema=schema)
            offset = 0
            while offset < table.num_rows:
                while current_shard < args.shards and written[current_shard] >= sizes[current_shard]:
                    current_shard += 1
                if current_shard >= args.shards:
                    raise RuntimeError("Shard row targets were exceeded")
                take = min(sizes[current_shard] - written[current_shard], table.num_rows - offset)
                piece = table.slice(offset, take)
                writers[current_shard].write_table(piece, row_group_size=args.batch_rows)
                if first_ids[current_shard] is None:
                    first_ids[current_shard] = ids[offset]
                last_ids[current_shard] = ids[offset + take - 1]
                written[current_shard] += take
                offset += take
            db.commit()
        if written != sizes:
            raise RuntimeError(f"Shard row totals mismatch: expected={sizes}, actual={written}")
        for writer in writers:
            writer.close()
        writers.clear()

        manifest = {
            "schema_version": 1,
            "input": args.input.name,
            "input_sha256": sha256(args.input),
            "rows": rows,
            "shards": args.shards,
            "files": [],
        }
        for index, path in enumerate(shard_paths):
            manifest["files"].append({
                "index": index,
                "file": path.name,
                "rows": written[index],
                "first_id": first_ids[index],
                "last_id": last_ids[index],
                "sha256": sha256(path),
            })
        (args.output_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        successful = True
        print(json.dumps({
            "rows": rows,
            "shards": args.shards,
            "shard_rows": written,
            "input_sha256": manifest["input_sha256"],
        }))
    finally:
        for writer in writers:
            writer.close()
        db.close()
        state_path.unlink(missing_ok=True)
        if not successful:
            for path in shard_paths:
                path.unlink(missing_ok=True)
            (args.output_dir / "manifest.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
