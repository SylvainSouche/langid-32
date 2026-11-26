# Source catalogue and per-language sentence matrix

**Prepared:** 26 November 2026  
**Repository:** `SylvainSouche/langid-32`  
**Purpose:** source-by-source operational inventory. This file separates (1) actual sentence/segment counts, (2) document/paragraph/token audit measures, (3) staged historical rows, and (4) current-pipeline ingestion. These are not interchangeable.

## Counting rules

- A number is called a **sentence count** only when the source audit or acquisition manifest actually counted sentence/segment records. Translation units and sentence segments are identified as such; documents, paragraphs, tokens and heuristic sentence splits are not silently converted into sentences.
- `not measured` means the checked-in evidence does not provide a source × language sentence count. It does **not** mean zero or unavailable source material.
- `not integrated` means the source has audit/sample evidence but no active production adapter in the current staged workflow.
- Historical artifacts are not clean-run inputs except for the four explicitly pinned snapshots (v5, Leipzig, Tatoeba CC0 and DGT-TM) described in the pipeline contract.
- A technical candidate is not automatically rights-cleared for redistribution. Keep the source's licence, underlying-work rights, attribution and project selection decision distinct.

## Source-by-source catalogue

### Common Voice 22.0 — HF-hosted text conversion (`fsicoli/common_voice_22_0`)

**Description.** Text-only extraction from `transcript/<locale>/validated_sentences.tsv`; no audio, clip paths, speaker/client identifiers or demographic metadata. The current adapter resolves and records an immutable HF revision, TSV hashes and sentence IDs. Common Voice 22 has five upstream locales; Croatian (`hr`) is absent from this release. This is the sole source-specific language availability exception.

**Sentence/segment matrix (current source acquisition):**

| Language | Count/evidence |
|---|---:|
| Finnish (fi) | not measured in a current full run; provider inventory below 20,000 |
| Greek (el) | not measured in a current full run; provider inventory below 20,000 |
| Maltese (mt) | not measured in a current full run; provider inventory below 20,000 |
| Slovenian (sl) | not measured in a current full run; provider inventory below 20,000 |
| Icelandic (is) | not measured in a current full run; provider inventory below 20,000 |
| Other 29 configured labels | not in current Common Voice locale matrix |

Historical pilot: 259,352 rows across 33 labels; it is not reused as a current clean-run acquisition count. The current 20,000/source/language value is a ceiling, not a claim that the source contains that many rows.

**Licence and attribution.** HF dataset card declares CC0-1.0 for this specific conversion. This is not a claim about every Common Voice release. Cite Ardila et al. (2020) as recommended. No per-locale terms acceptance gate is used for this HF-hosted conversion.

**Pending questions/checks.** First clean run must record actual eligible counts, provider exhaustion and source hashes for each of the five locales. Retain the user-approved text-only scope. No Croatian Common Voice input is approved. Mozilla Data Collective and Mozilla-hosted data remain voluntarily excluded by project decision.

### Tatoeba — CC0 sentence export (14 November 2026 refresh)

**Description.** Only `sentences_CC0.csv` rows are emitted; the base export is used for translation grouping, not as a second text source. Historical staged artifact: 80,155 rows.

**Sentence matrix.** The historical artifact represents 18 target labels, 80,155 rows total. The checked-in source register does not provide a verified per-language breakdown; therefore every per-language count remains **not measured in the available checked-in evidence**. Do not divide 80,155 evenly or infer counts from the 18-label coverage.

**Licence and attribution.** CC0-1.0 applies to the separate CC0 export. The general Tatoeba export is CC BY 2.0 FR and was not ingested. Scholarly citation is recommended, not a CC0 legal condition.

**Pending questions/checks.** Extract and publish the artifact manifest's exact language counts, deduplication counts and provenance. Confirm the current historical snapshot validation and candidate-boundary results. No blanket use of the general export.

### DGT-TM 2021

