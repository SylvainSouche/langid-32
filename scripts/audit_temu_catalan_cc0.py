#!/usr/bin/env python3
"""Audit the documented CC0 sentence files in TeMU-BSC/catalan_CC0_sentences."""
from __future__ import annotations
import csv, hashlib, io, json, re, unicodedata, urllib.request, zipfile
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
    all_hashes: dict[str, set[str]] = {}
    results = []
    for path, licence_basis in FILES.items():
        raw = zf.read(prefix + path)
        text = raw.decode("utf-8-sig")
        lines = [line for line in text.splitlines() if line.strip()]
        # For TSV retain row counts and column structure; do not guess which
        # column is the sentence field without a schema.
        if path.endswith(".tsv"):
            parsed = list(csv.reader(io.StringIO(text), delimiter="\t"))
            widths = Counter(len(row) for row in parsed)
            keys = [norm("\t".join(row)) for row in parsed if any(x.strip() for x in row)]
            unit = "TSV_records (sentence field not inferred)"
        else:
            keys = [norm(line) for line in lines]
            widths = Counter()
            unit = "non-empty text lines (provider-described sentences)"
        unique = set(keys)
        all_hashes[path] = unique
        results.append({
            "path": path, "licence_basis_from_README": licence_basis,
            "unit": unit, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "physical_lines": len(text.splitlines()), "nonempty_records": len(lines),
            "distinct_NFC_whitespace_casefold_records": len(unique),
            "within_file_normalized_duplicates": len(keys) - len(unique),
            "tsv_column_widths": dict(widths) if widths else None,
        })
    # Cross-file duplicate counts are informative only: aggregate files
    # intentionally include component files, so do not sum these counts.
    cross = []
    for i, left in enumerate(FILES):
        for right in list(FILES)[i+1:]:
            overlap = len(all_hashes[left] & all_hashes[right])
            if overlap:
                cross.append({"left": left, "right": right, "shared_normalized_records": overlap})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {"repository": REPO, "revision": REV, "archive_sha256": archive_sha,
              "archive_bytes": len(archive), "results": results,
              "cross_file_overlap_pairs": cross,
              "warning": "No totals across files: aggregate/component overlap and differing row schemas. Counts are structural, not semantic or rights verification."}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
