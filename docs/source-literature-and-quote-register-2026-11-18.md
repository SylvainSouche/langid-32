# Source literature, quotations and constituent-level rights audit — 18 November 2026

This is a focused review of the publisher documentation and associated literature for sources already staged or technically sampled. It is not a legal opinion or a release clearance. The quotations below are short evidence excerpts from source papers or official source documentation; they are **not** proposed corpus content and do not replace licence attribution.

## 1. TeMU-BSC Catalan CC0 sentences — constituent review

Repository: https://github.com/TeMU-BSC/catalan_CC0_sentences  
Acquisition code: `scripts/acquire_waiting_sources.py`, source group `catalan`  
Measured evidence: waiting-source run [44241908630](https://github.com/SylvainSouche/langid-32/actions/runs/44241908630), artifact 14403758073.

The current script selects exactly these 12 files. Counts below are the measured sampled candidates in the run manifest, not the source files' total sizes.

| Selected constituent file | Candidates | README's stated origin / rights evidence |
|---|---:|---|
| `catalan_government_crawling_frases_seleccionades_filtrades.txt` | 49,864 | 93,691 sentences selected from the Catalan Government Crawl; README says both package and content are CC0 and links the Generalitat legal notice. |
| `datasets_sentences.tsv` | 49,979 | Extracted from caBreu, CoQCat, NLUCat and Parafraseja; README says the Language Technologies Unit waived rights under CC0 for Mozilla publication. |
| `edited_generated_selected_chatbot.txt` | 1,134 | Generated from the edited chatbot set; README says TeMU-BSC applies a CC0 waiver. |
| `edited_selected_chatbot.txt` | 437 | Selected chatbot sentences; README says TeMU-BSC applies a CC0 waiver. |
| `frases_spl.txt` | 696 | Sentences created by the Catalan Government's Secretaria de Política Lingüística; README points to `SPL_CC0_waiver.pdf`. |
| `generades_spl_seleccionades.txt` | 1,733 | Generated from the SPL set; README says BSC CC0 waiver. |
| `literatura.txt` | 287 | README labels these literary sentences CC0, but does not identify the works or explain the rights chain in the short file description. Keep this constituent on hold until the underlying waiver/source evidence is inspected. |
| `more_intents.txt` | 50,000 | Generated intent-like sentences; README says BSC CC0 waiver. Sample cap reached. |
| `plantilles_intents.txt` | 2,124 | Template-generated intent-like sentences; README says BSC CC0 waiver. |
| `sentences_from_xitxat_corpus.txt` | 2,230 | XitXat sentences written by the team; README says BSC CC0 waiver. |
| `sentences_from_xitxat_corpus2.txt` | 721 | Further XitXat sentences; README says BSC CC0 waiver. |
| `wikidata_sentences.txt` | 18,521 | Template-generated sentences using Wikidata; README says BSC CC0 waiver. |
| **Total** | **177,726** | |

This is a file-level rights inventory, not a sentence-by-sentence rights determination. The candidate rows currently identify a file and line/row index; they do not retain an original article title, author, publication date or URL. The source code also applies a generic repository-claim licence label to every TeMU constituent. That label is too coarse for final attribution.

The README describes additional files which the current script does **not** select, including Marius Serra's literary works (the README says they were extracted with the author's permission), Joan Pujolar's work, Catalan newswire material, translated Spanish Wikipedia sentences, and other files/aggregates. Do not imply that those materials contributed to the 177,726 candidates. The current selection does not include the Marius Serra or Pujolar files, the newswire file, or the translated-Wikipedia file.

Short source description quoted from the repository README: “collected CC0 sentences written in Catalan”. That headline is not a substitute for checking the constituent-level statements and agreements listed above.

**Decision:** retain the 177,726 rows as technical candidates only. Before changing their rights status, inspect the actual SPL waiver PDF, the Projecte Aina contribution agreement/image, the Enciclopèdia Catalana contribution agreement, and the provenance of the 287 literary sentences. Then split source metadata by constituent rather than retaining one generic TeMU licence claim.

## 2. GreynirCorpus — important acquisition-scope correction

Official project repository: https://github.com/icelandic-lt/GreynirCorpus  
CLARIN-IS record: https://repository.clarin.is/repository/xmlui/handle/20.500.12537/119  
Acquired archive SHA-256: `417d7e37cf63f01844760239675a5d15e3627c5ea0dcb3461005bcaf656c06a5` (1,658,164 bytes), from waiting-source run 44241908630.

The previous source summary overstated what was acquired. The CLARIN archive lists `testset/txt` and `devset/txt` files, but the nominal full-size `psd/copper` and `psd/silver` compressed data are only 134-byte Git-LFS pointer stubs in this archive. The acquisition script scans ordinary text/JSON/CSV files and does not retrieve Git-LFS objects or read the compressed `.gz` corpus payloads. Therefore the 4,930 candidates came from the parser's small gold-standard test/development material, not from a representative sample of the 10-million-sentence treebank.

The project README describes the full treebank as “10 million parsed sentences” and says the text was extracted from news and government sites during 2015–2021. It identifies Miðeind ehf. as the publisher to credit under CC BY 4.0. The README's English description says the gold standard contains 5,000 manually corrected sentences split into 500 test and 4,500 development sentences; the Icelandic description later says 2,610 gold-standard sentences while repeating the 500/4,500 split. Treat that as a README inconsistency and rely on the explicit `testset` and `devset` directories and their file counts, not the conflicting 2,610 summary figure. The CLARIN deposit also labels the archive CC BY 4.0.

