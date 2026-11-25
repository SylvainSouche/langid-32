# Source decisions — operational source of truth

**Updated: 25 November 2026**

This document and [`data/source-decisions.json`](../data/source-decisions.json) are authoritative for source inclusion/exclusion. Numeric targets and thresholds are defined only in [`config/langid32.toml`](../config/langid32.toml). The descriptive [source register](source-register.md) remains useful for audit measurements and rights/provenance detail.

## First-pass acquisition rule

**Stream up to the eligible-unique target configured for each individual source and language in [`config/langid32.toml`](../config/langid32.toml).**

This is a first-pass acquisition target, not a final corpus quota and not a candidate-selection quota. Read each source as a stream, apply its source-specific eligibility/quality filters and deduplication, and retain up to its configured eligible-unique target. Do not downsample a source to the abandoned smaller historical limits at acquisition.

The following old limits are explicitly abandoned:

| Source | Abandoned historical limit | Active target |
|---|---:|---|
| Leipzig News | 3,000 / language | See central config |
| Leipzig Wikipedia | 3,000 / language | See central config |
| DGT-TM | 5,000 / language | See central config |

Leipzig News and Leipzig Wikipedia are separate sources and each gets its own configured stream target. DGT-TM has its own configured target. The per-source target is not a family-wide cap and must not be interpreted as one. No general source-family cap is established by this register.

Candidate construction happens later. Its per-language targets, source-balance policy and split allocation must not be pushed backwards into acquisition as smaller scraping limits. In particular, do not use candidate preferred-share/hard-share values to decide how many rows to scrape from an upstream source.

## Inclusion and exclusion decisions for the six underfilled languages

| Language | Include in first-pass acquisition | Explicitly unavailable / excluded / held |
|---|---|---|
| Croatian (`hr`) | DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`hrv_Latn`, technical only); **MaCoCu-hr 2.0** | Common Voice has no Croatian locale. FineWeb2 remains on underlying-text rights hold for release. |
| Finnish (`fi`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; Tatoeba CC0; FineWeb2 (`fin_Latn`, technical only) | FineWeb2 remains on underlying-text rights hold for release. |
| Greek (`el`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`ell_Grek`, technical only) | FineWeb2 remains on underlying-text rights hold for release. |
| Maltese (`mt`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`mlt_Latn`, technical only); **MaCoCu-mt 2.0** | FineWeb2 remains on underlying-text rights hold for release. Korpus Malti is not a substitute for MaCoCu-mt. |
| Slovenian (`sl`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`slv_Latn`, technical only); **MaCoCu-sl 2.0**; **ParlaMint 4.0** | FineWeb2 remains on underlying-text rights hold for release. Do not double-count MaCoCu derivatives or overlapping parliamentary corpora as independent sources. |
| Icelandic (`is`) | Common Voice 22; IGC2024 Filtered-1; Leipzig News; Leipzig Wikipedia; FineWeb2 (`isl_Latn`, technical only); **ParlaMint 4.0**; **Greynir Copper and Silver** | IGC Filtered-2 is excluded under its custom terms. **Greynir Gold development/test is excluded; Copper/Silver are included.** FineWeb2 remains on underlying-text rights hold for release. |

The configured target means "up to the eligible unique entry count"; if a source contains fewer qualifying records, retain the available qualifying records and report the shortfall. It is not permission to fabricate or duplicate rows.

## Important Greynir correction

The previous active rule excluding source family `greynir` wholesale is too broad. The decision is partition-specific:

- Include the full LFS-backed **Copper** and **Silver** corpora.
- Exclude only the **Gold development/test** partition.
- Do not invent a shared family-wide cap for Copper and Silver.

## Other staged source families and rights holds

| Source | Candidate decision | Release/rights status |
|---|---|---|
| FineWeb v1 | Exclude | ODC-BY covers the compilation, not individual web-page excerpts |
| BSC-LT Legal Catalan-Spanish | Technical candidate only | Hold pending file- and constituent-level terms |
| Korean Wikipedia cleaned | Technical candidate only | Hold pending CC BY-SA/GFDL compatibility review |
| Målfrid 2026 | Technical candidate only | Hold pending database and third-party content review |
| TeMU-BSC CC0 component union | Include the README-scoped CC0/waived constituents | Source-level review remains; retain constituent-file provenance |
| Gaois Irish legislation TMX | Include Irish-side segments | CC BY 4.0 derivative; preserve DCU/Gaois attribution and review original legislation rights |
| UN Arabic-English Filtered | Include | CC BY 4.0; preserve derivative credit and mandatory UN acknowledgement |
| Catalan-DPO-V2 | Exclude | Hold pending a Catalan-only, source-traceable rights review |

The source registry is fail-closed: every candidate source identifier must have a rule in the central configuration. Explicitly excluded and unregistered sources are rejected before candidate family normalization. A rights hold may permit technical candidate use only where the source decision says so; it never implies release clearance.

## Rights and provenance remain separate

- FineWeb2 may be used in the technical candidate but remains on hold for release because underlying web-text rights are unresolved.
- IGC2024 Filtered-1 is the open-access CC BY 4.0 portion; preserve TEI/source provenance and attribution. Filtered-2 remains excluded under its custom terms.
- MaCoCu archives: preserve document URLs and paragraph quality/sensitive-information/language/heading flags.
- ParlaMint: preserve speaker refs/roles, session/document IDs, dates and party metadata.
- Greynir Copper/Silver: preserve source-document provenance and attribute Miðeind ehf.
- DGT-TM: preserve NumDoc/member provenance and Commission attribution.

## Current pipeline discrepancy

The latest pre-refresh diagnostics show Leipzig News and Wikipedia at approximately 3,000 each and DGT at approximately 5,000. Those figures are obsolete historical caps, not the current sourcing decision. The acquisition scripts now read active targets from config/langid32.toml. The refreshed Leipzig and DGT first-pass acquisitions are verified; see [the reconciled acquisition status](acquisition-status-2026-11-25.md). Other approved but missing sources (MaCoCu, ParlaMint, Greynir Copper/Silver) remain separate integration tasks.

Never encode source decisions only in a workflow matrix, script default or historical report. Update this register first, then make the acquisition implementation conform to it.
