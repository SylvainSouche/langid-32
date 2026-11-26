import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config


def _run(script, *args, env=None):
    merged_env = os.environ.copy()
    merged_env["PYTHONPATH"] = str(ROOT / "src")
    if env:
        merged_env.update(env)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *map(str, args)],
        cwd=ROOT,
        env=merged_env,
        check=True,
        capture_output=True,
        text=True,
    )


def test_full_candidate_to_global_jql_pruning_contract(tmp_path):
    config = load_config()
    candidate = tmp_path / "candidate-records.jsonl"
    rows = []
    for index in range(8):
        source = f"original-source-{index % 4}"
        language = "ar" if index == 7 else ("en" if index < 4 else "fr")
        rows.append({
            "text": f"This is a synthetic educational sentence number {index}.",
            "language": language,
            "source": "normalized-family",
            "source_release": "synthetic-test-release",
            "group_id": f"group-{index}",
            "licence_id": "CC0-1.0",
            "text_origin": "synthetic test data",
            "provenance": {"source_original_name": source},
        })
    candidate.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    assessment = tmp_path / "assessment.parquet"
    assessment_summary = tmp_path / "assessment-summary.json"
    _run(
        "sample_jql_assessment.py",
        "--input", candidate,
        "--output", assessment,
        "--summary", assessment_summary,
        "--all",
        "--batch-size", "2",
    )
    assessment_meta = json.loads(assessment_summary.read_text())
    assert assessment_meta["sampling"] is False
    assert assessment_meta["rows"] == 8
    assert assessment_meta["input_sha256"] == hashlib.sha256(candidate.read_bytes()).hexdigest()

    shards_dir = tmp_path / "shards"
    _run("split_jql_parquet.py", "--input", assessment, "--output-dir", shards_dir)
    split_manifest = json.loads((shards_dir / "manifest.json").read_text())
    assert split_manifest["rows"] == 8
    assert split_manifest["shards"] == 8
    assert [item["rows"] for item in split_manifest["files"]] == [1] * 8

    ratings_dir = tmp_path / "ratings"
    ratings_dir.mkdir()
    judges = config["jql"]["judges"]
    embedder_revision = config["jql"]["embedder_revision"]
    head_revision = "b" * 40
    checkpoint_hashes = {judge: (chr(ord("c") + index) * 64) for index, judge in enumerate(judges)}
    for index, shard in enumerate(split_manifest["files"]):
        shard_path = shards_dir / shard["file"]
        shard_frame = pd.read_parquet(shard_path)
        row = shard_frame.iloc[0]
        raw_scores = {
            "gemma": float(index),
            "mistral": float(7 - index),
            "llama": float(index % 3),
        }
        ratings_name = f"shard-{index}.csv"
        with (ratings_dir / ratings_name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["id", "language", "ratings"])
            writer.writeheader()
            writer.writerow({
                "id": row["id"],
                "language": row["lang"],
                "ratings": json.dumps(raw_scores, sort_keys=True),
            })
        manifest = {
            "schema_version": 1,
            "pipeline_source_sha": "f" * 40,
            "pipeline_source_run_id": "123456",
            "input_file": shard["file"],
            "input_sha256": hashlib.sha256(shard_path.read_bytes()).hexdigest(),
            "input_rows": 1,
            "scored_rows": 1,
            "models": {
                "embedder_repository": config["jql"]["embedder_model"],
                "embedder_revision_requested": embedder_revision,
                "embedder_revision_resolved": embedder_revision,
                "head_repository": config["jql"]["head_repository"],
                "head_revision_requested": config["jql"]["head_repository_revision"],
                "head_revision_resolved": head_revision,
            },
            "head_checkpoint_sha256": checkpoint_hashes,
            "scoring": {
                "judges": judges,
                "embedding_dimension": config["jql"]["embedding_dimension"],
                "head_hidden_dimension": config["jql"]["head_hidden_dimension"],
                "max_token_length": config["jql"]["max_token_length"],
                "inference_batch_size": config["jql"]["inference_batch_size"],
                "dtype": "bfloat16",
                "pooling": "CLS",
                "normalization": "L2",
            },
            "runtime": {
                "python_version": "3.11.9",
                "torch_version": "2.6.0+cpu",
                "transformers_version": "4.44.2",
                "huggingface_hub_version": "0.26.5",
            },
        }
        (ratings_dir / f"{ratings_name}.manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

    quality = tmp_path / "quality.csv"
    with quality.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["id", "initial_capitalization", "terminal_punctuation"]
        )
        writer.writeheader()
        for row in pd.read_parquet(assessment).to_dict("records"):
            writer.writerow({
                "id": row["id"],
                "initial_capitalization": "pass",
                "terminal_punctuation": "pass",
            })

    full_csv = tmp_path / "full.csv"
    full_parquet = tmp_path / "full.parquet"
    full_summary = tmp_path / "full-summary.json"
    pruned_csv = tmp_path / "pruned.csv"
    pruned_parquet = tmp_path / "pruned.parquet"
    pruning_summary = tmp_path / "pruning-summary.json"
    _run(
        "merge_jql_ratings.py",
        "--input", assessment,
        "--ratings-dir", ratings_dir,
        "--quality", quality,
        "--shards-dir", shards_dir,
        "--output-csv", full_csv,
        "--output-parquet", full_parquet,
        "--summary", full_summary,
        "--include-text",
        "--pruned-output-csv", pruned_csv,
        "--pruned-output-parquet", pruned_parquet,
        "--pruning-summary", pruning_summary,
        env={"LANGID32_SOURCE_SHA": "f" * 40, "LANGID32_SOURCE_RUN_ID": "123456"},
    )

    summary = json.loads(full_summary.read_text())
    pruning = json.loads(pruning_summary.read_text())
    full = pd.read_csv(full_csv)
    pruned = pd.read_csv(pruned_csv)
    assert summary["rows"] == 8
    assert summary["ratings_rows"] == 8
    scored_counts = {
        (item["language"], item["source"]): item["count"]
        for item in summary["scored_by_language_source"]
    }
    assert sum(scored_counts.values()) == 8
    assert len(scored_counts) == 8
    assert summary["normalization_scope"] == "entire assessment corpus, all languages combined, independently per judge"
    assert summary["model_provenance"]["models"]["embedder_revision_resolved"] == embedder_revision
    assert pruning["scope"] == "global_all_languages_after_full_corpus_normalization"
    assert pruning["pruned_rows"] == 2
    assert pruning["retained_rows"] == 6
    assert len(full) == 8 and len(pruned) == 6
    assert "sentence" in pruned.columns
    assert full["jql_training_domain_status"].value_counts().to_dict() == {
        "training_domain": 7, "out_of_training_domain": 1
    }
    assert summary["jql_out_of_training_languages"] == config["jql"]["out_of_training_languages"]
    assert pruning["out_of_training_domain_rows_pruned"] + pruning["out_of_training_domain_rows_retained"] == 1
    assert set(full["source-variant"]) == {f"original-source-{i}" for i in range(4)}
    assert len(summary["shard_manifests"]) == 8
    from collections import Counter
    full_counts = Counter(full["source-variant"])
    retained_counts = Counter(pruned["source-variant"])
    pruned_counts = Counter()
    for item in pruning["pruned_by_language_source"]:
        pruned_counts[item["source"]] += item["count"]
    assert retained_counts + pruned_counts == full_counts
