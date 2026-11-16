# Corpus source inventory

Status: initial desk inventory, 2026-11-16. This is a source-discovery document, not a claim that any corpus has already been downloaded, parsed, or counted. All per-language usable-record counts remain **unmeasured**.

Target: 20,000 usable text examples per language across 32 languages (640,000 total). Count after normalization, quality filtering, and cross-source deduplication—not archive size, audio hours, aligned sentence pairs, or document counts.

## 1. Source coverage by target language

Legend:
- **Y** = source documentation explicitly lists this language.
- **—** = source's documented language coverage excludes it.
- **?** = not yet verified against the current source catalogue or release.
- A Y means coverage, not a guarantee of 20,000 usable examples.

| Code | Language | Common Voice 27 | Målfrid 2026 | HPLT 3.0 | JRC-Acquis 3 | DGT-TM | Europarl v7 | Tatoeba CC0 | OPUS |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| bg | Bulgarian | Y | — | Y | Y | Y | Y | — | ? |
| hr | Croatian | Y | — | Y | — | Y | — | — | ? |
| cs | Czech | Y | — | Y | Y | Y | Y | Y | ? |
| da | Danish | Y | — | Y | Y | Y | Y | Y | ? |
| nl | Dutch | Y | — | Y | Y | Y | Y | Y | ? |
| en | English | Y | — | Y | Y | Y | Y | Y | ? |
| et | Estonian | Y | — | Y | Y | Y | Y | — | ? |
| fi | Finnish | Y | — | Y | Y | Y | Y | Y | ? |
| fr | French | Y | — | Y | Y | Y | Y | Y | ? |
| de | German | Y | — | Y | Y | Y | Y | Y | ? |
| el | Greek | Y | — | Y | Y | Y | Y | — | ? |
| hu | Hungarian | Y | — | Y | Y | Y | Y | Y | ? |
| ga | Irish | Y | — | Y | — | Y | — | — | ? |
| it | Italian | Y | — | Y | Y | Y | Y | Y | ? |
| lv | Latvian | Y | — | Y | Y | Y | Y | — | ? |
| lt | Lithuanian | Y | — | Y | Y | Y | Y | — | ? |
| mt | Maltese | Y | — | Y | Y | Y | — | — | ? |
| pl | Polish | Y | — | Y | Y | Y | Y | Y | ? |
| pt | Portuguese | Y | — | Y | Y | Y | Y | Y | ? |
| ro | Romanian | Y | — | Y | Y | Y | Y | — | ? |
| sk | Slovak | Y | — | Y | Y | Y | Y | — | ? |
| sl | Slovenian | Y | — | Y | Y | Y | Y | — | ? |
| es | Spanish | Y | — | Y | Y | Y | Y | Y | ? |
| sv | Swedish | Y | — | Y | Y | Y | Y | Y | ? |
| nb | Norwegian Bokmål | Y | Y | Y | — | — | — | Y | ? |
| nn | Norwegian Nynorsk | Y | Y | Y | — | — | — | — | ? |
| ru | Russian | Y | — | Y | — | — | — | Y | ? |
| ja | Japanese | Y | — | Y | — | — | — | Y | ? |
| zh | Chinese | Y | — | Y | — | — | — | Y | ? |
| ko | Korean | Y | — | Y | — | — | — | — | ? |
| ar | Arabic | Y | — | Y | — | — | — | Y | ? |
| tr | Turkish | Y | — | Y | — | — | — | — | ? |

