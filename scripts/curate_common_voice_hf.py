#!/usr/bin/env python3
"""Build a small, text-only Common Voice candidate sample from private Common Voice TSVs.

Raw TSVs are kept only in private working storage and authenticated encrypted checkpoints; never uploaded in plaintext or committed.
Only deterministic, deduplicated sentence text (up to 20,000/language) and an
aggregate report are written to the artifact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config, acquisition_target
from langid32.privacy import screen_text
from langid32.acquisition_batches import open_state, plan_file_batches, next_batch, finish_batch, add_eligible, export_records, task_report, retained_count, pending_batch_count, mark_exhausted

def norm(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def script_ratio(text: str, script: str) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    prefix = script.upper() + " "
    matched = sum(unicodedata.name(char, "").startswith(prefix) for char in letters)
    return matched / len(letters)


def priority(language: str, text: str) -> str:
    return hashlib.sha256(f"langid-32-cv-v1\0{language}\0{text}".encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-language-cap", type=int, default=None)
    parser.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    languages = tuple(cfg["acquisition"]["source_rules"]["common_voice_v22"]["languages"])
    if not languages:
        raise SystemExit("No Common Voice target languages are configured.")
    text_rules = cfg["acquisition"]["source_rules"]["common_voice_v22"]["text"]
    download_manifest_path = args.input_root / "hf-common-voice-download-manifest.json"
    if not download_manifest_path.is_file():
        raise SystemExit("Common Voice download manifest is required for immutable provenance.")
    download_manifest = json.loads(download_manifest_path.read_text(encoding="utf-8"))
    locale_metadata = {row["locale"]: row for row in download_manifest.get("results", [])}
    candidates = defaultdict(dict)
    counts = Counter()
    args.output.mkdir(parents=True, exist_ok=True)
    resolved_revision = str(download_manifest.get("revision_resolved") or "")
    if not resolved_revision:
        raise SystemExit("Common Voice manifest has no immutable dataset revision.")
    policy_digest = hashlib.sha256(
        Path(__file__).read_bytes()
        + (ROOT / "src/langid32/privacy.py").read_bytes()
        + args.config.read_bytes()
    ).hexdigest()[:12]
    state_db = open_state(
        args.output / f"common-voice-acquisition-{resolved_revision[:12]}-{policy_digest}.sqlite"
    )
    acquisition_status = []
    for language in languages:
        path = args.input_root / language / "validated_sentences.tsv"
        if not path.is_file():
            counts[f"{language}:missing_file"] += 1
            continue
        cap = args.per_language_cap if args.per_language_cap is not None else acquisition_target(cfg, "common_voice_v22", language)
        source_key = "common_voice_v22"
        resolved_path = str(path.resolve())
        plan_file_batches(state_db, source_key, language, cap, [resolved_path], 1)
        batch = next_batch(state_db, source_key, language)
        if batch is not None:
            batch_no, planned_files = batch
            if planned_files != [resolved_path]:
                raise RuntimeError(f"{language}: unexpected Common Voice checkpoint batch {planned_files}")
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
                    if len(text) < text_rules["min_characters"] or len(text) > text_rules["max_characters"] or len(text.encode("utf-8")) > text_rules["max_utf8_bytes"]:
                        counts[f"{language}:length_rejected"] += 1
                        continue
                    global_text_rules = cfg["acquisition"]["text"]
                    letters = sum(char.isalpha() for char in text)
                    if (letters < global_text_rules["min_letter_characters"]
                            or letters / max(len(text), 1) < global_text_rules["min_letter_ratio"]):
                        counts[f"{language}:letter_quality_rejected"] += 1
                        continue
                    script_rules = cfg["acquisition"]["source_rules"]["common_voice_v22"]["script"]
                    expected_script = script_rules["by_language"].get(language)
                    if not expected_script:
                        raise ValueError(f"No expected script configured for Common Voice language {language}")
                    if script_ratio(text, expected_script) < script_rules["minimum_ratio"]:
                        counts[f"{language}:wrong_or_mixed_script_rejected"] += 1
                        continue
                    privacy = screen_text(text, uncertain_action=cfg["acquisition"]["text"]["privacy_uncertain_action"])
                    if not privacy.accepted:
                        counts[f"{language}:privacy_{privacy.status}"] += 1
                        for flag in privacy.flags:
                            counts[f"{language}:privacy_flag_{flag}"] += 1
                        continue
                    if text in candidates[language]:
                        counts[f"{language}:within_language_duplicate"] += 1
                        continue
                    sid = (row.get("sentence_id") or "").strip()
                    locale = (row.get("source_locale") or "").strip()
                    if not sid or not locale:
                        raise ValueError(f"{path}: row is missing sentence_id or source_locale")
                    source_meta = locale_metadata.get(locale)
                    if not source_meta or not source_meta.get("repo_commit"):
                        raise ValueError(f"{path}: no immutable source revision recorded for locale {locale}")
                    group = f"common_voice_v22:{locale}:{sid}"
                    provenance = {
                        "dataset_repo": download_manifest.get("source"),
                        "source_locale": locale,
                        "sentence_id": sid,
                        "repo_commit": source_meta["repo_commit"],
                        "source_tsv_sha256": source_meta["sha256"],
                        "source_tsv_bytes": source_meta["bytes"],
                        "privacy_flags": [],
                    }
                    record = {
                        "text": text, "language": language, "source": source_key,
                        "source_release": f"Common Voice Corpus 22.0@{source_meta['repo_commit']}",
                        "group_id": group, "licence_id": "CC0-1.0",
                        "text_origin": "CC0-1.0 Common Voice 22.0 text via the Hugging Face dataset fsicoli/common_voice_22_0; transcript-only selection",
                        "provenance": provenance,
                    }
                    add_eligible(state_db, source_key, language, [record])

            digest = hashlib.sha256()
            with path.open("rb") as raw:
                for chunk in iter(lambda: raw.read(1024 * 1024), b""):
                    digest.update(chunk)
            finish_batch(state_db, source_key, language, batch_no, {resolved_path: digest.hexdigest()})
        if (retained_count(state_db, source_key, language) < cap
                and pending_batch_count(state_db, source_key, language) == 0):
            mark_exhausted(state_db, source_key, language)
        stored = export_records(state_db, source_key, language)
        for record in stored:
            candidates[language][record["text"]] = {
                "group_id": record["group_id"],
                "provenance": record["provenance"],
                "source_release": record["source_release"],
            }
        acquisition_status.append(task_report(state_db, source_key, language))

    # Remove every occurrence of any normalized string shared by language labels.
    owners = defaultdict(set)
    for language, rows in candidates.items():
        for text in rows:
            owners[text].add(language)
    collisions = {text for text, langs in owners.items() if len(langs) > 1}
    for language in languages:
        for text in collisions:
            if text in candidates[language]:
                del candidates[language][text]
                counts[f"{language}:cross_language_collision_removed"] += 1

    output_path = args.output / "common_voice_candidates.jsonl"
    final_counts = {}
    with output_path.open("w", encoding="utf-8", newline="\n") as out:
        for language in languages:
            items = list(candidates[language].items())
            before = len(items)
            cap = args.per_language_cap if args.per_language_cap is not None else acquisition_target(cfg, "common_voice_v22", language)
            items = items[:cap]
            final_counts[language] = {
                "eligible_after_privacy_dedup_collision_checks": before,
                "selected": len(items),
                "cap": cap,
            }
            for text, metadata in items:
                out.write(json.dumps({
                    "text": text,
                    "language": language,
                    "source": "common_voice_v22",
                    "source_release": metadata["source_release"],
                    "group_id": metadata["group_id"],
                    "licence_id": "CC0-1.0",
                    "text_origin": "CC0-1.0 Common Voice 22.0 text via the Hugging Face dataset fsicoli/common_voice_22_0; transcript-only selection",
                    "provenance": metadata["provenance"],
                }, ensure_ascii=False, separators=(",", ":")) + "\n")
    report = {
        "source": "fsicoli/common_voice_22_0 (Common Voice 22.0)",
        "dataset_url": "https://huggingface.co/datasets/fsicoli/common_voice_22_0",
        "source_license_claim": "CC0-1.0",
        "revision_resolved": download_manifest.get("revision_resolved"),
        "acquisition_policy_digest": policy_digest,
        "locale_revisions": {locale: row.get("repo_commit") for locale, row in sorted(locale_metadata.items())},
        "target_languages": list(languages),
        "raw_tsvs_uploaded": False,
        "audio_saved": False,
        "selection": {"validated_sentences_tsv": True, "require_is_used_true_when_present": True, "text_rules": text_rules, "within_language_deduplication": True, "expected_script_by_language": script_rules["by_language"], "minimum_expected_script_ratio": script_rules["minimum_ratio"], "all_language_collision_removal": True, "deterministic_cap": True},
        "cross_language_collision_strings_removed": len(collisions),
        "per_language": final_counts,
        "acquisition_state": acquisition_status,
        "counts": dict(sorted(counts.items())),
        "candidate_file_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "note": "Text-only candidates selected from the HF-hosted dataset card-declared CC0-1.0 Common Voice 22.0 conversion. Croatian is intentionally absent pending an alternative source.",
    }
    (args.output / "common_voice_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    state_db.close()


if __name__ == "__main__":
    main()
