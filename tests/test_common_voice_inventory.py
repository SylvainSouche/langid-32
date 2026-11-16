import csv
import json

from langid32.common_voice_inventory import build_rows, count_sentence_file


def test_count_sentence_file_normalizes_and_deduplicates(tmp_path):
    path = tmp_path / "validated_sentences.tsv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["sentence_id", "sentence", "is_used"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerow({"sentence_id": "1", "sentence": "École de ski en hiver.", "is_used": "true"})
        writer.writerow({"sentence_id": "2", "sentence": "  E\u0301cole   de ski en hiver. ", "is_used": "false"})
        writer.writerow({"sentence_id": "3", "sentence": "Court.", "is_used": "true"})
    counts = count_sentence_file(path, min_chars=12, max_chars=100, max_bytes=200)
    assert counts["rows"] == 3
    assert counts["is_used_true"] == 2
    assert counts["is_used_false"] == 1
    assert counts["unique_within_file"] == 1
    assert counts["duplicate_normalized_text"] == 1
    assert counts["too_short"] == 1


def test_build_rows_maps_target_locales_and_metadata(tmp_path):
    release = tmp_path / "release.json"
    release.write_text(json.dumps({
        "locales": {
            "fr": {"validatedSentences": 123, "unvalidatedSentences": 4,
                   "clips": 5, "users": 6},
            "zh-CN": {"validatedSentences": 10},
            "zh-TW": {"validatedSentences": 20},
        }
    }), encoding="utf-8")
    rows = build_rows(release, None, 12, 500, 1500)
    fr = next(row for row in rows if row["language"] == "fr")
    zh = [row for row in rows if row["language"] == "zh"]
    assert fr["metadata_validated_sentences"] == 123
    assert fr["tsv_status"] == "not_measured"
    assert {row["locale"] for row in zh} == {"zh-CN", "zh-TW"}
