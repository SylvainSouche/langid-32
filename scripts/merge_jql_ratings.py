#!/usr/bin/env python3
"""Merge sharded JQL ratings, quantile-normalize judges, and add quality flags."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config
from statistics import NormalDist

JUDGES = tuple(load_config()["jql"]["judges"])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_rating_files(directory: Path) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise SystemExit(f"No ratings CSV files found in {directory}")
    for path in files:
        with path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                row_id = row["id"]
                if row_id in merged:
                    raise SystemExit(f"Duplicate rating ID {row_id} (including {path.name})")
                try:
                    scores = json.loads(row["ratings"])
                    score_values = {judge: float(scores[judge]) for judge in JUDGES}
                    if not all(math.isfinite(value) for value in score_values.values()):
                        raise ValueError("non-finite score")
                    merged[row_id] = {"language": row["language"], **score_values}
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise SystemExit(f"Invalid rating row for {row_id} in {path}: {exc}") from exc
    return merged


def quantile_normalize(values: list[float], epsilon: float) -> list[float]:
    """Map average ranks to standard-normal quantiles; ties receive the same score."""
    n = len(values)
    if n == 0:
        return []
    order = sorted(range(n), key=lambda i: values[i])
    result = [0.0] * n
    normal = NormalDist()
    pos = 0
    while pos < n:
        end = pos + 1
        while end < n and values[order[end]] == values[order[pos]]:
            end += 1
        average_rank = ((pos + 1) + end) / 2.0  # 1-based ranks
        probability = (average_rank - 0.5) / n
        z = normal.inv_cdf(min(1.0 - epsilon, max(epsilon, probability)))
        for k in range(pos, end):
            result[order[k]] = z
        pos = end
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path, help="Full assessment Parquet")
    ap.add_argument("--ratings-dir", required=True, type=Path, help="Directory of shard ratings CSVs")
    ap.add_argument("--quality", required=True, type=Path, help="Boundary-check CSV")
    ap.add_argument("--output-csv", required=True, type=Path)
    ap.add_argument("--output-parquet", type=Path)
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--include-text", action="store_true", help="Include sentence text in output (avoid for public Actions artifacts)")
    ap.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    args = ap.parse_args()
    jql_config = load_config(args.config)["jql"]
    penalty = float(jql_config["consensus_disagreement_penalty"])
    mean_weight = float(jql_config["consensus_mean_weight"])

    if not args.input.is_file() or not args.quality.is_file():
        raise SystemExit("Input Parquet and quality CSV must both exist")
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit("Install pandas and pyarrow: python -m pip install pandas pyarrow") from exc
    frame = pd.read_parquet(args.input, columns=["id", "lang", "sentence", "source", "source-variant"])
    if frame["id"].isna().any() or frame["id"].astype(str).duplicated().any():
        raise SystemExit("Input IDs must be non-null and unique")
    frame["id"] = frame["id"].astype(str)
    ratings = read_rating_files(args.ratings_dir)
    expected, actual = set(frame["id"]), set(ratings)
    language_by_id = dict(zip(frame["id"], frame["lang"].astype(str)))
    missing, extra = expected - actual, actual - expected
    if missing or extra:
        raise SystemExit(f"Rating coverage mismatch: missing={len(missing)}, extra={len(extra)}")
    for row_id, rating in ratings.items():
        if language_by_id[row_id] != str(rating["language"]):
            raise SystemExit(
                f"Language mismatch for {row_id}: "
                f"Parquet={language_by_id[row_id]}, ratings={rating['language']}"
            )

    quality: dict[str, dict] = {}
    with args.quality.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            row_id = row["id"]
            if row_id in quality:
                raise SystemExit(f"Duplicate quality ID {row_id}")
            quality[row_id] = row
    if set(quality) != expected:
        raise SystemExit(
            f"Quality coverage mismatch: missing={len(expected-set(quality))}, "
            f"extra={len(set(quality)-expected)}"
        )

    for judge in JUDGES:
        frame[f"{judge}_raw"] = frame["id"].map(lambda key: ratings[key][judge])
        frame[f"{judge}_z"] = quantile_normalize(frame[f"{judge}_raw"].tolist())

    z_columns = [f"{judge}_z" for judge in JUDGES]
    frame["jql_mean"] = frame[z_columns].mean(axis=1)
    frame["jql_disagreement"] = frame[z_columns].std(axis=1, ddof=0)
    frame["jql_consensus"] = mean_weight * frame["jql_mean"] - penalty * frame["jql_disagreement"]


    frame["initial_capitalization"] = frame["id"].map(
        lambda key: quality[key]["initial_capitalization"]
    )
    frame["terminal_punctuation"] = frame["id"].map(
        lambda key: quality[key]["terminal_punctuation"]
    )
    columns = [
        "id", "lang", "source", "source-variant",
        "gemma_raw", "mistral_raw", "llama_raw",
        "gemma_z", "mistral_z", "llama_z",
        "jql_mean", "jql_disagreement", "jql_consensus",
        "initial_capitalization", "terminal_punctuation",
    ]
    if args.include_text:
        columns.insert(2, "sentence")
    frame = frame[columns].sort_values(["lang", "jql_consensus", "id"],
                                       ascending=[True, False, True])
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    if args.output_parquet:
        args.output_parquet.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(args.output_parquet, index=False, compression="zstd")

    summary = {
        "rows": len(frame),
        "input_sha256": sha256(args.input),
        "ratings_files": [p.name for p in sorted(args.ratings_dir.glob("*.csv"))],
        "ratings_rows": len(ratings),
        "quantile_normalization": "average ranks mapped through standard-normal inverse CDF; ties share average rank",
        "normalization_scope": "entire assessment corpus, all languages combined, independently per judge",
        "consensus_formula": "mean(gemma_z,mistral_z,llama_z) - 0.5 * population_std(gemma_z,mistral_z,llama_z)",
        "consensus_mean_weight": mean_weight,
        "consensus_penalty": penalty,
        "quality_flags_are_non_filtering": True,
        "sentence_text_included": bool(args.include_text),
        "capitalization": frame["initial_capitalization"].value_counts().to_dict(),
        "terminal_punctuation": frame["terminal_punctuation"].value_counts().to_dict(),
        "score_summary": {
            col: {"mean": float(frame[col].mean()), "std": float(frame[col].std(ddof=0)),
                  "min": float(frame[col].min()), "max": float(frame[col].max())}
            for col in z_columns + ["jql_mean", "jql_disagreement", "jql_consensus"]
        },
        "selection_note": "Corpus-relative ranking only; recalculate normalization when the reference corpus changes.",
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(frame), "csv": str(args.output_csv),
                      "parquet": str(args.output_parquet) if args.output_parquet else None}))


if __name__ == "__main__":
    main()
