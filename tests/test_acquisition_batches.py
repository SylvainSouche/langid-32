import json
import sqlite3

from langid32.acquisition_batches import (
    add_eligible, finish_batch, mark_exhausted, next_batch, open_state,
    plan_file_batches, retained_count, task_complete, task_report,
    is_retryable_remote_error, retry_delay_seconds,
)


def test_target_counts_only_unique_eligible_records_and_continues(tmp_path):
    db = open_state(tmp_path / "state.sqlite")
    assert plan_file_batches(db, "source-A", "fi", 3, ["a", "b", "c"], 1) == 3
    batch_no, files = next_batch(db, "source-A", "fi")
    assert files == ["a"]
    assert add_eligible(db, "source-A", "fi", [
        {"text": "one"}, {"text": "one"}, {"text": "two"}
    ]) == 2
    finish_batch(db, "source-A", "fi", batch_no, {"a": "a".ljust(64, "0")})
    assert not task_complete(db, "source-A", "fi")
    batch_no, files = next_batch(db, "source-A", "fi")
    assert files == ["b"]
    assert add_eligible(db, "source-A", "fi", [{"text": "three"}, {"text": "four"}]) == 1
    finish_batch(db, "source-A", "fi", batch_no, {"b": "b".ljust(64, "0")})
    assert retained_count(db, "source-A", "fi") == 3
    assert task_complete(db, "source-A", "fi")
    assert next_batch(db, "source-A", "fi") is None


def test_exhaustion_reports_exact_shortfall_and_source_isolation(tmp_path):
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "fi", 5, [], 1)
    plan_file_batches(db, "source-B", "fi", 5, [], 1)
    add_eligible(db, "source-A", "fi", [{"text": "same"}])
    assert mark_exhausted(db, "source-A", "fi") == 4
    assert task_complete(db, "source-A", "fi")
    assert retained_count(db, "source-B", "fi") == 0
    assert not task_complete(db, "source-B", "fi")


def test_completed_files_are_not_replanned(tmp_path):
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "is", 2, ["a", "b"], 1)
    batch_no, _ = next_batch(db, "source-A", "is")
    finish_batch(db, "source-A", "is", batch_no, {"a": "a".ljust(64, "0")})
    # Existing planned file paths are not duplicated when discovery is repeated.
    assert plan_file_batches(db, "source-A", "is", 2, ["a", "b", "c"], 1) == 1



def test_incomplete_batches_cannot_be_declared_exhausted(tmp_path):
    import pytest
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "fi", 5, ["not-yet-processed"], 1)
    with pytest.raises(RuntimeError, match="incomplete batches"):
        mark_exhausted(db, "source-A", "fi")


def test_record_cannot_cross_source_or_language_task(tmp_path):
    import pytest
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "fi", 5, [], 1)
    with pytest.raises(ValueError, match="does not match"):
        add_eligible(db, "source-A", "fi", [{"text": "wrong task", "source": "source-B"}])


def test_invalid_file_digest_cannot_complete_batch(tmp_path):
    import pytest
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "fi", 5, ["a"], 1)
    batch_no, _ = next_batch(db, "source-A", "fi")
    with pytest.raises(ValueError, match="valid SHA-256"):
        finish_batch(db, "source-A", "fi", batch_no, {"a": "not-a-hash"})



def test_running_batch_resumes_after_database_reopen(tmp_path):
    path = tmp_path / "state.sqlite"
    db = open_state(path)
    plan_file_batches(db, "source-A", "fi", 2, ["b", "a", "a"], 1)
    batch_no, files = next_batch(db, "source-A", "fi")
    assert files == ["a"]
    db.close()

    db = open_state(path)
    resumed_no, resumed_files = next_batch(db, "source-A", "fi")
    assert (resumed_no, resumed_files) == (batch_no, ["a"])
    add_eligible(db, "source-A", "fi", [{"text": "first", "source": "source-A", "language": "fi"}])
    finish_batch(db, "source-A", "fi", batch_no, {"a": "a".ljust(64, "0")})
    report = task_report(db, "source-A", "fi")
    assert report["retained_unique_post_filter"] == 1
    assert report["shortfall"] == 1
    assert report["incomplete_file_batches"] == 1


