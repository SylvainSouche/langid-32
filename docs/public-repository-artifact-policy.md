# Public repository and Actions artifact handling

**Repository:** https://github.com/SylvainSouche/langid-32  
**Updated:** 26 November 2026  
**Observed repository visibility:** public (`private=false`).

## Why this matters

GitHub's documentation says people signed in to GitHub who have read access to a repository can download its workflow artifacts. Its REST API documentation also says artifact endpoints can be used without authentication when requesting public resources:

- [Downloading workflow artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
- [REST API endpoints for GitHub Actions artifacts](https://docs.github.com/en/rest/actions/artifacts)

Because this repository is public, Actions artifacts containing candidate JSONL, Parquet, archives or other source text must be treated as publicly accessible. An artifact upload is not the same thing as a formal dataset release, but it can still make source excerpts available to third parties. That is inappropriate for sources whose underlying-text rights or redistribution terms remain unresolved.

## Original metadata-only policy applied on 18 November 2026

The 18 November policy prohibited uploading plaintext candidate JSONL, internal provenance JSONL, Parquet datasets, downloaded archives or other source text. That prohibition remains in force for **plaintext** artifacts and for all legacy/standalone workflows that do not implement the encrypted-checkpoint protocol below.

Metadata-only artifacts may be uploaded in plaintext. This includes hashes, counts, source revisions, rights-status reports, sentence IDs, numeric JQL scores and non-text quality flags, provided they contain no sentence text or identifying contributor data.

## Current staged-pipeline encrypted-artifact exception (26 November 2026)

The later `docs/pipeline-contract.md` defines a specific exception for the staged corpus and JQL workflows. The repository remains public, so every Actions artifact is still publicly downloadable. Text-bearing data is therefore allowed in a new staged-pipeline artifact **only as authenticated ciphertext**:

- `scripts/checkpoint.py` packages the `input/` and `out/` working trees and encrypts the archive in 64 MiB chunks with AES-256-GCM.
- The AES key is derived from the GitHub Actions secret `LANGID32_CHECKPOINT_KEY` using SHA-256. The secret is not committed, printed, written into a manifest or uploaded. It must be a high-entropy random value of at least 32 characters; the workflow checks the minimum length before acquisition.
- Text-bearing acquisition, candidate, full JQL assessment, shard and pruned-pool artifacts are uploaded only as encrypted checkpoint files. No plaintext sentence JSONL, text-bearing Parquet, source archive or decrypted checkpoint is uploaded.
- Plaintext source/candidate/assessment workspaces are removed in cleanup steps after artifact upload, including on failed jobs. The waiting-source Hugging Face cache is kept inside the workspace and removed by the same cleanup. Scoring model weights may remain in the job-local cache because they are not corpus text.
- Plaintext metadata-only outputs remain allowed: the preflight manifest, sentence-boundary flags and per-shard rating files contain identifiers/counts/scores/statuses, not sentence text.
- Acquisition and candidate checkpoints use the configured short retention period (7 days); the full and pruned JQL encrypted artifact uses the configured artifact retention period (30 days).
- Ciphertext is public and encryption is not repository access control. Anyone can download the encrypted bytes; decryption requires the separate secret. If that secret is disclosed or weak, the confidentiality guarantee is lost.

The four pinned historical snapshots listed below are an explicit, previously accepted exception: they are existing, unencrypted source artifacts. They are downloaded from their pinned successful runs, validated, and included in the new pipeline's encrypted checkpoint before any new artifact upload. They are not re-uploaded as plaintext.

This exception applies only to `.github/workflows/langid32-pipeline.yml` and its downstream `.github/workflows/score-jql-assessment.yml`. It does not relax the metadata-only rule for unrelated workflows or authorize publication/re-hosting of source text.

## Existing artifacts requiring an owner decision

Earlier workflow runs already uploaded text-bearing artifacts before this policy was applied. The following are known examples, not an exhaustive inventory:

| Workflow run | Artifact | Contents |
|---|---:|---|
| [43950037392](https://github.com/SylvainSouche/langid-32/actions/runs/43950037392) | 14266897039 | Historical multisource candidate v5 records |
| [44121162591](https://github.com/SylvainSouche/langid-32/actions/runs/44121162591) | 14345216923 | Tatoeba CC0 staged rows |
| [44291075180](https://github.com/SylvainSouche/langid-32/actions/runs/44291075180) | 14421763101 | DGT-TM 2021 staged translation units |
| [44241908630](https://github.com/SylvainSouche/langid-32/actions/runs/44241908630) | 14403758073 | Historical waiting-source candidate rows |
| [44315031026](https://github.com/SylvainSouche/langid-32/actions/runs/44315031026) | 14431583044 | HF-hosted CC0 Common Voice source manifest and aggregate report only; no sentence text |
| [44316263013](https://github.com/SylvainSouche/langid-32/actions/runs/44316263013) | 14432198714 | Dataset-card, licensing, source-register and attribution documentation only; no dataset text |

Run [44293866614](https://github.com/SylvainSouche/langid-32/actions/runs/44293866614) completed successfully; a follow-up artifact query returned no artifacts. It is not an outstanding text-bearing artifact.

**Completed:** the one-off cleanup workflow [44315309698](https://github.com/SylvainSouche/langid-32/actions/runs/44315309698) deleted all three retired Common Voice artifacts: 14319841407 (Croatian subset), 14332474956 (mixed pilot) and 14423311681 (mixed-source metadata). Follow-up artifact-list queries for the three originating runs returned no remaining artifacts. The other non-Common-Voice artifacts listed above are unchanged.

## Important distinction

The metadata-only policy does not retrospectively undo earlier artifact downloads. It prevents future runs from repeating the exposure. Existing source-level rights holds remain in force, regardless of whether an artifact has expired or been deleted.
