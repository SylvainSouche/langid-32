# Public repository and Actions artifact handling

**Repository:** https://github.com/SylvainSouche/langid-32  
**Checked:** 18 November 2026  
**Observed repository visibility:** public (`private=false`).

## Why this matters

GitHub's documentation says people signed in to GitHub who have read access to a repository can download its workflow artifacts. Its REST API documentation also says artifact endpoints can be used without authentication when requesting public resources:

- [Downloading workflow artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
- [REST API endpoints for GitHub Actions artifacts](https://docs.github.com/en/rest/actions/artifacts)

Because this repository is public, Actions artifacts containing candidate JSONL, Parquet, archives or other source text must be treated as publicly accessible. An artifact upload is not the same thing as a formal dataset release, but it can still make source excerpts available to third parties. That is inappropriate for sources whose underlying-text rights or redistribution terms remain unresolved.

## Policy applied on 18 November 2026

For future runs in this public repository:

- Upload metadata manifests, hashes, counts, source revisions, quality summaries and rights-status reports only.
- Do not upload candidate sentence JSONL, internal provenance JSONL, Parquet datasets, downloaded archives or other source text.
- Candidate text may be processed transiently on the Actions runner for technical validation, but must be deleted from the runner workspace before the job ends and must not be included in an artifact.
- Do not upload a prepared Hugging Face dataset package until every included record has passed its source-level rights gate and the intended destination/release terms have been approved.

Workflow changes made to implement metadata-only artifacts include:

- `acquire-waiting-sources.yml`
- `common-voice-cc0-hf.yml`
- `dgt-tmx-ingest.yml`
- `tatoeba-ingest.yml`
- `fineweb-extract.yml`
- `corpus-integrate-fineweb.yml`
- `corpus-integrate-fineweb2.yml`
- the FineWeb2 assemble, buffer, extract, extract-all, top-up and Turkish/Chinese buffer workflows
- `prepare-hf-dataset.yml`
- `acquire-leipzig-corpora.yml`

The Leipzig REST API probe uploads only OpenAPI, corpus catalogue and metadata-only probe reports; it does not retain sentence text.

## Existing artifacts requiring an owner decision

Earlier workflow runs already uploaded text-bearing artifacts before this policy was applied. The following are known examples, not an exhaustive inventory:

| Workflow run | Artifact | Contents |
|---|---:|---|
| [43950037392](https://github.com/SylvainSouche/langid-32/actions/runs/43950037392) | 14266897039 | Historical multisource candidate v5 records |
| [44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591) | 14345216923 | Tatoeba CC0 staged rows |
| [44291075180](https://github.com/SylvainSouche/langid-32/actions/runs/44291075180) | 14421763101 | DGT-TM 2021 staged translation units |
| [44241908630](https://github.com/SylvainSouche/langid-32/actions/runs/44241908630) | 14403758073 | Historical waiting-source candidate rows |

Run [44293866614](https://github.com/SylvainSouche/langid-32/actions/runs/44293866614) was still running when this note was written and was started before the metadata-only workflow change. Its original workflow definition may still upload candidate text. Its completion and artifact contents must be checked.

**Completed:** the one-off cleanup workflow [44315309698](https://github.com/SylvainSouche/langid-32/actions/runs/44315309698) deleted all three retired Common Voice artifacts: 14319841407 (Croatian subset), 14332474956 (mixed pilot) and 14423311681 (mixed-source metadata). Follow-up artifact-list queries for the three originating runs returned no remaining artifacts. The other non-Common-Voice artifacts listed above are unchanged.

## Important distinction

The metadata-only policy does not retrospectively undo earlier artifact downloads. It prevents future runs from repeating the exposure. Existing source-level rights holds remain in force, regardless of whether an artifact has expired or been deleted.
