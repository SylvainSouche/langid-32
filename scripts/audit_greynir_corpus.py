#!/usr/bin/env python3
"""Count GreynirCorpus treebank records in pinned Git-LFS files."""
from __future__ import annotations
import gzip, hashlib, json
from pathlib import Path

REVISION = "deb60c4b2775a4e0c709a6890c28678b913f44aa"
ROOT = Path(".")
OUT = Path("reports/greynir-corpus-audit.json")
MARKER = b"( (META"

def count_gzip(path: Path, kind: str) -> dict:
    digest = hashlib.sha256()
    compressed_bytes = 0
    with path.open("rb") as raw:
        prefix = raw.read(200)
        if prefix.startswith(b"version https://git-lfs.github.com/spec"):
            raise RuntimeError(f"{path} is still an LFS pointer; checkout must fetch LFS objects")
        digest.update(prefix)
        compressed_bytes += len(prefix)
        for chunk in iter(lambda: raw.read(1024 * 1024), b""):
            digest.update(chunk)
            compressed_bytes += len(chunk)
    records = decompressed_bytes = 0
    overlap = b""
    with gzip.open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            decompressed_bytes += len(chunk)
            data = overlap + chunk
            records += data.count(MARKER)
            overlap = data[-(len(MARKER)-1):]
    return {
        "path": str(path), "kind": kind, "compressed_bytes": compressed_bytes,
        "sha256_compressed": digest.hexdigest(),
        "decompressed_bytes": decompressed_bytes,
        "tree_records_marker_count": records,
    }

def count_plain(path: Path, kind: str) -> dict:
    data = path.read_bytes()
    if data.startswith(b"version https://git-lfs.github.com/spec"):
        raise RuntimeError(f"{path} is still an LFS pointer")
    return {
        "path": str(path), "kind": kind, "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "tree_records_marker_count": data.count(MARKER),
    }

def main() -> None:
    files = []
    for path in sorted((ROOT / "psd/copper").glob("*.gz")):
        files.append(count_gzip(path, "copper"))
    for path in sorted((ROOT / "psd/silver").glob("*.gz")):
        files.append(count_gzip(path, "silver"))
    for path in sorted((ROOT / "extra").glob("*.gz")):
        files.append(count_gzip(path, "extra"))
    gold = []
    for directory in ("devset/psd", "testset/psd"):
        for path in sorted((ROOT / directory).glob("*.gld")):
            gold.append(count_plain(path, directory))
    totals = {}
    for kind in ("copper", "silver", "extra"):
        subset = [x for x in files if x["kind"] == kind]
        totals[kind] = {
            "files": len(subset),
            "tree_records_marker_count": sum(x["tree_records_marker_count"] for x in subset),
            "compressed_bytes": sum(x["compressed_bytes"] for x in subset),
            "decompressed_bytes": sum(x["decompressed_bytes"] for x in subset),
        }
    totals["gold"] = {
        "files": len(gold),
        "dev_records": sum(x["tree_records_marker_count"] for x in gold if x["kind"] == "devset/psd"),
        "test_records": sum(x["tree_records_marker_count"] for x in gold if x["kind"] == "testset/psd"),
    }
    report = {
        "repository": "mideind/GreynirCorpus",
        "revision": REVISION,
        "method": "Count occurrences of the tree-record opener ( (META in every decompressed gzip/plain treebank file; verify all LFS pointers were hydrated.",
        "files": files + gold,
        "totals": totals,
        "warning": "Copper/silver/extra are separate corpus partitions with possible overlap; do not sum them as unique sentences without text-level cross-partition deduplication."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if any(x["tree_records_marker_count"] == 0 for x in files):
        raise SystemExit("A corpus file contained zero tree markers")

if __name__ == "__main__":
    main()
