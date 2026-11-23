| is | 4,993 | — | 8,349,376 | ca | undefined | 45,018,757 || tr | undefined | 260,547,567 || ar | undefined | 154,130,106 || ko | undefined | 197,842,127 || zh | undefined | 1,485,809,411 || ja | undefined | 1,274,369,743 || ru | undefined | 2,018,681,664 || nn | undefined | 10,729,196 || nb | undefined | 88,766,514 || sv | undefined | 212,118,133 || es | undefined | 1,079,742,994 || sl | undefined | 36,116,785 || sk | undefined | 92,017,704 || ro | undefined | 138,597,415 || pt | undefined | 617,680,364 || pl | undefined | 452,922,883 || mt | undefined | 10,128,530 || lt | undefined | 45,910,855 || lv | undefined | 34,678,846 || it | undefined | 540,170,115 || ga | undefined | 2,712,276 || hu | undefined | 142,923,778 || el | undefined | 144,812,222 || de | undefined | 1,054,844,054 || fr | undefined | 956,947,801 || fi | undefined | 115,719,855 || et | undefined | 39,552,577 || en | undefined | — || nl | undefined | 456,247,913 || da | undefined | 148,211,420 || cs | undefined | 239,100,701 || hr | undefined | 60,362,437 || bg | undefined | 67,154,724 || is | 4,993 || ca | 1,302,361 || tr | 410,398 || ar | 59,434 || ko | 7,322 || zh | 78,686 || ja | 37,288 || ru | 47,819 || nn | 5,318 || nb | 4,372 || sv | 26,202 || es | 1,081,921 || sl | 4,206 || sk | 17,876 || ro | 13,753 || pt | 43,526 || pl | 229,899 || mt | 5,273 || lt | 129,304 || lv | 34,333 || it | 924,883 || ga | 1,675 || hu | 326,221 || el | 6,856 || de | 2,057,917 || fr | 1,648,822 || fi | 5,848 || et | 10,910 || en | 1,680,014 || nl | 259,729 || da | 20,779 || cs | 451,100 || hr | — || bg | 39,572 |# Upstream availability matrix

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

Counts shown below are native upstream units until sentence-level candidate counts have been computed. Common Voice has provider-reported validated-sentence counts transcribed for all 34 target languages; Croatian is absent from this release; DGT and FineWeb-2 have provider-reported per-language counts; FineWeb English has a dataset-viewer row count; TeMU-BSC has a conservative, file-level minimum for Catalan. FineWeb-2 counts now sum provider filtered train, filtered test and removed train documents after global deduplication; they are documents, not sentences. English is distributed separately in FineWeb. Other cells remain explicitly unmeasured rather than repeating old project caps.

