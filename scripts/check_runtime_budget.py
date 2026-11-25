#!/usr/bin/env python3
"""Fail a pipeline stage when the shared run deadline or safety reserve is reached."""
from __future__ import annotations

import argparse
import time


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--started-epoch", type=int, required=True)
    parser.add_argument("--budget-minutes", type=int, required=True)
    parser.add_argument("--safety-margin-minutes", type=int, required=True)
    args = parser.parse_args()
    now = int(time.time())
    elapsed = max(0, now - args.started_epoch)
    budget_seconds = args.budget_minutes * 60
    reserve_seconds = args.safety_margin_minutes * 60
    remaining = budget_seconds - elapsed
    print(f"Workflow elapsed: {elapsed // 60} min; budget remaining: {remaining // 60} min")
    if remaining <= reserve_seconds:
        raise SystemExit(
            f"Global time budget reached with safety reserve: remaining={remaining}s, "
            f"reserve={reserve_seconds}s"
        )


if __name__ == "__main__":
    main()
