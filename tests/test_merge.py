import json
from pathlib import Path

from langid32.merge import merge, split_for


def _args(tmp_path, inputs, cap=0):
    import argparse
    return argparse.Namespace(
        inputs=inputs, output=tmp_path / "out", min_chars=1, max_chars=500,
        max_bytes=1500, max_per_language=cap, validation_fraction=0.1,
        test_fraction=0.1, seed="test-seed",
    )


def _row(text, language, source, group):
    return {
        "text": text, "language": language, "source": source,
        "source_release": "r1", "group_id": group,
        "licence_id": "CC0-1.0", "text_origin": "original",
        "provenance": {"document": "opaque-id"},
    }


def test_same_group_has_same_split_across_languages():
    assert split_for("source:document-1", "seed", 0.1, 0.1) == split_for(
        "source:document-1", "seed", 0.1, 0.1
    )


def test_merge_deduplicates_across_sources_and_retains_internal_provenance(tmp_path):
    input_a = tmp_path / "a.jsonl"
    input_b = tmp_path / "b.jsonl"
    input_a.write_text(json.dumps(_row(" Bonjour  monde ", "fr", "a", "a:doc1")) + "\n"
                       + json.dumps(_row("Hello world", "en", "a", "a:doc1")) + "\n")
    input_b.write_text(json.dumps(_row("Bonjour monde", "fr", "b", "b:doc9")) + "\n")
    args = _args(tmp_path, [input_a, input_b])
    merge(args)
    output = args.output
    public = []
    for split in ("train", "validation", "test"):
        public.extend(json.loads(line) for line in
                      (output / f"{split}.jsonl").read_text().splitlines())
    assert sum(row["language"] == "fr" for row in public) == 1
    assert sum(row["language"] == "en" for row in public) == 1
    internal = [json.loads(line) for line in (output / "records.jsonl").read_text().splitlines()]
    assert all("group_id" in row and "licence_id" in row and "provenance" in row
               for row in internal)
    assert all("group_id" not in row for row in public)


def test_merge_applies_cap_after_dedup(tmp_path):
    source = tmp_path / "source.jsonl"
    rows = [_row(f"Sentence number {i}", "fr", "a", f"a:doc{i}") for i in range(100)]
    source.write_text("".join(json.dumps(row) + "\n" for row in rows))
    args = _args(tmp_path, [source], cap=20)
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    assert sum(v for k, v in manifest["counts"].items() if k.startswith("fr:")) == 20
