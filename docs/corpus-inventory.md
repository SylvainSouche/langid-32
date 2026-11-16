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
| en | English | Y | Y | Y | Y | Y | Y | Y | ? |
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
- HPLT Monolingual Datasets 3.0 covers 198 language-script combinations and includes all 32 target language classes (Chinese has Simplified and Traditional variants). It is a very large Common Crawl/Internet Archive-derived web corpus (2012–2024), with document-level and segment-level language labels, provenance, WDS quality ordering, and PII-span annotations. Its v3 catalogue reports very large segment pools even for our smaller targets: Irish 3.77M, Maltese 17.22M, Norwegian Nynorsk 31.94M, Norwegian Bokmål 888.91M, and Korean 2.34B segments. These are source-level segments, not our filtered usable-example counts. Sources: https://hplt-project.org/datasets/v3.0 and https://data.hplt-project.org/three/sorted/manifest.json
- Common Voice: v27.0 was announced on 2026-09-18 with 295 scripted-speech languages. Its release documentation specifies a per-locale `validated_sentences.tsv` (available since corpus 17.0) with `sentence_id`, `sentence`, optional `variant`, optional `sentence_domain`, `source`, `is_used`, and `clips_count`. This is the most directly relevant text inventory for this project; it is distinct from the audio clip TSVs. The release metadata JSON also reports a per-locale `validatedSentences` count, useful as a preliminary cross-check. We still need to verify the 32 exact locale codes and count the actual TSV rows after our own filters.

The committed metadata snapshot contains 33 locale entries mapping to 32 target classes and 9,711,592 validated-sentence metadata records in total. Eleven classes are below the 20,000 target: Croatian 1,781; Estonian 11,118; Finnish 5,865; Greek 8,950; Irish 4,883; Maltese 5,274; Romanian 13,756; Slovenian 4,209; Bokmål 4,419; Nynorsk 5,318; Korean 7,432. The other 21 classes meet or exceed 20,000 at metadata level. This is not yet the usable count: `is_used=true`, text length, normalized duplicates and actual text rows must still be checked. The 33-locale snapshot is [common-voice-v27-metadata.csv](data/common-voice-v27-metadata.csv). Sources: https://github.com/common-voice/cv-dataset/blob/main/datasets/scripted-speech/README.md, https://github.com/common-voice/cv-dataset/blob/main/datasets/scripted-speech/cv-corpus-27.0-delta-2026-09-11.json, https://discourse.mozilla.org/t/common-voice-scripted-speech-v27-0-and-spontaneous-speech-v5-0-released/149490 and https://commonvoice.mozilla.org/datasets
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

The data is provided as separate per-language TAR archives containing gzipped JSONL documents. Each document includes `doc_id`, `doc_hash`, `domain`, `url`, `date`, `mimetype`, `title`, document-level `lang`, and `fulltext` as paragraph strings. The catalogue says exact duplicates were removed at the domain level. The published documentation warns that language identification between closely related languages is not perfect, so the Nynorsk/Bokmål labels must be audited rather than trusted blindly. The corpus also includes 570.1M English tokens, although English is not a shortfall language.

This is much better suited to the project than HPLT for Norwegian: explicit NLOD 2.0, institutional source domains, separate locale archives, and stable document/domain provenance. NLOD permits use, modification and redistribution for any purpose with attribution. Section 9 lists CC BY 4.0 as compatible for adapted/combined works, but distinguishes database rights: for material constituting a database, it specifies ODC-By 1.0 compatibility rather than CC BY. Do not assume the entire Målfrid compilation can be relicensed under CC BY 4.0; preserve the NLOD terms for the source database unless its database-right status and the applicable compatibility route are established. NLOD also excludes personal data lacking a legitimate basis and third-party material the licensor cannot license, so PII and embedded third-party rights still require screening. For splitting, retain document IDs and consider domain-level grouping to reduce website-template leakage. The language label is document-level; a cross-check on paragraphs is needed.

