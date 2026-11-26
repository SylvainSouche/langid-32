# JQL assessment and global pruning

## Purpose and limits

JQL-Edu-Heads supplies a relative educational-value signal for ranking candidate sentences. It is not a measure of language correctness, grammaticality, factuality, safety, privacy or copyright status. JQL must not replace language validation, privacy screening or source-rights review.

The accepted project decision is to use JQL as a **global candidate-pool pruning step**, not merely an optional annotation. The complete eligible candidate pool is assessed before any final per-language selection.

## Binding assessment policy

1. Assess **every row** in the post-filter candidate pool. Sampling is forbidden. The assessment manifest must prove exact one-to-one coverage of candidate IDs.
2. Score independently with the Gemma, Mistral and Llama JQL-Edu regression heads. Preserve each judge's raw score.
3. Independently quantile-normalize each judge's scores over the **entire assessment corpus**, with all languages and original sources combined. Use average ranks for ties and map the ranks through the standard-normal inverse CDF.
4. For each record calculate:

   `consensus = mean(gemma_z, mistral_z, llama_z) - 0.5 × population_std(gemma_z, mistral_z, llama_z)`

5. Remove the bottom 25% **globally**, not 25% per language or source. Resolve boundary ties deterministically by consensus ascending, then stable record ID, and prune exactly `floor(0.25 × N)` records.
6. Preserve the three raw scores, three normalized scores, mean, disagreement, consensus, candidate ID, language and original source identity.
7. Report counts before scoring, successfully scored, retained and pruned by language and **original source**, plus missing, duplicate and failed scoring IDs.
8. Capitalization and terminal-punctuation checks are diagnostic flags only; they do not filter records.

The final selection of exactly 30,000 records per language, including source balancing, is a separate decision after privacy review and review of the post-pruning source/language counts. It must not be performed automatically by the JQL workflow.

## Model provenance and reproducibility

- Embedding backbone: `Snowflake/snowflake-arctic-embed-m-v2.0`.
- JQL heads: `JQL-AI/JQL-Edu-Heads`, balanced Gemma, Mistral and Llama checkpoints.
- The architecture currently encoded by the scorer is a 768-dimensional embedding, 1,000-unit hidden layer and ReLU regression head.
- The pipeline must resolve and record immutable repository revisions for both the embedding backbone and head repository, along with checkpoint file hashes, in the run manifest. Floating `main` references are not acceptable for a reproducible production assessment.
- Scores for labels outside the published training/evaluation coverage of the model are exploratory and may be out of domain. In particular, do not interpret Arabic, Japanese, Korean, Chinese, Bokmål or Nynorsk scores as calibrated equivalently to well-covered languages.

**Implementation audit note (2026-11-26):** the scoring script and merge/normalization utility exist, but immutable model revision recording and the complete staged-workflow integration have not yet been verified. Do not treat the scoring workflow as production-ready until those requirements and the pipeline contract checks pass.

## Execution constraints

- Use the configured eight deterministic shards and no more than four concurrent scoring workers as the initial execution shape.
- Keep scoring batches bounded to at most 3,600 seconds. Use a small initial throughput measurement when necessary to estimate safe batch sizes and the number of batches; persist completed ratings and resume without rescoring them.
- The six-hour ceiling is binding. A single unbounded scoring job is not an acceptable implementation.
- Preserve complete coverage across all shards; a partial set of ratings must never be merged or reported as a completed assessment.
- The automated workflow must keep sentence-bearing assessment and result artifacts encrypted at rest. Score-only intermediate files must not contain sentence text.

## Local inference

Local scoring is an alternative execution environment, not a different selection policy. Install a platform-appropriate PyTorch build first, then install the remaining dependencies from `requirements-jql.txt`.

- Apple Silicon: use a PyTorch build with MPS support and `--device mps`.
- Windows/NVIDIA: use a CUDA-enabled PyTorch build matching the installed driver/runtime and `--device cuda`.
- CPU fallback: `--device cpu`.

Any local run must use the same immutable model revisions, full-pool normalization, exact coverage checks, consensus formula and global pruning rule as the automated pipeline.
