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

This is a **manifest coverage gap**, not evidence that the Spanish and Turkish data do not exist. The Hugging Face dataset-viewer documentation says conversions can be partial and that large splits may be listed under names such as `partial-train`; the original shard CLI accepted only `train` and `test`. It has now been corrected to normalize `partial-train` / `partial-test` while preserving the original API split in `api_split`, and to report target languages without any shard entries. See the [dataset-viewer Parquet API documentation](https://huggingface.co/docs/dataset-viewer/parquet).

The shard sizes are mostly around 4.84 GB, with smaller final shards. This supports the earlier conclusion: do not download whole language subsets. The next step is to regenerate the manifest with the corrected CLI and see whether Spanish and Turkish appear as partial splits. If still absent, inspect the API's `pending`, `failed` and `partial` fields from the raw JSON response.

### Consistency checks

- For all 29 languages represented, summed filtered-train shard bytes equal the metadata CSV exactly.
- No duplicate URLs or duplicate (language, role, split, filename) entries occur in the supplied CSV.
- The uploaded shard manifest contains only the filtered train/test roles; it does not include the `_removed` datasets.
- The manifest URLs use Hugging Face's `refs/convert/parquet` revision. These are converted Parquet references, not a pinned immutable dataset commit; retain the original API JSON and retrieval date for reproducibility.

### Remote query feasibility

The uploaded listing confirms that shard URLs are direct Hugging Face Parquet URLs. DuckDB's `httpfs` supports HTTP range requests for Parquet and can fetch only the metadata and column data needed by a query; Hugging Face also documents the `hf://` route for querying datasets directly. This is a credible path to test, but actual transferred bytes and compatibility with these FineWeb2 converted shards remain unmeasured. Sources: [DuckDB HTTP partial reads](https://duckdb.org/docs/current/core_extensions/httpfs/https), [Hugging Face DuckDB integration](https://huggingface.co/docs/hub/en/datasets-duckdb).
