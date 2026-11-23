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

## Verified upstream availability (independent of project acquisition)

The pinned Hugging Face conversion includes `release_stats.py`, with provider-reported per-locale `validatedSentences` counts. The following have been transcribed and mapped to project language labels so far:

| Language | Locale | Validated sentences |
|---|---|---:|
| cs | cs | 451,100 |
| en | en | 1,680,014 |
| fr | fr | 1,648,822 |
| ga | ga-IE | 1,675 |

These are sentence counts, not audio-clip counts or project-selected records. The complete per-locale table is not yet transcribed; all other target-language cells remain unmeasured, not zero. Source file at pinned revision: https://huggingface.co/datasets/fsicoli/common_voice_22_0/blob/0ca7c0e9cf2c25897c13aa73c54003d8d6d1cf28/release_stats.py

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

- Extract all remaining target locales from the pinned `release_stats.py` and verify locale-to-language mapping, including zh-CN/zh-TW and nb/nn variants.
- Reconcile provider `validatedSentences` counts with actual sentence TSVs at the same immutable revision.
- Keep provider counts, downloaded rows, project-filtered candidates and globally deduplicated sentences separate.
- Reconfirm the CC0 declaration applies to this text-only conversion and retain its revision/hash.
