# Historical 34,000-row JQL-Edu assessment sample

> **ARCHIVED — superseded by the current pipeline contract.** This document describes an earlier 1,000-per-language (34,000-row) experiment and its manual/local workflow. The current pipeline does not sample 1,000 per language: it scores every post-filter candidate row, flags `ar`, `ja`, `ko`, `zh`, `nb` and `nn` as outside the JQL heads' training-language set, normalizes all three judges over the full combined assessment corpus, and prunes the global bottom 25%. The current workflow and execution rules are in [`docs/pipeline-contract.md`](pipeline-contract.md).

This historical workflow builds a private working sample from the current merged candidate pool. It selects exactly 1,000 sentences for each of the 34 project language labels (34,000 rows total), after the candidate merge's normalization, deduplication, privacy-pattern filtering and active source-exclusion registry.

## Files

- `out/jql-assessment-34k.parquet`: columns `id`, `lang`, `sentence`, `source`, `source-variant`.
- `out/jql-assessment-34k-summary.json`: exact per-language and source/variant counts.
- `scripts/sample_jql_assessment.py`: deterministic source-balanced sample builder.
- `scripts/score_jql_parquet.py`: JQL scorer; output CSV columns are `id`, `language`, `ratings`.

Sampling is deterministic. It balances source families first and source variants within each family, then selects by a SHA-256 rank within each bucket. If any language has fewer than 1,000 eligible rows, the build fails rather than silently producing an undersized file.

## Build the Parquet locally

After the normal candidate build has produced its private `records.jsonl`:

```sh
python -m pip install pyarrow
python scripts/sample_jql_assessment.py \
  --input out/candidate/records.jsonl \
  --output out/jql-assessment-34k.parquet \
  --summary out/jql-assessment-34k-summary.json \
  --per-language 1000
```

## Install JQL

Use Python 3.11 or 3.12 in a clean virtual environment. The embedder is **Snowflake/snowflake-arctic-embed-m-v2.0**. The three balanced heads are downloaded from **JQL-AI/JQL-Edu-Heads** on first run; no Gemma, Mistral or Llama teacher model is downloaded.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch transformers==4.44.2 huggingface_hub pyarrow pandas einops sentencepiece safetensors
```

On Apple Silicon, the regular PyTorch wheel includes MPS support. On Windows/Linux, install the PyTorch build appropriate for the machine; CPU is the safe baseline. No CUDA or GPU is required.

## Run all three JQL-Edu heads

```sh
python scripts/score_jql_parquet.py \
  --input out/jql-assessment-34k.parquet \
  --output out/jql-assessment-34k-ratings.csv \
  --device auto \
  --batch-size 32
```

For a CPU-only run, use `--device cpu`. For a quick test, use `--max-rows 100`.

Each CSV `ratings` cell is a JSON object with three independent raw scores: `gemma`, `mistral`, and `llama`. The heads are the balanced checkpoints. The scores are not collapsed into one average and are not language-identification or factuality scores.

## Interpretation and limits

The model estimates educational value (nominal 0–5), not grammatical correctness, language identity, factuality, privacy, safety or copyright status. The model card lists Norwegian as `no`, not separate `nb` and `nn`; it does not list Arabic, Japanese, Korean or Chinese. Scores for those project labels should be treated as exploratory/out-of-coverage rather than validated ratings. Other languages should also be checked against the model card's training/evaluation coverage.

The Parquet is an **internal assessment sample, not a rights-cleared or publication-ready dataset**. It inherits the mixed rights status and provenance limitations of its source records. Do not publish or redistribute it until each source's release conditions and underlying text rights have been cleared.

## Upstream references

- Embedder: https://huggingface.co/Snowflake/snowflake-arctic-embed-m-v2.0
- Heads: https://huggingface.co/JQL-AI/JQL-Edu-Heads
- Inference implementation: https://github.com/JQL-AI/JQL-Annotation-Pipeline
- Paper: https://arxiv.org/abs/2505.22232

## Historical parallel scoring, boundary checks and consensus ranking

The following describes the archived 34,000-row experiment only. Its manual-dispatch workflow and its text-free final artifact are not the current staged pipeline.

The current hosted workflow is `.github/workflows/score-jql-assessment.yml`. It starts automatically after a successful staged-pipeline run, checks out the exact source-run commit, restores the encrypted full-pool assessment, creates eight streaming shards, and runs four CPU-only workers concurrently. It uses the published bfloat16 inference recipe with pinned Python/PyTorch/Transformers/Hub versions. Each shard's ratings are bound to the source pipeline run, source commit, shard hash, model revisions and checkpoint hashes. A failed scoring run can be resumed by manually dispatching the scoring workflow with the original source run ID and the previous scoring run ID; it rejects ratings from any other source run or model/runtime provenance.

The current pipeline encrypts every text-bearing intermediate and final review artifact before uploading it to the public repository's Actions storage. Plain inter-job rating CSVs and quality flags contain IDs/language/scores or flags, not sentence text. The final encrypted JQL artifact includes the pruned sentence text for the required manual privacy and source-rights review. The encryption key is a repository secret and is never included in an artifact.

### Consensus score

The merge normalizes each judge independently over the **entire assessment corpus, all languages combined**. It converts average ranks to standard-normal quantiles using the inverse normal CDF; tied raw scores receive the same normalized score. This makes each judge's distribution comparable without assuming that the original regression heads share the same calibration.

For each sentence, the merge stores the three raw scores, the three normalized scores, their mean, their population standard deviation (inter-judge disagreement), and:

\[
JQL_{\mathrm{consensus}} =
\operatorname{mean}(z_G,z_M,z_L)
- 0.5 \times \operatorname{std}_{\mathrm{population}}(z_G,z_M,z_L)
\]

The result is a corpus-relative ranking signal, not an absolute quality score. Recompute it whenever the reference assessment corpus changes. Raw ratings are retained and never overwritten.

### Sentence-boundary flags

The separate quality job records:

- `initial_capitalization`: `pass`, `fail` or `not_applicable` (Arabic, Chinese, Japanese and Korean are treated as caseless for this test).
- `terminal_punctuation`: `pass` or `fail`, allowing common Unicode sentence-final marks followed by closing quotation marks or brackets.

These are **flags, not automatic exclusions**. They are intended to identify fragments and likely sentence chunks for review. Punctuation conventions, abbreviations and source-specific formatting still require inspection.

### Run locally

With the assessment Parquet at `out/jql-assessment-34k.parquet`, install `requirements-jql.txt` (plus a platform-appropriate PyTorch build), then run:

```sh
make -j4 jql-pipeline DEVICE=auto
```

Use `DEVICE=mps` on Apple Silicon or `DEVICE=cuda` where CUDA is available. `-j4` runs up to four shard scorers concurrently; reduce it if memory is constrained. The outputs are written under `out/` and can be redirected with the `JQL_*` Make variables.

The original single-file scorer remains available for smoke tests and manual runs. It uses native PyTorch SDPA rather than the embedder's xformers-only attention path.

**Public-repository artifact caution:** `langid-32` is public. GitHub documents that anyone with repository read access can download workflow artifacts ([artifact access documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)). Current text-bearing artifacts are therefore AES-GCM encrypted before upload; their ciphertext and non-sensitive manifests remain downloadable, but sentence text is not exposed without the secret key. Never upload the key or unencrypted text-bearing artifacts. The manual privacy review must be performed on the decrypted local review artifact. This encryption does not clear source rights or authorise redistribution.
