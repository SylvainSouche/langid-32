#!/usr/bin/env python3
"""Stage Tatoeba CC0 sentences with translation-base grouping and provenance."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config, acquisition_target

from langid32.merge import (EMAIL_RE, HTTP_FRAGMENT_RE, IPV4_RE, LONG_NUMBER_RE,
                            URL_RE, WEB_FRAGMENT_RE, has_phone_like)

CODES = {
    "bg": ("bul",), "hr": ("hrv",), "cs": ("ces",), "da": ("dan",),
    "nl": ("nld",), "en": ("eng",), "et": ("est",), "fi": ("fin",), "ca": ("cat",), "is": ("isl",),
    "fr": ("fra",), "de": ("deu",), "el": ("ell",), "hu": ("hun",),
    "ga": ("gle",), "it": ("ita",), "lv": ("lav",), "lt": ("lit",),
    "mt": ("mlt",), "pl": ("pol",), "pt": ("por",), "ro": ("ron",),
    "sk": ("slk",), "sl": ("slv",), "es": ("spa",), "sv": ("swe",),
    "nb": ("nob",), "nn": ("nno",), "ru": ("rus",), "ja": ("jpn",),
    "zh": ("cmn",), "ko": ("kor",), "ar": ("ara",), "tr": ("tur",),
}
CODE_TO_LANGUAGE = {code: lang for lang, codes in CODES.items() for code in codes}
def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def sha256_file(path: Path, chunk_bytes: int) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(chunk_bytes), b""):
            digest.update(block)
    return digest.hexdigest()


def stage(args):
    cfg = load_config(getattr(args, "config", None))
    source_rule = cfg["acquisition"]["source_rules"]["tatoeba_cc0"]
    target_languages = tuple(cfg["project"]["languages"])
    target_by_language = {
        language: (getattr(args, "target_per_language", None) or acquisition_target(cfg, "tatoeba_cc0", language))
        for language in target_languages
    }
    text_rules = cfg["acquisition"]["text"]
    chunk_bytes = cfg["execution"]["download_chunk_bytes"]
    batch_insert = cfg["execution"]["sqlite_insert_batch_size"]
    batch_join = cfg["execution"]["sqlite_join_batch_size"]
    args.min_chars = args.min_chars if args.min_chars is not None else text_rules["min_characters"]
    args.max_chars = args.max_chars if args.max_chars is not None else text_rules["max_characters"]
    args.max_bytes = args.max_bytes if args.max_bytes is not None else text_rules["max_utf8_bytes"]
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
                if language is None or language not in target_languages:
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
                if text_rules["exclude_email"] and EMAIL_RE.search(text):
                    counts["email_excluded"] += 1
                    continue
                if text_rules["exclude_url"] and (URL_RE.search(text) or WEB_FRAGMENT_RE.search(text) or HTTP_FRAGMENT_RE.search(text)):
                    counts["url_excluded"] += 1
                    continue
                if text_rules["exclude_ipv4"] and IPV4_RE.search(text):
                    counts["ipv4_excluded"] += 1
                    continue
                privacy_flags = []
                if has_phone_like(text):
                    privacy_flags.append("phone_like")
                    counts["phone_like_flagged"] += 1
                if LONG_NUMBER_RE.search(text):
                    privacy_flags.append("long_numeric_sequence")
                    counts["long_number_flagged"] += 1
                modified = fields[3] if len(fields) > 3 else ""
                batch.append((sentence_id, language, text, modified, None,
                              json.dumps(privacy_flags)))
                counts[f"accepted_before_base_join:{language}"] += 1
                if len(batch) >= batch_insert:
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
                if len(batch) >= batch_join:
                    db.executemany("UPDATE sentence SET base_id=? WHERE id=?", batch)
                    batch.clear()
        if batch:
            db.executemany("UPDATE sentence SET base_id=? WHERE id=?", batch)
        db.commit()

        output_count = 0
        selected_counts = Counter()
        with args.output.open("w", encoding="utf-8", newline="\n") as output:
            cursor = db.execute(
                "SELECT id, language, text, modified, base_id, privacy_flags "
                "FROM sentence ORDER BY id"
            )
            for sentence_id, language, text, modified, base_id, privacy_flags in cursor:
                if selected_counts[language] >= target_by_language.get(language, 0):
                    counts[f"over_target_cap:{language}"] += 1
                    continue
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
                selected_counts[language] += 1
                output_count += 1
        db.close()

    manifest = {
        "source": "Tatoeba sentences_CC0.csv + sentences_base.csv",
        "source_release": args.source_release,
        "source_licence": "CC0-1.0 (CC0 sentence export only)",
        "source_download_origin": "https://downloads.tatoeba.org/exports/",
        "sentences_cc0_sha256": sha256_file(args.sentences_cc0, chunk_bytes),
        "sentences_base_sha256": sha256_file(args.sentences_base, chunk_bytes),
        "output_sha256": sha256_file(args.output, chunk_bytes),
        "output_records": output_count,
        "selection": {"target_per_language": target_by_language, "selected_per_language": dict(selected_counts), "text_rules": text_rules},
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
            "Email, URL and IPv4 matches are excluded. Phone-like and long numeric "
            "sequences are retained with review flags according to the central configuration. This is not full PII review."
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
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("LANGID32_CONFIG", ROOT / "config/langid32.toml")) )
    parser.add_argument("--target-per-language", type=int, default=None)
    parser.add_argument("--min-chars", type=int, default=None)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--max-bytes", type=int, default=None)
    args = parser.parse_args()
    if ((args.min_chars is not None and args.min_chars < 1)
            or (args.max_chars is not None and args.min_chars is not None and args.max_chars < args.min_chars)
            or (args.max_bytes is not None and args.max_bytes < 1)):
        parser.error("invalid text length limits")
    stage(args)


if __name__ == "__main__":
    main()
