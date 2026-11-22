#!/usr/bin/env python3
"""Apply a global JQL quality floor, then restore each language's baseline core source mix."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

LANGUAGES = (
    "bg hr cs da nl en et fi fr de el hu ga it lv lt mt pl pt ro sk sl es sv "
    "nb nn ru ja zh ko ar tr ca is"
).split()


def baseline_source_counts(manifest_path: Path) -> dict[str, Counter]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result: dict[str, Counter] = defaultdict(Counter)
    for key, count in manifest.get("source_counts", {}).items():
        parts = key.split(":")
        if len(parts) != 4:
            continue
        source, language, role, split = parts
        if role == "core" and language in LANGUAGES:
            result[language][source] += int(count)
    missing = [lang for lang in LANGUAGES if not result[lang]]
    if missing:
        raise RuntimeError(f"Baseline core source proportions missing for languages: {missing}")
    return result


def allocate(counts: Counter, target: int) -> dict[str, int]:
    total = sum(counts.values())
    if total <= 0:
        raise RuntimeError("Cannot allocate quotas from an empty baseline")
    exact = {source: target * count / total for source, count in counts.items()}
    quotas = {source: math.floor(value) for source, value in exact.items()}
    remainder = target - sum(quotas.values())
    order = sorted(counts, key=lambda source: (-(exact[source] - quotas[source]), source))
    for source in order[:remainder]:
        quotas[source] += 1
    return quotas


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--consensus", type=Path, required=True)
    ap.add_argument("--baseline-manifest", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--target-per-language", type=int, default=25000)
    ap.add_argument("--minimum-candidate-per-language", type=int, default=35000)
    ap.add_argument("--global-quantile", type=float, default=0.25)
    args = ap.parse_args()
    if not 0 < args.global_quantile < 1:
        ap.error("--global-quantile must be between 0 and 1")
    if args.target_per_language <= 20000:
        ap.error("--target-per-language must be well over 20,000")

    import pandas as pd

    frame = pd.read_parquet(args.consensus)
    required = {"id", "lang", "source", "jql_consensus"}
    if not required.issubset(frame.columns):
        raise RuntimeError(f"Consensus file missing columns: {sorted(required-set(frame.columns))}")
    if frame["id"].isna().any() or frame["id"].astype(str).duplicated().any():
        raise RuntimeError("Consensus IDs must be non-null and unique")
    if frame["jql_consensus"].isna().any():
        raise RuntimeError("Consensus scores contain nulls")

    candidate_counts = frame.groupby("lang").size().to_dict()
    insufficient_candidates = {
        lang: int(candidate_counts.get(lang, 0))
        for lang in LANGUAGES
        if candidate_counts.get(lang, 0) < args.minimum_candidate_per_language
    }
    if insufficient_candidates:
        raise RuntimeError(
            "Candidate pool below required per-language target; refusing to silently "
            f"proceed: {insufficient_candidates}"
        )

    cutoff = float(frame["jql_consensus"].quantile(args.global_quantile, interpolation="linear"))
    eligible = frame.loc[frame["jql_consensus"] >= cutoff].copy()
    baseline = baseline_source_counts(args.baseline_manifest)
    selected_parts = []
    quota_report = {}
    for lang in LANGUAGES:
        lang_rows = eligible.loc[eligible["lang"] == lang]
        quotas = allocate(baseline[lang], args.target_per_language)
        available = lang_rows.groupby("source").size().to_dict()
        shortages = {
            source: {"required": quota, "available_above_global_cutoff": int(available.get(source, 0))}
            for source, quota in quotas.items()
            if available.get(source, 0) < quota
        }
        if shortages:
            raise RuntimeError(
                f"{lang}: cannot preserve baseline source proportions above global "
                f"quality cutoff; refusing to redistribute quotas: {shortages}"
            )
        for source, quota in quotas.items():
            bucket = lang_rows.loc[lang_rows["source"] == source]
            chosen = bucket.sort_values(["jql_consensus", "id"], ascending=[False, True]).head(quota)
            if len(chosen) != quota:
                raise RuntimeError(f"Selection count mismatch for {lang}/{source}")
            selected_parts.append(chosen)
        quota_report[lang] = {
            "target": args.target_per_language,
            "baseline_source_counts": dict(sorted(baseline[lang].items())),
            "selected_source_counts": dict(sorted(quotas.items())),
            "eligible_above_global_cutoff": int(len(lang_rows)),
        }

    selected = pd.concat(selected_parts, ignore_index=True)
    selected = selected.sort_values(["lang", "source", "jql_consensus", "id"],
                                    ascending=[True, True, False, True])
    if len(selected) != len(LANGUAGES) * args.target_per_language:
        raise RuntimeError("Final selected row count does not match exact language targets")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "jql-consensus-selected.csv"
    parquet_path = args.output_dir / "jql-consensus-selected.parquet"
    selected.to_csv(csv_path, index=False)
    selected.to_parquet(parquet_path, index=False, compression="zstd")
    summary = {
        "rows_before_filter": int(len(frame)),
        "global_quality_quantile": args.global_quantile,
        "global_jql_consensus_cutoff": cutoff,
        "rows_above_global_cutoff": int(len(eligible)),
        "target_per_language": args.target_per_language,
        "selected_rows": int(len(selected)),
        "language_counts": {lang: int(count) for lang, count in selected.groupby("lang").size().items()},
        "baseline_source_mix": "existing baseline core manifest; source proportions preserved independently within each language",
        "selection": "global 25th-percentile floor; within each language/source cell retain highest JQL consensus to exact baseline-proportional quotas",
        "quotas": quota_report,
        "files": [csv_path.name, parquet_path.name],
    }
    (args.output_dir / "selection-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "rows_before_filter": len(frame),
        "global_cutoff": cutoff,
        "eligible_rows": len(eligible),
        "selected_rows": len(selected),
        "per_language": args.target_per_language,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
