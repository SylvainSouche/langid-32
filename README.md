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

## Corpus status — 18 November 2026

**Preparation only — not release-ready.**

No public corpus data has been uploaded to the Hugging Face dataset repository. No language is currently release-cleared.

Measured technical staging currently includes:

| Staging set | Rows | Meaning |
|---|---:|---|
| Waiting-source acquisition | 613,860 | New source candidates across Catalan, Icelandic, Bokmål, Nynorsk, Korean and Arabic; includes 100,000 FineWeb2 backfill candidates |
| Common Voice text-only pilot | 261,076 | Pilot rows across 34 labels; not a release corpus |
| Tatoeba CC0 refresh | 80,155 | Fresh staged export; concentrated in a subset of languages |
| DGT-TM 2021 refresh | 120,000 | 5,000 staged translation units per 24 EU languages |
| Legacy v5 candidate | 640,000 | Historical 32-label technical candidate; source balance and rights gates fail |

These are **separate staging artifacts and must not be summed**. They have not all been globally deduplicated against one another. They are not final usable-record counts.

The waiting-source artifact contains useful independent candidates, but some classes remain concentrated in one source and several licences or underlying-text rights remain under review. In particular:

- Catalan: BSC/TeMU and Catalan-DPO components require constituent-level provenance and terms checks; FineWeb2 is on legal hold.
- Icelandic: IGC2024 and Greynir are CC BY 4.0 candidates; FineWeb2 is on legal hold.
- Bokmål and Nynorsk: Målfrid 2026 is a substantial NLOD 2.0 source, but each current 50k candidate batch comes from that one source.
- Korean: the current Wikipedia candidate has CC BY-SA/GFDL obligations; it is not yet approved for the release.
- Arabic: the UN-derived candidate needs confirmation of the underlying UN source terms; the Hugging Face card alone is not sufficient.

See [the dated corpus status report](docs/corpus-status-2026-11-17.md), [source inventory](docs/corpus-inventory.md), [v6 corpus policy](docs/corpus-policy-v6.md), and [source exclusion registry](docs/source-exclusion-registry.md) for measured details and acquisition decisions.

## Data preparation rules

All sources are staged independently with immutable release identifiers, retrieval dates, source URLs, file hashes, adapter versions, licence/terms and attribution requirements.

The global merge is responsible for:

1. NFC and whitespace normalization, common length and byte limits, and language/script sanity checks.
2. Privacy-pattern exclusions and source/document exclusions from the versioned registry.
3. Exact deduplication within each language across **all** staged sources.
4. Removal of every normalized text string found under more than one language label. No “first language wins” rule is used.
5. Stable document/group-aware train, validation and test assignment before sample selection.
6. Deterministic source-aware selection, per-language source-share reporting, and a 20k core plus 10k reserve.
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

Rights holders and affected persons can submit copyright, database-rights, privacy, source-terms and removal notices to **[abuse@souche.fr](mailto:abuse@souche.fr)**. The mailbox is configured in the project maintainer's email client and has successfully received and acknowledged a test message. Operational case handling, source-level traceability and removal controls still need to be validated before release. See [Terms of Use](docs/terms-of-use.md), [Notice and Takedown](docs/notice-and-takedown.md), [web-text release controls](docs/web-text-release-controls.md), and the [source attribution and citation register](docs/source-attribution-register.md).

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
