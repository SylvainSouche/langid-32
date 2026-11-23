# Upstream availability matrix

**Purpose:** count material actually available from each upstream source for each of the 34 target languages, independently of what langid-32 previously downloaded, sampled, capped, staged or selected.

This source-capacity matrix is separate from the historical acquisition matrix in [README.md](README.md).

## Counting rules

- A cell is an upstream availability count, never a project-used count.
- The target unit is candidate sentences wherever the source supplies sentences or can be segmented reproducibly. Preserve a second native-unit count where the provider reports translation units, documents, paragraphs, tokens, words or articles.
- For document corpora, do not pretend document counts are sentence counts. Count complete source-side records and sentence-segment the available text, or explicitly mark the sentence count as not yet measured.
- For parallel corpora, count each language side independently. Do not multiply pair counts by the number of pairs; deduplicate within the source before reporting unique monolingual sentences.
- Apply only source-defined eligibility rules at this stage. Do not apply langid-32 sampling caps, JQL scoring or final quality selection.
- Keep four distinct quantities where possible: provider-reported native units; acquired raw records; sentence-segmented candidates; unique candidates after within-source deduplication.
- TBD means not yet measured; it does not mean zero. — means the source does not cover that language according to its documented scope. Approximate values must carry ~ and a source/method note.

## Matrix

Counts shown below are native upstream units until sentence-level candidate counts have been computed. DGT is the first source transcribed from its provider's per-language statistics. Other cells remain explicitly unmeasured rather than repeating old project caps.

| Language | Common Voice 22 | DGT-TM 2021 (TUs) | FineWeb-2 (documents) | Leipzig News | Leipzig Wikipedia | Tatoeba CC0 | FineWeb English (documents) | Målfrid 2026 (tokens) | Icelandic Gigaword 2024 (words) | Korean Wikipedia (articles) | BSC Legal (sentence pairs) | TeMU-BSC CC0 | MultiUN | UNPC | UN Arabic-English Filtered* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bg | TBD | 4,602,085 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| hr | TBD | 2,554,319 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| cs | TBD | 6,410,466 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| da | TBD | 5,935,254 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| nl | TBD | 5,873,514 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| en | TBD | 8,624,934 | TBD | TBD | TBD | TBD | TBD | 570,099,658 | — | — | — | — | TBD | TBD | TBD |
| et | TBD | 6,450,667 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| fi | TBD | 5,933,745 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| fr | TBD | 6,397,822 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| de | TBD | 5,958,872 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | TBD (small) | — | — |
| el | TBD | 5,782,498 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| hu | TBD | 6,559,000 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| ga | TBD | 235,384 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| it | TBD | 5,967,350 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| lv | TBD | 6,504,918 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| lt | TBD | 6,501,706 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| mt | TBD | 4,830,614 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| pl | TBD | 6,463,748 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| pt | TBD | 6,390,501 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| ro | TBD | 4,520,726 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| sk | TBD | 6,505,108 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| sl | TBD | 6,472,554 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| es | TBD | 5,965,669 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| sv | TBD | 6,025,986 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| nb | TBD | — | TBD | TBD | TBD | TBD | — | 1,890,232,881 | — | — | — | — | — | — | — |
| nn | TBD | — | TBD | TBD | TBD | TBD | — | 170,231,965 | — | — | — | — | — | — | — |
| ru | TBD | — | TBD | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| ja | TBD | — | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| zh | TBD | — | TBD | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| ko | TBD | — | TBD | TBD | TBD | TBD | — | — | — | TBD | — | — | — | — | — |
| ar | TBD | — | TBD | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | TBD |
| tr | TBD | — | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| ca | TBD | — | TBD | TBD | TBD | TBD | — | — | — | — | TBD | TBD | — | — | — |
| is | TBD | — | TBD | TBD | TBD | TBD | — | — | TBD | — | — | — | — | — | — |

* The Arabic-English filtered derivative combines MultiUN and UNPC. Its pair count must not be added to either upstream source, nor counted as independent unique material.

## First verified provider counts

### DGT-TM 2021

The JRC's official statistics file reports cumulative TUs through DGT-TM 2020 (the release distributed as DGT-TM 2021), including the DGT-TM 2007 baseline. The language-level values are reproduced in [sources/dgt-tm-2021.md](sources/dgt-tm-2021.md). The source's TU definition explicitly permits sentence fragments; the figures are not sentence counts.

### Målfrid 2026

The National Library of Norway reports provider token counts: Bokmål 1,890,232,881; English 570,099,658; Nynorsk 170,231,965. These remain tokens, not sentence counts. Source: https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026.pdf

## Next source-counting passes

1. Common Voice 22: read the release's per-locale validatedSentences statistics; do not use the project's 9,000 cap.
2. FineWeb-2: use the provider's language/script distribution manifest, including filtered and removed subsets as appropriate; record document counts and word counts. English is in the separate FineWeb dataset.
3. Leipzig News and Wikipedia: enumerate downloadable package manifests for every target language and count sentence rows in the actual archives.
4. Tatoeba: count the CC0 export by language code; distinguish CC0-only from the larger CC-BY export.
5. Målfrid, Icelandic Gigaword, Korean Wikipedia: count documents/records and segment their complete text into candidate sentences; provider token/word/article totals are not sentence totals.
6. BSC Legal and TeMU-BSC: enumerate files and count language-side sentences, excluding duplicates and non-sentence/generated material where source documentation requires.
7. MultiUN and UNPC: count monolingual language sides, not pair-configuration row sums; deduplicate within each corpus and compare document identifiers between corpora.
8. GreynirCorpus: currently excluded pending explicit rights approval; inventorying its upstream capacity does not imply permission to use it.

No source's previous langid-32 sample cap or staged count is admissible as an upstream availability count.
