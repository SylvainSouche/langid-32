"""Inventory FineWeb2 Parquet shard metadata without downloading Parquet data.

Uses the Hugging Face dataset-viewer /parquet endpoint (or a saved JSON
response) and emits only shard paths, sizes and subset/split metadata.
"""
from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from .fineweb2_inventory import TARGET_SUBSETS

DATASET = "HuggingFaceFW/fineweb-2"
API_BASE = "https://datasets-server.huggingface.co/parquet"


def fetch_listing(dataset: str, timeout: int) -> dict:
    query = urllib.parse.urlencode({"dataset": dataset})
    request = urllib.request.Request(
        f"{API_BASE}?{query}",
        headers={"User-Agent": "langid-32 shard inventory/0.1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Unexpected dataset-viewer response")
    return payload


def load_listing(input_json: Path | None, dataset: str, timeout: int) -> tuple[dict, str]:
    if input_json:
        payload = json.loads(input_json.read_text(encoding="utf-8"))
        return payload, str(input_json)
    return fetch_listing(dataset, timeout), f"{API_BASE}?dataset={dataset}"


def flatten_shards(payload: dict) -> list[dict[str, object]]:
    files = payload.get("parquet_files")
    if not isinstance(files, list):
        raise ValueError("Dataset-viewer response has no parquet_files array")

    subset_to_language = {
        subset: language
        for language, subset in TARGET_SUBSETS.items()
        if subset is not None
    }
    rows = []
    for item in files:
        if not isinstance(item, dict):
            continue
        config = str(item.get("config", ""))
        split = str(item.get("split", ""))
        base_split = split.removeprefix("partial-")
        is_partial = base_split != split
        removed = config.endswith("_removed")
        base_config = config[:-8] if removed else config
        language = subset_to_language.get(base_config)
        if language is None or base_split not in {"train", "test", "validation"}:
            continue
        size = item.get("size")
        if not isinstance(size, int) or size < 0:
            size = 0
        rows.append({
            "language": language,
            "subset": base_config,
            "subset_role": "removed" if removed else "filtered",
            "split": base_split,
            "partial": is_partial,
            "api_split": split,
            "filename": item.get("filename", ""),
            "size_bytes": size,
            "url": item.get("url", ""),
        })
    return rows


def target_failed_conversions(payload: dict) -> list[dict[str, str]]:
    """Return failed dataset-viewer conversions for project target subsets."""
    target_subsets = {subset for subset in TARGET_SUBSETS.values() if subset}
    failures = payload.get("failed", [])
    if not isinstance(failures, list):
        return []
    return sorted(
        (
            {
                "config": str(item.get("config", "")),
                "kind": str(item.get("kind", "")),
            }
            for item in failures
            if isinstance(item, dict) and item.get("config") in target_subsets
        ),
        key=lambda item: item["config"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--input-json", type=Path,
                        help="Use a saved /parquet API response instead of querying the endpoint")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")

    payload, source = load_listing(args.input_json, args.dataset, args.timeout)
    rows = flatten_shards(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "language", "subset", "subset_role", "split", "partial",
        "api_split", "filename", "size_bytes", "url",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = defaultdict(lambda: {"files": 0, "bytes": 0})
    for row in rows:
        key = f'{row["language"]}:{row["subset_role"]}:{row["split"]}'
        summary[key]["files"] += 1
        summary[key]["bytes"] += int(row["size_bytes"])
    print(json.dumps({
        "dataset": args.dataset,
        "source": source,
        "output": str(args.output),
        "target_languages": len(TARGET_SUBSETS),
        "matching_shards": len(rows),
        "languages_with_shards": sorted({str(row["language"]) for row in rows}),
        "target_languages_without_shards": sorted(
            set(TARGET_SUBSETS) - {str(row["language"]) for row in rows}
        ),
        "pending_count": len(payload.get("pending", [])),
        "failed_count": len(payload.get("failed", [])),
        "target_failed_conversions": target_failed_conversions(payload),
        "partial": payload.get("partial"),
        "by_language_role_split": dict(sorted(summary.items())),
        "note": "Shard metadata only; no Parquet data downloaded.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
