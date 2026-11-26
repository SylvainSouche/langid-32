#!/usr/bin/env python3
"""Fail-closed guard for the deferred final 30,000-per-language selection.

The JQL pipeline ends at the globally pruned candidate pool. Final selection is
a separate human decision and must not be automated before explicit approval
and a separately reviewed implementation of the final source-mix contract.
"""
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consensus", required=False)
    parser.add_argument("--baseline-manifest", required=False)
    parser.add_argument("--output-dir", required=False)
    parser.parse_args()
    raise SystemExit(
        "FINAL SELECTION DISABLED BY CONTRACT: the automated pipeline stops "
        "after global bottom-25% JQL pruning. Do not select 30,000 records per "
        "language until the user explicitly approves that separate step and "
        "its source-mix implementation is reviewed."
    )


if __name__ == "__main__":
    main()