Coverage references and caveats:
- HPLT Monolingual Datasets 3.0 covers 198 language-script combinations and includes all 32 target language classes (Chinese has Simplified and Traditional variants). It is a very large Common Crawl/Internet Archive-derived web corpus (2012–2024), with document-level and segment-level language labels, provenance, WDS quality ordering, and PII-span annotations. Its v3 catalogue reports very large segment pools even for our smaller targets: Irish 3.77M, Maltese 17.22M, Norwegian Nynorsk 4.12M, Norwegian Bokmål 888.91M, and Korean 2.34B segments. These are source-level segments, not our filtered usable-example counts. Sources: https://hplt-project.org/datasets/v3.0 and https://data.hplt-project.org/three/sorted/manifest.json
- Common Voice: v27.0 was announced on 2026-09-18 with 295 scripted-speech languages. Its release documentation specifies a per-locale `validated_sentences.tsv` (available since corpus 17.0) with `sentence_id`, `sentence`, optional `variant`, and optional `sentence_domain`. This is the most directly relevant text inventory for this project; it is distinct from the audio clip TSVs. The release metadata JSON also reports a per-locale `validatedSentences` count, useful as a preliminary cross-check. We still need to verify the 32 exact locale codes and count the actual TSV rows after our own filters. Sources: https://github.com/common-voice/cv-dataset/blob/main/datasets/scripted-speech/README.md, https://github.com/common-voice/cv-dataset/blob/main/datasets/scripted-speech/cv-corpus-27.0-delta-2026-09-11.json, https://discourse.mozilla.org/t/common-voice-scripted-speech-v27-0-and-spontaneous-speech-v5-0-released/149490 and https://commonvoice.mozilla.org/datasets
- JRC-Acquis 3.0 explicitly lists 22 languages and reports 463,792 documents in total. It excludes Croatian and Irish. The JRC says it is a research corpus, not a legal reference corpus; the official conditions require source attribution and retention of Commission ownership, and distinguish public-domain official legislative material from other content. Do not assume the entire compiled corpus has one blanket CC0-style licence. Review the actual conditions before redistributing it. Source: https://joint-research-centre.ec.europa.eu/language-technology-resources/jrc-acquis_en
- DGT-TM documents coverage of all 24 EU official languages, but Irish is sparse and Croatian has less material. It consists of translation units, mostly sentence or sub-sentence segments, not full reproducible documents. The current download page lists releases through DGT-TM-release 2021 (the 2020 data update); do not describe it as a current annual feed. The statistics PDF reports roughly 0.24M to 6.44M translation units per language in the 2011–2020 updates, but these are aligned translation units, not unique independent sentences. The Commission permits reuse subject to attribution, source/date identification and retention of Commission ownership. Sources: https://joint-research-centre.ec.europa.eu/language-technology-resources/dgt-translation-memory_en and https://wt-public.emm4u.eu/Resources/DGT-TM_Statistics.pdf
- Europarl v7 documents 21 languages and publishes per-language sentence counts after XML removal. It does not cover Croatian, Irish or Maltese. All 21 target-language counts exceed 387,000; its documents retain IDs, which makes group-level splitting possible. It is parliamentary proceedings from 1996–2011, with strong domain/register bias. The project page says it is not aware of copyright restrictions, but this should still be recorded as the source's statement rather than a formal licence grant. Source: https://www.statmt.org/europarl/
- Tatoeba publishes a full sentence export and a separate CC0-only export. The general sentence export is CC BY 2.0 FR; only the separately identified subset is CC0. The CC0 language list includes 18 of our target classes (cs, da, nl, en, fi, fr, de, hu, it, pl, pt, es, sv, nb, ru, ja, zh/Mandarin, ar); it does not list the other 14 target classes. This is a language-availability signal, not a count. Preserve the sentence-base and translation-link files to identify translations and prevent cross-split leakage. The CC0 export is updated weekly. The 14 November 2026 export index lists `sentences_CC0.csv` at 41.9 MB uncompressed (7.96 MB compressed) and `sentences_base.csv` at 196.9 MB uncompressed (64.1 MB compressed). The CC0 export uses ISO 639-3 language codes; Mandarin Chinese is the relevant Chinese variety for this inventory. Pin the weekly export date and hashes. Source: https://tatoeba.org/en/downloads and https://downloads.tatoeba.org/exports/
- OPUS is an aggregator, not a single uniformly licensed dataset. Its catalogue spans many languages and corpora, but each corpus has its own coverage, provenance, quality and licence. Screen each candidate individually; do not ingest the aggregate indiscriminately. Source: https://opus.nlpl.eu/

### Norwegian Bokmål and Nynorsk: Målfrid 2026 resolves the volume gap

