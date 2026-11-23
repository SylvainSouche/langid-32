#!/usr/bin/env python3
"""Full metadata and record-count audit of Målfrid 2026 Bokmål/Nynorsk archives."""
from __future__ import annotations
import collections, gzip, hashlib, io, json, os, sqlite3, tempfile, tarfile
from pathlib import Path
import requests

SOURCES = {
    "nb": "https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026_nob.tar",
    "nn": "https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026_nno.tar",
}
OUT = Path("reports/maalfrid-2026-audit.json")
CHUNK = 1024 * 1024

def download(url: str, path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with requests.get(url, stream=True, timeout=(60, 240)) as response:
        response.raise_for_status()
        with path.open("wb") as f:
            for chunk in response.iter_content(CHUNK):
                if chunk:
                    f.write(chunk)
                    h.update(chunk)
                    size += len(chunk)
    return size, h.hexdigest()

def audit_archive(language: str, url: str, db: sqlite3.Connection) -> dict:
    fd, name = tempfile.mkstemp(prefix=f"maalfrid-{language}-", suffix=".tar")
    os.close(fd)
    path = Path(name)
    try:
        size, archive_hash = download(url, path)
        members = []
        totals = collections.Counter()
        langs = collections.Counter()
        domains = collections.Counter()
        mimetypes = collections.Counter()
        member_rows = []
        min_date = max_date = None
        missing = collections.Counter()
        malformed = 0
        duplicate_hashes = duplicate_ids = 0
        with tarfile.open(path, mode="r:*") as archive:
            for member in archive:
                if not member.isfile():
                    continue
                members.append(member.name)
                stream = archive.extractfile(member)
                if stream is None:
                    continue
                opener = gzip.GzipFile(fileobj=stream) if member.name.endswith(".gz") else stream
                rows = paragraphs = words = chars = 0
                try:
                    text_stream = io.TextIOWrapper(opener, encoding="utf-8")
                    for line in text_stream:
                        if not line.strip():
                            continue
                        try:
                            obj = json.loads(line)
                            if not isinstance(obj, dict):
                                raise ValueError("not object")
                        except Exception:
                            malformed += 1
                            continue
                        rows += 1
                        totals["documents"] += 1
                        for field in ("doc_id", "doc_hash", "domain", "url", "date", "mimetype", "lang", "fulltext"):
                            if field not in obj or obj[field] is None or obj[field] == "":
                                missing[field] += 1
                        doc_id = obj.get("doc_id")
                        doc_hash = obj.get("doc_hash")
                        if isinstance(doc_id, str) and doc_id:
                            try:
                                db.execute("INSERT INTO ids VALUES (?)", (doc_id,))
                            except sqlite3.IntegrityError:
                                duplicate_ids += 1
                        if isinstance(doc_hash, str) and doc_hash:
                            try:
                                db.execute("INSERT INTO hashes VALUES (?)", (doc_hash,))
                            except sqlite3.IntegrityError:
                                duplicate_hashes += 1
                        lang = str(obj.get("lang") or "MISSING")
                        domain = str(obj.get("domain") or "MISSING")
                        mime = str(obj.get("mimetype") or "MISSING")
                        langs[lang] += 1
                        domains[domain] += 1
                        mimetypes[mime] += 1
                        fulltext = obj.get("fulltext")
                        if isinstance(fulltext, list):
                            paragraphs += len(fulltext)
                            for p in fulltext:
                                if isinstance(p, str):
                                    chars += len(p)
                                    words += len(p.split())
                                    if not p.strip():
                                        totals["empty_paragraphs"] += 1
                        elif fulltext is not None:
                            totals["non_array_fulltext"] += 1
                        date = str(obj.get("date") or "")
                        if date:
                            min_date = date if min_date is None else min(min_date, date)
                            max_date = date if max_date is None else max(max_date, date)
                finally:
                    try:
                        text_stream.detach()
                    except Exception:
                        pass
                totals["paragraphs"] += paragraphs
                totals["whitespace_tokens"] += words
                totals["text_characters"] += chars
                member_rows.append({"member": member.name, "uncompressed_bytes": member.size, "documents": rows,
                                    "paragraphs": paragraphs, "whitespace_tokens": words, "text_characters": chars})
        db.commit()
        return {
            "language": language, "url": url, "archive_bytes": size, "archive_sha256": archive_hash,
            "archive_members": len(members), "members": member_rows,
            "documents": totals["documents"], "paragraphs": totals["paragraphs"],
            "whitespace_tokens": totals["whitespace_tokens"], "text_characters": totals["text_characters"],
            "empty_paragraphs": totals["empty_paragraphs"], "non_array_fulltext": totals["non_array_fulltext"],
            "language_field_counts": dict(langs), "mimetype_counts": dict(mimetypes),
            "distinct_domains": len(domains), "top_domains_by_documents": domains.most_common(20),
            "date_min": min_date, "date_max": max_date, "missing_field_counts": dict(missing),
            "malformed_jsonl_rows": malformed, "duplicate_doc_ids_within_and_across_archives": duplicate_ids,
            "duplicate_doc_hashes_within_and_across_archives": duplicate_hashes,
        }
    finally:
        path.unlink(missing_ok=True)

def main() -> None:
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE ids (value TEXT PRIMARY KEY)")
    db.execute("CREATE TABLE hashes (value TEXT PRIMARY KEY)")
    results = [audit_archive(lang, url, db) for lang, url in SOURCES.items()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "dataset": "Målfrid 2026", "permanent_record": "https://hdl.handle.net/21.11146/107",
        "licence_claim": "NLOD 2.0", "method": "Full tarball scan; one JSONL record per document; publisher doc_id/doc_hash uniqueness checked across Bokmål and Nynorsk; paragraph counts and whitespace-token counts measured directly.",
        "results": results,
        "combined_distinct_doc_ids": db.execute("SELECT COUNT(*) FROM ids").fetchone()[0],
        "combined_distinct_doc_hashes": db.execute("SELECT COUNT(*) FROM hashes").fetchone()[0],
        "warning": "Whitespace-token counts are a reproducible local measure, not asserted to be identical to the publisher's tokenizer. NLOD 2.0 does not itself resolve third-party rights in embedded documents or personal data."
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))
    db.close()

if __name__ == "__main__":
    main()