The practical issue is not simply article-level attribution: the current candidate pipeline has no original source article URL/title/author/date for these parser test/development sentences. The source file and line are insufficient to reconstruct the news or government work from which a sentence originated.

**Decision:** do not count the 4,930 rows as a broad Greynir corpus contribution. Exclude them from the main language corpus pending a separate, deliberate acquisition of the full copper/silver data, confirmation of Git-LFS retrieval, and a provenance/rights assessment. If the gold/dev set is ever used for a separate evaluation task, keep it isolated from training and preserve its exact parser-test/dev designation.

## 3. IGC2024 Filtered-1 — the open CC BY portion, not the full IGC

CLARIN-IS record: https://repository.clarin.is/repository/xmlui/handle/20.500.12537/381  
README: https://repository.clarin.is/repository/xmlui/bitstream/handle/20.500.12537/381/README.txt?isAllowed=y&sequence=3  
2026 paper: Daðason & Steingrímsson, “Optimized for AI: Curating the Icelandic Gigaword Corpus for Stable LLM Training,” CMLC-12 (2026), pp. 49–56. https://doi.org/10.63317/3uatbht8mdrf

The CLARIN item identifies the authors Jón Friðrik Daðason, Steinþór Steingrímsson and Hinrik Hafsteinsson; issue date 30 March 2026; publisher The Árni Magnússon Institute for Icelandic Studies; and CC BY 4.0. It reports 794,816,184 words. Its README describes the archive as a JSONL version prepared for language-model training and explicitly calls its contents “CC-BY-licensed documents from the IGC.” The README requests citation of the 2018 IGC paper and the 2026 curation paper.

The 2026 paper resolves the licensing split that was previously ambiguous. It says “Approximately 63% of the corpus is available under a permissive license, CC BY 4.0” and that “The remaining 37% falls under the IGC Custom License.” It then quantifies the filtered distribution: the CC BY 4.0 open-access portion is approximately 795M running words and is published in CLARIN-IS and Hugging Face; the custom-license portion is approximately 895M words and is not for raw-text republication. The paper says the custom licence permits research use and language-model training but “prohibits republication of raw texts.” The CLARIN Filtered-1 record's 794.8M-word size matches the paper's ≈795M open portion. Filtered-1 is therefore the CC BY 4.0 subset; Filtered-2 is the custom-licensed subset and remains excluded.

The paper also explains that books, journals and social-media material are distributed as shuffled paragraphs or sentences for licensing/copyright reasons and are unsuitable for the pre-training JSONL release. Do not mix those restricted fragments into the Filtered-1 open-text path.

The JSONL schema example contains:
- tei_archive: the source TEI archive;
- tei_path: the path to the original TEI document;
- source: the original source/site;
- altered: whether the document was changed by processing;
- text: the processed document text.

The paper says “the inclusion of tei_path ensures full traceability to the original TEI-XML source.” This is precisely the provenance we need to retain. The previous acquisition parser did not preserve tei_archive, tei_path, source or altered; the current parser must be amended to retain all four. A 50,000-row sample from the historical artifact lacks those fields and is not sufficient for record-level attribution. The new same-run acquisition must preserve them before the source is used in a release build.

The 2026 paper also describes a quality pipeline: rule-based document filtering, boilerplate removal, normalization, removal of documents under 50 words, stop-word ratio thresholding, internal-duplication checks, code/encoding/OCR/phrase filters, and MinHash/LSH fuzzy deduplication. These are corpus quality operations; they do not replace the CC BY attribution obligation.

Required scholarly references:
- Jón Friðrik Daðason and Steinþór Steingrímsson. 2026. “Optimized for AI: Curating the Icelandic Gigaword Corpus for Stable LLM Training.” Proceedings of the 12th Workshop on Challenges in the Management of Large Corpora, pp. 49–56. DOI: https://doi.org/10.63317/3uatbht8mdrf.
- Starkaður Barkarson, Steinþór Steingrímsson and Hildur Hafsteinsdóttir. 2022. “Evolving Large Text Corpora: Four Versions of the Icelandic Gigaword Corpus.” LREC 2022, pp. 2371–2381.
- Steinþór Steingrímsson, Sigrún Helgadóttir, Eiríkur Rögnvaldsson, Starkaður Barkarson and Jón Guðnason. 2018. “Risamálheild: A Very Large Icelandic Text Corpus.” LREC 2018, pp. 4361–4366.

**Decision:** upgrade IGC2024 Filtered-1 from a narrow legal hold to **STAGED / CC BY 4.0 OPEN PORTION; ATTRIBUTION AND PROVENANCE REQUIRED**. Include only Filtered-1, preserve tei_archive/tei_path/source/altered for each record, and include the dataset and original IGC scholarly citations. Filtered-2 remains excluded because raw-text republication is prohibited under its custom licence.

## 4. Målfrid 2026 — authoritative technical metadata

Official technical PDF: https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026.pdf  
Permanent resource record: https://hdl.handle.net/21.11146/107  
Catalogue record: https://data.norge.no/en/datasets/b3da2524-c7c6-30c9-b757-d813f228c76f/malfrid-2026-freely-available-documents-from-norwegian-state-institutions

