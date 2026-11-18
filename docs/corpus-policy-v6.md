# Corpus v6 acquisition and selection policy

Status: approved project policy, 2026-11-16.

## Target and retention

- Build a **30,000-record usable pool per language** (34 languages; maximum target pool 1,020,000).
- Preserve the first **20,000 records per language as the core pool** for the first model comparison.
- Keep any accepted records above 20,000, up to 30,000, as **reserve material**. Do not discard it or silently mix it into the first 20k core set.
- If a language has fewer than 30,000 usable records after all available sources are exhausted, retain the shortfall explicitly; do not pad with low-quality or mislabeled records.

## Source concentration

- Aim for no single source to exceed **30%** of a language's 30,000-record pool (9,000 records).
- **Hard ceiling: 50%** per source (15,000 records) for every language where sufficient alternatives exist.
- Exceed 50% only for a documented low-resource exception: the language cannot reach the target from available eligible alternatives. Record the language, source, actual share, alternatives attempted, and remaining deficit.
- Apply quotas after all source adapters have run, and after normalization, privacy exclusion and global duplicate exclusion. Do not let the first source ingested automatically win a quota.
- Source means a distinct dataset/release family, not an individual archive shard, locale file, domain, or workflow artifact.

## Mandatory exclusions

Remove a record entirely (do not redact or repair it) if it:
- matches the project's PII/identifier exclusion rules (including email addresses, URLs, IP addresses, phone-like identifiers and long numeric identifiers under the agreed conservative patterns); or
- has normalized text that occurs under more than one language label anywhere in the combined candidate.

For cross-language collisions, remove **every occurrence of the colliding normalized string from every language**. Do not keep the first language, majority label, or earliest source. Within-language exact duplicates are also reduced to one record, retaining deterministic provenance for the kept copy.

These exclusions are applied globally across all staged sources before quota selection. Report excluded counts by source and language, without exposing the matched personal text in reports.

## Selection order

1. Acquire and stage all eligible sources with immutable release identifiers and file hashes.
2. Apply shared NFC and whitespace normalization and common length/script sanity checks.
3. Remove PII/identifier matches and all cross-language collision strings; remove within-language duplicates.
4. Split by stable document/group before selecting records; preserve source group boundaries across languages where applicable.
5. Select up to 30,000 per language using deterministic seeded sampling and source quotas. Prefer source diversity up to the 30% target; never exceed 50%.
6. Label records 1–20,000 per language as core and 20,001–30,000 as reserve. Keep reserve separate from train/validation/test until explicitly promoted.
7. Produce per-language/source counts, exclusions, group counts, domain mix, licence/provenance manifest, hashes and a validation report.

## Source priority and acquisition status

The current source list and all acquisition decisions are maintained in the [canonical source register](source-register.md). That register distinguishes sources actually staged from desk-researched alternatives, failed downloads and routes explicitly not pursued. This policy does not authorise acquisition from every source mentioned in historical audit or discovery documents.

Current technical candidates include the text-only Common Voice pilot, Tatoeba CC0, DGT-TM 2021, Målfrid 2026, IGC2024 Filtered-1, GreynirCorpus, TeMU-BSC, BSC Legal Catalan-Spanish, Catalan-DPO-V2, Korean Wikipedia, UN Arabic-English Filtered, FineWeb and FineWeb2. Each has a separate rights and attribution status; staged does not mean cleared. See the source register for exact counts, run links, conditions and decisions.

JRC-Acquis, Europarl v7, HPLT 3.0 and OPUS were investigated but are not in the current staged candidate artifacts. Leipzig bulk-archive discovery did not identify target archive links, but the separate REST API has now been probed successfully: it exposes 104 catalogue entries and corpora for 20/34 target labels, with per-sentence source IDs, URLs and dates. It remains on rights hold; the API's CC BY 4.0 label does not clear underlying news/web/Wikipedia works, and no Leipzig sentence text has been acquired. See the [Leipzig REST API audit](leipzig-rest-api-audit-2026-11-18.md). The Korea.kr/Korean legal-portal route and Korean Law Open Data API were not pursued; they are not current acquisition priorities. Do not revive these routes implicitly.

The Mozilla Data Collective acquisition workflow is retired. The retained Common Voice pilot reads text-only validated sentences from the unofficial third-party `fsicoli/common_voice_22_0` conversion plus a limited Croatian CV27 subset; it does not fetch audio or speaker/demographic metadata. Romanian terms acceptance is locale-specific and cannot be generalized to other locales. The CV22 conversion is now pinned to immutable HF revision `ae911de250fe9375d08e2daa2105b671d659d446`, with row-level sentence IDs and locale-file hashes. Locale-specific distribution terms and the third-party conversion chain remain release gates. If those checks fail, exclude affected records rather than silently reverting to MDC or another mirror.

FineWeb2 is not a default backfill source for a public release: all FineWeb/FineWeb2 excerpts remain on legal hold pending defensible excerpt-level rights analysis. FineWeb original is English-only and subject to the same underlying-page rights issue.

## Reproducibility and release status

- Pin dataset release, retrieval date, source URL, licence/terms, file SHA-256 and adapter version.
- Keep raw downloads and private provenance sidecars out of Git.
- Retain source-specific licence and attribution conditions; a source's compilation licence does not settle rights in underlying text.
- A technically validated candidate is not automatically rights-cleared or suitable for redistribution.
