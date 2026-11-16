# Corpus source inventory

Status: initial desk inventory, 2026-11-16. This is a source-discovery document, not a claim that any corpus has already been downloaded, parsed, or counted. All per-language usable-record counts remain **unmeasured**.

Target: 20,000 usable text examples per language across 32 languages (640,000 total). Count after normalization, quality filtering, and cross-source deduplication—not archive size, audio hours, aligned sentence pairs, or document counts.

## 1. Source coverage by target language

Legend:
- **Y** = source documentation explicitly lists this language.
- **—** = source's documented language coverage excludes it.
- **?** = not yet verified against the current source catalogue or release.
- A Y means coverage, not a guarantee of 20,000 usable examples.

| Code | Language | Common Voice 27 | JRC-Acquis 3 | DGT-TM | Europarl v7 | Tatoeba | OPUS |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| bg | Bulgarian | ? | Y | Y | Y | ? | ? |
| hr | Croatian | ? | — | Y | — | ? | ? |
| cs | Czech | ? | Y | Y | Y | ? | ? |
| da | Danish | ? | Y | Y | Y | ? | ? |
| nl | Dutch | ? | Y | Y | Y | ? | ? |
| en | English | ? | Y | Y | Y | ? | ? |
| et | Estonian | ? | Y | Y | Y | ? | ? |
| fi | Finnish | ? | Y | Y | Y | ? | ? |
| fr | French | ? | Y | Y | Y | ? | ? |
| de | German | ? | Y | Y | Y | ? | ? |
| el | Greek | ? | Y | Y | Y | ? | ? |
| hu | Hungarian | ? | Y | Y | Y | ? | ? |
| ga | Irish | ? | — | Y | — | ? | ? |
| it | Italian | ? | Y | Y | Y | ? | ? |
| lv | Latvian | ? | Y | Y | Y | ? | ? |
| lt | Lithuanian | ? | Y | Y | Y | ? | ? |
| mt | Maltese | ? | Y | Y | — | ? | ? |
| pl | Polish | ? | Y | Y | Y | ? | ? |
| pt | Portuguese | ? | Y | Y | Y | ? | ? |
| ro | Romanian | ? | Y | Y | Y | ? | ? |
| sk | Slovak | ? | Y | Y | Y | ? | ? |
| sl | Slovenian | ? | Y | Y | Y | ? | ? |
| es | Spanish | ? | Y | Y | Y | ? | ? |
| sv | Swedish | ? | Y | Y | Y | ? | ? |
| nb | Norwegian Bokmål | ? | — | — | — | ? | ? |
| nn | Norwegian Nynorsk | ? | — | — | — | ? | ? |
| ru | Russian | ? | — | — | — | ? | ? |
| ja | Japanese | ? | — | — | — | ? | ? |
| zh | Chinese | ? | — | — | — | ? | ? |
| ko | Korean | ? | — | — | — | ? | ? |
| ar | Arabic | ? | — | — | — | ? | ? |
| tr | Turkish | ? | — | — | — | ? | ? |

Coverage references and caveats:
- Common Voice: v27.0 was announced on 2026-09-18 with 295 scripted-speech languages. Its release documentation specifies a per-locale `validated_sentences.tsv` (available since corpus 17.0) with `sentence_id`, `sentence`, optional `variant`, and optional `sentence_domain`. This is the most directly relevant text inventory for this project; it is distinct from the audio clip TSVs. The release metadata JSON also reports a per-locale `validatedSentences` count, useful as a preliminary cross-check. We still need to verify the 32 exact locale codes and count the actual TSV rows after our own filters. Sources: https://github.com/common-voice/cv-dataset/blob/main/datasets/scripted-speech/README.md, https://github.com/common-voice/cv-dataset/blob/main/datasets/scripted-speech/cv-corpus-27.0-delta-2026-09-11.json, https://discourse.mozilla.org/t/common-voice-scripted-speech-v27-0-and-spontaneous-speech-v5-0-released/149490 and https://commonvoice.mozilla.org/datasets
- JRC-Acquis 3.0 explicitly lists 22 languages. Its documentation reports text/document statistics per language. It excludes Croatian and Irish from this release. It is a research corpus, not a legal reference corpus. Source: https://joint-research-centre.ec.europa.eu/language-technology-resources/jrc-acquis_en
- DGT-TM documents coverage of all 24 EU official languages, but Irish has very little material and Croatian less than older member-state languages. It consists of translation units, mostly sentence or sub-sentence segments, not full reproducible documents. Source: https://joint-research-centre.ec.europa.eu/language-technology-resources/dgt-translation-memory_en
- Europarl v7 documents 21 languages and publishes per-language sentence counts. It does not cover Croatian, Irish or Maltese. It is old parliamentary proceedings, with strong domain and register bias. Source: https://www.statmt.org/europarl/
- Tatoeba publishes a full sentence export and a separate CC0-only export. The general sentence export is CC BY 2.0 FR; only the separately identified subset is CC0. Coverage and usable counts must be measured per target language. Preserve base/translation links so translated variants can be grouped or excluded together. Source: https://tatoeba.org/en/downloads
- OPUS is an aggregator, not a single uniformly licensed dataset. Its catalogue spans many languages and corpora, but each corpus has its own coverage, provenance, quality and licence. Screen each candidate individually; do not ingest the aggregate indiscriminately. Source: https://opus.nlpl.eu/

## 2. Source assessment and acquisition priority

