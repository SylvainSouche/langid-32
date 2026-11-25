from pathlib import Path
import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_waiting_sources.py"
SPEC = importlib.util.spec_from_file_location("acquire_waiting_sources", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_acquisition_quota_keys_preserve_individual_source_identity():
    sources = (
        "temu_cc0:datasets_sentences.tsv",
        "temu_cc0:another_component.tsv",
        "temu_cc0:literatura.txt",
    )
    for source in sources:
        assert MODULE.source_bucket(source) == source
    assert MODULE.source_bucket("fineweb2:hrv_Latn") == "fineweb2"
    assert MODULE.source_bucket("maalfrid2026:nb") == "maalfrid2026"
    assert MODULE.source_bucket("un_arabic_english_filtered:text_ar") == "un_arabic_english_filtered"
