#!/usr/bin/env python3
"""Merge the already-curated Common Voice 27 Croatian subset into the HF pilot."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hf-curated", type=Path, required=True)
    parser.add_argument("--v27-artifact", type=Path, required=True)
    args = parser.parse_args()

    hf_jsonl = args.hf_curated / "common_voice_candidates.jsonl"
    hf_report_path = args.hf_curated / "common_voice_report.json"
    v27_jsonl = args.v27_artifact / "common_voice_candidates.jsonl"
    v27_report_path = args.v27_artifact / "common_voice_report.json"
    v27_manifest_path = args.v27_artifact / "mdc-download-manifest.json"

    for path in (hf_jsonl, hf_report_path, v27_jsonl, v27_report_path, v27_manifest_path):
        if not path.is_file():
            raise SystemExit(f"Required input missing: {path}")

    hf_rows = [json.loads(line) for line in hf_jsonl.read_text(encoding="utf-8").splitlines() if line]
    v27_rows = [json.loads(line) for line in v27_jsonl.read_text(encoding="utf-8").splitlines() if line]
    hr_rows = [row for row in v27_rows if row.get("language") == "hr"]
    if not hr_rows:
        raise SystemExit("The v27 artifact contains no curated Croatian rows.")
    if any(row.get("source") != "common_voice_v27" for row in hr_rows):
        raise SystemExit("Croatian rows do not have the expected Common Voice v27 provenance.")
    manifest = json.loads(v27_manifest_path.read_text(encoding="utf-8"))
    hr_source = next((item for item in manifest.get("results", []) if item.get("locale") == "hr"), None)
    if not hr_source or not hr_source.get("archive_checksum_verified"):
        raise SystemExit("The v27 Croatian source manifest has no verified archive checksum.")
    for row in hr_rows:
        row["provenance"] = {
            "source_dataset_id": hr_source.get("dataset_id"),
            "locale": "hr",
            "archive_sha256": hr_source.get("archive_sha256_actual"),
            "validated_sentences_tsv_sha256": hr_source.get("extracted_sha256"),
            "downloaded_at_utc": hr_source.get("downloaded_at_utc"),
            "candidate_record_hash": row.get("group_id"),
            "sentence_id_retained": False,
            "rights_status": "hold_locale_specific_terms_acceptance_not_recorded",
            "privacy_flags": [],
        }

    # Replace the empty/missing v22 Croatian slot with the existing v27 curated rows.
    rows = [row for row in hf_rows if row.get("language") != "hr"] + hr_rows
    rows.sort(key=lambda row: (row.get("language", ""), row.get("group_id", ""), row.get("text", "")))
    payload = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    hf_jsonl.write_text(payload, encoding="utf-8", newline="\n")

    report = json.loads(hf_report_path.read_text(encoding="utf-8"))
    v27_report = json.loads(v27_report_path.read_text(encoding="utf-8"))
    report.setdefault("per_language", {})["hr"] = v27_report["per_language"]["hr"]
    report["per_language"]["hr"]["source"] = "common_voice_v27"
    report.setdefault("counts", {}).update({
        key: value for key, value in v27_report.get("counts", {}).items() if key.startswith("hr:")
    })
    report["sources"] = {
        "hf": report.get("source"),
        "hr": {
            "source": "Mozilla Common Voice Scripted Speech 27.0",
            "origin": "Mozilla Data Collective authorised download; existing curated artifact",
            "locale": "hr",
            "dataset_id": hr_source.get("dataset_id"),
            "archive_sha256": hr_source.get("archive_sha256_actual"),
            "validated_sentences_tsv_sha256": hr_source.get("extracted_sha256"),
            "archive_checksum_verified": hr_source.get("archive_checksum_verified"),
            "curated_rows": len(hr_rows),
        },
    }
    report["source"] = "HF Common Voice 22 pilot plus Mozilla Common Voice 27 Croatian"
    report["candidate_file_sha256"] = hashlib.sha256(hf_jsonl.read_bytes()).hexdigest()
    report["note"] = (
        "Mixed-version text-only pilot: HF Common Voice 22 for its successful locales; "
        "Croatian supplied from the previously downloaded and curated Mozilla Common Voice 27.0 artifact. "
        "The Croatian source archive checksum was verified; only the curated text subset is included."
    )
    hf_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "source": "Mozilla Common Voice Scripted Speech 27.0",
        "locale": "hr",
        "target_language": "hr",
        "dataset_id": hr_source.get("dataset_id"),
        "archive_filename": hr_source.get("filename"),
        "archive_size_bytes": hr_source.get("archive_size_bytes"),
        "archive_sha256_expected": hr_source.get("archive_checksum_sha256_expected"),
        "archive_sha256_actual": hr_source.get("archive_sha256_actual"),
        "archive_checksum_verified": hr_source.get("archive_checksum_verified"),
        "validated_sentences_tsv_sha256": hr_source.get("extracted_sha256"),
        "validated_sentences_tsv_bytes": hr_source.get("extracted_bytes"),
        "downloaded_at_utc": hr_source.get("downloaded_at_utc"),
        "curation": v27_report.get("per_language", {}).get("hr"),
        "curation_counts": {k: v for k, v in v27_report.get("counts", {}).items() if k.startswith("hr:")},
        "selected_rows_in_combined_pilot": len(hr_rows),
        "source_artifact_run_id": 44058539144,
        "source_artifact_name": "common-voice-v27-other-accounts-curated",
        "source_artifact_sha256": "9b9c6eb20240bb18297435cb938886f7c274a7c04943ca35d6ad2acd03149a27",
        "restriction": "Curated subset only; do not rehost or redistribute the full source dataset/audio; no speaker identification.",
    }
    (args.hf_curated / "common_voice_v27_hr_provenance.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "replaced_hf_hr_rows": sum(row.get("language") == "hr" for row in hf_rows),
        "inserted_v27_hr_rows": len(hr_rows),
        "combined_rows": len(rows),
        "archive_checksum_verified": hr_source.get("archive_checksum_verified"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
