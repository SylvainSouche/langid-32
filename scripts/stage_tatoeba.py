#!/usr/bin/env python3
"""Stage Tatoeba CC0 sentences with translation-base grouping and provenance."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path

CODES = {
    "bg": ("bul",), "hr": ("hrv",), "cs": ("ces",), "da": ("dan",),
    "nl": ("nld",), "en": ("eng",), "et": ("est",), "fi": ("fin",),
    "fr": ("fra",), "de": ("deu",), "el": ("ell",), "hu": ("hun",),
    "ga": ("gle",), "it": ("ita",), "lv": ("lav",), "lt": ("lit",),
    "mt": ("mlt",), "pl": ("pol",), "pt": ("por",), "ro": ("ron",),
    "sk": ("slk",), "sl": ("slv",), "es": ("spa",), "sv": ("swe",),
    "nb": ("nob",), "nn": ("nno",), "ru": ("rus",), "ja": ("jpn",),
    "zh": ("cmn",), "ko": ("kor",), "ar": ("ara",), "tr": ("tur",),
}
CODE_TO_LANGUAGE = {code: lang for lang, codes in CODES.items() for code in codes}
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL = re.compile(r"(?i)(?:https?://|www\.)\S+")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PHONE = re.compile(r"(?<!\w)\+?\d[\d .()/-]{7,}\d(?!\w)")
LONG_NUMBER = re.compile(r"\d{9,}")


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stage(args):
    args.output.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    with tempfile.TemporaryDirectory(prefix="langid32-tatoeba-") as temp:
        db = sqlite3.connect(Path(temp) / "tatoeba.sqlite")
        db.execute("""
            CREATE TABLE sentence (
                id INTEGER PRIMARY KEY,
                language TEXT NOT NULL,
                text TEXT NOT NULL,
                modified TEXT,
                base_id TEXT,
                privacy_flags TEXT NOT NULL
            )
        """)
        batch = []
        with args.sentences_cc0.open("r", encoding="utf-8-sig", newline="") as stream:
            for fields in csv.reader(stream, delimiter="\t"):
                if len(fields) < 3:
                    counts["malformed_cc0_rows"] += 1
                    continue
                sentence_id, code, raw_text = fields[:3]
                language = CODE_TO_LANGUAGE.get(code)
                if language is None:
                    counts["non_target_language"] += 1
                    continue
                try:
                    sentence_id = int(sentence_id)
                except ValueError:
                    counts["invalid_sentence_id"] += 1
                    continue
                text = normalize(raw_text)
                if not text:
                    counts["empty_text"] += 1
                    continue
                if len(text) < args.min_chars or len(text) > args.max_chars:
                    counts["outside_character_limits"] += 1
                    continue
                if len(text.encode("utf-8")) > args.max_bytes:
                    counts["outside_byte_limit"] += 1
                    continue
                if EMAIL.search(text):
                    counts["email_excluded"] += 1
                    continue
                if URL.search(text):
                    counts["url_excluded"] += 1
                    continue
                if IPV4.search(text):
                    counts["ipv4_excluded"] += 1
                    continue
                privacy_flags = []
                if PHONE.search(text):
                    privacy_flags.append("phone_like")
                    counts["phone_like_flagged"] += 1
                if LONG_NUMBER.search(text):
                    privacy_flags.append("long_numeric_sequence")
                    counts["long_number_flagged"] += 1
                modified = fields[3] if len(fields) > 3 else ""
                batch.append((sentence_id, language, text, modified, None,
                              json.dumps(privacy_flags)))
                counts[f"accepted_before_base_join:{language}"] += 1
                if len(batch) >= 5000:
                    db.executemany("INSERT OR REPLACE INTO sentence VALUES (?,?,?,?,?,?)", batch)
                    batch.clear()
        if batch:
            db.executemany("INSERT OR REPLACE INTO sentence VALUES (?,?,?,?,?,?)", batch)
        db.commit()

        # The base export contains all Tatoeba sentences, not just CC0 ones.
        # Join only IDs in the CC0 subset, so no CC-BY text enters staging.
        cc0_ids = {row[0] for row in db.execute("SELECT id FROM sentence")}
        batch = []
        with args.sentences_base.open("r", encoding="utf-8-sig", newline="") as stream:
            for fields in csv.reader(stream, delimiter="\t"):
                if len(fields) < 2:
                    continue
                try:
                    sentence_id = int(fields[0])
                except ValueError:
                    continue
                if sentence_id not in cc0_ids:
                    continue
                batch.append((fields[1], sentence_id))
                if len(batch) >= 10000:
                    db.executemany("UPDATE sentence SET base_id=? WHERE id=?", batch)
                    batch.clear()
        if batch:
            db.executemany("UPDATE sentence SET base_id=? WHERE id=?", batch)
        db.commit()

        output_count = 0
        with args.output.open("w", encoding="utf-8", newline="\n") as output:
            cursor = db.execute(
                "SELECT id, language, text, modified, base_id, privacy_flags "
                "FROM sentence ORDER BY id"
            )
            for sentence_id, language, text, modified, base_id, privacy_flags in cursor:
                if base_id is None or base_id in ("", r"\N"):
                    origin = "unknown"
                    group_material = f"sentence:{sentence_id}"
                    counts["base_unknown"] += 1
                elif str(base_id) == "0":
                    origin = "original"
                    group_material = f"base:{sentence_id}"
                    counts["base_original"] += 1
                else:
                    origin = "translated"
                    group_material = f"base:{base_id}"
                    counts["base_translation"] += 1
                record = {
                    "text": text,
                    "language": language,
                    "source": "tatoeba-cc0",
                    "source_release": args.source_release,
                    "group_id": f"tatoeba:{group_material}",
                    "licence_id": "CC0-1.0",
                    "text_origin": origin,
                    "provenance": {
                        "sentence_id": sentence_id,
                        "base_id": base_id,
                        "last_modified": modified,
                        "privacy_flags": json.loads(privacy_flags),
                        "source_url": "https://tatoeba.org/en/downloads",
                    },
                }
                output.write(json.dumps(record, ensure_ascii=False,
                                        separators=(",", ":")) + "\n")
                counts[f"output:{language}"] += 1
                output_count += 1
        db.close()

    manifest = {
        "source": "Tatoeba sentences_CC0.csv + sentences_base.csv",
        "source_release": args.source_release,
        "source_licence": "CC0-1.0 (CC0 sentence export only)",
        "source_download_origin": "https://downloads.tatoeba.org/exports/",
        "sentences_cc0_sha256": sha256_file(args.sentences_cc0),
        "sentences_base_sha256": sha256_file(args.sentences_base),
        "output_sha256": sha256_file(args.output),
        "output_records": output_count,
        "counts": dict(sorted(counts.items())),
        "policy": (
            "Only rows from sentences_CC0.csv are emitted. sentences_base.csv is "
            "used solely to derive translation-group IDs. Contributor names and "
            "the broader CC BY export are not ingested."
        ),
        "grouping": (
            "Base-zero sentences use their own sentence ID; translations use the "
            "base sentence ID; unknown bases use their own sentence ID."
        ),
        "privacy": (
            "Email, URL and IPv4 matches are excluded. Phone-like and 9+ digit "
            "sequences are retained with review flags. This is not full PII review."
        ),
        "caveat": (
            "The base relation is the source-provided translation parent, not a "
            "verified semantic-equivalence graph. Review translation-group leakage "
            "and duplicate text after global merge."
        ),
    }
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    print(json.dumps({"output": str(args.output), "records": output_count,
                      "counts": manifest["counts"], "manifest": str(manifest_path)},
                     ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sentences-cc0", required=True, type=Path)
    parser.add_argument("--sentences-base", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-release", default="weekly-2026-11-14")
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    args = parser.parse_args()
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    stage(args)


if __name__ == "__main__":
    main()
