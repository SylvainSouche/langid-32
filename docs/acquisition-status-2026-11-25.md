# Acquisition and corpus status — 25 November 2026

Branch: `recovery/fix-acquisition-20261124`

## Newly verified first-pass acquisitions

| Source | Languages | Verified rows | Evidence |
|---|---:|---:|---|
| Leipzig News | hr, fi, el, mt, sl, is | 120,000 | Run [45600192491](https://github.com/SylvainSouche/langid-32/actions/runs/45600192491), artifact `leipzig-first-pass-45600192491` |
| Leipzig Wikipedia | hr, fi, el, mt, sl, is | 120,000 | Same run; 20,000 each language |
| DGT-TM 2021 | hr, fi, el, mt, sl | 100,000 | Run [45600139292](https://github.com/SylvainSouche/langid-32/actions/runs/45600139292), artifact `dgt-tm-2021-first-pass-45600139292` |
| Tatoeba CC0 | fi | 1,545 | Refreshed in run [45600118583](https://github.com/SylvainSouche/langid-32/actions/runs/45600118583); artifact contains JSONL and manifest |

**340,000 newly acquired Leipzig and DGT records.** Tatoeba was re-staged with the same 1,545 Finnish rows already present in the previous intake; this refresh fixes the artifact to include the actual JSONL as well as the manifest. The Leipzig manifest confirms 12/12 source-language slots, 20,000 per slot and no missing archives. The DGT manifest confirms 20,000 per language across the five approved languages, with 16,000 train, 2,000 validation and 2,000 test records per language. The DGT artifact contains both the staged JSONL and its provenance manifest.

## Current per-language source intake

The table below is a reconciled *pre-global-dedup source-intake count*, not a final corpus count. It starts from source-intake diagnostics in candidate run 45581250730, removes the obsolete Leipzig and DGT samples, and substitutes the newly verified 240,000 Leipzig and 100,000 DGT rows. It is an exact arithmetic reconciliation of the reported intake manifests; the candidate inputs have not yet been rebuilt with the new artifacts.

| Language | Retained source rows | Gap to 35k candidate pool |
|---|---:|---:|
| Arabic (ar) | 59,715 | 0 |
| Bulgarian (bg) | 36,001 | 0 |
| Catalan (ca) | 61,656 | 0 |
| Czech (cs) | 36,000 | 0 |
| Danish (da) | 34,814 | 186 |
| German (de) | 36,015 | 0 |
| Greek (el) | 84,754 | 0 |
| English (en) | 45,968 | 0 |
| Spanish (es) | 36,069 | 0 |
| Estonian (et) | 26,664 | 8,336 |
| Finnish (fi) | 83,235 | 0 |
| French (fr) | 44,433 | 0 |
| Irish (ga) | 37,474 | 0 |
| Croatian (hr) | 76,532 | 0 |
| Hungarian (hu) | 35,993 | 0 |
| Icelandic (is) | 48,926 | 0 |
| Italian (it) | 35,982 | 0 |
| Japanese (ja) | 37,488 | 0 |
| Korean (ko) | 33,761 | 1,239 |
| Lithuanian (lt) | 36,054 | 0 |
| Latvian (lv) | 35,990 | 0 |
| Maltese (mt) | 82,600 | 0 |
| Norwegian Bokmål (nb) | 40,230 | 0 |
| Norwegian Nynorsk (nn) | 43,950 | 0 |
| Dutch (nl) | 35,989 | 0 |
| Polish (pl) | 36,021 | 0 |
| Portuguese (pt) | 36,037 | 0 |
| Romanian (ro) | 29,755 | 5,245 |
| Russian (ru) | 49,418 | 0 |
| Slovak (sk) | 30,263 | 4,737 |
| Slovenian (sl) | 82,185 | 0 |
| Swedish (sv) | 36,097 | 0 |
| Turkish (tr) | 40,000 | 0 |
| Chinese (zh) | 40,000 | 0 |
| **Total** | **1,546,069** | — |

- 29 languages meet the configured 35,000 candidate-pool floor in this reconciled intake.
- Five remain below it: Danish, Estonian, Korean, Romanian and Slovak.
- All 34 currently exceed the configured final target in *raw intake count*, but this does not establish that they will still meet it after cross-source deduplication, source-share constraints and quality checks.
- The global deduplicated count must be regenerated from the reconciled inputs. The prior 1,525,786 post-dedup count belongs to the obsolete source snapshot and is no longer current.

## Still missing from the integrated candidate inputs

Approved sources not yet wired into candidate construction:

- MaCoCu-hr 2.0
- MaCoCu-mt 2.0
- MaCoCu-sl 2.0
- ParlaMint 4.0 for Icelandic and Slovenian
- Greynir Copper and Silver for Icelandic

FineWeb2 remains technical-candidate-only while underlying web-text rights are unresolved. Do not treat technical acquisition as release clearance.

## Pipeline sequencing

- Leipzig and DGT acquisitions are verified.
- Candidate construction has **not** been rerun on the reconciled inputs.
- JQL remains pending; when run, it annotates/diagnoses only and cannot filter, rank or remove sentences.
- The recovery and candidate-build workflows have been switched to manual dispatch to prevent source-code/config edits from launching downstream stages prematurely.
- The next task is to integrate the approved missing sources, then rebuild and globally deduplicate the candidate pool. No full end-to-end run has been started.
