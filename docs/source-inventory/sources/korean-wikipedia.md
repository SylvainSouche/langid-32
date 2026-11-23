# Korean Wikipedia 2023-11-01

**Text unit:** Article paragraphs / text segments  
**Primary source:** https://huggingface.co/datasets/wikimedia/wikipedia

## Creator and origin

Wikimedia Foundation and Wikipedia contributors; HF wikimedia/wikipedia conversion.

## Access methods

HF datasets streaming config 20231101.ko, pinned revision; original Wikimedia dumps are XML.

## File types and structure

Article records with page ID, URL, title, text; project splits text into paragraph/sentence-like segments.

## Distribution conditions and rights

CC BY-SA and GFDL; imported-content exceptions and revision attribution. Held pending share-alike/attribution review.

## Content and language coverage

Korean Wikipedia articles from 2023-11-01 snapshot.

## Verified upstream availability (independent of project acquisition)

The pinned Wikimedia/Hugging Face `20231101.ko` split contains **647,897 article records** (the Hub structure table rounds this to 647.9K). Each row is one cleaned article with `id`, `url`, `title` and `text`; the article count is not a sentence count. The three Parquet shards total about 783 MB. The dataset metadata lists CC BY-SA 3.0 and GFDL; preserve attribution and review imported-content exceptions. Sentence candidates must be counted by segmenting the full article text. Sources: https://huggingface.co/datasets/wikimedia/wikipedia/tree/bef9a7e34c90b82f0a90ce374ae17c7c6873e314/20231101.ko and https://huggingface.co/datasets/wikimedia/wikipedia

## Current langid-32 acquisition snapshot

50,000 staged Korean segments, sampler ceiling, not total articles/paragraphs; held.

| Language | Current staged records |
|---|---:|
| ko | 50,000 |

**Current staged total:** 50,000 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Pin the Parquet file hashes and verify the exact row count from all three shards (the Hub structure table currently rounds it to 647.9K).
- Segment the full `text` field with a fixed sentence splitter and report raw/unique sentence counts separately.
- Preserve article IDs/URLs for attribution and audit imported-content exclusions under CC BY-SA/GFDL.
