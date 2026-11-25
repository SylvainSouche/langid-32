#!/usr/bin/env python3
"""Audit the complete IGC2024 Filtered-1 CC BY 4.0 JSONL archive."""
from __future__ import annotations
import collections, hashlib, io, json, os, sqlite3, tempfile, zipfile
from pathlib import Path
import requests

URL = "https://repository.clarin.is/repository/xmlui/bitstream/handle/20.500.12537/381/igc2024-1-filtered.zip?isAllowed=y&sequence=1"
OUT = Path("reports/igc2024-filtered-1-audit.json")
CHUNK = 1024 * 1024
FIELDS = ("tei_archive", "tei_path", "source", "altered", "text")

def download(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with requests.get(URL, stream=True, timeout=(60, 240), headers={"User-Agent": "langid-32-source-audit/1"}) as response:
        response.raise_for_status()
        with path.open("wb") as f:
            for chunk in response.iter_content(CHUNK):
                if chunk:
                    f.write(chunk)
                    h.update(chunk)
                    size += len(chunk)
    return size, h.hexdigest()

def main() -> None:
    fd, name = tempfile.mkstemp(prefix="igc2024-filtered-1-", suffix=".zip")
    os.close(fd)
    path = Path(name)
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE docpaths (value TEXT PRIMARY KEY)")
    db.execute("CREATE TABLE texthashes (value BLOB PRIMARY KEY)")
    try:
        archive_bytes, archive_sha = download(path)
        results = []
        totals = collections.Counter()
        sources = collections.Counter()
        altered = collections.Counter()
        missing = collections.Counter()
        malformed = 0
        duplicate_paths = duplicate_texts = 0
        min_words = None
        max_words = 0
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.is_dir() or not info.filename.lower().endswith(".jsonl"):
                    continue
                file_hash = hashlib.sha256()
                rows = words = chars = 0
                file_missing = collections.Counter()
                with archive.open(info, "r") as raw:
                    for line in raw:
                        file_hash.update(line)
                        if not line.strip():
                            continue
                        try:
                            item = json.loads(line)
                            if not isinstance(item, dict):
                                raise ValueError("not an object")
                        except Exception:
                            malformed += 1
                            continue
                        rows += 1
                        totals["documents"] += 1
                        for field in FIELDS:
                            if field not in item or item[field] is None or item[field] == "":
                                missing[field] += 1
                                file_missing[field] += 1
                        archive_id = str(item.get("tei_archive") or "")
                        tei_path = str(item.get("tei_path") or "")
                        if archive_id and tei_path:
                            key = archive_id + "/" + tei_path
                            try:
                                db.execute("INSERT INTO docpaths VALUES (?)", (key,))
                            except sqlite3.IntegrityError:
                                duplicate_paths += 1
                        text = item.get("text")
                        if isinstance(text, str):
                            nwords = len(text.split())
                            words += nwords
                            chars += len(text)
                            totals["text_bytes_utf8"] += len(text.encode("utf-8"))
                            min_words = nwords if min_words is None else min(min_words, nwords)
                            max_words = max(max_words, nwords)
                            digest = hashlib.sha256(text.encode("utf-8")).digest()
                            try:
                                db.execute("INSERT INTO texthashes VALUES (?)", (digest,))
                            except sqlite3.IntegrityError:
                                duplicate_texts += 1
                        elif text is not None:
                            totals["non_string_text"] += 1
                        source = str(item.get("source") or "MISSING")
                        sources[source] += 1
                        altered[str(item.get("altered"))] += 1
                results.append({
                    "file": info.filename, "uncompressed_bytes": info.file_size,
                    "sha256_uncompressed_jsonl": file_hash.hexdigest(), "documents": rows,
                    "whitespace_tokens": words, "text_characters": chars,
                    "missing_field_counts": dict(file_missing),
                })
        db.commit()
        totals["distinct_tei_archive_path"] = db.execute("SELECT COUNT(*) FROM docpaths").fetchone()[0]
        totals["distinct_exact_text_sha256"] = db.execute("SELECT COUNT(*) FROM texthashes").fetchone()[0]
        OUT.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "dataset": "IGC2024 Filtered-1", "revision": "CLARIN-IS handle 20.500.12537/381",
            "url": URL, "licence": "CC BY 4.0", "archive_bytes": archive_bytes,
            "archive_sha256": archive_sha, "archive_members": results,
            "total_documents": totals["documents"], "whitespace_tokens": sum(x["whitespace_tokens"] for x in results),
            "text_characters": sum(x["text_characters"] for x in results),
            "distinct_tei_archive_path": totals["distinct_tei_archive_path"],
            "distinct_exact_text_sha256": totals["distinct_exact_text_sha256"],
            "duplicate_tei_archive_path_rows": duplicate_paths, "duplicate_exact_text_rows": duplicate_texts,
            "source_counts": sources.most_common(100), "altered_counts": dict(altered),
            "missing_field_counts": dict(missing), "malformed_jsonl_rows": malformed,
            "min_words_per_document": min_words, "max_words_per_document": max_words,
            "method": "Full JSONL scan; exact UTF-8 text SHA-256 and tei_archive/tei_path uniqueness; source and altered metadata tallied.",
            "warning": "Whitespace token count is a local split-based measure. The CC BY 4.0 corpus-level grant still requires attribution and does not remove the need to retain source-document provenance."
        }
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        db.close()
        path.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
