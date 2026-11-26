#!/usr/bin/env python3
"""Download text-only Common Voice and curate bounded candidates."""
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("."))
    root = p.parse_args().root
    source = root / "input/common-voice/source"
    output = root / "input/common-voice"
    subprocess.run([sys.executable, "scripts/download_common_voice_hf.py", "--output-dir", str(source)], check=True)
    subprocess.run([sys.executable, "scripts/curate_common_voice_hf.py", "--input-root", str(source),
                    "--output", str(output)], check=True)

if __name__ == "__main__":
    main()
