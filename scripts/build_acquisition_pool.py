#!/usr/bin/env python3
"""Build the filtered, pre-JQL acquisition pool from source JSONL records.

This stage preserves original source IDs, filters before quota accounting, and
never performs final language/source balancing or candidate selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config, acquisition_target, source_quota_key

EMAIL = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Z]{2,}(?![A-Za-z0-9_.-])")
URL = re.compile(r"(?i)(?:https?://[^\s<>]+|www\.[^\s<>]+)")
IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
PHONE = re.compile(r"(?<!\w)\+?\d[\d ()-]{7,}\d(?!\w)")
LONG_NUMBER = re.compile(r"\d{9,}")
SENSITIVE_FLAGS = ("personal_name", "person_name", "personal_address", "home_address",
                   "phone", "email", "private_person", "pii", "sensitive_personal")
UNCERTAIN_FLAGS = ("privacy_uncertain", "possible_personal", "possible_address",
                   "possible_name", "ner_uncertain", "needs_privacy_review")
REQUIRED = ("text", "language", "source", "source_release", "group_id",
            "licence_id", "text_origin")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def reject_reason(row: dict, text: str, rules: dict) -> str | None:
    provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
    flags = provenance.get("privacy_flags", [])
    if not isinstance(flags, list):
        flags = []
    flags = [str(flag).lower() for flag in flags]
    if any(token in flag for flag in flags for token in SENSITIVE_FLAGS):
        return "source_privacy_flag"
    if any(token in flag for flag in flags for token in UNCERTAIN_FLAGS):
        return "privacy_uncertain_quarantine"
    if rules.get("exclude_email", True) and EMAIL.search(text):
        return "email"
    if rules.get("exclude_url", True) and URL.search(text):
        return "url"
    if rules.get("exclude_ipv4", True) and IPV4.search(text):
        return "ipv4"
    match = PHONE.search(text)
    if rules.get("exclude_phone_like", True) and match:
        digits = re.sub(r"\D", "", match.group())
        if int(rules.get("phone_min_digits", 9)) <= len(digits) <= int(rules.get("phone_max_digits", 15)):
            return "phone_like"
    if rules.get("exclude_long_numeric_sequences", True) and LONG_NUMBER.search(text):
        return "long_numeric_sequence"
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-root", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    ap.add_argument("--exclude-source", action="append", default=[])
    args = ap.parse_args()

    cfg = load_config(args.config)
    acq = cfg["acquisition"]
    global_rules = acq["text"]
    languages = set(cfg["project"]["languages"])
    files = sorted(p for p in args.input_root.rglob("*.jsonl")
                   if p.is_file() and args.output_dir not in p.parents)
    if not files:
        raise SystemExit(f"No JSONL source records found under {args.input_root}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.output_dir / "records.jsonl"
    counts_in = Counter()
    counts_out = Counter()
    rejected = Counter()
    source_counts = Counter()
    seen = defaultdict(set)
    quarantine = Counter()
    source_file_rows = []

    with records_path.open("w", encoding="utf-8", newline="\n") as out:
        for path in files:
            file_in = file_out = 0
            for line_no, line in enumerate(path.open("r", encoding="utf-8"), 1):
                if not line.strip():
                    continue
                file_in += 1
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
                missing = [key for key in REQUIRED if not row.get(key)]
                if missing:
                    raise ValueError(f"{path}:{line_no}: missing {', '.join(missing)}")
                source = str(row["source"])
                language = str(row["language"]).lower()
                if source in args.exclude_source:
                    rejected[(source, language, "explicitly_excluded")] += 1
                    continue
                if language not in languages:
                    rejected[(source, language, "language_not_in_project")] += 1
                    continue
                try:
                    limit = acquisition_target(cfg, source, language)
                except ValueError as exc:
                    reason = "source_excluded_by_policy" if "excluded by source policy" in str(exc) else "source_not_registered_or_language_not_approved"
                    rejected[(source, language, reason)] += 1
                    continue

                text = normalize_text(str(row["text"]))
                rules = dict(global_rules)
                normalized_source = source.replace("-", "_")
                source_rule = cfg["acquisition"].get("source_rules", {}).get(normalized_source, {})
                if not source_rule:
                    matches = [(len(k), v) for k, v in cfg["acquisition"].get("source_rules", {}).items()
                               if normalized_source.startswith(k + ":") or normalized_source.startswith(k + "_")]
                    if matches:
                        source_rule = max(matches, key=lambda x: x[0])[1]
                rules.update(source_rule.get("text", {}))
                letters = sum(ch.isalpha() for ch in text)
                if (not text or len(text) < int(rules.get("min_characters", 12))
                        or len(text) > int(rules.get("max_characters", 500))
                        or len(text.encode("utf-8")) > int(rules.get("max_utf8_bytes", 1500))
                        or letters < int(rules.get("min_letter_characters", 8))
                        or letters / max(len(text), 1) < float(rules.get("min_letter_ratio", 0.45))):
                    rejected[(source, language, "text_quality_or_length")] += 1
                    continue

                reason = reject_reason(row, text, rules)
                if reason:
                    rejected[(source, language, reason)] += 1
                    if reason == "privacy_uncertain_quarantine":
                        quarantine[(source, language)] += 1
                    continue

                key = (source, language)
                if text in seen[key]:
                    rejected[(source, language, "duplicate_within_original_source_language")] += 1
                    continue
                quota_key = (source_quota_key(cfg, source), language)
                if source_counts[quota_key] >= limit:
                    rejected[(source, language, "source_language_cap_reached")] += 1
                    continue

                seen[key].add(text)
                source_counts[quota_key] += 1
                counts_out[(source, language)] += 1
                row["text"] = text
                row["source"] = source
                provenance = row.get("provenance")
                if not isinstance(provenance, dict):
                    provenance = {}
                provenance["source_original_name"] = source
                provenance.setdefault("privacy_flags", [])
                row["provenance"] = provenance
                out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                file_out += 1
            source_file_rows.append({"path": str(path.relative_to(args.input_root)),
                                     "sha256": sha256(path), "rows_in": file_in, "rows_retained": file_out})
            counts_in[str(path.relative_to(args.input_root))] += file_in

    def matrix(counter):
        return [{"source": source, "language": language, "count": int(count)}
                for (source, language), count in sorted(counter.items())]

    manifest = {
        "status": "filtered_pre_jql_acquisition_pool",
        "policy": {
            "filter_before_quota": True,
            "deduplicate_before_quota": True,
            "quota_unit": "original source identifier x language (except explicitly declared quota_key)",
            "default_cap_per_source_language": int(acq["first_pass_target_per_source_language"]),
            "personal_names_and_addresses": "source privacy flags are enforced; multilingual name/address NER is not yet wired, so absence of a flag is not evidence of absence",
            "uncertain_privacy_action": acq["text"].get("privacy_uncertain_action", "quarantine"),
            "quarantine_content_retained": False,
            "final_30k_selection": "deferred_pending_user_review"
        },
        "files": source_file_rows,
        "input_rows_by_file": dict(counts_in),
        "retained_by_source_language": matrix(counts_out),
        "rejected_by_source_language_reason": [
            {"source": s, "language": l, "reason": reason, "count": int(n)}
            for (s, l, reason), n in sorted(rejected.items())
        ],
        "privacy_uncertain_quarantine_counts": matrix(quarantine),
        "retained_rows": int(sum(counts_out.values())),
        "records_sha256": sha256(records_path),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "retained_rows": manifest["retained_rows"],
                      "records": str(records_path), "manifest": str(args.output_dir / "manifest.json")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
