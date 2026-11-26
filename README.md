# langid-32

A reproducible multilingual language-identification corpus and benchmark project. The historical repository name reflects the original 32-language scope; the current target inventory contains **34 language labels**.

The project compares two compact character-based classifiers with a byte-level Transformer. Corpus construction, source rights, provenance and evaluation are treated as separate, auditable stages.

## Current objective

Build a balanced, reproducible text corpus for 34 language labels:

- The 24 official EU languages, including Maltese.
- Arabic, Catalan, Icelandic, Japanese, Korean, Russian and Turkish.
- Norwegian Bokmål (`nb`) and Nynorsk (`nn`) as separate labels.
- Chinese (`zh`), combining the intended Simplified and Traditional source varieties.

Target **30,000 usable records per language**: a 20,000-record core plus up to 10,000 reserve. A language must have at least 20,000 usable records to meet the minimum. Counts are measured only after normalization, privacy filtering, language/content checks, global exact deduplication and source quota enforcement.

Source mix target: **30% preferred, 50% hard ceiling per source and language**. Any exception must be explicit, justified and reported; a single-source class is not considered balanced.

The binding stage order, acquisition/privacy/JQL rules, execution limits, acceptance checks and workflow invocation procedure are in the [pipeline contract](docs/pipeline-contract.md). The 30,000-per-language target is a later human-approved selection target: the automated pipeline stops after full-pool JQL scoring and global bottom-25% pruning.

## Voluntary source-selection decision

The project voluntarily does not use the Mozilla Data Collective repository or any data hosted there. We consider its contractual practices abusive. This is a project sourcing decision, not a legal finding about any other dataset.

## Corpus status — 23 November 2026

**Preparation only — not release-ready.**

No public corpus data has been uploaded to the Hugging Face dataset repository. No language is currently release-cleared.

Measured technical staging currently includes:

