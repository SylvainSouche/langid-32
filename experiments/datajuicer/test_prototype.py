from experiments.datajuicer.prototype import replenish_source_bucket


def test_replenishes_until_target_across_batches_and_deduplicates_globally():
    rows = [
        {"text": "too short"},
        {"text": "  A sufficiently long sentence from source alpha.  "},
        {"text": "A sufficiently long sentence from source alpha."},
        {"text": "A second sufficiently long sentence from source alpha."},
        {"text": "A third sufficiently long sentence from source alpha."},
        {"text": "x" * 120},
        {"text": "A fourth sufficiently long sentence from source alpha."},
    ]

    result = replenish_source_bucket(
        iter(rows),
        language="en",
        source="synthetic-source",
        target=3,
        batch_size=2,
        min_chars=20,
        max_chars=100,
    )

    assert [row["text"] for row in result.rows] == [
        "A sufficiently long sentence from source alpha.",
        "A second sufficiently long sentence from source alpha.",
        "A third sufficiently long sentence from source alpha.",
    ]
    assert result.scanned == 6
    assert result.rejected_by_engine == 2
    assert result.duplicates_across_batches == 0
    assert all(row["language"] == "en" for row in result.rows)
    assert all(row["source"] == "synthetic-source" for row in result.rows)


def test_source_exhaustion_returns_short_bucket():
    result = replenish_source_bucket(
        [{"text": "Only one sufficiently long sentence."}],
        language="fr",
        source="small-source",
        target=5,
        batch_size=2,
        min_chars=10,
        max_chars=100,
    )
    assert len(result.rows) == 1
    assert result.scanned == 1
    assert result.exhausted is True
