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
