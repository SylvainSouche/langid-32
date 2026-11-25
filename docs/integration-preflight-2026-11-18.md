# Integration preflight — 18 November 2026

This note records a direct schema/provenance inspection of the completed GitHub Actions artifacts. It is a technical preflight, not a rights clearance and not a merged-corpus report.

## Artifacts inspected

| Component | Run / artifact | Rows | Result |
|---|---:|---:|---|
| Historical multisource v5 | [43950037392](https://github.com/SylvainSouche/langid-32/actions/runs/43950037392) / 14266897039 | 640,000 | Required merge fields and private provenance are present. Its DGT-TM (91,539) and Tatoeba (31,791) rows are superseded by the refreshed artifacts below; retain only FineWeb/FineWeb2 rows from this artifact for a refreshed technical integration. |
| HF-hosted Common Voice 22.0 CC0 text pilot | Historical HF-only component: 259,352 | 259,352 | HF source revision `ae911de250fe9375d08e2daa2105b671d659d446`; CV22 rows retain `source_locale`, upstream `sentence_id`, per-locale TSV SHA-256 and repository revision. Croatian is excluded and remains an alternative-source gap. Earlier mixed-source artifacts have been deleted. |
| Tatoeba CC0 refresh | [44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591) / 14345216923 | 80,155 | Required merge fields and provenance are present. Manifest confirms only `sentences_CC0.csv` rows are emitted; base export is used only for translation grouping. |
| DGT-TM 2021 refresh | [44291075180](https://github.com/SylvainSouche/langid-32/actions/runs/44291075180) / 14421763101 | 120,000 | Required merge fields and provenance are present. New run completed successfully, including tests, official archive download, staging and artifact upload. |
| Waiting-source acquisition | [44241908630](https://github.com/SylvainSouche/langid-32/actions/runs/44241908630) / 14403758073 | 613,860 | **Not mergeable in its current form.** Every sampled row lacks `source_release`, `licence_id`, `text_origin` and `provenance`. The source-specific manifests contain archive/file hashes and aggregate counts, but those are not attached to the individual rows. |

## Exact defects found

### Waiting-source rows

The candidate rows emitted by `scripts/acquire_waiting_sources.py` contain only `text`, `language`, `source` and `group_id`. This applies to the Catalan, Icelandic, Norwegian, Korean, Arabic and FineWeb2 waiting-source members. The global merge requires the seven non-empty fields `text`, `language`, `source`, `source_release`, `group_id`, `licence_id` and `text_origin`; it also needs retained provenance for auditability.

Do not fix this by assigning a generic permissive licence or inventing source-document URLs. The correct repair is to change acquisition so each row carries, where available:

- exact source release or immutable revision;
- the source's actual licence/terms claim, kept distinct from a separate `rights_status` such as `hold` or `conditional`;
- archive/file SHA-256 and source file/member;
- source record/document identifier and stable group/split-group identifier;
- original URL, title, author/issuing body and date when the source actually supplies them;
- explicit missing-value/rights-review status when the source does not supply required attribution metadata.

For file-based inputs, a line number or hash of the extracted sentence is not a substitute for the original article/document identity where article-level rights or attribution may apply. Records that cannot be tied to the necessary upstream work must remain held or be excluded from any release-eligible merge.

### HF-hosted Common Voice CC0 revision and row provenance

The retained Common Voice source is the HF-hosted [fsicoli/common_voice_22_0](https://huggingface.co/datasets/fsicoli/common_voice_22_0), whose card declares CC0-1.0. The workflow fetches only validated transcript TSVs. Each CV22 candidate retains locale, sentence ID, immutable dataset revision and per-locale TSV SHA-256. Croatian rows are not retained; an alternative independent source is required for hr. The old mixed-source workflow has been removed and its artifacts have been deleted.

### Refreshed DGT-TM

The refreshed DGT-TM 2021 artifact is now confirmed complete: 120,000 rows, 5,000 per each of 24 EU official languages. The latest run is [44291075180](https://github.com/SylvainSouche/langid-32/actions/runs/44291075180), not the older 44121170635 reference. The sample carries document/TMX-member grouping and the Commission reuse decision identifier. The multisource builder now preserves the EUR-Lex NumDoc identifier from each TMX member and derives a lookup URL using the CELEX query parameter (the URL has not yet been HTTP-verified). It records NumDoc sector/year/type and provisionally classifies origin by sector; the sample `22020D0933` is in sector 2 (international agreements), not an ordinary EU legal act. It also records the DGT-TM 2021 release as the latest dataset update. The exact Commission source/date/ownership wording and the 2012 reference-paper citation are recorded in the source attribution register; the final release-level ATTRIBUTION file still needs to reproduce that notice.

## Integration decision

A refreshed global 34-label merge has **not** been run. The earlier gross planning baseline of 976,177 rows is simply the arithmetic combination of v5 FineWeb/FineWeb2 rows (after removing its superseded DGT/Tatoeba rows), the 259,352-row HF-hosted Common Voice CC0 pilot, refreshed Tatoeba and refreshed DGT-TM. It is not a unique-record count, not a source-quota result, and not a rights-cleared total.

The waiting-source 613,860 rows are not included in that baseline because the refreshed artifact is still running and has not yet been validated. The HF-hosted Common Voice provenance/revision repair is complete; Croatian is not included.

### Multisource merge implementation

The global merge now implements the current pool policy:

- 34 target labels.
- Global exact-text collision removal across languages; every occurrence of a cross-language collision is removed.
- Exact deduplication within each language across all inputs.
- Split assignment by `split_group_id`, preserving groups across languages.
- Per-source preferred share 30% and hard maximum 50% in each language/split bucket.
- 20,000-record core per language, split 80/10/10; a separate 10,000-record reserve per language, excluded from every group used in core and emitted without a train/validation/test split.
- Internal provenance sidecar counts explicit rights statuses; missing source-specific statuses receive a conservative hold/review status.

The builder `scripts/build_multisource_candidate.py` prepares current source artifacts, filters superseded DGT/Tatoeba rows from historical v5, normalizes component/config/file suffixes to dataset-level source families for quota accounting, and unifies Catalan-DPO `messages`/`chosen` records by their common dataset-row ID. Builder normalization tests and merge tests pass in CI. The candidate build itself has **not** yet been run.

The repository is public. GitHub allows users with repository read access to download Actions artifacts; previous workflows uploaded text-bearing candidate artifacts. Workflows have now been changed to upload metadata manifests only. See [public repository artifact policy](public-repository-artifact-policy.md). Do not upload another text-bearing artifact from this repository.

The metadata-only build workflow is now prepared at [build-multisource-candidate.yml](../.github/workflows/build-multisource-candidate.yml). It downloads the five pinned source artifacts, normalizes dataset-family names, preselects at most the number of rows that could survive the 50% hard cap, builds the 20k core/10k reserve, then deletes all text and source files from the runner before uploading only manifests and aggregate summaries. It is intentionally triggered by creating/updating `docs/trigger-multisource-build.txt` (or by manual workflow dispatch). Before triggering it, inspect the refreshed waiting-source run [44293866614](https://github.com/SylvainSouche/langid-32/actions/runs/44293866614), verify all six source-group outputs and row-level provenance. That run was started before the metadata-only workflow change and may still upload candidate text; its artifact must be checked when it finishes.

No Hugging Face upload or public release is authorised by this preflight.
