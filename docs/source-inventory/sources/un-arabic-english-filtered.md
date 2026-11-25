# UN Arabic–English Filtered (Hugging Face derivative)

**Primary source:** https://huggingface.co/datasets/ymoslem/UN-Arabic-English-Filtered

## Identity and contents

This is a separate Hugging Face derivative combining **MultiUN + the UN Parallel Corpus (UNPC)**. Its dataset card describes rule-based and semantic filtering (train threshold >0.45; test/dev >0.9) and fastText language detection (>=0.1). The Hugging Face dataset viewer reports two string columns, text_en and text_ar.

Published dataset structure:
- Train: 19,279,407 aligned rows
- Test: 8,752 aligned rows
- Dev: 8,752 aligned rows
- Total: 19,296,911 aligned Arabic-English pairs
- Train Parquet: 19 shards, approximately 5.2 GB; test and dev each have one Parquet file.

A single Parquet shard can therefore contain around one million aligned rows. These are paired translation examples, not one million independent monolingual sentences in each language.

## Relationship to the upstream sources

Do not treat this derivative as the source identity for either upstream corpus:
- **MultiUN** is an independent multilingual UN-document corpus, covering the six UN official languages and a smaller German component. It has its own inventory entry: [MultiUN](multiun.md).
- **UN Parallel Corpus (UNPC)** is a separate UN-produced corpus of official records and parliamentary documents, distributed in up to six official languages with sentence alignments: https://www.un.org/dgacm/content/uncorpus.

The 19,296,911 rows are the filtered derivative's total. They are not the exact upstream MultiUN count, the exact UNPC count, or a count of unique sentences across both sources. There may be overlap between the upstream corpora.

## Rights and distribution

The dataset card declares CC-BY-4.0. That label applies to the Hugging Face repository's declared distribution terms; it should not replace the upstream rights analysis. The MultiUN paper explicitly cites UN Administrative Instruction ST/AI/189/Add.9/Rev.2 as the basis for public-domain status of the collected UN documents. UNPC is separately described by DGACM as public-domain official records and parliamentary documents. Keep provenance and UN attribution, and verify source composition and any exceptional/third-party material before treating the derivative as cleared.

## Current langid-32 project status

- Previously recorded project-selected records: **0**.
- This is not an upstream availability count and must not be used to infer that MultiUN or UNPC has no available data.
- Do not automatically ingest the combined derivative as a substitute for separately inventorying and acquiring MultiUN and UNPC.
- The derivative may be useful as a convenient filtered Arabic-English aligned dataset, but assess it separately and avoid double-counting its content against the upstream sources.
