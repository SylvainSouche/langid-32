# BSC Legal Catalan–Spanish Parallel Corpus

**Text unit:** Sentence pairs, paragraphs and documents  
**Primary source:** https://huggingface.co/datasets/BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus

## Creator and origin

Barcelona Supercomputing Center, Language Technologies Unit; public-administration sources.

## Access methods

HF dataset; downloads dogc_ca-es.tsv, legal_ca-es_dataset_clean.tsv, apdcat_ca-es.docs.jsonl over HTTPS.

## File types and structure

TSV sentence-level, TSV paragraph-level, JSONL document-level parallel data.

## Distribution conditions and rights

Dataset card declares CC BY 4.0 for the corpus. However, its source section describes distinct underlying bases: DOGC material as CC0; public-administration documents under the Catalan open-data licence (described by the provider as equivalent to CC0); and APDCAT documents collected under a data-sharing agreement. The card also warns that personal and sensitive information may be present and prohibits re-identification. Do not flatten this provenance into one assumed source licence: retain subcorpus/source identifiers and review the APDCAT agreement and privacy risk before reuse or redistribution.

## Content and language coverage

Authentic bilingual legal text: ~5.4M sentence pairs, ~13k paragraphs, 450 APDCAT documents (~170k words/language).

## Verified upstream availability (independent of project acquisition)

The dataset card at Hub revision `5f7eda4` declares CC BY 4.0 and reports approximately 5.4 million sentence pairs in `dogc_ca-es.tsv`, approximately 13,000 paragraph pairs in `legal_ca-es_dataset_clean.tsv`, and 450 parallel APDCAT documents in `apdcat_ca-es.docs.jsonl` (about 170,000 words per language). These are three distinct granularities and must not be summed as if they were all sentences. The 5.4M value is one pair count, represented on both Catalan and Spanish sides; do not add the two sides together when reporting corpus size. The provider describes the texts as authentic and non-synthetic and says the sentence/paragraph datasets were deduplicated. Source: https://huggingface.co/datasets/BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus

## Current langid-32 acquisition snapshot

62,518 current Catalan records; sample, not full corpus; Spanish side not staged as a target-language source.

| Language | Current staged records |
|---|---:|
| ca | 62,518 |

**Current staged total:** 62,518 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Pinned upstream snapshot

The audit targets Hugging Face revision `5f7eda4` (the README update dated 2026-10-19; abbreviated commit identifier surfaced by the Hub). Hub file sizes at that revision are: `dogc_ca-es.tsv` 2,068,213,310 bytes; `legal_ca-es_dataset_clean.tsv` 11,254,086 bytes; `apdcat_ca-es.docs.jsonl` 2,542,379 bytes. The DOGC Xet pointer exposes SHA-256 `6fef096b2ac863650c36898ff503ae0bb4deb30d9a1ce9a06ccecf048b6a1afe`. The audit workflow independently downloads each file and records its actual SHA-256 before parsing. Source snapshot: https://huggingface.co/datasets/BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus/tree/5f7eda4

## Remaining checks

- Record exact audit results and retrieval date after the GitHub Actions run completes.
- Count full upstream records by language in the source's native unit, independently of project sampling.
- Record raw, eligible-after-source-filters and project-selected counts separately.
- Verify file-level rights and redistribution conditions before public release.