| Language | Common Voice 22 | DGT-TM 2021 (TUs) | FineWeb-2 (all deduped documents) | Leipzig News | Leipzig Wikipedia | Tatoeba CC0 | FineWeb English (records) | Målfrid 2026 (tokens) | Icelandic Gigaword 2024 (words) | GreynirCorpus (sentences) | Korean Wikipedia (articles) | BSC Legal (sentence pairs) | TeMU-BSC CC0 | MultiUN | UNPC | UN Arabic-English Filtered* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bg | 39,572 | 4,602,085 | 67,154,724 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| hr | — | 2,554,319 | 60,362,437 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| cs | 451,100 | 6,410,466 | 239,100,701 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| da | 20,779 | 5,935,254 | 148,211,420 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| nl | 259,729 | 5,873,514 | 456,247,913 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| en | 1,680,014 | 8,624,934 | — | TBD | TBD | TBD | 25,900,000,000 | 570,099,658 | — | — | — | — | — | TBD | TBD | TBD |
| et | 10,910 | 6,450,667 | 39,552,577 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| fi | 5,848 | 5,933,745 | 115,719,855 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| fr | 1,648,822 | 6,397,822 | 956,947,801 | TBD | TBD | TBD | — | — | — | — | — | — | — | TBD | TBD | — |
| de | 2,057,917 | 5,958,872 | 1,054,844,054 | TBD | TBD | TBD | — | — | — | — | — | — | — | TBD (small) | — | — |
| el | 6,856 | 5,782,498 | 144,812,222 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| hu | 326,221 | 6,559,000 | 142,923,778 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| ga | 1,675 | 235,384 | 2,712,276 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| it | 924,883 | 5,967,350 | 540,170,115 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| lv | 34,333 | 6,504,918 | 34,678,846 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| lt | 129,304 | 6,501,706 | 45,910,855 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| mt | 5,273 | 4,830,614 | 10,128,530 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| pl | 229,899 | 6,463,748 | 452,922,883 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| pt | 43,526 | 6,390,501 | 617,680,364 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| ro | 13,753 | 4,520,726 | 138,597,415 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| sk | 17,876 | 6,505,108 | 92,017,704 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| sl | 4,206 | 6,472,554 | 36,116,785 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| es | 1,081,921 | 5,965,669 | 1,079,742,994 | TBD | TBD | TBD | — | — | — | — | — | ~5,400,000 sentence pairs | — | TBD | TBD | — |
| sv | 26,202 | 6,025,986 | 212,118,133 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| nb | 4,372 | — | 88,766,514 | TBD | TBD | TBD | — | 1,890,232,881 | — | — | — | — | — | — | — | — |
| nn | 5,318 | — | 10,729,196 | TBD | TBD | — | — | 170,231,965 | — | — | — | — | — | — | — | — |
| ru | 47,819 | — | 2,018,681,664 | TBD | TBD | TBD | — | — | — | — | — | — | — | TBD | TBD | — |
| ja | 37,288 | — | 1,274,369,743 | TBD | TBD | TBD | — | — | — | — | — | — | — | — | — | — |
| zh | 78,686 | — | 1,485,809,411 | TBD | TBD | TBD | — | — | — | — | — | — | — | TBD | TBD | — |
| ko | 7,322 | — | 197,842,127 | TBD | TBD | — | — | — | — | — | 647.9K | — | — | — | — | — |
| ar | 59,434 | — | 154,130,106 | TBD | TBD | TBD | — | — | — | — | — | — | — | TBD | TBD | TBD |
| tr | 410,398 | — | 260,547,567 | TBD | TBD | — | — | — | — | — | — | — | — | — | — | — |
| ca | 1,302,361 | — | 45,018,757 | TBD | TBD | TBD | — | — | — | — | — | ~5,400,000 sentence pairs | ≥249,681 identified CC0 sentences (partial) | — | — | — |
| is | 4,993 | — | 8,349,376 | TBD | TBD | — | — | — | 794,816,184 | 10,000,000 | — | — | — | — | — | — |

* The Arabic-English filtered derivative combines MultiUN and UNPC. Its pair count must not be added to either upstream source, nor counted as independent unique material.

## Leipzig catalogue findings (package availability; exact `All` counts pending)

The official per-language Leipzig catalogue confirms fixed-size sentence packages and full `All` archives. It has been checked across the target-language pages. News packages reach 1M for many target languages (including bg, hr, cs, da, nl, en, fi, fr, el, hu, it, lt, pl, pt, ro, sl, es, sv, ru, ko, ar and tr); lower maximum tiers occur for et, lv, mt, sk and is. Irish and Nynorsk have no News section in their current language pages. Wikipedia `All` packages exist for the target languages examined, with smaller fixed tiers for Irish and Maltese and up to 3M for Catalan in one release. These are catalogue availability tiers, not exact full-corpus sentence counts. The `All` archives must be downloaded and their `*_sentences.txt` files counted before replacing the matrix's `TBD` cells. Do not sum size tiers or release years. Sources: https://cls.wortschatz-leipzig.de/en and https://wortschatz.informatik.uni-leipzig.de/public/documents/Format_Download_File-eng.pdf

## First verified provider counts

### Common Voice 22.0

The pinned Hugging Face conversion exposes the release's `release_stats.py`, whose per-locale `validatedSentences` field is a provider-reported sentence count. The complete target-language mapping is now transcribed from the pinned file: `bg` 39,572; `cs` 451,100; `da` 20,779; `nl` 259,729; `en` 1,680,014; `et` 10,910; `fi` 5,848; `fr` 1,648,822; `de` 2,057,917; `el` 6,856; `hu` 326,221; `ga-IE` 1,675; `it` 924,883; `lv` 34,333; `lt` 129,304; `mt` 5,273; `pl` 229,899; `pt` 43,526; `ro` 13,753; `sk` 17,876; `sl` 4,206; `es` 1,081,921; `sv-SE` 26,202; `nb-NO` 4,372; `nn-NO` 5,318; `ru` 47,819; `ja` 37,288; `zh-CN` 59,060 plus `zh-TW` 19,626 (combined as `zh`: 78,686); `ko` 7,322; `ar` 59,434; `tr` 410,398; `ca` 1,302,361; `is` 4,993. Croatian (`hr`) has no locale entry in this release and is marked `—`, not zero. These are provider-reported validated sentence counts, not audio-clip counts or project-selected records. Source: https://huggingface.co/datasets/fsicoli/common_voice_22_0/blob/0ca7c0e9cf2c25897c13aa73c54003d8d6d1cf28/release_stats.py

