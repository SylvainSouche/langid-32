import copy
from pathlib import Path

import pytest

from langid32.settings import load_config, validate_acquisition_policy


ROOT = Path(__file__).resolve().parents[1]


def test_central_acquisition_policy_is_six_hour_safe():
    config = load_config(ROOT / "config/langid32.toml")
    validate_acquisition_policy(config)
    execution = config["execution"]
    assert execution["acquisition_files_per_batch"] == 1
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


def test_common_voice_hf_acquisition_is_enabled_for_configured_locales():
    config = load_config(ROOT / "config/langid32.toml")
    rule = config["acquisition"]["source_rules"]["common_voice_v22"]
    assert rule["target"] == 20000
    assert rule["languages"] == ["fi", "el", "mt", "sl", "is"]
    assert "proposed_languages" not in rule
    assert "status" not in rule

    downloader = (ROOT / "scripts/download_common_voice_hf.py").read_text()
    assert "individual locale terms acceptance" not in downloader
    assert "lack recorded individual terms acceptance" not in downloader
    assert 'BASE = f"https://huggingface.co/datasets/{REPO}/resolve"' in downloader

    workflow = (ROOT / ".github/workflows/langid32-pipeline.yml").read_text()
    assert "common-voice:\n    if: github.ref == 'refs/heads/main'" in workflow
    assert "if: false # Disabled until individual Common Voice locale terms" not in workflow



def test_waiting_source_record_rights_status_preserves_registered_holds():
    source = (ROOT / "scripts/acquire_waiting_sources.py").read_text(encoding="utf-8")
    register = (ROOT / "docs/source-register.md").read_text(encoding="utf-8")
    assert '"hold_constituent_terms_review"' in source
    assert '"hold_attribution_and_source_provenance_review"' in source
    assert "derivative attribution and source-document provenance remain on hold" in source
    assert "publisher-level declaration accepted" not in source
    assert "| **BSC-LT Legal Catalan-Spanish Parallel Corpus**" in register
    assert "**STAGED / HOLD**" in register
    assert "| **UN Arabic-English Filtered**" in register
    assert "**STAGED / ATTRIBUTION + PROVENANCE HOLD;" in register



def test_un_arabic_row_index_is_not_mislabelled_as_document_id():
    from scripts.acquire_waiting_sources import un_arabic_provenance

    provenance = un_arabic_provenance(
        {"text_ar": "نص عربي", "text_en": "English translation"},
        12345,
        "a" * 40,
    )
    assert provenance["source_row_index"] == 12345
    assert "source_record_id" not in provenance
    assert "source_document_id" not in provenance
    assert provenance["repo_commit"] == "a" * 40
    assert provenance["publisher_id"] == "united-nations"
    assert provenance["attribution_required"] is True



def test_acquisition_streaming_dependencies_are_config_pinned_and_used():
    config = load_config(ROOT / "config/langid32.toml")
    execution = config["execution"]
    assert execution["datasets_version"] == "3.3.2"
    assert execution["huggingface_hub_version"] == "0.26.5"
    assert execution["pyarrow_version"] == "19.0.1"

    workflow = (ROOT / ".github/workflows/langid32-pipeline.yml").read_text(encoding="utf-8")
    assert 'datasets==${{ steps.runtime.outputs.datasets_version }}' in workflow
    assert 'huggingface_hub==${{ steps.runtime.outputs.huggingface_hub_version }}' in workflow
    assert 'pyarrow==${{ steps.runtime.outputs.pyarrow_version }}' in workflow

    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert '"datasets==3.3.2"' in ci
    assert '"huggingface_hub==0.26.5"' in ci
    assert '"pyarrow==19.0.1"' in ci



def test_leipzig_historical_snapshot_is_restricted_to_six_current_languages():
    config = load_config(ROOT / "config/langid32.toml")
    expected = ["hr", "fi", "el", "mt", "sl", "is"]
    rules = config["acquisition"]["source_rules"]
    assert rules["leipzig_news"]["languages"] == expected
    assert rules["leipzig_wikipedia"]["languages"] == expected
    register = (ROOT / "docs/source-register.md").read_text(encoding="utf-8")
    assert "Current pipeline allowlist is exactly" in register
    assert "All 34 langid-32 labels targeted" not in register