**Description.** Translation-memory units staged from the 2021 DGT-TM release. Historical refresh: 120,000 translation units, exactly 5,000 per each of the 24 EU official languages. These are sentence/part-sentence translation units; source-language identity is not reliably known and some units may originally have been English.

**Sentence/translation-unit matrix.** The historical staging evidence records **5,000 units each** for: bg, cs, da, de, el, en, es, et, fi, fr, ga, hr, hu, it, lt, lv, mt, nl, pl, pt, ro, sk, sl, sv. These are staged translation units, not necessarily 5,000 independent original-language sentences. The former source-language allowlist has been removed. The DGT adapter must retain all target-language translation units it actually encounters; source-native language coverage and translation-unit counts are reported from the archive rather than configured allowlists.

**Licence and attribution.** JRC reuse conditions grant non-exclusive, free worldwide reuse of the DGT-TM database and structured elements under Commission Decision 2011/833/EU. Required attribution includes the source website, latest-update date and statement that the European Commission retains ownership. This does not automatically clear every underlying source document; some material is outside the Acquis.

**Pending questions/checks.** Restore all approved language coverage rather than silently restricting to five labels; confirm each TMX NumDoc mapping and source-document provenance; apply the Commission attribution; distinguish translationese/part-sentence content in reports; report exact post-filter eligible counts.

### Leipzig Corpora Collection — Leipzig Wikipedia and Leipzig News

**Description.** Two distinct original sources: `leipzig_wikipedia` and `leipzig_news`. A pinned historical artifact contains the earlier 34-label acquisition. The historical source register says 3,000 news plus 3,000 Wikipedia sentences per language in the subset then retained. The pipeline no longer applies a project-language allowlist to either Leipzig source. The historical artifact is validated against all configured labels; only genuine upstream absence may yield an empty source/language cell.

**Sentence matrix.** Historical artifact: 3,000 news + 3,000 Wikipedia rows for each of hr, fi, el, mt, sl, is (36,000 rows across these six labels if the artifact is exactly as described). The artifact also contains the earlier 34-label acquisition, but the source register/config do not provide a verified per-language/per-source breakdown for all 34 in the checked-in summary. For the other 28 labels: historical artifact rows exist, but current pipeline rules discard them. Do not describe those cells as source-empty.

**Licence and attribution.** Leipzig's official downloadable-corpora usage statement declares CC BY 4.0. Attribute Leipzig, link the licence/usage statement, cite Goldhahn et al. (LREC 2012), and preserve archive IDs, hashes, sentence/source mappings, URLs and timestamps.

**Pending questions/checks.** The six-language allowlist has been removed from the config and workflow. All 31 FineWeb2 subsets and all configured Leipzig language labels are now scheduled; the remaining verification is that the adapter and source manifest report actual upstream availability rather than filtering by project policy. The pinned artifact's complete JSONL validation remains a preflight gate because the 1.45 GB artifact exceeded the connector's 512 MB inspection limit. Report exact per-language × source counts after validation; do not treat the historical 3,000-per-source counts as current caps.

### FineWeb2 v2.1.1

**Description.** Multilingual Common Crawl-derived web-text dataset. The historical v5 artifact contains 510,702 FineWeb2 rows across 31 labels. A historical waiting-source artifact also contains FineWeb2 samples for Catalan and Icelandic. The current configuration and workflow schedule all 31 FineWeb2 non-English subsets available for project labels; no project-language allowlist is applied.

**Sentence matrix.** Historical v5 total: 510,702 rows across 31 labels; the checked-in summary does not provide a complete 31-language breakdown. Current fresh matrix: all 31 available non-English project subsets are scheduled; exact eligible sentence counts are not yet measured by a successful clean full run. English is naturally separate in FineWeb, not a FineWeb2 language subset.

**Licence and attribution.** ODC-BY 1.0 applies to the database/compilation, not automatically to individual page contents (ODC-BY §2.4). The dataset card also points to Common Crawl Terms of Use. The underlying web-page rights are not individually established by the compilation licence. This uncertainty is a rights-review question; it is not evidence that all crawled text is categorically prohibited. Keep rights status distinct from technical candidate eligibility and from the project's inclusion decision.

