# FineWeb-2

**Text unit:** Web documents / extracted text  
**Primary source:** https://huggingface.co/datasets/HuggingFaceFW/fineweb-2

## Creator and origin

Hugging Face FineWeb team; Common Crawl snapshots processed with DataTrove.

## Access methods

Hugging Face Hub streaming or Parquet downloads; project streams selected language-script configs with pinned revision.

## File types and structure

Parquet-backed records: text, IDs, URL, date, dump and language metadata.

## Distribution conditions and rights

ODC-By 1.0 dataset licence; underlying Common Crawl page rights/terms remain unresolved. Project release hold applies.

## Content and language coverage

Multilingual web crawl; card describes 96 snapshots, ~20 TB, 5B documents, >3T words, 1,868 language-script pairs.

## Upstream availability (independent of project acquisition)

The provider publishes per-language/script counts for its filtered subsets. The target-language document counts transcribed from that table are maintained in [the upstream availability matrix](../availability-matrix.md). They are provider document counts, **not sentence counts**. The dataset also publishes removed subsets separately; the filtered and removed subsets together represent the full globally deduplicated data for each language. English is intentionally distributed in the separate FineWeb dataset.

## Provider-reported filtered-subset counts

The current dataset card's **Languages and available subsets** table reports both word-tokenizer counts and document counts for the largest language-script subsets. The following target-language rows were transcribed from that table. These are the provider's *filtered* subset figures only; the card says the corresponding _removed subset must be added to recover the full globally deduplicated pool. The word counts are not model-tokenizer counts and are not sentence counts.

| Target language | Provider subset | Words | Documents |
|---|---|---:|---:|
| bg | bul_Cyrl | 16,074,326,712 | 25,994,731 |
| hr | hrv_Latn | 6,609,299,440 | 6,195,824 |
| cs | ces_Latn | 35,479,428,809 | 66,067,904 |
| da | dan_Latn | 28,055,948,840 | 45,391,655 |
| nl | nld_Latn | 74,634,633,118 | 147,301,270 |
| et | ekk_Latn | 6,564,292,000 | 10,218,587 |
| fi | fin_Latn | 20,343,096,672 | 36,710,816 |
| fr | fra_Latn | 220,662,584,640 | 360,058,973 |
| de | deu_Latn | 262,271,052,199 | 495,964,485 |
| el | ell_Grek | 22,827,957,288 | 47,421,073 |
| hu | hun_Latn | 30,919,839,164 | 49,935,986 |
| it | ita_Latn | 139,116,026,491 | 238,984,437 |
| lv | lvs_Latn | 5,371,151,279 | 8,030,316 |
| lt | lit_Latn | 9,132,828,961 | 13,471,965 |
| pl | pol_Latn | 73,119,437,217 | 151,966,724 |
| pt | por_Latn | 109,536,087,117 | 199,737,979 |
| ro | ron_Latn | 35,017,893,659 | 58,303,671 |
| sk | slk_Latn | 14,808,010,769 | 29,991,521 |
| sl | slv_Latn | 7,688,373,264 | 12,059,130 |
| es | spa_Latn | 261,523,749,595 | 441,287,261 |
| sv | swe_Latn | 35,745,969,364 | 59,485,306 |
| nb | nob_Latn | 32,008,904,934 | 38,144,343 |
| nn | nno_Latn | 522,740,774 | 1,214,870 |
| ru | rus_Cyrl | 588,579,493,780 | 699,083,579 |
| ja | jpn_Jpan | 331,144,301,801 | 400,138,563 |
| zh | cmn_Hani | 543,543,038,750 | 636,058,984 |
| ko | kor_Hang | 48,613,120,582 | 60,874,355 |
| ar | arb_Arab | 32,812,858,120 | 61,977,525 |
| tr | tur_Latn | 41,933,799,420 | 95,129,129 |
| ca | cat_Latn | 8,348,091,726 | 17,136,414 |
| is | isl_Latn | 1,696,354,360 | 3,014,429 |

The card's top-80 table does not contain a target row for Irish (gle) or Maltese (mlt); absence from this truncated table is not proof of zero or lack of a configuration. Their filtered and removed counts still require inspection of the complete provider distribution CSV and repository files. The card also states that English is distributed separately in FineWeb, not FineWeb-2. Source: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2

## Current langid-32 acquisition snapshot

610,702 staged records. Most per-language counts are stream/sampler caps (~10–20k); Catalan and Icelandic 50k. Not upstream availability; held.

| Language | Current staged records |
|---|---:|
| bg | 16,001 |
| hr | 16,013 |
| cs | 15,996 |
| da | 16,013 |
| nl | 15,940 |
| et | 16,002 |
| fi | 15,077 |
| fr | 10,251 |
| de | 15,970 |
| el | 16,081 |
| hu | 15,992 |
| ga | 16,024 |
| it | 15,963 |
| lv | 15,990 |
| lt | 16,054 |
| mt | 16,011 |
| pl | 15,964 |
| pt | 16,021 |
| ro | 16,002 |
| sk | 15,999 |
| sl | 16,007 |
| es | 16,033 |
| sv | 15,889 |
| nb | 19,996 |
| nn | 20,000 |
| ru | 9,418 |
| ja | 19,998 |
| zh | 19,999 |
| ko | 20,000 |
| ar | 19,998 |
| tr | 20,000 |
| ca | 50,000 |
| is | 50,000 |

**Current staged total:** 610,702 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Pin exact upstream release/version, retrieval date and immutable identifier.
- Count full upstream records by language in the source's native unit, independently of project sampling.
- Record raw, eligible-after-source-filters and project-selected counts separately.
- Verify file-level rights and redistribution conditions before public release.
