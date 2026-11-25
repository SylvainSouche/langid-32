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



def test_production_workflow_has_central_concurrency_and_deadline_guards():
    workflow = (ROOT / ".github/workflows/langid32-pipeline.yml").read_text()
    assert "max-parallel: ${{ fromJSON(needs.config.outputs.acquisition_max_parallel_source_tasks) }}" in workflow
    for name in ("historical:", "common-voice:", "waiting-source:", "candidate:", "jql:"):
        assert name in workflow
    assert workflow.count("Enforce shared six-hour workflow budget") == 5
    assert "needs: [config]" in workflow


def test_waiting_source_privacy_regexes_are_active():
    from scripts.acquire_waiting_sources import clean
    rules = load_config(ROOT / "config/langid32.toml")["acquisition"]["source_rules"]["waiting_sources"]
    base = "This is a sufficiently long ordinary sentence containing useful words"
    assert clean(base + " contact person@example.org", "en", rules) is None
    assert clean(base + " see https://example.org/page", "en", rules) is None
    assert clean(base + " server address 192.168.1.24", "en", rules) is None
    assert clean(base + " reference number 123456789012", "en", rules) is None


def test_common_voice_is_blocked_until_each_locale_is_accepted(tmp_path):
    import subprocess
    import sys
    config = load_config(ROOT / "config/langid32.toml")
    rule = config["acquisition"]["source_rules"]["common_voice_v22"]
    assert rule["languages"] == []
    assert rule["proposed_languages"] == ["fi", "el", "mt", "sl", "is"]
    script = ROOT / "scripts/download_common_voice_hf.py"
    result = subprocess.run(
        [sys.executable, str(script), "--output-dir", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "individual locale terms acceptance is pending" in result.stderr
    workflow = (ROOT / ".github/workflows/langid32-pipeline.yml").read_text()
    assert "common-voice:\n    if: false" in workflow
