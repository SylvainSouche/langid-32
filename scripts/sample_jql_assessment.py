#!/usr/bin/env python3
"""Build a deterministic, source-balanced JQL assessment sample from candidate records.jsonl."""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
from collections import Counter, defaultdict
from pathlib import Path

LANGUAGES = (
    "bg hr cs da nl en et fi fr de el hu ga it lv lt mt pl pt ro sk sl es sv "
    "nb nn ru ja zh ko ar tr ca is"
).split()


def variant_of(row: dict) -> str:
    p = row.get("provenance") or {}
    return str(
        p.get("source_component")
        or p.get("source_original_name")
        or row.get("source_release")
        or p.get("source_dataset")
        or "unspecified"
    )


def stable_rank(seed: str, row: dict) -> int:
    material = "\0".join((
        seed, str(row["language"]), str(row["source"]),
        variant_of(row), str(row.get("group_id") or ""), str(row["text"]),
    ))
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest(), "big")


def allocate_quotas(counts: Counter, target: int) -> dict[tuple[str, str, str], int]:
    """Equalize source-family shares first, then variants within each family."""
    by_lang_source: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(dict))
    for (lang, source, variant), count in counts.items():
        by_lang_source[lang][source][variant] = count

    quotas = {}
    for lang in LANGUAGES:
        sources = sorted(by_lang_source[lang])
        if not sources:
            raise RuntimeError(f"No candidate records for language {lang}")
        source_take = {source: 0 for source in sources}
        remaining = target
        while remaining:
            progressed = False
            for source in sources:
                available = sum(by_lang_source[lang][source].values())
                if source_take[source] < available:
                    source_take[source] += 1
                    remaining -= 1
                    progressed = True
                    if remaining == 0:
                        break
            if not progressed:
                total = sum(sum(v.values()) for v in by_lang_source[lang].values())
                raise RuntimeError(
                    f"{lang}: only {total} eligible records; {target} required"
                )

        for source in sources:
            variants = sorted(by_lang_source[lang][source])
            take = source_take[source]
            variant_take = {variant: 0 for variant in variants}
            while take:
                progressed = False
                for variant in variants:
                    available = by_lang_source[lang][source][variant]
                    if variant_take[variant] < available:
                        variant_take[variant] += 1
                        take -= 1
                        progressed = True
                        if take == 0:
                            break
                if not progressed:
                    raise RuntimeError(f"Quota allocation failed for {lang}/{source}")
            for variant, quota in variant_take.items():
                quotas[(lang, source, variant)] = quota
    return quotas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True, help="Private candidate records.jsonl")
    ap.add_argument("--output", type=Path, required=True, help="Output Parquet file")
    ap.add_argument("--summary", type=Path, help="Optional JSON summary")
    ap.add_argument("--per-language", type=int, default=1000)
    ap.add_argument("--seed", default="langid-32-jql-assessment-2026-11-19")
    args = ap.parse_args()

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("Install pyarrow: python -m pip install pyarrow") from exc

    if not args.input.is_file():
        raise SystemExit(f"Input not found: {args.input}")

    counts = Counter()
    with args.input.open("r", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            lang = str(row.get("language", "")).lower()
            if lang not in LANGUAGES:
                continue
            text = str(row.get("text") or "").strip()
            source = str(row.get("source") or "").strip()
            if not text or not source:
                continue
            counts[(lang, source, variant_of(row))] += 1

    quotas = allocate_quotas(counts, args.per_language)
    heaps = {key: [] for key, quota in quotas.items() if quota}
    serial = 0
    with args.input.open("r", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            lang = str(row.get("language", "")).lower()
            if lang not in LANGUAGES:
                continue
            sentence = str(row.get("text") or "").strip()
            source = str(row.get("source") or "").strip()
            if not sentence or not source:
                continue
            variant = variant_of(row)
            key = (lang, source, variant)
            quota = quotas.get(key, 0)
            if not quota:
                continue
            rank = stable_rank(args.seed, row)
            heap = heaps[key]
            serial += 1
            entry = (-rank, -serial, row)
            if len(heap) < quota:
                heapq.heappush(heap, entry)
            elif rank < -heap[0][0]:
                heapq.heapreplace(heap, entry)

    output_rows = []
    source_counts = Counter()
    variant_counts = Counter()
    for key, quota in quotas.items():
        selected = heaps.get(key, [])
        if len(selected) != quota:
            raise RuntimeError(f"Selected {len(selected)} of {quota} for bucket {key}")
        lang, source, variant = key
        for _, _, row in selected:
            sentence = " ".join(str(row["text"]).split())
            identity = "\0".join((lang, source, variant,
                                    str(row.get("group_id") or ""), sentence))
            row_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
            output_rows.append({
                "id": row_id,
                "lang": lang,
                "sentence": sentence,
                "source": source,
                "source-variant": variant,
            })
            source_counts[f"{lang}:{source}"] += 1
            variant_counts[f"{lang}:{source}:{variant}"] += 1

    output_rows.sort(key=lambda x: (x["lang"], x["source"], x["source-variant"], x["id"]))
    if len(output_rows) != len(LANGUAGES) * args.per_language:
        raise RuntimeError(f"Expected {len(LANGUAGES) * args.per_language} rows, got {len(output_rows)}")

    table = pa.Table.from_pylist(output_rows, schema=pa.schema([
        ("id", pa.string()),
        ("lang", pa.string()),
        ("sentence", pa.string()),
        ("source", pa.string()),
        ("source-variant", pa.string()),
    ]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, args.output, compression="zstd", use_dictionary=True)

    summary = {
        "status": "internal_assessment_sample_not_rights_cleared",
        "input": str(args.input),
        "output": str(args.output),
        "rows": len(output_rows),
        "per_language": args.per_language,
        "languages": LANGUAGES,
        "language_counts": {lang: sum(1 for row in output_rows if row["lang"] == lang)
                            for lang in LANGUAGES},
        "source_counts": dict(sorted(source_counts.items())),
        "source_variant_counts": dict(sorted(variant_counts.items())),
        "sampling": "deterministic; equalized source-family shares, then source variants; hash-ranked within each bucket",
        "seed": args.seed,
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
