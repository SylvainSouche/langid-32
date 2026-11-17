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
size_categories:
- 100K<n<1M
---

# langid-32

**Status: preparation snapshot — not a released or rights-cleared dataset.**

This repository is being prepared as a multilingual text dataset for language identification. The project retains the name `langid-32` for historical continuity; the current pilot contains **34 language labels**.

## Important publication notice

No dataset licence is declared in this card. The MIT licence in the companion GitHub software repository applies to software, not to these text records.

The current candidate combines:
- Common Voice Corpus 22.0 text obtained from the third-party Hugging Face conversion `fsicoli/common_voice_22_0`.
- A previously acquired and curated Croatian subset from Mozilla Common Voice Scripted Speech 27.0.

The conversion's CC0 label and the Common Voice source's licence/terms have not yet been independently reconciled for every locale. The Croatian-specific Data Collective acceptance and redistribution terms have not been verified in the project audit. The presence of a `CC0-1.0` field in the staging records is a source claim, not a legal determination by this project.

**Do not treat this snapshot as cleared for redistribution, training, or commercial use.** The candidate data is not uploaded as part of this preparation snapshot. A public data release will require a documented per-source and per-locale rights review, an explicit dataset licence decision, and a separate release approval.

## Planned data format

The planned public table has these columns:

| Column | Type | Meaning |
|---|---|---|
| `text` | string | Normalized sentence text |
| `label` | string | ISO 639-1 project language label |
| `source` | string | Source family and release key |
| `source_release` | string | Human-readable source release |
| `source_license_claim` | string | Licence label reported by the source; not a project rights grant |

Internal group identifiers, raw download URLs, signed URLs, speaker information, audio, and raw source manifests are excluded from the public table.

## Current preparation snapshot

The latest technical candidate has 261,076 rows across 34 labels. It is an un-split candidate pool: no train/validation/test partition is claimed. Per-language counts range from 1,450 (Irish) to 9,000 (the sampling cap for many labels). See the accompanying preparation report when a package is generated.

The current data has undergone automated Unicode NFC and whitespace normalization, length filtering, basic identifier/PII-pattern filtering, within-label exact deduplication, cross-label exact-string collision removal, and deterministic per-label sampling. These checks are heuristic and are not complete privacy review, human language validation, or quality assurance.

## Intended use

The intended research task is sentence-level language identification. The current snapshot should be used only for technical pipeline validation by the project maintainers while source rights remain under review.

## Citation

If and when a release is approved, cite the exact dataset revision and the source releases listed in its provenance manifest. No citable public data release is made by this preparation snapshot.