**Pending questions/checks.** Remove the unsupported six-language restriction unless it is an explicit, user-approved operational choice. Restore approved source/language coverage and the first-pass 20,000 eligible unique rows per original source × language. Retry transient 408/429/5xx and network failures at row-group boundaries with bounded backoff and no double-counting. Record shard LFS hashes, source URLs/domains and all per-language counts. Preserve a separate rights/attribution review flag; do not silently turn it into a source deletion or a blanket legal conclusion.

### FineWeb v1.4.0 (English)

**Description.** English-only historical sample: 20,000 selected sentences staged; historical v5 retained 5,968. Bounded extraction across 24 shards / 24 crawl dumps.

**Sentence matrix.** English: 20,000 historical selected rows; 5,968 retained in v5. Current pipeline: explicitly excluded by `source_rules.fineweb.exclude=true`, so current clean-run count is zero by configuration, not because upstream English material is absent.

**Licence and attribution.** ODC-BY 1.0 covers the database/compilation, not individual page contents. Common Crawl terms apply to crawled content; the source register notes that the reviewed paper/card does not document page-level rights clearance or a complete takedown workflow.

**Pending questions/checks.** This is a source-selection/legal-review hold that currently leaves English without an active source. Decide whether English web text is to be evaluated as a private technical candidate under the same careful provenance/rights flagging, or remains excluded by an explicit project decision. Do not describe the ODC-BY database licence as clearing individual passages.

### Målfrid 2026

**Description.** Norwegian Bokmål and Nynorsk archive. Full upstream structural audit: Bokmål 1,358,513 documents / 65,028,075 paragraphs / 1,889,421,910 local whitespace tokens; Nynorsk 191,976 documents / 7,311,579 paragraphs / 170,414,602 tokens. Combined 1,550,489 distinct document IDs. These are not sentence counts.

**Sentence matrix.** nb: sentence count not measured; nn: sentence count not measured. Document/paragraph/token audit measures above are not to be relabelled as sentence totals. Current adapter is active for both nb and nn.

**Licence and attribution.** NLOD 2.0 attribution. Database-rights treatment differs from ordinary text licensing; embedded third-party content and personal data may be outside the grant. Preserve doc_id, doc_hash, URL, date, domain, mimetype, language and paragraph structure.

**Pending questions/checks.** First production adapter run must report extracted sentence counts, filtering and quota/exhaustion per nb/nn. Review third-party content and personal data; retain attribution and source-document provenance. Do not omit either Norwegian label.

### IGC2024 Filtered-1

**Description.** Icelandic open-access filtered corpus. Full archive scan: 1,848,767 documents, 795,692,549 local whitespace tokens, 4,894,921,673 characters; one exact-text duplicate row. These are document/token/character measures, not sentence counts. Current adapter is active.

**Sentence matrix.** is: sentence count not measured in the checked-in audit; other labels: not applicable. Do not convert token or document totals into sentence counts.

**Licence and attribution.** The Filtered-1 open-access portion is CC BY 4.0. Preserve TEI archive/path, source, altered flag and publisher attribution where required. Filtered-2 is a separate release and remains excluded because its custom licence prohibits raw-text republication.

**Pending questions/checks.** Production parser must emit sentence counts and quota/exhaustion, retain TEI provenance and source attribution, and verify the pinned archive. Keep Filtered-1 and Filtered-2 distinct.

### GreynirCorpus — Copper and Silver (Icelandic)

**Description.** Pinned Git-LFS-backed Copper (10 files) and Silver (1 file) source partitions. Adapter validates checkout revision, LFS object SHA-256 and byte sizes, parses terminal text and groups by original article URL. Gold development/test and extra heading/short partitions are excluded. Historical 4,930 Gold rows are not current input.

