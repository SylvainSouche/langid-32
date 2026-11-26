import hashlib
import importlib.util
import json
import re
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


def test_push_with_truncated_commit_payload_fails_closed(tmp_path, monkeypatch):
    _write_sources(tmp_path)
    _set_push_event(monkeypatch, tmp_path)
    event_path = tmp_path / "event.json"
    event = json.loads(event_path.read_text(encoding="utf-8"))
    event["size"] = 2
    event_path.write_text(json.dumps(event), encoding="utf-8")
    with pytest.raises(SystemExit, match="commit list is incomplete"):
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



def test_staged_workflow_targets_and_referenced_scripts_exist_at_run_commit():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/langid32-pipeline.yml").read_text(encoding="utf-8")
    worker = (root / "scripts/acquire_waiting_sources.py").read_text(encoding="utf-8")
    targets = root / "stages/01-acquisition/targets"

    script_refs = set(re.findall(
        r"(?:python3?|python)\s+((?:scripts|stages)/[A-Za-z0-9_./-]+\.py)",
        workflow,
    ))
    assert script_refs
    assert all((root / path).is_file() for path in script_refs)

    matrix_targets = set(re.findall(r"^\s*-\s*target:\s*([a-z0-9-]+)", workflow, flags=re.M))
    assert matrix_targets
    assert all((targets / f"{name}.py").is_file() for name in matrix_targets)
    for target in matrix_targets - {"gaois"}:
        source = target.replace("-", "_")
        assert f'args.source == "{source}"' in worker or f'args.source == "{target}"' in worker
    assert (root / "scripts/acquire_gaois_irish_legislation.py").is_file()

    checkout_blocks = re.findall(
        r"- uses: actions/checkout@v4(.*?)(?=\n\s+- (?:uses:|name:)|\Z)",
        workflow,
        flags=re.S,
    )
    assert checkout_blocks
    assert all("ref:" not in block for block in checkout_blocks)



def test_staged_pipeline_deletes_plaintext_after_encrypted_checkpoint_uploads():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/langid32-pipeline.yml").read_text(encoding="utf-8")
    assert workflow.count("Remove plaintext working files") == 5
    assert "rm -rf input out checkpoint.bin" in workflow
    assert "rm -rf input out .cache checkpoint.bin" in workflow
    assert "rm -rf input out checkpoints candidate.bin" in workflow
    assert "rm -rf input out checkpoint final.bin" in workflow
    assert "HF_HOME: ${{ github.workspace }}/.cache/huggingface" in workflow



def test_plaintext_leipzig_upload_workflows_are_retired():
    root = Path(__file__).resolve().parents[1]
    workflows = root / ".github/workflows"
    assert not (workflows / "acquire-leipzig-balanced.yml").exists()
    assert not (workflows / "acquire-leipzig-corpora.yml").exists()
    for path in workflows.glob("*.yml"):
        content = path.read_text(encoding="utf-8")
        assert "path: out/leipzig/" not in content, path.name
        assert "path: out/leipzig/**" not in content, path.name



def test_legacy_waiting_source_and_greynir_audits_remain_metadata_only_and_cleaned():
    root = Path(__file__).resolve().parents[1]
    waiting = (root / ".github/workflows/acquire-waiting-sources.yml").read_text(encoding="utf-8")
    assert "datasets==3.3.2" in waiting
    assert "huggingface_hub==0.26.5" in waiting
    assert "pyarrow==19.0.1" in waiting
    assert "path: out/*/manifest.json" in waiting
    assert "path: out/**" not in waiting
    assert "rm -rf out input .cache" in waiting

    greynir = (root / ".github/workflows/audit-greynir-corpus.yml").read_text(encoding="utf-8")
    assert "path: greynir-corpus/reports/greynir-corpus-audit.json" in greynir
    assert "rm -rf greynir-corpus" in greynir
