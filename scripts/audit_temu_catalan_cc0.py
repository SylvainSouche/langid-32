#!/usr/bin/env python3
"""Audit documented CC0 files in TeMU-BSC/catalan_CC0_sentences."""
from __future__ import annotations
import csv, hashlib, io, json, unicodedata, urllib.request, zipfile
from collections import Counter
from pathlib import Path

REV = "30f19bbfaca7b8abdd195c4687c1a992bde4f63f"
REPO = "TeMU-BSC/catalan_CC0_sentences"
URL = f"https://codeload.github.com/{REPO}/zip/{REV}"
FILES = {
    "catalan_government_crawling_frases_seleccionades_filtrades.txt": "CC0_public_administration",
    "datasets_sentences.tsv": "CC0_TeMU_Mozilla_waiver",
    "aggregated_files/new_catalan_cc0_corpus.txt": "CC0_TeMU_aggregate",
    "frases_agenda.txt": "CC0_TeMU_generated",
    "frases_diccionaris_enciclopedia.txt": "CC0_Enciclopedia_waiver",
    "frases_toponimia_valenciana_balear.txt": "CC0_TeMU_generated",
    "literatura.txt": "CC0_public_administration",
    "new_sentences_from_catalan_newswire.txt": "CC0_owner_permission",
    "aggregated_files/xitxat_and_toponyms.txt": "CC0_TeMU_aggregate",
}
OUT = Path("reports/temu-catalan-cc0-audit.json")

def norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFC", s).split()).casefold()

def main() -> None:
    request = urllib.request.Request(URL, headers={"User-Agent": "langid-32-source-audit"})
    with urllib.request.urlopen(request, timeout=180) as response:
        archive = response.read()
    archive_sha = hashlib.sha256(archive).hexdigest()
    zf = zipfile.ZipFile(io.BytesIO(archive))
    prefix = f"catalan_CC0_sentences-{REV}/"
    text_sets: dict[str, set[str]] = {}
    results = []
    for path, licence_basis in FILES.items():
        raw = zf.read(prefix + path)
        content = raw.decode("utf-8-sig")
        physical = content.splitlines()
        lines = [line for line in physical if line.strip()]
        extra = {}
        if path.endswith(".tsv"):
            parsed = list(csv.reader(io.StringIO(content), delimiter="\t"))
            widths = Counter(len(row) for row in parsed)
            col0 = [norm(row[0]) for row in parsed if len(row) > 0 and row[0].strip()]
            col1 = [norm(row[1]) for row in parsed if len(row) > 1 and row[1].strip()]
            extra = {
                "tsv_column_widths": dict(widths),
                "column_0_nonempty": len(col0),
                "column_0_distinct_normalized": len(set(col0)),
                "column_1_nonempty": len(col1),
                "column_1_distinct_normalized": len(set(col1)),
                "rows_not_two_columns": sum(1 for row in parsed if len(row) != 2),
            }
            # Column 0 is the sentence text; column 1 is source metadata
            # (four distinct labels in this pinned snapshot).
            keys = col0
            text_sets[path + "[column_0]"] = set(col0)
            unit = "TSV_records; column 0 sentence text, column 1 source label"
        else:
            keys = [norm(line) for line in lines]
            text_sets[path] = set(keys)
            unit = "non-empty text lines (provider-described sentences)"
        unique = set(keys)
        results.append({
            "path": path, "licence_basis_from_README": licence_basis,
            "unit": unit, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "physical_lines": len(physical), "nonempty_records": len(lines),
            "distinct_NFC_whitespace_casefold_records": len(unique),
            "within_file_normalized_duplicates": len(keys) - len(unique),
            **extra,
        })
    # Report exact normalized text overlap among the eight line-based files.
    names = list(text_sets)
    cross = []
    for i, left in enumerate(names):
        for right in names[i+1:]:
            overlap = len(text_sets[left] & text_sets[right])
            if overlap:
                cross.append({"left": left, "right": right, "shared_normalized_records": overlap})
    union = set().union(*text_sets.values())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "repository": REPO, "revision": REV, "archive_sha256": archive_sha,
        "archive_bytes": len(archive), "results": results,
        "normalized_text_union": {
            "line_based_files": 8,
            "line_based_nonempty_rows": sum(x["nonempty_records"] for x in results if not x["path"].endswith(".tsv")),
            "tsv_nonempty_sentence_cells": next(x["column_0_nonempty"] for x in results if x["path"].endswith(".tsv")),
            "candidate_rows_or_cells_before_dedup": sum(x["nonempty_records"] for x in results if not x["path"].endswith(".tsv")) + next(x["column_0_nonempty"] for x in results if x["path"].endswith(".tsv")),
            "distinct_normalized_text_strings": len(union),
        },
        "cross_file_overlap_pairs": cross,
        "warning": "TSV column semantics are not inferred. No total combines TSV with line files. Counts are structural and exact-text normalized, not semantic deduplication or rights verification."
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
