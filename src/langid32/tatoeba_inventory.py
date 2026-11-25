"""Count Tatoeba's CC0 sentence export by langid-32 target language.

Inputs are the tab-separated files from Tatoeba's weekly exports:
sentences_CC0.csv and sentences_base.csv. No sentence text is written to
the report. The base relation is retained only as a group identifier/count.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path

TATOEBA_CODES = {
    "bg": ["bul"], "hr": ["hrv"], "cs": ["ces"], "da": ["dan"],
    "nl": ["nld"], "en": ["eng"], "et": ["est"], "fi": ["fin"],
    "fr": ["fra"], "de": ["deu"], "el": ["ell"], "hu": ["hun"],
    "ga": ["gle"], "it": ["ita"], "lv": ["lav"], "lt": ["lit"],
    "mt": ["mlt"], "pl": ["pol"], "pt": ["por"], "ro": ["ron"],
    "sk": ["slk"], "sl": ["slv"], "es": ["spa"], "sv": ["swe"],
    "nb": ["nob"], "nn": ["nno"], "ru": ["rus"], "ja": ["jpn"],
    "zh": ["cmn"], "ko": ["kor"], "ar": ["ara"], "tr": ["tur"],
}


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def read_sentences(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        yield from csv.reader(stream, delimiter="\t")


def read_base(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        yield from csv.reader(stream, delimiter="\t")


def inventory(sentences_path: Path, base_path: Path | None,
              min_chars: int, max_chars: int, max_bytes: int) -> list[dict]:
    code_to_target = {
        code: target for target, codes in TATOEBA_CODES.items() for code in codes
    }
    with tempfile.TemporaryDirectory(prefix="langid32-tatoeba-") as temp:
        db = sqlite3.connect(Path(temp) / "inventory.sqlite")
        db.execute("""
            CREATE TABLE sentences (
                sentence_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL,
                text TEXT NOT NULL,
                eligible INTEGER NOT NULL,
                base_id TEXT
            )
        """)
        db.execute("CREATE INDEX sentence_language ON sentences(language)")
        raw = Counter()
        empty = Counter()
        length_rejected = Counter()
        invalid_id = Counter()
        batch = []
        for fields in read_sentences(sentences_path):
            if len(fields) < 3:
                continue
            sentence_id, code, original_text = fields[:3]
            target = code_to_target.get(code)
            if target is None:
                continue
            raw[target] += 1
            text = normalize(original_text)
            if not text:
                empty[target] += 1
                continue
            eligible = (
                min_chars <= len(text) <= max_chars
                and len(text.encode("utf-8")) <= max_bytes
            )
            if not eligible:
                length_rejected[target] += 1
            try:
                numeric_id = int(sentence_id)
            except ValueError:
                invalid_id[target] += 1
                continue
            batch.append((numeric_id, target, text, int(eligible), None))
            if len(batch) >= 2000:
                db.executemany(
                    "INSERT OR REPLACE INTO sentences VALUES (?,?,?,?,?)", batch
                )
                batch.clear()
        if batch:
            db.executemany(
                "INSERT OR REPLACE INTO sentences VALUES (?,?,?,?,?)", batch
            )
        db.commit()

        if base_path:
            cc0_ids = {
                row[0] for row in db.execute("SELECT sentence_id FROM sentences")
            }
            batch = []
            for fields in read_base(base_path):
                if len(fields) < 2:
                    continue
                sentence_id, base_id = fields[:2]
                try:
                    sentence_id = int(sentence_id)
                except ValueError:
                    continue
                if sentence_id not in cc0_ids:
                    continue
                batch.append((base_id, sentence_id))
                if len(batch) >= 5000:
                    db.executemany(
                        "UPDATE sentences SET base_id=? WHERE sentence_id=?", batch
                    )
                    batch.clear()
            if batch:
                db.executemany(
                    "UPDATE sentences SET base_id=? WHERE sentence_id=?", batch
                )
            db.commit()

        rows = []
        for target in TATOEBA_CODES:
            stats = db.execute("""
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT CASE WHEN eligible=1 THEN text END),
                    SUM(CASE WHEN eligible=1 THEN 1 ELSE 0 END),
                    SUM(CASE WHEN eligible=1 AND base_id='0' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN eligible=1 AND CAST(base_id AS INTEGER)>0 THEN 1 ELSE 0 END),
                    SUM(CASE WHEN eligible=1 AND (base_id IS NULL OR base_id='\\N') THEN 1 ELSE 0 END),
                    COUNT(DISTINCT CASE WHEN eligible=1 THEN
                        CASE WHEN CAST(base_id AS INTEGER)>0 THEN base_id
                             ELSE CAST(sentence_id AS TEXT) END
                    END)
                FROM sentences WHERE language=?
            """, (target,)).fetchone()
            rows.append({
                "language": target,
                "iso639_3_codes": ";".join(TATOEBA_CODES[target]),
                "cc0_rows": raw[target],
                "empty_text": empty[target],
                "outside_length_limits": length_rejected[target],
                "invalid_sentence_id": invalid_id[target],
                "stored_rows": stats[0] or 0,
                "unique_eligible_text": stats[1] or 0,
                "eligible_rows": stats[2] or 0,
                "eligible_originals_base_zero": stats[3] or 0,
                "eligible_translations_base_positive": stats[4] or 0,
                "eligible_base_unknown": stats[5] or 0,
                "eligible_translation_groups": stats[6] or 0,
                "base_relation_status": "joined" if base_path else "not_joined",
            })
        db.close()
        return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sentences-cc0", required=True, type=Path)
    parser.add_argument("--sentences-base", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    args = parser.parse_args()
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    rows = inventory(args.sentences_cc0, args.sentences_base,
                     args.min_chars, args.max_chars, args.max_bytes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "output": str(args.output),
        "target_languages": len(TATOEBA_CODES),
        "languages_with_cc0_rows": sum(row["cc0_rows"] > 0 for row in rows),
        "total_cc0_rows_in_target_languages": sum(row["cc0_rows"] for row in rows),
    }, indent=2))


if __name__ == "__main__":
    main()
