import copy
from pathlib import Path

import pytest

from langid32.settings import load_config, validate_acquisition_policy


ROOT = Path(__file__).resolve().parents[1]


def test_central_acquisition_policy_is_six_hour_safe():
    config = load_config(ROOT / "config/langid32.toml")
    validate_acquisition_policy(config)
    execution = config["execution"]
    assert execution["acquisition_files_per_batch"] == 8
    assert execution["acquisition_max_parallel_source_tasks"] == 4
    assert execution["acquisition_global_budget_minutes"] + execution["acquisition_safety_margin_minutes"] <= 360


def test_source_family_quota_alias_is_rejected():
    config = load_config(ROOT / "config/langid32.toml")
    config = copy.deepcopy(config)
    config["acquisition"]["source_rules"]["macocu"]["quota_key"] = "macocu"
    with pytest.raises(ValueError, match="quota alias is forbidden"):
        validate_acquisition_policy(config)


def test_six_hour_budget_overrun_is_rejected():
    config = load_config(ROOT / "config/langid32.toml")
    config = copy.deepcopy(config)
    config["execution"]["acquisition_global_budget_minutes"] = 340
    with pytest.raises(ValueError, match="six-hour limit"):
        validate_acquisition_policy(config)


def test_filtering_must_precede_quota():
    config = load_config(ROOT / "config/langid32.toml")
    config = copy.deepcopy(config)
    config["acquisition"]["privacy_filter_before_quota"] = False
    with pytest.raises(ValueError, match="before quota"):
        validate_acquisition_policy(config)



def test_shared_runtime_budget_guard_respects_safety_reserve():
    import subprocess
    import sys
    script = ROOT / "scripts" / "check_runtime_budget.py"
    ok = subprocess.run(
        [sys.executable, str(script), "--started-epoch", str(int(__import__("time").time()) - 60),
         "--budget-minutes", "330", "--safety-margin-minutes", "30"],
        capture_output=True, text=True,
    )
    assert ok.returncode == 0, ok.stderr
    blocked = subprocess.run(
        [sys.executable, str(script), "--started-epoch", "1000",
         "--budget-minutes", "330", "--safety-margin-minutes", "30"],
        capture_output=True, text=True,
    )
    assert blocked.returncode != 0
    assert "safety reserve" in blocked.stderr
