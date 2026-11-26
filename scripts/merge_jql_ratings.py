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


def sha256(path: Path, chunk_bytes: int) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(chunk_bytes), b""):
            h.update(block)
    return h.hexdigest()


def read_rating_files(directory: Path) -> tuple[dict[str, dict], dict[str, int]]:
    merged: dict[str, dict] = {}
    file_rows: dict[str, int] = {}
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise SystemExit(f"No ratings CSV files found in {directory}")
    for path in files:
        count = 0
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["id", "language", "ratings"]:
                raise SystemExit(f"Unexpected ratings schema in {path}")
            for row in reader:
                row_id = row["id"]
                if not row_id or row_id in merged:
                    raise SystemExit(f"Empty or duplicate rating ID {row_id!r} (including {path.name})")
                try:
                    scores = json.loads(row["ratings"])
                    score_values = {judge: float(scores[judge]) for judge in JUDGES}
                    if not all(math.isfinite(value) for value in score_values.values()):
                        raise ValueError("non-finite score")
                    merged[row_id] = {"language": row["language"], **score_values}
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise SystemExit(f"Invalid rating row for {row_id} in {path}: {exc}") from exc
                count += 1
        file_rows[path.name] = count
    return merged, file_rows


def validate_split_manifest(
    assessment_path: Path,
    shards_dir: Path,
    assessment_rows: int,
    expected_shards: int,
) -> tuple[dict, dict[str, dict]]:
    manifest_path = shards_dir / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit("Missing deterministic JQL split manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("input") != assessment_path.name:
        raise SystemExit("JQL split manifest references a different assessment file")
    if manifest.get("input_sha256") != sha256(assessment_path, 1024 * 1024):
        raise SystemExit("JQL split manifest assessment hash mismatch")
    if int(manifest.get("rows", -1)) != assessment_rows:
        raise SystemExit("JQL split manifest assessment row count mismatch")
    if int(manifest.get("shards", -1)) != expected_shards:
        raise SystemExit("JQL split manifest shard count mismatch")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != expected_shards:
        raise SystemExit("JQL split manifest has an incomplete shard file list")
    file_map = {}
    for item in files:
        name = str(item.get("file", ""))
        if not name or Path(name).name != name or not name.endswith(".parquet") or name in file_map:
            raise SystemExit(f"Invalid or duplicate shard filename in split manifest: {name!r}")
        path = shards_dir / name
        if not path.is_file() or sha256(path, 1024 * 1024) != item.get("sha256"):
            raise SystemExit(f"JQL shard file hash mismatch: {name}")
        if int(item.get("rows", -1)) < 1:
            raise SystemExit(f"JQL shard is empty or has invalid row count: {name}")
        file_map[name] = item
    if sum(int(item["rows"]) for item in file_map.values()) != assessment_rows:
        raise SystemExit("JQL split shard row counts do not sum to assessment row count")
    return manifest, file_map


def read_score_manifests(
    directory: Path,
    file_rows: dict[str, int],
    shards_dir: Path,
    expected_shards: int,
) -> tuple[dict, list[dict]]:
    manifests = sorted(directory.glob("*.csv.manifest.json"))
    if len(manifests) != expected_shards or len(file_rows) != expected_shards:
        raise SystemExit(
            f"Expected {expected_shards} completed rating shards and manifests; "
            f"found {len(file_rows)} CSVs and {len(manifests)} manifests"
        )
    common_provenance = None
    shard_records = []
    manifest_csv_names = set()
    for manifest_path in manifests:
        csv_name = manifest_path.name.removesuffix(".manifest.json")
        manifest_csv_names.add(csv_name)
        if csv_name not in file_rows:
            raise SystemExit(f"Missing ratings CSV for manifest {manifest_path.name}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if int(manifest.get("scored_rows", -1)) != file_rows[csv_name]:
            raise SystemExit(f"Ratings row count does not match manifest {manifest_path.name}")
        if int(manifest.get("input_rows", -1)) != file_rows[csv_name]:
            raise SystemExit(f"Shard is incomplete according to manifest {manifest_path.name}")
        input_name = str(manifest.get("input_file", ""))
        if Path(input_name).name != input_name or not input_name.endswith(".parquet"):
            raise SystemExit(f"Unsafe shard filename in manifest {manifest_path.name}: {input_name!r}")
        input_path = shards_dir / input_name
        if not input_name or not input_path.is_file():
            raise SystemExit(f"Missing input shard for manifest {manifest_path.name}: {input_name}")
        input_hash = sha256(input_path, 1024 * 1024)
        if input_hash != manifest.get("input_sha256"):
            raise SystemExit(f"Input shard hash mismatch for {manifest_path.name}")
        provenance = {
            "pipeline_source_sha": manifest.get("pipeline_source_sha"),
            "pipeline_source_run_id": str(manifest.get("pipeline_source_run_id", "")),
            "models": manifest.get("models"),
            "head_checkpoint_sha256": manifest.get("head_checkpoint_sha256"),
            "scoring": manifest.get("scoring"),
        }
        source_sha = provenance["pipeline_source_sha"]
        if not isinstance(source_sha, str) or len(source_sha) != 40 or any(
            ch not in "0123456789abcdef" for ch in source_sha.lower()
        ):
            raise SystemExit(f"Invalid source pipeline commit SHA in {manifest_path.name}")
        if not provenance["pipeline_source_run_id"].isdigit():
            raise SystemExit(f"Invalid source pipeline run ID in {manifest_path.name}")
        if not provenance["models"] or not provenance["head_checkpoint_sha256"] or not provenance["scoring"]:
            raise SystemExit(f"Incomplete model provenance in {manifest_path.name}")
        for key in ("embedder_revision_resolved",):
            revision = provenance["models"].get(key)
            if not isinstance(revision, str) or len(revision) != 40 or any(ch not in "0123456789abcdef" for ch in revision.lower()):
                raise SystemExit(f"Unpinned model revision in {manifest_path.name}: {key}")
        head_revision = provenance["models"].get("head_revision_resolved")
        if not isinstance(head_revision, str) or len(head_revision) != 40 or any(ch not in "0123456789abcdef" for ch in head_revision.lower()):
            raise SystemExit(f"Unpinned JQL head revision in {manifest_path.name}")
        if common_provenance is None:
            common_provenance = provenance
        elif provenance != common_provenance:
            raise SystemExit("JQL shards used different model revisions, checkpoint files or scoring settings")
        shard_records.append({
            "ratings_file": csv_name,
            "input_file": input_name,
            "input_sha256": input_hash,
            "input_rows": int(manifest["input_rows"]),
            "scored_rows": int(manifest["scored_rows"]),
        })
    if manifest_csv_names != set(file_rows):
        raise SystemExit("Ratings CSV and provenance manifest sets differ")
    return common_provenance or {}, shard_records


def quantile_normalize(values: list[float], epsilon: float | None = None) -> list[float]:
    """Map average ranks to standard-normal quantiles; ties receive the same score."""
    if epsilon is None:
        epsilon = load_config()["jql"]["quantile_epsilon"]
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
    ap.add_argument("--shards-dir", required=True, type=Path, help="Directory containing the exact scored Parquet shards")
    ap.add_argument("--output-csv", required=True, type=Path)
    ap.add_argument("--output-parquet", type=Path)
    ap.add_argument("--summary", type=Path)
    ap.add_argument("--include-text", action="store_true", help="Include sentence text in output")
    ap.add_argument("--pruned-output-csv", type=Path)
    ap.add_argument("--pruned-output-parquet", type=Path)
    ap.add_argument("--pruning-summary", type=Path)
    ap.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    args = ap.parse_args()
    full_config = load_config(args.config)
    jql_config = full_config["jql"]
    chunk_bytes = full_config["execution"]["download_chunk_bytes"]
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
    ratings, rating_file_rows = read_rating_files(args.ratings_dir)
    model_provenance, shard_manifests = read_score_manifests(
        args.ratings_dir, rating_file_rows, args.shards_dir, int(jql_config["shard_count"])
    )
    split_manifest, split_files = validate_split_manifest(
        args.input, args.shards_dir, len(frame), int(jql_config["shard_count"])
    )
    scored_files = {item["input_file"]: item for item in shard_manifests}
    if set(scored_files) != set(split_files):
        raise SystemExit("Scored shard set differs from deterministic split manifest")
    for filename, split_item in split_files.items():
        scored_item = scored_files[filename]
        if (scored_item["input_sha256"] != split_item["sha256"]
                or scored_item["input_rows"] != int(split_item["rows"])):
            raise SystemExit(f"Scored shard provenance mismatch: {filename}")
    expected_source_sha = os.environ.get("LANGID32_SOURCE_SHA")
    expected_source_run_id = os.environ.get("LANGID32_SOURCE_RUN_ID")
    if expected_source_sha and model_provenance["pipeline_source_sha"] != expected_source_sha:
        raise SystemExit("JQL ratings were produced from a different staged-pipeline commit")
    if expected_source_run_id and model_provenance["pipeline_source_run_id"] != expected_source_run_id:
        raise SystemExit("JQL ratings were produced from a different staged-pipeline run")
    model_info = model_provenance["models"]
    if model_info.get("embedder_repository") != jql_config["embedder_model"]:
        raise SystemExit("JQL embedding repository does not match the authoritative config")
    if model_info.get("embedder_revision_resolved") != jql_config["embedder_revision"]:
        raise SystemExit("JQL embedding model revision does not match the configured immutable pin")
    if model_info.get("head_repository") != jql_config["head_repository"]:
        raise SystemExit("JQL head repository does not match the authoritative config")
    if model_info.get("head_revision_requested") != jql_config["head_repository_revision"]:
        raise SystemExit("JQL head repository revision request does not match the authoritative config")
    if tuple(model_provenance["scoring"].get("judges", [])) != JUDGES:
        raise SystemExit("JQL judge set does not match the authoritative config")
    checkpoint_hashes = model_provenance["head_checkpoint_sha256"]
    if set(checkpoint_hashes) != set(JUDGES) or any(
        not isinstance(value, str) or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value.lower())
        for value in checkpoint_hashes.values()
    ):
        raise SystemExit("JQL checkpoint hashes are missing or malformed")
    expected, actual = set(frame["id"]), set(ratings)
    if sum(item["input_rows"] for item in shard_manifests) != len(frame):
        raise SystemExit("JQL shard row counts do not sum to the complete assessment row count")
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

    pruning_summary = None
    if args.pruned_output_csv or args.pruned_output_parquet or args.pruning_summary:
        quantile = float(jql_config["prune_bottom_quantile"])
        if not 0.0 <= quantile < 1.0:
            raise SystemExit(f"Invalid prune_bottom_quantile: {quantile}")
        prune_count = int(len(frame) * quantile)
        ordered = frame.sort_values(["jql_consensus", "id"], ascending=[True, True])
        pruned_ids = set(ordered.head(prune_count)["id"].astype(str))
        retained = frame.loc[~frame["id"].astype(str).isin(pruned_ids)].copy()
        retained = retained.sort_values(["lang", "jql_consensus", "id"], ascending=[True, False, True])
        if args.pruned_output_csv:
            args.pruned_output_csv.parent.mkdir(parents=True, exist_ok=True)
            retained.to_csv(args.pruned_output_csv, index=False, quoting=csv.QUOTE_MINIMAL)
        if args.pruned_output_parquet:
            args.pruned_output_parquet.parent.mkdir(parents=True, exist_ok=True)
            retained.to_parquet(args.pruned_output_parquet, index=False, compression="zstd")
        def grouped_counts(data):
            grouped = data.groupby(["lang", "source-variant"], dropna=False).size()
            return [{"language": str(lang), "source": str(source), "count": int(count)}
                    for (lang, source), count in grouped.items()]
        pruning_summary = {
            "scope": "global_all_languages_after_full_corpus_normalization",
            "quantile": quantile, "input_rows": int(len(frame)),
            "pruned_rows": int(prune_count), "retained_rows": int(len(retained)),
            "pruned_by_language_source": grouped_counts(frame.loc[frame["id"].astype(str).isin(pruned_ids)]),
            "retained_by_language_source": grouped_counts(retained),
            "source_field": "source-variant (original source identifier)",
            "tie_break": "consensus ascending then id ascending; exact deterministic row count",
            "final_30k_selection": "deferred_pending_user_review",
        }
        if args.pruning_summary:
            args.pruning_summary.parent.mkdir(parents=True, exist_ok=True)
            args.pruning_summary.write_text(json.dumps(pruning_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "rows": len(frame),
        "input_sha256": sha256(args.input, chunk_bytes),
        "ratings_files": [p.name for p in sorted(args.ratings_dir.glob("*.csv"))],
        "model_provenance": model_provenance,
        "split_manifest_sha256": sha256(args.shards_dir / "manifest.json", chunk_bytes),
        "shard_manifests": shard_manifests,
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
        "pruning": pruning_summary,
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(frame), "csv": str(args.output_csv),
                      "parquet": str(args.output_parquet) if args.output_parquet else None}))


if __name__ == "__main__":
    main()
