import importlib.util
from pathlib import Path

from langid32.settings import load_config


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "curate_common_voice_hf.py"
SPEC = importlib.util.spec_from_file_location("curate_common_voice_hf", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_common_voice_expected_script_filter():
    assert MODULE.script_ratio("Καλημέρα σε όλους", "GREEK") > 0.95
    assert MODULE.script_ratio("Terve kaikille ystäville", "LATIN") > 0.95
    assert MODULE.script_ratio("Hello Καλημέρα", "LATIN") < 0.70


def test_common_voice_script_policy_covers_enabled_locales():
    cfg = load_config()
    languages = set(cfg["acquisition"]["source_rules"]["common_voice_v22"]["languages"])
    scripts = cfg["acquisition"]["source_rules"]["common_voice_v22"]["script"]["by_language"]
    assert set(scripts) == languages
    assert cfg["acquisition"]["source_rules"]["common_voice_v22"]["script"]["minimum_ratio"] == 0.70
