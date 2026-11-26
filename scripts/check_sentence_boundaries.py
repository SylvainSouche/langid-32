#!/usr/bin/env python3
"""Flag likely sentence chunks using Unicode-aware capitalization and punctuation."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

# Scripts without upper/lower case: capitalization is not a meaningful test.
CASELESS_LANGUAGES = {"ar", "zh", "ja", "ko"}
# Sentence-final marks used across the project's scripts/languages.
SENTENCE_FINAL = set(".!?…。！？؟۔։।॥՜՞՟;")
CLOSERS = set("\"'”’»›)]}〉》」』】〕〗〙〛")


def capitalization_status(text: str, lang: str) -> str:
    if lang in CASELESS_LANGUAGES:
        return "not_applicable"
    for char in text:
        if char.isupper() or char.islower() or char.istitle():
            return "pass" if char.isupper() or char.istitle() else "fail"
    return "not_applicable"


def punctuation_status(text: str) -> str:
    value = text.rstrip()
    while value and value[-1] in CLOSERS:
        value = value[:-1].rstrip()
    return "pass" if value and value[-1] in SENTENCE_FINAL else "fail"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if not args.input.is_file():
        ap.error(f"Input not found: {args.input}")
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("Install pyarrow: python -m pip install pyarrow") from exc
    parquet = pq.ParquetFile(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    total_rows = 0
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "id", "lang", "initial_capitalization", "terminal_punctuation"
        ])
        writer.writeheader()
        for row_group in range(parquet.num_row_groups):
            table = parquet.read_row_group(
                row_group, columns=["id", "lang", "sentence"]
            )
            for batch in table.to_batches(max_chunksize=8192):
                for row in batch.to_pylist():
                    sentence = str(row["sentence"] or "")
                    lang = str(row["lang"] or "").lower()
                    writer.writerow({
                        "id": str(row["id"]),
                        "lang": lang,
                        "initial_capitalization": capitalization_status(sentence, lang),
                        "terminal_punctuation": punctuation_status(sentence),
                    })
                    total_rows += 1
    if total_rows != parquet.metadata.num_rows:
        raise RuntimeError(
            f"Sentence-boundary diagnostic row mismatch: "
            f"{total_rows} != {parquet.metadata.num_rows}"
        )
    print(f"Flagged {total_rows} sentences: {args.output}")


if __name__ == "__main__":
    main()
