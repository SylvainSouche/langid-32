# Common Voice 22.0 (HF conversion)

**Text unit:** Validated prompted sentences  
**Primary source:** https://huggingface.co/datasets/fsicoli/common_voice_22_0

## Creator and origin

Mozilla Foundation and Common Voice contributors; fsicoli Hugging Face conversion.

## Access methods

Hugging Face Hub/direct HTTPS; transcript/<locale>/validated_sentences.tsv; downloader pins revision and hashes files; TSV only, no audio.

## File types and structure

UTF-8 TSV: sentence_id, sentence, validation/use metadata; project adds source_locale.

## Distribution conditions and rights

HF card declares CC0-1.0 for this conversion. Do not conflate with other releases or Mozilla Data Collective agreements. No audio, speaker IDs or demographics.

## Content and language coverage

Crowd-contributed read prompts/transcripts; project locale map supports target languages except Croatian; zh-CN and zh-TW combined.

## Current langid-32 acquisition snapshot

9,000/language hard curator cap, followed by text/privacy filtering and deduplication. These are our sample counts, not upstream totals.

| Language | Current staged records |
|---|---:|
| bg | 9,000 |
| cs | 9,000 |
| da | 9,000 |
| nl | 9,000 |
| en | 9,000 |
| et | 9,000 |
| fi | 5,798 |
| fr | 9,000 |
| de | 9,000 |
| el | 6,625 |
| hu | 9,000 |
| ga | 1,450 |
| it | 9,000 |
| lv | 9,000 |
| lt | 9,000 |
| mt | 5,222 |
| pl | 9,000 |
| pt | 9,000 |
| ro | 9,000 |
| sk | 9,000 |
| sl | 4,061 |
| es | 9,000 |
| sv | 9,000 |
| nb | 3,768 |
| nn | 5,179 |
| ru | 9,000 |
| ja | 9,000 |
| zh | 9,000 |
| ko | 6,258 |
| ar | 9,000 |
| tr | 9,000 |
| ca | 9,000 |
| is | 4,991 |

**Current staged total:** 259,352 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Pin exact upstream release/version, retrieval date and immutable identifier.
- Count full upstream records by language in the source's native unit, independently of project sampling.
- Record raw, eligible-after-source-filters and project-selected counts separately.
- Verify file-level rights and redistribution conditions before public release.
