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
- JRC-Acquis 3.0 explicitly lists 22 languages and reports 463,792 documents in total. It excludes Croatian and Irish. The JRC says it is a research corpus, not a legal reference corpus; the official conditions require source attribution and retention of Commission ownership, and distinguish public-domain official legislative material from other content. Do not assume the entire compiled corpus has one blanket CC0-style licence. Review the actual conditions before redistributing it. Source: https://joint-research-centre.ec.europa.eu/language-technology-resources/jrc-acquis_en
- DGT-TM documents coverage of all 24 EU official languages, but Irish is sparse and Croatian has less material. It consists of translation units, mostly sentence or sub-sentence segments, not full reproducible documents. The current download page lists releases through DGT-TM-release 2021 (the 2020 data update); do not describe it as a current annual feed. The statistics PDF reports roughly 0.24M to 6.44M translation units per language in the 2011–2020 updates, but these are aligned translation units, not unique independent sentences. The Commission permits reuse subject to attribution, source/date identification and retention of Commission ownership. Sources: https://joint-research-centre.ec.europa.eu/language-technology-resources/dgt-translation-memory_en and https://wt-public.emm4u.eu/Resources/DGT-TM_Statistics.pdf
- Europarl v7 documents 21 languages and publishes per-language sentence counts after XML removal. It does not cover Croatian, Irish or Maltese. All 21 target-language counts exceed 387,000; its documents retain IDs, which makes group-level splitting possible. It is parliamentary proceedings from 1996–2011, with strong domain/register bias. The project page says it is not aware of copyright restrictions, but this should still be recorded as the source's statement rather than a formal licence grant. Source: https://www.statmt.org/europarl/
- Tatoeba publishes a full sentence export and a separate CC0-only export. The general sentence export is CC BY 2.0 FR; only the separately identified subset is CC0. The CC0 language list includes 18 of our target classes (cs, da, nl, en, fi, fr, de, hu, it, pl, pt, es, sv, nb, ru, ja, zh/Mandarin, ar); it does not list the other 14 target classes. This is a language-availability signal, not a count. Preserve the sentence-base and translation-link files to identify translations and prevent cross-split leakage. The CC0 export is updated weekly. Source: https://tatoeba.org/en/downloads
- OPUS is an aggregator, not a single uniformly licensed dataset. Its catalogue spans many languages and corpora, but each corpus has its own coverage, provenance, quality and licence. Screen each candidate individually; do not ingest the aggregate indiscriminately. Source: https://opus.nlpl.eu/

## 2. Source assessment and acquisition priority

| Priority | Source | Why it matters | Main risks / work required |
|---|---|---|---|
| P0 | Common Voice Scripted Speech 27.0 | Natural, short, crowd-contributed sentences; CC0; broad language ambitions | Verify text TSV availability and count for every locale. Repeated prompts and domain-specific prompts; group prompt variants to prevent leakage. Text availability may differ from audio clip volume. |
| P1 | DGT-TM release 2021 (data through 2020) | Large translation-memory volume across all 24 EU languages; even Irish and Croatian have six-figure unit counts in the latest update | Translation-memory segments; legal/administrative register and translationese; duplicate segments; EUR-Lex document IDs must be retained for grouping. The source page's current list ends at the 2021 release. |
| P1 | Tatoeba CC0 export | Simple, directly downloadable sentence-level data; useful for many non-EU languages | CC0 subset is smaller than full export; translation chains and sentence pairs create leakage; sentence quality and language labels need validation. |
| P1 | OPUS candidates | Likely essential for Russian, Japanese, Chinese, Korean, Arabic, Turkish and Norwegian varieties | Treat each corpus separately. Check per-language volume, license, domain, source document IDs and translation overlap. Prefer original monolingual material where possible. |
| P2 | JRC-Acquis 3.0 | 22 languages and 463,792 documents; useful for EU language coverage and cross-language evaluation | Mostly legislative/legal register; overlaps substantially with DGT-TM. Compiled corpus has nuanced reuse conditions; inspect actual content rights and attribution requirements before publishing derived text. |
| P2 | Europarl v7 | Publicly documented per-language sentence counts; substantial volume for 21 languages | 1996–2011 parliamentary proceedings; strong domain bias; speaker/document markup; verify redistribution terms before publication. |
| P3 | Other monolingual sources | Fill shortfalls and broaden register/domain | Only admit sources with clear per-component terms, provenance, stable identifiers and defensible language labels. |

## 3. Common Voice v27.0 metadata: first measured result

