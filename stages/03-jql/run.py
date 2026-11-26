#!/usr/bin/env python3
"""Build the complete, unsampled JQL assessment Parquet from the candidate pool."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config


def main() -> None:
    config_path = ROOT / "config/langid32.toml"
    config = load_config(config_path)
    batch_size = int(config["jql"]["assessment_batch_size"])
    subprocess.run([
        sys.executable,
        "scripts/sample_jql_assessment.py",
        "--input", "out/candidate/records.jsonl",
        "--output", "out/jql-assessment-full.parquet",
        "--summary", "out/jql-assessment-full-summary.json",
        "--batch-size", str(batch_size),
        "--config", str(config_path),
        "--all",
    ], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
