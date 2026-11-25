# Source decisions — operational source of truth

**Updated: 25 November 2026**

This document records the operational decisions on whether a source is to be ingested into the technical candidate. The machine-readable register is [`data/source-decisions.json`](../data/source-decisions.json). It is authoritative for inclusion/exclusion decisions and takes precedence over older discovery notes and any contradictory blanket exclusion. The descriptive [source register](source-register.md) remains useful for audit measurements and rights/provenance detail.

## Decision rule

- **Include** means the source is approved for candidate ingestion, subject to its stated adapter, filtering, provenance and family cap.
- **Include — technical only** means it may appear in the technical candidate but must not be represented as rights-cleared or release-eligible.
- **Approved, not yet integrated** means the decision is to take the source; absence from the current candidate is an implementation failure, not a decision to exclude it.
- **Exclude** must be narrow and explicit. An exclusion of one partition must never be expanded silently to the entire dataset family.
- Candidate ingestion and public-release rights clearance are separate decisions.
- Source-family caps aggregate all components/configurations/partitions belonging to that family: **20,000 records per language and family**. The preferred source share is 30%; the hard ceiling is 50%.

## Decisions for the six underfilled languages

| Language | Include in candidate | Explicitly excluded / held |
|---|---|---|
| Croatian (`hr`) | DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`hrv_Latn`, technical only); **MaCoCu-hr 2.0** | Common Voice has no Croatian locale. FineWeb2 remains on underlying-text rights hold for release. |
| Finnish (`fi`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; Tatoeba CC0; FineWeb2 (`fin_Latn`, technical only) | FineWeb2 remains on underlying-text rights hold for release. |
| Greek (`el`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`ell_Grek`, technical only) | FineWeb2 remains on underlying-text rights hold for release. |
| Maltese (`mt`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`mlt_Latn`, technical only); **MaCoCu-mt 2.0** | FineWeb2 remains on underlying-text rights hold for release. Korpus Malti is not a substitute for MaCoCu-mt. |
| Slovenian (`sl`) | Common Voice 22; DGT-TM 2021; Leipzig News; Leipzig Wikipedia; FineWeb2 (`slv_Latn`, technical only); **MaCoCu-sl 2.0**; **ParlaMint 4.0** | FineWeb2 remains on underlying-text rights hold for release. Do not double-count MaCoCu derivatives or overlapping parliamentary corpora as independent sources. |
| Icelandic (`is`) | Common Voice 22; IGC2024 Filtered-1; Leipzig News; Leipzig Wikipedia; FineWeb2 (`isl_Latn`, technical only); **ParlaMint 4.0**; **Greynir Copper and Silver** | IGC Filtered-2 is excluded under its custom terms. **Greynir Gold development/test is excluded; Copper/Silver are included.** FineWeb2 remains on underlying-text rights hold for release. |

## Important Greynir correction

The previous active rule excluding source family `greynir` wholesale is too broad and contradicts the decision recorded here. The decision is partition-specific:

- Include the full LFS-backed **Copper** and **Silver** corpora.
- Exclude only the **Gold development/test** partition.
- Copper and Silver share one 20,000-record Greynir family cap.

The current candidate adapter still needs partition-aware source labels and filtering before the old broad exclusion can safely be removed. Do not re-run candidate assembly with the old 4,930-row Gold/dev sample allowed through. The blanket exclusion is an implementation defect to replace, not the current source-selection decision.

## Current pipeline discrepancy (run 45581250730)

The candidate diagnostics show that the approved new sources are not being supplied to the builder: MaCoCu-hr, MaCoCu-mt, MaCoCu-sl, ParlaMint-4.0, Greynir Copper and Greynir Silver are all absent. Icelandic IGC2024 contributes only 1,478 rows after the current intake filters. The source decisions above are therefore not reflected in the current build.

See the JSON file for the per-source machine-readable decision, integration status, licence/rights distinction and language mapping. Update this register when a decision changes; never encode a source decision only in an acquisition script, workflow matrix or historical report.
