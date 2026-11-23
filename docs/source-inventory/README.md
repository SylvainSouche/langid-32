# langid-32 source inventory — current staged-volume synthesis

**Snapshot:** 2026-11-23  
**Target languages:** 34  
**Current staged source records:** 1,713,852

## Scope and interpretation

This directory separates source discovery from acquisition and quality selection. Each source has an individual Markdown file documenting creator, origin, access, distribution format, licence/conditions, language coverage and current project counts.

**1,713,852 is the sum of records currently staged by our pipeline, not the number of unique sentences available upstream.** Several values are our own caps: Common Voice 9,000/language; DGT-TM 5,000/language; Leipzig 3,000/language; Målfrid 50,000/language; IGC and Korean Wikipedia 50,000. Other values are partial acquisitions. Sources have mixed units: sentences, translation segments, paragraphs, examples and documents. Duplicates can exist between sources. Do not describe this total as 1,713,852 unique sentences or as full upstream availability.

Full upstream availability remains unknown for most sources. Words, tokens or document counts published by providers are recorded in source files but are not added to sentence counts.

## Current staged records by language

| Language | Current staged records |
|---|---:|
| bg | 36,001 |
| hr | 27,013 |
| cs | 36,000 |
| da | 36,046 |
| nl | 35,989 |
| en | 67,198 |
| et | 36,002 |
| fi | 33,420 |
| fr | 44,433 |
| de | 36,015 |
| el | 33,706 |
| hu | 35,993 |
| ga | 28,474 |
| it | 35,982 |
| lv | 35,990 |
| lt | 36,054 |
| mt | 32,233 |
| pl | 36,021 |
| pt | 36,037 |
| ro | 36,002 |
| sk | 35,999 |
| sl | 31,068 |
| es | 36,069 |
| sv | 36,097 |
| nb | 79,768 |
| nn | 78,179 |
| ru | 47,139 |
| ja | 35,000 |
| zh | 35,000 |
| ko | 82,258 |
| ar | 35,000 |
| tr | 35,000 |
| ca | 301,675 |
| is | 110,991 |
| **TOTAL** | **1,713,852** |

## Current staged records by source

| Source | Current staged records | Native unit |
|---|---:|---|
| [Common Voice 22.0 (HF conversion)](sources/common-voice-22.md) | 259,352 | Validated prompted sentences |
| [European Commission DGT Translation Memory 2021](sources/dgt-tm-2021.md) | 120,000 | Translation units / segment pairs |
| [FineWeb-2](sources/fineweb-2.md) | 610,702 | Web documents / extracted text |
| [Leipzig Corpora Collection — News](sources/leipzig-news.md) | 99,000 | Sentences from news text |
| [Leipzig Corpora Collection — Wikipedia](sources/leipzig-wikipedia.md) | 102,000 | Sentences from Wikipedia articles |
| [Tatoeba — CC0 subset](sources/tatoeba-cc0.md) | 80,155 | Individual sentences |
| [FineWeb (English)](sources/fineweb-english.md) | 5,968 | Web documents / extracted text |
| [Målfrid 2026 — Norwegian state institutions](sources/maalfrid-2026.md) | 100,000 | Documents / text records |
| [Icelandic Gigaword Corpus 2024 — Filtered-1](sources/icelandic-gigaword-2024.md) | 50,000 | Documents / JSONL text |
| [Korean Wikipedia 2023-11-01](sources/korean-wikipedia.md) | 50,000 | Article paragraphs / text segments |
| [BSC Legal Catalan–Spanish Parallel Corpus](sources/bsc-legal-catalan-spanish.md) | 62,518 | Sentence pairs, paragraphs and documents |
| [TeMU-BSC — Catalan CC0 collection](sources/temu-catalan-cc0.md) | 174,157 | Sentences / generated examples (mixed) |
| **TOTAL** | **1,713,852** | **Mixed units; not unique sentences** |

## Individual source files