The corpus is a strong volume source, not a ready-to-use 20k sentence corpus. We still need to extract paragraph/sentence examples, check for mixed-language pages and PII, deduplicate across languages and sources, and sample across domains. The Nynorsk archive is 342.1 MB and the Bokmål archive 3.8 GB.

A read-only inventory command is now implemented. It streams the per-language TAR, reads the gzipped JSONL members, and reports document hashes, domains, paragraph counts, length-filtered unique paragraphs, and language-label mismatches without exporting text. It explicitly marks PII screening as not performed.

```sh
langid32-maalfrid-inventory \
  --archive nn=/path/to/maalfrid_2026_nno.tar \
  --archive nb=/path/to/maalfrid_2026_nob.tar \
  --output data/inventory/maalfrid-2026.csv
```

The inventory counts paragraphs, not sentences. Sentence segmentation and language-label audit remain later preparation steps.

Additional Norwegian sources:
- Målfrid 2021–2025 parallel text provides 145,267 English–Bokmål, 12,268 English–Nynorsk and 50,957 Bokmål–Nynorsk translation units under NLOD. Useful for translation-aware split groups, but not a replacement for monolingual text.
- The randomized Nynorsk corpus contains 3.3M sentences / 57.5M words under CC BY 3.0, but is lemmatized and morphologically tagged; treat as supplementary rather than clean raw text.
- NorNE is CC0 and contains about 300k words each for Bokmål and Nynorsk, but it reuses the Norwegian Dependency Treebank texts and contains named-entity annotations.
- The Norwegian Newspaper Corpus has large volumes (68M Nynorsk words and 1.68B Bokmål words) but is CC BY-NC; exclude from a permissive public corpus.

Source metadata and counts: [norwegian-korean-source-counts.csv](data/norwegian-korean-source-counts.csv). Sources: https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-107/, https://data.norge.no/en/datasets/b3da2524-c7c6-30c9-b757-d813f228c76f/malfrid-2026, and https://data.norge.no/nlod/en/2.0.

### Korean: a viable government-text route is emerging

Korean remains the one non-EU Common Voice shortfall without a fully verified, permissive 20k source mix. Several candidates are now better defined:

1. **Korean legislation and government-issued legal texts (Law Open Data API).** This is the clearest rights position for Korean so far: Article 7 of the Korean Copyright Act excludes constitutions, acts, treaties, decrees, municipal ordinances/rules, government public notifications/announcements/directives, court decisions, and government-produced compilations/translations of those materials from copyright protection. The Law Open Data API exposes lists and full text (HTML/XML/JSON) for current legislation and administrative rules. API registration requires an application, but the registration page says approval is automatic. This is likely enough volume for a first legal-register Korean subset; count it before relying on it. Preserve law ID, effective date and article/section IDs as grouping keys, and use current versions only. The source text being uncopyrightable does not remove API access conditions or possible database-right questions, so check the API terms before bulk extraction or redistribution. The API registration page requires identity verification, contact details, a user-chosen OC key, a system description, a server IP and explicit selection of the list/body API products. It warns against excessive short-interval calls and misattribution/tampering, but says OPEN API applications are automatically approved. Use statutes, administrative rules and local ordinances first; avoid court decisions and administrative case records because they can contain personal data. Sources: https://www.copyright.or.kr/eng/laws-and-treaties/copyright-law/chapter02/section01.do, https://open.law.go.kr/LSO/openApi/openApiManual.do, https://open.law.go.kr/LSO/information/guide.do, https://open.law.go.kr/LSO/usrJoin.do.
2. **Korea.kr policy briefing and ministry press releases.** Its copyright policy says text carrying a KOGL Type 1 mark can be reused with source attribution; items without that mark must not be assumed reusable. Individual 2026 articles now display additional KOGL AI-training conditions: prevent model outputs identical or substantially similar to source works, preserve source attribution when an output directly quotes a work, and do not resell AI-training datasets made from public works. This is a plausible source for a language-ID corpus, but terms must be recorded per article. It is not enough to label the whole site CC BY. The site's RSS service was discontinued on 1 July 2026, so acquisition would use its search/pagination pages rather than RSS.
2. **NIKL Written Corpus 2025.** The National Institute of Korean Language lists 10,293 types of copyright-cleared written works across literary and informational genres. Access is by request; the public catalogue does not publish a blanket redistribution licence. It is a strong candidate if the actual approved-use terms permit the intended corpus use.
3. **NSMC (Naver Sentiment Movie Corpus).** 200,000 short reviews are available. Licence metadata conflicts: the original GitHub repository has no clear licence file; the Hugging Face dataset card says CC BY 2.0, while its `dataset_infos.json` and the KLUE paper describe CC0. Do not ingest until this is resolved with the source. It is also user-generated, short-review text and needs PII/quality filtering.
4. **Korean Wikipedia.** The 2020 Korean raw-text collection description reports 5.3M sentences from the Korean Wikipedia dump. A direct Wikimedia dump is a possible share-alike fallback, but retain page/revision attribution and treat CC BY-SA/GFDL separately from the preferred permissive sources.
5. **Korean Parallel Corpus.** The repository provides 31k Bible sentences under CC BY-SA 3.0 plus other parallel sets. It is a narrow religious register and translated text; supplementary only.
6. **Open Korean Historical Corpus.** 17.7M documents and 5.1B tokens, but the dataset is CC BY-NC 4.0, spans 1,300 years and several historical scripts/languages, and is not a default source for a modern, commercially reusable corpus.
7. **HPLT v3 Korean.** 2.34B segments, but CC0 applies to packaging, not underlying web text; legal hold.

