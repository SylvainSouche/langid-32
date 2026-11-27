#!/usr/bin/env python3
"""Verify the complete pinned Greynir Copper 01 partition without exposing text."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from src.langid32.greynir import LFS_POINTERS, PARTITION_FILES, iter_sentences


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_greynir_runtime.py PATH_TO_COPPER01_GZ")

    path = Path(sys.argv[1])
    expected_sha256, expected_size = LFS_POINTERS[PARTITION_FILES["copper"]]
    actual_size = path.stat().st_size
    if actual_size != expected_size:
        raise RuntimeError(
            f"Greynir LFS size mismatch: expected {expected_size}, got {actual_size}"
        )

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_sha256 = digest.hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            f"Greynir LFS SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )

    sentence_count = 0
    last_emitted_record = 0
    for row in iter_sentences(path, "copper"):
        sentence_count += 1
        last_emitted_record = row["provenance"]["source_record_number"]

    if sentence_count == 0:
        raise RuntimeError("Greynir Copper 01 produced no sentence rows")

    print(f"Verified source bytes: {actual_size}")
    print(f"Verified source SHA-256: {actual_sha256}")
    print(f"Parsed sentence rows: {sentence_count}")
    print(f"Last emitted source record: {last_emitted_record}")
    print("PASS: iter_sentences consumed Copper 01 to EOF without a parser error")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
