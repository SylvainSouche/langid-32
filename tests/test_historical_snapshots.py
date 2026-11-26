import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "stages" / "01-acquisition" / "targets" / "historical.py"
SPEC = importlib.util.spec_from_file_location("langid32_historical_target", MODULE_PATH)
historical = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(historical)


def _record(language="fr"):
    return {
        "text": "A valid historical sentence with sufficient content.",
        "language": language,
        "source": "normalized-family",
        "source_release": "pinned-release",
        "group_id": "group-1",
        "licence_id": "CC0-1.0",
        "text_origin": "historical source record",
        "provenance": {"source_original_name": "original-source"},
    }


def test_historical_snapshot_validation_hashes_and_counts_original_source(tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_text(json.dumps(_record()) + "\n", encoding="utf-8")
    result = historical.validate_snapshot(tmp_path, "records.jsonl", {"fr"})
    assert result["rows"] == 1
    assert result["original_source_language_counts"] == {"original-source:fr": 1}
    assert len(result["sha256"]) == 64


def test_historical_snapshot_validation_rejects_unexpected_language(tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_text(json.dumps(_record("xx")) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="unexpected language"):
        historical.validate_snapshot(tmp_path, "records.jsonl", {"fr"})


def test_historical_snapshot_validation_requires_exactly_one_file(tmp_path):
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    (tmp_path / "one" / "records.jsonl").write_text(json.dumps(_record()) + "\n")
    (tmp_path / "two" / "records.jsonl").write_text(json.dumps(_record()) + "\n")
    with pytest.raises(SystemExit, match="Expected exactly one"):
        historical.validate_snapshot(tmp_path, "records.jsonl", {"fr"})
