"""Small Data-Juicer adapter and source-bucket replenishment experiment.

Data-Juicer owns generic text transforms. This module deliberately retains
langid-32's source/language accounting and feedback loop outside the engine.
"""
from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any


@dataclass
class IntakeResult:
    rows: list[dict[str, Any]]
    scanned: int
    rejected_by_engine: int
    duplicates_across_batches: int
    exhausted: bool


def _data_juicer_batch(
    rows: list[dict[str, Any]], *, min_chars: int, max_chars: int
) -> tuple[list[dict[str, Any]], int]:
    """Run the generic normalization, length-filter and exact-dedup operators."""
    from data_juicer.core.data import NestedDataset
    from data_juicer.ops.deduplicator import DocumentDeduplicator
    from data_juicer.ops.filter import TextLengthFilter
    from data_juicer.ops.mapper import WhitespaceNormalizationMapper

    # langid-32's NFC rule is intentionally kept explicit; DJ's mapper handles
    # whitespace normalization. Preserve all non-text provenance columns.
    normalized = [
        {**row, "text": unicodedata.normalize("NFC", str(row.get("text", "")))}
        for row in rows
    ]
    dataset = NestedDataset.from_dict({
        key: [row.get(key) for row in normalized]
        for key in normalized[0]
    }) if normalized else NestedDataset.from_dict({"text": []})

    before = len(dataset)
    dataset = WhitespaceNormalizationMapper().run(dataset=dataset)
    dataset = TextLengthFilter(min_len=min_chars, max_len=max_chars).run(dataset=dataset)
    after_filter = len(dataset)
    dataset = DocumentDeduplicator().run(dataset=dataset)
    return [dict(row) for row in dataset], before - after_filter


def replenish_source_bucket(
    source_rows: Iterable[dict[str, Any]],
    *,
    language: str,
    source: str,
    target: int,
    batch_size: int = 256,
    min_chars: int = 12,
    max_chars: int = 500,
) -> IntakeResult:
    """Read until the accepted unique bucket reaches target or the source ends.

    The caller supplies a source iterator (which may itself stream a remote
    dataset). Deduplication is language-scoped and spans batch boundaries.
    """
    if target < 0 or batch_size < 1:
        raise ValueError("target must be >= 0 and batch_size must be >= 1")

    iterator: Iterator[dict[str, Any]] = iter(source_rows)
    retained: list[dict[str, Any]] = []
    seen: set[str] = set()
    scanned = rejected = cross_batch_duplicates = 0
    exhausted = False

    while len(retained) < target:
        batch: list[dict[str, Any]] = []
        for _ in range(batch_size):
            try:
                row = next(iterator)
            except StopIteration:
                exhausted = True
                break
            scanned += 1
            batch.append(row)
        if not batch:
            break

        processed, rejected_now = _data_juicer_batch(
            batch, min_chars=min_chars, max_chars=max_chars
        )
        rejected += rejected_now
        for row in processed:
            text = str(row.get("text", ""))
            if text in seen:
                cross_batch_duplicates += 1
                continue
            seen.add(text)
            retained.append({
                **row,
                "language": language,
                "source": source,
            })
            if len(retained) >= target:
                break

    return IntakeResult(
        rows=retained,
        scanned=scanned,
        rejected_by_engine=rejected,
        duplicates_across_batches=cross_batch_duplicates,
        exhausted=exhausted,
    )
