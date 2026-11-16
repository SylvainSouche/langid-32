# langid-32

A reproducible multilingual language-identification project covering 32 languages. The project compares lightweight character-based classifiers with a byte-level Transformer, using a shared corpus preparation and evaluation pipeline.

## Dataset sourcing

### Mozilla Common Voice

Mozilla's distribution policy is that Common Voice datasets are made available through the [Mozilla Data Collective](https://datacollective.mozillafoundation.org/), and that users should not obtain mirrored copies from GitHub, Hugging Face, or other third-party platforms. Please download the original dataset directly from MDC. This repository is not an access point or mirror for the original Common Voice distribution.

The Common Voice dataset is released under CC0. Mozilla's request about where the original dataset is distributed is its data-distribution and stewardship policy; it is distinct from the CC0 licence applied to the dataset.

For this language-identification project, we prepare a targeted text-only corpus rather than republishing the original Common Voice dataset. The preparation pipeline selects and transforms sentence text for the 32 language classes. It excludes audio, speaker recordings, speaker or contributor identifiers, demographic metadata, and text that identifies a person or contains personal identifying information. The aim is to avoid retaining material that would identify a contributor, and to keep the resulting corpus focused on language identification rather than voice or speaker analysis.

We record the source release, provenance, transformations, corpus configuration, and output hashes so that preparation is reproducible. Each source and any additional corpus component is documented separately.

## Data policy

- Prefer datasets with permissive, clearly documented terms; prioritise MIT, BSD, and CC0 where applicable.
- Record the licence and relevant source-distribution terms separately; do not conflate a dataset licence with a platform's distribution policy.
- Keep source provenance and preparation steps reproducible.
- Exclude personal identifying text and contributor-linked identifiers or metadata from the language-identification corpus.
- Keep training, validation, and test splits separate; split by source document before extracting or cropping samples to avoid leakage.
- Do not commit credentials, access tokens, audio, or unnecessary personal data.

## Status

Initial repository setup. The corpus pipeline, model implementations, and evaluation protocol will be added next.