def test_waiting_source_adapter_uses_durable_file_batches_and_reports_shortfalls():
    from pathlib import Path
    worker = (Path(__file__).resolve().parents[1] / "scripts/acquire_waiting_sources.py").read_text()
    assert 'temp_root = output_root / ".work"' in worker
    assert 'state_path = args.state_db or (output_root / f"acquisition-state-{policy_digest}.sqlite")' in worker
    assert 'policy_digest = hashlib.sha256(' in worker
    assert "plan_file_batches(" in worker
    assert "next_batch(state_db" in worker
    assert "finish_batch(state_db" in worker
    assert "begin_remote_file(" in worker
    assert "finish_remote_file(" in worker
    assert "row_groups=[row_group]" in worker
    assert "Quota reached before end of" in worker
    assert "stream_exhausted = True" in worker
    assert "if failures or incomplete_tasks:" in worker
    assert '"acquisition_failures": failures' in worker
    assert "dataset.load_state_dict(saved[\"state\"])" in worker
    assert "persist_arabic_stream_state()" in worker
    assert '"source_language_status": task_status' in worker
    assert "inspect source_language_status for exact retained counts and shortfalls" in worker


def test_new_file_version_reopens_previously_exhausted_task(tmp_path):
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "fi", 3, ["old#sha256=" + "a" * 64], 1)
    batch_no, files = next_batch(db, "source-A", "fi")
    finish_batch(db, "source-A", "fi", batch_no, {files[0]: "a" * 64})
    assert mark_exhausted(db, "source-A", "fi") == 3
    assert task_complete(db, "source-A", "fi")
    assert plan_file_batches(db, "source-A", "fi", 3, ["new#sha256=" + "b" * 64], 1) == 1
    assert not task_complete(db, "source-A", "fi")
    assert next_batch(db, "source-A", "fi")[1] == ["new#sha256=" + "b" * 64]


def test_interrupted_batch_rolls_back_uncommitted_rows_for_safe_replay(tmp_path):
    import sqlite3
    path = tmp_path / "state.sqlite"
    db = open_state(path)
    plan_file_batches(db, "source-A", "fi", 2, ["one-file"], 1)
    batch_no, _ = next_batch(db, "source-A", "fi")
    assert add_eligible(db, "source-A", "fi", [{
        "text": "one durable sentence", "source": "source-A", "language": "fi"
    }]) == 1
    observer = sqlite3.connect(path)
    assert observer.execute("SELECT COUNT(*) FROM sentence").fetchone()[0] == 0
    observer.close()
    db.close()  # simulates interruption before finish_batch
    db = open_state(path)
    assert retained_count(db, "source-A", "fi") == 0
    resumed_no, resumed_files = next_batch(db, "source-A", "fi")
    assert (resumed_no, resumed_files) == (batch_no, ["one-file"])
    add_eligible(db, "source-A", "fi", [{
        "text": "one durable sentence", "source": "source-A", "language": "fi"
    }])
    finish_batch(db, "source-A", "fi", batch_no, {"one-file": "a" * 64})
    assert retained_count(db, "source-A", "fi") == 1


def test_transient_http_errors_are_retryable_but_permanent_errors_are_not():
    class HttpError(Exception):
        def __init__(self, status):
            super().__init__(f"HTTP status {status}")
            self.status = status

    assert is_retryable_remote_error(HttpError(429))
    assert is_retryable_remote_error(HttpError(503))
    assert is_retryable_remote_error(TimeoutError("read timed out"))
    assert not is_retryable_remote_error(HttpError(404))
    assert not is_retryable_remote_error(ValueError("invalid parquet schema"))


def test_retry_delay_uses_capped_exponential_backoff():
    assert [retry_delay_seconds(n, 5, 120) for n in range(1, 9)] == [
        5, 10, 20, 40, 80, 120, 120, 120
    ]
