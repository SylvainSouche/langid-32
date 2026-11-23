# European Commission DGT Translation Memory 2021

**Text unit:** Translation units (TU), not guaranteed to be complete sentences  
**Primary source:** https://joint-research-centre.ec.europa.eu/language-technology-resources/dgt-translation-memory_en  
**Statistics source:** https://wt-public.emm4u.eu/Resources/DGT-TM_Statistics.pdf

## Creator and origin

Directorate-General for Translation, European Commission; Acquis Communautaire and other EU institutional texts extracted from EURAMIS. The official JRC description says the memory contains most, but not all, Acquis documents and some other documents.

## Access methods and format

Official JRC page; DGT-TM 2021 release consists of five ZIP volumes (Vol_2020_1…5; 583 MB total) plus the TMXtract Java extractor. All five volumes are needed for the complete release. TMX files use UTF-16LE. Each TU is a segment and may be a sentence or part of a sentence.

## Distribution conditions and rights

The European Commission grants worldwide, royalty-free, non-exclusive reuse under Commission Decision 2011/833/EU. Re-users must identify the source, give the website address and latest update date, and state that the European Commission retains ownership.

## Language coverage

24 EU official languages: bg, hr, cs, da, nl, en, et, fi, fr, de, el, hu, ga, it, lv, lt, mt, pl, pt, ro, sk, sl, es, sv. Irish has very little data; Croatian has less than older EU languages. The official page warns that TUs can be sentences or sentence fragments.

## Upstream availability — independent of langid-32 sampling

The JRC's DGT-TM statistics workbook/PDF reports counts by language and release. The latest column in the published statistics is DGT-TM 2020 (distributed as DGT-TM 2021). The figures below are **cumulative TUs including the 2007 baseline**, not the 5,000-per-language project sample.

| Language | Cumulative TUs through DGT-TM 2020 |
|---|---:|
| bg | 4,602,085 |
| hr | 2,554,319 |
| cs | 6,410,466 |
| da | 5,935,254 |
| nl | 5,873,514 |
| en | 8,624,934 |
| et | 6,450,667 |
| fi | 5,933,745 |
| fr | 6,397,822 |
| de | 5,958,872 |
| el | 5,782,498 |
| hu | 6,559,000 |
| ga | 235,384 |
| it | 5,967,350 |
| lv | 6,504,918 |
| lt | 6,501,706 |
| mt | 4,830,614 |
| pl | 6,463,748 |
| pt | 6,390,501 |
| ro | 4,520,726 |
| sk | 6,505,108 |
| sl | 6,472,554 |
| es | 5,965,669 |
| sv | 6,025,986 |

These are source-level TU availability figures, not unique candidate sentences. A TU may be a fragment; repeated boilerplate (for example, “Article 1”) is present; and the source notes that redundancies are inevitable. The project must count actual extracted language-side records and then sentence-eligible candidates after its own text filters. Do not substitute the 5,000-per-language acquisition cap for these upstream figures.

## Current project acquisition (separate measure)

The previous langid-32 build staged 5,000 records per DGT-covered language (120,000 total). This is solely a historical project sample and is **not** the source availability figure above. It must not be used in the source-availability matrix.

## Counting interpretation and remaining checks

- The official statistics report per-language TU counts across releases. They are not counts of unique sentences.
- For the 2021 release, use the five 2020 volumes together and preserve the EUR-Lex NumDoc identifier.
- To obtain exact eligible sentence counts, extract each language side, normalize and segment consistently, then report raw TUs, non-empty text segments, sentence-segmented candidates, and unique candidates separately.
- Record the retrieval revision/date and hashes for all five volumes.