The Korea.kr page-level conditions are particularly relevant: KOGL Type 1 itself permits commercial reuse and modification with attribution, but the newer AI-specific terms add conditions for AI training and prohibit resale of training datasets made from the public works. A free public release may be different from resale, but the exact scope should be confirmed before including those records in a redistributable corpus. See [Korea.kr copyright policy](https://www.korea.kr/guide/copyRight.do), [an example 2026 press release with AI conditions](https://www.korea.kr/briefing/pressReleaseView.do?newsId=156788833), and the official [KOGL Type 1 terms](https://www.kogl.or.kr/info/licenseTypeEn.do).

The Korean candidate counts and rights status are recorded in [norwegian-korean-source-counts.csv](data/norwegian-korean-source-counts.csv). The legislation/API route should be measured before deciding whether NIKL access or a share-alike fallback is necessary.

A metadata/body counter is now implemented as `langid32-korean-law-inventory`. It uses the official `lawSearch.do` list endpoint and `lawService.do` body endpoint, stores only law metadata, article counts, rough sentence counts and body hashes, and reads the user-selected OC key from `LAW_API_OC` (never from a command-line argument or repository file).

After registering at the Law Open Data portal and setting the OC key locally:

```sh
export LAW_API_OC='your-registered-OC-value'
langid32-korean-law-inventory --output data/inventory/korean-laws-sample.csv --max-documents 100
```

The 100-document run is a smoke inventory; if the API returns valid counts, remove `--max-documents` for a full current-law inventory. The default one-second delay respects the portal's warning about excessive short-interval requests. This command does not export legal text. A dedicated acquisition/rights issue is open: [#4](https://github.com/SylvainSouche/langid-32/issues/4).

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
| P0 | Common Voice Scripted Speech 27.0 | Natural short sentences; CC0; metadata entry for all 32 targets | Actual TSV rows and `is_used=true` counts remain unmeasured. MDC archive is an MP3 tarball; extract only the TSV. Keep platform/dataset conditions separate from the CC0 licence. |
| P1 | DGT-TM release 2021 (data through 2020) | Large translation-memory volume across all 24 EU languages, including Irish and Croatian | Aligned legal/administrative translation units, not independent sentences; deduplicate and group by EUR-Lex document ID. |
| P1 | Målfrid 2026 | 1.89B Bokmål tokens and 170.2M Nynorsk tokens from 720 Norwegian public-sector domains; NLOD 2.0 | Document-level language ID needs auditing; extract paragraphs/sentences, retain domain/document IDs, PII-check and deduplicate. |
| P1 | Tatoeba CC0 export | Sentence-level CC0 text in 18 target classes; compact weekly export | Small/uneven by language; quality filtering and translation-graph grouping required. |
| P1 | Korean Law Open Data API | Current statutes and administrative rules; underlying official legal texts excluded from copyright by Korean Copyright Act Article 7 | API registration/OC key required; API access and database conditions remain separate; legal register only; exclude court/case data with PII. |
| P2 | Europarl v7 | 21 languages with 387k–2.33M published sentences; document IDs available | 1996–2011 parliamentary proceedings; strong domain/register bias; record the source's reuse statement rather than assuming a formal licence. |
| P2 | JRC-Acquis 3.0 | 22 languages and 463,792 documents | Legislative/legal register; overlaps DGT-TM; review component-level rights and attribution before publication. |
| P2 | Korea.kr KOGL Type 1 press releases | Potential varied modern Korean government text | Per-article licence filtering; AI-specific conditions include attribution and no resale of training datasets; measure volume and confirm free public distribution scope. |
| P2 | NIKL Written Corpus 2025 | 10,293 types of copyright-cleared written works across genres | Access by request; approved-use and redistribution terms not yet verified. |
| P3 / legal hold | HPLT 3.0 | All 32 targets and enormous segment pools; WDS, segment-language and PII annotations | CC0 applies to packaging, not underlying web text. Do not redistribute extracted text without rights/TDM review. |
| P3 | OPUS candidates and other monolingual sources | Potential supplementary volume and domain diversity | OPUS is not a single licence; assess each component's coverage, licence, provenance and translation overlap individually. |

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

A read-only counter is now implemented at `src/langid32/common_voice_inventory.py`. It reads the official release JSON and, when given extracted locale directories, scans `validated_sentences.tsv` without copying sentence text into the report. It records raw rows, non-empty rows, `is_used` counts, length-filter counts, normalized duplicates across all rows and within the active `is_used=true` pool, plus per-locale source/domain counts. Duplicate sets are shared across locale files belonging to the same target class, so the two Chinese locale exports are deduplicated against each other.

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

### Reproducible DGT-TM 2021 inventory

The JRC technical page's download table still ends at **DGT-TM-release 2021** (the 2020 update, five ZIP volumes totalling 583 MB). However, the current [data.europa.eu catalogue](https://data.europa.eu/data/datasets/dgt-translation-memory?locale=en) additionally lists five distributions titled **New Volume 2025 part 1/5** through **part 5/5**. Its metadata still says version 2024 and temporal coverage through 24 March 2024. This is a release-description discrepancy: do not assume the five 2025 volumes replace the 2021 package or that they contain a complete 2025 snapshot. Inspect their access/download metadata and archive contents before choosing the ingestion release. The existing inventory command and notes below describe the documented 2021 ZIP/TMX layout, not yet the 2025 additions. Each volume contains TMX files identified by their EUR-Lex document number; the TMX is UTF-16LE, with language segments in `<tuv xml:lang>` / `<seg>` elements. The source documentation says the extracted files are English-centred parallel translation units; the original source language is unknown, and many documents were originally written in English. The sequence is not the original document order and repeated boilerplate such as “Article 1” occurs. The TMX file name supplies a document-group key.

A read-only streaming counter is implemented as `langid32-dgt-inventory`. It reads TMX directly from the ZIP volumes (no Java/TMXtract step), counts per-language segments and unique normalized text, and retains the EUR-Lex document group for later global splitting. It does not export text or perform PII screening.

```sh
langid32-dgt-inventory \
  --data-root data/raw/dgt-tm-2021 \
  --output data/inventory/dgt-tm-2021.csv \
  --max-files 10
```

The ten-file run is a parser smoke inventory. Remove `--max-files` to process all TMX members in the five release ZIPs. The default length filters match the other source counters. Do not treat the resulting segment totals as independent authored sentences; DGT-TM is one translated legal/administrative source bucket. Sources: https://joint-research-centre.ec.europa.eu/language-technology-resources/dgt-translation-memory_en and https://wt-public.emm4u.eu/Resources/DGT-TM_Statistics.pdf.

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

The source adapter is now implemented as `scripts/stage_tatoeba.py`, with workflow `.github/workflows/tatoeba-ingest.yml`. It downloads the official weekly CC0 and base exports, emits only CC0 sentence text, excludes email/URL/IPv4 matches, flags phone-like and long numeric strings, and records file hashes and sentence IDs without contributor names.

The 14 November 2026 export was staged successfully in workflow run [43931414124](https://github.com/SylvainSouche/langid-32/actions/runs/43931414124). After length and basic privacy filters it produced **80,151 target-language records across 18 classes**:
- English 41,230
- Russian 22,717
- French 14,182
- Finnish 1,545
- Swedish 208
- all remaining represented classes: 57 or fewer each

The base join reported **80,151 originals, zero translations and zero unknown-base rows**. Thus this CC0 subset is useful mainly as an original-sentence supplement; it does not contribute the multilingual translation pairs one might expect from Tatoeba's broader CC BY export. Four email and ten URL matches were excluded; 15 phone-like and one long-number match were flagged for review. The remaining corpus is not fully PII-cleared.

The source page distinguishes the general CC BY 2.0 FR export from the separate CC0 1.0 sentence export. Only `sentences_CC0.csv` is used as text; `sentences_base.csv` contributes grouping metadata only. See https://tatoeba.org/en/downloads and https://downloads.tatoeba.org/exports/.

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

## 5. Global merge pipeline

The single-source `langid32-prepare` command remains useful for CSV/TSV inputs, but it is not the multi-source corpus builder. A merge-first implementation is now available as `langid32-merge` / `python -m langid32.merge`.

The source-neutral staging JSONL contract requires:
- `text`, `language` (one of the 32 project labels)
- `source`, `source_release`
- `group_id` (stable and source-namespaced; shared across languages where applicable)
- `licence_id` (include unresolved rights explicitly)
- `text_origin` (`original`, `translated`, or `unknown`)
- optional `split_group_id` when a source has an existing stable split key that must be preserved
- optional `provenance` object (document/domain/hash/date/quality/privacy metadata)

The merge pipeline normalizes NFC and whitespace, applies common length filters, removes exact normalized duplicates across all inputs within each language, assigns deterministic group-level train/validation/test splits, and applies the 20,000-per-language cap only after global deduplication. It writes three text-only split files and an internal `records.jsonl` sidecar retaining group, licence and source provenance. It reports source contributions and duplicate counts; it does not apply hidden source quotas or silently prioritize a source.

Source adapters must preserve a shared group key across languages when the underlying source group is shared. FineWeb2 uses its hostname hash as `split_group_id` so the original validated split assignment remains unchanged; its source-namespaced `group_id` is retained separately. Other sources should use their stable document/translation group IDs.

## 6. FineWeb2 integration result

The adapter is `scripts/stage_fineweb2.py`. It joins each selected sentence to the provenance sidecar, maps the exact FineWeb2 subset identifiers to project language labels, retains hashed document/URL provenance and the hostname group, and marks the licence as `ODC-By-1.0;underlying-crawled-text-rights-unresolved`.

Workflow `.github/workflows/corpus-integrate-fineweb2.yml` downloaded the verified source artifact from assembly run 43929112868, ran the test suite, staged the 620,000 non-English records, and executed the global merge. The completed baseline workflow is run [43930504989](https://github.com/SylvainSouche/langid-32/actions/runs/43930504989); its private artifact was `fineweb2-global-candidate-v1`.

Baseline result:
- 31 languages, exactly 20,000 records each (620,000 total)
- each language: 16,000 train / 2,000 validation / 2,000 test
- zero records rejected by the common normalization/length stage
- 77,767 distinct hostname groups
- no exact within-language duplicates remaining

FineWeb2's ODC-By licence for the dataset/compilation does not settle rights in underlying crawled pages. Its deterministic row-group sample is not statistically representative of each full language subset. Phone-like and long-number flags are retained in internal provenance and still require review. Do not publish or redistribute the text at this stage.

## 7. Two-source 32-language candidate

Tatoeba's CC0-only export has now been staged and merged with FineWeb2. The integration workflow downloads the FineWeb2 baseline artifact and the Tatoeba staging artifact, runs the common tests, performs cross-source exact deduplication, recomputes deterministic group splits, and enforces exact counts for all 32 languages. It retains both source manifests in the candidate artifact.

The completed run is [43931843065](https://github.com/SylvainSouche/langid-32/actions/runs/43931843065). Artifact: `multisource-candidate-v1` (artifact ID 14259711049; 14-day retention).

Verified result:
- **32 languages × 20,000 = 640,000 records**
- every class has exactly 16,000 train / 2,000 validation / 2,000 test
- 157,918 source groups across the merged candidate
- no records rejected by the common merge stage
- no exact normalized within-language duplicates across the two source inputs
- no source quotas; source contributions are deterministic and reported in the manifest

Source contributions after the cap:
- English: 20,000 Tatoeba CC0
- Russian: 10,555 Tatoeba CC0 / 9,445 FineWeb2
- French: 8,287 Tatoeba CC0 / 11,713 FineWeb2
- Finnish: 1,431 Tatoeba CC0
- Swedish: 204 Tatoeba CC0
- the other 27 classes receive at most 57 Tatoeba rows each; FineWeb2 supplies the balance

Tatoeba's 80,151 staged target-language records were all marked as originals by the source base relation; no translated or unknown-base records were present in this CC0 subset. The CC0 subset therefore adds English coverage and some additional original-sentence variety, not a large parallel-text component. The broader Tatoeba CC BY export was not ingested.

This is the first complete 32-class technical candidate, **not** a release-ready corpus. FineWeb2's underlying crawled-text rights remain unresolved. Tatoeba's included sentence text comes from the CC0 1.0 export. Text-level privacy, language quality, domain balance and source-specific rights/attribution still require review. The internal provenance sidecar must remain private until PII review.

## 8. Next ingestion sequence

1. **DGT-TM release selection**: resolve the discrepancy between the JRC technical page, whose download table ends at the 2021 release, and the data.europa.eu catalogue, which lists five additional distributions titled “New Volume 2025 part 1/5” through “part 5/5” while retaining version-2024 metadata and temporal coverage through 24 March 2024. Inspect the 2025 access/download metadata and archive contents before deciding whether those volumes supplement or replace the 2021 package. Then parse the selected TMX release(s) for the 24 EU languages, retaining EUR-Lex document grouping and translated/parallel origin.
2. **Målfrid 2026**: process Bokmål and Nynorsk separately; retain document/domain grouping and NLOD attribution metadata; sentence-segment the JSONL, run PII screening and compare overlap with FineWeb2.
3. **Common Voice v27**: obtain the original MDC archives through the authorised route; extract only the text TSV; count active `is_used=true` sentences and preserve sentence IDs and locale provenance. Do not download or retain audio.
4. **English**: Tatoeba now fills the English class, but its source mix is entirely CC0 user-contributed originals. Add Common Voice English if its usable volume and terms are suitable; evaluate original FineWeb separately only if needed, with the same underlying-rights caveat.
5. **Korean**: use FineWeb2 as the current baseline while pursuing a better-documented Korean source; do not block the pipeline on the inaccessible Korean Law portal registration.
6. Produce a per-language/per-source coverage, domain, quality, privacy and overlap report before setting source quotas or selecting a final 20,000 examples per class.

The next investigation is DGT-TM release identity, not blind ingestion of the 2021 files. Once the 2025 distributions are understood, DGT-TM is still the best next text source to add because it contributes a distinct translated legal/administrative domain across 24 EU languages.

## FineWeb2: priority multilingual web source

FineWeb2 now has a read-only metadata inventory tool and a target-language distribution snapshot in `docs/data/fineweb2-target-distribution-v2.1.1.csv`. See [FineWeb2 inventory and acquisition notes](fineweb2-inventory.md). The published table provides filtered train, test and removed document counts and Parquet sizes without downloading any Parquet data. In the current mapping, exact filtered subsets are published for 31 target classes; English is separately served by original FineWeb. Estonian and Latvian use the FineWeb2 subset identifiers `ekk_Latn` and `lvs_Latn`. Korean has 60.9M filtered-train documents; Irish 646.8k; Maltese 489.2k; Nynorsk 1.21M; Bokmål 38.1M. These are document counts, not sample counts. The filtered train split is the candidate pool; keep the test split out of training and do not assume the `_removed` subset is clean.


FineWeb2's pinned target-language distribution CSV reports 4,498,336,994 filtered-train documents across the 31 exact target subsets, occupying approximately 8.57 TB of Parquet data. This is a metadata sum, not a recommended download: acquisition must be bounded to a small, reproducible sample per language.


## Current merged candidate: v4

GitHub Actions run [43938190407](https://github.com/SylvainSouche/langid-32/actions/runs/43938190407) produced artifact `multisource-candidate-v4-unicode-pii-clean`. This is a bounded technical candidate, not a public release.

| Source | Final rows | Source coverage |
|---|---:|---|
| FineWeb2 v2.1.0 | 510,702 | 31 target languages |
| DGT-TM release 2021 | 92,196 | 24 EU official languages |
| Tatoeba CC0 export, 2026-11-14 | 37,102 | 18 staged; 17 retained |
| **Total** | **640,000** | **32 target classes** |

All 32 classes have exactly 16,000 train, 2,000 validation and 2,000 test records. The final output contains 186,190 source groups; 241,195 groups were present before the per-language cap. Group IDs are split-consistent across languages. Exact normalized-text duplicates within a language were absent, and no cross-source duplicate pairs were recorded.

### Source-specific notes

- **FineWeb2:** 510,702 final records. The extraction used the original v2.1.0 Parquet files and a 20,100-per-language buffer to allow global privacy filtering without reducing the final class counts. English is not in FineWeb2's 31-class sample.
- **DGT-TM 2021:** five official ZIP volumes (596,532,514 bytes) containing 2,445 TMX files and 564,332 translation units were processed. The staging sample was 5,000 records per each of the 24 EU official languages, capped at 20 segments per TMX document and language. The final merge retained 92,196 DGT-TM records. The original language of a segment is not identified by this extraction; treat the text as translation-memory material, not necessarily original prose. Segments may be fragments, boilerplate or translationese.
- **Tatoeba:** the CC0 export yielded 80,151 staged records; 37,102 were retained in the final candidate. It supplies all 20,000 English records, plus substantial Russian and French contributions and smaller additions in other supported languages.

### Privacy and deduplication audit

The global merge excluded 11 email matches and 31 URL matches. An independent scan of the final 640,000 records found no remaining email addresses, URLs or valid IPv4 addresses. Phone-like and 9+ digit numeric sequences are not blanket-excluded; 1,006 and 676 occurrences respectively remain flagged in the internal provenance sidecar for review.

An earlier three-source candidate was superseded after an independent scan found Unicode email addresses and URLs attached directly to preceding text. The v4 email and URL patterns account for Unicode local parts and missing whitespace; the URL pattern also avoids treating an ordinary word ending in `awww.` as a web address.

### Rights and next integrations

- FineWeb2's ODC-By compilation terms do not settle the rights in the underlying crawled text.
- DGT-TM 2021 is reused under European Commission reuse conditions and attribution requirements; it is not CC0.
- Tatoeba records in this pipeline come from the CC0 export.
- The candidate is not rights-cleared and must not be treated as a redistributable corpus yet.

Only the documented 2021 DGT-TM package is included. Newer 2025 catalogue entries have not yet been reconciled with the JRC release documentation. Common Voice v27 and Målfrid 2026 remain the next source integrations; Common Voice must be obtained from the original Mozilla Data Collective distribution.

The independent post-run review of v4 found 94 exact text strings (194 records) assigned to multiple language labels, measurable FineWeb2 hostname concentration in Maltese, Nynorsk and Irish, and 1,619 records with phone-like or long-number review flags. See [the candidate v4 audit](candidate-audit-v4.md) before treating the balanced row counts as evidence of balanced language quality.
