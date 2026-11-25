# Source licensing, terms and publication policy

## Current publication decision

**Do not publish the current candidate corpus to Hugging Face.**

The target remains **20,000–30,000 curated records per language**, with varied and independently identified sources. The current HF-hosted Common Voice text pilot is only one initial source component and does not meet that target. No public dataset release or dataset-level licence is being declared at this stage.

The GitHub repository's root `LICENSE` is MIT and applies to project software. It does not apply to third-party text records and must not be copied as the dataset licence.

## HF-hosted Common Voice 22.0 CC0 source

The current technical pilot uses the HF-hosted dataset [`fsicoli/common_voice_22_0`](https://huggingface.co/datasets/fsicoli/common_voice_22_0). Its Hugging Face dataset card declares **CC0-1.0** and describes it as an unofficial conversion of Common Voice Corpus 22.0.

The project uses that Hugging Face repository as its acquisition source and downloads only `transcript/<locale>/validated_sentences.tsv`. No audio, speaker identifiers, contributor IDs or demographic metadata are acquired. The workflow pins the resolved repository revision and retains locale, sentence ID, TSV SHA-256 and retrieval metadata.

The latest HF-only pilot run [44315031026](https://github.com/SylvainSouche/langid-32/actions/runs/44315031026) selected 259,352 text rows across 33 target labels. Its artifact [14431583044](https://github.com/SylvainSouche/langid-32/actions/runs/44315031026) contains metadata only, not sentence text. Croatian (`hr`) is not supplied by this source and remains an explicit source gap; no substitute from another Common Voice distribution is used.

For scholarly acknowledgement, cite Ardila et al. (2020), “Common Voice: A Massively-Multilingual Speech Corpus,” *Proceedings of LREC 2020*, pp. 4211–4215, https://aclanthology.org/2020.lrec-1.520/, together with the exact HF dataset and immutable revision.

## Voluntary source-selection decision

The project voluntarily does not use the Mozilla Data Collective repository or any data hosted there. We consider its contractual practices abusive. This is a project sourcing decision, not a legal conclusion.

## Hugging Face public-repository terms are a further rights grant

Hugging Face's Terms of Service make the uploader responsible for content and require the uploader to warrant that they own/control it or otherwise have the right to post it. For a public repository, the uploader grants each Hub user a **perpetual, irrevocable, worldwide, royalty-free, non-exclusive licence** to use, display, publish, reproduce, distribute and make derivative works of the content through Hugging Face services. The uploader also agrees to indemnify Hugging Face for claims arising from content or data posted or used.

Before a public dataset upload, the rights held by the project must cover the rights the Hub Terms grant to other users. A source's CC0/ODC-BY packaging tag does not supply those rights for underlying excerpts.

Accordingly, the current HF dataset repository remains empty and no text-bearing package is uploaded. The GitHub repository's MIT licence applies to software only. The HF dataset repository's initial MIT tag is not an established text-dataset licence and must be removed or replaced before any dataset publication.

## Dataset release gate

A public Hugging Face release remains blocked until all of the following are met:

1. The corpus reaches 20,000–30,000 curated records per language.
2. Each language has meaningful diversity of sources; the target must not be met merely by scaling one source or duplicating similar material.
3. Each source has recorded provenance, applicable data licence, retrieval revision and integrity hashes.
4. Every included source has been checked for redistribution rights and any required source-specific notices.
5. The released representation excludes audio, direct speaker/contributor identifiers, internal group IDs and private acquisition artefacts.
6. Quality and privacy checks are run on the assembled release, with their limitations documented.
7. A release version and dataset-level licence/notice decision are explicitly approved.

Until then, keep development artefacts in controlled project storage and do not upload candidate data to the Hugging Face dataset repository.

## Publication metadata

- Do not declare the dataset as MIT merely because the software repository is MIT-licensed.
- Do not infer that a combined dataset automatically has a single licence merely because one or more source components are CC0.
- When the release gate is met, state the applicable dataset licence and source-specific notices accurately. If the source terms require additional conditions or notices, include them.
- Keep the source-level provenance manifest with the release, but remove temporary signed URLs, credentials, private identifiers and other sensitive acquisition metadata.

## Scope

This document records the project's current understanding and operational policy. It is not a legal opinion. Where source rights or licence scope are ambiguous, preserve the uncertainty and obtain a source-specific review rather than silently broadening permissions.

## Source attribution and scholarly citations

The project maintains a separate [source attribution and citation register](source-attribution-register.md). It distinguishes mandatory legal attribution, scholarly citations and record-level provenance. A dataset-paper citation does not replace article-level attribution where a source requires it.

For article-derived material, retain title, author or issuing body, publication date, source URL, licence/notice and source record ID where available. If a licence or article-level term requires that information and it cannot be recovered, hold or exclude the affected record. Do not reproduce article text merely to satisfy an attribution requirement: use bibliographic references and exact prescribed notices unless a quotation is explicitly required and independently justified.

Before a source is enabled for a release, capture the exact attribution wording from its official source, determine whether attribution is per-record or may be consolidated, and verify that the source permits redistribution of the selected text. The release must contain an `ATTRIBUTION.md` generated from sources actually retained.