The National Library of Norway's documentation says the focused crawl covered 720 state-institution domains from December 2025 to January 2026, respecting robots.txt and politeness restrictions. The published schema is unusually useful for record-level provenance: `doc_id`, `doc_hash`, `domain`, `url`, `date`, `mimetype`, `title` (HTML only), `lang` and paragraph-array `fulltext`. The technical document reports 1,890,232,881 Bokmål tokens and 170,231,965 Nynorsk tokens. It states NLOD 2.0.

The source documentation notes that language identification “is never perfect”, particularly for similar languages and noisy web data. That supports retaining a language-validation stage rather than treating the publisher's language field as ground truth.

No scholarly paper specifically describing the 2026 release was identified in this review. Cite the permanent resource record and National Library technical documentation unless the publisher supplies a preferred paper citation.

**Decision:** this source has sufficient document-level metadata to support traceability better than the current TeMU and Greynir text-only files. The remaining review is NLOD/database-rights interpretation, third-party material, privacy, and exact required attribution—not missing source URLs by design.

## 5. BSC-LT Legal Catalan-Spanish Parallel Corpus

Dataset card: https://huggingface.co/datasets/BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus  
Point of contact in card: ai_institute_mt@bsc.es.

The card states that the corpus combines three granularities and that the source material comes from DOGC, Catalan public-administration documents and APDCAT. It identifies DOGC as CC0/open data, the public-administration material as under the Generalitat's open-information licence, and APDCAT content as obtained under a Data Sharing Agreement. The APDCAT file has document IDs and paired URLs; the DOGC and legal paragraph files have different schemas.

The card's summary says the texts are “authentic parallel text” from public institutions. This is useful evidence of origin and authenticity, not a standalone rights grant for every constituent. In particular, the APDCAT agreement must be checked for downstream redistribution by third parties, and the acquisition pipeline must preserve source document identity for all three files.

The 50,414 candidate count in the waiting-source manifest consists of 50,000 DOGC and 414 APDCAT segments. The paragraph-level file contributed no rows because the generic TSV scanner reads the first field (`dataset`) rather than the Catalan text field (`ca_text`). The first rows of that file show the schema `dataset`, `segment_id`, `ca_text`, `es_text`, `alignment_score`. The historical scanner also dropped APDCAT's `url_ca` and `url_es` fields even though the README documents them. The parser has now been corrected to preserve both URLs and to select the `ca_text` column from the paragraph TSV; the next same-run acquisition will verify the corrected row count. Do not describe all three subcorpora as represented in the candidate sample.

**Decision:** keep all BSC-LT candidates on hold pending a PII screen; keep APDCAT additionally on hold pending review of the actual Data Sharing Agreement. DOGC and the paragraph corpus have stronger CC0/equivalent-to-CC0 upstream routes, but the BSC curated corpus itself declares CC BY 4.0. Fix the paragraph TSV parser and retain APDCAT URLs before any re-acquisition. The card's warning that personal and sensitive information may be present is a material privacy issue, not a generic caveat.

## 6. Verified scholarly references and short quotation evidence for other staged sources

| Source | Associated publication / official documentation | Short quotation and use |
|---|---|---|
| Common Voice | Ardila et al. (2020), “Common Voice: A Massively-Multilingual Speech Corpus,” LREC 2020. https://aclanthology.org/2020.lrec-1.520/ | The abstract says Common Voice “can be useful in other domains (e.g. language identification).” This supports relevance to the task, not text redistribution rights. |
| DGT-TM | Steinberger, Eisele, Klocek, Pilos and Schlüter (2012), “DGT-TM: A freely available Translation Memory in 22 languages,” LREC 2012, pp. 454–459. https://aclanthology.org/L12-1481/ | The paper describes a translation memory as “sentences and their professionally produced translations.” This is a resource description, not a rights statement. |
| Leipzig Corpora Collection | Eckart and Quasthoff (2013), “Statistical Corpus and Language Comparison on Comparable Corpora,” pp. 151–165. DOI: https://doi.org/10.1007/978-3-642-20128-8_8 | Cite as the corpus-family scholarly reference. The API/underlying-work rights issue is documented separately in the Leipzig audit. |
| Tatoeba | Official “Using the Tatoeba Corpus for Your Own Projects” and “How to contribute under CC0” pages. https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus ; https://en.wiki.tatoeba.org/articles/show/cc0-contributions | The CC0 page says CC0 is currently usable only on “original sentences”; translations inherit compatible rights from the original. This supports keeping the CC0 export separate from the general CC BY 2.0 FR export. |
| GreynirCorpus | CLARIN-IS deposit and project README; no separate scholarly paper identified in this review. | Cite the named authors/deposit and Miðeind ehf. attribution. The 4,930 rows are only from the small test/development sets. |
| Målfrid 2026 | National Library of Norway technical documentation and permanent resource record; no scholarly paper identified for the 2026 release in this review. | Cite the official documentation and resource record; preserve the document metadata fields listed above. |
| TeMU-BSC and BSC-LT | Repository README and dataset card; no dedicated scholarly paper identified in this review. | Cite the exact constituent/repository and source publishers. The repository/dataset citation does not replace source-specific waivers or APDCAT agreement review. |
| Catalan-DPO-V2 | Hugging Face dataset card. https://huggingface.co/datasets/catallama/Catalan-DPO-V2 | The card describes a mixture of “synthetically generated data and public preferences datasets.” This is provenance evidence; Apache-2.0 card metadata does not clear third-party dialogue text. |
| UN Arabic-English Filtered | Hugging Face dataset card. https://huggingface.co/datasets/ymoslem/UN-Arabic-English-Filtered | No upstream legal grant was confirmed in this review. Cite the derivative card only as the provenance lead, not as proof of UN rights. |

