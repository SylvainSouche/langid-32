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

## Live general-catalogue sentence totals (all licences; not the CC0 export)

On 2026-11-23, the public Tatoeba statistics page reported **13,685,619 sentences** across all languages. The table below records the current total sentence count for each of the 34 langid-32 target languages. These are live catalogue counts across licence types, not counts from the separate `sentences_CC0` export. They are useful as an upper bound on the Tatoeba pool, but they do not establish CC0 availability or permission to use the sentences under the project's CC0-only source decision.

| Target language | Tatoeba code | All-licence sentences |
|---|---|---:|
| Arabic | ara | 68,968 |
| Bulgarian | bul | 25,725 |
| Catalan | cat | 11,016 |
| Czech | ces | 90,266 |
| Danish | dan | 66,569 |
| German | deu | 787,848 |
| Greek | ell | 43,301 |
| English | eng | 2,050,243 |
| Spanish | spa | 446,423 |
| Estonian | est | 6,556 |
| Finnish | fin | 155,051 |
| French | fra | 738,333 |
| Irish | gle | 3,103 |
| Croatian | hrv | 6,587 |
| Hungarian | hun | 445,782 |
| Icelandic | isl | 13,396 |
| Italian | ita | 995,850 |
| Japanese | jpn | 249,285 |
| Korean | kor | 16,027 |
| Lithuanian | lit | 159,902 |
| Latvian | lvs | 20,730 |
| Maltese | mlt | 699 |
| Norwegian Bokmål | nob | 18,904 |
| Dutch | nld | 201,710 |
| Norwegian Nynorsk | nno | 12,495 |
| Polish | pol | 137,255 |
| Portuguese | por | 446,190 |
| Romanian | ron | 42,136 |
| Russian | rus | 1,240,726 |
| Slovak | slk | 33,392 |
| Slovenian | slv | 3,614 |
| Swedish | swe | 57,517 |
| Turkish | tur | 750,704 |
| Mandarin Chinese | cmn | 89,428 |

The statistics page is a snapshot and will change as community members add, remove or relabel sentences. It reports all sentence records by language, not necessarily only correct sentences, and not distinct sentence texts. It must not be substituted for a count of the CC0 weekly export. Source: https://tatoeba.org/en/stats/sentences_by_language

## Verified export-selection semantics

Tatoeba's own weekly export SQL creates the CC0 file from the sentence table using `correctness > -1 AND license = 'CC0 1.0'`, exporting `id`, `lang`, `text` and `modified`. This confirms the official file is not the complete sentence table and that rows marked incorrect (`correctness = -1`) are excluded. For a future count, count rows and distinct sentence IDs by language code from this exact export; do not count translation links or infer CC0 availability from the general CC-BY sentence export. Official implementation: https://github.com/Tatoeba/tatoeba2/blob/f2c80b81032630648f7896182174a9f5784ccde2/docs/database/scripts/weekly_exports.sql

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
