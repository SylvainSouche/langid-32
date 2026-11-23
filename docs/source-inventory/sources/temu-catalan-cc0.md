# TeMU-BSC — Catalan CC0 collection

**Text unit:** Sentences / generated examples (mixed)  
**Primary source:** https://github.com/TeMU-BSC/catalan_CC0_sentences

## Creator and origin

Text Mining Unit, Barcelona Supercomputing Center, with Catalan public-sector and other contributors.

## Access methods

Public Git repository; clone/archive over HTTPS; project scans allowlisted TXT/TSV files and records Git revision.

## File types and structure

TXT/TSV, including aggregate collections.

## Distribution conditions and rights

Many files declared CC0/public domain, but terms vary by file. Check README entries, waivers and agreements. Catalan-DPO-V2 excluded due mixed 40/60 language split.

## Content and language coverage

Catalan government crawl, linguistic-policy material, dictionaries, templates, literature and community contributions.

## Verified upstream availability (independent of project acquisition)

The pinned upstream README (`30f19bbfaca7b8abdd195c4687c1a992bde4f63f`) reports the following distinct CC0 files or non-overlapping aggregate groups. This expands the previously documented two-file minimum. Counts below are **raw source-reported sentence rows**, not within-source unique sentences; the repository does not publish a global deduplication count. Some entries are template-generated or synthetic-like, so retain their provenance for later quality assessment.

| File or non-overlapping group | Sentence rows | Basis / note |
|---|---:|---|
| catalan_government_crawling_frases_seleccionades_filtrades.txt | 93,691 | Provider README; selected/filtered from Catalan Government crawl; CC0 |
| datasets_sentences.tsv | 155,990 | Provider README; Projecte Aina source datasets; CC0 waiver |
| Seven constituent files of new_catalan_cc0_corpus.txt | 107,892 | Sum of the seven individual README counts; TeMU-BSC-owned CC0 material; aggregate file itself is not added again |
| frases_agenda.txt | 160,665 | Template-generated; TeMU-BSC CC0 waiver |
| frases_diccionaris_enciclopedia.txt | 20,122 | Counted non-empty lines in the file at the pinned repository revision; source README says ~20k; CC0 waiver |
| frases_toponimia_valenciana_balear.txt | 15,451 | Template-generated; TeMU-BSC CC0 waiver |
| literatura.txt | 366 | Counted non-empty lines in the file at the pinned repository revision; source README reports 366; CC0 |
| new_sentences_from_catalan_newswire.txt | 58,310 | Provider README; owner agrees to CC0 publication |
| xitxat_toponyms.txt | 37,428 | Provider-reported aggregate; do not add its constituent files separately |
| **Reported raw CC0 rows across these disjoint files/groups** | **649,915** | Sum before cross-file exact/near-duplicate audit; not a unique-sentence count |

The seven-file group consists of `edited_generated_selected_chatbot.txt` (2,166), `edited_selected_chatbot.txt` (873), `frases_spl.txt` (1,711), `generades_spl_seleccionades.txt` (4,469), `more_intents.txt` (74,772), `plantilles_intents.txt` (2,664), and `selected_club.txt` (21,237). The xitxat aggregate includes `sentences_from_xitxat_corpus.txt` and `wikidata_sentences.txt`, so these are not added a second time. The README also lists files under individual permission arrangements (including Marius Serra and Joan Pujolar contributions); they are not included in this CC0 subtotal. The translated Spanish-Wikipedia file is also excluded until its rights basis is documented.

This subtotal replaces the former 249,681 two-file minimum, but remains a pre-dedup raw count. It is not the same as the project's 174,157 staged records. Source: https://github.com/TeMU-BSC/catalan_CC0_sentences/tree/30f19bbfaca7b8abdd195c4687c1a992bde4f63f

## Current langid-32 acquisition snapshot

174,157 current Catalan records; may include generated/template examples; not necessarily unique natural sentences or full upstream count.

| Language | Current staged records |
|---|---:|
| ca | 174,157 |

**Current staged total:** 174,157 records.

> These counts describe our staged sample, not upstream capacity. They may reflect our own caps, partial downloads, filtering or selected snapshots. Counts across sources are not necessarily unique. Granularity varies by source.

## Remaining checks

- Enumerate every remaining individual file and identify aggregate/constituent relationships.
- Verify file-level waivers, contributor agreements and permission scope; do not assume every repository file is CC0.
- Count exact lines and unique normalized sentences from a pinned Git revision, then reconcile against the README's stated totals.
- Keep the 249,681 identified minimum separate from the 174,157 historical project sample.
