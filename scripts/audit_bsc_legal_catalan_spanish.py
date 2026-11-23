#!/usr/bin/env python3
"""Count the upstream BSC Legal Catalan–Spanish corpus without retaining text.

Downloads the three files at a pinned Hub revision, records byte-level SHA-256,
counts source records and exact distinct texts per language side. Sentence,
paragraph and document granularities remain separate.
"""
from __future__ import annotations
import csv, hashlib, json, os, sqlite3, tempfile
from pathlib import Path
import requests

REPO = "BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus"
REVISION = os.environ.get("BSC_REVISION", "main")
BASE = f"https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/"
FILES = {
    "dogc_ca-es.tsv": "sentence_pair",
    "legal_ca-es_dataset_clean.tsv": "paragraph_pair",
    "apdcat_ca-es.docs.jsonl": "document_segment_pair",
}
OUT = Path("reports/bsc-legal-catalan-spanish-audit.json")

def count_file(name: str, unit: str) -> dict:
    url = BASE + name
    response = requests.get(url, stream=True, timeout=(30, 180))
    response.raise_for_status()
    digest = hashlib.sha256()
    rows = malformed = empty_ca = empty_es = 0
    byte_count = 0
    tmp = tempfile.NamedTemporaryFile(prefix="bsc-audit-", suffix=".sqlite", delete=False)
    tmp.close()
    db = sqlite3.connect(tmp.name)
    db.execute("CREATE TABLE ca (text TEXT PRIMARY KEY)")
    db.execute("CREATE TABLE es (text TEXT PRIMARY KEY)")
    def add(side: str, value: str) -> None:
        db.execute(f"INSERT OR IGNORE INTO {side} VALUES (?)", (value,))
    try:
        if name.endswith(".jsonl"):
            for raw in response.iter_lines():
                if not raw:
                    continue
                digest.update(raw + b"\\n")
                byte_count += len(raw) + 1
                rows += 1
                try:
                    item = json.loads(raw)
                    ca, es = item["ca"], item["es"]
                    if not isinstance(ca, str) or not isinstance(es, str):
                        raise ValueError("ca/es not strings")
                except Exception:
                    malformed += 1
                    continue
                empty_ca += not bool(ca.strip())
                empty_es += not bool(es.strip())
                add("ca", ca)
                add("es", es)
                if rows % 10000 == 0:
                    db.commit()
        else:
            import codecs
            reader = csv.reader(codecs.getreader("utf-8")(response.raw), delimiter="\\t")
            for fields in reader:
                if not fields:
                    continue
                rows += 1
                if len(fields) != 2:
                    malformed += 1
                    continue
                ca, es = fields
                encoded = (ca + "\\t" + es + "\\n").encode("utf-8")
                digest.update(encoded)
                byte_count += len(encoded)
                empty_ca += not bool(ca.strip())
                empty_es += not bool(es.strip())
                add("ca", ca)
                add("es", es)
                if rows % 100000 == 0:
                    db.commit()
                    print(f"{name}: {rows:,} rows", flush=True)
        db.commit()
        result = {
            "file": name, "unit": unit, "revision": REVISION,
            "url": url, "etag": response.headers.get("ETag"),
            "content_length": response.headers.get("Content-Length"),
            "bytes_streamed": byte_count, "sha256_stream": digest.hexdigest(),
            "rows": rows, "malformed_rows": malformed,
            "empty_ca": empty_ca, "empty_es": empty_es,
            "distinct_exact_ca": db.execute("SELECT COUNT(*) FROM ca").fetchone()[0],
            "distinct_exact_es": db.execute("SELECT COUNT(*) FROM es").fetchone()[0],
        }
        return result
    finally:
        db.close()
        os.unlink(tmp.name)
        response.close()

def main() -> None:
    results = [count_file(name, unit) for name, unit in FILES.items()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repository": REPO, "revision": REVISION,
        "license_card": "CC-BY-4.0", "results": results},
        ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if any(x["malformed_rows"] for x in results):
        raise SystemExit("Malformed records found; inspect report")

if __name__ == "__main__":
    main()
