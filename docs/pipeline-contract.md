# langid-32 pipeline contract and execution protocol

**Status:** audit baseline, 2026-11-26. This document records the agreed operational contract and the implementation state observed on `main` at commit `1e6f8319b6cfd102c650c3b516cc4583d0d42730`. It is not a claim that the pipeline currently satisfies the contract.

**Authority:** this is the single pipeline-level source of truth for stage order, acceptance criteria, execution constraints and the rule for triggering a run. Numeric acquisition/JQL settings remain centralized in `config/langid32.toml`; source-specific rights and inclusion decisions remain in `docs/source-register.md`. If those sources conflict with this contract, stop and reconcile them in a reviewed change. Never silently choose one.

## 1. Required outcome and stop point

Build a private, reproducible, multi-source candidate pool for all 34 configured language labels. Acquire current sources afresh, validate the pinned historical snapshots, normalize and screen records, apply source/language quotas, assess the entire resulting candidate pool with the three JQL judges, globally prune the bottom 25% by the agreed consensus score, and produce complete audit reports.

**Stop after the JQL-pruned pool and reports.** The final selection of exactly 30,000 records per language is a separate human decision. Do not run it, publish it, upload it to a public dataset, or treat a technical candidate as rights-cleared without explicit user approval.

## 2. Stage contract

### Stage 0 — configuration and preflight

- Read operational values from `config/langid32.toml`; do not duplicate numeric policy in workflow YAML or scripts.
- Validate the configuration, registered source IDs, language labels, source/language quotas, rights statuses, required secrets and all stage input/output contracts before acquisition starts.
- Pin the workflow code to one commit for every job. A run must not mix a workflow from `main` with scripts/config from a moving recovery branch.
- Fail before downloading if any required script, config file, adapter, dependency, secret or historical artifact is missing.
- Produce a machine-readable preflight manifest with commit SHA, config hash, source/revision plan, expected inputs, outputs and policy version.

### Stage 1 — acquisition

- Current Common Voice and waiting-source acquisitions are fresh for each clean run. Do not restore, reuse or silently top up from artifacts/checkpoints produced by earlier failed or partial pipeline runs.
- Exception: the explicitly approved historical source snapshots may be downloaded from their pinned, successful source runs and validated. Current pins: v5 run `43950037392`, Leipzig run `44361364340`, Tatoeba run `44121162591`, DGT-TM run `44291075180`. These are source snapshots, not failed pipeline checkpoints.
- Preserve original source identity, immutable upstream revision/release, retrieval date, source URL, file hashes, adapter version, licence/terms, attribution and row/document provenance.
- Keep each original source × language quota independent. Do not alias different sources into one family quota unless the source register and config explicitly approve that exact relationship.
- Apply normalization, source quality checks, privacy screening and within-source deduplication **before** quota accounting. Target: up to 20,000 eligible unique records per original source per language. Underfilled source/language cells remain underfilled; never silently top up from another source.
- Keep source rights holds in the records and reports. Technical acquisition is not permission to redistribute.

### Stage 2 — candidate construction and global exclusions

- Consume all required historical, Common Voice and waiting-source inputs from the same run, plus only the approved historical source snapshots above.
- Validate the exact expected files and schemas before processing. Missing or duplicate inputs are fatal; do not skip a source silently.
- Normalize text consistently (NFC and whitespace), enforce configured character/byte/script/quality rules, and apply privacy screening again at the candidate boundary.
- Deduplicate exact normalized text within each language across all sources.
- If the same normalized text occurs under more than one language label, exclude **every occurrence in every language**. Never use first-language-wins.
- Preserve stable source/document/group identity for split integrity and provenance. Keep private provenance separate from text-only candidate outputs.
- Report input, accepted, rejected, duplicate, cross-language collision, privacy rejection/quarantine and quota counts by original source and language. Reports must never include matched personal text or personal metadata values.

### Stage 3 — JQL assessment and pruning

- Assess **every row** in the post-filter candidate pool. Sampling is forbidden. The assessment manifest must prove exact one-to-one coverage of candidate IDs.
- Score independently with Gemma, Mistral and Llama JQL heads. Preserve all three raw scores and model/repository immutable revisions.
- Independently quantile-normalize each judge's scores over the **entire assessment corpus**, all languages and sources combined. Use average ranks for ties and map ranks through the standard-normal inverse CDF.
- For each record calculate:
  `consensus = mean(gemma_z, mistral_z, llama_z) - 0.5 × population_std(gemma_z, mistral_z, llama_z)`.
- Remove the bottom 25% **globally**, not 25% per language or source. Use a deterministic tie-break (consensus ascending, then stable record ID) to remove exactly the configured global count.
- Preserve raw and normalized judge scores, mean, disagreement, consensus, IDs, language and original source in the private assessment output.
- Report before-scoring, successfully-scored, retained and pruned counts by language and original source; include missing/duplicate/error counts and prove complete judge coverage.
- Boundary/quality annotations are diagnostics only unless separately approved. JQL is not a privacy, rights, language-correctness or factuality test.
- Respect the six-hour ceiling by splitting work into small, resumable batches. The existing agreed execution shape is eight deterministic shards, at most four scoring workers, with each scoring batch capped at 3,600 seconds. Measure throughput with a small initial batch when needed, then calculate batch size/count; do not attempt one monolithic run.

