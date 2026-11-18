# Leipzig Corpora Collection — acquisition and rights audit — 18 November 2026

**Project priority: first acquisition and integration priority.** The user supplied a practical access guide and the Hugging Face index `imvladikon/leipzig_corpora_collection`. These materially change the acquisition plan: do not use the bot-checked portal UI as an automation target, and do not rely on the REST API for bulk sentence extraction. Use the Hugging Face catalogue as the downloadable archive index and the Leipzig download host for corpus archives.

## 1. Preferred catalogue and bulk route

Hugging Face index: https://huggingface.co/datasets/imvladikon/leipzig_corpora_collection

The HF repository contains:
- `data/links.parquet`: one `links` config, 5,780 rows, 7 columns (`id`, `data_id`, `url`, `language`, `language_short`, `year`, `size`), approximately 154 KB.
- `leipzig_loader.py`: a convenience downloader/extractor.
- `README.md`: documents that the parquet file is an index only. The sentence corpora are **not hosted on HF**; the helper downloads the original `.tar.gz` archives from `downloads.wortschatz-leipzig.de`. The README explicitly says the HF repo does not mirror/re-host the archives.

The index's Dataset Viewer shows a 5.78K-row train split and 268 distinct values for the language fields. Its visible sample includes Arabic news and regional Arabic news-crawl corpora. The HF tags list only a subset of languages and must not be treated as the catalogue's complete language coverage. The complete Parquet index should be parsed and mapped against all 34 langid-32 labels before deciding coverage or acquisition volume.

The user-supplied practical guide (verified 18 November 2026) reports:
- `downloads.wortschatz-leipzig.de` accepts direct archive requests and byte-range/resumable downloads; directory autoindex is disabled (403), but direct archive URLs work.
- Archive URL pattern: `https://downloads.wortschatz-leipzig.de/corpora/{data_id}.tar.gz`.
- Archive members include `{data_id}-sentences.txt` (`id<TAB>sentence`), `{data_id}-sources.txt` (source URL and timestamp per sentence), and words/co-occurrence/index files.
- The portal hosts (`wortschatz.uni-leipzig.de` / `corpora.wortschatz-leipzig.de`) trigger Anubis proof-of-work from the tested datacenter environment. Avoid automating the portal.
- Prefer serialized, polite archive downloads with resume/backoff; do not hammer the academic service.

The helper in the HF repo is useful as a format reference, not a dependency to execute blindly. Its `load_corpus` downloads an entire archive and extracts only the sentences file; langid-32 should additionally preserve and parse the paired sources file, pin the index revision, hash every archive, and retain the original archive and corpus IDs in provenance. Review its parser carefully; the source files are TSV and should be parsed with quote handling disabled (the helper already uses `csv.QUOTE_NONE` to avoid corrupting sentences containing quote characters).

## 2. What the catalogue establishes — and what it does not

The HF index is a catalogue of archive names, URLs, language codes, years and nominal sizes. It is not a copy of the corpora and it does not itself grant rights to the sentence content.

The HF dataset card/README inspected on 18 November 2026 has **no declared dataset licence field**. Its descriptive text says corpora contain randomly selected sentences from newspaper or web sources and says they are automatically collected without detailed consideration of the content. It disclaims responsibility for the content and opinions. This is not a corpus-text licence grant.

The previously inspected Leipzig OpenAPI specification declares CC BY 4.0 for the API/documentation. That declaration must not be transposed to the underlying sentence corpora. The actual usage terms at https://wortschatz-leipzig.de/usage still need to be read. The source works remain the decisive issue: the `*-sources.txt` files provide URL and timestamp, which makes a source-level rights review feasible, but a URL and attribution alone do not grant redistribution rights.

**Working rights rule:** no blanket clearance for Leipzig sentences. Separate:
1. Leipzig API/software/documentation terms;
2. Leipzig's own corpus packaging/database and usage terms;
3. rights in each underlying newspaper/web/Wikipedia/source work.

Preserve provenance and hold/exclude sentences whose source-work reuse rights cannot be established. Wikipedia-derived corpora require their applicable licence and revision/attribution analysis; news/web corpora require source-publisher terms or another defensible permission/licence basis. Do not assume all 5,780 archives share one licence.

## 3. Earlier REST API probe — useful but no longer the bulk route

The earlier API work remains useful for metadata and comparison, not bulk acquisition:
- OpenAPI: https://api.wortschatz-leipzig.de/ws/v3/api-docs
- Catalogue: `GET /corpora`
- Sentence examples: `GET /sentences/{corpusName}/sentences/{word}`
- Prior probe run [44294431022](https://github.com/SylvainSouche/langid-32/actions/runs/44294431022), artifact [14423405978](https://github.com/SylvainSouche/langid-32/actions/runs/44294431022/artifacts/14423405978): 104 API-service corpora; 20/34 target labels; 29/30 sentence-service probes returned examples. It examined 289 example sentences transiently and retained no sentence text.
- That 104-corpus API-service subset is not the same as the 5,780-entry downloadable archive index.

The earlier HTML catalogue scraper's failure (33 pages, zero archive links) was a failure of the portal-automation route, not evidence that the corpus or download host is inaccessible.

## 4. Acquisition plan — first priority

1. **Parse and pin the complete HF links index.** Save its revision, Parquet SHA-256, schema and all 5,780 rows as metadata only. Normalize ISO-639-3 and region-qualified codes to the project's 34 labels without losing original codes.
2. **Produce a full inventory.** Group by target label, source family (`news`, `newscrawl`, `wikipedia`, `web`, `webpublic`, `community`, `mixed`, `doku`, `sub`, etc.), year and nominal size. Identify missing labels and the best candidates for each. Do not infer archive availability solely from API-service coverage.
3. **Probe direct archive URLs politely.** HEAD/GET with bounded concurrency, capture status, content length, Last-Modified/ETag and byte-range support. A missing archive is a per-name 404, not a language-level failure. Download serially with resume/backoff.
4. **Pilot a small, diverse set.** Prefer corpora whose source type and provenance can be assessed; avoid treating the largest nominal size as automatically best. Download and hash the archive, inspect tar members, parse sentence/source records together, validate row counts and source-ID joins.
5. **Rights audit before candidate staging.** Resolve usage terms and representative underlying source works. Separate source families and licences; exclude or hold unclear records. No text should enter the training candidate merely because an archive downloads successfully.
6. **Integrate with common langid-32 controls.** Preserve `data_id`, source ID, original URL, source timestamp, corpus language code, source type, year, archive URL, pinned index revision, archive hash and row ID. Apply privacy/PII, language verification, exact and near-duplicate checks, cross-language collision removal, document/source-group splits and per-source quotas.
7. **Rebuild the 34-label candidate and recalculate gaps/source shares** only after the Leipzig sample is technically validated and rights-cleared.

## 5. Earlier API rights notes and citation

The OpenAPI `info` object previously inspected labels the API CC BY 4.0 and links the terms URL above. An earlier automated fetch of the terms page returned an Anubis challenge rather than the terms text. That access failure is superseded as a technical blocker for data acquisition by the direct archive route, but the legal terms still need to be obtained and reviewed.

Scholarly citation listed by the HF dataset card:
Goldhahn, Dirk; Eckart, Thomas; Quasthoff, Uwe (2012), “Building Large Monolingual Dictionaries at the Leipzig Corpora Collection: From 100 to 200 Languages,” LREC 2012, pp. 759–765. Cite the Leipzig collection and the relevant corpus release in project documentation; scholarly citation does not replace legal attribution.