- [Common Voice 22.0 (HF conversion)](sources/common-voice-22.md)
- [European Commission DGT Translation Memory 2021](sources/dgt-tm-2021.md)
- [FineWeb-2](sources/fineweb-2.md)
- [Leipzig Corpora Collection — News](sources/leipzig-news.md)
- [Leipzig Corpora Collection — Wikipedia](sources/leipzig-wikipedia.md)
- [Tatoeba — CC0 subset](sources/tatoeba-cc0.md)
- [FineWeb (English)](sources/fineweb-english.md)
- [Målfrid 2026 — Norwegian state institutions](sources/maalfrid-2026.md)
- [Icelandic Gigaword Corpus 2024 — Filtered-1](sources/icelandic-gigaword-2024.md)
- [Korean Wikipedia 2023-11-01](sources/korean-wikipedia.md)
- [BSC Legal Catalan–Spanish Parallel Corpus](sources/bsc-legal-catalan-spanish.md)
- [TeMU-BSC — Catalan CC0 collection](sources/temu-catalan-cc0.md)
- [MultiUN — multilingual UN documents](sources/multiun.md)
- [UN Arabic-English Filtered — combined derivative](sources/un-arabic-english-filtered.md)
- [GreynirCorpus 1.1 — excluded](sources/greynir-corpus.md)

## Full language/source matrix — current staged inventory

Counts are reconstructed from candidate manifest field preselection.bucket_rows_seen. They represent records entering preselection, not upstream totals. Some source samplers apply their own caps before these values are recorded.

| Language | cv | dgt | fw2 | news | wiki | tatoeba | fineweb | maal | igc | kwiki | bsc | temu | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bg | 9,000 | 5,000 | 16,001 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 36,001 |
| hr | 0 | 5,000 | 16,013 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 27,013 |
| cs | 9,000 | 5,000 | 15,996 | 3,000 | 3,000 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 36,000 |
| da | 9,000 | 5,000 | 16,013 | 3,000 | 3,000 | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 36,046 |
| nl | 9,000 | 5,000 | 15,940 | 3,000 | 3,000 | 49 | 0 | 0 | 0 | 0 | 0 | 0 | 35,989 |
| en | 9,000 | 5,000 | 0 | 3,000 | 3,000 | 41,230 | 5,968 | 0 | 0 | 0 | 0 | 0 | 67,198 |
| et | 9,000 | 5,000 | 16,002 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 36,002 |
| fi | 5,798 | 5,000 | 15,077 | 3,000 | 3,000 | 1,545 | 0 | 0 | 0 | 0 | 0 | 0 | 33,420 |
| fr | 9,000 | 5,000 | 10,251 | 3,000 | 3,000 | 14,182 | 0 | 0 | 0 | 0 | 0 | 0 | 44,433 |
| de | 9,000 | 5,000 | 15,970 | 3,000 | 3,000 | 45 | 0 | 0 | 0 | 0 | 0 | 0 | 36,015 |
| el | 6,625 | 5,000 | 16,081 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 33,706 |
| hu | 9,000 | 5,000 | 15,992 | 3,000 | 3,000 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 35,993 |
| ga | 1,450 | 5,000 | 16,024 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 28,474 |
| it | 9,000 | 5,000 | 15,963 | 3,000 | 3,000 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 35,982 |
| lv | 9,000 | 5,000 | 15,990 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 35,990 |
| lt | 9,000 | 5,000 | 16,054 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 36,054 |
| mt | 5,222 | 5,000 | 16,011 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 32,233 |
| pl | 9,000 | 5,000 | 15,964 | 3,000 | 3,000 | 57 | 0 | 0 | 0 | 0 | 0 | 0 | 36,021 |
| pt | 9,000 | 5,000 | 16,021 | 3,000 | 3,000 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 36,037 |
| ro | 9,000 | 5,000 | 16,002 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 36,002 |
| sk | 9,000 | 5,000 | 15,999 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 35,999 |
| sl | 4,061 | 5,000 | 16,007 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31,068 |
| es | 9,000 | 5,000 | 16,033 | 3,000 | 3,000 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 36,069 |
| sv | 9,000 | 5,000 | 15,889 | 3,000 | 3,000 | 208 | 0 | 0 | 0 | 0 | 0 | 0 | 36,097 |
| nb | 3,768 | 0 | 19,996 | 3,000 | 3,000 | 4 | 0 | 50,000 | 0 | 0 | 0 | 0 | 79,768 |
| nn | 5,179 | 0 | 20,000 | 0 | 3,000 | 0 | 0 | 50,000 | 0 | 0 | 0 | 0 | 78,179 |
| ru | 9,000 | 0 | 9,418 | 3,000 | 3,000 | 22,721 | 0 | 0 | 0 | 0 | 0 | 0 | 47,139 |
| ja | 9,000 | 0 | 19,998 | 3,000 | 3,000 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 35,000 |
| zh | 9,000 | 0 | 19,999 | 3,000 | 3,000 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 35,000 |
| ko | 6,258 | 0 | 20,000 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 50,000 | 0 | 0 | 82,258 |
| ar | 9,000 | 0 | 19,998 | 3,000 | 3,000 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 35,000 |
| tr | 9,000 | 0 | 20,000 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 35,000 |
| ca | 9,000 | 0 | 50,000 | 3,000 | 3,000 | 0 | 0 | 0 | 0 | 0 | 62,518 | 174,157 | 301,675 |
| is | 4,991 | 0 | 50,000 | 3,000 | 3,000 | 0 | 0 | 0 | 50,000 | 0 | 0 | 0 | 110,991 |

