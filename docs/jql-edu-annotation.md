# JQL-Edu-Heads annotation batches

## Purpose and non-use

JQL-Edu-Heads is an optional QA annotation, not a corpus-selection signal. The scorer adds three educational-value regression scores (Gemma, Mistral and Llama heads), their mean and their range to each JSONL row. It preserves every input row. Scores must never exclude, down-rank, replace, reorder or otherwise alter the production corpus.

The score is an estimate of educational value, not a measure of language correctness, grammaticality, factuality, safety or copyright status. Do not use it as a language-label validator.

## Model provenance

- Heads: `JQL-AI/JQL-Edu-Heads`, balanced checkpoints for Gemma, Mistral and Llama.
- Embedding backbone: `Snowflake/snowflake-arctic-embed-m-v2.0`.
- The runner records resolved Hugging Face commit revisions for both repositories in every annotated row and in `jql_run_summary.json`.
- The three raw scores are retained independently. The mean and range are descriptive only.
- The implementation follows the public JQL annotation pipeline's CLS embedding and three regression-head design. It uses a small direct inference runner rather than installing the full Datatrove pipeline.

## One-hour resumable batches

`scripts/rate_jql_edu.py` defaults to a 3,600-second scoring window. Model loading happens before the timer starts, so the reported hour measures inference rather than initial model downloads. It writes and fsyncs each completed batch. If a run stops at its time limit, run it again with the same input and output paths: already annotated rows are skipped using a stable key. The output is append-only JSONL and keeps the original text and provenance.

Example:

```sh
python scripts/rate_jql_edu.py \
  --input out/leipzig/leipzig-candidates.jsonl \
  --output out/jql/leipzig-jql.jsonl \
  --max-seconds 3600 \
  --batch-size 128
```

Use a CUDA-capable machine for throughput measurements. The runner falls back to CPU, but CPU and GPU rates must not be compared as if they were equivalent. The first pilot is restricted to Croatian and Icelandic to check behavior on two of the least-resourced project labels before scaling to the full 34-label set. It acquires the same Leipzig news/Wikipedia quota and applies the existing news-only Unicode decimal-digit filter.

## Interpreting the first pilot

Report:
- number rated in the one-hour inference window;
- rows/hour, effective batch size and hardware;
- throughput by language and source;
- score distributions for each head, plus mean and inter-head range;
- errors, skipped rows and remaining backlog.

Do not set a score threshold or discard low-scoring records. Inspect examples across the score distribution manually, and check whether score distributions differ systematically by language or source before deciding whether the annotation is useful.
