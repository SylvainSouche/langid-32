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

## Verified upstream availability (independent of project acquisition)

The current Hugging Face dataset page reports approximately **25.9 billion rows** for the default dataset view and describes the corpus as containing more than **18.5 trillion tokens**. The row count is the provider's dataset-viewer record count, not a count of sentences. Sentence candidates require segmentation of the complete text field; do not infer them by multiplying the row count by an assumed average. Source: https://huggingface.co/datasets/HuggingFaceFW/fineweb

## Current langid-32 acquisition snapshot

5,968 staged English records only; our sample, not FineWeb availability; records are documents.

| Language | Current staged records |
|---|---:|
| en | 5,968 |

**Current staged total:** 5,968 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Pin an immutable dataset revision and record the exact dataset-viewer/API snapshot date.
- Verify the approximate 25.9B row count against the pinned Parquet manifest/shard metadata.
- Obtain complete token/word counts and segment the complete text field to measure sentence candidates.
- Keep underlying Common Crawl text rights separate from the ODC-By dataset/compilation terms.
