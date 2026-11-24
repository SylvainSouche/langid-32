#!/usr/bin/env python3
"""Acquire one FineWeb-2 language configuration as an independent batch."""
import argparse
import subprocess
import sys
from pathlib import Path

CONFIGS = {
    "cat_Latn", "isl_Latn", "nob_Latn", "nno_Latn", "arb_Arab",
    "hrv_Latn", "fin_Latn", "ell_Grek", "mlt_Latn", "slv_Latn",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--config", required=True, choices=sorted(CONFIGS))
    args = parser.parse_args()
    root = args.root.resolve()
    subprocess.run([
        sys.executable, "scripts/acquire_waiting_sources.py",
        "--source", "fineweb2", "--fineweb2-config", args.config,
        "--out", str(root / "input/waiting/fineweb2" / args.config),
    ], check=True)


if __name__ == "__main__":
    main()
