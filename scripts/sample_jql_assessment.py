#!/usr/bin/env python3
"""Stream every filtered acquisition-pool record into the full JQL Parquet."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path


def sentence_id(language: str, source: str, sentence: str) -> str:
    return hashlib.sha256("\0".join((language, source, sentence)).encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--all", action="store_true", help="Required: sampling is forbidden")
    parser.add_argument("--batch-size", type=int, default=8192)
    args = parser.parse_args()
    if not args.all:
        parser.error("--all is mandatory")
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    if not args.input.is_file():
        parser.error(f"missing input: {args.input}")

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("Install pyarrow") from exc

    schema = pa.schema([
        ("id", pa.string()), ("lang", pa.string()), ("sentence", pa.string()),
        ("source", pa.string()), ("source-variant", pa.string()),
    ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    duplicate_db = args.output.with_suffix(args.output.suffix + ".ids.sqlite")
    duplicate_db.unlink(missing_ok=True)
    counts: Counter[tuple[str, str]] = Counter()
    batch: list[dict[str, str]] = []
    rows = 0
    writer = None

    try:
        with sqlite3.connect(duplicate_db) as db:
            db.execute("CREATE TABLE ids (id TEXT PRIMARY KEY)")
            writer = pq.ParquetWriter(args.output, schema, compression="zstd")
            with args.input.open(encoding="utf-8") as stream:
                for line_number, line in enumerate(stream, 1):
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"{args.input}:{line_number}: {exc}") from exc
                    language = str(row.get("language", "")).strip().lower()
                    source = str(row.get("source", "")).strip()
                    sentence = " ".join(
                        unicodedata.normalize("NFC", str(row.get("text", ""))).split()
                    )
                    if not language or not source or not sentence:
                        raise ValueError(
                            f"{args.input}:{line_number}: missing language/source/text"
                        )
                    ident = sentence_id(language, source, sentence)
                    try:
                        db.execute("INSERT INTO ids(id) VALUES (?)", (ident,))
                    except sqlite3.IntegrityError as exc:
                        raise ValueError(
                            f"{args.input}:{line_number}: duplicate assessment ID {ident}"
                        ) from exc
                    provenance = row.get("provenance")
                    if not isinstance(provenance, dict):
                        provenance = {}
                    original_source = str(provenance.get("source_original_name") or source).strip()
                    if not original_source:
                        raise ValueError(
                            f"{args.input}:{line_number}: missing original source identity"
                        )
                    batch.append({
                        "id": ident, "lang": language, "sentence": sentence,
                        "source": source, "source-variant": original_source,
                    })
                    counts[(language, original_source)] += 1
                    rows += 1
                    if len(batch) >= args.batch_size:
                        writer.write_table(pa.Table.from_pylist(batch, schema=schema))
                        batch.clear()
            if batch:
                writer.write_table(pa.Table.from_pylist(batch, schema=schema))
            db.commit()
        writer.close()
        writer = None
        summary = {
            "status": "full_filtered_acquisition_pool",
            "sampling": False,
            "rows": rows,
            "unique_ids": rows,
            "source_identity": "provenance.source_original_name, falling back to source only when no family mapping exists",
            "final_30k_selection": "deferred_pending_user_review",
            "counts_by_language_source": [
                {"language": language, "source": source, "count": count}
                for (language, source), count in sorted(counts.items())
            ],
        }
        args.summary.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"status": summary["status"], "rows": rows}, indent=2))
    except Exception:
        if writer is not None:
            writer.close()
        args.output.unlink(missing_ok=True)
        args.summary.unlink(missing_ok=True)
        raise
    finally:
        duplicate_db.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
