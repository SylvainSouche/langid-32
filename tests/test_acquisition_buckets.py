from pathlib import Path
import importlib.util


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_waiting_sources.py"
SPEC = importlib.util.spec_from_file_location("acquire_waiting_sources", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_acquisition_quota_keys_preserve_individual_source_identity():
    assert MODULE.source_bucket("temu_cc0:datasets_sentences.tsv") == "temu_cc0:datasets_sentences.tsv"
    assert MODULE.source_bucket("temu_cc0:another_component.tsv") == "temu_cc0:another_component.tsv"
    assert MODULE.source_bucket("temu_cc0:literatura.txt") == "temu_cc0"
    assert MODULE.source_bucket("bsc_legal:dogc_ca-es.tsv") == "bsc_legal"
    assert MODULE.source_bucket("fineweb2:arb_Arab") == "fineweb2"
    assert MODULE.source_bucket("common_voice_v22") == "common_voice_v22"


def test_arabic_screening_uses_actual_arabic_unicode_range():
    text = "هذا نص عربي واضح ومفيد للاختبار، ويتكون من كلمات عربية كافية لاجتياز المرشح."
    assert MODULE.clean(text, "ar") == text
    assert MODULE.clean("This is an English sentence with enough letters to pass.", "ar") is None
