# MultiUN — multilingual United Nations document corpus

**Primary references**
- Original corpus paper: Eisele & Chen, *MultiUN: A Multilingual Corpus from United Nation Documents* (LREC 2010): https://aclanthology.org/L10-1473/
- Updated corpus paper: Chen & Eisele, *MultiUN v2: UN Documents with Multilingual Alignments* (LREC 2012): https://aclanthology.org/L12-1371/
- OPUS distribution and statistics: https://opus.nlpl.eu/datasets/MultiUN
- Original UN source catalogue: https://documents.un.org/
- UN ODS FAQ: https://documents.un.org/faq

## Creator and origin

Compiled by Andreas Eisele and Yu Chen from official United Nations documents retrieved from the UN Official Document System (ODS). The v1 paper describes crawling ODS documents from 2000 through 2011, retaining only the latest version when a document had multiple releases. The v2 paper reports more than 513,091 documents, including over 9% newly retrieved documents, and improved multilingual sentence alignment.

The source is the UN's official documentary record: General Assembly, Security Council, Economic and Social Council and subsidiary-body documents, reports and related official material. This is a distinct source from the UN Parallel Corpus (UNPC), even though both draw on UN material. Do not merge their inventory identities or assume identical document coverage, dates, processing, or licence provenance.

## Languages and language pairs

- The original v1 paper describes all six UN official languages: Arabic (ar), Chinese (zh), English (en), French (fr), Russian (ru), Spanish (es).
- The v2 paper reports those six languages plus a smaller German (de) component.
- OPUS currently catalogues 7 languages and 21 bilingual bitexts: all 21 possible pairs among the seven language labels. This does not mean every document exists in every language or every pair has equal coverage.
- The six official languages yield up to 15 language pairs per multilingual document when all six versions exist.

For langid-32, the direct target-language intersection is ar, zh, en, fr, ru, es and, on a smaller/less certain basis, de. It does not directly cover the other target languages.

## Upstream scale — do not confuse with project counts

Published scale indicators differ by release and unit:

| Reference | Reported scale | Unit / qualification |
|---|---:|---|
| MultiUN v1 paper | Around 300 million | Words per language, six official languages |
| MultiUN v2 paper | More than 513,091 | Documents |
| OPUS MultiUN v1 catalogue | 489,334 | Files |
| OPUS MultiUN v1 catalogue | 1.99 billion | Tokens |
| OPUS MultiUN v1 catalogue | 81.41 million | Sentence fragments |
| OPUS MultiUN v1 catalogue | 7 languages / 21 bitexts | Language and pair coverage |

These are corpus-wide published statistics, not verified per-language sentence counts for the exact downloadable revision. Do not add the units together or treat files, documents, tokens and sentence fragments as interchangeable. The inventory still needs exact downloadable file counts and sentence counts by language and pair, pinned to a specific release.

## Access methods and formats

- Original acquisition route: crawl/download from the UN Official Document System (ODS), https://documents.un.org/.
- ODS document links can be resolved by UN document symbol; the UN documentation system supports language-specific links.
- ODS contains born-digital full text from 1993 onward and scanned documents from 1946–1993, with availability in the six official languages and some German. MultiUN itself is a historical processed snapshot, not a live mirror of all current ODS content.
- Processed corpus distributions are available through OPUS: https://opus.nlpl.eu/datasets/MultiUN
- Original documents were Microsoft Word files. The MultiUN paper says the authors extracted plain text, removed footnotes, figures, graphics, tables, hyperlinks and other non-text material, split text into sentences, and generated multilingual sentence alignments.
- MultiUN v2 encodes sentence-alignment information together with text in XML. OPUS offers corpus packages/bitexts for language pairs. Confirm exact archive formats and release checksums when selecting a download.
- UN ODS provides document files and metadata; the current ODS collection includes PDF and Word or other born-digital/scanned document representations depending on record.

## Distribution terms and rights rationale

The MultiUN v2 paper explicitly states that the collected documents are in the public domain according to UN Administrative Instruction ST/AI/189/Add.9/Rev.2 (1987). It says the documents were collected from the UN ODS. The relevant UN policy covers official records and UN documents officially issued under a UN document symbol, subject to exceptions.