| Priority | Source | Why it matters | Main risks / work required |
|---|---|---|---|
| P0 | Common Voice Scripted Speech 27.0 | Natural, short, crowd-contributed sentences; CC0; broad language ambitions | Verify text TSV availability and count for every locale. Repeated prompts and domain-specific prompts; group prompt variants to prevent leakage. Text availability may differ from audio clip volume. |
| P1 | DGT-TM latest available release | Potentially strong source for all 24 EU official languages, including Irish and Croatian | Translation-memory segments; high translationese/legal register; document identity is present in EUR-Lex IDs and must be retained internally for splitting. Verify current release and extraction format. |
| P1 | Tatoeba CC0 export | Simple, directly downloadable sentence-level data; useful for many non-EU languages | CC0 subset is smaller than full export; translation chains and sentence pairs create leakage; sentence quality and language labels need validation. |
| P1 | OPUS candidates | Likely essential for Russian, Japanese, Chinese, Korean, Arabic, Turkish and Norwegian varieties | Treat each corpus separately. Check per-language volume, license, domain, source document IDs and translation overlap. Prefer original monolingual material where possible. |
| P2 | JRC-Acquis 3.0 | Large and documented 22-language multilingual corpus; useful for EU language coverage and cross-language testing | Mostly legislative/legal register; overlaps substantially with DGT-TM; not all source text is necessarily equally suitable. Reuse conditions require attribution and retention of Commission ownership/source information. |
| P2 | Europarl v7 | Publicly documented per-language sentence counts; substantial volume for 21 languages | 1996–2011 parliamentary proceedings; strong domain bias; speaker/document markup; verify redistribution terms before publication. |
| P3 | Other monolingual sources | Fill shortfalls and broaden register/domain | Only admit sources with clear per-component terms, provenance, stable identifiers and defensible language labels. |

## 3. What is already established—and what is not

Established from source documentation:
- JRC-Acquis 3.0 covers 22 target languages and reports 463,792 texts across those languages. These are **document counts**, not usable sentence counts.
- DGT-TM documentation lists 24 EU official languages; Irish is explicitly described as sparse and Croatian as smaller.
- Europarl v7 documents 21 languages and per-language sentence counts, ranging from 387,490 Polish sentences to over 2.3 million Danish/Dutch sentences in the source corpus.
- Tatoeba's ordinary export and CC0-only export are distinct. Do not label the entire ordinary export CC0.
- OPUS contains many independent corpora with different licences; OPUS-wide totals are not evidence that any particular target language has 20,000 admissible examples.

Not established:
- Current Common Voice v27 text/TSV availability and usable counts for each of the 32 target locales.
- Exact usable counts for any source after our text-length, language, duplicate, privacy and quality filters.
- Per-language coverage and licence eligibility of Tatoeba CC0 and each OPUS candidate.
- Whether 20,000 examples per language can be reached without over-relying on one domain or translated text.

## 4. Required inventory measurements

For each (source, release, language), record:

1. Archive/file URL and retrieval date; archive SHA-256.
2. Licence and source-specific reuse/attribution conditions, checked against the actual release.
3. Raw rows, non-empty rows, and rows with a valid language label.
4. Rows passing basic length/Unicode/script checks.
5. Exact duplicates within source and cross-source duplicates.
6. Unique source documents/groups and number of groups contributing usable examples.
7. Usable examples after all agreed filters.
8. Domain/register label and whether text is original, translated, or uncertain.
9. PII/identifier review outcome.
10. Final accepted count and shortfall against 20,000.

Do not use archive byte size, number of audio clips, number of translation pairs, or document count as a substitute for usable text-example counts.

## 5. Pipeline implications

The current `langid32-prepare` command processes one input file per invocation and caps each invocation independently. That is not yet sufficient for a multi-source corpus: independently prepared outputs cannot safely be concatenated because duplicate removal, source balancing, document grouping, and the final 20,000-per-language cap must be applied globally.

Before bulk ingestion, the corpus pipeline should gain a merge-first stage with an intermediate record containing at least:
- `text`
- `language`
- `source_id` and `source_release`
- `document_group` (or another stable leakage-control group)
- `licence_id`
- `text_origin` (`original`, `translated`, `unknown`)

The internal staging data may retain provenance/group identifiers; the published training JSONL should continue to omit contributor identifiers and internal group IDs. Global deduplication and group-level train/validation/test splitting must happen after source ingestion and before the final cap. Related translations and repeated prompts must not be split across train and evaluation.

For source balancing, keep per-source counts and quotas visible. A language with 20,000 examples drawn almost entirely from legal text is not equivalent to one with broad domain coverage. Do not silently fill a shortfall with translated or synthetic sentences.

## 6. Immediate execution sequence

1. Use the v27 release metadata JSON to enumerate exact locale codes and preliminary `validatedSentences` counts; then inspect/download the corresponding MDC locale archives and count `validated_sentences.tsv` rows and usable text.
2. Implement a read-only inventory/counting command that reports the measurements in section 4 without publishing text.
3. Inspect DGT-TM release metadata and extract counts for all 24 EU languages.
4. Measure Tatoeba CC0 per language and preserve its translation/base graph.
5. Query OPUS corpus-by-corpus for the seven non-EU additions and Norwegian Bokmål/Nynorsk; shortlist by licence, volume, and source quality.
6. Only then implement the merge-first global preparation stage and build the first corpus.

No source counts are currently claimed in this inventory beyond the published source-level statistics described above.
