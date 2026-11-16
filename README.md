# langid-32

A reproducible multilingual language-identification project covering 32 languages. The project compares lightweight character-based classifiers with a byte-level Transformer, using a shared corpus preparation and evaluation pipeline.

## Dataset sourcing

### Mozilla Common Voice

Mozilla asks users to download Common Voice datasets directly from the [Mozilla Data Collective](https://datacollective.mozillafoundation.org/). Please obtain the original Common Voice data there rather than using this repository as a download point or mirror of Mozilla's distribution.

This project may document and perform its own targeted corpus preparation for language-identification training and evaluation. Dataset provenance, applicable licence terms, source versions, transformations, and redistribution conditions must be recorded for each corpus component. Do not assume that the terms for one source apply to another, or that a source's licence and its platform terms are interchangeable.

## Data policy

- Prefer datasets with permissive, clearly documented terms; prioritise MIT, BSD, and CC0 where applicable.
- Verify the actual licence and redistribution permissions for each dataset and component before publishing derived material.
- Keep source provenance and preparation steps reproducible.
- Keep training, validation, and test splits separate; split by source document before extracting or cropping samples to avoid leakage.
- Do not commit credentials, access tokens, or unlicensed source material.

## Status

Initial repository setup. The corpus pipeline, model implementations, and evaluation protocol will be added next.
