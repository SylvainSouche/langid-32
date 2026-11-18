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

The current Common Voice-based material is an initial component of that work, not a release candidate. We are identifying and integrating additional sources. A raw or early-stage pilot is not representative of the intended final corpus.

## Sources and terms

The current development inventory includes several independent candidate families: Common Voice text, Tatoeba CC0, DGT-TM 2021, Målfrid 2026, Icelandic IGC2024 and GreynirCorpus, Catalan BSC/TeMU components, Korean Wikipedia, an UN-derived Arabic corpus, and FineWeb/FineWeb2 web-extracted candidates. These are not all approved for redistribution. The current source-specific rights status and required notices are maintained in the GitHub project documentation.

No single licence is declared for the combined dataset at this stage. The software repository's MIT licence does not apply to the text. A source wrapper or compilation licence is not treated as a blanket licence for underlying third-party passages.

### Source attribution and citations

The release will distinguish three things: (1) legal attribution required by the source licence or reuse terms, (2) scholarly citation of the dataset paper/project/release, and (3) record-level provenance linking each retained text to its source document. A bibliography entry or citation to a dataset paper does not replace article-level attribution where the source requires it.

Some source terms require specific notices. For example, DGT-TM and JRC-Acquis require source attribution and retention of European Commission ownership; Målfrid is subject to NLOD attribution and separate database-right considerations; CC BY sources require appropriate credit, a licence link and indication of changes; and any share-alike source requires a separate compatibility decision. The release will include an `ATTRIBUTION.md` containing the exact required notices and source citations, and record-level article/document attribution where required and permitted.

For article-derived text, the internal provenance ledger must retain the original article/document title, author or issuing body, publication date, URL, source licence/notice and source record identifier whenever available. If a source requires that information and it cannot be recovered, the affected record will be held or excluded. We will not reproduce article passages merely to satisfy a citation requirement: citations and attribution notices are used unless an actual quotation is explicitly required and legally appropriate.

Korea.kr/KOGL material is not approved for this release: article-specific conditions include AI-training restrictions and a restriction on resale of training datasets made from public works. FineWeb/FineWeb2 and HPLT extracted passages remain on legal hold because compilation/packaging licences do not clear the underlying web text.

See `docs/huggingface-licensing.md` and `docs/source-attribution-register.md` in the GitHub repository for the source-by-source decisions. Source-level rights and contractual restrictions remain distinct.

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

The current technical staging includes separate artifacts: 613,860 waiting-source candidates, 261,076 Common Voice pilot rows, 80,155 fresh Tatoeba CC0 rows and 120,000 DGT-TM rows. These figures are not additive, have not all been globally deduplicated against one another, and are not final usable-record counts. No public release or language-level legal clearance is claimed.

Automated processing includes Unicode NFC and whitespace normalization, length filtering, basic identifier/PII-pattern filtering, within-label exact deduplication, cross-label exact-string collision removal, and deterministic per-language sampling. These are curation heuristics, not complete privacy clearance, human language validation, or quality assurance.

**This development snapshot is not published on Hugging Face and must not be presented as the completed langid-32 dataset.**

## Citation

A citable dataset release will be assigned only after the corpus meets the release criteria and a versioned release is approved. Cite the exact dataset revision and its source manifest at that time. Each source will also be cited using its own recommended scholarly reference where one is published; mandatory legal attribution will be provided separately in `ATTRIBUTION.md`.
