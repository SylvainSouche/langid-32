# langid-32

A reproducible multilingual language-identification project. The `langid-32` name identifies the original 32-language scope; the supported language inventory can grow beyond 32 while preserving the original benchmark. The project compares two compact character-based classifiers with a byte-level Transformer, using a shared corpus preparation and evaluation pipeline.

## Dataset sourcing

The next corpus build follows the [v6 acquisition and selection policy](docs/corpus-policy-v6.md): 30,000 usable records per language, a 20,000-record core plus reserve, a 30% preferred / 50% hard per-source ceiling (documented low-resource exceptions only), and global exclusion of PII matches and every text string shared across language labels.

The corpus is the current project priority. See [the corpus source inventory](docs/corpus-inventory.md) for source coverage and the acquisition plan, [the FineWeb2 inventory](docs/fineweb2-inventory.md), [the English FineWeb inventory](docs/fineweb-inventory.md), and the [independent v5 candidate audit](docs/candidate-audit-v5.md). Read-only inventory commands cover Common Voice, FineWeb2 metadata and Parquet shard listings, DGT-TM, Tatoeba, Målfrid and Korean Law Open Data. The FineWeb2 inventory downloads only its small published language-distribution CSV; the shard inventory queries file metadata only. Neither downloads Parquet shards or document text. The 31 exact target subsets account for about 8.57 TB of Parquet data in aggregate, so the plan is bounded sampling, not wholesale download. Metadata/document counts are not verified usable-example counts.

### Common Voice text-only pilot