## 7. Work still required before any rights-status promotion

1. Inspect the three TeMU agreement/waiver files and identify exactly which selected files they cover; resolve the 287 literary sentences; retain per-constituent licence IDs and evidence references.
2. Exclude the current Greynir test/development sample from the main language corpus. If the full corpus is pursued, retrieve the Git-LFS objects and verify that the source/document provenance is preserved.
3. Confirm the exact redistribution scope for IGC2024 Filtered-1 and inspect the actual JSONL record schema for document metadata.
4. Read the APDCAT Data Sharing Agreement and exact Generalitat notices; keep DOGC, legal paragraphs and APDCAT as separate rights constituents.
5. Inspect Målfrid's NLOD 2.0 and database-rights implications against the actual release format; test how many records retain usable titles/URLs and whether the full paragraph-to-document mapping survives.
6. Keep scholarly citations, exact legal notices and per-record source attribution as separate fields in the final source manifest.

No source is made release-eligible by this audit alone.


## 7. UN Arabic-English Filtered — upstream rights independently verified

Derivative dataset card: https://huggingface.co/datasets/ymoslem/UN-Arabic-English-Filtered  
Official UN Parallel Corpus terms: https://www.un.org/dgacm/en/content/uncorpus  
Official UNPC paper: https://www.un.org/dgacm/sites/www.un.org.dgacm/files/files/UNCORPUS/un.pdf  
MultiUN v1 paper: https://aclanthology.org/L10-1473/  
MultiUN v2 paper: https://aclanthology.org/L12-1371/

The derivative Hugging Face card explicitly says the dataset combines **MultiUN + UNPC**, applies rule-based and semantic filtering plus FastText language detection, and declares CC BY 4.0. Its current schema has only two fields, `text_en` and `text_ar`; the splits are 19,279,407 train rows and 8,752 each for test and dev. The 50,000 Arabic candidates in langid-32 were sampled from the train split.

The upstream rights position is materially better than the previous card-only assessment:

- The official UNPC v1.0 paper states that the corpus is composed of official UN records and other parliamentary documents “in the public domain.” Its integral disclaimer says no other restrictions apply, but users must acknowledge the UN as the source and cite the 2016 paper by Ziemski, Junczys-Dowmunt and Pouliquen.
- The official UNPC terms repeat the mandatory acknowledgement and citation. This is a corpus-level acknowledgement, not a requirement to reproduce the text of each source document.
- The MultiUN v2 paper states: “The documents we collected are in public domain” and ties this to UN Administrative Instruction ST/AI/189/Add.9/Rev.2. It describes ODS documents collected from 2000–2011 and says the XML corpus retains original file IDs, language, publication dates and document symbols.
- The MultiUN v1 paper describes the source as official UN documents. OPUS's MultiUN page recommends citing both Eisele & Chen (2010) and Tiedemann (2012); the derivative card also includes the Chen & Eisele (2012) v2 paper and the Ziemski et al. (2016) UNPC paper.

This confirms the public-domain status of the two named upstream corpus families at the corpus level. It does **not** restore source-document metadata removed by the derivative. The HF derivative schema does not expose the original UN symbol, translation job number, file ID, publication date or URL. The current acquisition code therefore falls back to the row index in the derivative split. That value must be recorded as `dataset_row_index`, never as an original `source_document_id` or article identifier.

The official UNPC paper says the corpus is “composed of official records and other parliamentary documents of the United Nations that are in the public domain.” The MultiUN v2 paper says its collected documents “are in public domain”. These are source-rights statements from the associated papers, not independent guarantees for any additional content that a downstream derivative might have introduced. The derivative card names only MultiUN and UNPC; pin the exact HF revision and retain its CC BY 4.0 attribution.

Required notices/citations for any retained material from this derivative:
1. Credit the derivative dataset creator/repository `ymoslem/UN-Arabic-English-Filtered` under its declared CC BY 4.0 licence, with a licence link and changes noted.
2. Acknowledge the United Nations as the source of the underlying corpus and include the UNPC reference: Ziemski, Michał; Marcin Junczys-Dowmunt; Bruno Pouliquen (2016), “The United Nations Parallel Corpus”, LREC 2016.
3. Include the MultiUN references: Eisele & Chen (2010), “MultiUN: A Multilingual Corpus from United Nation Documents”; Chen & Eisele (2012), “MultiUN v2: UN Documents with Multilingual Alignments”. Include Tiedemann (2012), “Parallel Data, Tools and Interfaces in OPUS”, where the OPUS-distributed MultiUN copy is the acquisition route.
4. Preserve the immutable HF revision, split name and row index. State explicitly that original UN document-level identifiers were not included in the derivative schema.

**Decision:** the underlying UNPC and MultiUN text is supported by official public-domain statements; the derivative has a declared CC BY 4.0 licence and a mandatory UN acknowledgement. The remaining hold is attribution packaging, immutable revision capture and accurate provenance labelling—not an unverified assumption that UN documents are copyrighted. A future re-acquisition directly from UNPC/MultiUN could restore original document IDs and substantially improve traceability.


## 8. Korean Wikipedia 2023-11-01 — the HF licence metadata is stale/incomplete