The National Library of Norway's **Målfrid 2026** corpus is a major discovery and should now be the primary candidate for both Norwegian classes. It contains documents from 720 Norwegian state-institution domains, crawled between December 2025 and January 2026, and is released under the Norwegian Licence for Open Government Data (NLOD) 2.0.

| Language | Tokens |
|---|---:|
| Bokmål | 1,890,232,881 |
| Nynorsk | 170,231,965 |

The data is provided as separate per-language TAR archives containing gzipped JSONL documents. Each document includes `doc_id`, `doc_hash`, `domain`, `url`, `date`, `mimetype`, `title`, document-level `lang`, and `fulltext` as paragraph strings. The catalogue says exact duplicates were removed at the domain level. The published documentation warns that language identification between closely related languages is not perfect, so the Nynorsk/Bokmål labels must be audited rather than trusted blindly.

This is much better suited to the project than HPLT for Norwegian: explicit NLOD 2.0, institutional source domains, separate locale archives, and stable document/domain provenance. For splitting, retain document IDs and consider domain-level grouping to reduce website-template leakage. The language label is document-level; a cross-check on paragraphs is needed.

The corpus is a strong volume source, not a ready-to-use 20k sentence corpus. We still need to extract paragraph/sentence examples, check for mixed-language pages and PII, deduplicate across languages and sources, and sample across domains. The Nynorsk archive is 342.1 MB and the Bokmål archive 3.8 GB.

Additional Norwegian sources:
- Målfrid 2021–2025 parallel text provides 145,267 English–Bokmål, 12,268 English–Nynorsk and 50,957 Bokmål–Nynorsk translation units under NLOD. Useful for translation-aware split groups, but not a replacement for monolingual text.
- The randomized Nynorsk corpus contains 3.3M sentences / 57.5M words under CC BY 3.0, but is lemmatized and morphologically tagged; treat as supplementary rather than clean raw text.
- NorNE is CC0 and contains about 300k words each for Bokmål and Nynorsk, but it reuses the Norwegian Dependency Treebank texts and contains named-entity annotations.
- The Norwegian Newspaper Corpus has large volumes (68M Nynorsk words and 1.68B Bokmål words) but is CC BY-NC; exclude from a permissive public corpus.

Source metadata and counts: [norwegian-korean-source-counts.csv](data/norwegian-korean-source-counts.csv). Sources: https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-107/ and https://data.norge.no/en/datasets/b3da2524-c7c6-30c9-b757-d813f228c76f/malfrid-2026.

### Korean: a viable government-text route is emerging

Korean remains the one non-EU Common Voice shortfall without a fully verified, permissive 20k source mix. Several candidates are now better defined:

1. **Korea.kr policy briefing and ministry press releases.** Its copyright policy says text carrying a KOGL Type 1 mark can be reused with source attribution; items without that mark must not be assumed reusable. Individual 2026 articles now display additional KOGL AI-training conditions: prevent model outputs identical or substantially similar to source works, preserve source attribution when an output directly quotes a work, and do not resell AI-training datasets made from public works. This is a plausible source for a language-ID corpus, but terms must be recorded per article. It is not enough to label the whole site CC BY. The site's RSS service was discontinued on 1 July 2026, so acquisition would use its search/pagination pages rather than RSS.
2. **NIKL Written Corpus 2025.** The National Institute of Korean Language lists 10,293 types of copyright-cleared written works across literary and informational genres. Access is by request; the public catalogue does not publish a blanket redistribution licence. It is a strong candidate if the actual approved-use terms permit the intended corpus use.
3. **NSMC (Naver Sentiment Movie Corpus).** 200,000 short reviews are available. Licence metadata conflicts: the original GitHub repository has no clear licence file; the Hugging Face dataset card says CC BY 2.0, while its `dataset_infos.json` and the KLUE paper describe CC0. Do not ingest until this is resolved with the source. It is also user-generated, short-review text and needs PII/quality filtering.
4. **Korean Wikipedia.** The 2020 Korean raw-text collection description reports 5.3M sentences from the Korean Wikipedia dump. A direct Wikimedia dump is a possible share-alike fallback, but retain page/revision attribution and treat CC BY-SA/GFDL separately from the preferred permissive sources.
5. **Korean Parallel Corpus.** The repository provides 31k Bible sentences under CC BY-SA 3.0 plus other parallel sets. It is a narrow religious register and translated text; supplementary only.
6. **Open Korean Historical Corpus.** 17.7M documents and 5.1B tokens, but the dataset is CC BY-NC 4.0, spans 1,300 years and several historical scripts/languages, and is not a default source for a modern, commercially reusable corpus.
7. **HPLT v3 Korean.** 2.34B segments, but CC0 applies to packaging, not underlying web text; legal hold.

