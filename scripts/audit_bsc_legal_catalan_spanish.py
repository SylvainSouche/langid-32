#!/usr/bin/env python3
"""Audit pinned BSC Legal Catalan–Spanish files with their actual TSV schemas."""
from __future__ import annotations
import csv, hashlib, json, os, sqlite3, sys, tempfile
from collections import Counter
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
    db.execute("CREATE TABLE docs (h BLOB PRIMARY KEY) WITHOUT ROWID")
    widths = Counter()
    rows = headers = malformed = empty_ca = empty_es = 0
    ca_batch: list[tuple[bytes]] = []
    es_batch: list[tuple[bytes]] = []
    doc_batch: list[tuple[bytes]] = []
    def flush() -> None:
        if ca_batch:
            db.executemany("INSERT OR IGNORE INTO ca VALUES (?)", ca_batch)
            db.executemany("INSERT OR IGNORE INTO es VALUES (?)", es_batch)
            if doc_batch:
                db.executemany("INSERT OR IGNORE INTO docs VALUES (?)", doc_batch)
            ca_batch.clear()
            es_batch.clear()
            doc_batch.clear()
    def add(ca: str, es: str, doc_id: str | None = None) -> None:
        ca_batch.append((hashlib.sha256(ca.encode("utf-8")).digest(),))
        es_batch.append((hashlib.sha256(es.encode("utf-8")).digest(),))
        if doc_id:
            doc_batch.append((hashlib.sha256(doc_id.encode("utf-8")).digest(),))
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
                        doc_id = item.get("doc_id")
                        if not isinstance(ca, str) or not isinstance(es, str):
                            raise ValueError("ca/es not strings")
                    except Exception:
                        malformed += 1
                        continue
                    empty_ca += not bool(ca.strip())
                    empty_es += not bool(es.strip())
                    add(ca, es, doc_id if isinstance(doc_id, str) else None)
        else:
            csv.field_size_limit(sys.maxsize)
            with source_path.open("r", encoding="utf-8", newline="") as stream:
                reader = csv.reader(stream, delimiter="\t")
                for fields in reader:
                    if not fields:
                        continue
                    rows += 1
                    widths[len(fields)] += 1
                    if rows == 1:
                        expected_header = ["ca", "es"] if name == "dogc_ca-es.tsv" else ["dataset", "segment_id", "ca_text", "es_text", "alignment_score"]
                        if [x.strip().lower() for x in fields] == expected_header:
                            headers += 1
                            continue
                    if name == "dogc_ca-es.tsv":
                        if len(fields) != 2:
                            malformed += 1
                            continue
                        ca, es = fields
                    else:
                        if len(fields) != 5:
                            malformed += 1
                            continue
                        ca, es = fields[2], fields[3]
                    empty_ca += not bool(ca.strip())
                    empty_es += not bool(es.strip())
                    add(ca, es)
                    if rows % 500000 == 0:
                        flush()
                        db.commit()
                        print(f"{name}: {rows:,} logical rows", flush=True)
        flush()
        db.commit()
        valid_pairs = rows - headers - malformed
        return {
            "file": name, "unit": unit, "revision": REVISION,
            "url": url, "bytes_downloaded": byte_count,
            "sha256": digest.hexdigest(),
            "logical_rows_including_header": rows, "header_rows": headers,
            "valid_pair_rows": valid_pairs, "malformed_rows": malformed,
            "field_width_counts": dict(widths) if widths else None,
            "empty_ca": empty_ca, "empty_es": empty_es,
            "distinct_sha256_ca": db.execute("SELECT COUNT(*) FROM ca").fetchone()[0],
            "distinct_sha256_es": db.execute("SELECT COUNT(*) FROM es").fetchone()[0],
            "distinct_doc_ids_sha256": db.execute("SELECT COUNT(*) FROM docs").fetchone()[0] if name.endswith(".jsonl") else None,
            "distinct_method": "SHA-256 of exact UTF-8 text; collision probability negligible",
        }
    finally:
        db.close()
        os.unlink(dbfile.name)
        os.unlink(source_path)

def main() -> None:
    results = [count_file(name, unit) for name, unit in FILES.items()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "repository": REPO, "revision": REVISION, "license_card": "CC-BY-4.0",
        "results": results,
        "warning": "Malformed TSV rows are excluded from valid-pair counts and retained in the report. Distinct counts are per file and per language side; paragraph/document units are not added to sentence pairs."
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