Hugging Face dataset: https://huggingface.co/datasets/wikimedia/wikipedia  
Korean config: `20231101.ko`  
Wikimedia Foundation Terms of Use: https://foundation.wikimedia.org/wiki/Terms_of_Use  
Wikimedia announcement of the 4.0 transition: https://diff.wikimedia.org/2023/06/29/stepping-into-the-future-wikimedia-projects-transition-to-creative-commons-4-0-license/  
Creative Commons announcement: https://certificate.creativecommons.org/2023/06/29/wikipedia-moves-to-cc-4-0-licenses/

The Hugging Face card declares CC BY-SA 3.0 and GFDL, but that statement is stale for a 2023-11-01 snapshot. Wikimedia's Terms of Use revision took effect on 29 June 2023: new text contributions are licensed under CC BY-SA 4.0 and GFDL (unversioned); earlier contributions remain under CC BY-SA 3.0 and GFDL. The Foundation's announcement explicitly says that older edits remain under BY-SA 3.0 while new edits use 4.0. Imported text can have its own compatible licence and additional attribution requirements; the Terms of Use say imported content cannot be GFDL-only and must be appropriately credited.

The relevant official statement is that new text is licensed under “Creative Commons Attribution-ShareAlike 4.0 International License”. This is not a simple wholesale upgrade of all old article text: the snapshot contains revisions spanning both licence periods. The HF dataset card's CC BY-SA 3.0/GFDL labels do not capture the complete 2023-11-01 rights position. The historical waiting-source artifact 442419 used the inaccurate label `CC-BY-SA-4.0;GFDL-1.3` for every row. The current acquisition code now records a mixed CC BY-SA 3.0 / 4.0 range and unversioned GFDL, but it still lacks revision IDs/timestamps and cannot identify imported-content exceptions; the old artifact remains historical and on hold.

The upstream `wikimedia/wikipedia` dataset description says each example is a cleaned full article. Its schema has four columns, and the acquisition code retains page ID, title and URL but not the revision ID or revision timestamp. This means:
- Page ID identifies the article, not the precise revision included in the 2023-11-01 snapshot.
- Article URL/title provide a useful attribution pointer, but the exact author/contributor history and any page-specific imported-content notices are not frozen in the candidate row.
- The script iterates no more than the first 500,000 page rows, while the HF structure reports about 647.9K rows for `20231101.ko`; the 50,000-candidate sample is therefore not drawn from the entire config.
- Paragraph splitting produces multiple candidate rows per article and correctly reuses the page ID as a grouping key, but it does not recover revision-level metadata.

No separate scholarly paper is specified by the Wikimedia dump card; the publisher directs users to cite the Wikimedia Dumps resource. For licensing, the controlling evidence is the Wikimedia Foundation Terms of Use and the dump's own legal information, not a generic citation paper.

**Decision:** keep the Korean Wikipedia candidates on hold. Before promotion, either rebuild from the original XML dump while preserving revision IDs/timestamps and page history, or establish that the exact HF conversion contains sufficient metadata to reconstruct each page revision. Then classify pre-/post-29 June 2023 content and imported material, implement article-level attribution, and choose a ShareAlike-compatible distribution licence. Do not rely on the current HF card's CC BY-SA 3.0/GFDL metadata or the sampler's single CC BY-SA 4.0 label.


## 9. Catalan-DPO-V2 — quarantine due mixed-language labelling and provenance loss

Derivative dataset: https://huggingface.co/datasets/catallama/Catalan-DPO-V2  
Source card: https://huggingface.co/datasets/catallama/Catalan-DPO-V2  
Upstream Orca pairs: https://huggingface.co/datasets/argilla/distilabel-intel-orca-dpo-pairs  
Upstream Capybara preferences: https://huggingface.co/datasets/argilla/Capybara-Preferences-Filtered  
Original Capybara: https://huggingface.co/datasets/LDJnr/Capybara  
Intel Orca DPO pairs: https://huggingface.co/datasets/Intel/orca_dpo_pairs  
Orca paper: https://arxiv.org/abs/2306.02707

The DPO V2 README reports 23,503 preference rows and says the mixture is:
- 9.5K preferences sampled from `argilla/distilabel-intel-orca-dpo-pairs`, with half translated into Catalan;
- 7.2K preferences sampled from `argilla/Capybara-Preferences-Filtered`;
- 6.8K preferences generated synthetically by CataLlama v0.2 Instruct SFT and scored by ArmoRM-Llama3-8B-v0.1.

The DPO V2 card explicitly reports **40% Catalan and 60% English**. Its schema contains only `messages`, `chosen` and `rejected`; it does not preserve the original upstream `source` field or a language label. The acquisition script selected assistant messages and `chosen`, but called `add("ca", ...)` for every item without language identification. The previous waiting-source artifact therefore contains 30,790 rows falsely labelled Catalan: 20,772 `chosen` rows and 10,018 assistant-message rows. Manual inspection of the actual candidate file found plainly English text among these rows. The rows are quarantined and must not enter any training merge or count toward the Catalan target.

