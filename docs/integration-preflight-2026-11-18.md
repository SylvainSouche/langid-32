# Integration preflight — 18 November 2026

This note records a direct schema/provenance inspection of the completed GitHub Actions artifacts. It is a technical preflight, not a rights clearance and not a merged-corpus report.

## Artifacts inspected

| Component | Run / artifact | Rows | Result |
|---|---:|---:|---|
| Historical multisource v5 | [43950037392](https://github.com/SylvainSouche/langid-32/actions/runs/43950037392) / 14266897039 | 640,000 | Required merge fields and private provenance are present. Its DGT-TM (91,539) and Tatoeba (31,791) rows are superseded by the refreshed artifacts below; retain only FineWeb/FineWeb2 rows from this artifact for a refreshed technical integration. |
| Common Voice mixed text pilot | [44293665775](https://github.com/SylvainSouche/langid-32/actions/runs/44293665775) / 14423311681 | 261,076 | All 34 requested locale files resolve to immutable HF dataset revision `ae911de250fe9375d08e2daa2105b671d659d446`; CV22 rows now retain `source_locale`, upstream `sentence_id`, per-locale TSV SHA-256 and repo revision. Croatian CV27 rows carry verified archive/TSV hashes and an explicit locale-terms hold; no upstream sentence ID was retained for those rows. |
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

### Common Voice revision and row provenance

The refreshed Common Voice run [44293665775](https://github.com/SylvainSouche/langid-32/actions/runs/44293665775) now resolves all 34 requested locale files to one immutable dataset revision: `ae911de250fe9375d08e2daa2105b671d659d446`. The candidate JSONL carries locale, sentence ID, file SHA-256 and revision in each CV22 row. The Croatian CV27 subset carries a verified source-archive SHA-256 and validated-sentences TSV SHA-256; its upstream sentence ID was not retained, so its group ID remains a candidate-record hash. Locale-specific terms and the no-rehosting restriction still require separate checks; the Romanian acceptance must not be generalized to Croatian or other locales.

### Refreshed DGT-TM

The refreshed DGT-TM 2021 artifact is now confirmed complete: 120,000 rows, 5,000 per each of 24 EU official languages. The latest run is [44291075180](https://github.com/SylvainSouche/langid-32/actions/runs/44291075180), not the older 44121170635 reference. The sample carries document/TMX-member grouping and the Commission reuse decision identifier; the exact mandatory ownership/source notice still needs to be copied from the official notice before publication.

## Integration decision

A refreshed global 34-label merge has **not** been run. The earlier gross planning baseline of 977,901 rows is simply the arithmetic combination of v5 FineWeb/FineWeb2 rows (after removing its superseded DGT/Tatoeba rows), the Common Voice pilot, refreshed Tatoeba and refreshed DGT-TM. It is not a unique-record count, not a source-quota result, and not a rights-cleared total.

The waiting-source 613,860 rows are not included in that baseline because their row schema and provenance are incomplete. The Common Voice provenance/revision repair is complete. The next implementation step is to inspect the refreshed waiting-source acquisition artifact, verify that the new row-level metadata is genuinely preserved, then run global normalization, cross-source deduplication, cross-language collision removal, group-aware splitting and per-language source caps. Rights-held sources must remain explicitly marked as held; a technically mergeable record is not thereby release-eligible.

No Hugging Face upload or public release is authorised by this preflight.