This is a documented source-specific public-domain rationale, not merely an inference from the Hugging Face wrapper's CC-BY-4.0 metadata. Preserve UN provenance and attribution. For rigorous clearance, retain document symbols and verify that sampled/selected records fall within the categories covered by the instruction and are not subject to an exceptional copyright decision or a separate third-party-rights notice. Do not infer that every item found anywhere on the ODS website, or every annex/embedded third-party item, is automatically public domain.

The UN ODS FAQ describes the system's scope and language access: https://documents.un.org/faq. The UN Parallel Corpus is separately described by DGACM as public-domain official records and parliamentary documents: https://www.un.org/dgacm/content/uncorpus.

## Relevance to langid-32

**Treat MultiUN as an independent source in its own right.** It is not just a component of the ymoslem Hugging Face Arabic-English filtered derivative. Its multilingual corpus and language-pair distribution make it relevant to all six official UN languages and the smaller German component.

It is a strong candidate for source-level acquisition and language coverage analysis. The current project inventory previously recorded zero selected records for the separate ymoslem/UN-Arabic-English-Filtered dataset; that is not evidence of zero MultiUN availability. Do not count the Hugging Face derivative's 19.3 million aligned Arabic-English rows as MultiUN's exact upstream count, because that derivative combines MultiUN and UNPC and applies additional filtering.

## Hugging Face mirror: exact pair-config example counts

The Helsinki-NLP Hugging Face dataset card separately reports `num_examples` for each of its 21 train configurations. The following counts are source-reported sentence-pair examples in that mirror, not unique monolingual sentence counts. Their sum is 159,488,597 pair rows; it must **not** be compared as if it were the same measure as OPUS's 81.41 million sentence fragments, nor added to it. Pair configurations share language sides and likely repeat the same source-side sentences across several alignments. This table is useful for locating the larger and smaller pair packages, but does not close the per-language unique-sentence inventory gap.

| Bitext | Pair examples |
|---|---:|
| ar–de | 165,090 |
| ar–en | 9,759,125 |
| ar–es | 10,119,379 |
| ar–fr | 9,929,567 |
| ar–ru | 10,206,243 |
| ar–zh | 9,832,293 |
| de–en | 162,981 |
| de–es | 162,078 |
| de–fr | 164,025 |
| de–ru | 164,792 |
| de–zh | 176,933 |
| en–es | 11,350,967 |
| en–fr | 13,172,019 |
| en–ru | 11,654,416 |
| en–zh | 9,564,315 |
| es–fr | 11,441,889 |
| es–ru | 10,605,056 |
| es–zh | 9,847,770 |
| fr–ru | 11,761,738 |
| fr–zh | 9,690,914 |
| ru–zh | 9,557,007 |

Source: https://huggingface.co/datasets/Helsinki-NLP/multiun (dataset card's per-configuration `num_examples`; mirror metadata is not a substitute for OPUS's original package manifest).

## Verified upstream availability (independent of project acquisition)

OPUS's current MultiUN v1 catalogue reports **489,334 files, 1.99 billion tokens and 81.41 million sentence fragments** across seven languages and 21 bitexts. These are corpus-wide aggregate figures, not per-language unique sentence counts. Pairwise configurations overlap, so summing rows across bitexts would multiply shared monolingual material. Exact per-language sentence counts require extracting language sides from the downloadable OPUS packages and deduplicating by sentence/document identity. Source: https://opus.nlpl.eu/datasets/MultiUN

## Current langid-32 project count

- Current staged/selected records attributed directly to this independent MultiUN source: **0** (not yet separately acquired or attributed).
- This zero is a project acquisition status only, not an upstream availability estimate.
- Rights status: **candidate / documented public-domain basis; preserve attribution and verify exceptions at record level**.
- No acquisition, candidate expansion, JQL scoring or selection has been performed as part of this inventory entry.

## Remaining inventory work

1. Pin the exact MultiUN release used (v1/v2 and OPUS package revision) and archive its metadata/checksums.
2. Obtain exact per-language and per-pair sentence-fragment counts from the downloadable manifests, rather than relying only on corpus-wide OPUS statistics.
3. Record native file formats, archive sizes, file counts, and document-symbol metadata.
4. Compare MultiUN and UNPC by document symbol to quantify overlap; do not double-count shared documents in any later combined source pool.
5. Retain the UN public-domain rationale and attribution requirements alongside source-level provenance.