| Staging set | Rows | Meaning |
|---|---:|---|
| Waiting-source acquisition | 613,860 | New source candidates across Catalan, Icelandic, Bokmål, Nynorsk, Korean and Arabic; includes 100,000 FineWeb2 backfill candidates |
| [HF-hosted Common Voice 22 CC0 text pilot](https://huggingface.co/datasets/fsicoli/common_voice_22_0) | 259,352 | Historical text-only pilot across 33 labels; Croatian has no source yet |
| Tatoeba CC0 refresh | 80,155 | Fresh staged export; concentrated in a subset of languages |
| DGT-TM 2021 refresh | 120,000 | 5,000 staged translation units per 24 EU languages |
| Legacy v5 candidate | 640,000 | Historical 32-label technical candidate; source balance and rights gates fail |

These are **separate staging artifacts and must not be summed**. They have not all been globally deduplicated against one another. They are not final usable-record counts.

The table above is the **18 November candidate-staging snapshot**. The upstream source audits below were run after that snapshot; their measured source volume is not yet integrated into the waiting-source artifact or the global candidate build.

### Upstream source audits completed or underway on 23 November

- **Catalan:** full TeMU-BSC inventory now measures 605,468 distinct normalized strings across 17 README-identified CC0/CC0-waived constituents, after excluding aggregate copies and permission-only/unresolved files. The BSC legal corpus audit separately measured 5,220,918 DOGC sentence pairs plus smaller paragraph/document collections. The APDCAT data-sharing agreement remains the one specific BSC document to inspect for downstream scope.
- **Icelandic:** IGC2024 Filtered-1 full scan: 1,848,767 documents and 795.7M local whitespace tokens under CC BY 4.0. Greynir copper/silver/extra were also fully counted; keep gold test/dev material separate.
- **Norwegian:** Målfrid 2026 full scan: 1,550,489 distinct document IDs across Bokmål and Nynorsk, with 2.06B local whitespace tokens combined. NLOD 2.0 attribution and document-level third-party/personal-data exclusions remain.
- **Croatian:** MaCoCu-hr 2.0 full structural audit: 8,106,239 documents and 62,797,162 paragraphs; CLARIN.SI declares CC0. Paragraph quality, fluency and sensitive-information flags must be retained.
- **Slovenian:** MaCoCu-sl 2.0 audit is retrying after a CLARIN connection timeout. ParlaMint 4.0 is being audited for Icelandic, Slovenian and Turkish.
- **Maltese:** MaCoCu-mt 2.0 is a newly identified CC0 source (537,336 catalogue texts; 347.9M catalogue words); its full XML audit is running. Korpus Malti is a separate, much larger corpus but carries CC BY-NC-SA 4.0 and includes literary material by permission, so it is not substituted for the CC0 source.
- **Irish:** Gaois legislation TMX audit: 984,006 Irish segments, 478,948 distinct normalized segments across six files, CC BY 4.0 for the DCU derivative translation memories. This is a legal/administrative register, not general contemporary Irish.
- **Japanese:** Soranoha v0.2 full plaintext audit: 17,308 works, 232.7M characters and 5.42M punctuation/line-break sentence segments. Works are stated to be public domain in Japan; bibliographic metadata needs CC BY 4.0 attribution.
- **Korean:** cleaned 2026-07-01 Wikipedia release: 593,006 articles and 17.77M heuristic sentence segments. Its CC BY-SA 4.0/GFDL terms remain a compatibility decision, not a CC BY/CC0 source.
- **Arabic:** the official UN download route currently redirects to the landing page rather than returning the archive. A full audit of all 19.28M train rows plus dev/test in the CC BY 4.0 HF derivative is now running; its schema still lacks source document IDs/URLs and row-level provenance.

These are **upstream audit measures**, not final usable-record counts. They must still pass the global normalization, privacy, language/content, cross-source deduplication, source quota and rights gates before they can affect the 20k core or 10k reserve.

The waiting-source artifact contains useful independent candidates, but some classes remain concentrated in one source and several licences or underlying-text rights remain under review. In particular:

- Catalan: BSC/TeMU and Catalan-DPO components require constituent-level provenance and terms checks; FineWeb2 is on legal hold.
- Icelandic: IGC2024 and Greynir are CC BY 4.0 candidates; FineWeb2 is on legal hold.
- Bokmål and Nynorsk: Målfrid 2026 is a substantial NLOD 2.0 source, but each current 50k candidate batch comes from that one source.
- Korean: the current Wikipedia candidate has CC BY-SA/GFDL obligations; it is not yet approved for the release.
- Arabic: the UN-derived candidate needs confirmation of the underlying UN source terms; the Hugging Face card alone is not sufficient.

See the [canonical source register](docs/source-register.md) for every source investigated or acquired, its measured status, rights position and retired routes. The [dated corpus status report](docs/corpus-status-2026-11-17.md) and [candidate audits](docs/candidate-audit-v5.md) preserve historical measurements; they are not current acquisition plans. The [v6 corpus policy](docs/corpus-policy-v6.md) defines selection rules.

## Current staged data preparation rules

The binding stage order and acceptance criteria are in the [pipeline contract](docs/pipeline-contract.md). In summary:

1. Acquire current sources afresh and validate the four approved pinned historical snapshots before fresh acquisition begins.
2. Normalize text/language, apply source quality checks and the accepted privacy screen, then enforce up to 20,000 eligible unique records per original source × language (with the explicit Gaois Irish 50,000-record exception).
3. Build the complete candidate pool, preserve original-source provenance, remove within-language duplicates and remove every occurrence of cross-language text collisions.
4. Assess **every** post-filter candidate row with the three JQL heads; no 1,000-per-language sampling.
5. Independently quantile-normalize each judge over the full combined assessment corpus, calculate the agreed consensus and prune the global bottom 25%.
6. Produce full per-language × original-source counts and encrypted review artifacts. Preserve document/group IDs for later split integrity.
7. Stop for manual privacy and source-rights review.

The final 30,000-per-language selection, 20k core plus 10k reserve labels, and 30% preferred / 50% hard per-source mix are deferred human decisions. The automated pipeline does not perform them. The accepted privacy implementation is heuristic; its output is held for manual review before any external release.

Raw downloads and private provenance sidecars are not committed to Git. GitHub Actions artifacts are temporary preparation outputs, not public releases.

## Rights and licensing

The project does not infer the licence of an extracted passage solely from the licence of its host page, dataset wrapper or compilation.

- Source text rights and compilation/database rights are tracked separately.
- Excerpt-level origin, quotation, attribution and third-party content must be investigated where relevant.
- CC BY material may be included if its conditions can be met; the release must carry the appropriate attribution. A mixed release is not relabelled CC0.
- Unclear, incompatible or unverified source material remains on hold or is excluded.
- If every included source is genuinely CC0/public domain and all other rights checks pass, the release may be CC0. Otherwise the release licence and attribution package must reflect the included sources and their obligations.

### Web-extracted text

For Common Crawl and other web-archive material, the project follows an HPLT-style separation-of-rights and notice-and-takedown approach:

- We do not claim ownership of, or grant a licence to, the underlying extracted text.
- A CC0 dedication, if used, applies only to eligible original project packaging (selection, arrangement, schema, annotations and preparation metadata); it does not relicense source passages.
- The compilation licence of FineWeb, FineWeb2 or HPLT does not, by itself, establish the rights status of every excerpt.
- A source URL is provenance for investigation, not proof that the page owner licensed every passage it contains.
- This approach is not a representation that every passage has been individually rights-cleared, nor a legal safe harbour or guarantee of downstream legality.

Rights holders and affected persons can submit copyright, database-rights, privacy, source-terms and removal notices to **[abuse@souche.fr](mailto:abuse@souche.fr)**. The mailbox is configured in the project maintainer's email client and has successfully received and acknowledged a test message. Operational case handling, source-level traceability and removal controls still need to be validated before release. See [Terms of Use](docs/terms-of-use.md), [Notice and Takedown](docs/notice-and-takedown.md), [web-text release controls](docs/web-text-release-controls.md), and the [source attribution and citation register](docs/source-attribution-register.md), and the [canonical source register](docs/source-register.md).

## Reproducible development

Install and test the Python package:

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
```

The original `langid32-prepare` command remains a single-source CSV/TSV helper. The merge-first pipeline accepts source-normalized JSONL records and creates text-only splits plus an internal provenance sidecar. See the CLI help and source-specific staging scripts for current interfaces.

## Model routes

- **A1:** hashed character n-gram features with a sparse linear classifier.
- **A2:** hashed character n-gram EmbeddingBag with a compact linear head.
- **B:** byte-level Transformer trained from scratch.

Model benchmarking is deferred until corpus source diversity, quality, privacy and rights gates have been met. See [model design](docs/model-design.md).

## Contact

For project questions and rights notices: [abuse@souche.fr](mailto:abuse@souche.fr).

## Legacy local reproducible pipeline (historical pilots only)

The Makefile targets below orchestrate earlier Leipzig experiments. They are **not** the current staged corpus pipeline and must not be used to create the current candidate pool or final 30,000-per-language selection.

The current pipeline runs through GitHub Actions: `.github/workflows/langid32-pipeline.yml` performs preflight, fresh acquisition, candidate construction and full-pool assessment; `.github/workflows/score-jql-assessment.yml` then scores all three JQL heads, performs global normalization and bottom-25% pruning, and uploads encrypted review artifacts. It stops before final selection. Its exact push trigger and resume procedure are in the [pipeline contract](docs/pipeline-contract.md).

For historical local experiments only:

```sh
make help
make install-corpus
make install-jql
make all LABELS=hr,is DEVICE=mps
```

The local `make anonymize` and 34k JQL sample settings belong to that legacy workflow; they are not the accepted current privacy or JQL implementation. Do not use those outputs as substitutes for the current encrypted staged-pipeline artifacts.
