# FineWeb (English)

**Text unit:** Web documents / extracted text  
**Primary source:** https://huggingface.co/datasets/HuggingFaceFW/fineweb

## Creator and origin

Hugging Face FineWeb team; Common Crawl pages processed with DataTrove.

## Access methods

Hugging Face Hub; Parquet/streaming via datasets, Hub downloads or HF CLI.

## File types and structure

Parquet records with text, ID, dump, URL, date, file path, language, score and token count.

## Distribution conditions and rights

ODC-By 1.0 plus Common Crawl terms; underlying page rights need review.

## Content and language coverage

English web text from Common Crawl since 2013; card reports >18.5T tokens.

## Current langid-32 acquisition snapshot

5,968 staged English records only; our sample, not FineWeb availability; records are documents.

| Language | Current staged records |
|---|---:|
| en | 5,968 |

**Current staged total:** 5,968 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Pin exact upstream release/version, retrieval date and immutable identifier.
- Count full upstream records by language in the source's native unit, independently of project sampling.
- Record raw, eligible-after-source-filters and project-selected counts separately.
- Verify file-level rights and redistribution conditions before public release.
