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
| et | `ekk_Latn` | Check published availability |
| fi | `fin_Latn` | Finnish |
| fr | `fra_Latn` | French |
| de | `deu_Latn` | German |
| el | `ell_Grek` | Modern Greek |
| hu | `hun_Latn` | Hungarian |
| ga | `gle_Latn` | Irish |
| it | `ita_Latn` | Italian |
| lv | `lvs_Latn` | Check published availability |
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

The pinned distribution snapshot (upstream commit `d0defb24f193bb9a5a11b8b14524a03c4858e1b6`, 2025-10-27) confirms large filtered subsets for Korean (`kor_Hang`: 60,874,355 train documents), Irish (`gle_Latn`: 646,842), Maltese (`mlt_Latn`: 489,190), Nynorsk (`nno_Latn`: 1,214,870) and Bokmål (`nob_Latn`: 38,144,343). These are publisher-reported document counts, not sentence counts or usable samples. The 29 target subsets range from 489,190 filtered-train documents for Maltese to hundreds of millions for several high-resource languages. The table has exact subsets for 31 of the 32 target classes in the current mapping; English is separately distributed in original FineWeb. The mapping deliberately uses `ekk` and `lvs` for Standard Estonian and Standard Latvian.

The filtered FineWeb2 corpus has already been globally deduplicated per language. The dataset retains `minhash_cluster_size`, source URL, crawl dump/date and language confidence metadata. For our evaluation, split by source document or domain before sentence extraction; do not randomly split extracted sentences. A FineWeb2-held-out evaluation is also not independent of other Common Crawl derivatives such as HPLT or MADLAD-400.

## Source and licence cautions

- FineWeb2: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2
- Language distribution: https://github.com/huggingface/fineweb-2/blob/main/fineweb2-language-distribution.csv
- Pipeline and per-language configurations: https://github.com/huggingface/fineweb-2
- FineWeb2 dataset card declares ODC-By 1.0. Record that as the dataset/compilation licence; it does not establish that all underlying crawled pages are individually licensed for unrestricted redistribution.
- The dataset card describes PII anonymization and provides an opt-out route. Our own source review and text-level checks remain necessary.
