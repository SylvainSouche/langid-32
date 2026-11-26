#!/usr/bin/env python3
"""Emit runtime settings for GitHub Actions from the authoritative TOML file."""
from __future__ import annotations

import hashlib
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
    }
    for name, snapshot in config["historical_snapshots"].items():
        values[f"historical_{name}_run_id"] = snapshot["run_id"]
        values[f"historical_{name}_artifact_name"] = snapshot["artifact_name"]
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
