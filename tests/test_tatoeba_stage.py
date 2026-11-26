import csv
import json

from scripts.stage_tatoeba import stage


def test_stage_tatoeba_uses_cc0_only_and_preserves_base_groups(tmp_path):
    cc0 = tmp_path / "sentences_CC0.csv"
    base = tmp_path / "sentences_base.csv"
    with cc0.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow([1, "fin", "Hei siellä.", "2026-11-14"])
        writer.writerow([2, "fin", "Hyvää päivää.", "2026-11-14"])
        writer.writerow([3, "fin", "Terve kaikille.", "2026-11-14"])
        writer.writerow([4, "fin", "Hyvää huomenta.", "2026-11-14"])
    with base.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow([1, "0"])
        writer.writerow([2, "1"])
        writer.writerow([3, "1"])
        writer.writerow([4, "0"])

    import argparse
    output = tmp_path / "stage.jsonl"
    args = argparse.Namespace(
        sentences_cc0=cc0, sentences_base=base, output=output,
        source_release="fixture", min_chars=1, max_chars=100, max_bytes=500,
    )
    stage(args)
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert len(rows) == 4
    assert rows[0]["language"] == "fi"
    assert rows[1]["group_id"] == rows[2]["group_id"] == "tatoeba:base:1"
    assert rows[1]["text_origin"] == "translated"
    assert rows[0]["text_origin"] == "original"
    assert all(row["licence_id"] == "CC0-1.0" for row in rows)
