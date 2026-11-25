#!/usr/bin/env python3
"""Build a deterministic, source-balanced JQL assessment sample from candidate records.jsonl."""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config

LANGUAGES = tuple(load_config()["project"]["languages"])
