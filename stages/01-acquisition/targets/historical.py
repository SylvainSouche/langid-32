#!/usr/bin/env python3
"""Validate the immutable historical snapshots downloaded by the workflow."""
import argparse
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("."))
    root = p.parse_args().root
    expected = ("v5", "leipzig", "tatoeba", "dgt")
    missing = [name for name in expected if not (root / "input" / name).exists()]
    empty = [name for name in expected if (root / "input" / name).exists()
             and not any(x.is_file() for x in (root / "input" / name).rglob("*"))]
    if missing or empty:
        raise SystemExit(f"Historical snapshot validation failed; missing={missing}, empty={empty}")
    print("Historical snapshots validated:", ", ".join(expected))

if __name__ == "__main__":
    main()
