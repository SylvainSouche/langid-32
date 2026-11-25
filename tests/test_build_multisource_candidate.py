import importlib.util
import json
from pathlib import Path

from langid32.settings import load_config


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_multisource_candidate.py"
SPEC = importlib.util.spec_from_file_location("build_multisource_candidate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _row(source, language, index):
    return {
        "text": f"Distinct sentence {source} {index}",
        "language": language,
        "source": source,
        "source_release": "test",
        "group_id": f"{source}:{index}",
        "licence_id": "CC0-1.0",
        "text_origin": "test",
        "provenance": {},
    }


def test_normalization_applies_source_language_scope_and_per_source_caps(tmp_path):
    config = load_config()
    config["acquisition"]["source_language_overrides"].update({
        "temu_cc0:component_a.hr": 1,
        "temu_cc0:component_b.hr": 1,
    })
    source = tmp_path / "input.jsonl"
    destination = tmp_path / "normalized.jsonl"
    rows = [
        _row("fineweb2:hrv_Latn", "hr", 1),
        _row("fineweb2:cat_Latn", "ca", 2),
        _row("temu_cc0:component_a", "hr", 3),
        _row("temu_cc0:component_a", "hr", 4),
        _row("temu_cc0:component_b", "hr", 5),
        _row("temu_cc0:component_b", "hr", 6),
    ]
    source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    report = MODULE.normalize_file(source, destination, config=config)
    retained = [json.loads(line) for line in destination.read_text(encoding="utf-8").splitlines()]

    assert len(retained) == 3
    assert report["filtered_superseded_sources"] == {
        "configured_source_target_reached": 2,
        "source_language_not_approved": 1,
    }
    assert report["source_counts"] == {"fineweb2": 1, "temu_cc0": 2}
    assert {row["provenance"]["source_original_name"] for row in retained} == {
        "fineweb2:hrv_Latn", "temu_cc0:component_a", "temu_cc0:component_b"
    }
