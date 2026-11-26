#!/usr/bin/env python3
"""Assemble the current source artifacts and build the 34-label core/reserve candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config, acquisition_target, source_quota_key
from langid32.privacy import screen_record, sanitize_provenance

FAMILY_PREFIXES = (
    "temu_cc0",
    "catalan_dpo_v2",
    "bsc_legal",
    "maalfrid2026",
    "fineweb2",
    "un_arabic_english_filtered",
)
SUPERSEDED_V5_SOURCES = {
    "dgt-tm-2021",
    "tatoeba-cc0",
    "common_voice_v22",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_one(root: Path, filename: str) -> Path:
    matches = sorted(root.rglob(filename))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {filename} under {root}, found {len(matches)}")
    return matches[0]


def source_family(raw_source: str) -> tuple[str, str | None]:
    for prefix in FAMILY_PREFIXES:
        marker = prefix + ":"
        if raw_source.startswith(marker):
            return prefix, raw_source[len(marker):]
    if ":" in raw_source:
        raise ValueError(f"Unmapped source component syntax: {raw_source}")
    return raw_source, None


def normalize_file(source_path: Path, destination: Path, *, config=None, source_language_counts=None, source_language_seen=None, filter_superseded=False):
    if config is None:
        config = load_config()
    rows_in = 0
    rows_out = 0
    filtered = Counter()
    source_counts = Counter()
    raw_source_counts = Counter()
    if source_language_counts is None:
        source_language_counts = Counter()
    if source_language_seen is None:
        source_language_seen = defaultdict(set)
    with source_path.open("r", encoding="utf-8") as source, destination.open(
        "w", encoding="utf-8", newline="\n"
    ) as output:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            rows_in += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{source_path}:{line_number}: invalid JSON: {exc}") from exc
            raw_source = str(row.get("source") or "")
            if filter_superseded and raw_source in SUPERSEDED_V5_SOURCES:
                filtered[raw_source] += 1
                continue
            required = ("text", "language", "source", "source_release",
                        "group_id", "licence_id", "text_origin")
            missing = [key for key in required if not row.get(key)]
            if missing:
                raise ValueError(f"{source_path}:{line_number}: missing {', '.join(missing)}")
            if not isinstance(row.get("provenance"), dict):
                raise ValueError(f"{source_path}:{line_number}: provenance object is required")
            row, removed_top_metadata = sanitize_provenance(row)
            row["provenance"], removed_provenance_metadata = sanitize_provenance(row["provenance"])
            removed_metadata = set(removed_top_metadata) | set(removed_provenance_metadata)
            if removed_metadata:
                filtered["personal_metadata_fields_removed"] += len(removed_metadata)
            text_rules = config["acquisition"]["text"]
            normalized_text = unicodedata.normalize("NFC", " ".join(str(row["text"]).split()))
            row["text"] = normalized_text
            if (len(normalized_text) < text_rules["min_characters"]
                    or len(normalized_text) > text_rules["max_characters"]
                    or len(normalized_text.encode("utf-8")) > text_rules["max_utf8_bytes"]):
                filtered["text_length_or_bytes"] += 1
                continue
            letter_count = sum(char.isalpha() for char in normalized_text)
            if (letter_count < text_rules["min_letter_characters"]
                    or letter_count / max(len(normalized_text), 1) < text_rules["min_letter_ratio"]):
                filtered["text_letter_quality"] += 1
                continue
            privacy = screen_record(row, uncertain_action=text_rules["privacy_uncertain_action"])
            if not privacy.accepted:
                filtered["privacy_" + privacy.status] += 1
                for flag in privacy.flags:
                    filtered["privacy_flag_" + flag] += 1
                continue
            language = str(row["language"])
            try:
                source_limit = acquisition_target(config, raw_source, language)
            except ValueError as exc:
                reason = ("source_excluded_by_policy" if "excluded by source policy" in str(exc) else "source_not_registered" if "not registered" in str(exc) else "source_language_not_approved")
                filtered[reason] += 1
                continue
            quota_key = source_quota_key(config, raw_source)
            source_language_key = (quota_key, language)
            if normalized_text in source_language_seen[source_language_key]:
                filtered["duplicate_within_exact_source_language"] += 1
                continue
            if source_language_counts[source_language_key] >= source_limit:
                filtered["configured_source_target_reached"] += 1
                continue
            source_language_seen[source_language_key].add(normalized_text)
            source_language_counts[source_language_key] += 1
            raw_source_counts[(raw_source, language)] += 1
            family, component = source_family(raw_source)
            provenance = row["provenance"]
            provenance["source_original_name"] = raw_source
            if component is not None:
                provenance["source_component"] = component
            if family == "dgt-tm-2021":
                member = provenance.get("tmx_member")
                if member:
                    numdoc_id = Path(str(member)).stem
                    provenance["source_document_id"] = numdoc_id
                    provenance["numdoc_id"] = numdoc_id
                    provenance["identifier_scheme"] = "EUR-Lex NumDoc (CELEX-compatible)"
                    provenance["source_url"] = (
                        "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:"
                        + numdoc_id
                    )
                    provenance["numdoc_sector"] = numdoc_id[:1]
                    if len(numdoc_id) >= 5 and numdoc_id[1:5].isdigit():
                        provenance["numdoc_year"] = int(numdoc_id[1:5])
                    if len(numdoc_id) >= 6:
                        provenance["numdoc_document_type"] = numdoc_id[5:6]
                    origin_by_sector = {
                        "2": "eu_international_agreement",
                        "3": "eu_legal_act",
                        "4": "eu_complementary_legislation",
                        "5": "eu_preparatory_document",
                        "0": "eu_consolidated_text",
                        "C": "eu_official_journal_document",
                        "E": "efta_document",
                    }
                    row["text_origin"] = origin_by_sector.get(
                        numdoc_id[:1], "eu_official_document"
                    )
                else:
                    row["text_origin"] = "eu_official_document"
                provenance["source_url_verification_status"] = "derived_from_numdoc_not_http_verified"
                provenance["source_dataset_url"] = (
                    "https://joint-research-centre.ec.europa.eu/language-technology-resources/"
                    "dgt-translation-memory_en"
                )
                provenance["source_latest_update"] = "DGT-TM release 2021; exact day/month not stated on JRC page"
            if family == "catalan_dpo_v2":
                row_id = provenance.get("dataset_row_id")
                if not row_id:
                    raise ValueError(f"{source_path}:{line_number}: DPO row lacks dataset_row_id")
                row["group_id"] = f"{family}:{row_id}"
                row["split_group_id"] = row["group_id"]
            row["source"] = family
            output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            rows_out += 1
            source_counts[family] += 1
    return {
        "input": str(source_path),
        "input_sha256": sha256(source_path),
        "rows_in": rows_in,
        "rows_out": rows_out,
        "filtered_superseded_sources": dict(filtered),
        "source_counts": dict(sorted(source_counts.items())),
        "raw_source_language_counts": {f"{source}:{language}": count for (source, language), count in sorted(raw_source_counts.items())},
        "normalized_path": str(destination),
    }



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v5-dir", type=Path, required=True)
    parser.add_argument("--common-voice-dir", type=Path, required=True)
    parser.add_argument("--leipzig-dir", type=Path, required=True)
    parser.add_argument("--tatoeba-dir", type=Path, required=True)
    parser.add_argument("--dgt-dir", type=Path, required=True)
    parser.add_argument("--waiting-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("LANGID32_CONFIG", ROOT / "config/langid32.toml")))
    parser.add_argument("--exclusions", type=Path, default=Path("data/source-exclusions.jsonl"))
    parser.add_argument("--max-per-language", type=int, default=None)
    parser.add_argument("--core-per-language", type=int, default=None)
    parser.add_argument("--preferred-source-share", type=float, default=None)
    parser.add_argument("--max-source-share", type=float, default=None)
    parser.add_argument("--seed", default=None)
    parser.add_argument("--require-exact-counts", action="store_true",
                        help="Fail unless every language reaches every core split target")
    args = parser.parse_args()
    cfg = load_config(args.config)
    # Keep the complete eligible pool for JQL. Final 30k/language selection and
    # source balancing are intentionally deferred until after global JQL pruning.
    args.seed = args.seed or cfg["candidate"]["splits"]["seed"]

    v5_records = find_one(args.v5_dir, "records.jsonl")
    cv_records = find_one(args.common_voice_dir, "common_voice_candidates.jsonl")
    leipzig_records = find_one(args.leipzig_dir, "leipzig-candidates.jsonl")
    tatoeba_records = find_one(args.tatoeba_dir, "tatoeba-cc0-staged.jsonl")
    dgt_records = find_one(args.dgt_dir, "dgt-tm-2021-staged.jsonl")
    waiting_records = sorted(args.waiting_dir.rglob("candidates.jsonl"))
    if not waiting_records:
        raise RuntimeError(f"No waiting-source candidates.jsonl files found under {args.waiting_dir}")

    args.output.mkdir(parents=True, exist_ok=True)
    normalized_dir = args.output / "normalized-inputs"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    sources = [
        ("v5-current-families", v5_records, True),
        ("common-voice-current", cv_records, False),
        ("leipzig-balanced-2026-11-18", leipzig_records, False),
        ("tatoeba-cc0-current", tatoeba_records, False),
        ("dgt-tm-2021-current", dgt_records, False),
    ] + [(f"waiting-{index:02d}", path, False)
         for index, path in enumerate(waiting_records, 1)]

    reports = []
    merge_inputs = []
    source_language_counts = Counter()
    source_language_seen = defaultdict(set)
    for label, path, filter_superseded in sources:
        destination = normalized_dir / f"{label}.jsonl"
        reports.append(normalize_file(path, destination, config=cfg, source_language_counts=source_language_counts, source_language_seen=source_language_seen, filter_superseded=filter_superseded))
        if destination.stat().st_size:
            merge_inputs.append(destination)

    if not merge_inputs:
        raise RuntimeError("No non-empty normalized inputs were prepared")

    # Keep every source-retained row until global merge/deduplication.
    combined_path = args.output / "all-source-inputs.jsonl"
    combined_rows = 0
    with combined_path.open("w", encoding="utf-8") as combined:
        for path in merge_inputs:
            with path.open("r", encoding="utf-8") as source:
                for line in source:
                    if line.strip():
                        combined.write(line)
                        combined_rows += 1

    input_manifest = {
        "status": "prepared_for_global_candidate_merge",
        "source_artifacts": {
            "historical_v5_run": 43950037392,
            "common_voice_run": None,
            "leipzig_balanced_run": 44361364340,
            "common_voice_dataset": "fsicoli/common_voice_22_0",
            "common_voice_acquisition": "same-run ephemeral HF-hosted CC0 acquisition; raw TSV and candidate text are retained only inside the encrypted checkpoint; no plaintext text-bearing artifact is uploaded",
            "tatoeba_run": 44121162591,
            "dgt_tm_2021_run": 44291075180,
            "waiting_sources_run": None,
            "waiting_sources_acquisition": "same-run ephemeral acquisition; candidate text is retained only inside the encrypted checkpoint; raw source archives/caches are ephemeral and not uploaded",
        },
        "inputs": reports,
        "normalized_input_count": len(merge_inputs),
        "source_language_acquisition_counts": {f"{source}:{language}": count for (source, language), count in sorted(source_language_counts.items())},
        "normalized_inputs": [str(path) for path in merge_inputs],
        "merge_input": str(combined_path),
        "preselection": {"status": "disabled"},
        "combined_rows": combined_rows,
        "source_family_policy": "source families are used only for normalized display/grouping; acquisition quotas, candidate caps, source-balance constraints and all source-level reports use provenance.source_original_name",
        "v5_replacements": sorted(SUPERSEDED_V5_SOURCES),
    }
    (args.output / "input-manifest.json").write_text(
        json.dumps(input_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    command = [
        sys.executable, "-m", "langid32.merge",
        "--output", str(args.output / "candidate"),
        "--config", str(args.config),
        "--exclusions", str(args.exclusions),
        "--seed", args.seed,
    ]
    if args.require_exact_counts:
        command.append("--require-exact-counts")
    command.extend(["--input", str(combined_path)])
    subprocess.run(command, check=True)

    summary = {
        "status": "candidate_built_not_rights_cleared",
        "input_manifest": "input-manifest.json",
        "candidate_manifest": "candidate/manifest.json",
        "normalized_input_count": len(merge_inputs),
        "normalized_rows_out": sum(item["rows_out"] for item in reports),
        "combined_source_rows": combined_rows,
        "normalized_rows_filtered_as_superseded": sum(
            sum(item["filtered_superseded_sources"].values()) for item in reports
        ),
    }
    (args.output / "build-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
