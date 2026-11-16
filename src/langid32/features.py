"""Deterministic UTF-8 byte and hashed character n-gram features."""
from __future__ import annotations

import hashlib
from collections.abc import Iterable

BYTE_PAD = 0
BYTE_CLS = 1
BYTE_OFFSET = 3
BYTE_VOCAB_SIZE = 259


def char_ngram_ids(text: str, buckets: int = 65536,
                   min_n: int = 2, max_n: int = 5) -> list[int]:
    """Hash character n-grams with boundary markers into a fixed vocabulary."""
    if buckets < 1 or min_n < 1 or max_n < min_n:
        raise ValueError("invalid n-gram configuration")
    marked = "^" + text + "$"
    ids: list[int] = []
    for n in range(min_n, max_n + 1):
        for start in range(max(0, len(marked) - n + 1)):
            gram = marked[start:start + n].encode("utf-8")
            digest = hashlib.blake2b(gram, digest_size=8,
                                     person=b"langid32").digest()
            ids.append(int.from_bytes(digest, "little") % buckets)
    return ids


def byte_ids(text: str, max_bytes: int = 256) -> list[int]:
    """Encode UTF-8 bytes; reserve 0 for padding and 1 for CLS."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    raw = text.encode("utf-8")[:max_bytes]
    return [BYTE_CLS] + [b + BYTE_OFFSET for b in raw]


def sparse_rows(rows: Iterable[list[int]], width: int):
    """Build a coalesced COO tensor without requiring SciPy."""
    import torch
    materialized = list(rows)
    indices = []
    values = []
    for row_index, ids in enumerate(materialized):
        counts: dict[int, int] = {}
        for feature_id in ids:
            counts[feature_id] = counts.get(feature_id, 0) + 1
        for feature_id, count in counts.items():
            indices.append((row_index, feature_id))
            values.append(float(count))
    if indices:
        index_tensor = torch.tensor(indices, dtype=torch.long).t().contiguous()
        value_tensor = torch.tensor(values, dtype=torch.float32)
    else:
        index_tensor = torch.empty((2, 0), dtype=torch.long)
        value_tensor = torch.empty((0,), dtype=torch.float32)
    return torch.sparse_coo_tensor(index_tensor, value_tensor,
                                   (len(materialized), width)).coalesce()


def embedding_bag_batch(rows: list[list[int]], device=None):
    """Flatten n-gram IDs and offsets for torch.nn.EmbeddingBag."""
    import torch
    flat: list[int] = []
    offsets: list[int] = []
    for row in rows:
        offsets.append(len(flat))
        flat.extend(row or [0])
    return (torch.tensor(flat, dtype=torch.long, device=device),
            torch.tensor(offsets, dtype=torch.long, device=device))
