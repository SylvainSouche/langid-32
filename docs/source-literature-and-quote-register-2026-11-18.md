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

The project README describes the treebank as “10 million parsed sentences” and says the text was extracted from news and government sites during 2015–2021. It identifies Miðeind ehf. as the publisher to credit under CC BY 4.0. The CLARIN deposit also labels the archive CC BY 4.0.

The practical issue is not simply article-level attribution: the current candidate pipeline has no original source article URL/title/author/date for these parser test/development sentences. The source file and line are insufficient to reconstruct the news or government work from which a sentence originated.

**Decision:** do not count the 4,930 rows as a broad Greynir corpus contribution. Exclude them from the main language corpus pending a separate, deliberate acquisition of the full copper/silver data, confirmation of Git-LFS retrieval, and a provenance/rights assessment. If the gold/dev set is ever used for a separate evaluation task, keep it isolated from training and preserve its exact parser-test/dev designation.

## 3. IGC2024 Filtered-1 — updated rights and citation evidence

CLARIN-IS record: https://repository.clarin.is/repository/xmlui/handle/20.500.12537/381  
Project portal: https://igc.arnastofnun.is/  
2026 paper: https://lrec.elra.info/lrec2026-ws-cmlc-06  
README: https://repository.clarin.is/repository/xmlui/bitstream/handle/20.500.12537/381/README.txt?isAllowed=y&sequence=3

The CLARIN record identifies authors Jón Friðrik Daðason, Steinþór Steingrímsson and Hinrik Hafsteinsson; issue date 30 March 2026; publisher The Árni Magnússon Institute for Icelandic Studies; and CC BY 4.0. The archive README calls it a JSONL version of the 2024 IGC “prepared for language model training” and describes the documents as “unannotated, CC-BY-licensed documents from the IGC.” It also explicitly requests citation of the 2018 IGC paper and the 2026 curation paper.

A further, important statement on the official IGC portal says that copyright clearance has been secured for the texts used to enable Language Technology projects. This is stronger and more specific than a generic crawl-dataset wrapper licence. It materially improves the rights evidence, but the exact scope of that clearance and whether it expressly covers redistribution of selected excerpts in a separately published corpus still need confirmation. The filtered JSONL's actual retained bibliographic fields must also be checked before asserting that every selected record can carry source-level attribution.

The 2026 paper's abstract describes a filtering pipeline including “fuzzy deduplication to reduce the risk of data leakage”. This is scholarly context for the filtered release, not a licence grant.

Required scholarly references:
- Jón Friðrik Daðason and Steinþór Steingrímsson. 2026. “Optimized for AI: Curating the Icelandic Gigaword Corpus for Stable LLM Training.” Proceedings of the 12th Workshop on Challenges in the Management of Large Corpora, pp. 49–56. DOI: https://doi.org/10.63317/3uatbht8mdrf.
- Starkaður Barkarson, Steinþór Steingrímsson and Hildur Hafsteinsdóttir. 2022. “Evolving Large Text Corpora: Four Versions of the Icelandic Gigaword Corpus.” LREC 2022, pp. 2371–2381.

**Decision:** retain the current rights hold as a narrow verification hold, not as a conclusion that IGC lacks text rights. Confirm the filtered-release grant and inspect the acquired JSONL schema/record metadata. If the grant and attribution conditions cover redistribution, the CC BY 4.0 corpus can be considered for inclusion with required attribution and change notice.

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

The 50,414 candidate count in the waiting-source manifest consists of 50,000 DOGC and 414 APDCAT rows. The paragraph-level file contributed no rows to that sample. Do not describe all three subcorpora as represented in the candidate sample.

**Decision:** keep BSC-LT on hold pending review of the exact Generalitat open-data notice and the APDCAT data-sharing agreement. The DOGC component has a stronger public CC0 route; do not let the APDCAT agreement's uncertainty unnecessarily obscure that separable constituent.

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

The relevant official statement is that new text is licensed under “Creative Commons Attribution-ShareAlike 4.0 International License”. This is not a simple wholesale upgrade of all old article text: the snapshot contains revisions spanning both licence periods. The HF dataset card's CC BY-SA 3.0/GFDL labels do not capture the complete 2023-11-01 rights position. The current langid-32 acquisition metadata, which labels every row `CC-BY-SA-4.0;GFDL-1.3`, is also inaccurate/incomplete: it does not distinguish pre- and post-transition revisions and treats the GFDL version as fixed.

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

**Decision:** the 30,790 rows from the old waiting-source artifact are quarantined and excluded from all Catalan totals. The acquisition workflow now deliberately skips DPO V2 until a separate pipeline can identify Catalan rows, preserve source-component provenance and resolve the underlying content/model-output terms. The previous artifact's 613,860 rows therefore reduce to 583,070 non-DPO technical candidates; this does not make the remaining rows release-cleared.
