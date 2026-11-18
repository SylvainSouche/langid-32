"""Three comparable language-ID model families; class count is configurable."""
from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class SparseNgramLogReg(nn.Module):
    """A1: hashed character n-gram counts followed by a linear classifier."""
    def __init__(self, buckets: int = 65536, classes: int = 34):
        super().__init__()
        self.weight = nn.Parameter(torch.empty(classes, buckets))
        self.bias = nn.Parameter(torch.zeros(classes))
        nn.init.xavier_uniform_(self.weight)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        if features.layout == torch.sparse_coo:
            return torch.sparse.mm(features, self.weight.t()) + self.bias
        return F.linear(features, self.weight, self.bias)


class CharEmbeddingBag(nn.Module):
    """A2: mean-pooled hashed character n-gram embeddings + linear head."""
    def __init__(self, buckets: int = 32768, dimension: int = 32,
                 classes: int = 34):
        super().__init__()
        self.embedding = nn.EmbeddingBag(buckets, dimension, mode="mean")
        self.classifier = nn.Linear(dimension, classes)

    def forward(self, token_ids: torch.Tensor,
                offsets: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.embedding(token_ids, offsets))


class TransformerBlock(nn.Module):
    def __init__(self, dimension: int = 128, heads: int = 4,
                 ff_dimension: int = 384, dropout: float = 0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(dimension)
        self.attention = nn.MultiheadAttention(
            dimension, heads, dropout=dropout, batch_first=True
        )
        self.norm2 = nn.LayerNorm(dimension)
        self.ff = nn.Sequential(
            nn.Linear(dimension, ff_dimension),
            nn.GELU(),
            nn.Linear(ff_dimension, dimension),
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, padding_mask: torch.Tensor) -> torch.Tensor:
        normalized = self.norm1(x)
        attended, _ = self.attention(
            normalized, normalized, normalized,
            key_padding_mask=padding_mask, need_weights=False
        )
        x = x + self.dropout(attended)
        return x + self.dropout(self.ff(self.norm2(x)))


class ByteTransformer(nn.Module):
    """B: compact bidirectional byte Transformer with a CLS classifier."""
    def __init__(self, max_bytes: int = 256, dimension: int = 128,
                 layers: int = 4, heads: int = 4, ff_dimension: int = 384,
                 classes: int = 34, dropout: float = 0.1):
        super().__init__()
        self.max_bytes = max_bytes
        self.byte_embedding = nn.Embedding(259, dimension, padding_idx=0)
        self.position_embedding = nn.Embedding(max_bytes + 1, dimension)
        self.blocks = nn.ModuleList([
            TransformerBlock(dimension, heads, ff_dimension, dropout)
            for _ in range(layers)
        ])
        self.final_norm = nn.LayerNorm(dimension)
        self.classifier = nn.Linear(dimension, classes)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        _, length = input_ids.shape
        if length > self.max_bytes + 1:
            raise ValueError("sequence exceeds configured max_bytes")
        positions = torch.arange(length, device=input_ids.device).unsqueeze(0)
        x = self.byte_embedding(input_ids) + self.position_embedding(positions)
        padding_mask = input_ids.eq(0)
        for block in self.blocks:
            x = block(x, padding_mask)
        return self.classifier(self.final_norm(x[:, 0]))


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters()
               if parameter.requires_grad)
