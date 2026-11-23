# Leipzig Corpora Collection — News

**Text unit:** Sentences from news text  
**Primary source:** https://wortschatz.uni-leipzig.de/en/download/

## Creator and origin

Leipzig University Wortschatz / Leipzig Corpora Collection.

## Access methods

Language-specific packages via download portal; exact archive/version must be recorded from local manifest.

## File types and structure

Compressed UTF-8 TSV; *_sentences.txt contains sentence ID and sentence; companion word/source lists and optional POS files.

## Distribution conditions and rights

Underlying news rights and package terms are corpus/release dependent. Download availability is not blanket redistribution permission.

## Content and language coverage

News texts in many languages; project stages 3,000 for 33 target languages, no Nynorsk news sample.

## Verified upstream catalogue availability (independent of project acquisition)

The Leipzig Corpora Collection catalogue has been checked at the per-language corpus pages, not inferred from the project's 3,000-row downloads. It exposes downloadable sentence packages at 10K, 30K, 100K, 300K and (where offered) 1M tiers, plus an `All` package. The latest catalogue includes News releases through 2024 for some languages; older historical releases remain available for others. Examples verified directly from the provider catalogue:

| Language | News catalogue evidence |
|---|---|
| bg | 2020: 1M and All; 2019: 1M and All |
| hr | 2020: 1M and All |
| cs | 2022: 1M and All; 2024: 30K and 300K |
| da | 2021: 1M; 2022: 30K and 100K; earlier All releases |
| nl | 2024: up to 1M; All on 2023 |
| en | 2020: 1M and All; 2021: 1M; 2023–2024: 30K |
| et | 2022: up to 300K; earlier All releases |
| fi | 2022: 1M and All |
| fr | 2022: 1M and All; 2023–2024 packages also listed |
| el | 2024: 1M and All |
| hu | 2024: 1M and All |
| ga | No News section in the current Irish catalogue; Wikipedia is listed separately |
| it | 2023: 1M and All; 2024: 30K and 300K |
| lv | 2020: up to 300K; older All releases |
| lt | 2020: 1M and All |
| mt | 2020: 30K and All |
| pl | 2024: 1M and All |
| pt | 2024: 1M and All |
| ro | 2024: 1M and All |
| sk | 2020: up to 100K |
| sl | 2020: 1M and All |
| es | 2024: 1M and All |
| sv | 2023: 1M and All |
| nb | Historical News packages include 1M; latest page also lists web corpora separately |
| nn | No News section; Web and Wikipedia corpora are listed |
| ru | 2024: 1M and All |
| ja | Historical News packages include 1M |
| zh | No News section in the Mandarin Chinese catalogue; Wikipedia is listed separately |
| ko | 2022: 1M and All |
| ar | Multiple historical News releases include 1M and All |
| tr | 2024: 1M and All |
| ca | Recent News releases include All packages; 2022 includes up to 300K |
| is | 2020: up to 30K; Web corpora separately reach 1M |

These are catalogue package tiers, not counts of the complete `All` corpora and not a sum across releases. The fixed-size tiers are samples, so they must not be summed together. The `All` package is the full corpus for that release. The exact row counts for `All` archives still need to be obtained from the archive manifests or `*_sentences.txt` files. The provider's file-format note confirms that `*_sentences.txt` contains all sentences in the downloaded corpus. Sources: https://cls.wortschatz-leipzig.de/en and https://wortschatz.informatik.uni-leipzig.de/public/documents/Format_Download_File-eng.pdf

## Current langid-32 acquisition snapshot

3,000/language is our sample, not the complete Leipzig corpus.

| Language | Current staged records |
|---|---:|
| bg | 3,000 |
| hr | 3,000 |
| cs | 3,000 |
| da | 3,000 |
| nl | 3,000 |
| en | 3,000 |
| et | 3,000 |
| fi | 3,000 |
| fr | 3,000 |
| de | 3,000 |
| el | 3,000 |
| hu | 3,000 |
| ga | 3,000 |
| it | 3,000 |
| lv | 3,000 |
| lt | 3,000 |
| mt | 3,000 |
| pl | 3,000 |
| pt | 3,000 |
| ro | 3,000 |
| sk | 3,000 |
| sl | 3,000 |
| es | 3,000 |
| sv | 3,000 |
| nb | 3,000 |
| ru | 3,000 |
| ja | 3,000 |
| zh | 3,000 |
| ko | 3,000 |
| ar | 3,000 |
| tr | 3,000 |
| ca | 3,000 |
| is | 3,000 |

**Current staged total:** 99,000 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Select and pin one consistent release strategy per language (prefer the newest usable News release; retain older `All` corpora when they are the only full-size option).
- Download each `All` archive and count lines in its `*_sentences.txt`; fixed-size 10K–1M packages are not full capacity.
- Record archive checksums, release dates and exact line counts; never add overlapping releases or size tiers.
- Verify package-specific terms and underlying news rights.