**Sentence matrix.** is: exact sentence count not yet measured by the production adapter. Historical Gold dev/test: 4,930 rows were observed in an earlier implementation and are explicitly excluded. Copper/Silver production extraction remains first-run verification. Other labels: not applicable.

**Licence and attribution.** CLARIN/Greynir README state CC BY 4.0; attribute Miðeind ehf. Text was extracted from news and government sites (2015–2021), so retain article URLs and any source-specific rights status. Do not treat the corpus-level CC BY statement as resolving every underlying article right.

**Pending questions/checks.** First production run must prove all 11 LFS objects hydrate, parse, and report quota reached or genuine exhaustion. Preserve article URL, corpus/local IDs, file path/hash, pinned revision and attribution. Do not reintroduce Gold dev/test.

### MaCoCu 2.0 — Croatian, Maltese and Slovenian

**Description.** Three distinct locale archives (MaCoCu-hr, MaCoCu-mt, MaCoCu-sl), with XML-in-ZIP streaming adapter. It retains document URL/ID, paragraph ID, quality, raw lm_score, sensitive flag, language and heading metadata; filters flagged-sensitive paragraphs, explicit headings and missing/non-target language before source/language quota. The user approved all three for the current candidate pipeline.

**Sentence matrix.** hr: sentence count not measured; archive audit reports 8,106,239 documents and 62,797,162 paragraphs. mt: sentence count not measured; archive catalogue reports 537,336 texts and 347.9M catalogue words (not a sentence count). sl: sentence count not measured in checked-in summary. Current production extraction for all three remains unverified. Other labels: not applicable.

**Licence and attribution.** CLARIN.SI catalogue declares CC0 for the three audited releases. Preserve the catalogue/release identity and source/document provenance. The archive's paragraph-level flags remain part of the source's quality/eligibility contract.

**Pending questions/checks.** First production adapter run must validate archive hashes, parse records, preserve flags and report per-language eligible counts/quota or true exhaustion. Do not invent a new lm_score threshold; missing language is dropped as unknown and missing heading is treated as unflagged, as specified in the adapter audit.

### ParlaMint 4.0 — Icelandic, Slovenian and Turkish

**Description.** TEI parliamentary corpora. Audit reports 928 Icelandic and 1,572 Slovenian session files; Turkish is also listed in the source inventory. Adapter groups segment-bearing utterances and fallback utterance records by session, preserves session/date and utterance/segment IDs, and keeps only the non-identifying role whitelist (chair, regular, guest). It excludes speaker references and person metadata.

**Sentence matrix.** is: sentence count not measured; sl: sentence count not measured; tr: sentence count not measured. Session-file counts are not sentence counts. The adapter coverage table in the pipeline contract lists only IS/SI while the source register lists IS/SI/TR; reconcile the Turkish coverage in the workflow matrix/config before claiming it is active.

**Licence and attribution.** ParlaMint/CLARIN.SI attribution is required; inspect the exact national-corpus licence/terms in the pinned release manifest rather than assuming one blanket licence for every national corpus.

**Pending questions/checks.** Verify Turkish is actually included in the active matrix and its precise licence/attribution. First production run must parse the real archives, count emitted segments, and report source/language quota or exhaustion. Keep speaker/person metadata excluded.

### Gaois Parallel English-Irish Legislation Corpus — Irish side only

**Description.** Six approved TMX archives. Full audit measured 984,006 Irish segments and 478,948 distinct normalized Irish segments (another source-register snapshot reports 984,085 translation units). The active adapter emits Irish-side text only, with a deterministic maximum 50,000-record candidate sample. English-side text is not emitted or used as candidate text.

**Sentence/segment matrix.** ga: 984,006 Irish segments in the full audit; 478,948 distinct normalized segments; production target up to 50,000 eligible rows after current privacy/quality filters. en: 0 candidate rows by explicit scope; English-side hashes/character counts may be retained as non-text provenance only.

**Licence and attribution.** DCU/Gaois derivative TMX is CC BY 4.0 with attribution. Underlying Government of Ireland legislation rights remain a separate review. Preserve Gaois/DCU attribution and distinguish derivative translation-memory rights from original legislation rights.