The project has retired its Mozilla Data Collective acquisition workflow. The current technical pilot reads only `transcript/<locale>/validated_sentences.tsv` from the unofficial Hugging Face conversion [`fsicoli/common_voice_22_0`](https://huggingface.co/datasets/fsicoli/common_voice_22_0); it does not fetch audio or speaker/demographic metadata. This is not an official Mozilla distribution. The HF dataset card labels the conversion CC0, but that label alone is not sufficient to establish the rights and distribution status of the conversion or its source material. Verify conversion provenance, exact upstream release, licence and applicable source-specific terms before treating any record as cleared for publication.

The text-only curation step applies NFC/whitespace normalization, length limits, basic email/URL/IPv4/long-number/phone-pattern exclusions, within-language deduplication, cross-language exact-string collision removal, and deterministic per-language sampling. These are conservative automated filters, **not complete PII detection, human language validation, or legal clearance**. Raw source TSVs are removed from the ephemeral runner; only curated candidate text and audit metadata are uploaded as a short-lived workflow artifact. A failed source locale causes the workflow to finish with failure even when other locales were curated.

## Data policy

- Prefer datasets with permissive, clearly documented terms; prioritise MIT, BSD, and CC0 where applicable.
- Record the dataset licence and source-distribution policy separately.
- Keep source provenance and preparation steps reproducible.
- Do not include audio, contributor-linked identifiers, demographic metadata, or text identifying individuals in published corpus material.
- Keep training, validation, and test splits separate; split by source document/group before extracting or cropping samples to avoid leakage.
- Do not commit credentials, access tokens, raw source downloads, or unnecessary personal data.

## Corpus preparation and global merge

The original `langid32-prepare` command remains a single-source CSV/TSV helper. A separate merge-first pipeline now accepts source-normalized JSONL records, applies shared NFC/whitespace normalization, exact cross-source deduplication within each language, deterministic group-level splits, and the final per-language cap. It retains licence and source provenance in an internal `records.jsonl` sidecar while keeping group IDs and detailed provenance out of the text-only split files. The merge does not silently balance or prioritize sources; it reports source counts so quotas can be designed from measured coverage.

FineWeb2 v2.1.0 has been extracted and assembled as a private 640,000-sentence candidate (31 languages × 20,000). The new staging adapter and GitHub Actions workflow run it through the global merge pipeline. FineWeb2 remains a candidate only: its ODC-By compilation licence does not resolve rights in underlying crawled text, and the deterministic bounded sample still needs quality and privacy review. English remains a separate FineWeb acquisition route. See [FineWeb2 inventory](docs/fineweb2-inventory.md).

## Corpus preparation (initial implementation)

The first preparation CLI accepts a UTF-8 CSV or TSV containing a text column, language column, and source document/group column. It applies NFC normalization, collapses whitespace, filters by character and UTF-8 byte length, removes duplicate text within each language, assigns deterministic group-level splits, and writes text-only JSONL plus a SHA-256 provenance manifest. The default cap is 20,000 examples per language in total, allocated across the three splits according to their configured fractions.

Install and test:

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
```

Example using a Common Voice locale TSV (after downloading it directly from MDC):

```sh
langid32-prepare \
  --input data/raw/fr/train.tsv \
  --output data/processed/common-voice-fr \
  --text-column sentence \
  --group-column sentence \
  --source-name common-voice \
  --source-release "RECORD THE MDC RELEASE" \
  --source-licence CC0-1.0 \
  --source-download-origin https://datacollective.mozillafoundation.org/ \
  --language fr
```

The CLI currently processes one input file per invocation. Raw downloads and generated corpora are excluded from Git; do not commit them directly. Dataset publication and Hugging Face upload will be handled as a separate, explicit pipeline stage after the corpus format and licensing review are validated.

## Model routes

- **A1:** hashed character n-gram features with a sparse linear classifier.
- **A2:** hashed character n-gram EmbeddingBag with a compact linear head.
- **B:** byte-level Transformer trained from scratch.

The initial PyTorch model definitions and a shared training/validation loop are now implemented. Install the optional training dependency:

```sh
python -m pip install -e ".[train,dev]"
```

Train each route against the same prepared split directory:

```sh
langid32-train --route a1 --data data/processed/corpus --output runs/a1
langid32-train --route a2 --data data/processed/corpus --output runs/a2
langid32-train --route b  --data data/processed/corpus --output runs/b
```

The trainer selects checkpoints using validation loss and writes a training report with parameter counts and per-class validation metrics. It auto-selects CUDA, Apple MPS, or CPU; use `--device cpu`, `mps`, or `cuda` to override. These are first implementations, not yet benchmarked or validated on a full corpus. The test split is not read by the trainer.

See [model design](docs/model-design.md) for architecture details.

## Status

The corpus remains the active priority; model benchmarking is deferred until the source mix and rights review are complete.

A three-source **original 32-language / 640,000-row candidate** has passed the global merge pipeline. This remains the historical baseline; subsequent language additions are versioned extensions.

| Source | Records in final candidate | Coverage |
|---|---:|---|
| FineWeb2 v2.1.0 | 510,702 | 31 target languages |
| DGT-TM release 2021 | 92,196 | 24 EU official languages |
| Tatoeba CC0 export (14 Nov 2026) | 37,102 | 18 staged; 17 retained |
| **Total** | **640,000** | **32 languages** |

Every language has exactly 20,000 records: 16,000 train, 2,000 validation and 2,000 test. The final artifact is `multisource-candidate-v4-unicode-pii-clean`, produced by [GitHub Actions run 43938190407](https://github.com/SylvainSouche/langid-32/actions/runs/43938190407). It contains the text-only splits, an internal provenance sidecar, the merge manifest and source manifests. The artifact is retained by GitHub Actions for 14 days.

The merge independently verifies exact per-language counts, exact normalized-text deduplication within each language, and globally consistent group splits. The final candidate has 186,190 output groups (241,195 candidate groups before the per-language cap); no exact duplicate pairs across sources were recorded. The global privacy pass excluded 11 email matches and 31 URL matches. An independent scan of the final 640,000 records found no residual email addresses, URLs or valid IPv4 addresses. Phone-like and long numeric sequences are retained with flags for review (1,006 and 676 occurrences respectively). An independent review also found 94 exact text strings (194 records) assigned to multiple language labels, plus marked FineWeb2 hostname concentration in Maltese (20.1% from one host), Nynorsk (9.0%) and Irish (5.0%). These are quality-review findings, not reasons to treat the candidate as cleared. See [the independent v4 audit](docs/candidate-audit-v4.md).

Source composition is deliberately reported rather than balanced with hidden quotas. English consists of 17,797 Tatoeba and 2,203 DGT-TM records; Russian is 10,582 Tatoeba and 9,418 FineWeb2; French combines all three sources (10,251 FineWeb2, 7,190 Tatoeba, 2,559 DGT-TM). DGT-TM is an English-centred translation memory: its original-language status is unknown, and segments may be fragments or translationese.

This is a technical candidate, **not a release-ready or rights-cleared corpus**:
- FineWeb2's compilation licence does not resolve rights in the underlying crawled text.
- DGT-TM is reused under the European Commission's reuse conditions and requires attribution; it is not CC0.
- Tatoeba records come from its CC0 export.
- Text quality, domain/source balance, remaining privacy risks and source-specific rights still need review.

The DGT component uses the five-volume 2021 package. The newer 2025 catalogue entries have not yet been ingested or reconciled with the JRC release documentation. Common Voice v27 and Målfrid 2026 remain the next major source integrations; Common Voice must be obtained from the original Mozilla Data Collective distribution, not third-party mirrors.

See [the corpus source inventory](docs/corpus-inventory.md), [FineWeb2 inventory](docs/fineweb2-inventory.md), and the DGT/Tatoeba source manifests in the candidate artifact.
