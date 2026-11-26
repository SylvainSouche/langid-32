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

from langid32.settings import load_config
from langid32.privacy import screen_record, sanitize_provenance

CONFIG = load_config()
LANGUAGES = tuple(CONFIG["project"]["languages"])
TEXT_RULES = CONFIG["acquisition"]["text"]
PRIVACY_RULES = CONFIG["candidate"]["privacy"]
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
PHONE_CANDIDATE_RE = re.compile(r"(?<!\w)\+?\d[\d -]{" + str(PRIVACY_RULES["phone_candidate_min_intervening_characters"]) + r",}\d(?!\w)")
LONG_NUMBER_RE = re.compile(r"\d{" + str(PRIVACY_RULES["long_numeric_min_digits"]) + r",}")


def has_phone_like(text: str) -> bool:
    for match in PHONE_CANDIDATE_RE.finditer(text):
        value = match.group()
        digits = re.sub(r"\D", "", value)
        if not PRIVACY_RULES["phone_min_digits"] <= len(digits) <= PRIVACY_RULES["phone_max_digits"]:
            continue
        if value.count(" ") + value.count("-") < PRIVACY_RULES["phone_min_separators"] and "+" not in value:
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


def original_source_identity(row: dict) -> str:
    provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
    return str(provenance.get("source_original_name") or row.get("source") or "").strip()


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
        provenance.get("source_url") or provenance.get("source_document_url") or
        provenance.get("document_url") or provenance.get("url") or
        provenance.get("canonical_url") or provenance.get("source_archive_url") or
        provenance.get("archive_url") or row.get("source_url") or
        row.get("source_document_url") or row.get("source_archive_url") or
        row.get("url") or row.get("canonical_url") or ""
    )


