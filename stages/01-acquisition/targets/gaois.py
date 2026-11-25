#!/usr/bin/env python3
"""Acquire the bounded Irish legislation candidate sample."""
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("."))
    root = p.parse_args().root
    subprocess.run([sys.executable, "scripts/acquire_gaois_irish_legislation.py",
                    "--out", str(root / "input/waiting/irish/candidates.jsonl")], check=True)

if __name__ == "__main__":
    main()
