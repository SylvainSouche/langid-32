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

Counts shown below are native upstream units until sentence-level candidate counts have been computed. DGT and FineWeb-2 have provider-reported per-language counts; FineWeb English has a dataset-viewer row count; TeMU-BSC has a conservative, file-level minimum for Catalan. FineWeb-2 counts are filtered document counts, not sentence counts; English is distributed separately in FineWeb. Other cells remain explicitly unmeasured rather than repeating old project caps.

| Language | Common Voice 22 | DGT-TM 2021 (TUs) | FineWeb-2 (documents) | Leipzig News | Leipzig Wikipedia | Tatoeba CC0 | FineWeb English (records) | Målfrid 2026 (tokens) | Icelandic Gigaword 2024 (words) | Korean Wikipedia (articles) | BSC Legal (sentence pairs) | TeMU-BSC CC0 | MultiUN | UNPC | UN Arabic-English Filtered* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bg | TBD | 4,602,085 | 25,994,731 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| hr | TBD | 2,554,319 | 6,195,824 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| cs | TBD | 6,410,466 | 66,067,904 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| da | TBD | 5,935,254 | 45,391,655 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| nl | TBD | 5,873,514 | 147,301,270 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| en | TBD | 8,624,934 | TBD | TBD | TBD | TBD | 25,900,000,000 | 570,099,658 | — | — | — | — | TBD | TBD | TBD |
| et | TBD | 6,450,667 | 10,218,587 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| fi | TBD | 5,933,745 | 36,710,816 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| fr | TBD | 6,397,822 | 360,058,973 | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| de | TBD | 5,958,872 | 495,964,485 | TBD | TBD | TBD | — | — | — | — | — | — | TBD (small) | — | — |
| el | TBD | 5,782,498 | 47,421,073 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| hu | TBD | 6,559,000 | 49,935,986 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| ga | TBD | 235,384 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| it | TBD | 5,967,350 | 238,984,437 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| lv | TBD | 6,504,918 | 8,030,316 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| lt | TBD | 6,501,706 | 13,471,965 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| mt | TBD | 4,830,614 | TBD | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| pl | TBD | 6,463,748 | 151,966,724 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| pt | TBD | 6,390,501 | 199,737,979 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| ro | TBD | 4,520,726 | 58,303,671 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| sk | TBD | 6,505,108 | 29,991,521 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| sl | TBD | 6,472,554 | 12,059,130 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| es | TBD | 5,965,669 | 441,287,261 | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| sv | TBD | 6,025,986 | 59,485,306 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| nb | TBD | — | 38,144,343 | TBD | TBD | TBD | — | 1,890,232,881 | — | — | — | — | — | — | — |
| nn | TBD | — | TBD | TBD | TBD | TBD | — | 170,231,965 | — | — | — | — | — | — | — |
| ru | TBD | — | 699,083,579 | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| ja | TBD | — | 400,138,563 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| zh | TBD | — | 636,058,984 | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | — |
| ko | TBD | — | 60,874,355 | TBD | TBD | TBD | — | — | — | TBD | — | — | — | — | — |
| ar | TBD | — | 61,977,525 | TBD | TBD | TBD | — | — | — | — | — | — | TBD | TBD | TBD |
| tr | TBD | — | 95,129,129 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — |
| ca | TBD | — | 17,136,414 | TBD | TBD | TBD | — | — | — | — | TBD | ≥249,681 identified CC0 sentences (partial) | — | — | — |
| is | TBD | — | 3,014,429 | TBD | TBD | TBD | — | — | TBD | — | — | — | — | — | — |

* The Arabic-English filtered derivative combines MultiUN and UNPC. Its pair count must not be added to either upstream source, nor counted as independent unique material.

## First verified provider counts

### DGT-TM 2021

The JRC's official statistics file reports cumulative TUs through DGT-TM 2020 (the release distributed as DGT-TM 2021), including the DGT-TM 2007 baseline. The language-level values are reproduced in [sources/dgt-tm-2021.md](sources/dgt-tm-2021.md). The source's TU definition explicitly permits sentence fragments; the figures are not sentence counts.

### FineWeb-2

The provider's language/script distribution table reports filtered document counts. Counts in this matrix map the project's target languages to the relevant ISO 639-3 subset (for example, Greek ell_Grek, Catalan cat_Latn, Icelandic isl_Latn). They are **documents**, not sentences. FineWeb-2 also distributes removed subsets separately; the filtered counts below are not the full post-deduplication language pool. The README says filtered plus removed together represent the entire data for each language following global deduplication. Source: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2

### FineWeb English

The Hugging Face dataset page exposes 25.9 billion rows for the default FineWeb dataset and describes more than 18.5 trillion tokens. The row figure is retained as the provider's native record count; it is not a sentence count. Source: https://huggingface.co/datasets/HuggingFaceFW/fineweb

### TeMU-BSC Catalan CC0

The repository README explicitly reports 93,691 sentences in the filtered Catalan Government crawl file and 155,990 sentences in `datasets_sentences.tsv` from Projecte Aina. These two named files give a conservative identified minimum of 249,681 sentences. This is not a complete repository total: the repository contains further individual files, aggregate files overlap their constituents, and some contributions have separate permission/waiver terms. Do not add `new_catalan_cc0_corpus.txt` or `xitxat_toponyms.txt` on top of their constituent files. The number is a file-level identified minimum, not the final deduplicated unique count. Source: https://github.com/TeMU-BSC/catalan_CC0_sentences

### Målfrid 2026

The National Library of Norway reports provider token counts: Bokmål 1,890,232,881; English 570,099,658; Nynorsk 170,231,965. These remain tokens, not sentence counts. Source: https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026.pdf

## Next source-counting passes

1. Common Voice 22: read the release's per-locale validatedSentences statistics; do not use the project's 9,000 cap.
2. FineWeb-2: filtered document counts have been transcribed for 30 target languages. Complete the missing Gaelic, Nynorsk and Maltese mapping; record removed-subset counts and word counts too. FineWeb English has 25.9B provider rows recorded separately.
3. Leipzig News and Wikipedia: enumerate downloadable package manifests for every target language and count sentence rows in the actual archives.
4. Tatoeba: count the CC0 export by language code; distinguish CC0-only from the larger CC-BY export.
5. Målfrid, Icelandic Gigaword, Korean Wikipedia: count documents/records and segment their complete text into candidate sentences; provider token/word/article totals are not sentence totals.
6. BSC Legal and TeMU-BSC: TeMU-BSC now has a conservative identified minimum of 249,681 Catalan CC0 sentences from two explicitly counted files; enumerate the remaining files, rights and overlaps. BSC Legal still needs language-side sentence counts.
7. MultiUN and UNPC: count monolingual language sides, not pair-configuration row sums; deduplicate within each corpus and compare document identifiers between corpora.
8. GreynirCorpus: currently excluded pending explicit rights approval; inventorying its upstream capacity does not imply permission to use it.

No source's previous langid-32 sample cap or staged count is admissible as an upstream availability count.
