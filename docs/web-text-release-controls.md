# Web-text release controls (HPLT-style)

This document translates the HPLT packaging-only licensing and notice-and-takedown approach into operational controls for langid-32. HPLT's published model states that it does not own extracted text, dedicates only the packaging under CC0, asks claimants to identify the work and corpus material, and removes affected sources from a subsequent release. See the [HPLT dataset terms](https://hplt-project.org/datasets/v2.0) and [HPLT3.0 dataset card](https://huggingface.co/datasets/HPLT/HPLT3.0).

## Required before release

- [ ] Publish a monitored rights-notice contact channel and assign an accountable maintainer.
- [ ] Include the packaging-only terms and takedown policy in the dataset card and every downloadable release.
- [ ] Do not set Hugging Face's dataset licence metadata to plain `cc0-1.0` if the repository contains third-party web text. Use an accurately described custom/other licence field and explain that CC0 covers packaging only.
- [ ] Retain source-level provenance sufficient to locate and remove affected material: source dataset, crawl/archive, URL or stable source identifier, source document ID, retrieval/release information, and derived record IDs.
- [ ] Keep the detailed provenance ledger private where it contains sensitive URLs, personal data or operational information; publish only the fields necessary for transparency and attribution.
- [ ] Maintain a source/document exclusion registry and apply it before every release build.
- [ ] Ensure exclusion cascades through duplicates, language labels, translations/segments, and train/validation/test splits.
- [ ] Verify that an exclusion rebuild removes all affected records and updates counts/manifests.
- [ ] Preserve separate licence and attribution treatment for independently licensed sources (for example CC BY or CC BY-SA). The packaging-only statement must not erase those obligations.
- [ ] Keep the release marked not publication-ready until all mandatory controls are implemented and tested.

## Exclusion registry format

The release pipeline should consume a versioned UTF-8 CSV or JSONL registry with at least:

- `source_key`: stable internal source/document key;
- `url_sha256`: SHA-256 of the canonical source URL (avoid exposing raw URL in the public registry where unnecessary);
- `source_url`: restricted/private field where needed for operational matching;
- `reason_code`: rights_notice, privacy_notice, provider_restriction, legal_review, or source_unknown;
- `case_id`: internal case identifier, not claimant identity;
- `effective_at`: timestamp;
- `scope`: document, URL, domain, archive-batch, or source-dataset;
- `status`: active or superseded.

The registry must not contain claimant contact details or unnecessary personal data. A source-level exclusion is preferable to a domain-wide exclusion unless the evidence or notice requires broader scope.

## Current implementation status

Policy documentation is being established first. The public notice contact, automated registry enforcement, source-to-output traceability tests, and release-card metadata changes are not yet confirmed operational. Therefore this policy does not authorise publication of the current FineWeb/FineWeb2 candidates. They remain technical candidates on legal hold until these controls and the broader release review are complete.