### DGT-TM 2021

The JRC's official statistics file reports cumulative TUs through DGT-TM 2020 (the release distributed as DGT-TM 2021), including the DGT-TM 2007 baseline. The language-level values are reproduced in [sources/dgt-tm-2021.md](sources/dgt-tm-2021.md). The source's TU definition explicitly permits sentence fragments; the figures are not sentence counts.

### FineWeb-2

The provider's complete fineweb2-language-distribution.csv lists train/test filtered splits and separate _removed train splits. The matrix now reports total available documents as filtered train + filtered test + removed train, which matches the provider's statement that filtered plus removed subsets reconstruct the entire per-language pool after global deduplication. These are **documents**, not sentences. English is intentionally separate in FineWeb. Counts include all scripts present for a target language (notably Romanian ron_Latn + ron_Cyrl, and Arabic arb_Arab + arb_Latn). Irish and Maltese are present in the CSV and are now counted rather than left TBD. Source CSV blob SHA: 24e400385ad45ebf477bb2dc49e502d9af8a4fd5.

### BSC Legal Catalan–Spanish

The BSC dataset card reports about 5.4 million parallel sentence pairs in `dogc_ca-es.tsv`, plus about 13,000 paragraph pairs and 450 parallel APDCAT documents (about 170,000 words per language). The matrix records the sentence-pair count on both language rows; it is a pair count, not two independent corpora to add together. Paragraphs and documents are separate native units and are not added to the sentence-pair count. The provider describes the content as authentic, non-synthetic, and deduplicated. Source: https://huggingface.co/datasets/BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus

### Icelandic Gigaword 2024 — Filtered-1

The CLARIN-IS record for the exact Filtered-1 artifact used by the project (handle 381) reports 794,816,184 words across filtered, deduplicated, normalized Icelandic documents. This is a word count, not a sentence or document count. A separate Filtered-2 artifact exists under handle 382 and must not be merged into Filtered-1 without checking overlap and licence scope. Source: https://repository.clarin.is/repository/xmlui/handle/20.500.12537/381

### GreynirCorpus 1.1

The CLARIN-IS repository metadata and the upstream project README independently describe GreynirCorpus 1.1 as **10 million Icelandic sentences**, approximately **110,893,504 tokens** in the repository record (the project README gives approximately 140 million words). The 5,000 hand-annotated trees are a subset/annotation layer, not additional sentences. The repository marks the corpus publicly available under CC BY 4.0. This is upstream capacity only; langid-32's previous zero staged records and pending project rights review are separate questions. Sources: https://repository.clarin.is/repository/xmlui/handle/20.500.12537/119 and https://github.com/mideind/GreynirCorpus

### Korean Wikipedia 2023-11-01

The pinned Wikimedia/Hugging Face `20231101.ko` split contains **647,897 article records** (provider split metadata rounds this to 647.9K). The dataset has one full cleaned article per row; this is an article count, not a sentence count. Sentence candidates require segmenting the full article text. The three Parquet shards total about 783 MB. License metadata lists CC BY-SA 3.0 and GFDL; preserve article/revision attribution and review imported-content exceptions. Sources: https://huggingface.co/datasets/wikimedia/wikipedia/tree/bef9a7e34c90b82f0a90ce374ae17c7c6873e314/20231101.ko and https://huggingface.co/datasets/wikimedia/wikipedia

### UN Parallel Corpus (UNPC)

