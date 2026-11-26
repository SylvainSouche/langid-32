import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_pipeline_trigger.py"
SPEC = importlib.util.spec_from_file_location("validate_pipeline_trigger", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _write_sources(root):
    (root / "config").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "out").mkdir()
    (root / "config/langid32.toml").write_text("[project]\nname='test'\n")
    (root / "docs/source-register.md").write_text("# source register\n")
    (root / "docs/pipeline-contract.md").write_text("# contract\n")
    hashes = {
        "config_sha256": hashlib.sha256((root / "config/langid32.toml").read_bytes()).hexdigest(),
        "source_register_sha256": hashlib.sha256((root / "docs/source-register.md").read_bytes()).hexdigest(),
        "pipeline_contract_sha256": hashlib.sha256((root / "docs/pipeline-contract.md").read_bytes()).hexdigest(),
    }
    trigger = {
        "run_mode": "clean_full_pipeline",
        "nonce": "20261126-clean-run-01",
        **hashes,
        "artifact_reuse": False,
        "final_selection": "deferred",
        "privacy_review_required": True,
    }
    (root / "pipeline-trigger.json").write_text(json.dumps(trigger))
    return trigger


def _set_push_event(monkeypatch, tmp_path, *, changed_files=None):
    event = {
        "commits": [{
            "added": [],
            "modified": changed_files or ["pipeline-trigger.json"],
            "removed": [],
        }]
    }
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(event))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
    monkeypatch.setattr(MODULE, "ROOT", tmp_path)


def test_valid_guarded_push_trigger_passes_and_records_hashes(tmp_path, monkeypatch):
    trigger = _write_sources(tmp_path)
    _set_push_event(monkeypatch, tmp_path)
    MODULE.main()
    result = json.loads((tmp_path / "out/pipeline-trigger-validation.json").read_text())
    assert result["status"] == "passed"
    assert result["nonce"] == trigger["nonce"]
    assert result["trigger_commit_sha"] == "a" * 40
    assert result["pipeline_contract_sha256"] == trigger["pipeline_contract_sha256"]


def test_push_without_trigger_file_change_fails_closed(tmp_path, monkeypatch):
    _write_sources(tmp_path)
    _set_push_event(monkeypatch, tmp_path, changed_files=["README.md"])
    with pytest.raises(SystemExit, match="must modify pipeline-trigger.json and no other path"):
        MODULE.main()


def test_push_with_trigger_and_code_change_fails_closed(tmp_path, monkeypatch):
    _write_sources(tmp_path)
    _set_push_event(
        monkeypatch, tmp_path,
        changed_files=["pipeline-trigger.json", "scripts/acquire_waiting_sources.py"],
    )
    with pytest.raises(SystemExit, match="must modify pipeline-trigger.json and no other path"):
        MODULE.main()


def test_disabled_trigger_cannot_launch(tmp_path, monkeypatch):
    _write_sources(tmp_path)
    trigger_path = tmp_path / "pipeline-trigger.json"
    trigger = json.loads(trigger_path.read_text())
    trigger["run_mode"] = "disabled"
    trigger_path.write_text(json.dumps(trigger))
    _set_push_event(monkeypatch, tmp_path)
    with pytest.raises(SystemExit, match="not armed for a clean full run"):
        MODULE.main()


def test_contract_hash_mismatch_fails_closed(tmp_path, monkeypatch):
    _write_sources(tmp_path)
    trigger_path = tmp_path / "pipeline-trigger.json"
    trigger = json.loads(trigger_path.read_text())
    trigger["pipeline_contract_sha256"] = "0" * 64
    trigger_path.write_text(json.dumps(trigger))
    _set_push_event(monkeypatch, tmp_path)
    with pytest.raises(SystemExit, match="pipeline_contract_sha256 does not match"):
        MODULE.main()


def test_manual_dispatch_does_not_require_push_trigger_file(tmp_path, monkeypatch):
    _write_sources(tmp_path)
    monkeypatch.setattr(MODULE, "ROOT", tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.delenv("GITHUB_REF", raising=False)
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    MODULE.main()
    result = json.loads((tmp_path / "out/pipeline-trigger-validation.json").read_text())
    assert result == {"event": "workflow_dispatch", "status": "not_applicable"}



def test_preflight_manifest_uses_actual_common_voice_acquisition_path():
    root = Path(__file__).resolve().parents[1]
    emitter = (root / "scripts/emit_runtime_config.py").read_text(encoding="utf-8")
    target = (root / "stages/01-acquisition/targets/common-voice.py").read_text(encoding="utf-8")
    assert '"input/common-voice/**"' in emitter
    assert 'root / "input/common-voice/source"' in target
    assert 'root / "input/common-voice"' in target
    assert '"input/common_voice/**"' not in emitter
