# 34,000-row JQL-Edu assessment sample

This workflow builds a private working sample from the current merged candidate pool. It selects exactly 1,000 sentences for each of the 34 project language labels (34,000 rows total), after the candidate merge's normalization, deduplication, privacy-pattern filtering and active source-exclusion registry.

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