The UN's official v1.0 statistics report **799,276 total documents**, **1,727,539 aligned document pairs**, and a fully aligned subcorpus of **86,307 documents / 11,365,709 aligned lines**. Pairwise statistics are published per language pair: each upper-triangle cell contains aligned document count and aligned line count; lower-triangle cells contain token counts for each language side. Pairwise lines must not be summed across the 15 language pairs because the same sentence/document can recur in several pair configurations. The source provides language-specific XML archives and parallel link files, enabling a proper monolingual extraction; exact unique sentence counts by language remain to be computed. Official source and attribution requirement: https://www.un.org/dgacm/en/content/uncorpus and https://www.un.org/dgacm/content/uncorpus/Download

### Tatoeba CC0 subset

The current official download page confirms that the CC0 export is a distinct subset of Tatoeba's larger CC BY 2.0 FR export. The CC0 locale list includes these project target languages: Arabic, Catalan, Czech, Danish, Dutch, English, Finnish, French, German, Hungarian, Italian, Japanese, Mandarin Chinese, Norwegian Bokmål, Polish, Portuguese, Russian, Spanish and Swedish. It does not list the other target languages. The matrix uses `—` only for those absent from the provider's published CC0 language list; counts for supported target languages remain TBD pending an actual count of the weekly CC0 archive. Source: https://tatoeba.org/en/downloads

### FineWeb English

The Hugging Face dataset page exposes 25.9 billion rows for the default FineWeb dataset and describes more than 18.5 trillion tokens. The row figure is retained as the provider's native record count; it is not a sentence count. Source: https://huggingface.co/datasets/HuggingFaceFW/fineweb

### TeMU-BSC Catalan CC0

The repository README explicitly reports 93,691 sentences in the filtered Catalan Government crawl file and 155,990 sentences in `datasets_sentences.tsv` from Projecte Aina. These two named files give a conservative identified minimum of 249,681 sentences. This is not a complete repository total: the repository contains further individual files, aggregate files overlap their constituents, and some contributions have separate permission/waiver terms. Do not add `new_catalan_cc0_corpus.txt` or `xitxat_toponyms.txt` on top of their constituent files. The number is a file-level identified minimum, not the final deduplicated unique count. Source: https://github.com/TeMU-BSC/catalan_CC0_sentences

### Målfrid 2026

The National Library of Norway reports provider token counts: Bokmål 1,890,232,881; English 570,099,658; Nynorsk 170,231,965. These remain tokens, not sentence counts. Source: https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026.pdf

## Next source-counting passes

1. Common Voice 22: provider `validatedSentences` figures have now been transcribed for cs, en, fr and ga; extract and verify all remaining target locales. Do not use the project's 9,000 cap.
2. FineWeb-2: filtered document counts have been transcribed for 30 target languages. Complete the missing Gaelic, Nynorsk and Maltese mapping; record removed-subset counts and word counts too. FineWeb English has 25.9B provider rows recorded separately.
3. Leipzig News and Wikipedia: per-language catalogue review confirms fixed-size tiers up to 1M for many News corpora and `All` archives for Wikipedia/News. Download pinned `All` archives and count exact `*_sentences.txt` rows; the 3k project cap remains irrelevant.
4. Tatoeba: CC0 language coverage is now mapped; count the weekly CC0 export by language code. Do not use the larger CC-BY export.
5. Målfrid, Icelandic Gigaword, Korean Wikipedia and GreynirCorpus: IGC2024 Filtered-1 provider word count (794,816,184) is recorded; count its documents and segment complete text. Korean Wikipedia has 647,897 article records; sentence segmentation remains. GreynirCorpus has 10M provider-reported sentences. Målfrid counts remain tokens, not sentence totals.
6. BSC Legal and TeMU-BSC: BSC Legal reports ~5.4M Catalan–Spanish sentence pairs plus separate paragraph/document units; verify exact row counts and rights. TeMU-BSC has a conservative identified minimum of 249,681 Catalan CC0 sentences from two explicitly counted files; enumerate the remaining files, rights and overlaps.
7. MultiUN and UNPC: UNPC official corpus-wide counts (799,276 documents; 1,727,539 aligned document pairs; 11,365,709 lines in the fully aligned subcorpus) are recorded. Count monolingual language sides, not pair-configuration row sums; deduplicate within each corpus and compare document identifiers between corpora.
8. GreynirCorpus: upstream size is 10M Icelandic sentences (~110.9M tokens in CLARIN metadata); CC BY 4.0. Project use remains subject to the separate rights/approval decision.

No source's previous langid-32 sample cap or staged count is admissible as an upstream availability count.