The upstream licence chain is not resolved by the DPO V2 Apache-2.0 card:
- Argilla's Orca pairs card declares Apache-2.0 and says it is a distilabeled derivative of `Intel/orca_dpo_pairs`, itself based on Open-Orca/Orca-style data. The source paper, Mukherjee et al. (2023), “Orca: Progressive Learning from Complex Explanation Traces of GPT-4,” describes GPT-4 explanation traces and synthetic training data. It is relevant research context, not a blanket rights grant for every text in the derivative.
- Argilla's Capybara Preferences card says it is built on `LDJnr/Capybara`, with synthetic conversations and alternative responses generated by GPT-4 and several open models. The filtered derivative card declares Apache-2.0, but the original Capybara README says most tokens are newly synthesized while seed instructions come from a number of third-party datasets. Its cited “Amplify-Instruct” paper is a placeholder with `arXiv:(coming soon)`; no actual paper identifier was found.
- The 6.8K DPO V2 synthetic preferences were generated using `catallama/CataLlama-v0.2-Instruct-SFT` and scored with `RLHFlow/ArmoRM-Llama3-8B-v0.1`. Both model cards declare the Meta Llama 3 licence, not Apache-2.0. Meta's Llama 3 Community License §1(b)(v) restricts use of Llama Materials or their outputs/results to improve another large language model. Whether a small language-identification classifier falls within “another large language model” is not assumed either way; obtain a specific legal assessment before relying on these generated rows. The model licence does not automatically become the text licence, but the derivative Apache card does not resolve all model-output and upstream-text issues.
- The DPO V2 row schema has no per-row source-component label. The acquisition fallback row index is not an upstream document ID and cannot recover which source dataset or seed work supplied a particular passage.

Short quotation from the original Capybara README: “Most tokens contained in this dataset are newly synthesized and did not exist prior online.” This is the creator's description of its generation process, not a rights clearance. The associated Orca paper describes the model as learning from “rich signals from GPT-4 including explanation traces”; this is research context, not a licence grant.

**Decision:** the 30,790 rows from the old waiting-source artifact are quarantined and excluded from all Catalan totals. The acquisition workflow now deliberately skips DPO V2. Active source-dataset exclusion rules enforce this for both `chosen` and `messages`. A third active rule excludes all 4,930 Greynir rows from the main corpus because they are parser gold/development samples, not representative corpus text. The previous artifact's 613,860 rows therefore reduce to 578,140 non-DPO, non-Greynir technical candidates; this does not make the remaining rows release-cleared.


## 10. Common Voice 22.0 — CC0 and the later MDC no-mirroring terms are separate

Third-party conversion: https://huggingface.co/datasets/fsicoli/common_voice_22_0  
Mozilla Common Voice terms (effective 31 October 2025): https://commonvoice.mozilla.org/en/terms  
Common Voice 22.0 release announcement (25 June 2025): https://discourse.mozilla.org/t/common-voice-22-0-release/144358  
Official CV dataset metadata repository: https://github.com/common-voice/cv-dataset  
Associated paper: Ardila et al. (2020), “Common Voice: A Massively-Multilingual Speech Corpus,” LREC 2020, pp. 4211–4215. https://aclanthology.org/2020.lrec-1.520/

The third-party Hugging Face repository describes itself as “an unofficial version” downloaded and converted from the Common Voice website. It declares CC0-1.0. HF metadata records creation on 27 June 2025 and last update 11 August 2025. The Mozilla Common Voice 22.0 release announcement is dated 25 June 2025. Thus this conversion predates the new Common Voice terms effective 31 October 2025.

The current Mozilla terms continue to make contributions available under CC0, but separately state that Common Voice datasets are made available “exclusively through MDC” and ask users not to “post, distribute, or mirror any Common Voice dataset, in whole or in part, on other platforms or services.” The legal distinction matters:
- CC0 addresses copyright and related rights in contributions.
- The Common Voice Terms of Use contain a separate access/stewardship restriction concerning distribution and mirroring.
- The HF conversion was created before that change and is a third-party copy downloaded from the public Common Voice website, not an MDC download. The terms' retroactive application to this already-published copy, and their contractual effect on downstream users who did not accept them, are not established by the source card.
- Publishing selected text-only excerpts in another dataset may still be characterised as redistributing part of a Common Voice dataset; do not assume that using text rather than audio avoids the wording.

The associated Ardila et al. paper describes Common Voice as a “massively-multilingual speech corpus” and notes its usefulness for “language identification”. That is task-relevance evidence, not a rights grant. The paper's citation should accompany the source attribution, but it does not replace the CC0 dedication or the current Mozilla terms.

The 27.0 Romanian MDC terms acceptance previously recorded for this project is specific to Romanian and prohibits re-hosting/re-sharing; it must not be generalized to CV22 or other CV27 locales. The Croatian CV27 sample has no recorded locale-specific acceptance. CV22's current text-only sample retains locale, upstream sentence ID, exact HF conversion revision and per-locale TSV hashes, but this provenance does not resolve the contractual question.

**Decision:** keep the 259,352 CV22 rows on hold and do not publish them while the pre-/post-31 October 2025 terms question is unresolved. Do not delete or conflate the CC0 claim; record it separately from the no-mirroring term and obtain a specific legal determination. Keep CV27 locale acceptances separate.


## 11. Målfrid 2026 — NLOD, database compatibility, personal data and document language

Official technical PDF: https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026.pdf  
Permanent resource record: https://hdl.handle.net/21.11146/107  
NLOD 2.0 full text: https://data.norge.no/nlod/en/2.0

The National Library of Norway's two-page technical document states that the corpus was collected from 720 state-institution domains during December 2025–January 2026, respecting robots.txt and politeness restrictions. It provides separate Bokmål and Nynorsk tarballs but also reports English and three Sami languages in the overall crawl. The published JSONL schema is strong for provenance: `doc_id`, `doc_hash`, `domain`, `url`, `date`, `mimetype`, `title` (HTML only), `lang`, and `fulltext` as paragraph strings.

