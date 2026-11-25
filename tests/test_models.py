import pytest

torch = pytest.importorskip("torch")

from langid32.features import byte_ids, char_ngram_ids
from langid32.models import (ByteTransformer, CharEmbeddingBag,
                             SparseNgramLogReg, parameter_count)


def test_feature_encoders_are_deterministic_and_utf8_safe():
    assert char_ngram_ids("été") == char_ngram_ids("été")
    encoded = byte_ids("é", max_bytes=8)
    assert encoded[0] == 1
    assert len(encoded) == 3


def test_sparse_logreg_forward():
    model = SparseNgramLogReg(buckets=64, classes=3)
    x = torch.sparse_coo_tensor(
        torch.tensor([[0, 1], [2, 4]]),
        torch.tensor([1.0, 2.0]), (2, 64)
    ).coalesce()
    assert model(x).shape == (2, 3)
    assert parameter_count(model) == 64 * 3 + 3


def test_embedding_bag_forward():
    model = CharEmbeddingBag(buckets=64, dimension=8, classes=3)
    ids = torch.tensor([1, 2, 3, 4])
    offsets = torch.tensor([0, 2])
    assert model(ids, offsets).shape == (2, 3)


def test_byte_transformer_forward_and_parameter_count():
    model = ByteTransformer(max_bytes=16, dimension=32, layers=2,
                            heads=4, ff_dimension=64, classes=3, dropout=0)
    x = torch.tensor([[1, 70, 71, 0], [1, 80, 0, 0]])
    assert model(x).shape == (2, 3)
    assert parameter_count(model) > 0


def test_sparse_rows_builds_dense_count_features():
    from langid32.features import sparse_rows
    dense = sparse_rows([[1, 1, 3], [2]], 8).to_dense()
    assert dense.tolist() == [
        [0.0, 2.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    ]


def test_default_model_parameter_counts_match_design():
    assert parameter_count(SparseNgramLogReg()) == 2_228_258
    assert parameter_count(CharEmbeddingBag()) == 1_049_698
    assert parameter_count(ByteTransformer()) == 732_194
