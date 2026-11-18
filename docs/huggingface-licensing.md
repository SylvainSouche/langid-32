# Source licensing, terms and publication policy

## Current publication decision

**Do not publish the current candidate corpus to Hugging Face.**

This is a corpus-maturity decision as well as a release-management rule: the target is **20,000–30,000 curated records per language, with varied and independently identified sources**. The current Common Voice pilot is only one initial source component and does not meet that target. No public dataset release or dataset-level licence is being declared at this stage.

The GitHub repository's root `LICENSE` is MIT and applies to project software. It does not apply to the third-party text records and must not be copied as the dataset licence.

## Hugging Face public-repository terms are a further rights grant

Hugging Face's Terms of Service make the uploader responsible for content and require the uploader to warrant that they own/control it or otherwise have the right to post it. For a public repository, the uploader grants each Hub user a **perpetual, irrevocable, worldwide, royalty-free, non-exclusive licence** to use, display, publish, reproduce, distribute and make derivative works of the content through Hugging Face services. The uploader also agrees to indemnify Hugging Face for claims arising from content or data posted or used.

This is materially broader than merely storing a file on a website. Before a public dataset upload, the rights held by the project must cover the rights the Hub Terms grant to other users. A source's CC0/ODC-BY packaging tag does not supply those rights for underlying excerpts.

The Hub's dataset-card documentation describes the YAML `license` field as metadata displayed on the dataset page and used for discovery/filtering. It does not describe a source-by-source rights verification process. The Content Policy prohibits content infringing third-party IP or privacy rights and provides reporting/DMCA channels; those are reactive moderation mechanisms, not pre-publication clearance.

Accordingly, the current HF dataset repository remains empty and no text-bearing package is uploaded. The existing repository MIT tag applies to the software repository only; it must not be represented as the text dataset's licence.

## Distinguish data licence from contractual terms

A data licence and a platform's Terms of Service (ToS) or dataset agreement are different instruments:

- The **CC0 dedication/licence** concerns rights in the data.
- Mozilla's **ToS and dataset agreement** impose separate conditions on access and use. They are not themselves the data licence.
- Compliance with contractual conditions remains necessary even where the underlying data is CC0.

The project records the underlying Common Voice text as CC0, but this does not resolve separate contractual terms. No Common Voice-derived text is authorised for redistribution until the no-mirroring terms and their application to the specific acquisition route have been reviewed.

## Common Voice 22.0 — HF conversion

The current pilot uses text from the third-party Hugging Face conversion `fsicoli/common_voice_22_0`, representing Common Voice Corpus 22.0.

The source chain is understood as: upstream Common Voice data → conversion/publication process → Hugging Face dataset. The conversion is an intermediary publication point, not the original source of the underlying text. The underlying Common Voice text is identified as CC0; the source's CC0 status should not be confused with Mozilla's separate contractual terms.

The third-party HF conversion was created on 27 June 2025 and updated on 11 August 2025, before the current Mozilla Common Voice terms effective 31 October 2025. The newer terms make Common Voice datasets available through MDC and prohibit posting, distributing or mirroring any Common Voice dataset, in whole or in part, on other platforms. The effect of those later terms on a pre-existing third-party conversion and downstream reuse of excerpts has not been established. The old HF conversion's CC0 declaration remains evidence about the source copyright status; it does not answer the separate contractual question.

For reproducibility, retain the exact HF repository, requested revision, resolved commit where available, locale, retrieval date, file hash and conversion provenance in the internal source manifest. A mutable `main` reference alone is not sufficient provenance for a final release.

## Common Voice contractual restriction and project hold

The current Mozilla Common Voice terms prohibit posting, distributing or mirroring **any Common Voice dataset, in whole or in part**, on other platforms or services. A partial, curated text selection is not treated as an exception. The third-party CV22 HF conversion predates the 31 October 2025 terms, and the contractual effect on downstream users of that pre-existing copy has not been established. The source's CC0 declaration does not resolve that separate question.

Accordingly:
- CV22 text remains on hold pending legal review of the pre-existing conversion and downstream excerpt use.
- CV27 Croatian text remains on hold because locale-specific terms acceptance is not recorded.
- The recorded CV27 Romanian acceptance is specific to Romanian and expressly prohibits re-hosting/re-sharing; it does not authorise other locales.
- No Common Voice-derived text may be included in a public release until the relevant terms and acquisition route are resolved.
- Excluding audio, speaker identifiers or contributor metadata does not resolve the no-mirroring clause.

The last point describes the project's data-minimisation design and intent; it is not an absolute guarantee that arbitrary text can never contain personal or identifying information. Continue applying automated filtering and appropriate review.

## Current candidate inventory

| Component | Rows in current technical pilot | Treatment |
|---|---:|---|
| Common Voice 22.0 via HF conversion | 259,352 | Technical candidates only; no redistribution pending legal review of post-31 October 2025 terms and pre-existing third-party conversion |
| Common Voice Scripted Speech 27.0, Croatian | 1,724 | Technical candidates only; locale-specific terms acceptance not recorded; no redistribution |
| **Total** | **261,076** | Development-only, not a public release |

These counts describe the current technical pilot and will change as additional sources are identified, reviewed and curated.

## Dataset release gate

A public Hugging Face release remains blocked until all of the following are met:

1. The corpus reaches 20,000–30,000 curated records per language.
2. Each language has meaningful diversity of sources; the target must not be met merely by scaling one source or duplicating similar material.
3. Each source has recorded provenance, applicable data licence, ToS/dataset-agreement conditions, retrieval revision and integrity hashes.
4. No Common Voice-derived text is distributed while the no-mirroring question or locale-specific terms remain unresolved; partial selections are not treated as an exception.
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


## Source attribution and scholarly citations

The project maintains a separate [source attribution and citation register](source-attribution-register.md). It distinguishes:
1. mandatory legal attribution and notices under source licences or reuse terms;
2. scholarly citations to source dataset papers, corpus descriptions or releases; and
3. record-level provenance to the original source document/article.

These are not interchangeable. In particular, a citation to a dataset paper does not satisfy a requirement to identify the underlying article, source and date, nor does it satisfy the European Commission source/ownership notice applicable to DGT-TM and JRC-Acquis.

For article-derived material, retain title, author or issuing body, publication date, source URL, licence/notice and source record ID where available. If a licence or article-level term requires this information and it cannot be recovered, hold or exclude the affected record. Do not reproduce article text merely to satisfy an attribution requirement: use bibliographic references and exact prescribed notices unless a quotation is explicitly required and independently justified.

Before a source is enabled for a release, capture the exact attribution wording from its current official terms, determine whether attribution is per-record or may be consolidated, and verify that the source permits redistribution of the selected text. The release must contain an `ATTRIBUTION.md` generated from the sources actually retained. It must not contain boilerplate attribution for sources that were considered but not used.
