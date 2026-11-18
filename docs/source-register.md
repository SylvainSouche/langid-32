# Source register — canonical status

**Last reconciled: 18 November 2026.** This is the canonical index of every dataset/source family actually acquired, staged, sampled, investigated, rejected, or retired for langid-32. It supersedes the source-discovery and acquisition-priority narrative in older inventory documents. Historical audit reports remain available but are not current source-status statements.

Status vocabulary:
- **STAGED** — an acquisition or sample artifact exists; this does not mean the source is legally cleared.
- **PILOT** — limited technical sample; not part of a release-ready corpus.
- **INVESTIGATED** — documentation/catalogue examined, but no usable text has been acquired into the current candidate pipeline.
- **HOLD** — technically acquired or sampled, but rights/terms or required attribution remain unresolved.
- **NOT PURSUED / RETIRED** — route was considered but is not part of the current acquisition plan.
- **FAILED** — attempted acquisition did not yield usable source data.

No source in this register is automatically approved for public redistribution. The current global corpus has not been rebuilt from all current artifacts.

## 1. Acquired and staged sources

| Source family / release | Languages | Actual project use and measured state | Rights / attribution state | Current decision |
|---|---|---|---|---|
| **Common Voice 22.0**, third-party HF conversion `fsicoli/common_voice_22_0` | Pilot across 33 labels; combined CV pilot has 34 | Refreshed text-only artifact [44293665775](https://github.com/SylvainSouche/langid-32/actions/runs/44293665775), artifact 14423311681: 259,352 rows. All 34 requested locale files resolve to immutable HF revision `ae911de250fe9375d08e2daa2105b671d659d446`; each row now retains locale, upstream sentence ID, per-locale TSV SHA-256 and revision. No audio or speaker metadata. | Underlying text identified as CC0, but Mozilla terms and third-party conversion chain are separate. Romanian MDC acceptance must not be generalized to other locales. | **PILOT / HOLD** pending locale-specific terms and conversion-chain assessment. No complete-dataset mirroring. |
| **Common Voice 27.0**, Croatian subset | Croatian (`hr`) | 1,724 rows in the combined 261,076-row pilot. Archive SHA-256 and validated-sentences TSV SHA-256 are retained in the provenance sidecar; the row group ID is a candidate-record hash, not the upstream sentence ID. | Croatian locale-specific terms acceptance is not recorded. The source manifest records the dataset ID and verified archive checksum; Romanian MDC acceptance is not applicable. | **PILOT / HOLD** pending Croatian-specific terms confirmation. |
| Common Voice 27.0 metadata catalogue | 33 locale metadata entries / 32 mapped labels in snapshot | Metadata-only inventory (9,711,592 validated-sentence metadata rows); not itself a text acquisition. | Catalogue does not establish the terms of each acquired text locale. | **INVESTIGATED**; do not count metadata as corpus rows. |
| **Tatoeba CC0 export**, 14 November 2026 refresh | 18 represented target labels | Run [44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591), artifact 14345216923: 80,155 staged rows. Only `sentences_CC0.csv` rows emitted; base export used only for translation grouping. | CC0-1.0 applies to this separate CC0 export. General Tatoeba export is CC BY 2.0 FR and was not ingested. Scholarly citation recommended, not legally required by CC0. | **STAGED**; candidate source for merge. |
| **DGT-TM 2021** | 24 EU official languages | Run [44291075180](https://github.com/SylvainSouche/langid-32/actions/runs/44291075180): 120,000 staged translation units, 5,000 per language. Sentence/subsentence translation-memory segments, not independent natural-document sentences. | European Commission reuse conditions: source/date attribution and Commission ownership notice. Not CC0. Exact mandatory notice must be captured verbatim. | **STAGED / ATTRIBUTION REQUIRED**; verify exact terms and source notice before release. |
| **FineWeb2 v2.1.1** | 31 target classes; English handled by FineWeb | Legacy v5 candidate: 510,702 rows. Additional 50,000 Catalan and 50,000 Icelandic technical candidates in waiting-source run [44241908630](https://github.com/SylvainSouche/langid-32/actions/runs/44241908630). | ODC-By-1.0 describes dataset/compilation; does not establish rights in individual crawled passages. URL is provenance, not permission. No documented excerpt-level rights clearance. | **HOLD**. Do not count toward redistributable corpus until passage-level rights route is established. |
| **FineWeb v1.4.0** | English | 20,000 selected sentences staged; v5 retained 5,968. Bounded extraction across 24 shards / 24 crawl dumps. | ODC-By-1.0 compilation terms; underlying Common Crawl page rights unresolved. | **HOLD**; same excerpt-level rights gate as FineWeb2. |
| **Målfrid 2026** | Norwegian Bokmål (`nb`), Nynorsk (`nn`) | Both archives downloaded and hashed. Waiting-source run selected 50,000 candidates per label. Archive sizes: Bokmål 4,056,002,560 bytes; Nynorsk 358,758,400 bytes. | NLOD 2.0 attribution; database-rights treatment differs from ordinary text licence. Embedded third-party content and personal data may be outside grant. Need document-level title/issuer/date/URL and domain provenance. | **STAGED / ATTRIBUTION REQUIRED**; sole source in each current Norwegian batch, so source diversity fails. |
| **IGC2024 Filtered-1** | Icelandic | Downloaded archive, SHA-256 recorded; waiting-source run selected 50,000 candidates. | CC BY 4.0 recorded at corpus level; source-article rights and any embedded third-party material require review. Preserve article/work metadata and CC BY attribution/change notice. | **STAGED / HOLD** pending exact source-level rights/attribution assessment. |
| **GreynirCorpus 21.06 / 1.1** | Icelandic | Downloaded tar archive, SHA-256 recorded; 4,930 additional candidates in waiting-source run. News and government-site material, 2015–2021. | CC BY 4.0 recorded at corpus level; news article rights may differ. Corpus metadata alone is insufficient to clear every article. | **STAGED / HOLD** pending article-level rights assessment. |
| **TeMU-BSC catalan_CC0_sentences** | Catalan | Repository cloned and sampled; 177,726 candidates in waiting-source run across selected files. | Repository-level CC0 label is not assumed to cover every constituent identically. Constituent datasets, waivers and upstream origins differ. | **STAGED / HOLD** until constituent-level source and waiver mapping is complete. |
| **BSC-LT Legal Catalan-Spanish Parallel Corpus** | Catalan | Three files acquired/sampled: DOGC, cleaned legal corpus and APDCAT documents; 50,414 candidates in waiting-source run (50,000 DOGC + 414 APDCAT; confirm per-file manifest for any other constituent). | HF/repository CC BY 4.0 is not treated as blanket clearance. DOGC government terms and APDCAT data-sharing agreement need separate confirmation. | **STAGED / HOLD** pending file- and constituent-level terms. |
| **Catalan-DPO-V2** (`catallama/Catalan-DPO-V2`) | Catalan | Assistant `messages` and `chosen` content only; 30,790 candidates in waiting-source run. Rejected responses are not used. | HF metadata Apache-2.0 does not establish copyright/licence for underlying dialogue text. | **STAGED / HOLD** pending upstream provenance and text rights. |
| **Wikimedia Korean Wikipedia** (2023-11-01 dump) | Korean | Streamed up to 500,000 articles; 50,000 paragraph candidates selected in waiting-source run. | CC BY-SA / GFDL obligations, revision attribution and share-alike compatibility unresolved. | **STAGED / HOLD**; not an approved permissive source. |
| **UN Arabic-English Filtered** (`ymoslem/UN-Arabic-English-Filtered`) | Arabic | Full train split streamed; 50,000 Arabic text candidates selected in waiting-source run. | HF card reports CC BY 4.0; underlying UN source terms and attribution not confirmed. HF wrapper metadata is insufficient. | **STAGED / HOLD** pending authoritative UN reuse terms. |

### Artifact accounting — do not add these totals

- Waiting-source run [44241908630](https://github.com/SylvainSouche/langid-32/actions/runs/44241908630), artifact 14403758073: **613,860** candidates across Catalan (258,930), Icelandic (104,930 including 50,000 FineWeb2), Bokmål (50,000), Nynorsk (50,000), Korean (50,000), Arabic (50,000). The 613,860 figure includes the FineWeb2 Catalan and Icelandic samples; the non-FineWeb2 subtotal is 513,860.
- Common Voice mixed text pilot [44293665775](https://github.com/SylvainSouche/langid-32/actions/runs/44293665775): **261,076** rows, including 259,352 CV22 and 1,724 Croatian CV27.
- Tatoeba CC0 refresh [44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591): **80,155** rows.
- DGT-TM refresh [44291075180](https://github.com/SylvainSouche/langid-32/actions/runs/44291075180): **120,000** rows.
- Historical v5 candidate [43950037392](https://github.com/SylvainSouche/langid-32/actions/runs/43950037392): **640,000** rows (32 labels × 20,000), comprising FineWeb2 510,702; DGT-TM 91,539; Tatoeba CC0 31,791; FineWeb 5,968. It is a historical candidate, not a current source count and not release-ready.

Artifacts overlap in source content and have not been globally deduplicated against each other. Never sum them to claim a unique corpus size.

## 2. Investigated but not acquired into the current candidate corpus

| Source / family | Scope of investigation | Status / reason not currently used |
|---|---|---|
| **HPLT 3.0** | Catalogue and language coverage inspected; very large Common Crawl/Internet Archive-derived multilingual segments. | **INVESTIGATED / NOT ACQUIRED**. CC0 packaging/metadata does not clear underlying passages. Do not list as an active staged source or imply that HPLT text has been ingested. |
| **JRC-Acquis 3.0** | Coverage, corpus structure and Commission reuse conditions reviewed. | **INVESTIGATED / NOT ACQUIRED**. Component-level rights and exact Commission notices need work; not in current staging artifacts. |
| **Europarl v7** | Language coverage, document IDs and source statement reviewed. | **INVESTIGATED / NOT ACQUIRED**. Project's statement that it is unaware of restrictions is not a formal licence grant; no current staging artifact. |
| **OPUS catalogue** | Reviewed as an aggregator and possible route to parallel corpora. | **INVESTIGATED / NOT ACQUIRED**. Each component has separate licence/provenance; no indiscriminate OPUS ingest. |
| **Leipzig Corpora Collection** | REST API probe [44294431022](https://github.com/SylvainSouche/langid-32/actions/runs/44294431022), artifact 14423405978: 104 catalogue entries; corpora for 20/34 target labels; 29/30 sentence-service probes successful; response includes per-sentence source ID, URL and date. No sentence text retained. | **INVESTIGATED / API TECHNICALLY VIABLE / RIGHTS HOLD**. API OpenAPI labels the service CC BY 4.0, but this does not clear underlying news/web/Wikipedia works. No Leipzig text acquired. See [REST API audit](leipzig-rest-api-audit-2026-11-18.md). |
| **Nynorskkorpuset / randomized Nynorsk corpus** | Catalogue inspected; 3.3M sentences reported, lemmatized/tagged. | **INVESTIGATED / NOT ACQUIRED**. CC BY 3.0 but processed/annotated text is not a clean raw-text substitute. |
| **Målfrid 2021–2025 parallel data** | Translation-unit counts inspected (English–Bokmål, English–Nynorsk, Bokmål–Nynorsk). | **INVESTIGATED / NOT ACQUIRED** in current artifacts; potentially useful only with translation-aware grouping and NLOD/database review. |
| **Korean NSMC** | Conflicting claims across repository, HF card and paper/metadata (unclear original licence vs CC BY 2.0 vs CC0). | **HOLD / NOT ACQUIRED**. Exclude until resolved by rights holder in writing. |
| **NIKL Written Corpus 2025** | Access-by-request catalogue and terms considered. | **INVESTIGATED / NOT ACQUIRED**. No written approval permitting redistribution. |
| **Korean Parallel Bible** | CC BY-SA 3.0 corpus identified. | **INVESTIGATED / NOT ACQUIRED**. Share-alike, translation and publisher attribution need assessment; translationese makes it supplementary only. |
| **Korean Open Historical Corpus** | CC BY-NC 4.0 terms identified. | **REJECTED for intended unrestricted release** due non-commercial restriction. |
| **UN source corpora (UNPC / MultiUN)** | Identified as upstream origins of the Arabic-English HF derivative. | **RIGHTS INVESTIGATION**. Underlying UN reuse terms are not established by the derivative HF card. |
| **Common Crawl / web pages underlying FineWeb, FineWeb2 and HPLT** | Passage-level rights question identified; dataset schemas expose source URLs and crawl metadata. | **LEGAL HOLD**. No verified systematic excerpt-level licensing or clearance in those upstream pipelines. |

## 3. Routes explicitly not pursued / retired

| Route | Decision |
|---|---|
| **Korea.kr / KOGL government legal/news portal article scraping** | **NOT PURSUED.** This was a research lead only; no article corpus was acquired and no records from this route are in the current staging artifacts. Remove it from active acquisition priorities and from claims about the corpus. The old `korean_law_inventory.py` implementation/tests are historical exploratory code, not an active data source. |
| **Korean Law Open Data API** | **NOT PURSUED for current build.** No measured corpus or API acquisition exists; statutory public-domain provisions do not resolve API terms/database rights. Do not spend further acquisition effort unless explicitly reopened. |
| Mozilla Data Collective as a general multi-locale acquisition route | **RETIRED.** Do not restart the old MDC workflow or infer acceptance across locales. The only retained CV27 subset is the separately documented Croatian pilot; Romanian terms acceptance is locale-specific and not a corpus acquisition authorisation for other locales. |
| Full Common Voice mirroring / audio and speaker metadata | **EXCLUDED.** The project uses text-only selections; no audio, speaker identifiers or demographic metadata are to be staged or redistributed. |
| FineWeb original outside English | **NOT APPLICABLE**; English-only source. FineWeb2 is the multilingual route. |

## 4. Current acquisition priorities

1. **Do not acquire more sources blindly.** First reconcile immutable revisions, per-file manifests, licence evidence and provenance for the staged sources above.
2. **Diversify source mix** in Catalan, Icelandic, Bokmål, Nynorsk, Korean and Arabic. Current waiting-source samples are concentrated: TeMU is large in Catalan; IGC dominates non-FineWeb2 Icelandic; Målfrid is the only source in each Norwegian batch; Wikipedia is the only Korean source; UN-derived data is the only Arabic source.
3. **Resolve the non-web source holds**: BSC constituent terms, TeMU constituent waivers, Catalan-DPO text rights, Greynir article rights, IGC source-document provenance, Målfrid database/third-party terms, Korean Wikipedia share-alike, UN source terms.
4. Keep FineWeb/FineWeb2/HPLT out of a redistributable release unless a defensible excerpt-level rights process is established; their compilation licences are not passage licences.
5. Only then rebuild the global 34-label candidate with common privacy, language, deduplication, group-split and source-quota rules.

## 5. Where to find the rest of the evidence

- Measured run-level results and historical candidate audit: [corpus status](corpus-status-2026-11-17.md), [candidate audit v5](candidate-audit-v5.md), [candidate audit v4](candidate-audit-v4.md).
- Web source metadata and technical extraction: [FineWeb inventory](fineweb-inventory.md), [FineWeb2 inventory](fineweb2-inventory.md).
- Rights and exact attribution work: [source attribution register](source-attribution-register.md), [Hugging Face licensing policy](huggingface-licensing.md), [web-text release controls](web-text-release-controls.md).
- Acquisition implementation: `scripts/acquire_waiting_sources.py`, `scripts/stage_tatoeba.py`, `src/langid32/dgt_tmx_stage.py`, and the corresponding workflow files.
- Leipzig API and excerpt-provenance inspection: [Leipzig REST API audit — 18 November 2026](leipzig-rest-api-audit-2026-11-18.md).\n- Direct integration schema/provenance inspection: [integration preflight — 18 November 2026](integration-preflight-2026-11-18.md). It records why the waiting-source artifact is not yet mergeable and the 12 Common Voice locale revisions that remain unresolved.\n- This file is the current status index. Older discovery narratives and audit documents are historical evidence, not live priorities.