def _row_domain(url):
    try:
        return (urlparse(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""


def _matches_exclusion(row, rule):
    provenance = row.get("provenance", {}) if isinstance(row.get("provenance"), dict) else {}
    source = original_source_identity(row)
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
    source_seen = defaultdict(set)
    source_retained = Counter()
    source_limit = getattr(args, "max_sentences_per_source", 0)
    exclusions_path = getattr(args, "exclusions", None)
    exclusions = load_exclusions(exclusions_path)
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
                row, removed_top_metadata = sanitize_provenance(row)
                row["provenance"], removed_provenance_metadata = sanitize_provenance(
                    row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
                )
                removed_metadata = set(removed_top_metadata) | set(removed_provenance_metadata)
                if removed_metadata:
                    rejected["personal_metadata_fields_removed"] += len(removed_metadata)
                privacy_result = screen_record(row, uncertain_action=CONFIG["acquisition"]["text"]["privacy_uncertain_action"])
                if not privacy_result.accepted:
                    rejected["privacy_" + privacy_result.status] += 1
                    for flag in privacy_result.flags:
                        rejected["privacy_flag_" + flag] += 1
                    continue
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
                if TEXT_RULES["exclude_email"] and EMAIL_RE.search(text):
                    rejected["email_excluded"] += 1
                    continue
                if TEXT_RULES["exclude_url"] and (URL_RE.search(text) or WEB_FRAGMENT_RE.search(text) or HTTP_FRAGMENT_RE.search(text)):
                    rejected["url_excluded"] += 1
                    continue
                if TEXT_RULES["exclude_ipv4"] and IPV4_RE.search(text):
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
                if not provenance.get("rights_status"):
                    source_name = str(row["source"])
                    if source_name.startswith(("fineweb", "fineweb2")):
                        provenance["rights_status"] = "hold_underlying_web_text_rights_unresolved"
                    elif source_name == "common_voice_v22":
                        provenance["rights_status"] = "cc0_hf_hosted_dataset_claim"
                    elif source_name == "common_voice_v27":
                        provenance["rights_status"] = "hold_locale_terms_acceptance_not_recorded"
                    elif source_name == "dgt-tm-2021":
                        provenance["rights_status"] = "hold_underlying_document_rights_review_attribution_required"
                    elif source_name == "tatoeba-cc0":
                        provenance["rights_status"] = "cc0_export_rows_only"
                    else:
                        provenance["rights_status"] = "rights_review_required"
                group = str(row["group_id"]).strip()
                if not group:
                    rejected["empty_group_id"] += 1
                    continue
                source = str(row["source"]).strip()
                original_source = original_source_identity(row)
                if not original_source:
                    rejected["missing_original_source_identity"] += 1
                    continue
                source_key = (language, original_source)
                if text in source_seen[source_key]:
                    rejected[f"source_duplicate_within_source:{language}:{source}"] += 1
                    continue
                if source_limit and source_retained[source_key] >= source_limit:
                    rejected[f"source_limit_discarded:{language}:{source}"] += 1
                    continue
                source_seen[source_key].add(text)
                source_retained[source_key] += 1
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
    return rows, rejected, source_retained


def _select_source_balanced(bucket, target, preferred_share, hard_share):
    """Select a split bucket using configured preferred and hard source-share ceilings."""
    if target is None:
        return list(bucket), Counter()
    if target <= 0:
        return [], Counter()
    preferred_cap = max(1, int(target * preferred_share))
    hard_cap = max(1, int(target * hard_share))
    selected = []
    selected_ids = set()
    source_counts = Counter()

    for row in bucket:
        source = original_source_identity(row)
        if source_counts[source] >= preferred_cap:
            continue
        selected.append(row)
        selected_ids.add(id(row))
        source_counts[source] += 1
        if len(selected) >= target:
            return selected, source_counts

    # Relax the preferred share only as needed, never beyond the hard ceiling.
    for row in bucket:
        if id(row) in selected_ids:
            continue
        source = original_source_identity(row)
        if source_counts[source] >= hard_cap:
            continue
        selected.append(row)
        selected_ids.add(id(row))
        source_counts[source] += 1
        if len(selected) >= target:
            break
    return selected, source_counts


def merge(args):
    exclusions_path = getattr(args, "exclusions", None)
    exclusions = load_exclusions(exclusions_path)
    rows, rejected, source_intake_counts = read_inputs(args.inputs, args)

    owners = defaultdict(set)
    for row in rows:
        owners[row["text"]].add(row["language"])
    cross_language_texts = {
        text for text, languages in owners.items() if len(languages) > 1
    }
    if cross_language_texts:
        before = len(rows)
        rows = [row for row in rows if row["text"] not in cross_language_texts]
        rejected["cross_language_collision"] += before - len(rows)

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
        first_source[key] = original_source_identity(row)
        previous = group_splits.setdefault(row["split_group_id"], row["split"])
        if previous != row["split"]:
            raise ValueError(f"split-group inconsistency: {row['split_group_id']}")
        selected.append(row)

    cfg = load_config(getattr(args, "config", None))
    balance_cfg = cfg["candidate"]["source_balance"]
    if int(getattr(args, "max_per_language", 0) or 0) > 0 or balance_cfg.get("enabled") is True:
        raise SystemExit(
            "Pre-JQL per-language selection/source balancing is disabled by contract; "
            "the candidate stage must retain the complete eligible pool."
        )
    preferred_share = getattr(args, "preferred_source_share", None)
    preferred_share = preferred_share if preferred_share is not None else balance_cfg.get("preferred_max_share_per_language_and_split", 1.0)
    hard_share = getattr(args, "max_source_share", None)
    hard_share = hard_share if hard_share is not None else balance_cfg.get("hard_max_share_per_language_and_split", 1.0)
    if not 0 < preferred_share <= hard_share <= 1:
        raise ValueError("source shares must satisfy 0 < preferred <= maximum <= 1")

    if args.max_per_language:
        total_target = args.max_per_language
        configured_core_target = getattr(args, "core_per_language", None)
        if configured_core_target is None:
            configured_core_target = cfg["candidate"]["minimum_candidates_per_language"]
        core_target = min(configured_core_target, total_target)
        reserve_target = total_target - core_target
        core_caps = {
            "train": max(0, core_target
                         - round(core_target * args.validation_fraction)
                         - round(core_target * args.test_fraction)),
            "validation": round(core_target * args.validation_fraction),
            "test": round(core_target * args.test_fraction),
        }
    else:
        total_target = core_target = None
        reserve_target = 0
        core_caps = {name: None for name in SPLITS}

    by_bucket = defaultdict(list)
    for row in selected:
        by_bucket[(row["language"], row["split"])].append(row)

    core_by_bucket = {}
    source_quota_shortfalls = {}
    core_split_groups = set()
    for language in LANGUAGES:
        for split in SPLITS:
            bucket = sorted(by_bucket[(language, split)], key=lambda row: row["_priority"])
            if args.max_per_language:
                chosen, bucket_source_counts = _select_source_balanced(
                    bucket, core_caps[split], preferred_share, hard_share
                )
                if len(chosen) < core_caps[split]:
                    source_quota_shortfalls[f"{language}:core:{split}"] = {
                        "expected": core_caps[split],
                        "actual": len(chosen),
                        "source_counts": dict(sorted(bucket_source_counts.items())),
                        "reason": "insufficient source diversity or source records under hard share cap",
                    }
            else:
                chosen = bucket
            core_by_bucket[(language, split)] = chosen
            core_split_groups.update(row["split_group_id"] for row in chosen)

    reserve_by_language = {language: [] for language in LANGUAGES}
    reserve_counts = Counter()
    if args.max_per_language and reserve_target:
        reserve_candidates = defaultdict(list)
        for row in selected:
            if row["split_group_id"] not in core_split_groups:
                reserve_candidates[row["language"]].append(row)
        for language in LANGUAGES:
            bucket = sorted(reserve_candidates[language], key=lambda row: row["_priority"])
            chosen, bucket_source_counts = _select_source_balanced(
                bucket, reserve_target, preferred_share, hard_share
            )
            if len(chosen) < reserve_target:
                source_quota_shortfalls[f"{language}:reserve"] = {
                    "expected": reserve_target,
                    "actual": len(chosen),
                    "source_counts": dict(sorted(bucket_source_counts.items())),
                    "reason": "insufficient unused document groups or source diversity under hard share cap",
                }
            for row in chosen:
                item = dict(row)
                item["pool_role"] = "reserve"
                item["reserved_split_assignment"] = item.pop("split")
                reserve_by_language[language].append(item)
                reserve_counts[language] += 1

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    source_counts = Counter()
    output_hashes = {}
    public_keys = ("text", "language", "source", "split")
    internal_rows = []
    for language in LANGUAGES:
        for split in SPLITS:
            for row in core_by_bucket[(language, split)]:
                item = dict(row)
                item["pool_role"] = "core"
                internal_rows.append(item)
    for language in LANGUAGES:
        internal_rows.extend(reserve_by_language[language])

    for split in SPLITS:
        public_path = output / f"{split}.jsonl"
        with public_path.open("w", encoding="utf-8", newline="\n") as public:
            for language in LANGUAGES:
                for row in core_by_bucket[(language, split)]:
                    public.write(json.dumps(
                        {key: row[key] for key in public_keys},
                        ensure_ascii=False, separators=(",", ":")
                    ) + "\n")
                    counts[f"{language}:{split}"] += 1
                    source_counts[f"{original_source_identity(row)}:{language}:core:{split}"] += 1
        output_hashes[public_path.name] = digest(public_path.read_text(encoding="utf-8"))

    reserve_path = output / "reserve.jsonl"
    with reserve_path.open("w", encoding="utf-8", newline="\n") as reserve:
        for language in LANGUAGES:
            for row in reserve_by_language[language]:
                reserve.write(json.dumps({
                    "text": row["text"],
                    "language": row["language"],
                    "source": row["source"],
                    "pool_role": "reserve",
                }, ensure_ascii=False, separators=(",", ":")) + "\n")
                source_counts[f"{original_source_identity(row)}:{language}:reserve"] += 1
    output_hashes[reserve_path.name] = digest(reserve_path.read_text(encoding="utf-8"))

    if args.require_exact_counts and args.max_per_language:
        shortfalls = {
            f"{language}:{split}": {
                "expected": core_caps[split],
                "actual": counts[f"{language}:{split}"],
            }
            for language in LANGUAGES for split in SPLITS
            if counts[f"{language}:{split}"] != core_caps[split]
        }
        if shortfalls:
            available_by_source = defaultdict(Counter)
            for (language, split), bucket in by_bucket.items():
                for row in bucket:
                    available_by_source[f"{language}:{split}"][original_source_identity(row)] += 1
            diagnostic = {
                "status": "candidate_incomplete",
                "exact_split_shortfalls": shortfalls,
                "available_after_global_dedup_by_language_split_source": {
                    key: dict(sorted(value.items()))
                    for key, value in sorted(available_by_source.items())
                },
                "selected_core_and_reserve_by_source": dict(sorted(source_counts.items())),
                "source_intake_counts_before_global_dedup": {
                    f"{language}:{source}": count
                    for (language, source), count in sorted(source_intake_counts.items())
                },
                "rejected": dict(sorted(rejected.items())),
                "cross_language_collision_strings_removed": len(cross_language_texts),
                "source_quota_shortfalls": source_quota_shortfalls,
            }
            diagnostic_path = output / "candidate-diagnostics.json"
            diagnostic_path.write_text(
                json.dumps(diagnostic, ensure_ascii=False, indent=2) + "\\n",
                encoding="utf-8",
            )
            print(json.dumps(diagnostic, ensure_ascii=False, indent=2), flush=True)
            raise ValueError(
                f"exact per-language core split target not met; diagnostics: {diagnostic_path}"
            )

    internal_path = output / "records.jsonl"
    with internal_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in internal_rows:
            stream.write(json.dumps(row, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
    output_hashes[internal_path.name] = digest(internal_path.read_text(encoding="utf-8"))

    privacy_flag_counts = Counter()
    rights_status_counts = Counter()
    output_groups = set()
    output_groups_by_source = defaultdict(set)
    core_group_ids = set()
    reserve_group_ids = set()
    for row in internal_rows:
        privacy_flag_counts.update(row.get("provenance", {}).get("privacy_flags", []))
        rights_status_counts[row.get("provenance", {}).get("rights_status", "unclassified")] += 1
        output_groups.add(row["group_id"])
        output_groups_by_source[original_source_identity(row)].add(row["group_id"])
        if row["pool_role"] == "core":
            core_group_ids.add(row["split_group_id"])
        else:
            reserve_group_ids.add(row["split_group_id"])

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
            "max_per_language_total": total_target,
            "core_per_language": core_target,
            "reserve_per_language": reserve_target,
            "core_split_caps": core_caps,
            "deduplication": "exact normalized text within language across all inputs",
            "cross_language_collision_policy": "remove every occurrence of a normalized string present in more than one target language",
            "group_split": "deterministic hash of split_group_id (or group_id); reserve excludes every group used in core",
            "source_balancing": {
                "preferred_max_share_per_language_and_bucket": preferred_share,
                "hard_max_share_per_language_and_bucket": hard_share,
                "policy": "fill to preferred share per source first; relax only as needed up to hard maximum; underfill rather than exceed hard maximum",
            },
            "reserve_policy": "reserve is emitted separately without a train/validation/test split and excludes every split group selected into core",
            "privacy_filters": "shared conservative PII screen before per-source quota accounting; email, URL, IP, phone, address and contextual personal-name matches rejected or quarantined",
            "source_exclusion_registry": str(exclusions_path) if exclusions_path else None,
            "exclusion_matching": "document, exact URL/hash, domain, archive batch or source dataset; any matched group/split group is cascaded out",
        },
        "counts": dict(sorted(counts.items())),
        "reserve_counts": dict(sorted(reserve_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "source_counts_identity": "provenance.source_original_name, falling back to source only when absent",
        "source_quota_shortfalls": source_quota_shortfalls,
        "cross_language_collision_strings_removed": len(cross_language_texts),
        "rejected": dict(sorted(rejected.items())),
        "source_intake_counts_before_global_dedup": {
            f"{language}:{source}": count
            for (language, source), count in sorted(source_intake_counts.items())
        },
        "duplicate_source_pairs": dict(sorted(duplicate_by_source_pair.items())),
        "privacy_flag_counts": dict(sorted(privacy_flag_counts.items())),
        "rights_status_counts": dict(sorted(rights_status_counts.items())),
        "group_count": len(output_groups),
        "core_group_count": len(core_group_ids),
        "reserve_group_count": len(reserve_group_ids),
        "candidate_group_count": len(group_splits),
        "group_counts_by_source": {source: len(groups) for source, groups in sorted(output_groups_by_source.items())},
        "group_counts_source_identity": "original source identifier",
        "output_sha256": output_hashes,
        "exclusion_registry": {"path": str(exclusions_path) if exclusions_path else None,
                              "active_rules_loaded": len(exclusions),
                              "excluded_rows": rejected.get("source_exclusion_registry", 0)},
        "rights_note": (
            "Technical deduplication is not a rights clearance. Each source's licence, "
            "database rights, underlying-text rights, attribution and privacy conditions "
            "must be reviewed independently before publication or redistribution."
        ),
        "privacy_note": (
            "The shared deterministic privacy gate runs before per-source acquisition quotas and again "
            "during global merge. High-confidence email, URL, IPv4/IPv6, phone, long-identifier, "
            "street-address and contextual personal-name matches are rejected; ambiguous personal-name "
            "candidates and upstream sensitive-data flags are quarantined. Contributor names, author names, "
            "contact identifiers and person-bearing title metadata are removed from provenance while "
            "non-identifying speaker references and roles are retained. The screen is conservative "
            "and does not claim perfect multilingual named-entity recognition; human review remains "
            "necessary before any external release."
        ),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"counts": manifest["counts"], "reserve_counts": manifest["reserve_counts"],
                      "source_counts": manifest["source_counts"],
                      "source_quota_shortfalls": manifest["source_quota_shortfalls"],
                      "rejected": manifest["rejected"], "groups": manifest["group_count"]},
                     ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", dest="inputs", action="append", required=True, type=Path,
                        help="Source-normalized JSONL; repeat for each source")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--exclusions", type=Path, default=None,
                        help="Active source/document exclusion registry (JSONL or CSV)")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--min-chars", type=int, default=None)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--max-bytes", type=int, default=None)
    parser.add_argument("--max-sentences-per-source", type=int, default=None,
                        help="0 disables a second-stage cap; acquisition limits are source-specific")
    parser.add_argument("--max-per-language", type=int, default=None)
    parser.add_argument("--core-per-language", type=int, default=None)
    parser.add_argument("--preferred-source-share", type=float, default=None)
    parser.add_argument("--max-source-share", type=float, default=None)
    parser.add_argument("--validation-fraction", type=float, default=None)
    parser.add_argument("--test-fraction", type=float, default=None)
    parser.add_argument("--seed", default=None)
    parser.add_argument("--require-exact-counts", action="store_true",
                        help="Fail unless every target language reaches every split cap")
    args = parser.parse_args()
    cfg = load_config(args.config)
    text_cfg = cfg["candidate"]["text"]
    split_cfg = cfg["candidate"]["splits"]
    balance_cfg = cfg["candidate"]["source_balance"]
    args.min_chars = args.min_chars if args.min_chars is not None else text_cfg["min_characters"]
    args.max_chars = args.max_chars if args.max_chars is not None else text_cfg["max_characters"]
    args.max_bytes = args.max_bytes if args.max_bytes is not None else text_cfg["max_utf8_bytes"]
    args.max_sentences_per_source = args.max_sentences_per_source if args.max_sentences_per_source is not None else balance_cfg.get("max_sentences_per_source_after_acquisition", 0)
    args.max_per_language = args.max_per_language if args.max_per_language is not None else 0
    args.core_per_language = args.core_per_language if args.core_per_language is not None else 0
    args.preferred_source_share = args.preferred_source_share if args.preferred_source_share is not None else balance_cfg.get("preferred_max_share_per_language_and_split", 1.0)
    args.max_source_share = args.max_source_share if args.max_source_share is not None else balance_cfg.get("hard_max_share_per_language_and_split", 1.0)
    args.validation_fraction = args.validation_fraction if args.validation_fraction is not None else split_cfg["validation_fraction"]
    args.test_fraction = args.test_fraction if args.test_fraction is not None else split_cfg["test_fraction"]
    args.seed = args.seed or split_cfg["seed"]
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    if args.max_sentences_per_source < 0:
        parser.error("--max-sentences-per-source must be >= 0")
    if args.max_per_language < 0:
        parser.error("--max-per-language must be >= 0")
    if args.core_per_language < 0:
        parser.error("--core-per-language must be >= 0")
    if args.max_per_language and args.core_per_language > args.max_per_language:
        parser.error("--core-per-language cannot exceed --max-per-language")
    if not 0 < args.preferred_source_share <= args.max_source_share <= 1:
        parser.error("source shares must satisfy 0 < preferred <= maximum <= 1")
    if not 0 <= args.validation_fraction < 1 or not 0 <= args.test_fraction < 1:
        parser.error("split fractions must be in [0, 1)")
    if args.validation_fraction + args.test_fraction >= 1:
        parser.error("validation + test fractions must be less than 1")
    merge(args)


if __name__ == "__main__":
    main()
