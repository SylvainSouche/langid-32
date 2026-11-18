> **Historical audit of v5.** This is a frozen analysis of the 16 November 2026 artifact, not the current corpus inventory or acquisition plan. See [the canonical source register](source-register.md) for current source status.

# Independent audit: four-source candidate v5

Audit date: 2026-11-16. Input: private GitHub Actions artifact `multisource-candidate-v5-fineweb-en`, produced by [run 43948367359](https://github.com/SylvainSouche/langid-32/actions/runs/43948367359). The archive was downloaded and its JSONL contents inspected locally. No corpus text was committed to Git.

## 1. Structural checks

| Check | Result |
|---|---:|
| Languages | 32 |
| Records | 640,000 |
| Train / validation / test | 512,000 / 64,000 / 64,000 |
| Per language | 16,000 / 2,000 / 2,000 |
| Output groups | 186,323 |
| Candidate groups before per-language cap | 256,900 |
| Conflicting splits for `group_id` | 0 |
| Conflicting splits for `split_group_id` | 0 |
| Exact normalized duplicates within a language | 0 |
| Public split and internal-record SHA-256 checks | all passed |
| Residual email / URL / valid IPv4 matches | 0 / 0 / 0 |

The four-source merge completed successfully and the artifact contains the text-only split files, internal `records.jsonl` provenance sidecar, and one manifest per source. The sidecar remains private.

## 2. Overall source composition

| Source | Final records | Share | Coverage |
|---|---:|---:|---|
| FineWeb2 v2.1.0 | 510,702 | 79.80% | 31 classes |
| DGT-TM 2021 | 91,539 | 14.30% | 24 EU official languages |
| Tatoeba CC0, 2026-11-14 | 31,791 | 4.97% | 17 classes represented |
| FineWeb (English) | 5,968 | 0.93% | English only |
| **Total** | **640,000** | **100%** | **32 classes** |

The 31 non-English class source counts are unchanged from v4. The FineWeb integration affects the English class only.

## 3. English source mix

| Source | Available staged candidates | Final English records | Final share |
|---|---:|---:|---:|
| FineWeb | 20,000 | 5,968 | 29.84% |
| Tatoeba CC0 | 41,230 | 12,486 | 62.43% |
| DGT-TM 2021 | 5,000 | 1,546 | 7.73% |
| **Total** | **66,230** | **20,000** | **100%** |

The merge applies no fixed source quota. It normalizes and deduplicates the available source pools, assigns deterministic group-level splits, then selects the final per-language cap. The final source mix is therefore close to the relative sizes of the available English pools. FineWeb reduces Tatoeba's share from 89.0% in v4 to 62.4% in v5 and adds a web-crawl component at 29.8%. English is still more Tatoeba-heavy than most other classes, whose principal source is FineWeb2. Source/register balance remains a real evaluation confound and should be measured explicitly.

## 4. FineWeb sample quality and domain spread

The English FineWeb input is documented separately in [fineweb-inventory.md](fineweb-inventory.md). Its bounded extraction read 95,979 documents from 24 selected shards spanning 24 Common Crawl dumps and 61,715 hostnames. The selected 20,000 sentences came from 15,705 hostnames; the largest hostname contributed 21 sentences (0.105%). Median sentence length was 108 characters, the 95th percentile 253, and the minimum retained FineWeb language score 0.90005.

This is much less concentrated by hostname than the most concentrated FineWeb2 classes in v4. It does not establish genre balance or human-verified English labels. The extractor's source revision is pinned to FineWeb v1.4.0 commit `9bb295ddab0e05d785b879661af7260fed5140fc`; per-shard object identifiers are retained in the private provenance sidecar.

## 5. Cross-language label collisions

The same **94 distinct exact text strings (194 records)** occur under more than one language label, as in v4. They include proper names, scientific names, multilingual headings, legal fragments and source boilerplate. The FineWeb English addition did not increase this collision count in the final candidate.

A text string present under multiple language labels has no uniquely inferable language label. Keep these strings out of ordinary supervised training unless individually resolved; retain them in a separate ambiguity/label-conflict evaluation set.

## 6. Privacy and text quality

The global merge excluded 11 email matches and 31 URL matches. An independent scan found no residual email addresses, URLs or valid IPv4 addresses. **1,623 records (0.254%) carry privacy-review flags**:

- 1,010 phone-like occurrences;
- 676 occurrences of 9+ digit sequences;
- 63 records carry both flags.

These are review flags, not proof of personal data. Long numbers include legal references, amounts and identifiers; phone-like patterns have false positives. Conversely, regex filtering is not proof that no personal data remain. The text corpus is not PII-cleared and the selected records have not had a human language-quality review.

## 7. Rights status

- **FineWeb2:** ODC-By-1.0 dataset/compilation licence; underlying crawled-page rights remain unresolved.
- **FineWeb:** ODC-By-1.0 dataset/compilation licence; underlying Common Crawl page rights remain separate.
- **DGT-TM 2021:** European Commission reuse conditions, with attribution and source identification; not CC0.
- **Tatoeba:** separate CC0 1.0 sentence export.

Technical deduplication, successful CI and a complete manifest do not constitute rights clearance.

## 8. Conclusion and next work

v5 is structurally sound as a 640,000-record four-source technical candidate. Adding FineWeb improves the English class materially: 29.8% of its records are now web-crawl sentences rather than the previous 0%. However, English remains 62.4% Tatoeba because the staged Tatoeba pool is more than twice the FineWeb pool. The corpus is still not a balanced, human-validated, privacy-cleared or rights-cleared training set.

Next priorities remain: quarantine the 94 label collisions; review flagged and sampled unflagged text; measure register/source confounds across classes; use the HF-hosted CC0-1.0 Common Voice 22 text source where appropriate; find an independent Croatian source; integrate Målfrid 2026; and resolve the DGT-TM release/catalogue question before freezing a training corpus.
