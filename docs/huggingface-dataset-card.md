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

The current technical pilot combines:
- Common Voice Corpus 22.0 text obtained through the third-party Hugging Face conversion `fsicoli/common_voice_22_0`. The underlying Common Voice text is identified as CC0. The upstream-to-conversion publication chain is recorded for provenance.
- A partial, curated Croatian subset from Mozilla Common Voice Scripted Speech 27.0, retained from an authorised acquisition.

CC0 is the data licence. Mozilla's Terms of Service and dataset agreements are separate contractual terms, not a replacement data licence. Those terms have changed over time. The project's understanding is that the public Common Voice publication sequence stopped at version 22 around the period of those changes; this is a historical hypothesis, not a verified causal statement.

The relevant no-mirroring restriction is respected: this project does not mirror or redistribute the complete Common Voice dataset. It works only with a partial, curated text selection, with direct speaker/contributor identifiers and audio excluded and no intended means of identifying individual contributors. This minimisation reduces identification risk but is not a guarantee that every text fragment is free of personal or identifying information.

See `LICENSING.md` for the project's source and terms interpretation. Source-level rights and contractual restrictions remain documented separately.

## Intended data format

The planned public table is:

| Column | Type | Meaning |
|---|---|---|
| `text` | string | Normalized sentence text |
| `label` | string | ISO 639-1 project language label |
| `source` | string | Source family and release key |
| `source_release` | string | Human-readable source release |
| `source_license_claim` | string | Source-reported licence identifier |

The eventual release will include a source-level provenance summary, per-language counts, quality information, and a clear dataset-level licensing statement consistent with all applicable source terms.

## Current development snapshot

The current technical pilot contains 261,076 rows across 34 labels. It is an un-split candidate pool: no train/validation/test partition is claimed. Per-language counts are unequal and do not meet the project's target of 20,000–30,000 records per language.

Automated processing includes Unicode NFC and whitespace normalization, length filtering, basic identifier/PII-pattern filtering, within-label exact deduplication, cross-label exact-string collision removal, and deterministic per-language sampling. These are curation heuristics, not complete privacy clearance, human language validation, or quality assurance.

**This development snapshot is not published on Hugging Face and must not be presented as the completed langid-32 dataset.**

## Citation

A citable dataset release will be assigned only after the corpus meets the release criteria and a versioned release is approved. Cite the exact dataset revision and its source manifest at that time.
