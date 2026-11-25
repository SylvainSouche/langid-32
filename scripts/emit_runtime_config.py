#!/usr/bin/env python3
"""Emit runtime settings for GitHub Actions from the authoritative TOML file."""
from __future__ import annotations

import os
import sys
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
    }
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        raise SystemExit("GITHUB_OUTPUT is required")
    with open(output, "a", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}" + chr(10))
    print(values)


if __name__ == "__main__":
    main()
