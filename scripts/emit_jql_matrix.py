#!/usr/bin/env python3
"""Emit the JQL shard matrix from the authoritative TOML configuration."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config


def main() -> None:
    config = load_config(ROOT / "config/langid32.toml")
    count = int(config["jql"]["shard_count"])
    parallel = int(config["jql"]["max_parallel_shards"])
    max_seconds = int(config["jql"]["max_seconds"])
    job_timeout = int(config["jql"]["job_timeout_minutes"])
    work_budget = job_timeout - int(config["jql"]["upload_buffer_minutes"])
    python_version = config["jql"]["python_version"]
    short_retention = int(config["jql"]["short_artifact_retention_days"])
    retention = int(config["execution"]["artifact_retention_days"])
    matrix = {"include": [{"index": i, "file": f"shard-{i:02d}.parquet"} for i in range(count)]}
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        raise SystemExit("GITHUB_OUTPUT is required")
    with open(output, "a", encoding="utf-8") as stream:
        stream.write("matrix=" + json.dumps(matrix, separators=(",", ":")) + chr(10))
        stream.write(f"max_parallel={parallel}" + chr(10))
        stream.write(f"max_seconds={max_seconds}" + chr(10))
        stream.write(f"job_timeout_minutes={job_timeout}" + chr(10))
        stream.write(f"work_budget_minutes={work_budget}" + chr(10))
        stream.write(f"python_version={python_version}" + chr(10))
        stream.write(f"short_retention_days={short_retention}" + chr(10))
        stream.write(f"retention_days={retention}" + chr(10))
    print(json.dumps({"shards": count, "max_parallel": parallel, "max_seconds": max_seconds, "job_timeout_minutes": job_timeout, "work_budget_minutes": work_budget, "python_version": python_version, "short_retention_days": short_retention, "retention_days": retention, "matrix": matrix}))


if __name__ == "__main__":
    main()
