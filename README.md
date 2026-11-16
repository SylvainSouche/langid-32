# langid-32

A reproducible multilingual language-identification project covering 32 languages. The project compares two compact character-based classifiers with a byte-level Transformer, using a shared corpus preparation and evaluation pipeline.

## Dataset sourcing

The corpus is the current project priority. See [the corpus source inventory](docs/corpus-inventory.md) for source coverage, preliminary Common Voice counts, FineWeb2 coverage, unresolved counts, and the acquisition plan. Read-only inventory commands cover Common Voice, FineWeb2 metadata and Parquet shard listings, DGT-TM, Tatoeba, Målfrid and Korean Law Open Data. The FineWeb2 inventory downloads only its small published language-distribution CSV; the shard inventory queries file metadata only. Neither downloads Parquet shards or document text. The 31 exact target subsets account for about 8.57 TB of Parquet data in aggregate, so the plan is bounded sampling, not wholesale download. Metadata/document counts are not verified usable-example counts.

### Mozilla Common Voice

Mozilla's distribution policy is that Common Voice datasets are made available through the [Mozilla Data Collective](https://datacollective.mozillafoundation.org/), and that users should not obtain mirrored copies from GitHub, Hugging Face, or other third-party platforms. Please download the original dataset directly from MDC. This repository is not an access point or mirror for the original Common Voice distribution.

Common Voice is released under CC0. Mozilla's request about where the original dataset is distributed is its data-distribution and stewardship policy; it is distinct from the CC0 licence applied to the dataset. Individual MDC datasheets also display dataset-level forbidden-use statements (including speaker re-identification and re-hosting/re-sharing the original dataset). We record those conditions separately from the SPDX CC0-1.0 field. This repository does not mirror the original archives; this statement does not pre-judge the legal status of a separately curated text-only derivative.

For this language-identification project, we prepare a targeted text-only corpus rather than republishing the original Common Voice dataset. The preparation pipeline selects and transforms sentence text for the 32 language classes. It excludes audio, speaker recordings, speaker or contributor identifiers, demographic metadata, and text that identifies a person or contains personal identifying information. The aim is to avoid retaining material that would identify a contributor, and to keep the resulting corpus focused on language identification rather than voice or speaker analysis.

We record the source release, provenance, transformations, corpus configuration, and output hashes so that preparation is reproducible. Each source and any additional corpus component is documented separately. The preparation tool does not export source group IDs or contributor metadata. Textual personal-data screening requires a reviewed policy and source-specific checks; optional regular-expression exclusions are available, but are not a substitute for that review.

**Code licence:** the MIT licence in `LICENSE` applies to the project code. It does not relicense source datasets or corpus contents; each dataset component retains its own documented terms.

## Data policy

- Prefer datasets with permissive, clearly documented terms; prioritise MIT, BSD, and CC0 where applicable.
- Record the dataset licence and source-distribution policy separately.
- Keep source provenance and preparation steps reproducible.
- Do not include audio, contributor-linked identifiers, demographic metadata, or text identifying individuals in published corpus material.
- Keep training, validation, and test splits separate; split by source document/group before extracting or cropping samples to avoid leakage.
- Do not commit credentials, access tokens, raw source downloads, or unnecessary personal data.

## Corpus preparation and global merge\n\nThe original `langid32-prepare` command remains a single-source CSV/TSV helper. A separate merge-first pipeline now accepts source-normalized JSONL records, applies shared NFC/whitespace normalization, exact cross-source deduplication within each language, deterministic group-level splits, and the final per-language cap. It retains licence and source provenance in an internal `records.jsonl` sidecar while keeping group IDs and detailed provenance out of the text-only split files. The merge does not silently balance or prioritize sources; it reports source counts so quotas can be designed from measured coverage.\n\nFineWeb2 v2.1.0 has been extracted and assembled as a private 640,000-sentence candidate (31 languages × 20,000). The new staging adapter and GitHub Actions workflow run it through the global merge pipeline. FineWeb2 remains a candidate only: its ODC-By compilation licence does not resolve rights in underlying crawled text, and the deterministic bounded sample still needs quality and privacy review. English remains a separate FineWeb acquisition route. See [FineWeb2 inventory](docs/fineweb2-inventory.md).\n\n## Corpus preparation (initial implementation)

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

The corpus is now the active priority. The source inventory records 32-language coverage and preliminary source counts for Common Voice, DGT-TM, Europarl, JRC-Acquis, Tatoeba, Målfrid and candidate Korean sources. Common Voice v27 metadata has entries for all 32 target classes; 21 have at least 20,000 validated-sentence metadata entries, while 11 fall below that threshold. These are metadata counts, not yet filtered TSV counts.

Read-only inventory tools are committed for Common Voice archives, Tatoeba CC0, Målfrid 2026 and the Korean Law Open Data API. A first source component has now been extracted and passed through the global pipeline: FineWeb2 v2.1.0, 31 non-English languages × 20,000 samples (640,000 total). The integration workflow re-ran normalization, exact per-language deduplication, global group splitting and the 20,000-per-language cap; it produced exactly 16,000 train / 2,000 validation / 2,000 test rows for every FineWeb2 language, with zero additional rejects and 77,767 distinct hostname groups. The private GitHub Actions artifact is `fineweb2-global-candidate-v1` (workflow run 43930504989). It is a technical candidate only: underlying crawled-text rights and text-level privacy/quality still need review.

The other sources are not yet ingested as text. Next work is to add DGT-TM, Tatoeba CC0, Målfrid and Common Voice adapters, measure cross-source duplicates and source/domain balance, and establish an English route (Common Voice and/or original FineWeb). The 32-language final corpus is not yet assembled. Model benchmarking and held-out evaluation remain deferred.
