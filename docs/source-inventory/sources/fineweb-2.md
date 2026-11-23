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

## Full per-language upstream document counts

The provider's complete fineweb2-language-distribution.csv (GitHub blob SHA 24e400385ad45ebf477bb2dc49e502d9af8a4fd5) has one row per language-script subset and split. This table aggregates all scripts mapped to each target language. **Total available documents** = filtered train + filtered test + removed train. The provider states that filtered plus removed reconstructs the full globally deduplicated language pool. The removed rows do not report word counts; therefore the word column below covers only filtered train + test. These remain document/word measures, never sentence counts.

| Language | Filtered train documents | Filtered test documents | Removed train documents | Total available documents | Filtered words (train + test) |
|---|---:|---:|---:|---:|---:|
| bg | 25,994,731 | 36,933 | 41,123,060 | 67,154,724 | 16,097,217,729 |
| hr | 6,195,824 | 9,248 | 54,157,365 | 60,362,437 | 6,619,122,430 |
| cs | 66,067,904 | 28,051 | 173,004,746 | 239,100,701 | 35,494,489,638 |
| da | 45,391,655 | 27,945 | 102,791,820 | 148,211,420 | 28,073,298,751 |
| nl | 147,301,270 | 33,283 | 308,913,360 | 456,247,913 | 74,651,199,348 |
| et | 10,218,587 | 25,786 | 29,308,204 | 39,552,577 | 6,580,544,367 |
| fi | 36,710,816 | 30,398 | 78,978,641 | 115,719,855 | 20,359,774,956 |
| fr | 360,058,973 | 44,245 | 596,844,583 | 956,947,801 | 220,689,378,295 |
| de | 495,964,485 | 65,176 | 558,814,393 | 1,054,844,054 | 262,305,627,266 |
| el | 47,421,073 | 32,936 | 97,358,213 | 144,812,222 | 22,844,004,778 |
| hu | 49,935,986 | 34,779 | 92,953,013 | 142,923,778 | 30,941,313,384 |
| ga | 646,842 | 6,881 | 2,058,553 | 2,712,276 | 419,596,485 |
| it | 238,984,437 | 41,029 | 301,144,649 | 540,170,115 | 139,140,142,697 |
| lv | 8,030,316 | 22,185 | 26,626,345 | 34,678,846 | 5,386,290,626 |
| lt | 13,471,965 | 27,694 | 32,411,196 | 45,910,855 | 9,151,439,320 |
| mt | 489,190 | 5,193 | 9,634,147 | 10,128,530 | 289,642,511 |
| pl | 151,966,724 | 36,574 | 300,919,585 | 452,922,883 | 73,137,196,876 |
| pt | 199,737,979 | 33,846 | 417,908,539 | 617,680,364 | 109,554,931,079 |
| ro | 58,305,577 | 45,800 | 80,246,038 | 138,597,415 | 35,048,022,260 |
| sk | 29,991,521 | 32,557 | 61,993,626 | 92,017,704 | 14,824,219,235 |
| sl | 12,059,130 | 32,447 | 24,025,208 | 36,116,785 | 7,709,635,936 |
| es | 441,287,261 | 40,970 | 638,414,763 | 1,079,742,994 | 261,547,491,469 |
| sv | 59,485,306 | 24,692 | 152,608,135 | 212,118,133 | 35,760,957,009 |
| nb | 38,144,343 | 43,396 | 50,578,775 | 88,766,514 | 32,045,225,370 |
| nn | 1,214,870 | 12,227 | 9,502,099 | 10,729,196 | 528,126,159 |
| ru | 699,083,579 | 34,714 | 1,319,563,371 | 2,018,681,664 | 588,610,006,686 |
| ja | 400,138,563 | 25,889 | 874,205,291 | 1,274,369,743 | 331,166,236,817 |
| zh | 636,058,984 | 33,296 | 849,717,131 | 1,485,809,411 | 543,571,389,611 |
| ko | 60,874,355 | 30,074 | 136,937,698 | 197,842,127 | 48,637,229,978 |
| ar | 61,979,490 | 42,095 | 92,108,521 | 154,130,106 | 32,837,139,175 |
| tr | 95,129,129 | 36,146 | 165,382,292 | 260,547,567 | 41,949,670,257 |
| ca | 17,136,414 | 37,517 | 27,844,826 | 45,018,757 | 8,366,625,285 |
| is | 3,014,429 | 32,586 | 5,302,361 | 8,349,376 | 1,714,501,973 |

English is absent from FineWeb-2 by design and is supplied separately by FineWeb. The Romanian total combines ron_Latn and ron_Cyrl; the Arabic total combines arb_Arab and arb_Latn. The CSV also resolves the formerly unmeasured Irish and Maltese counts. Source: https://github.com/huggingface/fineweb-2/blob/main/fineweb2-language-distribution.csv and https://huggingface.co/datasets/HuggingFaceFW/fineweb-2

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
