from langid32.fineweb2_shards import flatten_shards, target_failed_conversions


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
            {"config": "tur_Latn", "split": "partial-train", "filename": "turkish.parquet",
             "size": 400, "url": "https://example.invalid/turkish.parquet"},
            {"config": "eng_Latn", "split": "train", "filename": "english.parquet",
             "size": 300, "url": "https://example.invalid/english.parquet"},
        ],
        "pending": [],
        "failed": [],
        "partial": False,
    }

    rows = flatten_shards(payload)

    assert len(rows) == 5
    assert {(r["language"], r["subset_role"], r["split"]) for r in rows} == {
        ("ko", "filtered", "train"),
        ("ko", "filtered", "test"),
        ("ko", "removed", "train"),
        ("et", "filtered", "train"),
        ("tr", "filtered", "train"),
    }
    partial = next(r for r in rows if r["language"] == "tr")
    assert partial["partial"] is True
    assert partial["api_split"] == "partial-train"
    assert rows[0]["size_bytes"] == 1234



def test_target_failed_conversions_reports_only_project_subsets():
    payload = {
        "failed": [
            {"kind": "config-parquet", "config": "spa_Latn", "split": None},
            {"kind": "config-parquet", "config": "tur_Latn", "split": None},
            {"kind": "config-parquet", "config": "amh_Ethi", "split": None},
        ]
    }

    assert target_failed_conversions(payload) == [
        {"config": "spa_Latn", "kind": "config-parquet"},
        {"config": "tur_Latn", "kind": "config-parquet"},
    ]
