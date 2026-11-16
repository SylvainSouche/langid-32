# English FineWeb source inventory

Extraction date: 2026-11-16. Source: [HuggingFaceFW/fineweb](https://huggingface.co/datasets/HuggingFaceFW/fineweb), the English Common Crawl corpus. The dataset card describes more than 18.5 trillion tokens of cleaned English web data, built from Common Crawl snapshots, with ODC-By 1.0 as the dataset/compilation licence. That licence does not resolve rights in each underlying crawled page. See the [official dataset card](https://huggingface.co/datasets/HuggingFaceFW/fineweb).

## Bounded extraction

The extractor reads selected Parquet row groups remotely through DuckDB HTTP range requests. It does not download whole shards and does not commit corpus text to Git.

- GitHub Actions run: [43946321575](https://github.com/SylvainSouche/langid-32/actions/runs/43946321575)
- Artifact: `fineweb-en-20000-main`, 14-day retention; artifact ID `14265621126`
- FineWeb source revision recorded by the run: `main`
- 24 selected Parquet shards, from 24 distinct Common Crawl dumps
- 4 selected row groups per shard
- 95,979 source documents read
- 61,715 distinct hostnames in the scanned documents
- 1,098,372 sentence candidates after sentence-level filters and document cap
- 20,000 selected English sentences: 16,000 train / 2,000 validation / 2,000 test

The selection is deterministic for the source file listing and seed, but it is a bounded sample, not a statistically representative census of FineWeb. Per-shard object identifiers are retained in the provenance sidecar; the source revision field is the branch name rather than a commit pin.

## Selected-sample audit

| Metric | Result |
|---|---:|
| Unique normalized sentences | 20,000 |
| Distinct selected hostnames | 15,705 |
| Distinct Common Crawl dumps | 24 |
| Largest hostname contribution | 21 sentences (0.105%) |
| Median sentence length | 108 characters |
| 95th percentile sentence length | 253 characters |
| Maximum sentence length | 399 characters |
| Minimum selected FineWeb language score | 0.90005 |
| Median selected language score | 0.95428 |
| Email / URL / IPv4 matches remaining | 0 / 0 / 0 |
| Phone-like review flags | 19 |
| 9+ digit-sequence review flags | 5 |

The hostname distribution is notably diffuse: the largest host contributes only 21 of the 20,000 selected records. The 24 selected shards span 24 crawl dumps, rather than one crawl snapshot. This does not establish genre balance or sentence-level ground truth.

Filters include NFC/whitespace normalization, 25–400 character bounds, FineWeb language score >= 0.90, English-language label, minimum alphabetic content and five-word minimum, sentence-ending check, exact sentence deduplication, a 20-sentence-per-document cap, and exclusion of email, URL and IPv4 matches. Phone-like and long numeric sequences are retained for review rather than automatically discarded.

## Integration in candidate v5

The FineWeb source was staged into the common source-neutral schema and merged with FineWeb2, DGT-TM 2021 and Tatoeba CC0. The resulting 32-language candidate is documented in [candidate-audit-v5.md](candidate-audit-v5.md).

FineWeb contributes 6,075 records to the final 640,000-record candidate (all English). The final English class is 30.4% FineWeb, 61.9% Tatoeba CC0 and 7.7% DGT-TM 2021. The merge uses the available source pools without fixed source quotas; the English candidate pools were 20,000 FineWeb, 41,230 Tatoeba and 5,000 DGT-TM records. This is a material improvement over the v4 English class, which contained no web-crawl source, but English remains more Tatoeba-heavy than most other classes.

## Rights and privacy

- FineWeb is labelled ODC-By 1.0 at dataset/compilation level. Common Crawl source terms and the rights in individual pages remain separate questions.
- The sample excludes email, URL and IPv4 regex matches, but this is not complete PII clearance.
- Phone-like and long-number matches are review flags, not proof of personal data.
- Keep the artifact private pending source-specific rights review, manual privacy review and language-quality review.
