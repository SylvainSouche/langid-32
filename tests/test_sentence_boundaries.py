from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_sentence_boundaries", ROOT / "scripts/check_sentence_boundaries.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_sentence_boundary_diagnostics_stream_all_row_groups_without_text(tmp_path, monkeypatch):
    source = tmp_path / "assessment.parquet"
    output = tmp_path / "quality" / "flags.csv"
    table = pa.table({
        "id": ["id-1", "id-2", "id-3"],
        "lang": ["en", "en", "ar"],
        "sentence": [
            "Hello world.",
            "lowercase fragment",
            "مرحبا بالعالم؟",
        ],
        "source-variant": ["source-a", "source-a", "source-b"],
    })
    pq.write_table(table, source, row_group_size=1)

    monkeypatch.setattr(sys, "argv", [
        "check_sentence_boundaries.py", "--input", str(source),
        "--output", str(output),
    ])
    MODULE.main()

    with output.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["id"] for row in rows] == ["id-1", "id-2", "id-3"]
    assert rows[0]["initial_capitalization"] == "pass"
    assert rows[0]["terminal_punctuation"] == "pass"
    assert rows[1]["initial_capitalization"] == "fail"
    assert rows[1]["terminal_punctuation"] == "fail"
    assert rows[2]["initial_capitalization"] == "not_applicable"
    assert rows[2]["terminal_punctuation"] == "pass"
    assert set(rows[0]) == {
        "id", "lang", "initial_capitalization", "terminal_punctuation",
    }
    output_text = output.read_text(encoding="utf-8")
    assert "Hello world." not in output_text
    assert "lowercase fragment" not in output_text
