#!/usr/bin/env python3
"""Acquire the korean source bucket using the shared bounded-source adapter."""
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("."))
    root = p.parse_args().root
    subprocess.run([sys.executable, "scripts/acquire_waiting_sources.py", "--source", "korean",
                    "--out", str(root / "input/waiting/korean")], check=True)

if __name__ == "__main__":
    main()