## Rights status

- FineWeb-2: held pending review of underlying Common Crawl text rights; ODC-By 1.0 is not treated as clearance.
- Målfrid 2026: held pending database and third-party content review.
- IGC2024 Filtered-1: repository describes CC-BY material; project hold remains pending source-rights/licence-scope review.
- Korean Wikipedia: held pending attribution, share-alike and imported-content review.
- BSC Legal: held pending file-level/source-article rights verification.
- FineWeb English: ODC-By 1.0 plus Common Crawl terms; underlying page rights need review.
- Tatoeba: only explicit CC0 export counted; general sentences are CC BY 2.0 FR.
- TeMU-BSC: verify each file's waiver and source terms; repository name does not establish blanket CC0 status.
- MultiUN: separate multilingual source entry; published corpus-scale statistics indicate substantial availability in six official UN languages plus a smaller German component. The paper documents its public-domain rationale under ST/AI/189/Add.9/Rev.2; retain UN attribution and verify exceptions. Current direct project acquisition: zero.
- UN Arabic-English Filtered: combined MultiUN + UNPC derivative; 19,296,911 aligned pairs reported by the HF dataset viewer, but this is not an upstream count for either source. Keep the derivative separate and avoid double-counting.
- GreynirCorpus: excluded by current project rule; zero staged records.

## Remaining work in this inventory stage

1. Retrieve authoritative upstream catalogues/manifests for every source and record exact release, version, date and stable identifier.
2. Count full upstream records by language in each source's native unit: sentences, translation units, paragraphs, documents, words or tokens.
3. Count complete files or query provider APIs/catalogues where possible; distinguish exact counts, estimates and project caps.
4. Record raw upstream, eligible-after-source-filters and project-selected counts separately.
5. Verify file-level licences and redistribution conditions; mark sources cleared, conditional, held or excluded.
6. Only after this inventory is complete, design acquisition expansion. No JQL scoring or final selection is part of this stage.

## Count provenance

Reconstructed from candidate build run [45080282140](https://github.com/SylvainSouche/langid-32/actions/runs/45080282140), artifact [14779301721](https://github.com/SylvainSouche/langid-32/actions/runs/45080282140/artifacts/14779301721), using preselection.bucket_rows_seen. This field counts rows entering preselection, not the final unique corpus. Inventory dated 2026-11-23; refresh when source revisions or acquisition manifests change.
