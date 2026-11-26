from statistics import mean
from pathlib import Path
import subprocess
import sys

from scripts.check_sentence_boundaries import (
    capitalization_status,
    punctuation_status,
)
from scripts.merge_jql_ratings import quantile_normalize


def test_capitalization_unicode_and_caseless_languages():
    assert capitalization_status("«Été magnifique.»", "fr") == "pass"
    assert capitalization_status("«été magnifique.»", "fr") == "fail"
    assert capitalization_status("مرحبا بالعالم؟", "ar") == "not_applicable"
    assert capitalization_status("你好。", "zh") == "not_applicable"


def test_terminal_punctuation_with_closing_quotes():
    assert punctuation_status("A complete sentence.") == "pass"
    assert punctuation_status("«Une phrase complète !»") == "pass"
    assert punctuation_status("A sentence fragment") == "fail"
    assert punctuation_status("A Greek question;") == "fail"


def test_quantile_normalization_is_monotonic_and_tie_safe():
    result = quantile_normalize([10.0, 20.0, 20.0, 40.0])
    assert result[0] < result[1] == result[2] < result[3]
    assert abs(mean(result)) < 1e-12


def test_final_30k_selection_is_fail_closed_until_user_approval():
    script = Path(__file__).resolve().parents[1] / "scripts" / "select_jql_consensus.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "FINAL SELECTION DISABLED BY CONTRACT" in result.stderr