I parsed the upstream v27.0 release JSON directly:
`cv-corpus-27.0-delta-2026-09-11.json`, blob SHA `9de5d5b46eabc3678174f58adae4b5c75dc1e641`.

The metadata contains a matching locale entry for every one of our 32 target languages. There are 33 locale files to inspect because Chinese is represented by both `zh-CN` and `zh-TW`. The table below reports the upstream `validatedSentences` metadata field, not our own count of rows in the downloadable TSV and not the final usable count.

| Target | Common Voice locale(s) | Metadata validatedSentences | Gap to 20,000 (metadata only) |
|---|---|---:|---:|
| bg | bg | 39,572 | 0 |
| hr | hr | 1,781 | 18,219 |
| cs | cs | 451,317 | 0 |
| da | da | 20,986 | 0 |
| nl | nl | 260,921 | 0 |
| en | en | 1,682,617 | 0 |
| et | et | 11,118 | 8,882 |
| fi | fi | 5,865 | 14,135 |
| fr | fr | 1,661,012 | 0 |
| de | de | 2,058,031 | 0 |
| el | el | 8,950 | 11,050 |
| hu | hu | 326,554 | 0 |
| ga | ga-IE | 4,883 | 15,117 |
| it | it | 925,181 | 0 |
| lv | lv | 34,689 | 0 |
| lt | lt | 129,359 | 0 |
| mt | mt | 5,274 | 14,726 |
| pl | pl | 230,314 | 0 |
| pt | pt | 43,656 | 0 |
| ro | ro | 13,756 | 6,244 |
| sk | sk | 22,194 | 0 |
| sl | sl | 4,209 | 15,791 |
| es | es | 1,082,797 | 0 |
| sv | sv-SE | 26,893 | 0 |
| nb | nb-NO | 4,419 | 15,581 |
| nn | nn-NO | 5,318 | 14,682 |
| ru | ru | 48,002 | 0 |
| ja | ja | 44,606 | 0 |
| zh | zh-CN + zh-TW | 80,036 | 0 |
| ko | ko | 7,432 | 12,568 |
| ar | ar | 59,439 | 0 |
| tr | tr | 410,411 | 0 |

**Initial signal:** 21 of 32 target languages have at least 20,000 entries in this metadata field. Eleven are below the target: hr, et, fi, el, ga, mt, ro, sl, nb, nn and ko. The metadata total across the 32 target languages is 9,711,592.

This is encouraging but not yet evidence that Common Voice alone supplies the target corpus:
- The release JSON field is a preliminary inventory statistic. We have not counted the corresponding TSV rows. The per-locale metadata snapshot is committed at [common-voice-v27-metadata.csv](data/common-voice-v27-metadata.csv).
- The TSV has an `is_used` flag. Retired sentences may be outdated, too similar, incorrect, or otherwise no longer eligible for recording. We should count all non-empty rows and the `is_used=true` subset separately; use the latter as the conservative first-pass pool.
- The metadata's clip and user counts are not text-corpus counts and must not be used to infer the number of usable sentences.
- A sentence-level file has no source-document ID. Retain `sentence_id` as the grouping key to prevent repeated prompt text from crossing splits; this does not solve broader document-level leakage.
- For Chinese, retain the locale distinction during inventory and deduplication, then decide whether both script varieties belong in the single `zh` class. Do not discard the locale provenance.
- Metadata counts can be very large relative to the clips reported for some locales. This reinforces why we must inspect the actual archive and TSV rather than infer availability from the JSON.

The locale mapping used here is explicit: `ga-IE`, `sv-SE`, `nb-NO`, `nn-NO`, and `zh-CN` + `zh-TW`; the other targets use their two-letter locale codes.

### Reproducible inventory command

A read-only counter is now implemented at `src/langid32/common_voice_inventory.py`. It reads the official release JSON and, when given extracted locale directories, scans `validated_sentences.tsv` without copying sentence text into the report. It records raw rows, non-empty rows, `is_used` counts, basic length-filter counts, normalized within-file duplicates, and per-locale counts of sentence source and domain values.

After installing the project in the existing development environment:

```sh
langid32-cv-inventory \
  --release-json /path/to/cv-corpus-27.0-delta-2026-09-11.json \
  --data-root /path/to/extracted/common-voice-v27 \
  --output data/inventory/common-voice-v27.csv
```

The command also works without `--data-root`, in which case it emits metadata-only rows and explicitly marks TSV counts as unmeasured. It does not download data. Obtain original archives directly from MDC.

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
