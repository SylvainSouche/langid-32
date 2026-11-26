#!/usr/bin/env python3
"""Emit runtime settings for GitHub Actions from the authoritative TOML file."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config


def main() -> None:
    config = load_config(ROOT / "config/langid32.toml")
    values = {
        "python_version": config["execution"]["python_version"],
        "artifact_retention_days": config["execution"]["artifact_retention_days"],
        "checkpoint_retention_days": config["execution"]["checkpoint_retention_days"],
        "curl_retry_count": config["execution"]["curl_retry_count"],
        "acquisition_files_per_batch": config["execution"]["acquisition_files_per_batch"],
        "acquisition_max_parallel_source_tasks": config["execution"]["acquisition_max_parallel_source_tasks"],
        "acquisition_job_timeout_minutes": config["execution"]["acquisition_job_timeout_minutes"],
        "acquisition_global_budget_minutes": config["execution"]["acquisition_global_budget_minutes"],
        "acquisition_safety_margin_minutes": config["execution"]["acquisition_safety_margin_minutes"],
        "acquisition_started_epoch": int(time.time()),
        "code_commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "config_sha256": hashlib.sha256((ROOT / "config/langid32.toml").read_bytes()).hexdigest(),
        "source_register_sha256": hashlib.sha256((ROOT / "docs/source-register.md").read_bytes()).hexdigest(),
        "pipeline_contract_sha256": hashlib.sha256((ROOT / "docs/pipeline-contract.md").read_bytes()).hexdigest(),
        "pipeline_trigger_sha256": hashlib.sha256((ROOT / "pipeline-trigger.json").read_bytes()).hexdigest(),
    }
    for name, snapshot in config["historical_snapshots"].items():
        values[f"historical_{name}_run_id"] = snapshot["run_id"]
        values[f"historical_{name}_artifact_name"] = snapshot["artifact_name"]

    manifest = {
        "schema_version": 1,
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "code_commit_sha": values["code_commit_sha"],
        "generated_at_epoch": values["acquisition_started_epoch"],
        "policy_hashes": {
            "config_sha256": values["config_sha256"],
            "source_register_sha256": values["source_register_sha256"],
            "pipeline_contract_sha256": values["pipeline_contract_sha256"],
            "pipeline_trigger_sha256": values["pipeline_trigger_sha256"],
        },
        "pipeline_trigger": json.loads((ROOT / "pipeline-trigger.json").read_text(encoding="utf-8")),
        "languages": config["project"]["languages"],
        "source_revision_plan": {
            "source_rules": config["acquisition"]["source_rules"],
            "source_language_overrides": config["acquisition"].get("source_language_overrides", {}),
            "code_commit_sha_pins_adapter_constants": True,
        },
        "historical_snapshots": config["historical_snapshots"],
        "candidate_policy": config["candidate"],
        "jql_policy": config["jql"],
        "execution_policy": config["execution"],
        "expected_inputs": [
            "input/v5/records.jsonl",
            "input/leipzig/leipzig-candidates.jsonl",
            "input/tatoeba/tatoeba-cc0-staged.jsonl",
            "input/dgt/dgt-tm-2021-staged.jsonl",
            "input/common_voice/**",
            "input/waiting/**",
        ],
        "expected_outputs": [
            "out/candidate/records.jsonl",
            "out/candidate/manifest.json",
            "out/jql-assessment-full.parquet",
            "out/jql-assessment-full-summary.json",
            "encrypted artifact: langid-32-jql-assessment-full-encrypted",
            "encrypted downstream artifact: langid-32-jql-pruned-pool-encrypted",
        ],
        "stages": [
            "preflight",
            "fresh acquisition plus pinned historical snapshots",
            "privacy/quality filtering and per-original-source quotas",
            "cross-source and cross-language candidate construction",
            "full-pool JQL assessment",
            "three-judge scoring, global normalization and bottom-25% pruning",
            "manual privacy/source-rights review hand-off; final 30k selection deferred",
        ],
    }
    manifest_path = ROOT / "out" / "preflight-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    values["preflight_manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        raise SystemExit("GITHUB_OUTPUT is required")
    values["acquisition_deadline_epoch"] = values["acquisition_started_epoch"] + values["acquisition_global_budget_minutes"] * 60
    with open(output, "a", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}" + chr(10))
    print(values)


if __name__ == "__main__":
    main()
