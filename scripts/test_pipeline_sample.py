#!/usr/bin/env python3
"""Synthetic end-to-end smoke test for acquisition, JQL export, sharding and pruning."""
from __future__ import annotations

import csv
from collections import Counter
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ["hr", "fi", "el", "mt", "sl", "is"]


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="langid32-sample-") as tmp:
        root = Path(tmp)
        raw = root / "raw"
        pool = root / "pool"
        shards = root / "shards"
        ratings = root / "ratings"
        quality = root / "quality.csv"
        raw.mkdir()
        ratings.mkdir()
        source_file = raw / "sample.jsonl"

        with source_file.open("w", encoding="utf-8") as stream:
            for lang in LANGUAGES:
                for index in range(4):
                    row = {
                        "text": f"Public institutions published report number {index} for language {lang}.",
                        "language": lang,
                        "source": "leipzig_news",
                        "source_release": "synthetic-smoke-test",
                        "group_id": f"{lang}-{index}",
                        "licence_id": "synthetic-test-only",
                        "text_origin": "synthetic",
                        "provenance": {"privacy_flags": []},
                    }
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                duplicate = dict(row)
                duplicate["group_id"] = f"{lang}-duplicate"
                stream.write(json.dumps(duplicate, ensure_ascii=False) + "\n")
                pii = dict(row)
                pii["group_id"] = f"{lang}-pii"
                pii["text"] = f"Contact sample.person{lang}@example.org for the public report."
                stream.write(json.dumps(pii, ensure_ascii=False) + "\n")

        run("scripts/build_acquisition_pool.py", "--input-root", str(raw),
            "--output-dir", str(pool))
        manifest = json.loads((pool / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["retained_rows"] == 24, manifest
        assert len(manifest["retained_by_source_language"]) == 6, manifest
        assert all(item["count"] == 4 for item in manifest["retained_by_source_language"])
        reasons = Counter()
        for item in manifest["rejected_by_source_language_reason"]:
            reasons[item["reason"]] += item["count"]
        assert reasons.get("duplicate_within_original_source_language") == 6, reasons
        assert reasons.get("email") == 6, reasons

        assessment = root / "assessment.parquet"
        assessment_summary = root / "assessment.json"
        run("scripts/sample_jql_assessment.py", "--input", str(pool / "records.jsonl"),
            "--output", str(assessment), "--summary", str(assessment_summary), "--all")
        table = pq.read_table(assessment)
        assert table.num_rows == 24
        assert table.schema.names == ["id", "lang", "sentence", "source", "source-variant"]
        assert len(set(table.column("id").to_pylist())) == 24

        run("scripts/split_jql_parquet.py", "--input", str(assessment),
            "--output-dir", str(shards), "--shards", "3")
        shard_manifest = json.loads((shards / "manifest.json").read_text(encoding="utf-8"))
        assert [item["rows"] for item in shard_manifest["files"]] == [8, 8, 8]

        rows = table.to_pylist()
        with (ratings / "ratings.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["id", "language", "ratings"])
            writer.writeheader()
            for index, row in enumerate(rows):
                writer.writerow({
                    "id": row["id"],
                    "language": row["lang"],
                    "ratings": json.dumps({
                        "gemma": float(index),
                        "mistral": float(index * 2 + 1),
                        "llama": float(48 - index),
                    }),
                })
        with quality.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream, fieldnames=["id", "initial_capitalization", "terminal_punctuation"]
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({
                    "id": row["id"],
                    "initial_capitalization": "true",
                    "terminal_punctuation": "true",
                })

        full_csv = root / "full.csv"
        pruned_csv = root / "pruned.csv"
        pruning_summary = root / "pruning.json"
        run("scripts/merge_jql_ratings.py", "--input", str(assessment),
            "--ratings-dir", str(ratings), "--quality", str(quality),
            "--output-csv", str(full_csv), "--include-text",
            "--pruned-output-csv", str(pruned_csv),
            "--pruned-output-parquet", str(root / "pruned.parquet"),
            "--pruning-summary", str(pruning_summary))
        full = pd.read_csv(full_csv)
        pruned = pd.read_csv(pruned_csv)
        report = json.loads(pruning_summary.read_text(encoding="utf-8"))
        assert len(full) == 24
        assert len(pruned) == 18
        assert report["input_rows"] == 24 and report["pruned_rows"] == 6
        assert report["retained_rows"] == 18
        assert sum(row["count"] for row in report["retained_by_language_source"]) == 18
        assert set(full["lang"]) == set(LANGUAGES)
        assert set(full["source"]) == {"leipzig_news"}
        print(json.dumps({
            "status": "PASS",
            "input_rows": 36,
            "pre_jql_rows": 24,
            "duplicate_rejections": 6,
            "privacy_pattern_rejections": 6,
            "assessment_rows": 24,
            "shard_rows": [8, 8, 8],
            "jql_pruned": 6,
            "jql_retained": 18,
            "languages": LANGUAGES,
        }, indent=2))


if __name__ == "__main__":
    main()
