"""Inventory FineWeb2's published language-distribution metadata.

Only the small upstream CSV is downloaded; no Parquet shards or document text
are fetched. Counts are publisher-reported document/word/byte totals, not
usable sentence counts for this project.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

SOURCE_URL = (
    "https://raw.githubusercontent.com/huggingface/fineweb-2/"
    "d0defb24f193bb9a5a11b8b14524a03c4858e1b6/fineweb2-language-distribution.csv"
)
RELEASE = "v2.1.1"

# Target class -> exact FineWeb2 language/script subset.
# English is deliberately separate: the FineWeb2 card directs users to FineWeb.
TARGET_SUBSETS = {
    "bg": "bul_Cyrl",
    "hr": "hrv_Latn",
    "cs": "ces_Latn",
    "da": "dan_Latn",
    "nl": "nld_Latn",
    "en": None,
    "et": "est_Latn",
    "fi": "fin_Latn",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "el": "ell_Grek",
    "hu": "hun_Latn",
    "ga": "gle_Latn",
    "it": "ita_Latn",
    "lv": "lav_Latn",
    "lt": "lit_Latn",
    "mt": "mlt_Latn",
    "pl": "pol_Latn",
    "pt": "por_Latn",
    "ro": "ron_Latn",
    "sk": "slk_Latn",
    "sl": "slv_Latn",
    "es": "spa_Latn",
    "sv": "swe_Latn",
    "nb": "nob_Latn",
    "nn": "nno_Latn",
    "ru": "rus_Cyrl",
    "ja": "jpn_Jpan",
    "zh": "cmn_Hani",
    "ko": "kor_Hang",
    "ar": "arb_Arab",
    "tr": "tur_Latn",
}


def read_source(source_csv: Path | None, timeout: int) -> tuple[list[dict[str, str]], str]:
    if source_csv:
        raw = source_csv.read_text(encoding="utf-8-sig")
        source = str(source_csv)
    else:
        request = urllib.request.Request(
            SOURCE_URL,
            headers={"User-Agent": "langid-32 corpus inventory/0.1"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8-sig")
            source = response.geturl()
    reader = csv.DictReader(io.StringIO(raw))
    required = {
        "subset", "split", "code", "script", "name", "words",
        "documents", "utf8_bytes", "parquet_bytes",
    }
    if not required.issubset(reader.fieldnames or []):
        raise ValueError(
            f"Unexpected FineWeb2 distribution CSV columns: {reader.fieldnames}"
        )
    return list(reader), source


def as_int(value: str | None) -> int:
    if value in (None, "", "-"):
        return 0
    return int(value)


def inventory(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_subset: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        subset = row.get("subset", "")
        # The canonical filtered subset is e.g. kor_Hang; removed data is
        # published as kor_Hang_removed and is counted separately.
        for target_subset in TARGET_SUBSETS.values():
            if target_subset and (
                subset == target_subset
                or subset == f"{target_subset}_removed"
            ):
                by_subset[target_subset].append(row)

    result = []
    for language, subset in TARGET_SUBSETS.items():
        if subset is None:
            result.append({
                "language": language,
                "fineweb2_subset": "",
                "status": "separate_fineweb_dataset",
                "filtered_train_documents": 0,
                "filtered_train_words": 0,
                "filtered_train_utf8_bytes": 0,
                "filtered_train_parquet_bytes": 0,
                "test_documents": 0,
                "removed_train_documents": 0,
                "removed_train_parquet_bytes": 0,
                "source_name": "English is distributed in the original FineWeb dataset",
            })
            continue

        selected = by_subset.get(subset, [])
        train = next((r for r in selected if r["subset"] == subset and r["split"] == "train"), None)
        test = next((r for r in selected if r["subset"] == subset and r["split"] == "test"), None)
        removed = next((r for r in selected if r["subset"] == f"{subset}_removed" and r["split"] == "train"), None)
        status = "available" if train else "not_listed"
        result.append({
            "language": language,
            "fineweb2_subset": subset,
            "status": status,
            "source_language_code": train["code"] if train else "",
            "script": train["script"] if train else "",
            "source_name": train["name"] if train else "",
            "filtered_train_documents": as_int(train["documents"]) if train else 0,
            "filtered_train_words": as_int(train["words"]) if train else 0,
            "filtered_train_utf8_bytes": as_int(train["utf8_bytes"]) if train else 0,
            "filtered_train_parquet_bytes": as_int(train["parquet_bytes"]) if train else 0,
            "test_documents": as_int(test["documents"]) if test else 0,
            "removed_train_documents": as_int(removed["documents"]) if removed else 0,
            "removed_train_parquet_bytes": as_int(removed["parquet_bytes"]) if removed else 0,
            "source_name": train["name"] if train else (
                "No exact language/script subset found in the published distribution CSV"
            ),
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path,
                        help="Use a previously downloaded upstream distribution CSV")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")

    source_rows, source = read_source(args.input_csv, args.timeout)
    result = inventory(source_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)

    available = [r for r in result if r["status"] == "available"]
    print(json.dumps({
        "output": str(args.output),
        "release": RELEASE,
        "source_revision": "d0defb24f193bb9a5a11b8b14524a03c4858e1b6",
        "source": source,
        "target_languages": len(TARGET_SUBSETS),
        "available_filtered_subsets": len(available),
        "not_listed": [r["language"] for r in result if r["status"] == "not_listed"],
        "english_route": "original FineWeb",
        "filtered_train_documents_total": sum(
            int(r["filtered_train_documents"]) for r in available
        ),
        "note": "Publisher metadata only; no Parquet data or text downloaded.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
