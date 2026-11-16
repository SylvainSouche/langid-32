from langid32.fineweb2_shards import flatten_shards


def test_flatten_shards_filters_to_target_subsets_and_preserves_roles():
    payload = {
        "parquet_files": [
            {"config": "kor_Hang", "split": "train", "filename": "000.parquet",
             "size": 1234, "url": "https://example.invalid/kor.parquet"},
            {"config": "kor_Hang", "split": "test", "filename": "test.parquet",
             "size": 100, "url": "https://example.invalid/test.parquet"},
            {"config": "kor_Hang_removed", "split": "train", "filename": "removed.parquet",
             "size": 500, "url": "https://example.invalid/removed.parquet"},
            {"config": "ekk_Latn", "split": "train", "filename": "estonian.parquet",
             "size": 200, "url": "https://example.invalid/estonian.parquet"},
            {"config": "eng_Latn", "split": "train", "filename": "english.parquet",
             "size": 300, "url": "https://example.invalid/english.parquet"},
        ],
        "pending": [],
        "failed": [],
        "partial": False,
    }

    rows = flatten_shards(payload)

    assert len(rows) == 4
    assert {(r["language"], r["subset_role"], r["split"]) for r in rows} == {
        ("ko", "filtered", "train"),
        ("ko", "filtered", "test"),
        ("ko", "removed", "train"),
        ("et", "filtered", "train"),
    }
    assert rows[0]["size_bytes"] == 1234
