import csv

from langid32.tatoeba_inventory import inventory


def test_tatoeba_cc0_inventory_counts_languages_and_base_groups(tmp_path):
    sentences = tmp_path / "sentences_CC0.csv"
    with sentences.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow([1, "fra", "Bonjour tout le monde !", "2026-01-01"])
        writer.writerow([2, "fra", "Bonjour tout le monde !", "2026-01-02"])
        writer.writerow([3, "fra", "Une phrase différente pour tester.", "2026-01-03"])
        writer.writerow([4, "eng", "Hello there, this is a sentence.", "2026-01-03"])
    base = tmp_path / "sentences_base.csv"
    with base.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow([1, 0])
        writer.writerow([2, 1])
        writer.writerow([3, 0])
        writer.writerow([4, 0])
    rows = inventory(sentences, base, 12, 500, 1500)
    fr = next(row for row in rows if row["language"] == "fr")
    assert fr["cc0_rows"] == 3
    assert fr["eligible_rows"] == 3
    assert fr["unique_eligible_text"] == 2
    assert fr["eligible_originals_base_zero"] == 2
    assert fr["eligible_translations_base_positive"] == 1
    assert fr["eligible_translation_groups"] == 2
