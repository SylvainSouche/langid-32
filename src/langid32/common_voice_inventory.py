"""Inventory Common Voice Scripted Speech locale metadata and sentence TSVs.

This is a read-only counter. It does not download data or copy sentence text
into the report. Point --data-root at extracted MDC locale archives.
"""
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import Counter
from pathlib import Path

TARGET_LOCALES = {
    "bg": ["bg"], "hr": ["hr"], "cs": ["cs"], "da": ["da"],
    "nl": ["nl"], "en": ["en"], "et": ["et"], "fi": ["fi"],
    "fr": ["fr"], "de": ["de"], "el": ["el"], "hu": ["hu"],
    "ga": ["ga-IE"], "it": ["it"], "lv": ["lv"], "lt": ["lt"],
    "mt": ["mt"], "pl": ["pl"], "pt": ["pt"], "ro": ["ro"],
    "sk": ["sk"], "sl": ["sl"], "es": ["es"], "sv": ["sv-SE"],
    "nb": ["nb-NO"], "nn": ["nn-NO"], "ru": ["ru"], "ja": ["ja"],
    "zh": ["zh-CN", "zh-TW"], "ko": ["ko"], "ar": ["ar"], "tr": ["tr"],
}


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def count_sentence_file(path: Path, min_chars: int, max_chars: int,
                        max_bytes: int, seen_all: set[str] | None = None,
                        seen_active: set[str] | None = None) -> dict[str, int | str]:
    counts = Counter()
    source_counts = Counter()
    domain_counts = Counter()
    seen_all = seen_all if seen_all is not None else set()
    seen_active = seen_active if seen_active is not None else set()
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"sentence_id", "sentence"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                f"{path}: expected columns {sorted(required)}, "
                f"got {reader.fieldnames}"
            )
        for row in reader:
            counts["rows"] += 1
            text = normalize(row.get("sentence") or "")
            if not text:
                counts["empty"] += 1
                continue
            counts["nonempty"] += 1
            used_value = (row.get("is_used") or "").strip().lower()
            is_active = used_value in {"true", "1", "yes"}
            if is_active:
                counts["is_used_true"] += 1
            elif used_value in {"false", "0", "no"}:
                counts["is_used_false"] += 1
            else:
                counts["is_used_unspecified"] += 1
            source = (row.get("source") or "").strip() or "(blank)"
            source_counts[source] += 1
            domains = (row.get("sentence_domain") or "").strip()
            if domains:
                for domain in domains.split(","):
                    domain_counts[domain.strip()] += 1
            if len(text) < min_chars:
                counts["too_short"] += 1
                continue
            if len(text) > max_chars:
                counts["too_long"] += 1
                continue
            if len(text.encode("utf-8")) > max_bytes:
                counts["too_many_bytes"] += 1
                continue
            counts["within_length_limits"] += 1
            if text in seen_all:
                counts["duplicate_normalized_text"] += 1
            else:
                seen_all.add(text)
                counts["unique_within_target_language"] += 1
            if is_active:
                counts["is_used_true_within_length_limits"] += 1
                if text in seen_active:
                    counts["duplicate_is_used_true_text"] += 1
                else:
                    seen_active.add(text)
                    counts["unique_is_used_true_within_target_language"] += 1
    counts["source_counts_json"] = json.dumps(
        dict(sorted(source_counts.items())), ensure_ascii=False, sort_keys=True
    )
    counts["domain_counts_json"] = json.dumps(
        dict(sorted(domain_counts.items())), ensure_ascii=False, sort_keys=True
    )
    return dict(counts)


def find_locale_files(root: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in root.rglob("validated_sentences.tsv"):
        locale = path.parent.name
        if locale in {code for codes in TARGET_LOCALES.values() for code in codes}:
            if locale in found:
                raise ValueError(
                    f"Multiple validated_sentences.tsv files found for {locale}; "
                    "use one extracted release per --data-root"
                )
            found[locale] = path
    return found


def build_rows(release_json: Path, data_root: Path | None,
               min_chars: int, max_chars: int, max_bytes: int) -> list[dict]:
    release = json.loads(release_json.read_text(encoding="utf-8"))
    locale_stats = release.get("locales", {})
    files = find_locale_files(data_root) if data_root else {}
    rows = []
    seen_all_by_language = {language: set() for language in TARGET_LOCALES}
    seen_active_by_language = {language: set() for language in TARGET_LOCALES}
    for language, locales in TARGET_LOCALES.items():
        for locale in locales:
            stats = locale_stats.get(locale)
            path = files.get(locale)
            measured = (
                count_sentence_file(
                    path, min_chars, max_chars, max_bytes,
                    seen_all_by_language[language],
                    seen_active_by_language[language],
                ) if path else {}
            )
            rows.append({
                "language": language,
                "locale": locale,
                "metadata_validated_sentences": (
                    stats.get("validatedSentences", "") if stats else ""
                ),
                "metadata_unvalidated_sentences": (
                    stats.get("unvalidatedSentences", "") if stats else ""
                ),
                "metadata_clips": stats.get("clips", "") if stats else "",
                "metadata_users": stats.get("users", "") if stats else "",
                "tsv_status": "counted" if path else (
                    "not_found" if data_root else "not_measured"
                ),
                "tsv_path": str(path) if path else "",
                **measured,
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-json", required=True, type=Path)
    parser.add_argument("--data-root", type=Path,
                        help="Root containing extracted locale archives")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    args = parser.parse_args()
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    rows = build_rows(args.release_json, args.data_root,
                      args.min_chars, args.max_chars, args.max_bytes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "output": str(args.output),
        "languages": len(TARGET_LOCALES),
        "locale_files_found": sum(row["tsv_status"] == "counted" for row in rows),
        "locale_files_expected": sum(len(x) for x in TARGET_LOCALES.values()),
    }, indent=2))


if __name__ == "__main__":
    main()
