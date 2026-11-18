#!/usr/bin/env python3
"""Merge source-normalized JSONL files into a globally deduplicated corpus candidate.

Each input row must contain text, language, source, source_release, group_id,
licence_id and text_origin. Optional provenance is retained in the private
records.jsonl sidecar. Group IDs are namespaced by source by the caller; IDs
shared across languages within one source must remain identical.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from urllib.parse import urlparse
from collections import Counter, defaultdict
from pathlib import Path

LANGUAGES = (
    "bg hr cs da nl en et fi fr de el hu ga it lv lt mt pl pt ro sk sl es sv "
    "nb nn ru ja zh ko ar tr"
).split()
SPLITS = ("train", "validation", "test")
EMAIL_RE = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Z]{2,}(?![A-Za-z0-9_.-])")
URL_RE = re.compile(
    r"(?i)(?:https?://[^\s<>]+|(?<![A-Za-z0-9])www\.[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Z]{2,}(?:/[^\s<>]*)?)"
)
WEB_FRAGMENT_RE = re.compile(r"(?i)(?<![A-Za-z0-9])www\.(?=$|[\s,;])")
HTTP_FRAGMENT_RE = re.compile(r"(?i)https?://(?=$|[\s,;])")
IPV4_RE = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\b"
)
PHONE_CANDIDATE_RE = re.compile(r"(?<!\w)\+?\d[\d -]{7,}\d(?!\w)")
LONG_NUMBER_RE = re.compile(r"\d{9,}")


def has_phone_like(text: str) -> bool:
    for match in PHONE_CANDIDATE_RE.finditer(text):
        value = match.group()
        digits = re.sub(r"\D", "", value)
        if not 9 <= len(digits) <= 15:
            continue
        if value.count(" ") + value.count("-") < 2 and "+" not in value:
            continue
        if re.fullmatch(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", value):
            continue
        return True
    return False


def normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def fraction(group_id: str, seed: str) -> float:
    raw = hashlib.sha256(f"{seed}\0{group_id}".encode("utf-8")).digest()[:8]
    return int.from_bytes(raw, "big") / 2**64


def split_for(group_id: str, seed: str, validation: float, test: float) -> str:
    value = fraction(group_id, seed)
    if value < test:
        return "test"
    if value < test + validation:
        return "validation"
    return "train"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_exclusions(path: Path | None):
    """Load active source/document exclusions from JSONL or CSV."""
    if path is None:
        return []
    with path.open("r", encoding="utf-8", newline="") as stream:
        if path.suffix.lower() == ".csv":
            rows = list(csv.DictReader(stream))
        else:
            rows = [json.loads(line) for line in stream if line.strip()]
    active = []
    allowed_scopes = {"document", "url", "domain", "archive-batch", "source-dataset"}
    for number, row in enumerate(rows, 1):
        if str(row.get("status", "active")).lower() != "active":
            continue
        scope = str(row.get("scope", "")).lower()
        if scope not in allowed_scopes:
            raise ValueError(f"{path}:{number}: invalid exclusion scope {scope!r}")
        if not row.get("reason_code") or not row.get("effective_at"):
            raise ValueError(f"{path}:{number}: reason_code and effective_at are required")
        required_key = {
            "document": ("source_key",),
            "url": ("url_sha256", "source_url"),
            "domain": ("domain",),
            "archive-batch": ("archive_batch",),
            "source-dataset": ("source",),
        }[scope]
        if not any(row.get(key) for key in required_key):
            raise ValueError(
                f"{path}:{number}: scope {scope!r} requires one of {required_key}"
            )
        active.append(row)
    return active


def _row_source_url(row):
    provenance = row.get("provenance", {})
    if not isinstance(provenance, dict):
        provenance = {}
    return str(
        provenance.get("source_url") or provenance.get("url") or
        provenance.get("canonical_url") or row.get("source_url") or
        row.get("url") or row.get("canonical_url") or ""
    )


def _row_domain(url):
    try:
        return (urlparse(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""


def _matches_exclusion(row, rule):
    provenance = row.get("provenance", {}) if isinstance(row.get("provenance"), dict) else {}
    source = str(row.get("source", ""))
    release = str(row.get("source_release", ""))
    group = str(row.get("group_id", ""))
    url = _row_source_url(row)
    url_hash = digest(url) if url else ""
    scope = str(rule["scope"]).lower()
    if scope == "document":
        key = str(rule.get("source_key") or "")
        return bool(key and key in {group, f"{source}:{release}:{group}",
                                    str(provenance.get("source_key") or "")})
    if scope == "url":
        expected = str(rule.get("url_sha256") or "")
        exact_url = str(rule.get("source_url") or "")
        return bool((expected and url_hash == expected) or
                    (exact_url and url == exact_url))
    if scope == "domain":
        domain = str(rule.get("domain") or "").lower().rstrip(".")
        actual = _row_domain(url)
        return bool(domain and (actual == domain or actual.endswith("." + domain)))
    if scope == "archive-batch":
        batch = str(rule.get("archive_batch") or "")
        return bool(batch and batch == str(provenance.get("archive_batch") or ""))
    if scope == "source-dataset":
        return source == str(rule.get("source") or "") and (
            not rule.get("source_release") or release == str(rule["source_release"])
        )
    return False


def read_inputs(paths: list[Path], args):
    rejected = Counter()
    rows = []
    exclusions = load_exclusions(args.exclusions)
    for path in paths:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
                required = ("text", "language", "source", "source_release",
                            "group_id", "licence_id", "text_origin")
                missing = [key for key in required if not row.get(key)]
                if missing:
                    raise ValueError(f"{path}:{line_number}: missing {', '.join(missing)}")
                language = str(row["language"]).lower()
                if language not in LANGUAGES:
                    rejected["language_not_in_target_set"] += 1
                    continue
                text = normalize_text(str(row["text"]))
                if not text:
                    rejected["empty_text"] += 1
                    continue
                if len(text) < args.min_chars or len(text) > args.max_chars:
                    rejected["outside_character_limits"] += 1
                    continue
                if len(text.encode("utf-8")) > args.max_bytes:
                    rejected["outside_byte_limit"] += 1
                    continue
                if EMAIL_RE.search(text):
                    rejected["email_excluded"] += 1
                    continue
                if URL_RE.search(text) or WEB_FRAGMENT_RE.search(text) or HTTP_FRAGMENT_RE.search(text):
                    rejected["url_excluded"] += 1
                    continue
                if IPV4_RE.search(text):
                    rejected["ipv4_excluded"] += 1
                    continue
                provenance = row.get("provenance", {})
                if not isinstance(provenance, dict):
                    provenance = {}
                privacy_flags = provenance.get("privacy_flags", [])
                if not isinstance(privacy_flags, list):
                    privacy_flags = []
                privacy_flags = {str(flag) for flag in privacy_flags}
                if has_phone_like(text):
                    privacy_flags.add("phone_like")
                if LONG_NUMBER_RE.search(text):
                    privacy_flags.add("long_numeric_sequence")
                provenance["privacy_flags"] = sorted(privacy_flags)
                group = str(row["group_id"]).strip()
                if not group:
                    rejected["empty_group_id"] += 1
                    continue
                source = str(row["source"]).strip()
                normalized = {
                    "text": text,
                    "language": language,
                    "source": source,
                    "source_release": str(row["source_release"]),
                    "group_id": group,
                    "licence_id": str(row["licence_id"]),
                    "text_origin": str(row["text_origin"]),
                    "provenance": provenance,
                }
                split_group = str(row.get("split_group_id") or group)
                normalized["split_group_id"] = split_group
                normalized["split"] = split_for(
                    split_group, args.seed, args.validation_fraction, args.test_fraction
                )
                # A deterministic source-aware ordering selects one copy when
                # the same normalized sentence occurs in multiple sources.
                normalized["_priority"] = digest(
                    f"{args.seed}\0{language}\0{text}\0{source}\0{group}"
                )
                rows.append(normalized)
    if exclusions:
        matched_rules = Counter()
        excluded_groups = set()
        excluded_split_groups = set()
        for row in rows:
            for rule in exclusions:
                if _matches_exclusion(row, rule):
                    matched_rules[str(rule.get("case_id") or rule.get("reason_code"))] += 1
                    excluded_groups.add(row["group_id"])
                    excluded_split_groups.add(row["split_group_id"])
                    break
        kept = []
        for row in rows:
            if row["group_id"] in excluded_groups or row["split_group_id"] in excluded_split_groups:
                rejected["source_exclusion_registry"] += 1
            else:
                kept.append(row)
        rows = kept
        rejected["exclusion_rules_matched"] = sum(matched_rules.values())
    return rows, rejected


def merge(args):
    rows, rejected = read_inputs(args.inputs, args)
    rows.sort(key=lambda row: (row["language"], row["_priority"]))
    seen_text = set()
    selected = []
    duplicate_by_source_pair = Counter()
    first_source = {}
    group_splits = {}
    for row in rows:
        key = (row["language"], row["text"])
        if key in seen_text:
            rejected["duplicate_text_across_inputs_or_sources"] += 1
            original = first_source[key]
            duplicate_by_source_pair[f"{original}->{row['source']}"] += 1
            continue
        seen_text.add(key)
        first_source[key] = row["source"]
        previous = group_splits.setdefault(row["group_id"], row["split"])
        if previous != row["split"]:
            raise ValueError(f"group split inconsistency: {row['group_id']}")
        selected.append(row)

    # Apply the cap only after global normalization, deduplication and split
    # assignment. A source is not silently given priority or a fixed quota.
    by_bucket = defaultdict(list)
    for row in selected:
        by_bucket[(row["language"], row["split"])].append(row)
    caps = {
        "train": max(0, args.max_per_language
                     - round(args.max_per_language * args.validation_fraction)
                     - round(args.max_per_language * args.test_fraction)),
        "validation": round(args.max_per_language * args.validation_fraction),
        "test": round(args.max_per_language * args.test_fraction),
    } if args.max_per_language else {name: 0 for name in SPLITS}

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    source_counts = Counter()
    output_hashes = {}
    public_keys = ("text", "language", "source", "split")
    for split in SPLITS:
        public_path = output / f"{split}.jsonl"
        with public_path.open("w", encoding="utf-8", newline="\n") as public:
            for language in LANGUAGES:
                bucket = sorted(by_bucket[(language, split)],
                                key=lambda row: row["_priority"])
                if args.max_per_language:
                    bucket = bucket[:caps[split]]
                for row in bucket:
                    public.write(json.dumps(
                        {key: row[key] for key in public_keys},
                        ensure_ascii=False, separators=(",", ":")
                    ) + "\n")
                    counts[f"{language}:{split}"] += 1
                    source_counts[f"{row['source']}:{language}:{split}"] += 1
        output_hashes[public_path.name] = digest(public_path.read_text(encoding="utf-8"))

    if args.require_exact_counts and args.max_per_language:
        shortfalls = {
            f"{language}:{split}": {
                "expected": caps[split],
                "actual": counts[f"{language}:{split}"],
            }
            for language in LANGUAGES for split in SPLITS
            if counts[f"{language}:{split}"] != caps[split]
        }
        if shortfalls:
            raise ValueError(f"exact per-language split target not met: {shortfalls}")

    internal_path = output / "records.jsonl"
    internal_rows = []
    for split in SPLITS:
        for language in LANGUAGES:
            bucket = sorted(by_bucket[(language, split)],
                            key=lambda row: row["_priority"])
            if args.max_per_language:
                bucket = bucket[:caps[split]]
            for row in bucket:
                internal_rows.append({key: value for key, value in row.items()
                                      if key != "_priority"})
    with internal_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in internal_rows:
            stream.write(json.dumps(row, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
    output_hashes[internal_path.name] = digest(internal_path.read_text(encoding="utf-8"))

    privacy_flag_counts = Counter()
    output_groups = set()
    output_groups_by_source = defaultdict(set)
    for row in internal_rows:
        flags = row.get("provenance", {}).get("privacy_flags", [])
        privacy_flag_counts.update(flags)
        output_groups.add(row["group_id"])
        output_groups_by_source[row["source"]].add(row["group_id"])

    manifest = {
        "schema_version": 1,
        "project": "langid-32",
        "status": "candidate_not_rights_cleared",
        "languages": LANGUAGES,
        "input_files": [{"name": path.name, "sha256": digest(path.read_text(encoding="utf-8"))}
                        for path in args.inputs],
        "preparation": {
            "normalization": "Unicode NFC; collapse whitespace",
            "min_chars": args.min_chars,
            "max_chars": args.max_chars,
            "max_bytes": args.max_bytes,
            "seed": args.seed,
            "validation_fraction": args.validation_fraction,
            "test_fraction": args.test_fraction,
            "max_per_language_total": args.max_per_language,
            "split_caps": caps,
            "deduplication": "exact normalized text within language across all inputs",
            "group_split": "deterministic hash of split_group_id (or group_id); shared groups stay in one split",
            "source_balancing": "none; source counts are reported, no hidden quotas",
            "privacy_filters": "exclude email, URL and IPv4 matches; retain phone-like and 9+ digit sequences with flags",
            "source_exclusion_registry": str(args.exclusions) if args.exclusions else None,
            "exclusion_matching": "document, exact URL/hash, domain, archive batch or source dataset; any matched group/split group is cascaded out",
        },
        "counts": dict(sorted(counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "rejected": dict(sorted(rejected.items())),
        "duplicate_source_pairs": dict(sorted(duplicate_by_source_pair.items())),
        "privacy_flag_counts": dict(sorted(privacy_flag_counts.items())),
        "group_count": len(output_groups),
        "candidate_group_count": len(group_splits),
        "group_counts_by_source": {source: len(groups) for source, groups in sorted(output_groups_by_source.items())},
        "output_sha256": output_hashes,
        "exclusion_registry": {"path": str(args.exclusions) if args.exclusions else None,
                              "active_rules_loaded": len(load_exclusions(args.exclusions)),
                              "excluded_rows": rejected.get("source_exclusion_registry", 0)},
        "rights_note": (
            "Technical deduplication is not a rights clearance. Each source's licence, "
            "database rights, underlying-text rights, attribution and privacy conditions "
            "must be reviewed independently before publication or redistribution."
        ),
        "privacy_note": (
            "Email, URL and IPv4 matches are excluded in the global merge. "
            "Phone-like and 9+ digit sequences are retained with flags. The provenance "
            "sidecar is internal; full PII review is still required."
        ),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"counts": manifest["counts"], "source_counts": manifest["source_counts"],
                      "rejected": manifest["rejected"], "groups": manifest["group_count"]},
                     ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", dest="inputs", action="append", required=True, type=Path,
                        help="Source-normalized JSONL; repeat for each source")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--exclusions", type=Path, default=None,
                        help="Active source/document exclusion registry (JSONL or CSV)")
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    parser.add_argument("--max-per-language", type=int, default=20000,
                        help="Total cap per language; 0 disables the cap")
    parser.add_argument("--validation-fraction", type=float, default=0.10)
    parser.add_argument("--test-fraction", type=float, default=0.10)
    parser.add_argument("--seed", default="langid-32-fineweb2-v1")
    parser.add_argument("--require-exact-counts", action="store_true",
                        help="Fail unless every target language reaches every split cap")
    args = parser.parse_args()
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    if args.max_per_language < 0:
        parser.error("--max-per-language must be >= 0")
    if not 0 <= args.validation_fraction < 1 or not 0 <= args.test_fraction < 1:
        parser.error("split fractions must be in [0, 1)")
    if args.validation_fraction + args.test_fraction >= 1:
        parser.error("validation + test fractions must be less than 1")
    merge(args)


if __name__ == "__main__":
    main()
