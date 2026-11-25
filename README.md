# langid-32

**Operational policy:** see [the central corpus configuration](config/langid32.toml) and [its documentation](docs/configuration.md).

A reproducible multilingual language-identification corpus and benchmark project. The historical repository name reflects the original 32-language scope; the current target inventory contains **34 language labels**.

The project compares two compact character-based classifiers with a byte-level Transformer. Corpus construction, source rights, provenance and evaluation are treated as separate, auditable stages.

## Current objective

Build a balanced, reproducible text corpus for 34 language labels:

- The 24 official EU languages, including Maltese.
- Arabic, Catalan, Icelandic, Japanese, Korean, Russian and Turkish.
- Norwegian Bokmål (`nb`) and Nynorsk (`nn`) as separate labels.
- Chinese (`zh`), combining the intended Simplified and Traditional source varieties.

The candidate intake floor, exact final per-language sentence target and any language-specific overrides are defined in the central configuration. Counts are measured only after normalization, privacy filtering, language/content checks, global exact deduplication and source quota enforcement.

Candidate-stage preferred and hard source-share limits, and the final baseline-proportional source mix, are defined in the central configuration.

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
| DGT-TM 2021 refresh (historical snapshot) | Superseded | Old 24-language sample predates the current source scope and central configuration |
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

These are **upstream audit measures**, not final usable-record counts. They must still pass the global normalization, privacy, language/content, cross-source deduplication, source quota and rights gates before they can affect the configured final corpus.

The waiting-source artifact contains useful independent candidates, but some classes remain concentrated in one source and several licences or underlying-text rights remain under review. In particular:

- Catalan: BSC/TeMU and Catalan-DPO components require constituent-level provenance and terms checks; FineWeb2 is on legal hold.
- Icelandic: IGC2024 and Greynir are CC BY 4.0 candidates; FineWeb2 is on legal hold.
- Bokmål and Nynorsk: Målfrid 2026 is a substantial NLOD 2.0 source, but each current 50k candidate batch comes from that one source.
- Korean: the current Wikipedia candidate has CC BY-SA/GFDL obligations; it is not yet approved for the release.
- Arabic: the UN-derived candidate needs confirmation of the underlying UN source terms; the Hugging Face card alone is not sufficient.

See the [current acquisition status by language](docs/acquisition-status-2026-11-25.md), the [source decision register](docs/source-decisions.md) for authoritative inclusion/exclusion decisions and the [source register](docs/source-register.md) for measured audits, provenance, rights position and retired routes. The [dated corpus status report](docs/corpus-status-2026-11-17.md) and [candidate audits](docs/candidate-audit-v5.md) preserve historical measurements; they are not current acquisition plans. The [v6 corpus policy](docs/corpus-policy-v6.md) defines the wider selection principles; active numeric rules live only in [config/langid32.toml](config/langid32.toml).

## Data preparation rules

All sources are staged independently with immutable release identifiers, retrieval dates, source URLs, file hashes, adapter versions, licence/terms and attribution requirements.

The global merge is responsible for:

1. NFC and whitespace normalization, common length and byte limits, and language/script sanity checks.
2. Privacy-pattern exclusions and source/document exclusions from the versioned registry.
3. Exact deduplication within each language across **all** staged sources.
4. Removal of every normalized text string found under more than one language label. No “first language wins” rule is used.
5. Stable document/group-aware train, validation and test assignment before sample selection.
6. Deterministic source-aware selection, per-language source-share reporting, and the configured candidate core/reserve policy.
7. A private provenance sidecar, source manifests, hashes, counts and exclusion reports.

The automated privacy patterns are not a complete privacy review. Phone-like and long numeric strings are flagged for further assessment; automated language checks do not replace human review. Defective records are discarded rather than silently repaired.

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

## Local reproducible pipeline

The Makefile orchestrates the Leipzig corpus stages as independent targets with explicit dependencies:

`download -> filter -> anonymize -> count -> assess -> rate -> score-report`

```sh
make help
make install-corpus
# Install the matching PyTorch build separately (Apple MPS or Windows CUDA).
make install-jql
make all LABELS=hr,is DEVICE=mps  # Apple Silicon; 6k-sentence pilot, one-hour JQL batch
make all DEVICE=mps                 # Full Leipzig corpus, one-hour JQL batch
make rate DEVICE=cuda    # Windows/NVIDIA; resumes the same rating output
```

Targets can be run individually (`make download`, `make filter`, `make anonymize`, `make count`, `make assess`, `make rate`, `make score-report`). Use `LABELS=hr,is` to acquire selected labels, `MAX_SECONDS=3600` to set the scoring window, and `BATCH_SIZE=64` to tune inference. Re-run `make rate` to continue; completed annotations are skipped. JQL inference is local-only and is not run on GitHub Actions.

The anonymization stage currently performs pattern-based redaction of email addresses, URLs, IPv4 addresses and phone-like strings in sentence text. It is **not complete anonymization**: names, postal addresses and indirect identifiers require additional detection and review. Source provenance is retained in the local corpus for traceability. The filtering stage applies the agreed news-only Unicode decimal-digit rule, removes empty text and reports duplicates without silently dropping them. See [the JQL annotation and pipeline notes](docs/jql-edu-annotation.md).
