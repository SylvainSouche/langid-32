import csv
import json

from langid32.common_voice_inventory import build_rows, count_sentence_file


def test_count_sentence_file_normalizes_and_deduplicates(tmp_path):
    path = tmp_path / "validated_sentences.tsv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["sentence_id", "sentence", "is_used", "source", "sentence_domain"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerow({"sentence_id": "1", "sentence": "École de ski en hiver.", "is_used": "true", "source": "user", "sentence_domain": "general"})
        writer.writerow({"sentence_id": "2", "sentence": "  E\u0301cole   de ski en hiver. ", "is_used": "false", "source": "legacy", "sentence_domain": "general"})
        writer.writerow({"sentence_id": "3", "sentence": "Court.", "is_used": "true", "source": "user", "sentence_domain": ""})
    counts = count_sentence_file(path, min_chars=12, max_chars=100, max_bytes=200)
    assert counts["rows"] == 3
    assert counts["is_used_true"] == 2
    assert counts["is_used_false"] == 1
    assert counts["unique_within_target_language"] == 1
    assert counts["duplicate_normalized_text"] == 1
    assert counts["too_short"] == 1
    assert counts["is_used_true_within_length_limits"] == 1
    assert counts["unique_is_used_true_within_target_language"] == 1
    assert '"user": 2' in counts["source_counts_json"]
    assert '"general": 2' in counts["domain_counts_json"]


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

def test_build_rows_deduplicates_chinese_across_locale_files(tmp_path):
    release = tmp_path / "release.json"
    release.write_text(json.dumps({
        "locales": {
            "zh-CN": {"validatedSentences": 1},
            "zh-TW": {"validatedSentences": 1},
        }
    }), encoding="utf-8")
    for locale in ("zh-CN", "zh-TW"):
        folder = tmp_path / "data" / locale
        folder.mkdir(parents=True)
        with (folder / "validated_sentences.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as stream:
            writer = csv.DictWriter(
                stream, fieldnames=["sentence_id", "sentence", "is_used"],
                delimiter="\t",
            )
            writer.writeheader()
            writer.writerow({
                "sentence_id": "1", "sentence": "這是一個完整的測試句子。",
                "is_used": "true",
            })
    rows = build_rows(release, tmp_path / "data", 12, 500, 1500)
    zh = [row for row in rows if row["language"] == "zh"]
    assert zh[0]["unique_is_used_true_within_target_language"] == 1
    assert zh[1]["unique_is_used_true_within_target_language"] == 0
    assert zh[1]["duplicate_normalized_text"] == 1
