#!/usr/bin/env python3
"""Acquire the approved ParlaMint 4.0 Icelandic and Slovenian sources."""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args().root
    subprocess.run([
        sys.executable, "scripts/acquire_waiting_sources.py",
        "--source", "parlamint", "--out",
        str(root / "input/waiting/parlamint"),
    ], check=True)


if __name__ == "__main__":
    main()
