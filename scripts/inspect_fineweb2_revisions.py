#!/usr/bin/env python3
"""Inspect FineWeb2 shard paths in pinned Hugging Face dataset revisions.

Uses only the Hugging Face Hub tree API; it does not download Parquet data.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DATASET = "HuggingFaceFW/fineweb-2"
REVISIONS = ("v2.0.0", "v2.0.1", "v2.1.0", "v2.1.1", "main")
SUBSETS = ("spa_Latn", "tur_Latn")
SPLITS = ("train", "test")


def request_json(url: str, timeout: int, retries: int = 4) -> tuple[object, dict[str, str]]:
    headers = {
        "User-Agent": "langid-32 FineWeb2 revision inventory/0.1",
        "Accept": "application/json",
    }
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                response_headers = {k.lower(): v for k, v in response.headers.items()}
                return payload, response_headers
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:1000]
            if exc.code in (404, 410):
                return {"_not_found": exc.code, "_message": body or str(exc)}, {}
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                raise RuntimeError(f"HTTP {exc.code}: {body or exc.reason}") from exc
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
        time.sleep(min(2 ** attempt, 8))
    raise RuntimeError("unreachable retry state")


def next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        bits = part.split(";")
        if len(bits) < 2 or 'rel="next"' not in bits[1]:
            continue
        target = bits[0].strip()
        if target.startswith("<") and target.endswith(">"):
            return target[1:-1]
    return None


def list_tree(revision: str, path: str, timeout: int) -> tuple[list[dict], str | None]:
    url = (
        f"https://huggingface.co/api/datasets/{DATASET}/tree/"
        f"{urllib.parse.quote(revision, safe='')}/{path}"
        "?recursive=true&expand=false&limit=1000"
    )
    entries: list[dict] = []
    while url:
        payload, headers = request_json(url, timeout)
        if isinstance(payload, dict) and "_not_found" in payload:
            return [], f"HTTP {payload['_not_found']} for {path}"
        if not isinstance(payload, list):
            return entries, f"Unexpected API response for {path}: {type(payload).__name__}"
        entries.extend(item for item in payload if isinstance(item, dict))
        url = next_link(headers.get("link", ""))
    return entries, None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    checks: list[dict] = []
    for revision in REVISIONS:
        for subset in SUBSETS:
            for split in SPLITS:
                path = f"data/{subset}/{split}"
                try:
                    entries, error = list_tree(revision, path, args.timeout)
                except Exception as exc:  # preserve partial inventory and report transport/API failures
                    entries, error = [], f"{type(exc).__name__}: {exc}"
                files = [e for e in entries if e.get("type") == "file" or "size" in e]
                total_bytes = sum(int(e.get("size") or 0) for e in files)
                check = {
                    "revision": revision,
                    "subset": subset,
                    "split": split,
                    "path": path,
                    "entry_count": len(entries),
                    "file_count": len(files),
                    "total_bytes": total_bytes,
                    "error": error,
                }
                checks.append(check)
                for item in files:
                    lfs = item.get("lfs") or {}
                    rows.append({
                        "revision": revision,
                        "subset": subset,
                        "split": split,
                        "path": item.get("path", ""),
                        "size_bytes": item.get("size", ""),
                        "oid": item.get("oid", ""),
                        "lfs_oid": lfs.get("oid", "") if isinstance(lfs, dict) else "",
                        "lfs_size": lfs.get("size", "") if isinstance(lfs, dict) else "",
                    })
                print(json.dumps(check, ensure_ascii=False), flush=True)

    payload = {
        "dataset": DATASET,
        "revisions": list(REVISIONS),
        "subsets": list(SUBSETS),
        "method": "Hugging Face Hub tree API; metadata only, no Parquet download",
        "checks": checks,
        "files": rows,
    }
    (args.output_dir / "inventory.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (args.output_dir / "shards.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["revision", "subset", "split", "path", "size_bytes", "oid", "lfs_oid", "lfs_size"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
