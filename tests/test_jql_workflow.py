from statistics import mean
from pathlib import Path
import subprocess
import sys

import torch

from scripts.check_sentence_boundaries import (
    capitalization_status,
    punctuation_status,
)
from scripts.merge_jql_ratings import quantile_normalize


def test_capitalization_unicode_and_caseless_languages():
    assert capitalization_status("«Été magnifique.»", "fr") == "pass"
    assert capitalization_status("«été magnifique.»", "fr") == "fail"
    assert capitalization_status("مرحبا بالعالم؟", "ar") == "not_applicable"
    assert capitalization_status("你好。", "zh") == "not_applicable"


def test_terminal_punctuation_with_closing_quotes():
    assert punctuation_status("A complete sentence.") == "pass"
    assert punctuation_status("«Une phrase complète !»") == "pass"
    assert punctuation_status("A sentence fragment") == "fail"
    assert punctuation_status("A Greek question;") == "fail"


def test_quantile_normalization_is_monotonic_and_tie_safe():
    result = quantile_normalize([10.0, 20.0, 20.0, 40.0])
    assert result[0] < result[1] == result[2] < result[3]
    assert abs(mean(result)) < 1e-12


def test_final_30k_selection_is_fail_closed_until_user_approval():
    script = Path(__file__).resolve().parents[1] / "scripts" / "select_jql_consensus.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "FINAL SELECTION DISABLED BY CONTRACT" in result.stderr


def test_cpu_bfloat16_regression_head_operations_are_supported():
    head = torch.nn.Sequential(
        torch.nn.Linear(768, 1000),
        torch.nn.ReLU(),
        torch.nn.Linear(1000, 1),
    ).to(dtype=torch.bfloat16)
    embeddings = torch.randn(2, 768, dtype=torch.bfloat16)
    scores = head(embeddings)
    assert scores.dtype == torch.bfloat16
    assert scores.shape == (2, 1)



def test_jql_scoring_invocation_cannot_overrun_job_upload_budget():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/score-jql-assessment.yml").read_text(encoding="utf-8")
    scorer = (root / "scripts/score_jql_parquet.py").read_text(encoding="utf-8")
    score_job = workflow.split("\n  score:\n", 1)[1]
    assert score_job.index("Start the shard work-budget clock before setup") < score_job.index("actions/checkout@v4")
    assert 'JQL_JOB_STARTED_EPOCH: ${{ steps.job_clock.outputs.started_epoch }}' in score_job
    assert 'elapsed=$((now - JQL_JOB_STARTED_EPOCH))' in score_job
    assert 'invocation_budget=$((remaining - 60))' in workflow
    assert '--max-runtime-seconds "$invocation_budget"' in workflow
    assert 'process_started = time.monotonic()' in scorer
    assert 'runtime_limit_reached' in scorer
    assert 'args.max_seconds' in scorer



def test_downstream_jql_jobs_checkout_the_exact_source_pipeline_commit():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/score-jql-assessment.yml").read_text(encoding="utf-8")
    assert "ref: ${{ steps.source.outputs.head_sha }}" in workflow
    assert workflow.count("ref: ${{ needs.prepare.outputs.source_sha }}") == 2
    assert "source_sha: ${{ steps.source.outputs.head_sha }}" in workflow
