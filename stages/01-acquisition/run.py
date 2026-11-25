#!/usr/bin/env python3
"""Dispatch one acquisition target to its own stage-local implementation."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ROOT / "stages" / "01-acquisition" / "targets"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", help="Optional adapter-specific configuration")
    args = parser.parse_args()
    script = TARGETS / f"{args.target}.py"
    if not script.is_file():
        raise SystemExit(f"Unknown acquisition target: {args.target}")
    command = [sys.executable, str(script), "--root", str(Path(args.root).resolve())]
    if args.config:
        command.extend(["--config", args.config])
    subprocess.run(command, check=True)

if __name__ == "__main__":
    main()
