#!/usr/bin/env python3
"""Acquire one FineWeb-2 language configuration as an independent batch."""
import argparse
import subprocess
import sys
from pathlib import Path

CONFIGS = {
    "bul_Cyrl", "hrv_Latn", "cat_Latn", "ces_Latn", "dan_Latn",
    "nld_Latn", "ekk_Latn", "fin_Latn", "fra_Latn", "deu_Latn",
    "ell_Grek", "hun_Latn", "gle_Latn", "ita_Latn", "lvs_Latn",
    "lit_Latn", "mlt_Latn", "pol_Latn", "por_Latn", "ron_Latn",
    "slk_Latn", "slv_Latn", "spa_Latn", "swe_Latn", "nob_Latn",
    "nno_Latn", "isl_Latn", "rus_Cyrl", "jpn_Jpan", "cmn_Hani", "kor_Hang",
    "arb_Arab", "tur_Latn",
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
