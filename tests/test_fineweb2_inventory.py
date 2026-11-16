from langid32.fineweb2_inventory import TARGET_SUBSETS, inventory


def test_fineweb2_inventory_maps_targets_and_keeps_test_and_removed_separate():
    rows = [
        {"subset": "kor_Hang", "split": "train", "code": "kor", "script": "Hang",
         "name": "Korean", "words": "100000", "documents": "25000",
         "utf8_bytes": "500000", "parquet_bytes": "100000"},
        {"subset": "kor_Hang", "split": "test", "code": "kor", "script": "Hang",
         "name": "Korean", "words": "1000", "documents": "100",
         "utf8_bytes": "5000", "parquet_bytes": "1000"},
        {"subset": "kor_Hang_removed", "split": "train", "code": "kor", "script": "Hang",
         "name": "Korean", "words": "-", "documents": "50000",
         "utf8_bytes": "900000", "parquet_bytes": "200000"},
        {"subset": "bul_Cyrl", "split": "train", "code": "bul", "script": "Cyrl",
         "name": "Bulgarian", "words": "20000", "documents": "5000",
         "utf8_bytes": "100000", "parquet_bytes": "20000"},
    ]

    result = {row["language"]: row for row in inventory(rows)}

    assert len(result) == 32
    assert result["ko"]["status"] == "available"
    assert result["ko"]["filtered_train_documents"] == 25000
    assert result["ko"]["test_documents"] == 100
    assert result["ko"]["removed_train_documents"] == 50000
    assert result["ko"]["filtered_train_words"] == 100000
    assert result["bg"]["filtered_train_documents"] == 5000
    assert result["en"]["status"] == "separate_fineweb_dataset"
    assert result["et"]["status"] == "not_listed"


def test_target_mapping_has_32_classes_and_expected_special_cases():
    assert len(TARGET_SUBSETS) == 32
    assert TARGET_SUBSETS["ko"] == "kor_Hang"
    assert TARGET_SUBSETS["nn"] == "nno_Latn"
    assert TARGET_SUBSETS["en"] is None


def test_standard_estonian_and_latvian_iso6393_aliases_are_mapped():
    assert TARGET_SUBSETS["et"] == "ekk_Latn"
    assert TARGET_SUBSETS["lv"] == "lvs_Latn"