**Pending questions/checks.** First production run must reapply current privacy screening, report actual eligible Irish count and whether the 50,000 target is reached or source-exhausted. Reconcile the 984,006 vs 984,085 audit measure (segments vs translation units) in the source manifest. Never emit English text.

### TeMU-BSC Catalan CC0 sentence collection

**Description.** README-scoped audit of 32 root/nested files; 17 README-identified CC0/CC0-waived constituent files. Audit reports 638,372 nonempty sentence rows/cells and 608,105 within-file distinct normalized strings; a later source-register summary reports 605,468 distinct normalized strings across 17 constituents after excluding aggregate copies and permission-only/unresolved files. These are audit-level string counts, not current pipeline output.

**Sentence matrix.** ca: 638,372 nonempty sentence rows/cells; 608,105 within-file distinct normalized strings in one audit view; 605,468 distinct normalized strings in the later constituent-filtered summary. Keep the differing scopes explicit; do not collapse them into one unexplained count. Current production adapter count not yet verified.

**Licence and attribution.** CC0/CC0-waived status applies only to the 17 identified constituents, not every file in the repository. Keep constituent-level README evidence and exclude permission-only/unresolved constituents. Do not apply a blanket CC0 label to the repository.

**Pending questions/checks.** Reconcile the two distinct-count figures by documenting exact exclusion/deduplication scope. Verify adapter output, provenance and quota/exhaustion. Keep the constituent-level source/licence manifest.

### BSC-LT Legal Catalan–Spanish corpus

**Description.** Legal text/translation source. Historical waiting-source run recorded 50,414 Catalan candidates (50,000 DOGC + 414 APDCAT in the described sample). The current contract/source register notes constituent-level terms and APDCAT data-sharing agreement review.

**Sentence matrix.** ca: 50,414 historical candidate rows in the waiting-source artifact; this is not a fresh clean-run count and not all constituents are necessarily cleared. es: no Spanish target label in the configured 34-label set; not a candidate language. Current clean-run count: not measured.

**Licence and attribution.** Mixed constituent terms; no single blanket licence should be assigned. DOGC legal texts and APDCAT material have distinct terms/provenance; the APDCAT data-sharing agreement is specifically pending inspection.

**Pending questions/checks.** Verify the exact legal basis/terms for each constituent, inspect the APDCAT agreement, preserve document-level source provenance, and report eligible Catalan rows after privacy/quality checks. Do not treat the historical 50,414 as automatically eligible.

### Catalan-DPO-V2

**Description.** Mixed English/Catalan instruction/preference dataset. Historical artifact contains 30,790 rows from chosen and assistant messages; current source register says it is not a valid Catalan corpus as sampled and the source is excluded.

**Sentence matrix.** ca/en: no accepted sentence count; historical 30,790 rows are mixed-format message records, not clean language sentences. Current pipeline: excluded.

**Licence and attribution.** Dataset-card/repository terms require source-traceable rights review; no blanket redistribution clearance established for all constituent text.

**Pending questions/checks.** Keep excluded unless a new source-level audit proves text origin, language, licence and sentence segmentation. Do not count messages as sentences.

### Soranoha Japanese literature v0.2 (Aozora Bunko)

**Description.** Full plaintext archive audit: 17,308 works, 232.7M characters and 5.42M punctuation/line-break sentence segments. Audit/source-register only; no active staged adapter/config rule.

**Sentence matrix.** ja: 5.42M heuristic sentence segments in the audit; not current pipeline candidates. Other labels: not applicable.

**Licence and attribution.** Works are stated to be public domain in Japan; bibliographic metadata requires CC BY 4.0 attribution. Verify the relevant jurisdiction/public-domain determination for intended use.

**Pending questions/checks.** Not approved/integrated by inference. If the project elects to include it, implement and test an adapter, preserve work-level metadata and attribution, and report exact emitted sentence counts. Until then it remains audited but not acquired by this pipeline.