### Stage 4 — review hand-off

- Produce the complete private candidate/assessment artefacts and machine-readable manifests/reports, including per-language × original-source counts before and after every exclusion/pruning stage.
- Stop. Do not select the final 30,000 per language, publish, push text to Hugging Face, or release provenance until the user has reviewed privacy, source rights and source balance and explicitly approved the next step.

## 3. Privacy and rights constraints

- Screen sentence text and provenance metadata at acquisition and candidate boundaries. Remove personal contributor/author/contact/speaker/user identifiers from metadata; do not expose their values in logs or reports.
- Reject high-confidence identifiers and quarantine ambiguous personal-name/source privacy-flag cases. Keep only non-identifying source/document references needed for audit.
- The privacy implementation is deterministic heuristic screening, **not exhaustive multilingual NER or proof of anonymization**. Human review remains mandatory before any external release.
- Preserve source-specific rights/attribution status. In particular, FineWeb2 remains technical-candidate-only while underlying web-text rights are unresolved; Korean Wikipedia remains on share-alike compatibility hold; Målfrid remains on database/third-party-rights hold; any other hold in the source register remains binding.
- Do not infer a passage licence from a hosting page, dataset wrapper or compilation licence. Do not relabel mixed-rights content CC0.
- Common Voice scope is HF-hosted Common Voice 22 text only, CC0 dataset-level terms: no audio, speaker IDs or demographic data. Do not use Mozilla Data Collective data/repository. Keep the approved locales and source limitations in the source register; do not invent a Croatian Common Voice input.
- Failed/partial run artifacts are not clean-run inputs. The historical snapshot exception above is narrow and explicit.

## 4. Execution and time limits

Operational values currently recorded in `config/langid32.toml`:

| Control | Required value |
|---|---:|
| Configured language labels | 34 |
| First-pass target | 20,000 per original source × language |
| Acquisition concurrent source tasks | 4 maximum |
| Acquisition job timeout | 300 minutes |
| Shared acquisition workflow budget | 330 minutes |
| Safety reserve | 30 minutes |
| Acquisition file batch | 1 file |
| JQL assessment | all candidate rows; no sampling |
| JQL shards | 8 |
| JQL concurrent scoring shards | 4 maximum |
| JQL scoring batch ceiling | 3,600 seconds |
| Global JQL pruning | bottom 25% |
| Final selection | deferred; requires explicit user approval |

The shared acquisition budget plus reserve must remain within six hours. The JQL six-hour ceiling is also binding; do not reinterpret it as permission for a single six-hour uninterruptible job. Use small batches and resumable outputs.

## 5. Implementation audit baseline (main, 2026-11-26)

This is the observed state, not the desired state.

| Contract item | Observed implementation | Status |
|---|---|---|
| Central TOML configuration and fail-closed 20k source/language quota checks | `config/langid32.toml`, `src/langid32/settings.py` | Implemented on recovery branch; branch consistency is broken in the current workflow |
| Acquisition adapters, batching/state DB, revision pinning, retry/resume, encrypted checkpoints | Stage adapters, `acquisition_batches.py`, checkpoint/runtime scripts | Partly implemented; must be tested together on one pinned commit |
| Privacy screening and provenance sanitization | `src/langid32/privacy.py`; acquisition and candidate call sites | Implemented heuristically; not exhaustive and not a substitute for human review |
| Candidate normalization, privacy re-screen, source quota accounting, source manifest | `scripts/build_multisource_candidate.py` | Implemented on recovery branch; exact cross-source/cross-language and split behavior still needs contract tests and end-to-end proof |
| Full-pool assessment Parquet | `scripts/sample_jql_assessment.py --all`; stage 03 invokes it | Implemented; it creates assessment input only, not judge scores |
| Three-judge scoring | `scripts/score_jql_parquet.py` and separate shard workflow | Separate implementation exists; not integrated into the staged pipeline's terminal job |
| Global quantile normalization and consensus formula | `scripts/merge_jql_ratings.py` | Implemented as a separate utility; coverage checks exist |
| Bottom-25%-global pruning and per-source/language report | Merge utility supports pruned outputs when explicitly passed; config enables it | Utility capability exists; current staged workflow does not invoke it |
| Final 30k/language selection deferred | Assessment summary says deferred; separate selector exists | Must remain disabled pending user approval |
| Full workflow contract tests and same-commit integration verification | CI runs compileall, Make dry-run and pytest | Unit tests exist; no demonstrated full staged-workflow integration test |
| One-command clean end-to-end run | `.github/workflows/langid32-pipeline.yml` | **Not currently operational**; see blocking findings below |

### Blocking findings observed

