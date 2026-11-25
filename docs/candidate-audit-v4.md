> **Historical audit of v4.** This is a frozen analysis of the 16 November 2026 artifact, not the current corpus inventory or acquisition plan. See [the canonical source register](source-register.md) for current source status.

# Independent audit: three-source candidate v4

Audit date: 2026-11-16. Input: the private GitHub Actions artifact `multisource-candidate-v4-unicode-pii-clean`, produced by [run 43938190407](https://github.com/SylvainSouche/langid-32/actions/runs/43938190407). The archive was downloaded and its JSONL contents inspected locally. No corpus text was committed to Git.

## 1. Structural checks

| Check | Result |
|---|---:|
| Languages | 32 |
| Records | 640,000 |
| Train / validation / test | 512,000 / 64,000 / 64,000 |
| Per language | 16,000 / 2,000 / 2,000 |
| Output groups | 186,190 |
| Candidate groups before per-language cap | 241,195 |
| Conflicting splits for `group_id` | 0 |
| Conflicting splits for `split_group_id` | 0 |
| Exact normalized duplicates within a language | 0 |
| Output SHA-256 checks against manifest | all passed |
| Public split rows match the sidecar's text/language/source/split projection | all 640,000 matched |

The three public split files and the internal provenance sidecar have the expected row counts. The sidecar must remain private: it contains source grouping and provenance fields that are intentionally absent from the text-only split files.

## 2. Source composition

| Source | Final records | Share | Coverage |
|---|---:|---:|---|
| FineWeb2 v2.1.0 | 510,702 | 79.8% | 31 classes |
| DGT-TM 2021 | 92,196 | 14.4% | 24 EU official languages |
| Tatoeba CC0, 2026-11-14 | 37,102 | 5.8% | 17 classes represented in the final candidate |
| **Total** | **640,000** | **100%** | **32 classes** |

The source mix is not uniform across classes:

- English: 17,797 Tatoeba (89.0%) and 2,203 DGT-TM (11.0%); no FineWeb2.
- Russian: 10,582 Tatoeba (52.9%) and 9,418 FineWeb2 (47.1%).
- French: 10,251 FineWeb2 (51.3%), 7,190 Tatoeba (36.0%) and 2,559 DGT-TM (12.8%).
- Finnish: 15,077 FineWeb2, 3,766 DGT-TM and 1,157 Tatoeba.
- Most other EU classes are approximately 80% FineWeb2 and 20% DGT-TM. Non-EU classes without Tatoeba additions are entirely FineWeb2.

This gives every class the same row count, but not the same source or register distribution. In particular, English is almost entirely Tatoeba sentence material, while most other classes are web-crawl material plus a legal/administrative translation-memory component. That is a material domain confound for a general-purpose classifier.

## 3. Cross-language label collisions

There are **94 distinct exact text strings (194 records)** that occur under more than one language label. These are not within-language duplicates, so the merge's within-language deduplication correctly leaves them in place; however, the same input string cannot have a uniquely inferable language label.

- 67 of the colliding strings originate in DGT-TM.
- 27 originate in FineWeb2.
- 88 strings occur under two labels and six under three labels.

The DGT examples include proper names, scientific names, legal fragments, dates, multilingual headings and, in some cases, substantial text apparently left in another language. FineWeb2 examples include English cookie notices, website boilerplate and template text assigned to non-English classes. Some FineWeb2 examples have very high upstream `language_score` values despite being visibly English boilerplate. The score threshold is therefore not a guarantee of sentence-level language correctness.

**Recommendation:** quarantine these 94 strings in a separate ambiguity/label-conflict report and exclude them from supervised training unless individually resolved. They may be useful as a small ambiguity test set.

## 4. Domain concentration in the FineWeb2 component

The final FineWeb2 sample has many distinct hostnames, but concentration differs sharply by language. Examples of the largest single-host shares:

| Language | Largest hostname | Records | Share of FineWeb2 rows for that class |
|---|---|---:|---:|
| Maltese | `mt.airbnb.com` | 3,223 | 20.1% |
| Nynorsk | `nrk.no` | 1,807 | 9.0% |
| Irish | `tuairisc.ie` | 794 | 5.0% |
| Korean | `happycampus.com` | 651 | 3.3% |
| Latvian | `skaties.lv` | 495 | 3.1% |
| Lithuanian | `lrt.lt` | 476 | 3.0% |
| Estonian | `aripaev.ee` | 374 | 2.3% |

The number of distinct hostnames in these FineWeb2 class samples ranges from 714 (Maltese) to 7,927 (Chinese). The Maltese sample is particularly concentrated; the Nynorsk and Irish samples also have visible dependence on one major publisher. Hostname diversity alone does not establish domain or genre balance.

**Recommendation:** broaden the affected language samples across more shards/row groups and introduce a measured per-host cap (or at least a review threshold) before final selection. A cap should be applied before the final 20,000-row selection, with top-ups to avoid class shortfalls.

## 5. Privacy and text quality

The global merge excluded 11 email matches and 31 URL matches. The existing independent scan found no residual email addresses, URLs or valid IPv4 addresses. However, **1,619 records (0.253%) still carry privacy-review flags**:

- 1,006 phone-like occurrences;
- 676 occurrences of 9+ digit sequences;
- 63 records carry both flags.

The flags are not proof of personal data: long numbers include legal references, amounts and identifiers. Conversely, regex filtering is not proof that no personal data remain. Some sampled records visibly contain contact details, names, addresses, bank-account-like strings or web-page remnants. They require review; the text corpus is not PII-cleared.

Median text lengths are 99 characters for FineWeb2, 125 for DGT-TM and 47 for Tatoeba. DGT-TM's source documentation and its own manifest warn that the material consists of translation-memory segments: fragments, boilerplate, legal formulae and translationese are expected. Tatoeba's CC0 subset is user-contributed sentence material. FineWeb2 contains web text, including cookie notices, navigation/template material and occasional spam. None of these sources has yet had a human language-quality review at the selected-record level.

The artifact suffix `pii-clean` describes the email/URL/IP filtering pass only. It must not be interpreted as a claim of complete PII clearance.

## 6. Rights status

- **FineWeb2:** the ODC-By-1.0 dataset/compilation licence does not settle rights in the underlying crawled pages. This remains the largest rights blocker by volume (79.8% of the candidate).
- **DGT-TM 2021:** used under European Commission reuse conditions, with attribution and source identification. It is not CC0; retain the required attribution and release metadata.
- **Tatoeba:** text is from the separate CC0 1.0 export. The broader CC BY export was not ingested.

Technical deduplication, successful CI and a complete manifest do not constitute rights clearance.

## 7. Recommended order of work

1. Add the 94 cross-language exact-text collisions to a separate audit output and keep them out of supervised training pending resolution.
2. Improve FineWeb2 sampling for Maltese, Nynorsk and Irish first; check other classes for non-target-language boilerplate and domain/genre concentration.
3. Complete a reviewed privacy pass over the 1,619 flagged records, then sample the unflagged material as well.
4. Integrate the HF-hosted CC0-1.0 Common Voice 22 text source where it adds useful coverage, and Målfrid 2026. Croatian requires a separate independent source.
5. Resolve the DGT-TM 2025 catalogue/release discrepancy before replacing or supplementing the 2021 material.
6. Recompute source/domain balance and rights status before freezing a training corpus.

**Conclusion:** v4 is structurally sound as a 640,000-row technical candidate. It is not yet a balanced, human-validated, privacy-cleared or rights-cleared training corpus. The next bottleneck is sample quality and source balance, not model implementation.