### Korean Wikipedia cleaned release (2026-07-01)

**Description.** Full Parquet release audit: 593,006 articles and 17.77M heuristic sentence segments. Current waiting-source adapter is active for Korean.

**Sentence matrix.** ko: 17.77M heuristic sentence segments in the upstream audit; current clean-run eligible count not measured. These are heuristic splits, not manually validated sentences.

**Licence and attribution.** CC BY-SA 4.0 / GFDL obligations are recorded. This is a share-alike compatibility hold for the intended downstream release, not a claim that the source lacks a licence.

**Pending questions/checks.** Preserve article provenance and licence notices; determine compatibility for the intended release. Production run must report extracted and filtered counts. Do not silently drop the source from private technical candidate evaluation solely because release compatibility is pending.

### UN Arabic-English Filtered (HF derivative)

**Description.** Revision-pinned Arabic-English filtered dataset. The full-shard audit completed; current adapter reads the train stream and emits Arabic `text_ar` only. The source schema lacks source document IDs/URLs; source_row_index is retained but must not be mislabelled as a document ID.

**Sentence matrix.** ar: exact full-shard/train sentence count not stated in the checked-in source summary; the historical source-register mentions 19.28M train rows plus dev/test for the upstream audit, not the current eligible candidate count. en: 0 candidate rows by explicit Arabic-only scope.

**Licence and attribution.** HF derivative declares CC BY 4.0; United Nations publisher acknowledgement/citation is required. Underlying UN source terms and document-level provenance are separate questions not resolved by the derivative card.

**Pending questions/checks.** Record exact pinned revision, row count and source_row_index coverage; preserve UN acknowledgement; inspect underlying UN source terms and provenance. Never emit or score `text_en`.

### HPLT 3.0 (investigated, not acquired)

**Description.** Large multilingual Common Crawl/Internet Archive-derived corpus; catalogue and language coverage inspected, no current candidate acquisition.

**Sentence matrix.** No project sentence counts; not acquired. Language coverage must be read from the exact release catalogue if reconsidered.

**Licence and attribution.** HPLT does not own or grant rights in extracted text; CC0 applies to packaging/metadata only. The paper reports Internet Archive consent for derived language resources, but no comparable consent for Common Crawl. HPLT has notice/takedown processes.

**Pending questions/checks.** No acquisition without a source-specific rights/provenance plan and explicit project selection. If reconsidered, separate Internet Archive and Common Crawl origins.

### JRC-Acquis 3.0 (investigated, not acquired)

**Description.** EU legal corpus inspected for coverage/structure; no current staged artifact.

**Sentence matrix.** No project sentence counts; not acquired.

**Licence and attribution.** Commission reuse conditions and component-level rights/attribution require review; no blanket CC0 label.

**Pending questions/checks.** Resolve exact component notices and source-document provenance before acquisition.

### Europarl v7 (investigated, not acquired)

**Description.** Parliamentary proceedings corpus; language coverage, document IDs and source statement reviewed.

**Sentence matrix.** No project sentence counts; not acquired.

**Licence and attribution.** No formal corpus-wide licence grant established by the reviewed statement.

**Pending questions/checks.** Obtain definitive reuse terms and preserve document IDs before reconsideration.

### OPUS catalogue (investigated, not acquired as a blanket source)

**Description.** Aggregator of independently licensed parallel corpora, not one dataset with one licence.

**Sentence matrix.** No project sentence counts for OPUS as a whole; individual component counts/coverage depend on the chosen corpus.

**Licence and attribution.** Every component has separate licence and provenance. No blanket OPUS licence.

**Pending questions/checks.** Select and audit individual components only; never ingest the catalogue indiscriminately.

### Irish sources investigated but not acquired

**Description.** National Corpus of Irish (CNG), Oireachtas API, Citizens Information bilingual corpus, ParaCrawl v6, DCEP, Royal Irish Academy Historical Irish Corpus, CELT, Tobar na Gaedhilge and eSTÓR were separately investigated. None is an active current adapter in the staged workflow.

