---
pretty_name: langid-32 multilingual language-identification corpus
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
tags:
  - language-identification
  - multilingual
  - corpus
  - benchmark
---

# langid-32

A reproducible, multilingual text corpus and benchmark for **language identification across 34 language labels**. The historical project name reflects its original 32-language scope.

> **Status: under construction. No corpus data is currently published in this repository.**
> Source acquisition, quality checks and rights review are still in progress. Staged or technically usable text is not automatically approved for redistribution.

## Purpose

The project aims to build a balanced, traceable evaluation and training resource for language identification. It will make source composition, processing decisions, exclusions and licensing evidence inspectable rather than treating a large text dump as a benchmark.

The target is **up to 30,000 usable sentences per language**:
- **Core:** the first 20,000 records per language, intended for the initial model comparison.
- **Reserve:** up to 10,000 additional accepted records, kept separate until explicitly promoted.

A language may remain below target if eligible, sufficiently diverse material cannot be found. We will not fill gaps with low-quality or uncertainly labelled text.

## Languages

The 34 labels are:

`ar bg ca cs da de el en es et fi fr ga hr hu is it ja ko lt lv mt nb nl nn pl pt ro ru sk sl sv tr zh`

Norwegian Bokmål (`nb`) and Nynorsk (`nn`) are separate labels. Chinese (`zh`) is a combined label; source and script composition will be documented.

## Planned content

The corpus is being assembled from independently assessed sources, including:
- Leipzig news and Wikipedia sentence corpora;
- selected CC0 sentence material such as the Tatoeba CC0 export;
- selected public or institutional text and translation resources where source rights and provenance can be established;
- other language-specific sources only after technical, provenance and licensing review.

The initial Leipzig acquisition target is **3,000 news + 3,000 Wikipedia sentences per language**. News sentences containing Unicode decimal digits are excluded; the same digit rule is not applied to Wikipedia.

The eventual release is expected to contain sentence text, language labels and stable record identifiers, with source/provenance and licence information documented in manifests or accompanying metadata. The exact public schema and split files will be described when the first release is ready.

## Selection and preparation workflow

Each source is acquired and staged independently. The reproducible pipeline then:

1. Records the source/release identity, retrieval information, file hashes, adapter version, licence evidence and attribution requirements.
2. Normalizes Unicode to NFC and normalizes whitespace; applies common length, byte and language/script sanity checks.
3. Excludes records matching conservative personal-data and identifier patterns. This is automated screening, not a claim of complete anonymization.
4. Deduplicates normalized sentences globally within each language.
5. Removes **all occurrences** of a normalized sentence if it appears under more than one language label; no language is allowed to win by ingestion order.
6. Assigns stable document/group-aware splits before sample selection, to reduce leakage between related records.
7. Selects records deterministically, with source diversity quotas, and reports counts, exclusions and source composition.

Source concentration target: no single source should contribute more than **30%** of a language's pool. The **50% ceiling** is a documented exception limit where sufficient eligible alternatives do not exist. Repackagings of the same underlying material do not count as independent sources.

Raw source downloads and private provenance sidecars are not published as repository artifacts. Public releases will include appropriate manifests, counts, hashes and attribution information without exposing private or excluded text.

## Licensing approach

The goal is an **open, permissively reusable, non-copyleft corpus**. Source selection is made accordingly:

- Prefer **CC0** and **CC BY** material where the underlying text and database rights are sufficiently supported.
- CC BY material may be used only with the required attribution and licence notices.
- Exclude material carrying non-commercial, no-derivatives, share-alike or other incompatible restrictions from the intended release.
- A dataset card or compilation licence does not, by itself, establish rights in the underlying sentences. Unclear or unverified material stays on hold or is excluded.

There is **no blanket licence for the future corpus yet**. The final licence and attribution package will be determined by the sources actually included and their obligations. We will not relabel a mixed-source collection as CC0 or MIT merely for convenience.

## Planned model comparison

Once the corpus has sufficient source diversity, quality and rights clearance, the project intends to train and compare several compact language-identification approaches, including:

- character n-gram features with a sparse linear classifier;
- character n-gram embeddings with a compact classifier head;
- a byte-level Transformer trained from scratch.

The comparison will use documented, reproducible splits and per-language results. Model weights, training details and benchmark results will be published if the experiments prove useful and reproducible. These are future plans, not current results.

## Reproducibility and project status

The implementation, acquisition policies, source register, audits and pipeline are maintained in the [GitHub repository](https://github.com/SylvainSouche/langid-32).

Key project documents:
- [Corpus acquisition and selection policy](https://github.com/SylvainSouche/langid-32/blob/main/docs/corpus-policy-v6.md)
- [Canonical source register and rights status](https://github.com/SylvainSouche/langid-32/blob/main/docs/source-register.md)
- [Model design](https://github.com/SylvainSouche/langid-32/blob/main/docs/model-design.md)

Please do not treat this repository as a released dataset until a versioned data release, source manifests and final licensing information have been published.