The technical document cautions that language identification “is never perfect”, especially for similar languages and noisy web data. This matters directly for Bokmål/Nynorsk: the current acquisition code assigns `nb` or `nn` from the tarball name. The parser now retains the document-level `lang` and `mimetype` fields, but per-document validation is still pending before every paragraph is treated as the corresponding language.

NLOD 2.0 grants broad rights to copy, use, modify and distribute, with attribution and change notices. Its §5 says that, if the licensor has not supplied a custom attribution, the normal wording is: “Contains data under the Norwegian licence for Open Government data (NLOD) distributed by [name of licensor]”. The source documentation does not specify a custom attribution, so use National Library of Norway as licensor and include the NLOD 2.0 link and original document URL where practical.

The database-rights nuance must be stated accurately:
- Målfrid's publisher says the corpus is under NLOD 2.0.
- NLOD §9 lists ODC-By 1.0 as a compatible licence for parts that constitute databases. It does not automatically relicense the source database as ODC-By; it identifies a compatible route for distributing an adapted/combined work involving database-protected material.
- NLOD §3 excludes personal data unless there is a legitimate basis for disclosure/further processing, and excludes third-party material the licensor is not authorised to license. A government-domain crawl does not by itself prove that every embedded third-party work is covered.

No scholarly paper specifically describing the 2026 release was identified. The official PDF and permanent resource record are the primary citation sources.

**Decision:** preserve the existing NLOD/database-rights hold and extend it to per-document language validation and personal/third-party content review. The current 50K-per-language samples are technical candidates only until the `lang` field is retained and mismatches are filtered, and until a privacy/third-party screening process is applied.


## 12. DGT-TM 2021 — exact EC reuse conditions and the 2012 reference paper

Official JRC resource and terms: https://joint-research-centre.ec.europa.eu/language-technology-resources/dgt-translation-memory_en  
Reference paper: Steinberger et al. (2012), “DGT-TM: A freely available Translation Memory in 22 languages,” LREC 2012, pp. 454–459. https://aclanthology.org/L12-1481/  
Later overview: Steinberger et al. (2014), “An overview of the European Union's highly multilingual parallel corpora,” Language Resources and Evaluation 48, pp. 679–707. DOI: https://doi.org/10.1007/s10579-014-9277-0

The official JRC page distinguishes DGT-TM from full-text parallel corpora: DGT-TM is a translation memory of aligned translation units extracted from EURAMIS, the Directorate-General for Translation's shared translation memory. It contains most, but not all, Acquis documents and also some other documents. The 2021 release is distributed in five volumes labelled `Vol_2020_1` through `Vol_2020_5`; therefore “2021” is the release year, while the volume labels refer to 2020. The current JRC page describes 24 EU official languages. The 2012 reference paper's title and abstract describe the earlier 22-language state; it remains the required historical reference, not the source of current language-count metadata.

The JRC conditions are explicit: the database is the “exclusive property of the European Commission”; the Commission grants non-exclusive worldwide reuse under Commission Decision 2011/833/EU. Re-users must identify the source website, the latest update date and the fact that the European Commission retains ownership. The JRC page does not state an exact day/month for the 2021 release; the correct update date to report is therefore the 2021 release year, not an invented calendar date.

The 2012 paper repeats the conditions and notes that the underlying files are identified by the EUR-Lex Numdoc of the original legislative document, but preprocessing modifies documents and extracted sequence order does not necessarily match the original. This is important for excerpt-level provenance: preserve the Numdoc/CELEX ID and do not claim that a translation unit is a verbatim contiguous passage from the source legislation. The paper describes DGT-TM as “sentences and their professionally produced translations”; that is a corpus description, not a separate licence grant.

Recommended attribution text for the final source notice:

> Source: DGT-Translation Memory (DGT-TM), European Commission Directorate-General for Translation / Joint Research Centre, 2021 release (Vol_2020_1–Vol_2020_5). Latest update: 2021. The European Commission retains ownership of the DGT-TM database. Source page: https://joint-research-centre.ec.europa.eu/language-technology-resources/dgt-translation-memory_en. Accessed: [actual access date].

Cite Steinberger et al. (2012) for the resource and Steinberger et al. (2014) for the broader EU multilingual corpus landscape. The 2012 paper is not a 24-language citation; the current JRC page supplies that current count.

**Decision:** retain DGT-TM as a strong source under the Commission's reuse conditions, with explicit attribution and ownership notice. Preserve Numdoc IDs and release/version metadata. Do not label the source CC0 or CC BY unless the exact Commission reuse notice is separately mapped to a compatible licence; the project's final combined dataset may choose CC BY as a distribution policy while retaining the EC's original source notice.



## 13. Common Crawl, FineWeb, HPLT and Hugging Face — who grants what, and who bears the risk

### Common Crawl terms: the user assumes the downstream risk

Official Common Crawl Terms of Use (last updated 7 March 2024): https://commoncrawl.org/terms-of-use

The ToU says that using Crawled Content is binding acceptance of the terms; the content may be subject to separate terms from the origin website. It states that the content is the “sole responsibility” of the originator, tells users to respect third-party rights, and says users must evaluate and bear the risks of using it. The terms also say Common Crawl may remove content from its own service at its discretion; its §5 notice procedure applies to alleged infringement “on or through” Common Crawl's site/service, not to automatic removal from downstream corpora.

