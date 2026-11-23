#!/usr/bin/env python3
"""Audit/count locally committed Tatoeba per-language export archives.

Reads compressed archives in data/tatoeba/<iso639-3> and writes aggregate
counts only; sentence text is never copied into the report.
"""
from __future__ import annotations

import bz2
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("data/tatoeba")
OUT = Path("reports/tatoeba-repository-audit.json")


def inspect(path: Path, kind: str, expected_code: str) -> dict:
    digest = hashlib.sha256()
    row_count = malformed = 0
    ids: set[str] = set()
    duplicate_ids = 0
    languages: Counter[str] = Counter()
    wrong_language = 0
    with path.open("rb") as raw:
        for block in iter(lambda: raw.read(1024 * 1024), b""):
            digest.update(block)
    with bz2.open(path, "rt", encoding="utf-8", errors="strict", newline="") as stream:
        for fields in csv.reader(stream, delimiter="\t"):
            if not fields or all(not field for field in fields):
                continue
            row_count += 1
            minimum = {"CC0": 4, "base": 2, "detailed": 6}[kind]
            if len(fields) < minimum:
                malformed += 1
                continue
            sentence_id = fields[0]
            if not sentence_id.isdigit():
                malformed += 1
                continue
            if sentence_id in ids:
                duplicate_ids += 1
            ids.add(sentence_id)
            if kind in ("CC0", "detailed"):
                code = fields[1]
                languages[code] += 1
                if code != expected_code:
                    wrong_language += 1
    return {
        "file": str(path),
        "kind": kind,
        "expected_language": expected_code,
        "compressed_bytes": path.stat().st_size,
        "compressed_sha256": digest.hexdigest(),
        "rows": row_count,
        "unique_sentence_ids": len(ids),
        "duplicate_sentence_ids": duplicate_ids,
        "malformed_rows": malformed,
        "wrong_language_rows": wrong_language,
        "language_counts": dict(sorted(languages.items())),
        "status": "ok" if not malformed and not wrong_language else "review",
    }


def main() -> None:
    reports = []
    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        code = folder.name
        for kind, suffix in (
            ("CC0", "_sentences_CC0.tsv.bz2"),
            ("base", "_sentences_base.tsv.bz2"),
            ("detailed", "_sentences_detailed.tsv.bz2"),
        ):
            path = folder / f"{code}{suffix}"
            if path.exists():
                reports.append(inspect(path, kind, code))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "repository_path": str(ROOT),
        "files_found": len(reports),
        "files": reports,
        "totals_by_kind": {
            kind: {
                "files": sum(r["kind"] == kind for r in reports),
                "rows": sum(r["rows"] for r in reports if r["kind"] == kind),
                "unique_sentence_ids": sum(r["unique_sentence_ids"] for r in reports if r["kind"] == kind),
                "malformed_rows": sum(r["malformed_rows"] for r in reports if r["kind"] == kind),
                "wrong_language_rows": sum(r["wrong_language_rows"] for r in reports if r["kind"] == kind),
            }
            for kind in ("CC0", "base", "detailed")
        },
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["totals_by_kind"], indent=2))
    for item in reports:
        print(f'{item["kind"]:8} {item["expected_language"]:3} rows={item["rows"]:>10,} unique={item["unique_sentence_ids"]:>10,} malformed={item["malformed_rows"]} wrong_lang={item["wrong_language_rows"]} {item["status"]}')
    if any(r["status"] != "ok" for r in reports):
        raise SystemExit("Tatoeba archive audit found malformed or cross-language rows")


if __name__ == "__main__":
    main()
