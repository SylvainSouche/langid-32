#!/usr/bin/env python3
"""Acquire the approved MaCoCu 2.0 Croatian, Maltese and Slovenian sources."""
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
        "--source", "macocu", "--out",
        str(root / "input/waiting/macocu"),
    ], check=True)


if __name__ == "__main__":
    main()
