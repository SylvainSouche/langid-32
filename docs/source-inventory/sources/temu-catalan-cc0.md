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

The upstream README reports at least two separately identifiable sentence files:

| File | Provider-reported sentences | Notes |
|---|---:|---|
| `catalan_government_crawling_frases_seleccionades_filtrades_sorted.txt` | 93,691 | Selected/filtered sentences from a 39-million-token Catalan Government web crawl |
| `datasets_sentences.tsv` | 155,990 | Sentences extracted from Projecte Aina datasets (caBreu, CoQCat, NLUCat, Parafraseja) |
| **Identified minimum** | **249,681** | Sum of the two named files only; not a complete repository total or post-deduplication count |

Do not add aggregate files to their constituent files. In particular, `new_catalan_cc0_corpus.txt` aggregates seven listed files and `xitxat_toponyms.txt` aggregates other files. The README also lists sources with individual permission/waiver statements; file-level terms must be checked before counting them as CC0-eligible. This 249,681 minimum is not the same as the project's 174,157 staged records. Source: https://github.com/TeMU-BSC/catalan_CC0_sentences

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
