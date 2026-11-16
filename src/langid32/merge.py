#!/usr/bin/env python3
"""Merge source-normalized JSONL files into a globally deduplicated corpus candidate.

Each input row must contain text, language, source, source_release, group_id,
licence_id and text_origin. Optional provenance is retained in the private
records.jsonl sidecar. Group IDs are namespaced by source by the caller; IDs
shared across languages within one source must remain identical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

LANGUAGES = (
    "bg hr cs da nl en et fi fr de el hu ga it lv lt mt pl pt ro sk sl es sv "
    "nb nn ru ja zh ko ar tr"
).split()
SPLITS = ("train", "validation", "test")


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


def read_inputs(paths: list[Path], args):
    rejected = Counter()
    rows = []
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
                    "provenance": row.get("provenance", {}),
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
        },
        "counts": dict(sorted(counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "rejected": dict(sorted(rejected.items())),
        "duplicate_source_pairs": dict(sorted(duplicate_by_source_pair.items())),
        "group_count": len(group_splits),
        "output_sha256": output_hashes,
        "rights_note": (
            "Technical deduplication is not a rights clearance. Each source's licence, "
            "database rights, underlying-text rights, attribution and privacy conditions "
            "must be reviewed independently before publication or redistribution."
        ),
        "privacy_note": (
            "Provenance sidecar is internal. It may contain domains and source metadata; "
            "review text and provenance for personal data before any release."
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
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    parser.add_argument("--max-per-language", type=int, default=20000,
                        help="Total cap per language; 0 disables the cap")
    parser.add_argument("--validation-fraction", type=float, default=0.10)
    parser.add_argument("--test-fraction", type=float, default=0.10)
    parser.add_argument("--seed", default="langid-32-fineweb2-v1")\n    parser.add_argument("--require-exact-counts", action="store_true",\n                        help="Fail unless every target language reaches every split cap")
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