The Korea.kr page-level conditions are particularly relevant: KOGL Type 1 itself permits commercial reuse and modification with attribution, but the newer AI-specific terms add conditions for AI training and prohibit resale of training datasets made from the public works. A free public release may be different from resale, but the exact scope should be confirmed before including those records in a redistributable corpus. See [Korea.kr copyright policy](https://www.korea.kr/guide/copyRight.do), [an example 2026 press release with AI conditions](https://www.korea.kr/briefing/pressReleaseView.do?newsId=156788833), and the official [KOGL Type 1 terms](https://www.kogl.or.kr/info/licenseTypeEn.do).

The Korean candidate counts and rights status are recorded in [norwegian-korean-source-counts.csv](data/norwegian-korean-source-counts.csv). A dedicated acquisition/rights issue is open: [#4](https://github.com/SylvainSouche/langid-32/issues/4).

### HPLT 3.0: important high-volume candidate, but not a blanket text licence

HPLT 3.0 is the strongest single-source volume discovery so far. The catalogue has 198 language-script combinations, and all 32 project targets are represented. Its data is full-document JSONL in Zstandard shards; the `text` field is segmented by paragraph-like newlines. Metadata includes the original crawl URL and date, document-level top-three language predictions, segment-level language labels, WDS quality scores, and PII spans. It is globally deduplicated for most languages, but explicitly not for Chinese, English and Russian. The v3 release is from July 2025. The January 2026 v4 release cycle exposes a roughly 440-TiB pool of shallow-processed web documents; HPLT says this pool is not directly suitable for language engineering and that clean/noisy language-specific outputs are a separate, ongoing release. For the current corpus inventory, v3 remains the usable processed catalogue.

This gives us a technically attractive route, but it is no longer the leading gap-filler for Norwegian: the National Library of Norway has released a very large, open-licensed Målfrid 2026 corpus for both Bokmål and Nynorsk (see below):
- select the highest WDS bins first rather than download every shard;
- use segment-level language labels, not just document-level predictions;
- reject or carefully redact PII-annotated text;
- retain URL/domain, crawl date, document ID and quality metadata internally;
- deduplicate again across HPLT, Common Voice, DGT and other sources.

**Licensing distinction:** HPLT says it licenses the *packaging* under CC0 and explicitly says it does not own the extracted text. Its terms also leave compliance with copyright and data-protection law to the user. Therefore CC0 on the packaging is not a blanket CC0 grant for the underlying web text. Do not publish HPLT-derived text as CC0 merely because the HPLT package is CC0. Treat it as a high-volume candidate for internal research/training only after the applicable text-and-data-mining basis and privacy policy have been reviewed; do not put it in a publicly redistributed corpus unless the underlying rights are cleared.

The HPLT v3 source-level segment counts are far above the 20,000 target for Korean (74.79M documents, 2.34B segments). Norwegian Bokmål and Nynorsk also have large HPLT pools, but Målfrid 2026 is a better documented, open-licensed source for those languages.

Other useful low-volume Common Voice languages also have large HPLT segment pools: Irish 3.77M, Maltese 17.22M, and Estonian 425.93M. These counts are not equivalent to clean, unique, privacy-screened examples. The rounded catalogue figures for these eleven Common Voice shortfall languages are recorded in [hplt-v3-shortfall-language-counts.csv](data/hplt-v3-shortfall-language-counts.csv). Sources: https://hplt-project.org/datasets/v3.0, https://data.hplt-project.org/three/sorted/manifest.json, and https://hplt-project.org/datasets/v4.0.

## 2. Source assessment and acquisition priority

| Priority | Source | Why it matters | Main risks / work required |
|---|---|---|---|
| P0 | Common Voice Scripted Speech 27.0 | Natural, short, crowd-contributed sentences; CC0; broad language ambitions | Verify text TSV availability and count for every locale. Repeated prompts and domain-specific prompts; group prompt variants to prevent leakage. Text availability may differ from audio clip volume. |
| P1 | DGT-TM release 2021 (data through 2020) | Large translation-memory volume across all 24 EU languages; even Irish and Croatian have six-figure unit counts in the latest update | Translation-memory segments; legal/administrative register and translationese; duplicate segments; EUR-Lex document IDs must be retained for grouping. The source page's current list ends at the 2021 release. |
| P1 | Tatoeba CC0 export | Simple, directly downloadable sentence-level data; useful for many non-EU languages | CC0 subset is smaller than full export; translation chains and sentence pairs create leakage; sentence quality and language labels need validation. |
| P1 | OPUS candidates | Likely essential for Russian, Japanese, Chinese, Korean, Arabic, Turkish and Norwegian varieties | Treat each corpus separately. Check per-language volume, license, domain, source document IDs and translation overlap. Prefer original monolingual material where possible. |
| P2 | JRC-Acquis 3.0 | 22 languages and 463,792 documents; useful for EU language coverage and cross-language evaluation | Mostly legislative/legal register; overlaps substantially with DGT-TM. Compiled corpus has nuanced reuse conditions; inspect actual content rights and attribution requirements before publishing derived text. |
| P2 | Europarl v7 | Publicly documented per-language sentence counts; substantial volume for 21 languages | 1996–2011 parliamentary proceedings; strong domain bias; speaker/document markup; verify redistribution terms before publication. |
| P0 (technical) / legal hold | HPLT 3.0 | All 32 targets, very large segment counts, segment-level language IDs, PII spans and quality ordering | CC0 applies to packaging, not underlying text. Use only after rights/TDM review; do not redistribute extracted text by default. Very large shards; sample high-WDS bins. |
| P1 | Målfrid 2026 | 1.89B Bokmål tokens and 170.2M Nynorsk tokens from 720 Norwegian public-sector domains; NLOD 2.0 | Document-level language ID needs auditing; extract paragraphs/sentences, retain domain and document IDs, PII-check and deduplicate. |\n| P3 | Other monolingual sources | Fill shortfalls and broaden register/domain | Only admit sources with clear per-component terms, provenance, stable identifiers and defensible language labels. |

## 3. Common Voice v27.0 metadata: first measured result

I parsed the upstream v27.0 release JSON directly:
`cv-corpus-27.0-delta-2026-09-11.json`, blob SHA `9de5d5b46eabc3678174f58adae4b5c75dc1e641`.

The metadata contains a matching locale entry for every one of our 32 target languages. There are 33 locale files to inspect because Chinese is represented by both `zh-CN` and `zh-TW`. The table below reports the upstream `validatedSentences` metadata field, not our own count of rows in the downloadable TSV and not the final usable count.

| Target | Common Voice locale(s) | Metadata validatedSentences | Gap to 20,000 (metadata only) |
|---|---|---:|---:|
| bg | bg | 39,572 | 0 |
| hr | hr | 1,781 | 18,219 |
| cs | cs | 451,317 | 0 |
| da | da | 20,986 | 0 |
| nl | nl | 260,921 | 0 |
| en | en | 1,682,617 | 0 |
| et | et | 11,118 | 8,882 |
| fi | fi | 5,865 | 14,135 |
| fr | fr | 1,661,012 | 0 |
| de | de | 2,058,031 | 0 |
| el | el | 8,950 | 11,050 |
| hu | hu | 326,554 | 0 |
| ga | ga-IE | 4,883 | 15,117 |
| it | it | 925,181 | 0 |
| lv | lv | 34,689 | 0 |
| lt | lt | 129,359 | 0 |
| mt | mt | 5,274 | 14,726 |
| pl | pl | 230,314 | 0 |
| pt | pt | 43,656 | 0 |
| ro | ro | 13,756 | 6,244 |
| sk | sk | 22,194 | 0 |
| sl | sl | 4,209 | 15,791 |
| es | es | 1,082,797 | 0 |
| sv | sv-SE | 26,893 | 0 |
| nb | nb-NO | 4,419 | 15,581 |
| nn | nn-NO | 5,318 | 14,682 |
| ru | ru | 48,002 | 0 |
| ja | ja | 44,606 | 0 |
| zh | zh-CN + zh-TW | 80,036 | 0 |
| ko | ko | 7,432 | 12,568 |
| ar | ar | 59,439 | 0 |
| tr | tr | 410,411 | 0 |

**Initial signal:** 21 of 32 target languages have at least 20,000 entries in this metadata field. Eleven are below the target: hr, et, fi, el, ga, mt, ro, sl, nb, nn and ko. The metadata total across the 32 target language classes is 9,711,592 (33 locale entries because Chinese combines `zh-CN` and `zh-TW`).

This is encouraging but not yet evidence that Common Voice alone supplies the target corpus:
- The release JSON field is a preliminary inventory statistic. We have not counted the corresponding TSV rows. The per-locale metadata snapshot is committed at [common-voice-v27-metadata.csv](data/common-voice-v27-metadata.csv).
- The TSV has an `is_used` flag. Retired sentences may be outdated, too similar, incorrect, or otherwise no longer eligible for recording. We should count all non-empty rows and the `is_used=true` subset separately; use the latter as the conservative first-pass pool.
- The MDC catalogue exposes each locale as a single MP3 `.tar.gz` archive; the `validated_sentences.tsv` file is documented inside the archive, but the catalogue does not list a separate text-only download. This matters operationally: some locale archives are multi-gigabyte (for example Arabic 3.30 GB, Japanese 14.36 GB, and Italian 9.82 GB). Extract only the TSV after downloading; do not retain or process audio for this project. The public catalogue and locale datasheets show the archive sizes and TSV schema.
- The metadata's clip and user counts are not text-corpus counts and must not be used to infer the number of usable sentences.
- A sentence-level file has no source-document ID. Retain `sentence_id` as the grouping key to prevent repeated prompt text from crossing splits; this does not solve broader document-level leakage.
- For Chinese, retain the locale distinction during inventory and deduplication, then decide whether both script varieties belong in the single `zh` class. Do not discard the locale provenance.
- Metadata counts can be very large relative to the clips reported for some locales. This reinforces why we must inspect the actual archive and TSV rather than infer availability from the JSON.

The locale mapping used here is explicit: `ga-IE`, `sv-SE`, `nb-NO`, `nn-NO`, and `zh-CN` + `zh-TW`; the other targets use their two-letter locale codes.

### Reproducible inventory command

A read-only counter is now implemented at `src/langid32/common_voice_inventory.py`. It reads the official release JSON and, when given extracted locale directories, scans `validated_sentences.tsv` without copying sentence text into the report. It records raw rows, non-empty rows, `is_used` counts, length-filter counts, normalized duplicates across all rows and within the active `is_used=true` pool, plus per-locale source/domain counts.

After installing the project in the existing development environment, download the locale archives directly from MDC. The archive contains audio, but the project only needs `validated_sentences.tsv`. The new extractor streams the archive and writes only that TSV—no audio files are extracted or retained:

```sh
langid32-cv-extract \
  --archive fr=/path/to/french.tar.gz \
  --archive en=/path/to/english.tar.gz \
  --archive ga-IE=/path/to/irish.tar.gz \
  --output-root data/raw/common-voice-v27 \
  --manifest data/inventory/common-voice-v27-extraction.json
```

Repeat `--archive LOCALE=PATH` for each locale. The 33 locale archives are: bg, hr, cs, da, nl, en, et, fi, fr, de, el, hu, ga-IE, it, lv, lt, mt, pl, pt, ro, sk, sl, es, sv-SE, nb-NO, nn-NO, ru, ja, zh-CN, zh-TW, ko, ar, tr.

Then count the extracted text:

```sh
langid32-cv-inventory \
  --release-json /path/to/cv-corpus-27.0-delta-2026-09-11.json \
  --data-root data/raw/common-voice-v27 \
  --output data/inventory/common-voice-v27.csv
```

The counter also works without `--data-root`, in which case it emits metadata-only rows and explicitly marks TSV counts as unmeasured. Neither command downloads data.

### Reproducible Tatoeba CC0 inventory

A second read-only counter is implemented at `src/langid32/tatoeba_inventory.py`. It reads the CC0 sentence export and optionally joins the sentence-base export through a temporary SQLite database. It reports per-language raw rows, empty/length-filtered rows, unique eligible text, original/translated/unknown counts, and translation-group counts. It does not emit sentence text or contributor names.

The export files are tab-separated despite their `.csv` suffix. Download the CC0-only file and the base relation file from the Tatoeba weekly exports, then run:

```sh
langid32-tatoeba-inventory \
  --sentences-cc0 /path/to/sentences_CC0.csv \
  --sentences-base /path/to/sentences_base.csv \
  --output data/inventory/tatoeba-cc0.csv
```

The `sentences_base.csv` file is used to group translations with their source sentence; it is not itself used as training text. The counter stores only the CC0 sentence rows in a temporary SQLite database and removes it when finished. The export's base relation may point to a sentence outside the CC0 subset; that ID is still useful as an internal grouping key. A final merged corpus must still deduplicate against Common Voice and other sources.

## 4. Required inventory measurements

For each (source, release, language), record:

1. Archive/file URL and retrieval date; archive SHA-256.
2. Licence and source-specific reuse/attribution conditions, checked against the actual release.
3. Raw rows, non-empty rows, and rows with a valid language label.
4. Rows passing basic length/Unicode/script checks.
5. Exact duplicates within source and cross-source duplicates.
6. Unique source documents/groups and number of groups contributing usable examples.
7. Usable examples after all agreed filters.
8. Domain/register label and whether text is original, translated, or uncertain.
9. PII/identifier review outcome.
10. Final accepted count and shortfall against 20,000.

Do not use archive byte size, number of audio clips, number of translation pairs, or document count as a substitute for usable text-example counts.

## 5. Pipeline implications

The current `langid32-prepare` command processes one input file per invocation and caps each invocation independently. That is not yet sufficient for a multi-source corpus: independently prepared outputs cannot safely be concatenated because duplicate removal, source balancing, document grouping, and the final 20,000-per-language cap must be applied globally.

Before bulk ingestion, the corpus pipeline should gain a merge-first stage with an intermediate record containing at least:
- `text`
- `language`
- `source_id` and `source_release`
- `document_group` (or another stable leakage-control group)
- `licence_id`
- `text_origin` (`original`, `translated`, `unknown`)

The internal staging data may retain provenance/group identifiers; the published training JSONL should continue to omit contributor identifiers and internal group IDs. Global deduplication and group-level train/validation/test splitting must happen after source ingestion and before the final cap. Related translations and repeated prompts must not be split across train and evaluation.

For source balancing, keep per-source counts and quotas visible. A language with 20,000 examples drawn almost entirely from legal text is not equivalent to one with broad domain coverage. Do not silently fill a shortfall with translated or synthetic sentences.

## 6. Immediate execution sequence

1. Use the v27 release metadata JSON to enumerate exact locale codes and preliminary `validatedSentences` counts; then inspect/download the corresponding MDC locale archives and count `validated_sentences.tsv` rows and usable text.
2. Implement a read-only inventory/counting command that reports the measurements in section 4 without publishing text.
3. Inspect DGT-TM release metadata and extract counts for all 24 EU languages.
4. Measure Tatoeba CC0 per language and preserve its translation/base graph.
5. Query OPUS corpus-by-corpus for the seven non-EU additions and Norwegian Bokmål/Nynorsk; shortlist by licence, volume, and source quality.
6. Only then implement the merge-first global preparation stage and build the first corpus.

No source counts are currently claimed in this inventory beyond the published source-level statistics described above.
