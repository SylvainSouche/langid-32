# GreynirCorpus 1.1

**Primary source:** https://github.com/mideind/GreynirCorpus  
**CLARIN-IS record:** https://repository.clarin.is/repository/xmlui/handle/20.500.12537/119

## Provider-described availability

The upstream README describes these separate partitions:

| Partition | Provider-reported quantity | Unit / interpretation |
|---|---:|---|
| Copper | 10,000,000 | Mechanically parsed sentences, ten gzip files, one million each |
| Silver | 600,000 | Unique mechanically parsed sentences selected for parser fine-tuning; overlap with copper must not be assumed absent |
| Gold | 5,000 | Manually corrected/verified parse trees: 4,500 development + 500 test; subset/annotation layer, not additive |
| Extra headings | 531,855 | Parsed heading sentences |
| Extra short | 1,652,938 | Parsed sentences with fewer than five tokens |

The CLARIN-IS record reports **10 million sentences** and **110,893,504 tokens**. The upstream README reports approximately **140 million words**. These are different unit conventions or snapshots and must remain a documented discrepancy until reconciled; do not convert one into the other. The 5,000 gold trees are an annotation layer, not additional corpus sentences.

## Licence and provenance

Both the upstream repository README and CLARIN-IS record identify **CC BY 4.0**. The upstream README explicitly requests attribution to **Miðeind ehf., Reykjavík, Iceland**. I see no specific licensing restriction or conflict in the published metadata that would justify excluding the corpus. The 2015–2021 text is described as extracted from Icelandic news and government websites; CC BY 4.0 is the publisher's stated licence for the corpus. Preserve attribution and the licence URI. The CLARIN-IS record and GitHub repository are public.

No privacy/anonymisation restriction is identified in the licence metadata reviewed here. Any content-level personal-data handling remains a separate preprocessing matter, not a reason to misclassify the CC BY licence.

## Pinned upstream snapshot and audit

The GitHub repository tree was inspected at commit `deb60c4b2775a4e0c709a6890c28678b913f44aa`. Large corpus files are stored using Git LFS; the ten copper files, silver file and two extra files appear as LFS pointers in the Git tree, so ordinary Git blob sizes are not the corpus sizes. The audit workflow hydrates the LFS objects and counts actual `((META` tree-record openers in each decompressed gzip file, with SHA-256 checksums and decompressed byte counts.

- Audit script: `scripts/audit_greynir_corpus.py`
- Workflow: `.github/workflows/audit-greynir-corpus.yml`
- Target revision: `deb60c4b2775a4e0c709a6890c28678b913f44aa`
- Audit result: pending

The copper/silver/extra partitions are reported separately. Do not add their counts to claim unique sentences until cross-partition text-level deduplication is performed.

## Current langid-32 acquisition

Staged records: **0**. This is a project-acquisition count, not an upstream availability count.

## Remaining checks

- Complete the pinned LFS content audit and compare actual tree-record counts with README figures.
- Reconcile the CLARIN token count with the README's approximate word count without conflating units.
- If this source is later acquired, retain publisher attribution, CC BY 4.0 URI, release/revision and source URLs.
