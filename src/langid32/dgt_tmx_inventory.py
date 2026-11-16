"""Inventory DGT-TM 2021 TMX volumes without exporting segment text.

The official TMX files are UTF-16LE and are stored inside ZIP volumes. This
counter streams each TMX file, records per-language counts and document-group
counts, and deduplicates normalized text in a temporary SQLite database.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

EU_LANGUAGES = {
    "bg", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "de",
    "el", "hu", "ga", "it", "lv", "lt", "mt", "pl", "pt", "ro",
    "sk", "sl", "es", "sv",
}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def iter_translation_units(stream):
    stack = []
    for event, element in ET.iterparse(stream, events=("start", "end")):
        if event == "start":
            stack.append(element)
            continue
        if local_name(element.tag) == "tu":
            yield element
            if len(stack) > 1:
                stack[-2].remove(element)
            element.clear()
        stack.pop()


def segments_from_tu(tu):
    for tuv in tu:
        if local_name(tuv.tag) != "tuv":
            continue
        raw_language = tuv.attrib.get(XML_LANG, "").lower()
        language = raw_language.split("-", 1)[0]
        if language not in EU_LANGUAGES:
            continue
        for element in tuv.iter():
            if local_name(element.tag) == "seg":
                text = normalize("".join(element.itertext()))
                if text:
                    yield language, text
                break


def inventory(data_root: Path, output: Path, min_chars: int,
              max_chars: int, max_bytes: int, max_files: int) -> dict:
    archives = sorted(data_root.glob("*.zip"))
    if not archives:
        raise ValueError(f"no ZIP volumes found in {data_root}")
    processed_files = 0
    malformed_files = 0
    counts = Counter()

    with tempfile.TemporaryDirectory(prefix="langid32-dgt-") as temp:
        db = sqlite3.connect(Path(temp) / "inventory.sqlite")
        db.execute("""
            CREATE TABLE unique_text (
                language TEXT NOT NULL,
                text_hash TEXT NOT NULL,
                PRIMARY KEY(language, text_hash)
            )
        """)
        db.execute("""
            CREATE TABLE document_groups (
                language TEXT NOT NULL,
                group_id TEXT NOT NULL,
                PRIMARY KEY(language, group_id)
            )
        """)
        for archive_path in archives:
            with zipfile.ZipFile(archive_path) as archive:
                for member in sorted(archive.namelist()):
                    if not member.lower().endswith(".tmx"):
                        continue
                    if max_files and processed_files >= max_files:
                        break
                    processed_files += 1
                    group_id = f"DGT-TM-2021:{PurePosixPath(member).stem}"
                    try:
                        with archive.open(member) as stream:
                            for tu in iter_translation_units(stream):
                                counts["translation_units"] += 1
                                for language, text in segments_from_tu(tu):
                                    counts[f"segments::{language}"] += 1
                                    if len(text) < min_chars or len(text) > max_chars:
                                        counts[f"outside_character_limits::{language}"] += 1
                                        continue
                                    if len(text.encode("utf-8")) > max_bytes:
                                        counts[f"outside_byte_limit::{language}"] += 1
                                        continue
                                    counts[f"eligible_segments::{language}"] += 1
                                    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                                    cursor = db.execute(
                                        "INSERT OR IGNORE INTO unique_text VALUES (?,?)",
                                        (language, digest),
                                    )
                                    if cursor.rowcount == 0:
                                        counts[f"duplicate_text::{language}"] += 1
                                    db.execute(
                                        "INSERT OR IGNORE INTO document_groups VALUES (?,?)",
                                        (language, group_id),
                                    )
                    except (ET.ParseError, UnicodeError, OSError, zipfile.BadZipFile):
                        malformed_files += 1
                        counts["malformed_tmx_files"] += 1
            db.commit()
            if max_files and processed_files >= max_files:
                break

        rows = []
        for language in sorted(EU_LANGUAGES):
            unique = db.execute(
                "SELECT COUNT(*) FROM unique_text WHERE language=?", (language,)
            ).fetchone()[0]
            groups = db.execute(
                "SELECT COUNT(*) FROM document_groups WHERE language=?", (language,)
            ).fetchone()[0]
            rows.append({
                "language": language,
                "release": "DGT-TM-release-2021",
                "zip_volumes_found": len(archives),
                "tmx_files_processed": processed_files,
                "translation_units": counts["translation_units"],
                "segments": counts[f"segments::{language}"],
                "eligible_segments": counts[f"eligible_segments::{language}"],
                "unique_eligible_text": unique,
                "duplicate_eligible_text": counts[f"duplicate_text::{language}"],
                "outside_character_limits": counts[f"outside_character_limits::{language}"],
                "outside_byte_limit": counts[f"outside_byte_limit::{language}"],
                "document_groups": groups,
                "malformed_tmx_files": malformed_files,
                "pii_screening": "not_performed",
                "source_licence": "European Commission Re-use Decision 2011/833/EU",
            })
        db.close()

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {
        "output": str(output),
        "zip_volumes_found": len(archives),
        "tmx_files_processed": processed_files,
        "malformed_tmx_files": malformed_files,
        "total_unique_eligible_segments": sum(row["unique_eligible_text"] for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True, type=Path,
                        help="Directory containing DGT-TM-release-2021 ZIP volumes")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    parser.add_argument("--max-files", type=int, default=0,
                        help="Optional TMX-file limit for a smoke test; 0 means all")
    args = parser.parse_args()
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    if args.max_files < 0:
        parser.error("--max-files must be >= 0")
    print(json.dumps(
        inventory(args.data_root, args.output, args.min_chars, args.max_chars,
                  args.max_bytes, args.max_files),
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
