import argparse
import csv
import json

from langid32.corpus import assign_split, normalize_text, prepare


def test_normalize_preserves_diacritics_and_punctuation():
    assert normalize_text("  École\t de  ski ! ") == "École de ski !"


def test_split_is_deterministic():
    first = assign_split("document-42", "seed", 0.1, 0.1)
    assert first == assign_split("fr", "document-42", "seed", 0.1, 0.1)


def test_prepare_writes_text_only_splits_and_manifest(tmp_path):
    source = tmp_path / "sample.tsv"
    with source.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["sentence", "locale", "sentence_id"],
                                delimiter="\t")
        writer.writeheader()
        writer.writerow({"sentence": "Bonjour, le monde !", "locale": "fr",
                         "sentence_id": "source-a"})
        writer.writerow({"sentence": "Hello, world!", "locale": "en",
                         "sentence_id": "source-b"})
    output = tmp_path / "out"
    args = argparse.Namespace(
        input=str(source), output=str(output), languages=["fr", "en"],
        language=None, language_column="locale", text_column="sentence",
        group_column="sentence_id", min_chars=1, max_chars=100, max_bytes=500,
        exclude_regex=[], seed="test", validation_fraction=0.0, test_fraction=0.0,
        max_per_language=0, source_name="fixture", source_release="1",
        source_licence="CC0-1.0", source_download_origin="local test",
    )
    manifest = prepare(args)
    train = [json.loads(line) for line in (output / "train.jsonl").read_text().splitlines()]
    assert {item["language"] for item in train} == {"fr", "en"}
    assert all(set(item) == {"text", "language", "source", "split"} for item in train)
    assert manifest["counts"]["fr:train"] == 1
    assert (output / "manifest.json").exists()
