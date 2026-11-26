import json

import pytest

from scripts.sample_jql_assessment import original_source_id
from scripts.merge_jql_ratings import read_score_manifests, validate_split_manifest
from scripts.split_jql_parquet import shard_sizes


def _write_manifest(directory, shards_dir, index, *, head_revision="b" * 40, source_run_id="123456"):
    input_name = f"shard-{index:02d}.parquet"
    input_path = shards_dir / input_name
    input_path.write_bytes(f"shard-{index}".encode())
    import hashlib

    input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
    csv_name = f"shard-{index}.csv"
    manifest = {
        "schema_version": 1,
        "pipeline_source_sha": "f" * 40,
        "pipeline_source_run_id": source_run_id,
        "input_file": input_name,
        "input_sha256": input_hash,
        "input_rows": 1,
        "scored_rows": 1,
        "models": {
            "embedder_repository": "Snowflake/snowflake-arctic-embed-m-v2.0",
            "embedder_revision_resolved": "a" * 40,
            "head_repository": "JQL-AI/JQL-Edu-Heads",
            "head_revision_resolved": head_revision,
        },
        "head_checkpoint_sha256": {
            "gemma": "c" * 64,
            "mistral": "d" * 64,
            "llama": "e" * 64,
        },
        "scoring": {"judges": ["gemma", "mistral", "llama"], "dtype": "float32"},
    }
    (directory / f"{csv_name}.manifest.json").write_text(json.dumps(manifest))
    return csv_name


def test_original_source_identity_uses_provenance_not_source_family():
    row = {"provenance": {"source_original_name": "leipzig_news_2023"}}
    assert original_source_id(row, "leipzig") == "leipzig_news_2023"


def test_original_source_identity_falls_back_to_source():
    assert original_source_id({}, "tatoeba") == "tatoeba"


def test_original_source_identity_rejects_empty_source():
    with pytest.raises(ValueError):
        original_source_id({}, "  ")


def test_score_manifests_verify_exact_shards_and_pinned_models(tmp_path):
    ratings = tmp_path / "ratings"
    shards = tmp_path / "shards"
    ratings.mkdir()
    shards.mkdir()
    csv_name = _write_manifest(ratings, shards, 0)
    provenance, records = read_score_manifests(
        ratings, {csv_name: 1}, shards, expected_shards=1
    )
    assert provenance["models"]["embedder_revision_resolved"] == "a" * 40
    assert records[0]["input_file"] == "shard-00.parquet"


def test_score_manifests_reject_input_hash_mismatch(tmp_path):
    ratings = tmp_path / "ratings"
    shards = tmp_path / "shards"
    ratings.mkdir()
    shards.mkdir()
    csv_name = _write_manifest(ratings, shards, 0)
    (shards / "shard-00.parquet").write_bytes(b"changed")
    with pytest.raises(SystemExit, match="Input shard hash mismatch"):
        read_score_manifests(ratings, {csv_name: 1}, shards, expected_shards=1)


def test_score_manifests_reject_mixed_model_revisions(tmp_path):
    ratings = tmp_path / "ratings"
    shards = tmp_path / "shards"
    ratings.mkdir()
    shards.mkdir()
    csv0 = _write_manifest(ratings, shards, 0)
    csv1 = _write_manifest(ratings, shards, 1, head_revision="f" * 40)
    with pytest.raises(SystemExit, match="different model revisions"):
        read_score_manifests(
            ratings, {csv0: 1, csv1: 1}, shards, expected_shards=2
        )

def test_split_manifest_proves_exact_assessment_partition(tmp_path):
    shards = tmp_path / "shards"
    shards.mkdir()
    assessment = tmp_path / "assessment.parquet"
    assessment.write_bytes(b"assessment")
    shard = shards / "shard-00.parquet"
    shard.write_bytes(b"shard-data")
    import hashlib

    manifest = {
        "input": assessment.name,
        "input_sha256": hashlib.sha256(assessment.read_bytes()).hexdigest(),
        "rows": 3,
        "shards": 1,
        "files": [{
            "file": shard.name,
            "rows": 3,
            "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
        }],
    }
    (shards / "manifest.json").write_text(json.dumps(manifest))
    _, files = validate_split_manifest(assessment, shards, 3, 1)
    assert files["shard-00.parquet"]["rows"] == 3


def test_split_manifest_rejects_missing_rows_or_unsafe_paths(tmp_path):
    shards = tmp_path / "shards"
    shards.mkdir()
    assessment = tmp_path / "assessment.parquet"
    assessment.write_bytes(b"assessment")
    manifest = {
        "input": assessment.name,
        "input_sha256": __import__("hashlib").sha256(assessment.read_bytes()).hexdigest(),
        "rows": 1,
        "shards": 1,
        "files": [{"file": "../outside.parquet", "rows": 1, "sha256": "x"}],
    }
    (shards / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(SystemExit, match="Invalid or duplicate shard filename"):
        validate_split_manifest(assessment, shards, 1, 1)

def test_jql_shard_plan_is_balanced_and_exact():
    sizes = shard_sizes(10, 4)
    assert sizes == [3, 3, 2, 2]
    assert sum(sizes) == 10
    assert max(sizes) - min(sizes) <= 1


def test_jql_shard_plan_rejects_empty_shards():
    with pytest.raises(ValueError):
        shard_sizes(3, 4)

def test_score_manifests_reject_mixed_source_pipeline_runs(tmp_path):
    ratings = tmp_path / "ratings"
    shards = tmp_path / "shards"
    ratings.mkdir()
    shards.mkdir()
    csv0 = _write_manifest(ratings, shards, 0)
    csv1 = _write_manifest(ratings, shards, 1, source_run_id="654321")
    with pytest.raises(SystemExit, match="different model revisions"):
        read_score_manifests(
            ratings, {csv0: 1, csv1: 1}, shards, expected_shards=2
        )
