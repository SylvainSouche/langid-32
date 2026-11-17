#!/usr/bin/env python3
"""Build a small, text-only Common Voice candidate sample from private Common Voice TSVs.

Raw TSVs stay on the ephemeral runner and are never uploaded or committed.
Only deterministic, deduplicated sentence text (up to 9,000/language) and an
aggregate report are written to the artifact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

EMAIL = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Z]{2,}(?![A-Za-z0-9_.-])")
URL = re.compile(r"(?i)(?:https?://[^\s<>]+|www\.[^\s<>]+)")
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
LONG_NUMBER = re.compile(r"\d{9,}")
PHONE = re.compile(r"(?<!\w)\+?\d[\d -]{7,}\d(?!\w)")
LANGUAGES = ("bg", "hr", "is", "cs", "da", "nl", "en", "et", "fi", "fr", "de", "el", "hu", "ga", "it", "lv", "lt", "mt", "pl", "pt", "ro", "sk", "sl", "es", "sv", "nb", "nn", "ru", "ja", "zh", "ko", "ar", "tr")


def norm(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def phone_like(text: str) -> bool:
    for match in PHONE.finditer(text):
        raw = match.group()
        digits = re.sub(r"\D", "", raw)
        if 9 <= len(digits) <= 15 and (raw.count(" ") + raw.count("-") >= 2 or "+" in raw):
            return True
    return False


def priority(language: str, text: str) -> str:
    return hashlib.sha256(f"langid-32-cv-v1\0{language}\0{text}".encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-language-cap", type=int, default=9000)
    args = parser.parse_args()
    candidates = defaultdict(dict)
    counts = Counter()
    for language in LANGUAGES:
        path = args.input_root / language / "validated_sentences.tsv"
        if not path.is_file():
            counts[f"{language}:missing_file"] += 1
            continue
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if not {"sentence_id", "sentence"}.issubset(reader.fieldnames or []):
                raise ValueError(f"{path}: unexpected TSV columns")
            for row in reader:
                counts[f"{language}:rows"] += 1
                if "is_used" in row and (row.get("is_used") or "").strip().lower() not in {"true", "1", "yes"}:
                    counts[f"{language}:not_validated_or_inactive"] += 1
                    continue
                text = norm(row.get("sentence") or "")
                if not text:
                    counts[f"{language}:empty"] += 1
                    continue
                if len(text) < 12 or len(text) > 500 or len(text.encode("utf-8")) > 1500:
                    counts[f"{language}:length_rejected"] += 1
                    continue
                if EMAIL.search(text) or URL.search(text):
                    counts[f"{language}:email_or_url_rejected"] += 1
                    continue
                if IPV4.search(text):
                    counts[f"{language}:ipv4_rejected"] += 1
                    continue
                if phone_like(text) or LONG_NUMBER.search(text):
                    counts[f"{language}:numeric_identifier_rejected"] += 1
                    continue
                if text in candidates[language]:
                    counts[f"{language}:within_language_duplicate"] += 1
                    continue
                sid = (row.get("sentence_id") or "").strip()
                group = hashlib.sha256(f"common-voice-v22:{language}:{text}".encode()).hexdigest()
                candidates[language][text] = group

    # Remove every occurrence of any normalized string shared by language labels.
    owners = defaultdict(set)
    for language, rows in candidates.items():
        for text in rows:
            owners[text].add(language)
    collisions = {text for text, langs in owners.items() if len(langs) > 1}
    for language in LANGUAGES:
        for text in collisions:
            if text in candidates[language]:
                del candidates[language][text]
                counts[f"{language}:cross_language_collision_removed"] += 1

    args.output.mkdir(parents=True, exist_ok=True)
    output_path = args.output / "common_voice_candidates.jsonl"
    final_counts = {}
    with output_path.open("w", encoding="utf-8", newline="\n") as out:
        for language in LANGUAGES:
            items = sorted(candidates[language].items(),
                           key=lambda item: priority(language, item[0]))
            before = len(items)
            items = items[:args.per_language_cap]
            final_counts[language] = {
                "eligible_after_privacy_dedup_collision_checks": before,
                "selected": len(items),
                "cap": args.per_language_cap,
            }
            for text, group in items:
                out.write(json.dumps({
                    "text": text,
                    "language": language,
                    "source": "common_voice_v22",
                    "source_release": "Common Voice Corpus 22.0",
                    "group_id": group,
                    "licence_id": "CC0-1.0",
                    "text_origin": "Hugging Face fsicoli/common_voice_22_0 transcript-only conversion",
                }, ensure_ascii=False, separators=(",", ":")) + "\n")
    report = {
        "source": "fsicoli/common_voice_22_0 (Common Voice 22.0)",
        "target_languages": list(LANGUAGES),
        "raw_tsvs_uploaded": False,
        "audio_saved": False,
        "selection": "validated_sentences.tsv; if is_used exists require true; NFC/whitespace normalization; 12-500 chars; <=1500 UTF-8 bytes; conservative PII/identifier exclusions; within-language deduplication; all-label collision removal; deterministic cap",
        "cross_language_collision_strings_removed": len(collisions),
        "per_language": final_counts,
        "counts": dict(sorted(counts.items())),
        "candidate_file_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "note": "Curated text-only candidate sample from an unofficial third-party Common Voice 22.0 conversion; retain source-specific licence and distribution-policy review.",
    }
    (args.output / "common_voice_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
