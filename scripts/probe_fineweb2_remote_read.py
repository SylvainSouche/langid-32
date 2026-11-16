#!/usr/bin/env python3
"""Safely probe HTTP range support and a tiny DuckDB query on FineWeb2 shards.

The probe checks HTTP Range before DuckDB is allowed to touch a shard. It
stores no document text, only schema, row lengths and request diagnostics.
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

DATASET = "HuggingFaceFW/fineweb-2"
REVISION = "v2.1.0"
SHARDS = {
    "spa_Latn": "data/spa_Latn/train/000_00000.parquet",
    "tur_Latn": "data/tur_Latn/train/000_00000.parquet",
}


def probe_range(url: str, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "langid-32 FineWeb2 bounded-read probe/0.1",
            "Range": "bytes=0-1023",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            sample = response.read(1024)
            return {
                "status": response.status,
                "content_range": response.headers.get("Content-Range"),
                "content_length": response.headers.get("Content-Length"),
                "accept_ranges": response.headers.get("Accept-Ranges"),
                "bytes_read": len(sample),
                "parquet_magic": sample[:4].decode("ascii", errors="replace"),
                "final_url_host": urllib.request.urlparse(response.geturl()).netloc,
                "range_supported": response.status == 206 and
                    response.headers.get("Content-Range", "").startswith("bytes 0-"),
            }
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "error": str(exc), "range_supported": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    try:
        import duckdb
    except ImportError as exc:
        raise SystemExit("Install duckdb to run this isolated probe") from exc

    report = {
        "dataset": DATASET,
        "revision": REVISION,
        "method": "HTTP Range preflight followed by DuckDB httpfs; no full-shard download intended",
        "shards": {},
    }
    con = duckdb.connect()
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")

    for subset, path in SHARDS.items():
        url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{path}"
        item = {"path": path, "range_preflight": probe_range(url, args.timeout)}
        if not item["range_preflight"].get("range_supported"):
            item["duckdb"] = {"skipped": "Server did not confirm HTTP 206 range response"}
            report["shards"][subset] = item
            continue

        escaped = url.replace("'", "''")
        try:
            schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{escaped}')").fetchall()
            item["duckdb"] = {
                "schema": [{"name": row[0], "type": row[1]} for row in schema],
            }
            # LIMIT 1 deliberately projects only text and ID; never return or persist the text.
            row = con.execute(
                f"SELECT length(text), length(id) FROM read_parquet('{escaped}') LIMIT 1"
            ).fetchone()
            item["duckdb"]["sample_row_lengths"] = list(row) if row else None
            item["duckdb"]["query_ok"] = row is not None
        except Exception as exc:
            item["duckdb"] = {"query_ok": False, "error": f"{type(exc).__name__}: {exc}"}
        report["shards"][subset] = item

    con.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
