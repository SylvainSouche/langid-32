#!/usr/bin/env python3
"""Validate the four explicitly approved, immutable historical source snapshots."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config

SNAPSHOTS = {
    "v5": {
        "run_id": 43950037392,
        "artifact_id": 14266897039,
        "artifact_name": "multisource-candidate-v5-fineweb-en",
        "expires_at": "2026-11-30T20:30:01Z",
        "filename": "records.jsonl",
    },
    "leipzig": {
        "run_id": 44361364340,
        "artifact_id": 14454427333,
        "artifact_name": "leipzig-balanced-34-44361364340",
        "expires_at": "2026-12-18T17:46:23Z",
        "filename": "leipzig-candidates.jsonl",
    },
    "tatoeba": {
        "run_id": 44121162591,
        "artifact_id": 14345216923,
        "artifact_name": "tatoeba-cc0-staged-weekly-2026-11-14",
        "expires_at": "2026-12-01T16:03:33Z",
        "filename": "tatoeba-cc0-staged.jsonl",
    },
    "dgt": {
        "run_id": 44291075180,
        "artifact_id": 14421763101,
        "artifact_name": "dgt-tm-2021-staged-5k",
        "expires_at": "2026-12-02T11:07:30Z",
        "filename": "dgt-tm-2021-staged.jsonl",
    },
}
REQUIRED_FIELDS = (
    "text", "language", "source", "source_release",
    "group_id", "licence_id", "text_origin", "provenance",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_snapshot(root: Path, filename: str, languages: set[str]) -> dict:
    matches = sorted(root.rglob(filename))
    if len(matches) != 1:
        raise SystemExit(
            f"Expected exactly one {filename} under {root}, found {len(matches)}"
        )
    path = matches[0]
    language_counts = Counter()
    source_counts = Counter()
    rows = 0
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            missing = [key for key in REQUIRED_FIELDS if not row.get(key)]
            if missing:
                raise SystemExit(f"{path}:{line_number}: missing required fields {missing}")
            language = str(row["language"]).lower()
            if language not in languages:
                raise SystemExit(
                    f"{path}:{line_number}: unexpected language label {language!r}"
                )
            if not isinstance(row["provenance"], dict):
                raise SystemExit(f"{path}:{line_number}: provenance must be an object")
            if not str(row["text"]).strip():
                raise SystemExit(f"{path}:{line_number}: empty sentence text")
            original_source = str(
                row["provenance"].get("source_original_name") or row["source"]
            )
            language_counts[language] += 1
            source_counts[f"{original_source}:{language}"] += 1
            rows += 1
    if rows == 0:
        raise SystemExit(f"Historical snapshot is empty: {path}")
    return {
        "path": str(path.relative_to(root)),
        "sha256": sha256_file(path),
        "rows": rows,
        "language_counts": dict(sorted(language_counts.items())),
        "original_source_language_counts": dict(sorted(source_counts.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    languages = set(cfg["project"]["languages"])
    manifest = {
        "schema_version": 1,
        "kind": "approved_historical_source_snapshots",
        "snapshots": {},
    }
    for name, metadata in SNAPSHOTS.items():
        directory = args.root / "input" / name
        if not directory.is_dir():
            raise SystemExit(f"Missing historical snapshot directory: {directory}")
        validated = validate_snapshot(directory, metadata["filename"], languages)
        manifest["snapshots"][name] = {**metadata, **validated}
    output = args.root / "input" / "historical-manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
