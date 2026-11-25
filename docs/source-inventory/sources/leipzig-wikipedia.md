# Leipzig Corpora Collection — Wikipedia

**Text unit:** Sentences from Wikipedia articles  
**Primary source:** https://wortschatz.uni-leipzig.de/en/download/

## Creator and origin

Leipzig University Wortschatz / Leipzig Corpora Collection; underlying text from Wikipedia.

## Access methods

Language-specific packages via portal; exact archive/version from manifest.

## File types and structure

Compressed UTF-8 TSV; sentence ID and sentence plus companion word/source files.

## Distribution conditions and rights

Wikipedia generally CC BY-SA and/or GFDL depending on revision/imports; check package terms and preserve attribution/share-alike.

## Content and language coverage

Wikipedia text segmented into sentences; 3,000 project records per each of 34 target languages.

## Verified upstream catalogue availability (independent of project acquisition)

The provider's per-language catalogue lists Wikipedia corpora by dump year and offers fixed-size sentence packages (10K, 30K, 100K, 300K and sometimes 1M) plus an `All` archive. This confirms that the project's 3,000-row sample is not an upstream ceiling. Examples verified from the per-language catalogue include:

- bg: 2021 offers 1M and All.
- hr: 2021 offers 1M and All.
- cs: 2018 offers 1M and All.
- ga: 2021 offers 10K, 30K and All.
- mt: 2021 offers 10K, 30K and All.
- nn: Wikipedia packages through 2016 include 100K/300K; separate 2020 Web corpus offers up to 1M.
- zh (Mandarin): 2021 offers 1M and All.
- ca: 2016 offers up to 3M and All; 2018 offers 1M and All; 2021 offers All.

The `All` corpus means the full release, not a fixed sample. The exact full-corpus sentence counts still need to be computed from the archive's `*_sentences.txt` file; fixed-size tiers are samples and must not be summed across releases. Provider format specification: https://wortschatz.informatik.uni-leipzig.de/public/documents/Format_Download_File-eng.pdf. Per-language catalogues: https://cls.wortschatz-leipzig.de/en

## Current langid-32 acquisition snapshot

3,000/language is our sample, not full Leipzig/Wikipedia availability.

| Language | Current staged records |
|---|---:|
| bg | 3,000 |
| hr | 3,000 |
| cs | 3,000 |
| da | 3,000 |
| nl | 3,000 |
| en | 3,000 |
| et | 3,000 |
| fi | 3,000 |
| fr | 3,000 |
| de | 3,000 |
| el | 3,000 |
| hu | 3,000 |
| ga | 3,000 |
| it | 3,000 |
| lv | 3,000 |
| lt | 3,000 |
| mt | 3,000 |
| pl | 3,000 |
| pt | 3,000 |
| ro | 3,000 |
| sk | 3,000 |
| sl | 3,000 |
| es | 3,000 |
| sv | 3,000 |
| nb | 3,000 |
| nn | 3,000 |
| ru | 3,000 |
| ja | 3,000 |
| zh | 3,000 |
| ko | 3,000 |
| ar | 3,000 |
| tr | 3,000 |
| ca | 3,000 |
| is | 3,000 |

**Current staged total:** 102,000 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Enumerate each of the 34 target-language Wikipedia catalogue pages and pin the chosen dump year.
- Download the `All` archive for each target language and count exact lines in `*_sentences.txt`.
- Record archive checksums and release dates; never sum fixed-size tiers or multiple dump years.
- Verify Wikipedia attribution/share-alike obligations and imported-content exceptions for each package.
