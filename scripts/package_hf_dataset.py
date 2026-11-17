#!/usr/bin/env python3
"""Build a privacy-minimised Hugging Face dataset package from the CV pilot artifact.

This is a packaging/validation step only. It deliberately does not upload anything
and does not declare a dataset licence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

LANGUAGES = {
    "ar": "Arabic", "bg": "Bulgarian", "ca": "Catalan", "cs": "Czech",
    "da": "Danish", "de": "German", "el": "Greek", "en": "English",
    "es": "Spanish", "et": "Estonian", "fi": "Finnish", "fr": "French",
    "ga": "Irish", "hr": "Croatian", "hu": "Hungarian", "is": "Icelandic",
    "it": "Italian", "ja": "Japanese", "ko": "Korean", "lt": "Lithuanian",
    "lv": "Latvian", "mt": "Maltese", "nb": "Norwegian Bokmål",
    "nl": "Dutch", "nn": "Norwegian Nynorsk", "pl": "Polish",
    "pt": "Portuguese", "ro": "Romanian", "ru": "Russian",
    "sk": "Slovak", "sl": "Slovenian", "sv": "Swedish",
    "tr": "Turkish", "zh": "Chinese",
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    source = args.input_dir / "common_voice_candidates.jsonl"
    report_path = args.input_dir / "common_voice_report.json"
    hr_path = args.input_dir / "common_voice_v27_hr_provenance.json"
    for p in (source, report_path, hr_path):
        if not p.is_file():
            raise SystemExit(f"Required artifact file missing: {p}")

    import pyarrow as pa
    import pyarrow.parquet as pq

    counts: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    seen: set[tuple[str, str]] = set()
    cross_labels: dict[str, str] = {}
    out_rows = []
    with source.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            text = row.get("text")
            label = row.get("language")
            source_key = row.get("source")
            if not isinstance(text, str) or not text.strip():
                raise SystemExit(f"Invalid text at line {line_no}")
            if label not in LANGUAGES:
                raise SystemExit(f"Unexpected language label {label!r} at line {line_no}")
            if source_key not in {"common_voice_v22", "common_voice_v27"}:
                raise SystemExit(f"Unexpected source {source_key!r} at line {line_no}")
            if row.get("licence_id") != "CC0-1.0":
                raise SystemExit(f"Unexpected source licence claim at line {line_no}")
            key = (label, text)
            if key in seen:
                raise SystemExit(f"Duplicate text within label at line {line_no}")
            seen.add(key)
            previous = cross_labels.setdefault(text, label)
            if previous != label:
                raise SystemExit(f"Cross-label exact collision at line {line_no}")
            if source_key == "common_voice_v27" and label != "hr":
                raise SystemExit("v27 source is only expected for Croatian in this pilot")
            if source_key == "common_voice_v22" and label == "hr":
                raise SystemExit("Croatian must come from the retained v27 source")
            counts[label] += 1
            sources[source_key] += 1
            out_rows.append({
                "text": text,
                "label": label,
                "source": source_key,
                "source_release": row.get("source_release", ""),
                "source_license_claim": row.get("licence_id", ""),
            })

    if set(counts) != set(LANGUAGES):
        missing = sorted(set(LANGUAGES) - set(counts))
        extra = sorted(set(counts) - set(LANGUAGES))
        raise SystemExit(f"Language coverage mismatch; missing={missing}, extra={extra}")
    if counts["hr"] != 1724 or sources["common_voice_v27"] != 1724:
        raise SystemExit("Croatian v27 count/provenance does not match the verified pilot")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = args.output_dir / "data"
    meta_dir = args.output_dir / "metadata"
    data_dir.mkdir(exist_ok=True)
    meta_dir.mkdir(exist_ok=True)
    table = pa.Table.from_pylist(out_rows)
    parquet_path = data_dir / "candidate-00000-of-00001.parquet"
    pq.write_table(table, parquet_path, compression="zstd")

    with (meta_dir / "language_counts.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "language", "rows"])
        for code in sorted(LANGUAGES):
            w.writerow([code, LANGUAGES[code], counts[code]])

    raw_report = json.loads(report_path.read_text(encoding="utf-8"))
    hr = json.loads(hr_path.read_text(encoding="utf-8"))
    hf_manifest_path = args.input_dir / "hf-common-voice-download-manifest.json"
    if not hf_manifest_path.is_file():
        raise SystemExit("HF source manifest missing")
    raw_manifest = json.loads(hf_manifest_path.read_text(encoding="utf-8"))

    # Never copy raw URLs: some are temporary signed CDN URLs.
    locale_sources = []
    for item in raw_manifest.get("results", []):
        locale_sources.append({
            "locale": item.get("locale") or item.get("language"),
            "repository": "fsicoli/common_voice_22_0",
            "upstream_release_claim": "Common Voice Corpus 22.0 (unofficial conversion)",
            "requested_revision": raw_manifest.get("revision_requested"),
            "resolved_commit": item.get("repo_commit"),
            "etag": item.get("etag"),
            "bytes": item.get("bytes"),
            "sha256": item.get("sha256"),
            "downloaded_at_utc": item.get("downloaded_at_utc"),
            "retrieved": item.get("sha256") is not None,
        })

    source_summary = {
        "status": "development_only_release_blocked_by_corpus_maturity",
        "sources": [
            {
                "source": "common_voice_v22",
                "repository": "https://huggingface.co/datasets/fsicoli/common_voice_22_0",
                "release_claim": "Common Voice Corpus 22.0",
                "source_claimed_license": "CC0-1.0",
                "project_rights_status": "CC0 source data; applicable Common Voice ToS/dataset agreement also observed; partial curated selection only",
                "locales": locale_sources,
            },
            {
                "source": "common_voice_v27",
                "release": "Mozilla Common Voice Scripted Speech 27.0",
                "locale": "hr",
                "dataset_id": hr.get("dataset_id"),
                "archive_sha256": hr.get("archive_sha256_actual"),
                "validated_sentences_tsv_sha256": hr.get("validated_sentences_tsv_sha256"),
                "archive_checksum_verified": hr.get("archive_checksum_verified"),
                "curated_rows": hr.get("selected_rows_in_combined_pilot"),
                "terms_acceptance_status": "Common Voice ToS/dataset agreement includes a no-mirroring clause; project does not mirror the complete dataset",
                "project_rights_status": "partial curated text selection only; no audio or direct contributor identifiers; no complete-dataset mirroring",
            },
        ],
    }
    (meta_dir / "source_summary.json").write_text(
        json.dumps(source_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    quality = {
        "status": "technical_pilot_not_release_cleared",
        "rows": len(out_rows),
        "language_count": len(counts),
        "language_counts": dict(sorted(counts.items())),
        "source_counts": dict(sorted(sources.items())),
        "cross_language_collision_strings_removed": raw_report.get("cross_language_collision_strings_removed"),
        "curation_rules": raw_report.get("rules"),
        "limitations": [
            "Automated pattern filtering is not complete PII clearance.",
            "No human language or content quality review is represented.",
            "No train/validation/test split has been assigned.",
            "The current corpus is below the 20,000-30,000-per-language target and lacks the planned source diversity.",
        ],
        "candidate_jsonl_sha256": sha256(source),
        "parquet_sha256": sha256(parquet_path),
        "parquet_bytes": parquet_path.stat().st_size,
    }
    (meta_dir / "quality_summary.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "LICENSING_STATUS.md").write_text(
        "# Licensing status\n\n"
        "**Development-only; do not publish to Hugging Face yet.** The current corpus does not meet "
        "the project target of 20,000-30,000 curated records per language from varied sources. "
        "The Common Voice source data is identified as CC0; the separate ToS/dataset agreement "
        "includes a no-mirroring clause, which the project observes by using only partial curated "
        "text selections and excluding audio and direct contributor identifiers. See LICENSING.md.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "rows": len(out_rows),
        "languages": len(counts),
        "source_counts": dict(sources),
        "language_counts": dict(sorted(counts.items())),
        "parquet": str(parquet_path),
        "parquet_sha256": quality["parquet_sha256"],
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
