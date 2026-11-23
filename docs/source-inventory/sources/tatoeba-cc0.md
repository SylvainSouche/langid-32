# Tatoeba — CC0 subset

**Text unit:** Individual sentences  
**Primary source:** https://tatoeba.org/en/downloads

## Creator and origin

Tatoeba community; user-contributed multilingual example sentences and translations.

## Access methods

Official weekly export (Saturday 06:30 UTC); separate CC0 export; custom exports also available.

## File types and structure

TAR.BZ2; tab-separated sentence ID, language code, text, modified date; translation links separate.

## Distribution conditions and rights

General sentence export is CC BY 2.0 FR; only subset is CC0 1.0. Project uses CC0 file only. Audio has separate contributor licences and is not used.

## Content and language coverage

Broad community language coverage; CC0 subset is smaller than full Tatoeba.

## Verified upstream availability and language coverage

The official downloads page confirms a separate `sentences_CC0` weekly export (updated Saturdays at 06:30 UTC), distinct from the general CC BY 2.0 FR sentence export. The CC0 export's published locale list includes these langid-32 target languages:

`ar`, `ca`, `cs`, `da`, `de`, `en`, `es`, `fi`, `fr`, `hu`, `it`, `ja`, `nb`, `nl`, `pl`, `pt`, `ru`, `sv`, `zh` (Mandarin Chinese).

The following target languages are not listed in the current CC0 locale catalogue: `bg`, `hr`, `et`, `el`, `ga`, `lv`, `lt`, `mt`, `ro`, `sk`, `sl`, `nn`, `ko`, `tr`, `is`. These are out of scope for this CC0-only source, not zero counts in Tatoeba generally. Exact sentence counts for the supported target languages remain unmeasured until the weekly CC0 archive is parsed; do not substitute project staged counts. Source: https://tatoeba.org/en/downloads

## Current langid-32 acquisition snapshot

80,155 staged CC0 records; larger samples in English, French and Russian. Current export sample, not full CC0 availability.

| Language | Current staged records |
|---|---:|
| cs | 4 |
| da | 33 |
| nl | 49 |
| en | 41,230 |
| fi | 1,545 |
| fr | 14,182 |
| de | 45 |
| hu | 1 |
| it | 19 |
| pl | 57 |
| pt | 16 |
| es | 36 |
| sv | 208 |
| nb | 4 |
| ru | 22,721 |
| ja | 2 |
| zh | 1 |
| ar | 2 |

**Current staged total:** 80,155 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Parse the official weekly `sentences_CC0.tar.bz2` export and count records by ISO 639-3 language code for all 19 supported target languages.
- Record export timestamp, archive checksum, exact counts and unique sentence-ID counts.
- Map Mandarin Chinese and Norwegian Bokmål codes explicitly; do not merge Norwegian Nynorsk into Bokmål.
- Keep the CC0-only export separate from general CC BY 2.0 FR exports and audio licensing.
