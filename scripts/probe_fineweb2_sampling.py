#!/usr/bin/env python3
"""Measure bounded FineWeb2 row-group reads and inspect candidate quality.

No document text is written to disk. The report contains aggregate diagnostics
only. Uses DuckDB's HTTP logging to count bytes returned by GET requests.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import unicodedata
import urllib.parse
from collections import Counter
from pathlib import Path

DATASET = "HuggingFaceFW/fineweb-2"
REVISION = "v2.1.0"
SHARDS = {
    "es": ("spa_Latn", "data/spa_Latn/train/000_00000.parquet"),
    "tr": ("tur_Latn", "data/tur_Latn/train/000_00000.parquet"),
}
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?。！？؟։።])\s+|(?<=[。！？])")


def clean(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def sentence_count(text: str) -> int:
    return sum(1 for part in SENTENCE_BOUNDARY.split(text) if len(clean(part)) >= 20)


def http_bytes(connection) -> dict:
    try:
        rows = connection.execute(
            "SELECT request.type, response.status, response.headers "
            "FROM duckdb_logs_parsed('HTTP')"
        ).fetchall()
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    requests = []
    total = 0
    for method, status, headers in rows:
        headers = headers or {}
        length = headers.get("Content-Length") or headers.get("content-length")
        try:
            size = int(length) if length is not None else 0
        except (TypeError, ValueError):
            size = 0
        if str(method).upper() == "GET":
            total += size
        requests.append({"method": method, "status": status, "content_length": size})
    return {
        "available": True,
        "request_count": len(requests),
        "get_count": sum(1 for row in requests if str(row["method"]).upper() == "GET"),
        "get_content_length_bytes": total,
        "requests": requests,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rows-per-shard", type=int, default=5000)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if args.rows_per_shard < 1:
        parser.error("--rows-per-shard must be positive")

    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute("CALL enable_logging('HTTP', storage='memory')")
    report = {
        "probe_version": "0.2",
        "dataset": DATASET,
        "revision": REVISION,
        "duckdb_version": con.execute("SELECT version()").fetchone()[0],
        "method": "Parquet metadata inspection, then one deterministic row-group sample; HTTP GET Content-Length totals",
        "shards": {},
    }

    for language, (subset, path) in SHARDS.items():
        url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{path}"
        escaped = url.replace("'", "''")
        item = {"subset": subset, "path": path}

        con.execute("CALL truncate_duckdb_logs()")
        try:
            metadata = con.execute(
                "SELECT row_group_id, max(row_group_num_rows) AS rows, "
                "sum(total_compressed_size) FILTER (WHERE path_in_schema='text') AS text_bytes "
                f"FROM parquet_metadata('{escaped}') "
                "GROUP BY row_group_id ORDER BY row_group_id"
            ).fetchall()
            item["row_group_count"] = len(metadata)
            item["row_groups"] = [
                {"id": int(row[0]), "rows": int(row[1]), "text_compressed_bytes": int(row[2] or 0)}
                for row in metadata
            ]
            item["metadata_http"] = http_bytes(con)
        except Exception as exc:
            item["metadata_error"] = f"{type(exc).__name__}: {exc}"
            report["shards"][language] = item
            continue

        if not metadata:
            report["shards"][language] = item
            continue

        # Select a middle row group rather than the first rows in the file.
        selected = metadata[len(metadata) // 2]
        row_group_id = int(selected[0])
        item["selected_row_group"] = row_group_id
        item["selected_row_group_rows"] = int(selected[1])
        item["selected_text_compressed_bytes"] = int(selected[2] or 0)

        con.execute("CALL truncate_duckdb_logs()")
        try:
            schema = con.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{escaped}')"
            ).fetchall()
            item["schema_columns"] = [row[0] for row in schema]
            has_row_group_virtual = con.execute(
                "SELECT count(*) FROM duckdb_columns() "
                "WHERE column_name='file_row_group_number'"
            ).fetchone()[0] > 0
            # Probe support directly: virtual columns are available in DuckDB 2.0+.
            try:
                con.execute(
                    f"SELECT file_row_group_number FROM read_parquet('{escaped}') LIMIT 0"
                )
                has_row_group_virtual = True
            except Exception:
                has_row_group_virtual = False
            if not has_row_group_virtual:
                item["sample_error"] = "DuckDB lacks file_row_group_number; row-group pruning not available"
                item["sample_http"] = http_bytes(con)
                report["shards"][language] = item
                continue

            cursor = con.execute(
                "SELECT text, id, url, date, dump, language_score, language_script, "
                "minhash_cluster_size FROM read_parquet('" + escaped + "') "
                f"WHERE file_row_group_number = {row_group_id} LIMIT {args.rows_per_shard}"
            )
            lengths = []
            domains = set()
            scores = []
            scripts = Counter()
            valid_texts = 0
            sentence_candidates = 0
            chars = Counter()
            for batch in iter(lambda: cursor.fetchmany(500), []):
                for text, doc_id, source_url, date, dump, score, script, cluster_size in batch:
                    text = clean(text or "")
                    lengths.append(len(text))
                    if text:
                        valid_texts += 1
                        sentence_candidates += sentence_count(text)
                    if source_url:
                        host = urllib.parse.urlparse(source_url).hostname
                        if host:
                            domains.add(host.lower())
                    if score is not None:
                        scores.append(float(score))
                    if script:
                        scripts[str(script)] += 1
                    for char in text:
                        if char.isalpha():
                            chars[unicodedata.name(char, "UNKNOWN").split(" ")[0]] += 1

            item["sampled_rows"] = len(lengths)
            item["nonempty_text_rows"] = valid_texts
            item["distinct_hostnames"] = len(domains)
            item["sentence_candidates_min_20_chars"] = sentence_candidates
            item["text_length_chars"] = {
                "min": min(lengths) if lengths else 0,
                "median": int(statistics.median(lengths)) if lengths else 0,
                "p95": sorted(lengths)[int((len(lengths) - 1) * 0.95)] if lengths else 0,
                "max": max(lengths) if lengths else 0,
            }
            item["language_score"] = {
                "min": min(scores) if scores else None,
                "median": statistics.median(scores) if scores else None,
                "p10": sorted(scores)[int((len(scores) - 1) * 0.10)] if scores else None,
            }
            item["language_script_counts"] = dict(scripts)
            item["unicode_letter_name_prefixes"] = dict(chars.most_common(12))
            item["sample_http"] = http_bytes(con)
        except Exception as exc:
            item["sample_error"] = f"{type(exc).__name__}: {exc}"
            item["sample_http"] = http_bytes(con)
        report["shards"][language] = item

    con.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
