# FineWeb2 metadata inventory

FineWeb2 is a high-value Common Crawl derivative for this project. Its publisher reports language/script-specific document counts and Parquet sizes in the upstream [language distribution CSV](https://github.com/huggingface/fineweb-2/blob/d0defb24f193bb9a5a11b8b14524a03c4858e1b6/fineweb2-language-distribution.csv). The dataset card describes 96 Common Crawl snapshots (2013–April 2024), global per-language deduplication, language-specific filtering, and PII anonymization. The published data is ODC-By 1.0; this dataset licence does not by itself settle rights in every crawled source document.

**Important:** the distribution CSV is metadata, not an inventory of usable sentence samples. It reports document, word, byte and Parquet totals. The filtered `train` split is the candidate source. The small `test` split must not be mixed into training. The `_removed` subset contains material excluded by the FineWeb2 filtering pipeline; it is counted separately and should not be treated as clean training data without our own review. No Parquet shards or document text are downloaded by the inventory command.

## Target-language mapping

FineWeb2 uses ISO 639-3 language codes and language-script subset names. The project maps its 32 classes to exact subsets:

| Project | FineWeb2 subset | Notes |
|---|---|---|
| bg | `bul_Cyrl` | Bulgarian |
| hr | `hrv_Latn` | Croatian |
| cs | `ces_Latn` | Czech |
| da | `dan_Latn` | Danish |
| nl | `nld_Latn` | Dutch |
| en | — | FineWeb2 directs English users to original FineWeb |
| et | `ekk_Latn` | Standard Estonian (ISO 639-3 code `ekk`) |
| fi | `fin_Latn` | Finnish |
| fr | `fra_Latn` | French |
| de | `deu_Latn` | German |
| el | `ell_Grek` | Modern Greek |
| hu | `hun_Latn` | Hungarian |
| ga | `gle_Latn` | Irish |
| it | `ita_Latn` | Italian |
| lv | `lvs_Latn` | Standard Latvian (ISO 639-3 code `lvs`) |
| lt | `lit_Latn` | Lithuanian |
| mt | `mlt_Latn` | Maltese |
| pl | `pol_Latn` | Polish |
| pt | `por_Latn` | Portuguese |
| ro | `ron_Latn` | Romanian |
| sk | `slk_Latn` | Slovak |
| sl | `slv_Latn` | Slovenian |
| es | `spa_Latn` | Spanish |
| sv | `swe_Latn` | Swedish |
| nb | `nob_Latn` | Norwegian Bokmål |
| nn | `nno_Latn` | Norwegian Nynorsk |
| ru | `rus_Cyrl` | Russian |
| ja | `jpn_Jpan` | Japanese |
| zh | `cmn_Hani` | Mandarin Chinese |
| ko | `kor_Hang` | Korean |
| ar | `arb_Arab` | Standard Arabic |
| tr | `tur_Latn` | Turkish |

## Inventory command

The CLI downloads only the upstream CSV (roughly a few hundred KB), then writes one row per project language. It can also use a previously downloaded CSV for reproducibility/offline operation.

```sh
langid32-fineweb2-inventory \
  --output data/inventory/fineweb2-v2.1.1.csv

# Offline / pinned metadata snapshot:
langid32-fineweb2-inventory \
  --input-csv /path/to/fineweb2-language-distribution.csv \
  --output data/inventory/fineweb2-v2.1.1.csv
```

The report separates filtered train documents, test documents and removed train documents. A missing exact subset is reported as `not_listed`, not as proof that no such language exists anywhere in the underlying crawl. English is marked as a separate FineWeb route.

## Preliminary findings from the upstream distribution CSV

The pinned distribution snapshot (upstream commit `d0defb24f193bb9a5a11b8b14524a03c4858e1b6`, 2025-10-27) confirms large filtered subsets for Korean (`kor_Hang`: 60,874,355 train documents), Irish (`gle_Latn`: 646,842), Maltese (`mlt_Latn`: 489,190), Nynorsk (`nno_Latn`: 1,214,870) and Bokmål (`nob_Latn`: 38,144,343). These are publisher-reported document counts, not sentence counts or usable samples. The 31 target subsets range from 489,190 filtered-train documents for Maltese to hundreds of millions for several high-resource languages. The table has exact subsets for 31 of the 32 target classes in the current mapping; English is separately distributed in original FineWeb. The mapping deliberately uses `ekk` and `lvs` for Standard Estonian and Standard Latvian. Summing the 31 filtered-train rows in the pinned CSV gives **4,498,336,994 documents** and **8,565,676,448,996 Parquet bytes (about 8.57 TB)**. This is the combined source inventory, not a download target: the project needs 20,000 samples per class, so acquisition must be bounded and selective.

The filtered FineWeb2 corpus has already been globally deduplicated per language. The dataset retains `minhash_cluster_size`, source URL, crawl dump/date and language confidence metadata. For our evaluation, split by source document or domain before sentence extraction; do not randomly split extracted sentences. A FineWeb2-held-out evaluation is also not independent of other Common Crawl derivatives such as HPLT or MADLAD-400.

## Source and licence cautions

- FineWeb2: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2
- Language distribution: https://github.com/huggingface/fineweb-2/blob/d0defb24f193bb9a5a11b8b14524a03c4858e1b6/fineweb2-language-distribution.csv
- Pipeline and per-language configurations: https://github.com/huggingface/fineweb-2
- FineWeb2 dataset card declares ODC-By 1.0. Record that as the dataset/compilation licence; it does not establish that all underlying crawled pages are individually licensed for unrestricted redistribution.
- The dataset card says the pipeline anonymizes email addresses and IP addresses and provides an opt-out route; this is not a guarantee that all forms of personal data have been removed. Our own source review and text-level checks remain necessary.

## Document schema and provenance

The dataset viewer exposes these fields: `text`, `id`, `dump`, `url`, `date`, `file_path`, `language`, `language_score`, `language_script`, `minhash_cluster_size`, and `top_langs`. The card describes `id` as the original unique Common Crawl sample identifier. The `dump` and `date` fields identify the crawl snapshot/time; `url` gives the source page; `language_score` and `language_script` expose the GlotLID classification; and `minhash_cluster_size` records the pre-deduplication duplicate-cluster size.

There is no ready-made domain field: derive the hostname from `url`, canonicalize it, and retain the original URL separately. For split assignment, domain-level grouping is a conservative default to reduce website/template leakage; preserve document ID as a second-level stable group key. Do not use the raw URL as a public training feature or publish it in the text-only sample output unless the source review explicitly allows it.

FineWeb2's reported PII work specifically mentions email and IP-address anonymization. Treat that as a useful upstream filter, not a substitute for our own review of names, contact details, addresses, account identifiers, and other identifying text.

## Parquet shard inventory and bounded access

The second inventory command queries the Hugging Face dataset-viewer `/parquet` endpoint and records only file URLs, subset/split labels and byte sizes. It does not download Parquet contents.

```sh
langid32-fineweb2-shards \
  --output data/inventory/fineweb2-shards.csv

# Or process a previously saved response:
langid32-fineweb2-shards \
  --input-json data/inventory/fineweb2-parquet-api.json \
  --output data/inventory/fineweb2-shards.csv
```

The command keeps filtered, test and `_removed` shard roles separate. The API can report pending or failed conversions; check these fields before treating the manifest as complete.

A useful warning about acquisition scale: the Hugging Face file browser shows the Korean `kor_Hang/train` split as 25 Parquet files, mostly around 4.84 GB each, with smaller final shards; the directory is about 106 GB. Downloading whole shards is therefore not an acceptable default for this project. The next technical step is to prototype remote Parquet range reads against one shard and measure actual transferred bytes.

DuckDB's `httpfs` extension supports HTTP(S) Parquet partial reads using metadata and HTTP range requests ([DuckDB documentation](https://duckdb.org/docs/current/core_extensions/httpfs/https)). Hugging Face also documents direct `hf://` dataset access through DuckDB ([Hugging Face support](https://duckdb.org/docs/current/core_extensions/httpfs/hugging_face)). This is a promising low-dependency alternative to installing the full `datasets`/Datatrove stack, but must be tested against FineWeb2's Xet-backed files before we rely on it. No extraction or training data has been downloaded yet.


## First user-run inventory: findings (2026-11-16)

The two uploaded reports have been inspected. The metadata CSV contains 32 project rows: 31 FineWeb2 language subsets plus the separate English route. All 31 non-English rows are marked available.

The Parquet shard CSV contains **1,839 files**:
- **1,810 filtered train shards**, totalling **7,793,275,841,600 bytes** (about 7.79 TB);
- **29 filtered test shards**, totalling **1,638,147,059 bytes**;
- no `_removed` shards in the supplied listing;
- one test shard for each of the 29 languages represented.

The shard listing covers 29 languages. It has no entries for English (expected: separate FineWeb), **Spanish** (`spa_Latn`) or **Turkish** (`tur_Latn`). The metadata CSV expects 637,611,323,581 bytes of Spanish train shards and 134,789,283,815 bytes of Turkish train shards. Their combined **772,400,607,396-byte** gap exactly explains the difference between the metadata CSV's 8,565,676,448,996-byte aggregate and the shard listing's 7,793,275,841,600-byte filtered-train aggregate. For the 29 languages present, the shard byte totals match the metadata CSV exactly.

This is a **dataset-viewer conversion coverage gap**, not evidence that the Spanish and Turkish source data do not exist. The regenerated report includes the raw `/parquet` API response. It contains 4,569 Parquet entries across 1,314 configurations, 556 failed configuration conversions, zero pending conversions, and `partial: false`. Both missing target subsets are explicitly present in `failed` as `kind: config-parquet` (`spa_Latn` and `tur_Latn`); neither appears in `parquet_files`. They are therefore not omitted `partial-train` entries. The 29 other target subsets are present, and their train-shard byte totals match the distribution CSV exactly.

Hugging Face's dataset card documents the original data layout under `data/{subset}/train` and gives direct access examples using `hf://datasets/HuggingFaceFW/fineweb-2/data/por_Latn/train`. That means the failed dataset-viewer conversion should not be treated as source-data absence. The next route is to inspect the original `main` branch files for `data/spa_Latn/train` and `data/tur_Latn/train`, then access those original Parquet shards directly (for example via the Hub's `hf://` interface or direct file URLs), rather than relying on `refs/convert/parquet`. The dataset card also notes that streaming is supported and no smaller sample release is currently provided. [Dataset card](https://huggingface.co/datasets/HuggingFaceFW/fineweb-2) · [dataset-viewer Parquet API documentation](https://huggingface.co/docs/dataset-viewer/parquet).

The shard sizes are mostly around 4.84 GB, with smaller final shards. This supports the earlier conclusion: do not download whole language subsets. The immediate next step is to inventory original-branch shard paths and test a bounded remote read.

### Consistency checks

- For all 29 languages represented, summed filtered-train shard bytes equal the metadata CSV exactly.
- No duplicate URLs or duplicate (language, role, split, filename) entries occur in the supplied CSV.
- The uploaded shard manifest contains only the filtered train/test roles; it does not include the `_removed` datasets.
- The manifest URLs use Hugging Face's `refs/convert/parquet` revision. These are converted Parquet references, not a pinned immutable dataset commit; retain the original API JSON and retrieval date for reproducibility.

### Remote query feasibility

The uploaded listing confirms that shard URLs are direct Hugging Face Parquet URLs. DuckDB's `httpfs` supports HTTP range requests for Parquet and can fetch only the metadata and column data needed by a query; Hugging Face also documents the `hf://` route for querying datasets directly. This is a credible path to test, but actual transferred bytes and compatibility with these FineWeb2 converted shards remain unmeasured. Sources: [DuckDB HTTP partial reads](https://duckdb.org/docs/current/core_extensions/httpfs/https), [Hugging Face DuckDB integration](https://huggingface.co/docs/hub/en/datasets-duckdb).


### Raw Parquet API response (2026-11-16)

The second user upload supplied the raw Hugging Face `/parquet` JSON as well as the regenerated CSV. This resolves the earlier uncertainty:

- API response: 4,569 listed Parquet files, 1,314 configurations, 556 failed configuration conversions, zero pending conversions, `partial: false`.
- Both target subsets missing from the converted-shard manifest are in `failed` as `config-parquet`: `spa_Latn` and `tur_Latn`.
- Neither target is represented by a `partial-train` or `partial-test` split.
- The regenerated target CSV still has 1,839 rows (1,810 train and 29 test); this is expected because the API did not publish converted Parquet files for those two configs.
- The other 29 target subsets have converted shards, with train-byte sums matching the pinned distribution CSV exactly.

This changes the diagnosis: the issue is specifically the dataset-viewer Parquet conversion for two configs, not a bug in our split-name handling. The upstream dataset card documents original files below `data/{subset}/train` and demonstrates direct `hf://` streaming. We should inspect the original `main`-branch file trees for `spa_Latn` and `tur_Latn`; a conversion failure is not proof that the underlying data are unavailable. The original files may have a different schema or layout, so inspect metadata before using them.


### Historical revisions: Spanish and Turkish recovered (2026-11-16)

A metadata-only inventory was run from GitHub Actions against the Hugging Face Hub tree API. It inspected the train and test folders for spa_Latn and tur_Latn in v2.0.0, v2.0.1, v2.1.0, v2.1.1, and main. It enumerated file paths, sizes and object identifiers; **no Parquet data was downloaded**.

The result confirms that the Spanish and Turkish source shards exist in historical revisions:

| Revision | Spanish train files | Spanish bytes | Turkish train files | Turkish bytes |
|---|---:|---:|---:|---:|
| v2.0.0 | 136 | 594,934,740,560 | 28 | 125,243,448,949 |
| v2.0.1 | 137 | 597,493,126,238 | 28 | 126,286,680,890 |
| v2.1.0 | 146 | 637,611,323,581 | 30 | 134,789,283,815 |
| main | 146 | 637,611,323,581 | 30 | 134,789,283,815 |

Each of these revisions also has one test Parquet file per language. Exact file counts and byte totals, including test splits, are in [fineweb2-historical-revision-summary.csv](data/fineweb2-historical-revision-summary.csv).

The v2.1.0 totals match the current distribution CSV and the previously observed expected train-byte totals exactly. main has the same counts and byte totals for these two subsets. The literal v2.1.1 revision name returned HTTP 404 for the queried paths; current main is the usable latest snapshot, and its dataset card changelog identifies it as v2.1.1. We should therefore pin **v2.1.0 or main** for acquisition, not rely on the literal v2.1.1 revision name.

**Conclusion:** the original FineWeb2 data are present; the failure is confined to the dataset-viewer /parquet conversion representation. We can bypass that conversion layer and use the original Parquet files from the Hub tree. The dataset card's hf:// examples are compatible with revision pinning; for reproducibility, use v2.1.0 explicitly (or record the resolved commit SHA if using main). This still does not justify downloading whole shards: next we should test bounded HTTP-range/column reads against a single original shard and verify actual bytes transferred.

The inventory utility and its workflow are retained:
- [scripts/inspect_fineweb2_revisions.py](../scripts/inspect_fineweb2_revisions.py)
- [.github/workflows/fineweb2-revisions.yml](../.github/workflows/fineweb2-revisions.yml)


### Original Parquet access tested successfully (2026-11-16)

A second GitHub Actions probe used DuckDB's HTTPFS against the original v2.1.0 files, not the dataset-viewer conversion URLs. Before invoking DuckDB, the script sent a 1 KiB HTTP Range request and required an HTTP 206 response. Both files returned the expected Parquet magic bytes (PAR1) and advertised byte ranges:

| Language | First shard | Remote file size | Range preflight | DuckDB schema + LIMIT 1 |
|---|---|---:|---|---|
| Spanish | spa_Latn/train/000_00000.parquet | 4,846,280,144 bytes | 206, 1,024 bytes | successful |
| Turkish | tur_Latn/train/000_00000.parquet | 4,845,225,746 bytes | 206, 1,024 bytes | successful |

DuckDB read the Parquet schema and returned the lengths of one text field and its ID for each language; document text itself was not written to the report. The schema matches the expected FineWeb2 fields: text, id, dump, url, date, file_path, language, language_score, language_script, minhash_cluster_size, and top_langs.

This confirms the key technical route: **we can query original Spanish and Turkish Parquet files remotely with DuckDB without downloading entire shards**. The HTTP Range preflight proves the Hub/Xet delivery path supports byte ranges, and DuckDB's schema and row query both succeeded. The probe did not yet measure total bytes transferred by DuckDB, so we should still quantify that before scaling up.

Probe summary: [fineweb2-remote-read-probe.csv](data/fineweb2-remote-read-probe.csv). Reproducible probe: [scripts/probe_fineweb2_remote_read.py](../scripts/probe_fineweb2_remote_read.py), workflow: [.github/workflows/fineweb2-remote-read.yml](../.github/workflows/fineweb2-remote-read.yml).


### Bounded sentence extraction pilot: Spanish and Turkish (2026-11-16)

The first end-to-end extraction run has now produced **20,000 unique sentence samples per language**, using only four selected Parquet row groups per language. The sample text is not committed to the repository; it is available as a short-lived private GitHub Actions artifact (7-day retention): [run 43920993618](https://github.com/SylvainSouche/langid-32/actions/runs/43920993618). The workflow and extractor are [fineweb2-extract.yml](../.github/workflows/fineweb2-extract.yml) and [extract_fineweb2_sample.py](../scripts/extract_fineweb2_sample.py).

| Metric | Spanish | Turkish |
|---|---:|---:|
| Source documents read | 4,000 | 4,000 |
| Distinct hostnames in those documents | 3,532 | 2,476 |
| Candidate sentences after quality filters and document cap | 46,894 | 47,129 |
| Selected train / validation / test | 16,000 / 2,000 / 2,000 | 16,000 / 2,000 / 2,000 |
| Distinct hostname groups in selected train | 2,696 | 1,879 |
| Median sentence length | 137 chars | 103 chars |
| 95th percentile sentence length | 315 chars | 260 chars |
| HTTP GET bytes transferred (metadata + selected columns) | 19,776,882 | 13,975,100 |
| Transfer as percentage of selected Parquet shard size | 0.4081% | 0.4582% |

The selected shards were `data/spa_Latn/train/000_00032.parquet` (4,846,060,914 bytes) and `data/tur_Latn/train/004_00003.parquet` (3,049,909,820 bytes). Each selected four row groups of 1,000 documents. The extraction read only the required columns and those row groups; it did not download either whole Parquet file. Total recorded HTTP GET payload was **33,751,982 bytes** for 40,000 selected sentences.

The extractor now records per-sentence provenance without retaining full source URLs in the text corpus: hashed document ID, hashed hostname group, hostname, URL hash, crawl date/dump, language score/script, MinHash cluster size, shard path and object identifiers, and row-group number. The hostname-derived group hash is independent of language, so the same hostname is assigned to the same split across languages. The selected Spanish and Turkish samples had five shared hostname group hashes; all five were assigned to the same split in both languages.

Selection filters include NFC/whitespace normalization, document language score >= 0.90, matching language/script labels, 25–400 character sentences, script proportion, minimum token count for space-delimited scripts, sentence-ending checks, exact sentence deduplication, a 20-sentence-per-document cap, and exclusion of email addresses, URLs and IPv4 addresses. Phone-like strings and long numeric sequences are retained with per-sentence provenance review flags rather than automatically excluded: the FineWeb2 card itself notes that phone-number regexes have high false-positive rates. The manifest records rejection counts for these filters.

**Interpretation and caveats:** these are 20,000 *heuristically accepted* samples per class, not human-reviewed ground truth. The four row groups are a deterministic bounded sample, not a statistically representative sample of the entire language subset. The 10% test and 10% validation sets are split from the sampled upstream **train** documents by hostname; FineWeb2's own upstream `test` split was not used. The hostname grouping is not a full registrable-domain/public-suffix calculation, and the PII filters cannot guarantee anonymization. FineWeb2's ODC-By 1.0 dataset licence does not settle rights in each crawled page. Keep the artifact private pending manual quality, privacy and rights review.

Compact metrics: [fineweb2-es-tr-pilot-summary.csv](data/fineweb2-es-tr-pilot-summary.csv). The extractor has been extended to run all 31 non-English target subsets in a separate workflow; English remains a separate FineWeb source route.


### Full 31-language FineWeb2 bounded extraction (2026-11-16)

The all-subset run has completed successfully with extractor v0.3.0. It extracted **20,000 unique samples for every one of the 31 non-English target classes**: 620,000 sentences total, with no language errors and no split shortfalls.

**Result: 31 / 31 languages reached target.**

| Result | Value |
|---|---:|
| Languages | 31 |
| Samples per language | 20,000 |
| Total samples | 620,000 |
| Per-language train / validation / test | 16,000 / 2,000 / 2,000 |
| Source documents read | 8,000 per language (248,000 total) |
| Row groups read | 8 per language |
| Total HTTP GET payload | 727,899,605 bytes (~728 MB) |
| Compressed GitHub Actions artifact | ~204 MB |
| Language shortfalls / extraction errors | 0 / 0 |

The run used DuckDB v2.0.0 and pinned FineWeb2 revision `v2.1.0`. It selected one deterministic shard per language and eight evenly distributed row groups within that shard. It projected only the required columns. The highest transfer-to-shard ratio was 4.10% (Japanese, whose selected shard was relatively small); most languages were below 1%. No whole Parquet shard was downloaded.

Validation of the generated artifact confirmed:
- exactly 20,000 rows and 20,000 unique normalized texts in each language;
- exactly 16,000 train, 2,000 validation and 2,000 test rows per language;
- 620,000 provenance rows, each with all expected provenance fields;
- 1,191 hostname-group hashes shared between two or more language samples, with **zero cross-language split conflicts**;
- 52 exact sentence hashes shared across different language classes (kept rather than silently removed, since they can be useful ambiguous/hard-negative cases).

The all-language sample and full manifest/provenance sidecar are in the private GitHub Actions artifact: [run 43923113272](https://github.com/SylvainSouche/langid-32/actions/runs/43923113272). It has 7-day retention; the sample text has not been committed to Git. Per-language counts, selected shards, row groups, host counts, sentence lengths, transfer totals and selected privacy flags are in [fineweb2-31-language-sample-summary.csv](data/fineweb2-31-language-sample-summary.csv). Score distributions, punctuation ratios and filter/PII-flag counts are in [fineweb2-31-language-quality-summary.csv](data/fineweb2-31-language-quality-summary.csv).

**This is a first bounded corpus build, not final ground truth.** It samples eight row groups from one shard per language; the deterministic selection is not statistically representative of each entire subset. The text-level filters are heuristics, not human review or a complete PII detector. Email, URL and IPv4 patterns are excluded; phone-like and long numeric sequences are retained with per-sentence review flags. The v0.3 run contains 6,918 selected sentences with at least one such flag; the candidate pool had 61,592 phone-like and 3,768 long-number flags. This follows the FineWeb2 card's warning that phone-number regexes have high false-positive rates. Hostname grouping is not a public-suffix/registrable-domain calculation. The FineWeb2 ODC-By 1.0 licence applies to the dataset/compilation, but underlying crawled-page rights remain a separate question. Keep the artifact private until quality, privacy and rights review is complete. The earlier two-language pilot above used v0.2; this 31-language run uses v0.3 and retains phone-like/long-number matches with review flags. The sample's 10% validation and 10% test splits are made from upstream train documents; upstream FineWeb2 test and removed subsets are not mixed into this sample.

English is still the 32nd class and is not part of FineWeb2; the dataset card directs English users to the separate original FineWeb dataset. The other project sources (Common Voice, DGT-TM, Tatoeba, etc.) also remain relevant; this 31-language FineWeb2 build is one source component, not the merged final corpus.

### Bounded 31-language extraction completed (2026-11-16)

The original v2.1.0 Parquet shards were sampled remotely through DuckDB HTTP range reads. The first pass used 4 shards × 1 row group (1,000 documents) per selected shard for all 31 non-English target subsets. **27/31 languages reached the full 20,000-sentence target** (16,000 train / 2,000 validation / 2,000 test).

The four shortfalls were:
- Croatian: 10,612 / 1,185 / 1,420
- Irish: 7,702 / 1,188 / 716
- Maltese: 7,749 / 1,895 / 1,527
- Nynorsk: 10,603 / 718 / 805

These were not source absence: FineWeb2 has only 1 train shard for Irish, Maltese and Nynorsk, while Croatian has 4; the first pass simply sampled too few row groups.

A deterministic top-up then used 3 row groups per available shard for those four languages. All four reached the full 20,000 target:
- Croatian: 16,000 / 2,000 / 2,000
- Irish: 16,000 / 2,000 / 2,000
- Maltese: 16,000 / 2,000 / 2,000
- Nynorsk: 16,000 / 2,000 / 2,000

The 31-language base artifact contains 640,000 selected sentences before replacement of those four language partitions; the top-up artifact supplies their complete replacements. Both artifacts include manifest.json, split JSONL and provenance sidecars. No corpus text has been committed to Git.

The 31-language extraction transferred about 1.32 GB of compressed HTTP ranges for metadata + selected row groups. The resulting artifact is about 190 MB compressed. This is orders of magnitude below downloading the underlying multi-terabyte corpus.

Selection remains deliberately conservative: 25–400 characters, FineWeb2 language score >=0.90, script check, exact normalized sentence deduplication within the sampled material, hostname-level split grouping shared across languages, email/URL/IPv4 exclusion, and phone-like/long-number review flags. The manifest explicitly records that this is a bounded deterministic sample, not a statistically representative sample of the full FineWeb2 subsets.

Next: assemble the base and top-up artifacts into one canonical 640,000-sentence corpus artifact, then run the existing langid32.corpus normalization/deduplication and provenance checks before treating it as the first corpus candidate.