The indemnity is unusually explicit. Section 9 requires users to indemnify, defend and hold Common Crawl harmless for third-party claims arising from access to or use of Crawled Content, including claims involving “artificial intelligence, machine learning”, “developing, training, or deploying AI Systems”, infringement of third-party copyright, and privacy/publicity rights. This is a contractual allocation of risk to the user; it is not a copyright licence or clearance of the crawled pages.

### FineWeb and FineWeb2: ODC-BY is not an excerpt licence

FineWeb dataset card: https://huggingface.co/datasets/HuggingFaceFW/fineweb  
FineWeb paper: Penedo et al. (2024), “The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale.” https://arxiv.org/abs/2406.17557  
FineWeb2 dataset card: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2  
FineWeb2 paper: Penedo et al. (2025), “FineWeb2: One Pipeline to Scale Them All — Adapting Pre-Training Data Processing to Every Language.” https://arxiv.org/abs/2506.20920  
ODC-BY 1.0 full licence: https://opendatacommons.org/licenses/by/1-0/

Both Hub cards use the ODC-BY 1.0 licence tag and make use subject to Common Crawl's Terms of Use. The legal text of ODC-BY is decisive: its preamble says it “only governs the rights over the Database, and not the contents of the Database individually”; §2.4 says it does not cover rights in individual contents, which may separately involve copyright, data protection, privacy or personality rights. ODC-BY therefore licenses the database/compilation and its database rights; it is not a licence from each website author to reuse the page text.

The FineWeb paper's datasheet says the release anonymizes “email addresses and public IP addresses using regex patterns.” It does not describe a general PII review, per-page copyright clearance or a public takedown workflow. The FineWeb2 paper describes 96 Common Crawl snapshots and a multilingual filtering pipeline, but the reviewed paper and card do not discuss source-page copyright clearance, a per-excerpt licence registry or a takedown process. This is a statement about the public materials reviewed, not proof that no internal process exists.

### HPLT 3.0: unusually candid rights disclaimer and takedown process

HPLT 3.0 dataset card: https://huggingface.co/datasets/HPLT/HPLT3.0  
HPLT 3.0 paper: Oepen et al. (2026), “HPLT 3.0: Very Large-Scale Multilingual Resources for LLMs and MT.” DOI: https://doi.org/10.63317/25xbdofco9od

The card says: “We do not own any of the text from which these text data has been extracted.” It states that CC0 applies to the packaging/metadata, not the underlying text, and that users are responsible for compliance with applicable law. The paper explains that much of the web text is copyrighted or lacks reuse terms; HPLT claims no ownership and grants no rights in the text itself. It separately notes that Internet Archive expressly consented to redistribution of derived language resources, while Common Crawl and ArchiveBot data are treated as publicly accessible crawls rather than as content licensed by HPLT.

HPLT documents a notice-and-takedown channel. It says legitimate requests result in affected sources being removed from the next release. This is useful transparency and a real operational process, but it does not retroactively remove text from prior releases and does not transfer legal responsibility from the user. Its data also includes URL/crawl provenance, document- and segment-level language metadata, quality annotations and PII-span annotations; the paper expects users to mask or exclude PII rather than treating annotations as a universal removal guarantee.

### Hugging Face: license tags are publisher metadata, not rights verification

Hugging Face dataset-card documentation: https://huggingface.co/docs/hub/en/datasets-cards  
Hugging Face Terms of Service: https://huggingface.co/terms-of-service  
Hugging Face Content Policy / DMCA process: https://huggingface.co/content-policy

HF documentation says the repository README is the dataset card and that a publisher can add a license field in its YAML metadata; the Hub displays that tag and uses it for discovery. It does not describe a platform process that validates the rights in every source excerpt. The Terms of Service state: “You are solely responsible for the Content you post, publish, display or otherwise make available.” For a public repository, the uploader grants each Hub user a “perpetual, irrevocable, worldwide, royalty-free, non-exclusive license” to use, display, publish, reproduce, distribute and make derivative works of the content through HF services. The uploader also indemnifies HF for claims arising from any content or data posted or used. HF's Content Policy prohibits IP-infringing and privacy-violating content and provides reporting/DMCA channels, but these are reactive moderation mechanisms, not pre-publication excerpt-level clearance.

### Practical conclusion for langid-32

1. A CC0 or ODC-BY badge on a Common Crawl-derived dataset does not clear individual page text. Read the licence's scope and the source ToU separately.
2. Common Crawl's current ToU places substantial contractual risk on users, including for AI/ML training and copyright/privacy claims. A downstream dataset publisher should not treat the Common Crawl licence/terms as a permission to redistribute every page.
3. HPLT's approach is the most transparent of the reviewed publishers: it disclaims text rights, identifies source-specific consent where it exists, preserves provenance, annotates PII, and provides notice-and-takedown. Its policy is not a legal safe harbour and does not make the text rights-cleared.
4. FineWeb/FineWeb2 public documentation does not disclose comparable per-page rights clearance or a public takedown mechanism. Their ODC-BY tag is a database licence; the Common Crawl ToU still applies.
5. Hugging Face does not certify the uploader's source rights by displaying a licence tag. Its Terms place responsibility and indemnity on the uploader; DMCA is a reactive remedy.
6. If langid-32 ever uses Common Crawl-derived text, each retained record needs source URL, crawl identifier/date, exact text fingerprint, source terms/licence evidence, provenance and PII results. Maintain an exclusion/takedown ledger that propagates to all derived records and future releases. Do not claim CC0 for the excerpts merely because the packaging or metadata is CC0.
