"""Deterministic preparation of text-only language-ID corpora.

Input is a UTF-8 CSV/TSV with text, language and document/group columns.
The tool writes train/validation/test JSONL files and a provenance manifest.
It deliberately does not fetch source datasets: obtain originals from their
authorised distribution channels, then prepare them locally.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

DEFAULT_LANGUAGES = (
    "bg hr cs da nl en et fi fr de el hu ga it lv lt mt pl pt ro sk sl es sv "
    "nb nn ru ja zh ko ar tr"
).split()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_text(value: str) -> str:
    """NFC, collapse whitespace, preserve punctuation and diacritics."""
    value = unicodedata.normalize("NFC", value)
    return " ".join(value.split())


def stable_fraction(language: str, group: str, seed: str) -> float:
    payload = f"{seed}\0{language}\0{group}".encode("utf-8")
    number = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return number / 2**64


def assign_split(language: str, group: str, seed: str,
                 validation_fraction: float, test_fraction: float) -> str:
    value = stable_fraction(language, group, seed)
    if value < test_fraction:
        return "test"
    if value < test_fraction + validation_fraction:
        return "validation"
    return "train"


def read_rows(path: Path) -> Iterable[dict[str, str]]:
    delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream, delimiter=delimiter)


def prepare(args: argparse.Namespace) -> dict:
    source = Path(args.input)
    allowed = set(args.languages)
    exclusions = [re.compile(pattern, re.IGNORECASE) for pattern in args.exclude_regex]
    # A deterministic priority hash provides a stable cap without depending
    # on source row order.
    candidates: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    rejected = Counter()
    accepted_before_cap = Counter()

    for row_number, row in enumerate(read_rows(source), start=2):
        language = (row.get(args.language_column) or args.language or "").strip().lower()
        if language not in allowed:
            rejected["language_not_in_target_set"] += 1
            continue
        text = normalize_text(row.get(args.text_column) or "")
        group = (row.get(args.group_column) or "").strip()
        if not text or not group:
            rejected["empty_text_or_group"] += 1
            continue
        if len(text) < args.min_chars or len(text) > args.max_chars:
            rejected["outside_character_limits"] += 1
            continue
        if len(text.encode("utf-8")) > args.max_bytes:
            rejected["outside_byte_limit"] += 1
            continue
        if any(pattern.search(text) for pattern in exclusions):
            rejected["excluded_by_configured_pattern"] += 1
            continue
        key = (language, text)
        if key in seen:
            rejected["duplicate_text_within_language"] += 1
            continue
        seen.add(key)
        split = assign_split(language, group, args.seed,
                             args.validation_fraction, args.test_fraction)
        priority = hashlib.sha256(
            f"{args.seed}\0{language}\0{split}\0{text}".encode("utf-8")
        ).hexdigest()
        record = {"text": text, "language": language, "source": args.source_name}
        candidates[f"{language}:{split}"].append((priority, {**record, "split": split}))
        accepted_before_cap[f"{language}:{split}"] += 1

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    output_hashes = {}
    if args.max_per_language:
        validation_cap = round(args.max_per_language * args.validation_fraction)
        test_cap = round(args.max_per_language * args.test_fraction)
        split_caps = {
            "train": max(0, args.max_per_language - validation_cap - test_cap),
            "validation": validation_cap,
            "test": test_cap,
        }
    else:
        split_caps = {"train": 0, "validation": 0, "test": 0}
    for split in ("train", "validation", "test"):
        destination = output / f"{split}.jsonl"
        with destination.open("w", encoding="utf-8", newline="\n") as stream:
            for language in args.languages:
                items = sorted(candidates.get(f"{language}:{split}", []),
                               key=lambda item: item[0])
                if split_caps[split]:
                    items = items[:split_caps[split]]
                for _, record in items:
                    stream.write(json.dumps(record, ensure_ascii=False,
                                             separators=(",", ":")) + "\n")
                    counts[f"{language}:{split}"] += 1
        output_hashes[destination.name] = sha256_file(destination)

    manifest = {
        "schema_version": 1,
        "project": "langid-32",
        "source_name": args.source_name,
        "source_file_name": source.name,
        "source_sha256": sha256_file(source),
        "source_release": args.source_release,
        "source_licence": args.source_licence,
        "source_download_origin": args.source_download_origin,
        "preparation": {
            "text_column": args.text_column,
            "language_column": args.language_column,
            "group_column": args.group_column,
            "normalization": "Unicode NFC; collapse whitespace; preserve punctuation and diacritics",
            "min_chars": args.min_chars,
            "max_chars": args.max_chars,
            "max_bytes": args.max_bytes,
            "max_per_language_total": args.max_per_language,
            "per_language_split_caps": split_caps,
            "seed": args.seed,
            "validation_fraction": args.validation_fraction,
            "test_fraction": args.test_fraction,
            "exclude_regex": args.exclude_regex,
        },
        "target_languages": args.languages,
        "counts": dict(sorted(counts.items())),
        "accepted_before_cap": dict(sorted(accepted_before_cap.items())),
        "rejected": dict(sorted(rejected.items())),
        "output_sha256": output_hashes,
        "privacy_note": (
            "Text-only output. This tool does not export source group IDs or "
            "speaker/contributor metadata. Review text for personal data before publication."
        ),
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="UTF-8 CSV or TSV source file")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--text-column", required=True)
    parser.add_argument("--language-column", default="language")
    parser.add_argument("--group-column", required=True,
                        help="Source document/sentence group ID used before splitting")
    parser.add_argument("--language", help="Use this language when input has no language column")
    parser.add_argument("--languages", nargs="+", default=DEFAULT_LANGUAGES)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-release", default="unspecified")
    parser.add_argument("--source-licence", default="unspecified")
    parser.add_argument("--source-download-origin", default="unspecified")
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    parser.add_argument("--max-per-language", type=int, default=20000,
                        help="Maximum total per language across all splits; 0 means unlimited")
    parser.add_argument("--validation-fraction", type=float, default=0.10)
    parser.add_argument("--test-fraction", type=float, default=0.10)
    parser.add_argument("--seed", default="langid-32-v1")
    parser.add_argument("--exclude-regex", action="append", default=[],
                        help="Optional explicit text exclusion regex; may be repeated")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not 0 <= args.validation_fraction < 1 or not 0 <= args.test_fraction < 1:
        parser.error("split fractions must be in [0, 1)")
    if args.validation_fraction + args.test_fraction >= 1:
        parser.error("validation + test fractions must be less than 1")
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    if args.max_per_language < 0:
        parser.error("--max-per-language must be >= 0")
    manifest = prepare(args)
    print(json.dumps({"output": args.output, "counts": manifest["counts"],
                      "rejected": manifest["rejected"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