**Sentence matrix.** CNG: publisher-reported 100M words, not project-measured sentences. Oireachtas: 646 debate metadata records for 2024; five XML samples contained 714 speech elements but were English-only. Citizens Information: catalogue reports 10,297 aligned sentences, but source archive route was inaccessible/retired. ParaCrawl: catalogue reports 1,366,628 aligned lines, not a project measurement. DCEP: catalogue reports 46,146 English-Irish aligned lines. RIA/CELT/Tobar/eSTÓR: no project sentence counts.

**Licence and attribution.** CNG CC BY-SA 4.0; Oireachtas PSI/CC BY 4.0 for open data (Broadcast Proceedings separately permission-based); Citizens Information catalogue CC BY 4.0 but resource inaccessible; ParaCrawl underlying web rights unresolved; DCEP research-only rights; RIA item-specific rights; CELT restrictive/private-use terms; Tobar snippets only; eSTÓR platform CC BY-NC-SA 4.0 with resource-specific licences.

**Pending questions/checks.** Do not count catalogue claims as acquired rows. Revisit only through a working publisher route and source-specific terms. These are discovery leads, not silently active sources.

### Korean sources investigated but not acquired

**Description.** Korean NSMC, NIKL Written Corpus 2025, Korean Parallel Bible and Korean Open Historical Corpus were investigated; Korea.kr/Korean Law Open Data routes were explicitly not pursued.

**Sentence matrix.** No project sentence counts; not current pipeline sources.

**Licence and attribution.** NSMC conflicting licence claims; NIKL access-by-request without written redistribution approval; Bible CC BY-SA 3.0; Korean Open Historical Corpus CC BY-NC 4.0. Korea.kr and Korean Law API have no current acquired text.

**Pending questions/checks.** Keep these routes retired/not pursued unless explicitly reopened. Do not confuse historical exploratory code with an active source.

### Common Crawl underlying web pages (rights/provenance context, not a separate source adapter)

**Description.** Underlying origin for FineWeb, FineWeb2 and HPLT subsets. It is not itself a single language/source corpus in the current pipeline.

**Sentence matrix.** No separate project sentence count. Counts belong to the dataset/release and its source-language manifests.

**Licence and attribution.** Common Crawl terms bind use of Crawled Content and state that content may be subject to third-party site-owner terms; users must respect third-party rights. The ToU's indemnity provision allocates risk; it is not itself a determination that every excerpt is prohibited or permitted.

**Pending questions/checks.** Preserve page URLs/domains and takedown traceability where available. Distinguish dataset database rights, Common Crawl contractual terms and underlying page rights. Do not make a blanket legal conclusion from the crawl origin alone.

## Audit of the existing canonical source register against recorded project decisions

This audit compares the checked-in `docs/source-register.md`, `docs/pipeline-contract.md`, `config/langid32.toml`, `README.md`, and the decisions preserved in the shared project conversation history through 26 November 2026. It identifies mismatches; it does not claim access to unprovided private discussions.

### Blocking contradictions to correct

