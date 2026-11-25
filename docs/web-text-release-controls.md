# Web-text release controls (HPLT-informed; not a rights grant)

This policy borrows HPLT 3.0's transparency and notice-and-takedown mechanisms, not a claim that web text is cleared. HPLT states that it does not own or grant rights in extracted text; CC0 applies only to packaging/metadata, and users remain responsible for legal compliance. Its notice process removes affected sources from the next release. See the [HPLT 3.0 card](https://huggingface.co/datasets/HPLT/HPLT3.0) and [2026 paper](https://doi.org/10.63317/25xbdofco9od).

This project must also account for the [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use), including §9 indemnification for claims arising from AI/ML use, copyright and privacy/publicity rights. FineWeb/FineWeb2's ODC-BY tag covers database rights, not the rights in individual page contents. A public Hugging Face repository would additionally grant users broad rights through the Hub and make the uploader responsible for posted content. None of these wrapper terms clears an individual excerpt.

## Required before release

- [x] Publish a rights-notice contact channel. A test message was delivered; ongoing monitoring and an accountable case-handling rota still need operational verification.
- [ ] Include the packaging-only terms and a clear notice-and-takedown policy in the dataset card and every downloadable release.
- [x] Do not declare Common Crawl-derived excerpts CC0 or ODC-BY on the strength of packaging/database metadata alone. No dataset-level licence is declared while the release gate is blocked.
- [ ] Retain source-level provenance sufficient to locate every excerpt: source dataset, crawl/archive, URL or stable source ID, source document ID, retrieval/crawl date, exact text fingerprint, source terms/licence evidence, and derived record IDs.
- [ ] Keep detailed provenance private where it contains sensitive URLs, personal data or operational information; publish only fields necessary for transparency and attribution.
- [x] Maintain a versioned source/document exclusion registry and apply it before candidate merge/release builds. The merge implementation supports document, exact-URL/hash, domain, archive-batch and source-dataset scopes.
- [x] Active quarantine rules now exclude both Catalan-DPO-V2 components (chosen, messages) and the Greynir parser gold/development sample from candidate merges.
- [ ] Extend exclusion propagation to exact-text duplicates across different source groups. Current implementation cascades a matched record through its group_id and split_group_id, but does not yet remove identical text in a different source group.
- [ ] Complete URL canonicalisation before hashing. Current url_sha256 matching hashes the exact URL string; it does not normalise query strings, fragments, default ports or trailing slashes.
- [ ] Verify an end-to-end exclusion rebuild against a full candidate artifact and prove all affected records, duplicates and manifests are updated.
- [ ] Add privacy screening beyond the current email/URL/IPv4 filters. Phone-like and long numeric sequences are flagged but retained; names, addresses and sensitive categories are not comprehensively detected.
- [ ] Preserve separate licence and attribution treatment for independently licensed sources (for example CC BY or CC BY-SA); packaging-only terms must not erase those obligations.
- [x] Keep the release marked not publication-ready until mandatory controls and source-specific rights reviews are complete.

## Exclusion registry format and actual implementation

The registry is UTF-8 JSONL (CSV is also accepted by the merge CLI). Each active rule must have:
- scope: one of document, url, domain, archive-batch, source-dataset;
- reason_code and effective_at;
- one scope-specific key: source_key for document; url_sha256 or source_url for url; domain; archive_batch; or source (and optionally source_release) for source-dataset.

Optional fields include case_id and status (active by default; superseded rules are ignored). The code currently accepts any non-empty reason_code; the values used by this project include rights_notice, privacy_notice, provider_restriction, legal_review, source_unknown, mixed_language_mislabelled and quality_hold_nonrepresentative_gold_dev_sample.

For URL scope, prefer an exact source_url until canonicalisation is implemented. url_sha256 is currently the SHA-256 of the exact source URL string, not a canonical URL. The registry must not contain claimant contact details or unnecessary personal data. A source-level exclusion is preferable to a domain-wide exclusion unless the evidence or notice requires broader scope.

A matched row causes every row sharing its group_id or split_group_id to be excluded. This protects document groups, translations/segments and split groups when those identifiers are correct. It does not yet cascade to identical normalized text in a different group/source; that gap is a release blocker.

## Current active exclusions

- DPO-QUARANTINE-2026-11-18: excludes catalan_dpo_v2:chosen and catalan_dpo_v2:messages, because the source is 40% Catalan / 60% English and the prior sampler labelled every row ca.
- GREYNIR-GOLDDEV-2026-11-18: excludes greynir, because the 4,930 acquired rows came from parser test/development gold-standard files, not the full corpus.

## Current implementation status

The registry is no longer empty. The merge code loads active rules, matches the supported scopes and cascades exclusions through group/split-group identifiers; unit tests cover URL, domain and document/group propagation, with a source-dataset test added for the DPO and Greynir rules. The multisource candidate workflow applies data/source-exclusions.jsonl and uploads metadata only, not candidate text.

Remaining blockers are exact URL canonicalisation, cross-source duplicate propagation, a full end-to-end exclusion rebuild, more comprehensive PII screening, complete source-to-output traceability and operational confirmation of mailbox monitoring/case ownership. Therefore this policy does not authorise publication of FineWeb/FineWeb2 or any other rights-held web-text candidates.