1. The workflow file on `main` checks out `recovery/fix-acquisition-20261124` for config, Common Voice, waiting-source, candidate and JQL jobs, but checks out the default `main` branch for the historical job. This mixes code revisions within one run.
2. The historical job on `main` executes `python3 scripts/emit_runtime_config.py`, but that file is absent from `main`. This exactly caused run #178 historical job failure. The file exists on the recovery branch.
3. Run #178 (ID `45780510056`) had candidate and JQL jobs skipped. It did not produce a candidate pool, judge scores, a pruned pool or privacy-review output. FineWeb2 Croatian also encountered HTTP 429. The other successful acquisitions do not turn that run into a full pipeline.
4. The staged workflow's JQL job only restores the candidate and invokes `stages/03-jql/run.py`, which builds the full assessment Parquet. It does not invoke the scoring shards, merge/normalization, consensus or bottom-25% pruning.
5. The separate scoring workflow is not a reliable substitute for integration: its `workflow_run` trigger names a different upstream workflow title, and its current contract/trigger/artifact wiring must be reconciled with the staged workflow.
6. The repository's older `docs/jql-edu-annotation.md` describes JQL as non-filtering QA, which conflicts with the later agreed project decision to globally prune the bottom 25% after full-pool scoring. This contract and the TOML encode the later decision; the stale documentation must be corrected, not followed.
7. The workflow currently downloads and restores acquisition checkpoints as artifacts. Clean-run logic must explicitly distinguish same-run fresh acquisition outputs from the four approved historical source snapshots and must not consume prior failed-run acquisition artifacts.
8. The current privacy patterns are heuristic. They cannot certify the pool as anonymous; the requested human privacy review remains a hard stop before any public release.
9. The recovery branch is not a safe direct merge base: comparison against `main` reports a diverged history, 450 commits ahead and 6 behind (merge base `e57dc61dfb485a2fee13529ba5cd3cb88a5bea34`). It contains the missing runtime/config/privacy/acquisition/JQL code, but it also contains hundreds of commits and many unrelated workflow/source changes. Do not merge the branch wholesale or move `main` to it. Reconcile the required implementation into a clean branch based on current `main`, in reviewed, contract-checked increments.

**Conclusion:** do not trigger another full acquisition run until the branch pinning, missing historical runtime script, same-run artifact contract, integrated JQL scoring/merge/pruning, retry behavior and end-to-end tests have been repaired and verified.

## 6. Mandatory change-control protocol

Before **every** code, workflow, configuration or contract modification:

1. Read the current contract, config, source register and every affected caller/callee.
2. Record the current base commit and relevant file hashes.
3. Map the proposed change to the contract clauses it affects. Run the pre-change contract checks and record existing failures.
4. If the requested change alters a decision, stop treating it as an implementation detail: write the proposed new rule into this contract (and the relevant config/source register), explain the old and new behavior, then validate the change against the new contract. Do not silently change the contract.

After **every** modification:

1. Fetch the committed file(s) back from GitHub and verify their exact content and commit SHA.
2. Re-run the affected unit tests, static checks and contract checks. Check all downstream callers, workflow paths, artifact names and schemas—not just the edited file.
3. Re-check every contract clause affected by the change and explicitly state pass/fail/not-yet-verified with evidence.
4. Do not merge or trigger a full pipeline while any blocking contract check fails.
5. Never describe a stage as implemented, verified, integrated or complete based only on its existence, documentation, a successful compile, or a skipped downstream job. Integration is verified only by a successful end-to-end run with complete expected outputs and coverage.

Required preflight/integration assertions include: every job uses the same commit SHA; every referenced file exists at that SHA; all required historical inputs validate; fresh acquisitions are same-run only; no failed-run artifacts are restored; every source/language cell is independently quota-limited after privacy/quality filters; candidate IDs are unique and cross-language collisions are fully removed; privacy metadata is sanitized; JQL assessment IDs equal candidate IDs exactly; every ID has all three judge scores; normalized distributions use the full combined assessment pool; consensus matches the formula above; exactly floor(25% × N) rows are pruned globally with deterministic ties; counts reconcile by language and original source; no final 30k selection or publication occurs.

## 7. How to invoke the workflow without asking the user to click Run

The staged workflow `.github/workflows/langid32-pipeline.yml` is configured for `push` to branch `main` and also declares `workflow_dispatch`.

- **Preferred automated route when the connector has no workflow-dispatch action:** after all preflight checks pass, create a meaningful, reviewed commit on `main` using the GitHub `create_file` or `update_file` action. A commit to `main` is a push and triggers the staged workflow automatically. For an existing file, first fetch its current blob SHA and pass that SHA to `update_file`. For a new file, use `create_file`. Do not use a no-op or unrelated edit just to trigger compute.
- A merged PR to `main` also creates the push that triggers the workflow. Do not merge a PR while the pipeline is known broken.
- Manual fallback: use the repository's Actions page, select **langid-32 staged corpus pipeline**, then **Run workflow** on `main`. The GitHub connector available in this session exposes read and repository-write operations but no workflow-dispatch operation; do not pretend a dispatch occurred.
- After the commit/push, fetch the new run ID from the Actions API and inspect every job, step, log and artifact. A successful trigger is not a successful pipeline. Wait for all stages to finish and verify the contract assertions before reporting success.

**Current gate:** this invocation procedure is documented, but the staged workflow must remain untriggered until all blocking findings in §5 are resolved and preflight passes.
