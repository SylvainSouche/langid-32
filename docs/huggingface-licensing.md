# Source licensing, terms and publication policy

## Current publication decision

**Do not publish the current candidate corpus to Hugging Face.**

This is a corpus-maturity decision as well as a release-management rule: the target is **20,000–30,000 curated records per language, with varied and independently identified sources**. The current Common Voice pilot is only one initial source component and does not meet that target. No public dataset release or dataset-level licence is being declared at this stage.

The GitHub repository's root `LICENSE` is MIT and applies to project software. It does not apply to the third-party text records and must not be copied as the dataset licence.

## Distinguish data licence from contractual terms

A data licence and a platform's Terms of Service (ToS) or dataset agreement are different instruments:

- The **CC0 dedication/licence** concerns rights in the data.
- Mozilla's **ToS and dataset agreement** impose separate conditions on access and use. They are not themselves the data licence.
- Compliance with contractual conditions remains necessary even where the underlying data is CC0.

The project treats CC0 Common Voice text as permissible source material, subject to the applicable ToS/dataset agreement and the project's curation and privacy controls.

## Common Voice 22.0 — HF conversion

The current pilot uses text from the third-party Hugging Face conversion `fsicoli/common_voice_22_0`, representing Common Voice Corpus 22.0.

The source chain is understood as: upstream Common Voice data → conversion/publication process → Hugging Face dataset. The conversion is an intermediary publication point, not the original source of the underlying text. The underlying Common Voice text is identified as CC0; the source's CC0 status should not be confused with Mozilla's separate contractual terms.

Mozilla's ToS changed over time. The project's working hypothesis is that the public Common Voice publication sequence stopped at version 22 around the time of those changes. This is recorded as a hypothesis, not asserted as a proven explanation for the publication history.

For reproducibility, retain the exact HF repository, requested revision, resolved commit where available, locale, retrieval date, file hash and conversion provenance in the internal source manifest. A mutable `main` reference alone is not sufficient provenance for a final release.

## Common Voice contractual restriction and project compliance

The applicable Common Voice ToS/dataset agreement contains a **no-mirroring clause**. The project abides by that restriction:

- It does not mirror or redistribute the complete Common Voice dataset.
- It uses only a partial, curated text selection.
- It excludes audio and direct speaker/contributor identifiers.
- It does not attempt to identify contributors.
- The curated representation is designed to prevent identification of individual contributors.

The last point describes the project's data-minimisation design and intent; it is not an absolute guarantee that arbitrary text can never contain personal or identifying information. Continue applying automated filtering and appropriate review.

The Croatian Common Voice Scripted Speech 27.0 material is a partial curated subset retained from an authorised acquisition. Its source archive checksum and validated-sentences TSV hash are recorded in the internal audit material. The same no-mirroring approach applies: no complete source dataset, audio, or speaker identifiers are mirrored.

## Current candidate inventory

| Component | Rows in current technical pilot | Treatment |
|---|---:|---|
| Common Voice 22.0 via HF conversion | 259,352 | Partial curated text selection; source chain and hashes recorded |
| Common Voice Scripted Speech 27.0, Croatian | 1,724 | Retained partial curated text selection; source archive and TSV hashes recorded |
| **Total** | **261,076** | Development-only, not a public release |

These counts describe the current technical pilot and will change as additional sources are identified, reviewed and curated.

## Dataset release gate

A public Hugging Face release remains blocked until all of the following are met:

1. The corpus reaches 20,000–30,000 curated records per language.
2. Each language has meaningful diversity of sources; the target must not be met merely by scaling one source or duplicating similar material.
3. Each source has recorded provenance, applicable data licence, ToS/dataset-agreement conditions, retrieval revision and integrity hashes.
4. The no-mirroring restriction and any other source-specific contractual conditions are respected.
5. The released representation excludes audio, direct speaker/contributor identifiers, internal group IDs and private acquisition artefacts.
6. Quality and privacy checks are run on the assembled release, with their limitations documented.
7. A release version and dataset-level licence/notice decision are explicitly approved.

Until then, keep development artefacts in controlled project storage and do not upload the candidate data to the Hugging Face dataset repository.

## Publication metadata

- Do not declare the dataset as MIT merely because the software repository is MIT-licensed.
- Do not infer that a combined dataset automatically has a single licence merely because one or more source components are CC0.
- When the release gate is met, state the applicable dataset licence and source-specific notices accurately. If the source terms require additional conditions or notices, include them.
- Keep the source-level provenance manifest with the release, but remove temporary signed URLs, credentials, private identifiers and other sensitive acquisition metadata.

## Scope

This document records the project's current understanding and operational policy. It is not a legal opinion. Where source terms or the relationship between licence and contractual conditions are ambiguous, preserve the uncertainty and obtain a source-specific review rather than silently broadening permissions.
