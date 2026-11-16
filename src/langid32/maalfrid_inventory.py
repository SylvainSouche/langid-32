"""Inventory Målfrid 2026 per-language TAR archives without exporting text.

The TAR contains gzipped JSONL files. This counter records document, domain,
paragraph and deduplication counts only; it does not perform PII screening or
sentence segmentation.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sqlite3
import tarfile
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path

SOURCE_LANGUAGES = {"nb": "nob", "nn": "nno"}


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def inventory_archive(language: str, archive_path: Path, min_chars: int,
                      max_chars: int, max_bytes: int, db: sqlite3.Connection) -> dict:
    expected_code = SOURCE_LANGUAGES[language]
    counts = Counter()
    domains: set[str] = set()
    batch: list[tuple[str, str]] = []
    doc_batch: list[tuple[str, str]] = []

    with tarfile.open(archive_path, mode="r|") as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith(".jsonl.gz"):
                continue
            raw = archive.extractfile(member)
            if raw is None:
                continue
            with raw, gzip.GzipFile(fileobj=raw, mode="rb") as stream:
                for line in stream:
                    if not line.strip():
                        continue
                    counts["jsonl_rows"] += 1
                    try:
                        doc = json.loads(line)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        counts["invalid_json_rows"] += 1
                        continue
                    doc_lang = (doc.get("lang") or "").lower()
                    if doc_lang != expected_code:
                        counts["document_language_mismatch"] += 1
                        continue
                    counts["documents"] += 1
                    doc_hash = doc.get("doc_hash")
                    if doc_hash:
                        doc_batch.append((language, str(doc_hash)))
                    domain = (doc.get("domain") or "").strip().lower()
                    if domain:
                        domains.add(domain)
                    paragraphs = doc.get("fulltext") or []
                    if not isinstance(paragraphs, list):
                        counts["invalid_fulltext_field"] += 1
                        continue
                    for paragraph in paragraphs:
                        if not isinstance(paragraph, str):
                            continue
                        counts["paragraphs"] += 1
                        text = normalize(paragraph)
                        if not text:
                            counts["empty_paragraphs"] += 1
                            continue
                        if len(text) < min_chars or len(text) > max_chars:
                            counts["outside_character_limits"] += 1
                            continue
                        if len(text.encode("utf-8")) > max_bytes:
                            counts["outside_byte_limit"] += 1
                            continue
                        counts["eligible_paragraphs"] += 1
                        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                        batch.append((language, digest))
                        if len(batch) >= 5000:
                            db.executemany(
                                "INSERT OR IGNORE INTO paragraph_hashes VALUES (?,?)",
                                batch,
                            )
                            batch.clear()
                    if len(doc_batch) >= 5000:
                        db.executemany(
                            "INSERT OR IGNORE INTO document_hashes VALUES (?,?)",
                            doc_batch,
                        )
                        doc_batch.clear()
    if batch:
        db.executemany("INSERT OR IGNORE INTO paragraph_hashes VALUES (?,?)", batch)
    if doc_batch:
        db.executemany("INSERT OR IGNORE INTO document_hashes VALUES (?,?)", doc_batch)
    db.commit()
    counts["unique_eligible_paragraphs"] = db.execute(
        "SELECT COUNT(*) FROM paragraph_hashes WHERE language=?", (language,)
    ).fetchone()[0]
    counts["cross_language_shared_paragraphs"] = db.execute("""
        SELECT COUNT(*) FROM paragraph_hashes AS p
        WHERE p.language=? AND EXISTS (
            SELECT 1 FROM paragraph_hashes AS q
            WHERE q.text_hash=p.text_hash AND q.language<>p.language
        )
    """, (language,)).fetchone()[0]
    counts["unique_documents_by_hash"] = db.execute(
        "SELECT COUNT(*) FROM document_hashes WHERE language=?", (language,)
    ).fetchone()[0]
    counts["domains"] = len(domains)
    return {
        "language": language,
        "source_language_code": expected_code,
        "archive_name": archive_path.name,
        "archive_bytes": archive_path.stat().st_size,
        "pii_screening": "not_performed",
        **dict(counts),
    }


def inventory(archives: list[tuple[str, Path]], min_chars: int,
              max_chars: int, max_bytes: int) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="langid32-maalfrid-") as temp:
        db = sqlite3.connect(Path(temp) / "inventory.sqlite")
        db.execute("""
            CREATE TABLE paragraph_hashes (
                language TEXT NOT NULL,
                text_hash TEXT NOT NULL,
                PRIMARY KEY(language, text_hash)
            )
        """)
        db.execute("""
            CREATE TABLE document_hashes (
                language TEXT NOT NULL,
                doc_hash TEXT NOT NULL,
                PRIMARY KEY(language, doc_hash)
            )
        """)
        rows = [
            inventory_archive(language, path, min_chars, max_chars, max_bytes, db)
            for language, path in archives
        ]
        db.close()
        return rows


def parse_archive(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected LANGUAGE=PATH (nb=... or nn=...)")
    language, filename = value.split("=", 1)
    language = language.strip().lower()
    if language not in SOURCE_LANGUAGES:
        raise argparse.ArgumentTypeError(f"unsupported language: {language}")
    path = Path(filename).expanduser()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"archive not found: {path}")
    return language, path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", action="append", required=True, type=parse_archive,
                        metavar="LANGUAGE=PATH")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    args = parser.parse_args()
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    if len({lang for lang, _ in args.archive}) != len(args.archive):
        parser.error("each language may be supplied only once")
    rows = inventory(args.archive, args.min_chars, args.max_chars, args.max_bytes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "output": str(args.output),
        "languages_inventoried": len(rows),
        "total_unique_eligible_paragraphs": sum(
            row.get("unique_eligible_paragraphs", 0) for row in rows
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
