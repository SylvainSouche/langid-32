# Acquisition and corpus status — 25 November 2026

Branch: `recovery/fix-acquisition-20261124`

## Newly verified first-pass acquisitions

| Source | Languages | Verified rows | Evidence |
|---|---:|---:|---|
| Leipzig News | hr, fi, el, mt, sl, is | 120,000 | Run [45600192491](https://github.com/SylvainSouche/langid-32/actions/runs/45600192491), artifact `leipzig-first-pass-45600192491` |
| Leipzig Wikipedia | hr, fi, el, mt, sl, is | 120,000 | Same run; 20,000 each language |
| DGT-TM 2021 | hr, fi, el, mt, sl | 100,000 | Run [45600139292](https://github.com/SylvainSouche/langid-32/actions/runs/45600139292), artifact `dgt-tm-2021-first-pass-45600139292` |
| Tatoeba CC0 | fi | 1,545 | Refreshed in run [45600118583](https://github.com/SylvainSouche/langid-32/actions/runs/45600118583); artifact contains JSONL and manifest |

**340,000 newly acquired Leipzig and DGT records.** Tatoeba was re-staged with the same 1,545 Finnish rows already present in the previous intake; the refresh fixes the artifact to include the actual JSONL as well as the manifest.

The Leipzig manifest confirms all 12 source-language slots completed, with 20,000 rows per slot and no missing archives. The DGT manifest confirms 20,000 rows per language across the five approved languages, with 16,000 train, 2,000 validation and 2,000 test records per language. The DGT artifact contains both staged JSONL and provenance manifest.

## Reconciled per-language intake

This is a *provisional pre-global-dedup source-intake count*, not a final corpus count. It starts from source-intake diagnostics in candidate run 45581250730 and applies the current source decisions:

- remove obsolete Leipzig samples outside the six approved Leipzig languages, then substitute the new 240,000-row Leipzig acquisition;
- remove obsolete DGT samples outside the five approved DGT languages, then substitute the new 100,000-row DGT acquisition;
- retain FineWeb2 only for its six approved technical-candidate languages (hr, fi, el, mt, sl, is);
- retain the approved Tatoeba CC0 Finnish source.

The candidate inputs have not yet been rebuilt from these reconciled sources. Counts below are therefore an exact arithmetic reconciliation of the previous intake diagnostics and verified acquisition manifests, before cross-source deduplication.

| Language | Raw source rows | Gap to final 25k | Gap to candidate pool 35k |
|---|---:|---:|---:|
| Arabic (ar) | 39,715 | 0 | 0 |
| Bulgarian (bg) | 20,000 | 5,000 | 15,000 |
| Catalan (ca) | 59,144 | 0 | 0 |
| Czech (cs) | 20,004 | 4,996 | 14,996 |
| Danish (da) | 18,801 | 6,199 | 16,199 |
| German (de) | 20,045 | 4,955 | 14,955 |
| Greek (el) | 84,754 | 0 | 0 |
| English (en) | 45,968 | 0 | 0 |
| Spanish (es) | 20,036 | 4,964 | 14,964 |
| Estonian (et) | 10,662 | 14,338 | 24,338 |
| Finnish (fi) | 83,235 | 0 | 0 |
| French (fr) | 34,182 | 0 | 818 |
| Irish (ga) | 21,450 | 3,550 | 13,550 |
| Croatian (hr) | 76,532 | 0 | 0 |
| Hungarian (hu) | 20,001 | 4,999 | 14,999 |
| Icelandic (is) | 48,926 | 0 | 0 |
| Italian (it) | 20,019 | 4,981 | 14,981 |
| Japanese (ja) | 17,490 | 7,510 | 17,510 |
| Korean (ko) | 13,761 | 11,239 | 21,239 |
| Lithuanian (lt) | 20,000 | 5,000 | 15,000 |
| Latvian (lv) | 20,000 | 5,000 | 15,000 |
| Maltese (mt) | 82,600 | 0 | 0 |
| Norwegian Bokmål (nb) | 20,230 | 4,770 | 14,770 |
| Norwegian Nynorsk (nn) | 23,950 | 1,050 | 11,050 |
| Dutch (nl) | 20,049 | 4,951 | 14,951 |
| Polish (pl) | 20,057 | 4,943 | 14,943 |
| Portuguese (pt) | 20,016 | 4,984 | 14,984 |
| Romanian (ro) | 13,753 | 11,247 | 21,247 |
| Russian (ru) | 40,000 | 0 | 0 |
| Slovak (sk) | 14,264 | 10,736 | 20,736 |
| Slovenian (sl) | 82,185 | 0 | 0 |
| Swedish (sv) | 20,208 | 4,792 | 14,792 |
| Turkish (tr) | 20,000 | 5,000 | 15,000 |
| Chinese (zh) | 20,001 | 4,999 | 14,999 |
| **Total** | **1,112,038** | — | — |

- Only **11 languages** currently reach the configured final target in raw intake.
- Only **10 languages** reach the configured candidate-pool floor.
- **23 languages remain below the final target** even before global deduplication and source-share constraints. Their gaps are shown above.
- The old post-global-dedup count of 1,525,786 belongs to the obsolete source snapshot and is not a current unique count. The reconciled inputs must be globally deduplicated again before a definitive unique total can be reported.

## Approved sources still missing from integrated candidate inputs

- MaCoCu-hr 2.0
- MaCoCu-mt 2.0
- MaCoCu-sl 2.0
- ParlaMint 4.0 for Icelandic and Slovenian
- Greynir Copper and Silver for Icelandic

These sources are already registered in the central configuration with their approved language scopes and first-pass targets, but their adapters/intake are not yet integrated.

FineWeb2 remains technical-candidate-only while underlying web-text rights are unresolved. Technical acquisition does not imply release clearance. FineWeb2 rows outside its approved six-language scope are now filtered before candidate source-family normalization.

## Pipeline sequencing

- Leipzig and DGT first-pass acquisitions are verified.
- Tatoeba CC0 refresh is verified and now retains both JSONL and manifest.
- Candidate construction has **not** been rerun on the reconciled inputs.
- JQL remains pending; when run, it annotates/diagnoses only and cannot filter, rank or remove sentences.
- Candidate construction and the full production pipeline are manual-only until the missing approved sources are integrated and the intake review is complete.
