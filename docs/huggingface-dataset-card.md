---
pretty_name: langid-32 multilingual language-identification text candidates
task_categories:
- text-classification
language:
- ar
- bg
- ca
- cs
- da
- de
- el
- en
- es
- et
- fi
- fr
- ga
- hr
- hu
- is
- it
- ja
- ko
- lt
- lv
- mt
- nb
- nl
- nn
- pl
- pt
- ro
- ru
- sk
- sl
- sv
- tr
- zh
---

# langid-32

**Status: private development project — no dataset release is currently published or authorised.**

The project retains the name `langid-32` for historical continuity; the current pilot covers **34 language labels**. This repository is being developed for sentence-level language identification.

## Release policy

We will not publish a dataset snapshot to Hugging Face until the corpus has reached the project's target scale of **20,000–30,000 curated records per language**, with meaningful source diversity within each language.

The current Common Voice-based material is an initial technical pilot, not a release candidate and not authorised for redistribution. The refreshed pilot is recorded in GitHub Actions run [44293665775](https://github.com/SylvainSouche/langid-32/actions/runs/44293665775): 261,076 text-only rows across 34 labels, pinned to Common Voice conversion revision `ae911de250fe9375d08e2daa2105b671d659d446`. CV22 is a pre-existing third-party HF conversion declaring CC0, but Mozilla's terms effective 31 October 2025 include a no-mirroring restriction covering whole or partial datasets; its application to this earlier conversion and downstream excerpts remains unresolved. CV27 Croatian terms acceptance is not recorded. No Common Voice-derived text will be published pending review. We are identifying and integrating additional sources.

## Sources and terms

The current staged source families are Common Voice text, Tatoeba CC0, DGT-TM 2021, Målfrid 2026, Icelandic IGC2024 and GreynirCorpus, Catalan BSC/TeMU components (Catalan-DPO-V2 is quarantined due to mixed-language mislabelling and is not part of the current usable candidate count), Korean Wikipedia, an UN-derived Arabic corpus, and FineWeb/FineWeb2 web-extracted candidates. Some remain on legal hold; others require attribution or constituent-level review. HPLT, JRC-Acquis, Europarl and OPUS were investigated but not acquired. The Leipzig REST API was successfully probed at the metadata/sentence-service level (104 catalogue entries; 20 of 34 target labels; 29 of 30 sentence-service probes returned examples), but no Leipzig sentence text was retained. The linked usage terms were blocked by an Anubis challenge and underlying source works remain uncleared; this is a rights hold, not a failed API discovery. The Korean government legal portal/API route was not pursued. The canonical [source register](source-register.md) gives the exact status of every source and retired route.

No single licence is declared for the combined dataset at this stage. The software repository's MIT licence does not apply to the text. A source wrapper or compilation licence is not treated as a blanket licence for underlying third-party passages.

### Source attribution and citations

The release will distinguish three things: (1) legal attribution required by the source licence or reuse terms, (2) scholarly citation of the dataset paper/project/release, and (3) record-level provenance linking each retained text to its source document. A bibliography entry or citation to a dataset paper does not replace article-level attribution where the source requires it.

Some source terms require specific notices. For example, DGT-TM and JRC-Acquis require source attribution and retention of European Commission ownership; Målfrid is subject to NLOD attribution and separate database-right considerations; CC BY sources require appropriate credit, a licence link and indication of changes; and any share-alike source requires a separate compatibility decision. The release will include an `ATTRIBUTION.md` containing the exact required notices and source citations, and record-level article/document attribution where required and permitted.

For article-derived text, the internal provenance ledger must retain the original article/document title, author or issuing body, publication date, URL, source licence/notice and source record identifier whenever available. If a source requires that information and it cannot be recovered, the affected record will be held or excluded. We will not reproduce article passages merely to satisfy a citation requirement: citations and attribution notices are used unless an actual quotation is explicitly required and legally appropriate.

The Korea.kr/KOGL government-article portal was an exploratory route only; it was not pursued and no articles from it were acquired. FineWeb/FineWeb2 and HPLT extracted passages remain on legal hold because compilation/packaging licences do not clear the underlying web text.

See `docs/source-register.md` for the canonical status of all acquired, investigated and retired sources; `docs/huggingface-licensing.md` and `docs/source-attribution-register.md` hold the source-by-source rights and attribution analysis. Source-level rights and contractual restrictions remain distinct.

## Intended data format

The planned public table is:

| Column | Type | Meaning |
|---|---|---|
| `text` | string | Normalized sentence text |
| `label` | string | ISO 639-1 project language label |
| `source` | string | Source family and release key |
| `source_release` | string | Human-readable source release |
| `source_license_claim` | string | Source-reported licence identifier |

The eventual release will include source-level provenance, an attribution file, a source bibliography, per-language and per-source counts, quality/privacy information, and a dataset-level licensing statement consistent with all applicable source terms. The attribution file will be generated from the records actually retained, not from the list of sources merely considered.

## Current development snapshot

The historical waiting-source artifact contains 613,860 rows, but 30,790 Catalan-DPO rows are quarantined because English and Catalan text were all labelled `ca`; the non-DPO, non-Greynir remainder is 578,140 technical candidates. Other separate artifacts include 261,076 Common Voice pilot rows, 80,155 Tatoeba CC0 rows and 120,000 DGT-TM rows. These figures are not additive, have not all been globally deduplicated against one another, and are not final usable-record counts. No public release or language-level legal clearance is claimed.

Automated processing includes Unicode NFC and whitespace normalization, length filtering, basic identifier/PII-pattern filtering, within-label exact deduplication, cross-label exact-string collision removal, and deterministic per-language sampling. These are curation heuristics, not complete privacy clearance, human language validation, or quality assurance.

**This development snapshot is not published on Hugging Face and must not be presented as the completed langid-32 dataset.**

## Citation

A citable dataset release will be assigned only after the corpus meets the release criteria and a versioned release is approved. Cite the exact dataset revision and its source manifest at that time. Each source will also be cited using its own recommended scholarly reference where one is published; mandatory legal attribution will be provided separately in `ATTRIBUTION.md`.
