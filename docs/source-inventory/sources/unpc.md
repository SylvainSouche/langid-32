# United Nations Parallel Corpus (UNPC) v1.0

**Text unit:** Official documents, aligned document pairs and sentence/line alignments  
**Primary source:** https://www.un.org/dgacm/en/content/uncorpus  
**Download page:** https://www.un.org/dgacm/content/uncorpus/Download

## Creator and origin

United Nations Department for General Assembly and Conference Management (DGACM). The corpus contains official records and other parliamentary documents, mostly available in the six UN official languages: Arabic, Chinese, English, French, Russian and Spanish. Coverage spans material produced and manually translated between 1990 and 2014.

## Verified upstream availability

The official UN statistics report:

| Measure | Provider-reported count | Unit |
|---|---:|---|
| Total documents | 799,276 | documents |
| Aligned document pairs | 1,727,539 | language-pair document alignments |
| Fully aligned subcorpus | 86,307 | documents |
| Fully aligned subcorpus | 11,365,709 | aligned lines |
| Fully aligned subcorpus | 334,953,817 | English tokens |

The official pairwise matrix provides, for each language pair, an aligned document count and aligned line count in the upper triangle, and language-side token counts in the lower triangle. Those pairwise line counts are not independent monolingual pools: a multilingual sentence may occur in several pair configurations. Do not sum across the 15 pairs and label the result unique sentences. Exact per-language unique sentence counts remain to be computed from the XML language archives.

## Access and format

The UN provides language-specific TEI XML archives organized by language, year and publication symbol. Parallel versions share corresponding paths; separate link archives identify aligned sentence IDs, link type and alignment quality. Plain-text bitext archives are also provided for each language pair. The six language-specific archives are the correct basis for monolingual extraction and deduplication.

## Rights and attribution

The UN describes the corpus as consisting of official records and other parliamentary documents in the public domain. Users must acknowledge the United Nations as the source and cite Ziemski, Junczys-Dowmunt and Pouliquen (2016), *The United Nations Parallel Corpus*, LREC 2016. Preserve document symbols and source metadata.

## Remaining work

- Download and pin the six language-specific XML archives and link files.
- Count source documents and sentence elements per language, deduplicating by UN document symbol and sentence identity.
- Reconcile extracted counts with the official pairwise statistics without summing pairwise rows.
- Keep the fully aligned subset distinct from the full corpus.
- Record archive checksums and retrieval date.