1. **Leipzig source/language scope has been restored in config.** No source-specific language allowlist is used for News or Wikipedia. The historical 3,000-per-source rows are a starting snapshot, not a new cap; the acquisition process must retain every supported project label and report actual archive absence.
2. **FineWeb2's six-label restriction has been removed.** The workflow now schedules all 31 available non-English project subsets. The source-wide technical-candidate/release-rights status remains a separate review flag, not a language exclusion.
3. **DGT-TM is narrowed to five labels in config**, despite the historical 24-language artifact at 5,000 units per language and the broader approved first-pass acquisition decision. Restore all approved DGT languages and the 20,000/source/language first-pass ceiling; report source exhaustion honestly.
4. **English source availability is distinct from language allowlists.** FineWeb2 does not supply English; FineWeb is a separate source currently excluded by its source-wide rights hold. No other source-language allowlist is used to exclude English.
5. **Targets are inconsistent across project truth files.** README/config/contract say 34 labels and 30,000 per language (20k core + 10k reserve); earlier recorded project decisions specify a 32-language project and 25,000 final sentences per language with at least 35,000 candidates. This must be reconciled explicitly. Do not silently treat the newer README/config values as approved decisions.
6. **No automatic top-up after global deduplication is currently permitted.** The contract says not to top up shortfalls, whereas the recorded project decision calls for adaptive oversampling/replenishment when quotas fail and additional material acquisition. This is a material policy mismatch and must be corrected in contract/config before a run.
7. **The source register's status vocabulary mixes technical staging with approval and legal holds.** Each source needs separate fields for acquisition state, adapter integration, sentence-count evidence, rights/attribution status, project selection decision and first-run verification. "HOLD" must not automatically mean "do not ingest for private technical candidate evaluation" unless that exact exclusion was approved.
8. **ParlaMint language scope is inconsistent.** The source register records IS/SI/TR; the pipeline contract adapter table says IS/SI; verify the workflow matrix and restore Turkish if it is an approved target.
9. **The source register has historical counts but not a complete source × language sentence matrix.** It must not present documents, paragraphs, words/tokens, archive files, translation units or heuristic sentence splits as interchangeable. The new tables above mark unavailable counts as not measured rather than fabricating them.
10. **The current run is not a full-pipeline completion.** Run 45780510056 completed partial acquisition; candidate and JQL were skipped. The 110-test CI run 45798217209 and 146-test adapter CI run 45825016266 are synthetic/code evidence, not a full scrape.

### Decisions retained as settled (do not reopen without new evidence)

- Common Voice scope is the HF-hosted Common Voice 22 text-only conversion; the project accepted its CC0-1.0 dataset declaration. Do not introduce per-locale acceptance gates or fetch audio/speaker/demographic data.
- Mozilla Data Collective and data hosted there are voluntarily excluded by project decision. Do not generalize this decision to the separate HF-hosted Common Voice 22 conversion.
- The privacy-screen implementation is accepted for private candidate/JQL processing. Manual review of actual resulting records is required before any external release; do not block private processing on replacing the implementation.
- MaCoCu-hr 2.0, MaCoCu-mt 2.0 and MaCoCu-sl 2.0 are approved for the current candidate pipeline; their adapter integration is implementation work, not a source-scope question.
- Greynir Copper/Silver are approved Icelandic technical inputs; Gold dev/test is excluded. The LFS hydration audit and synthetic tests are evidence, but production extraction remains a first-run check.
- The final selection/publication stage is deferred until after full-pool JQL and manual privacy/rights review. This does not authorize deleting candidate sources before assessment.
- Acquisition must respect the six-hour workflow ceiling using small resumable batches, bounded concurrency and a measured initial throughput batch where necessary.

### Required correction order

1. Reconcile the 32-vs-34 language inventory and 25k/35k-vs-30k targets against the actual approved decision record.
2. Keep the source-language allowlist invariant: Common Voice 22 alone has an explicit locale list because Croatian is absent; all other sources must derive coverage from their actual source content, with no config-level language allowlists.
3. Restore adaptive oversampling/replenishment policy while preserving per-source provenance and the 6-hour batch ceiling.
4. Reconcile source register, config, pipeline contract, README and trigger hashes as one reviewed contract change.
5. Re-run full CI and source-adapter synthetic tests.
6. Launch the clean full workflow; validate every acquisition adapter against real archives, then candidate construction, all-row JQL, three-judge merge/prune and encrypted hand-off.
7. Publish complete per-language × original-source counts at every stage. Do not call the pipeline complete until these outputs reconcile.

## Implementation status of this file

This catalogue is an evidence-based inventory, not a legal opinion. Where the checked-in source evidence did not provide per-language sentence counts, the matrix explicitly says **not measured**. The next required data update is to populate those cells from the actual clean-run acquisition manifests and candidate reports, not from guessed proportions or upstream document/token totals.
