# langid-32 pipeline contract and execution protocol

**Status:** contract and implementation audit, refreshed 2026-11-26 against `main` commit `71fde5b0c2b02b34783d120fdfa3ada0c290f71f`. CI run [45798217209](https://github.com/SylvainSouche/langid-32/actions/runs/45798217209) passed all 110 tests, including the synthetic JQL integration test, actionlint, script compilation and Make dependency validation. This verifies the tested code paths only; it is **not** a successful real-data end-to-end pipeline run.

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
- These four existing source snapshots are public, unencrypted GitHub Actions artifacts. Their current expiries are: v5 `2026-11-30T20:30:01Z`, Tatoeba `2026-12-01T16:03:33Z`, DGT-TM `2026-12-02T11:07:30Z`, Leipzig `2026-12-18T17:46:23Z`. Their use is the previously accepted historical-snapshot exception; do not upload any new plaintext text-bearing artifact. The current pipeline re-encrypts restored text-bearing data before its own artifact upload. Preflight must fail if any pinned artifact is missing or expired.
- V5, Tatoeba and DGT artifact contents have been inspected directly for JSONL validity and required record fields. The Leipzig artifact is 1.45 GB and exceeded the connector's 512 MB download limit; its complete JSONL schema/content check remains a required step in the historical job before fresh acquisitions.
- Preserve original source identity, immutable upstream revision/release, retrieval date, source URL, file hashes, adapter version, licence/terms, attribution and row/document provenance.
- For FineWeb2 remote Parquet reads, record the upstream LFS SHA-256 for each shard and retry transient HTTP 408/429/5xx and connection/time-out failures at the current row-group boundary with bounded exponential backoff (8 attempts, 5-second base, 120-second cap). Roll back an incomplete row-group transaction before replay; never double-count rows or privacy rejections. Stop retrying when the shared acquisition deadline is reached.
- Keep each original source × language quota independent. Do not alias different sources into one family quota unless the source register and config explicitly approve that exact relationship.
- Apply normalization, source quality checks, privacy screening and within-source deduplication before the **first-pass acquisition intake cap**: up to 20,000 eligible unique records per original source × language. This is an acquisition cap, not a guaranteed post-global-dedup count and not the final 30,000-per-language selection.
- **Approved exception: Gaois Parallel English-Irish Legislation, Irish side only, up to 50,000 deterministic candidates** from the six audited TMX archives. This is the explicitly accepted candidate-sample scope. The prior preview measured 390,992 screened distinct Irish segments; the fresh pipeline run must reapply the accepted privacy screen, report its actual eligible count, and select up to 50,000 deterministic candidates. Do not assume the prior count will be reproduced. This is not a final language selection or approval to ingest the entire underlying corpus. Preserve DCU/Gaois attribution and the distinction between CC BY 4.0 derivative TMX rights and Government of Ireland rights in original legislation.
- The first-pass cap is applied by each source adapter before cross-source global deduplication. The candidate merge then removes global duplicates and cross-language collisions. Do not silently top up a shortfall from another source; no automatic post-global-dedup top-up is currently in the contract.
- The 30% preferred / 50% hard source-share limits apply only to the later final selection, after JQL pruning and explicit user approval; they are not applied in acquisition or candidate construction. Underfilled source/language cells remain underfilled.
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

- Assess **every row** in the post-filter candidate pool. Sampling is forbidden. The staged workflow must pass `--all`; configuration also requires `assessment_sample_per_language=0` and `max_rows=0`. The assessment manifest must prove exact one-to-one coverage of candidate IDs. No sampling or row cap is permitted; the archived 34k experiment is not a current input.
- Score independently with Gemma, Mistral and Llama JQL heads. Preserve all three raw scores and model/repository immutable revisions.
- Use the Snowflake Arctic Embed M v2.0 embedder pinned by the configured commit SHA and the balanced JQL-Edu heads from `JQL-AI/JQL-Edu-Heads`. Resolve the head repository's `main` selector to a commit SHA before downloading any checkpoint; use that immutable SHA for every download and require all shards to report the same resolved SHA.
- Match the published inference recipe: CLS pooling, L2-normalized embeddings, 768→1000→1 regression heads, bfloat16 inference. Pin Python 3.11, PyTorch 2.6.0, Transformers 4.44.2 and Hugging Face Hub 0.26.5. Record exact runtime versions and checkpoint SHA-256 values in every shard manifest; reject drift at merge.
- The heads were not trained on `ar`, `ja`, `ko`, `zh`, `nb` or `nn`. Score these rows as agreed, but preserve an explicit out-of-training-domain flag and report their counts separately; do not present them as in-training-language ratings.
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
- The deferred final selection target is 30,000 per language. The agreed source-mix rule for that later selection is 30% preferred and 50% hard maximum per original source within each language; document any underfill or single-source exception. Do not apply this balancing before global JQL pruning.

## 3. Privacy and rights constraints

- Screen sentence text and provenance metadata at acquisition and candidate boundaries. Remove personal contributor/author/contact/speaker/user identifiers from metadata; do not expose their values in logs or reports.
- Reject high-confidence identifiers and quarantine ambiguous personal-name/source privacy-flag cases. Keep only non-identifying source/document references needed for audit.
- The user has accepted the current deterministic multilingual privacy-screening implementation for private pipeline use. Do not reopen its implementation acceptance or block private candidate/JQL processing on replacing it.
- The screen is **not exhaustive multilingual NER or proof of anonymization**. The user will manually review the actual resulting pool; that review is a hard stop before any external release. Do not publish or redistribute before that review and explicit approval.
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
| JQL assessment Parquet batch | 2,000 rows |
| JQL shard Parquet batch | 8,192 rows |
| JQL shards | 8 |
| JQL concurrent scoring shards | 4 maximum |
| JQL model inference batch | 8 rows |
| JQL inference precision | bfloat16 |
| JQL runtime | Python 3.11; PyTorch 2.6.0; Transformers 4.44.2; Hugging Face Hub 0.26.5 |
| JQL out-of-training labels | ar, ja, ko, zh, nb, nn (flagged, still scored) |
| JQL scoring batch ceiling | 3,600 seconds |
| JQL job timeout / work budget / upload reserve | 360 / 350 / 10 minutes |
| Global JQL pruning | bottom 25% |
| Final selection | deferred; requires explicit user approval |

The shared acquisition budget plus reserve must remain within six hours. The JQL six-hour ceiling is also binding; do not reinterpret it as permission for a single six-hour uninterruptible job. Use small batches and resumable outputs.

## 5. Implementation audit baseline and current status

The original audit baseline was `main` commit `1e6f8319b6cfd102c650c3b516cc4583d0d42730` on 2026-11-26. That baseline was not operational. The findings below record the corrections subsequently made on `main`; they do **not** claim a successful real-data end-to-end run.

| Contract item | Current implementation on main | Status |
|---|---|---|
| Central configuration and fail-closed policy validation | `config/langid32.toml`, `src/langid32/settings.py`; locks 34 language labels, source-local first-pass targets, Gaois 50k exception, all-row JQL, consensus/pruning, runtime versions, out-of-training flags and deferred final selection | Implemented; tests added |
| Preflight evidence | `scripts/emit_runtime_config.py`, `scripts/validate_historical_artifacts.py`, `scripts/validate_pipeline_trigger.py`; machine-readable manifest records commit/config/source-register/contract/trigger hashes, historical pins, source plan, expected inputs/outputs and policy | Implemented; workflow uploads the evidence before acquisition |
| Historical snapshots | `stages/01-acquisition/targets/historical.py`; exact four pinned artifacts, schema validation, hashes and per-original-source/language counts; current fresh acquisition jobs wait for historical validation | Implemented; V5, Tatoeba and DGT artifact contents were inspected directly; Leipzig artifact is too large for the connector's 512 MB download limit and will be fully checked by the workflow before fresh acquisition |
| Fresh acquisition | Common Voice, waiting-source and Gaois adapters; immutable upstream revisions are resolved and recorded in source manifests; bounded batches, encrypted resumable checkpoints and retry handling | Implemented; no new full acquisition run yet |
| Privacy | `src/langid32/privacy.py`, invoked at acquisition and candidate boundaries; provenance sanitization and multilingual pattern screening | Accepted implementation; manual review of the resulting pool remains required |
| Candidate construction | `scripts/build_multisource_candidate.py`, `src/langid32/merge.py`; original-source identity, first-pass intake caps, global within-language deduplication, all-occurrence cross-language collision removal, provenance and count reports | Implemented; tests added; real full-pool output not yet produced |
| Premature selection guard | Candidate merge rejects nonzero per-language final caps; `scripts/select_jql_consensus.py` fails closed pending user approval | Implemented; guard tests added |
| Full-pool JQL assessment | `scripts/sample_jql_assessment.py --all`; records candidate input hash, assessment Parquet hash, row count and out-of-training-domain language flags | Implemented; no sampling path in the staged workflow |
| Deterministic JQL sharding | `scripts/split_jql_parquet.py`; streaming Parquet batches, SQLite global ID uniqueness, balanced eight-shard plan, per-shard hashes and manifest | Implemented; unit and synthetic integration coverage added |
| Three-judge scoring | `scripts/score_jql_parquet.py`; three balanced heads, bfloat16, pinned runtime, source pipeline SHA/run ID, immutable model revisions and checkpoint hashes in each shard manifest | Implemented; actual model inference on the full pool not yet verified |
| Global normalization, consensus and pruning | `scripts/merge_jql_ratings.py`; validates exact split manifest, all candidate IDs, all three judge ratings, source run/commit, model/runtime provenance, global quantile normalization, consensus and exact global bottom-25% pruning | Implemented; synthetic end-to-end JQL integration test added |
| JQL workflow integration and resumption | `.github/workflows/score-jql-assessment.yml`; automatic `workflow_run` after staged pipeline success, exact source-run SHA checkout, optional resume from previous scoring-run artifacts with provenance checks | Implemented; workflow syntax and repository CI passed in run `45798217209`; real downstream scoring run not yet exercised |
| Manual review hand-off | Text-bearing candidate/JQL outputs are encrypted before Actions artifact upload; final 30k selector is disabled | Implemented; no review artifact from a new full run yet |
| Full real-data end-to-end proof | Staged acquisition → candidate → full-pool JQL scoring → merge/prune → encrypted hand-off | **Not yet verified**; do not describe the pipeline as production-verified until a complete run succeeds |

### Source adapter coverage audit

The current staged workflow's source coverage is narrower than the full set of audited/registered sources. A TOML `source_rules` entry or an audit report does **not** mean a source is acquired by the staged pipeline.

| Source scope | Code path observed on main | Current status |
|---|---|---|
| Historical v5, Leipzig, Tatoeba CC0 and DGT-TM 2021 | `stages/01-acquisition/targets/historical.py` plus pinned artifact restore | Active; validated before fresh acquisition |
| Common Voice 22 text-only (fi, el, mt, sl, is) | `stages/01-acquisition/targets/common-voice.py`, `scripts/download_common_voice_hf.py`, `scripts/curate_common_voice_hf.py` | Active; fresh HF acquisition |
| FineWeb2 (is/hr/fi/el/mt/sl), TeMU CC0 + BSC-LT legal (ca), IGC2024 Filtered-1 (is), Målfrid 2026 (nb/nn), Korean Wikipedia (ko), UN Arabic-English Filtered (ar) | `scripts/acquire_waiting_sources.py` via the waiting-source job and its explicit matrix; FineWeb2 locale matrix is `isl_Latn`, `hrv_Latn`, `fin_Latn`, `ell_Grek`, `mlt_Latn`, `slv_Latn` | Active technical candidates; each source's rights hold/status in the source register remains binding |
| Gaois Irish legislation, Irish side only | `scripts/acquire_gaois_irish_legislation.py`, `stages/01-acquisition/targets/gaois.py` | Active; accepted 50,000-record bounded sample |
| IGC2024 Filtered-1 | `scripts/acquire_waiting_sources.py --source icelandic` downloads the Filtered-1 archive and scans it into candidate records under source ID `igc` | Active; fresh acquisition in the waiting-source matrix |
| Greynir Copper and Silver | Audit workflow/script only; no candidate extraction adapter in the staged workflow | Audited/registered, **not acquired by this pipeline** |
| MaCoCu-hr 2.0, MaCoCu-mt 2.0, MaCoCu-sl 2.0 | Full archive audit workflows/scripts only; no paragraph-to-candidate adapter in the staged workflow | Audited/registered, **not acquired by this pipeline** |
| ParlaMint 4.0 (IS/SI) | `src/langid32/parlamint.py`, `scripts/acquire_waiting_sources.py --source parlamint`, `stages/01-acquisition/targets/parlamint.py`, waiting-source matrix | Adapter and synthetic fixture added on main; latest CI run [45812720539](https://github.com/SylvainSouche/langid-32/actions/runs/45812720539) passed on commit `d76b3bcb50e229e8be6b629006a104f8233d1f51` (workflow lint, script compilation, Make dependency validation, and 111 tests). The run fixed the prior CI failure: the adapter now extracts only the fixed non-identifying role whitelist (`chair`, `regular`, `guest`) from TEI `ana`; speaker `who` references and person metadata are not emitted. Real-archive integration and source exhaustion remain unverified. |
| Soranoha Japanese literature | Audit artifact/source-register entry only; no active config rule or staged acquisition adapter | Audited/registered, **not acquired by this pipeline** |

The v5 artifact is a composite historical snapshot. Restoring it does not override source exclusions: rows from held/excluded sources (including FineWeb where marked held) must still be filtered by the source register and exclusion registry before candidate construction.

The `config/langid32.toml` contains target rules for Greynir Copper/Silver and MaCoCu, but those entries are not evidence that their text enters the candidate pool. ParlaMint now has an extraction adapter, synthetic fixture and workflow matrix entry on main; synthetic CI is green, but real-archive integration and source exhaustion remain unverified. Greynir Copper/Silver and all three MaCoCu sources still lack candidate extraction adapters and remain launch blockers. The user has explicitly approved these source-language groups for the current candidate scope. Soranoha is not included in this approved scope.

### Resolved findings from run #178

1. The mixed branch checkout was removed: the staged jobs use the workflow run's single commit; the downstream JQL workflow resolves and checks out the exact source pipeline run SHA.
2. `scripts/emit_runtime_config.py` and the historical validation path are now present on `main`.
3. Run #178 (ID `45780510056`) remains a failed partial acquisition attempt: candidate and JQL were skipped, and Croatian FineWeb2 received HTTP 429. Its artifacts are not inputs to a clean run.
4. The downstream JQL workflow now performs sharding, three-head scoring, merge, normalization, consensus and global pruning; it no longer stops after building the assessment Parquet.
5. Manual JQL resume is bound to the original successful staged run ID and commit. Shard manifests reject ratings from a different run, commit, shard hash, model revision, checkpoint hash or runtime.
6. Stale 34k-sample documentation is marked historical; README and corpus policy now describe the full-pool staged pipeline and deferred final selection.
7. The recovery branch was not merged wholesale. It diverged from `main` by 450 commits ahead and 6 behind; required implementation was reconciled into `main` in reviewed changes.

### Remaining verification gates

- CI gate: **passed** in run `45798217209` on commit `71fde5b0c2b02b34783d120fdfa3ada0c290f71f` (110 tests; CPU PyTorch/bfloat16 dependency installed; actionlint, script compilation and Make dependency validation passed). Earlier run `45795368247` failed two tests; those failures were subsequently corrected and the later run is green. CI success does not replace a full real-data pipeline run.
- Integrate the already-approved current-pipeline sources that are still missing from the adapter matrix: MaCoCu-hr 2.0 (`hr`), MaCoCu-mt 2.0 (`mt`), MaCoCu-sl 2.0 (`sl`), ParlaMint 4.0 (`is`, `sl`), and Greynir Copper and Silver (`is`). These are required inputs, not an open scope question. Greynir Gold development/test partitions remain excluded. Implement and test each adapter; the current pipeline is not launch-ready while any of these approved sources is absent. Soranoha remains audited/investigated only: it has not been ruled into the current candidate scope and must not be added by inference.
- The historical job must validate the full Leipzig JSONL as well as the other three snapshots before any fresh acquisition job starts.
- A clean real-data run must complete all in-scope acquisitions, candidate construction, every JQL shard, exact merge/pruning and encrypted artifact upload. The run must produce reconciled per-language × original-source counts.
- The user then manually reviews privacy and source-rights outputs. No final 30k selection or publication follows automatically.

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

The staged workflow `.github/workflows/langid32-pipeline.yml` has two triggers:

- `workflow_dispatch` for an explicit manual run.
- A guarded `push` trigger on `main`, restricted to changes to **`pipeline-trigger.json` only**. Ordinary code, documentation and config commits do not launch acquisition.

**Assistant-controlled push route (preferred once every gate passes):**

1. Re-fetch and verify the current contract, config, source register, all affected code and the latest passing CI checks.
2. Calculate the exact SHA-256 values of `config/langid32.toml`, `docs/source-register.md` and `docs/pipeline-contract.md`.
3. Update `pipeline-trigger.json` on `main` with:
   - `run_mode: "clean_full_pipeline"`
   - a fresh 12–80 character nonce
   - those three exact hashes
   - `artifact_reuse: false`
   - `final_selection: "deferred"`
   - `privacy_review_required: true`
4. Commit that meaningful operational command to `main`. The resulting push to the single configured path triggers the staged workflow automatically.
5. The first config job runs `scripts/validate_pipeline_trigger.py`; it verifies the push actually changed the trigger file, the branch is `main`, all hashes match the current sources of truth, no prior failed/partial artifact reuse is requested, and final selection remains deferred. It writes a validation record and uploads it with the preflight manifest.
6. Retrieve the new run ID and inspect every job, step, log and artifact. A successful push or trigger is not a successful pipeline.

The checked-in `pipeline-trigger.json` is currently **disabled**. Do not arm it until all remaining verification gates in §5 pass. The trigger file is a command, not a no-op edit; never change it merely to test whether GitHub Actions starts.

**Downstream JQL scoring and resume:**

- On successful completion of the staged pipeline, `.github/workflows/score-jql-assessment.yml` starts automatically through its `workflow_run` trigger.
- It retrieves the source run metadata, verifies the workflow name, success conclusion and `main` branch, then checks out the exact source run commit SHA.
- If a scoring job exceeds its work budget, its completed ratings and manifest are uploaded. A manual resume dispatch supplies the original successful `source_run_id` and optional `resume_ratings_run_id`; it checks out the original source commit and restores only that previous scoring run's shard artifact. The scorer/merge reject mismatched source run IDs, source SHAs, shard hashes, model revisions, checkpoint hashes or runtime versions.
- The GitHub connector available in this session has repository read/write operations but no workflow-dispatch operation. The guarded `pipeline-trigger.json` commit is therefore the supported assistant-controlled launch route; do not claim a dispatch occurred when only a file was committed.

**Current gate:** no full run has been launched from the new contract-compliant implementation. The trigger remains disabled until CI and the remaining preflight/integration checks pass.
