# langid-32

A reproducible multilingual language-identification project covering 32 languages. The project compares two compact character-based classifiers with a byte-level Transformer, using a shared corpus preparation and evaluation pipeline.

## Dataset sourcing

### Mozilla Common Voice

Mozilla's distribution policy is that Common Voice datasets are made available through the [Mozilla Data Collective](https://datacollective.mozillafoundation.org/), and that users should not obtain mirrored copies from GitHub, Hugging Face, or other third-party platforms. Please download the original dataset directly from MDC. This repository is not an access point or mirror for the original Common Voice distribution.

Common Voice is released under CC0. Mozilla's request about where the original dataset is distributed is its data-distribution and stewardship policy; it is distinct from the CC0 licence applied to the dataset.

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

## Corpus preparation (initial implementation)

The first preparation CLI accepts a UTF-8 CSV or TSV containing a text column, language column, and source document/group column. It applies NFC normalization, collapses whitespace, filters by character and UTF-8 byte length, removes duplicate text within each language, assigns deterministic group-level splits, and writes text-only JSONL plus a SHA-256 provenance manifest.

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

All routes will share corpus splits and evaluation, including per-language metrics, confusion pairs, length sensitivity, calibration, latency, memory, and model size.

## Status

Repository scaffold and initial deterministic corpus-preparation CLI are in place. Model implementations, source-specific adapters, and the full evaluation protocol are next.
