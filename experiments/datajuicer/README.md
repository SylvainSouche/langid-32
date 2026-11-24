# Data-Juicer adapter experiment

This is an isolated evaluation; it does not change the production acquisition,
merge or JQL workflows.

## Question being tested

Can Data-Juicer replace generic per-batch text operations while a small Python
adapter retains the langid-32-specific source/language bucket and replenishment
policy?

The prototype runs three built-in operators, in order:

1. `whitespace_normalization_mapper`
2. `text_length_filter`
3. `document_deduplicator` (exact text match)

NFC normalization remains an explicit langid-32 compatibility step. The
adapter performs cross-batch exact deduplication and continues reading batches
until the accepted unique bucket reaches its target or the source is exhausted.
Those are project-specific semantics, not delegated to Data-Juicer.

## Run

Use Python 3.11 in a clean virtual environment:

```sh
python -m pip install "py-data-juicer==1.6.0" pytest
python -m pytest -q experiments/datajuicer
```

The CI experiment installs Data-Juicer independently of the production
environment. It uses synthetic data only: no corpus text or source credentials
are involved.

## Evaluation criteria

- Does the documented Python API run with a small in-memory dataset?
- Does operator ordering produce the expected normalized/filter/deduplicated
  rows?
- Does the adapter keep reading after filtering and duplicates reduce yield?
- Does it stop at the target without reading the rest of the source?
- What are install size, startup cost and runtime on a small CPU runner?

## Current scope and known limits

This first test covers whitespace normalization, character-length filtering,
exact text deduplication and the replenishment feedback loop. It does not yet
cover source-specific readers, global cross-source deduplication, fuzzy
deduplication, licensing/provenance manifests, JQL, or source balancing.
Data-Juicer must not be allowed to rewrite/drop provenance columns silently;
the next evaluation should verify preservation on real source-shaped records.
