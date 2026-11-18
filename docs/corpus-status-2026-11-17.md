> **Historical report.** This report records the state on 17–18 November 2026. The canonical current source-by-source status is now [docs/source-register.md](source-register.md). In particular, the Korean government legal-portal/API route discussed in earlier drafts was not pursued and produced no acquired records. Do not use the old “Korean law API route” statements below as current acquisition plans.

# Corpus status — 2026-11-17

Status: **not publication-ready; no language currently release-cleared**.

This report distinguishes measured candidate counts from rights-cleared usable counts. Counts below come from completed GitHub Actions artifacts, not estimates. Candidate rows from separate artifacts have **not** been globally deduplicated against each other, so they must not be added together as a final corpus total.

## Completed measured artifacts

- Multisource candidate v5: GitHub Actions run [43950037392](https://github.com/SylvainSouche/langid-32/actions/runs/43950037392), artifact `multisource-candidate-v5-fineweb-en`, 640,000 rows across 32 labels, exactly 20,000 each. It is capped at 20k, not the current 30k target.
- Common Voice mixed text-only pilot: run [44095077926](https://github.com/SylvainSouche/langid-32/actions/runs/44095077926), artifact `common-voice-mixed-curated-text`, 261,076 selected rows across 34 labels. This is capped at 9,000 per label and is a pilot, not a release corpus.
- Both artifacts contain counts and provenance manifests. Neither is a final rights-cleared release.

### Multisource candidate v5: rows by source

| Language | Total | FineWeb2 | DGT-TM 2021 | Tatoeba CC0 | FineWeb |
|---|---:|---:|---:|---:|---:|
| bg | 20,000 | 16,001 | 3,999 | 0 | 0 |
| hr | 20,000 | 16,013 | 3,987 | 0 | 0 |
| cs | 20,000 | 15,996 | 4,002 | 2 | 0 |
| da | 20,000 | 16,013 | 3,963 | 24 | 0 |
| nl | 20,000 | 15,940 | 4,021 | 39 | 0 |
| en | 20,000 | 0 | 1,546 | 12,486 | 5,968 |
| et | 20,000 | 16,002 | 3,998 | 0 | 0 |
| fi | 20,000 | 15,077 | 3,766 | 1,157 | 0 |
| fr | 20,000 | 10,251 | 2,559 | 7,190 | 0 |
| de | 20,000 | 15,970 | 3,991 | 39 | 0 |
| el | 20,000 | 16,081 | 3,919 | 0 | 0 |
| hu | 20,000 | 15,992 | 4,008 | 0 | 0 |
| ga | 20,000 | 16,024 | 3,976 | 0 | 0 |
| it | 20,000 | 15,963 | 4,022 | 15 | 0 |
| lv | 20,000 | 15,990 | 4,010 | 0 | 0 |
| lt | 20,000 | 16,054 | 3,946 | 0 | 0 |
| mt | 20,000 | 16,011 | 3,989 | 0 | 0 |
| pl | 20,000 | 15,964 | 3,992 | 44 | 0 |
| pt | 20,000 | 16,021 | 3,966 | 13 | 0 |
| ro | 20,000 | 16,002 | 3,998 | 0 | 0 |
| sk | 20,000 | 15,999 | 4,001 | 0 | 0 |
| sl | 20,000 | 16,007 | 3,993 | 0 | 0 |
| es | 20,000 | 16,033 | 3,941 | 26 | 0 |
| sv | 20,000 | 15,889 | 3,946 | 165 | 0 |
| nb | 20,000 | 19,996 | 0 | 4 | 0 |
| nn | 20,000 | 20,000 | 0 | 0 | 0 |
| ru | 20,000 | 9,418 | 0 | 10,582 | 0 |
| ja | 20,000 | 19,998 | 0 | 2 | 0 |
| zh | 20,000 | 19,999 | 0 | 1 | 0 |
| ko | 20,000 | 20,000 | 0 | 0 | 0 |
| ar | 20,000 | 19,998 | 0 | 2 | 0 |
| tr | 20,000 | 20,000 | 0 | 0 | 0 |

Source totals in this candidate: FineWeb2 510,702; DGT-TM 91,539; Tatoeba CC0 31,791; FineWeb 5,968.\n\nA fresh official Tatoeba export/staging completed successfully in run [44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591), artifact [14345216923](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591). It contains 80,155 staged CC0 rows: en 41,230; ru 22,721; fr 14,182; fi 1,545; sv 208; nl 49; da 33; es 36; pl 57; de 45; pt 16; it 19; cs 4; nb 4; ja 2; ar 2; hu 1; zh 1. It adds no Catalan or Icelandic. These are pre-global-merge staging counts, not additive to the v5 counts.

**The 50% source ceiling fails in all 32 languages in this candidate.** FineWeb2 supplies about 80% in most EU classes, 100% in several non-EU classes; English is 62.4% Tatoeba and Russian is 52.9% Tatoeba. French is 51.3% FineWeb2. The source mix must be rebuilt; do not train or publish from this artifact as-is.

## Common Voice 22 / 27 text-only pilot

Counts below are selected rows after the pilot's own normalization, basic privacy-pattern exclusions, within-label deduplication and cross-label collision removal. The cap is 9,000. Croatian comes from the retained Common Voice 27 subset; other successful locales come from the HF Common Voice 22 conversion.

| Language | Selected | Language | Selected |
|---|---:|---|---:|
| bg | 9,000 | hr | 1,724 |
| is | 4,991 | ca | 9,000 |
| cs | 9,000 | da | 9,000 |
| nl | 9,000 | en | 9,000 |
| et | 9,000 | fi | 5,798 |
| fr | 9,000 | de | 9,000 |
| el | 6,625 | hu | 9,000 |
| ga | 1,450 | it | 9,000 |
| lv | 9,000 | lt | 9,000 |
| mt | 5,222 | pl | 9,000 |
| pt | 9,000 | ro | 9,000 |
| sk | 9,000 | sl | 4,061 |
| es | 9,000 | sv | 9,000 |
| nb | 3,768 | nn | 5,179 |
| ru | 9,000 | ja | 9,000 |
| zh | 9,000 | ko | 6,258 |
| ar | 9,000 | tr | 9,000 |

Total selected: 261,076. Icelandic and Catalan are present here but have no rows in the v5 multisource candidate. Ten classes are below the 9,000 pilot cap: hr, is, fi, el, ga, mt, sl, nb, nn and ko. Every class remains far below the 20,000 minimum. No pilot class reaches 20,000.

Pilot limitations: no train/validation/test split; no global deduplication against v5 or the refreshed Tatoeba/DGT staging; automated privacy patterns are not complete PII clearance; no human language/content review; source terms and immutable upstream revisions still need final verification. The HF CV22 download manifest did not return a resolved commit for Catalan, so that locale is not immutably pinned.

## Source rights and outstanding acquisition

- **FineWeb2 / FineWeb:** candidate v5 manifests identify ODC-By for the dataset/compilation, while explicitly leaving underlying web-source rights separate. These rows are on legal hold and cannot count toward a public redistributable corpus until the underlying text rights are established.
- **Tatoeba:** only `sentences_CC0.csv` rows are staged as CC0; the general export is not treated as CC0. The v5 candidate retained only 31,791 Tatoeba rows after merge. The fresh official export is being re-downloaded.
- **DGT-TM 2021:** attribution and Commission ownership/source conditions apply. The v5 candidate retained 91,539 rows. Preserve source/date and ownership notices; verify the exact redistribution terms before final corpus licensing.
- **Common Voice:** the pilot is text-only, with no audio or speaker identifiers. The source's CC0 claim does not by itself settle all contractual terms. Acceptance/terms must be tracked per locale; do not infer acceptance for every locale from another locale's acceptance.
- **Catalan:** TeMU-BSC has CC0-labelled constituent datasets, including candidate components reported at 93,691 and 155,990 sentences, but constituent provenance/waivers need checking individually. They have not been downloaded and curated in this run.
- **Icelandic:** 50,000 IGC2024 Filtered-1 candidates are staged from the CC BY 4.0 open-access portion (≈795M words); the 2026 paper distinguishes this from the ≈895M-word custom-licensed portion. Preserve tei_archive/tei_path/source/altered for attribution. Greynir's 4,930 historical parser gold/dev rows are excluded from the main candidate merge. IGC Filtered-2 is excluded because its custom terms prohibit raw-text republication.
- **Norwegian Bokmål/Nynorsk:** Målfrid 2026 inventories 1.89B and 170.2M tokens respectively under NLOD 2.0. The archives have not been downloaded/curated here; preserve database-right and attribution distinctions. The randomized Nynorsk corpus (3.3M sentences) is lemmatized/tagged and is not clean raw text.
- **Korean:** Korean Wikipedia was subsequently acquired as a 50,000-row technical candidate and remains on hold for CC BY-SA/GFDL obligations. NSMC has conflicting licence claims; NIKL remains unacquired because written redistribution approval is missing. The Korea.kr/Korean legal-portal route was not pursued.

## Actions launched 2026-11-17

Two source refresh workflows were triggered by commits to the watched workflow files:

- Tatoeba fresh official CC0/base export: [run 44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591) — **completed successfully**; 80,155 staged rows, artifact 14345216923.
- DGT-TM 2021 archive refresh and staging: [run 44121170635](https://github.com/SylvainSouche/langid-32/actions/runs/44121170635) — running when this report was written.

The repository's existing global integration workflow was also triggered twice ([44121162341](https://github.com/SylvainSouche/langid-32/actions/runs/44121162341), [44121170605](https://github.com/SylvainSouche/langid-32/actions/runs/44121170605)). Its current YAML downloads **fixed older artifact run IDs**, not the two fresh artifacts above. Treat those integration outputs as stale with respect to the refresh; the workflow needs refactoring before a refreshed, valid global merge can be claimed.

## Decision summary

At present:
- 0/34 languages have a verified, publication-ready count of 20,000.
- 0/34 meet the 30,000 target.
- 32/34 have a measured 20,000-row technical candidate, but every one violates the source-share ceiling and the dominant web-crawl rights remain unresolved.
- 34/34 have a Common Voice text-only pilot, but each is below 20,000 and the pilot is not globally deduplicated or fully rights-cleared.
- Icelandic and Catalan need additional non-Common-Voice sources.
- Norwegian needs the Målfrid extraction path; Korean needs a rights-cleared volume source.

No public HF dataset was uploaded.


## Follow-up staging — 18 November 2026

The following source-acquisition work completed after this report was first written. These are independent candidate artifacts, not a merged corpus:

- Waiting-source acquisition: [GitHub Actions run 44241908630](https://github.com/SylvainSouche/langid-32/actions/runs/44241908630), artifact 14403758073. It contains 613,860 candidate rows: Catalan 258,930; Icelandic 54,930; Bokmål 50,000; Nynorsk 50,000; Korean 50,000; Arabic 50,000; plus 50,000 FineWeb2 Catalan and 50,000 FineWeb2 Icelandic candidates included in the stated language totals. Treat the source-specific components and licence caveats in the acquisition manifest as controlling; these counts are not globally deduplicated against other staging artifacts.
- The waiting-source composition still exposes concentration risks: TeMU is a large share of the non-FineWeb2 Catalan candidates; IGC2024 dominates non-FineWeb2 Icelandic; Målfrid is the sole source in each current Norwegian batch; Korean Wikipedia is the sole Korean source; and the UN-derived source is the sole Arabic source. FineWeb2 rows remain on legal hold pending excerpt-level rights analysis.
- Tatoeba fresh CC0 staging: [run 44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591), artifact 14345216923, 80,155 rows.
- DGT-TM 2021 staging: [run 44121170635](https://github.com/SylvainSouche/langid-32/actions/runs/44121170635), 120,000 rows (5,000 per 24 EU official languages).

Do not add these counts to the v5 or Common Voice totals. No cross-artifact global merge has yet established unique usable records, source quotas, final splits or release rights.

The public rights-notice contact [abuse@souche.fr](mailto:abuse@souche.fr) has been published in the repository README and policy documents. A test message was sent and a short acknowledgement was received. The mailbox is configured in the maintainer's email client; formal monitoring and case-handling procedures remain a release gate.

The source-exclusion registry is now wired into the merge workflow. Rule loading validates scope-specific keys, and URL extraction accepts both nested provenance and top-level URL fields. The integration workflow's malformed path-filter entry was corrected. These code changes still require a successful CI run before the registry implementation can be considered validated end to end.


## Repository reconciliation — 18 November 2026

The canonical [source register](source-register.md) now supersedes the older desk-inventory narrative. It records every acquired/staged source, investigated-but-not-acquired source, failed Leipzig acquisition, and route explicitly not pursued. In particular, the Korean government legal portal and Korean Law Open Data API are marked **not pursued**; no data from either route is in the candidate artifacts.

The legacy `corpus-integrate-fineweb2.yml` workflow has been changed to manual-only and labelled as the historical 32-language v4 integration. It still references fixed old artifact IDs and must not be dispatched or mistaken for the current 34-language integration. No current global 34-language merge has yet been built.

The target label list, model defaults, parameter-count documentation and tests have been updated from 32 to 34 classes (Catalan and Icelandic added). GitHub Actions CI run [44282209777](https://github.com/SylvainSouche/langid-32/actions/runs/44282209777) was still installing dependencies when this note was written; test completion is not yet verified.


### 18 November 2026 — Catalan-DPO correction

The 30,790 Catalan-DPO-V2 rows in artifact 14403758073 were incorrectly assigned the Catalan label. The source card states a 40% Catalan / 60% English mix, the source schema has no row-level language field, and the acquisition code had no language-identification step. Sample inspection confirmed English text among the rows. All 30,790 rows are quarantined and excluded from Catalan totals and any merge. The acquisition workflow now skips DPO V2 until a separate language-filtered and provenance-preserving route exists. The historical waiting-source total of 613,860 therefore has 583,070 non-DPO technical candidates remaining; these are still not release-cleared.


### 18 November 2026 — source-exclusion registry enforcement

Three active source-dataset rules now quarantine the two Catalan-DPO-V2 components (20,772 chosen responses and 10,018 assistant messages) and the 4,930-row Greynir parser test/development sample. The multisource candidate builder applies this registry. The historical 613,860-row waiting-source artifact therefore yields 578,140 non-DPO, non-Greynir technical candidates before other quality, privacy and rights checks.


### 18 November 2026 — corrected waiting-source language totals

The 613,860-row historical artifact 14403758073 contains 50,000 FineWeb2 Catalan rows and 50,000 FineWeb2 Icelandic rows in a separate file. Correct historical language totals are Catalan 308,930 and Icelandic 104,930 (not 258,930 and 104,930 respectively), plus 50,000 each for Bokmål, Nynorsk, Korean and Arabic. After excluding 30,790 mixed-language DPO rows and 4,930 Greynir parser gold/development rows, 578,140 technical candidates remain: Catalan 278,140; Icelandic 100,000; and 50,000 each for Bokmål, Nynorsk, Korean and Arabic. This is an accounting correction to the old artifact, not a release-clearance decision.
