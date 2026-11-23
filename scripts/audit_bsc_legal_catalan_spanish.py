#!/usr/bin/env python3
"""Audit pinned BSC Legal Catalan–Spanish files without retaining source text."""
from __future__ import annotations
import csv, hashlib, json, os, sqlite3, sys, tempfile
from pathlib import Path
import requests

REPO = "BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus"
REVISION = os.environ.get("BSC_REVISION", "5f7eda4")
BASE = f"https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/"
FILES = {
    "dogc_ca-es.tsv": "sentence_pair",
    "legal_ca-es_dataset_clean.tsv": "paragraph_pair",
    "apdcat_ca-es.docs.jsonl": "document_segment_pair",
}
OUT = Path("reports/bsc-legal-catalan-spanish-audit.json")
BATCH = 10000

def count_file(name: str, unit: str) -> dict:
    url = BASE + name
    response = requests.get(url, stream=True, timeout=(30, 180))
    response.raise_for_status()
    source = tempfile.NamedTemporaryFile(prefix="bsc-source-", delete=False)
    source_path = Path(source.name)
    digest = hashlib.sha256()
    byte_count = 0
    try:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                source.write(chunk)
                digest.update(chunk)
                byte_count += len(chunk)
        source.close()
    finally:
        response.close()

    dbfile = tempfile.NamedTemporaryFile(prefix="bsc-audit-", suffix=".sqlite", delete=False)
    dbfile.close()
    db = sqlite3.connect(dbfile.name)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("PRAGMA temp_store=MEMORY")
    db.execute("PRAGMA cache_size=-200000")
    db.execute("CREATE TABLE ca (h BLOB PRIMARY KEY) WITHOUT ROWID")
    db.execute("CREATE TABLE es (h BLOB PRIMARY KEY) WITHOUT ROWID")
    rows = malformed = empty_ca = empty_es = 0
    ca_batch: list[tuple[bytes]] = []
    es_batch: list[tuple[bytes]] = []
    insert_ca = "INSERT OR IGNORE INTO ca VALUES (?)"
    insert_es = "INSERT OR IGNORE INTO es VALUES (?)"
    def flush() -> None:
        if ca_batch:
            db.executemany(insert_ca, ca_batch)
            db.executemany(insert_es, es_batch)
            ca_batch.clear()
            es_batch.clear()
    def add(ca: str, es: str) -> None:
        ca_batch.append((hashlib.sha256(ca.encode("utf-8")).digest(),))
        es_batch.append((hashlib.sha256(es.encode("utf-8")).digest(),))
        if len(ca_batch) >= BATCH:
            flush()
    try:
        if name.endswith(".jsonl"):
            with source_path.open("r", encoding="utf-8") as stream:
                for line in stream:
                    if not line.strip():
                        continue
                    rows += 1
                    try:
                        item = json.loads(line)
                        ca, es = item["ca"], item["es"]
                        if not isinstance(ca, str) or not isinstance(es, str):
                            raise ValueError("ca/es not strings")
                    except Exception:
                        malformed += 1
                        continue
                    empty_ca += not bool(ca.strip())
                    empty_es += not bool(es.strip())
                    add(ca, es)
        else:
            csv.field_size_limit(sys.maxsize)
            with source_path.open("r", encoding="utf-8", newline="") as stream:
                reader = csv.reader(stream, delimiter="\t")
                for fields in reader:
                    if not fields:
                        continue
                    rows += 1
                    if len(fields) != 2:
                        malformed += 1
                        continue
                    ca, es = fields
                    empty_ca += not bool(ca.strip())
                    empty_es += not bool(es.strip())
                    add(ca, es)
                    if rows % 500000 == 0:
                        flush()
                        db.commit()
                        print(f"{name}: {rows:,} rows", flush=True)
        flush()
        db.commit()
        return {
            "file": name, "unit": unit, "revision": REVISION,
            "url": url, "content_length": byte_count, "bytes_downloaded": byte_count,
            "sha256": digest.hexdigest(), "rows": rows, "malformed_rows": malformed,
            "empty_ca": empty_ca, "empty_es": empty_es,
            "distinct_sha256_ca": db.execute("SELECT COUNT(*) FROM ca").fetchone()[0],
            "distinct_sha256_es": db.execute("SELECT COUNT(*) FROM es").fetchone()[0],
            "distinct_method": "SHA-256 of exact UTF-8 text; collision probability negligible",
        }
    finally:
        db.close()
        os.unlink(dbfile.name)
        os.unlink(source_path)

def main() -> None:
    results = [count_file(name, unit) for name, unit in FILES.items()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"repository": REPO, "revision": REVISION,
        "license_card": "CC-BY-4.0", "results": results},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if any(x["malformed_rows"] for x in results):
        raise SystemExit("Malformed records found; inspect report")

if __name__ == "__main__":
    main()
