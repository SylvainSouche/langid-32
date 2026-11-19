# JQL-Edu-Heads annotation

## Purpose and non-use

JQL-Edu-Heads is an optional QA annotation, not a corpus-selection signal. The scorer adds three educational-value regression scores (Gemma, Mistral and Llama heads), their mean and their range to each JSONL row. It preserves every input row. Scores must never exclude, down-rank, replace, reorder or otherwise alter the production corpus.

The score estimates educational value. It is not a measure of language correctness, grammaticality, factuality, safety, privacy or copyright status. Do not use it as a language-label validator.

The model card lists training/evaluation language coverage for many, but not all, project labels. Arabic, Japanese, Korean and Chinese are not in its published language list. Treat those scores as exploratory and potentially out-of-domain; do not compare them as if calibrated equivalently to supported languages.

## Model provenance

- Heads: `JQL-AI/JQL-Edu-Heads`, balanced checkpoints for Gemma, Mistral and Llama.
- Embedding backbone: `Snowflake/snowflake-arctic-embed-m-v2.0`.
- The runner records resolved Hugging Face commit revisions for both repositories in every annotated row and in `jql_run_summary.json`.
- Three raw scores are retained independently. The mean and inter-head range are descriptive only.
- The implementation follows the public model card architecture: 768-dimensional embedding, 1,000-unit hidden layer and ReLU regression head.

## Local hardware

Inference is local. No GitHub Actions or hosted GPU is used for JQL scoring.

- Apple Silicon: install a PyTorch build with MPS support, then use `DEVICE=mps` (or `auto`).
- Windows/NVIDIA: install the CUDA-enabled PyTorch build matching the installed NVIDIA driver/CUDA runtime from the official PyTorch selector, then use `DEVICE=cuda` (or `auto`).
- CPU fallback: `DEVICE=cpu`.

The Makefile deliberately does not install PyTorch automatically: CPU-only and CUDA/MPS wheels are platform-specific. Install the matching PyTorch build first, then install the remaining JQL dependencies with `make install-jql`.

## One-hour resumable batches

Model downloads and initialization happen before the one-hour timer starts. Each completed batch is appended and fsynced. Re-run the same target with the same output path to resume; rows already present in the output are skipped using a stable key.

```sh
make install-corpus
# Install platform-appropriate PyTorch separately.
make install-jql
make all DEVICE=mps                 # Apple Silicon
make rate DEVICE=cuda MAX_SECONDS=3600 BATCH_SIZE=64  # Windows/NVIDIA
```

The full dependency chain is:

`download -> filter -> anonymize -> count -> assess -> rate`

Each stage is an individual Make target. See the repository Makefile and `make help`. `make rate` runs one batch (3,600 seconds by default); invoke it again to continue rating. Set `MAX_SECONDS` for a shorter test or a different batch duration.

## Filtering and redaction policy

The news-only Unicode decimal-digit exclusion is applied at Leipzig acquisition and checked again during filtering. Wikipedia is not subjected to that rule. The default filter removes only empty/invalid text rows; it reports duplicate rows but keeps them, and has no arbitrary maximum sentence length. Override `MIN_CHARS` or `MAX_CHARS` explicitly if desired.

The `anonymize` target currently performs **pattern-based redaction only** in sentence text: email addresses, URLs, IPv4 addresses and phone-like strings. It does not reliably detect personal names, postal addresses, indirect identifiers or every format. It is not a guarantee of complete anonymization and requires review before public release. Provenance fields are retained for traceability; do not publish them if source-level anonymization is required.

## Interpreting scores

Report:
- number rated in each batch and cumulative rows/hour;
- hardware, device, batch size and maximum token length;
- throughput by language and source;
- score distributions for each head, plus mean and inter-head range;
- errors, skipped rows and remaining backlog.

Do not set a score threshold or discard low-scoring records. Inspect examples across the score distribution, and check whether distributions differ systematically by language or source before deciding whether the annotation is useful.
