import json
import sqlite3

from langid32.acquisition_batches import (
    add_eligible, finish_batch, mark_exhausted, next_batch, open_state,
    plan_file_batches, retained_count, task_complete,
)


def test_target_counts_only_unique_eligible_records_and_continues(tmp_path):
    db = open_state(tmp_path / "state.sqlite")
    assert plan_file_batches(db, "source-A", "fi", 3, ["a", "b", "c"], 1) == 3
    batch_no, files = next_batch(db, "source-A", "fi")
    assert files == ["a"]
    assert add_eligible(db, "source-A", "fi", [
        {"text": "one"}, {"text": "one"}, {"text": "two"}
    ]) == 2
    finish_batch(db, "source-A", "fi", batch_no, {"a": "sha-a"})
    assert not task_complete(db, "source-A", "fi")
    batch_no, files = next_batch(db, "source-A", "fi")
    assert files == ["b"]
    assert add_eligible(db, "source-A", "fi", [{"text": "three"}, {"text": "four"}]) == 1
    finish_batch(db, "source-A", "fi", batch_no, {"b": "sha-b"})
    assert retained_count(db, "source-A", "fi") == 3
    assert task_complete(db, "source-A", "fi")
    assert next_batch(db, "source-A", "fi") is None


def test_exhaustion_reports_exact_shortfall_and_source_isolation(tmp_path):
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "fi", 5, ["a"], 1)
    plan_file_batches(db, "source-B", "fi", 5, ["b"], 1)
    add_eligible(db, "source-A", "fi", [{"text": "same"}])
    assert mark_exhausted(db, "source-A", "fi") == 4
    assert task_complete(db, "source-A", "fi")
    assert retained_count(db, "source-B", "fi") == 0
    assert not task_complete(db, "source-B", "fi")


def test_completed_files_are_not_replanned(tmp_path):
    db = open_state(tmp_path / "state.sqlite")
    plan_file_batches(db, "source-A", "is", 2, ["a", "b"], 1)
    batch_no, _ = next_batch(db, "source-A", "is")
    finish_batch(db, "source-A", "is", batch_no, {"a": "sha-a"})
    # Existing planned file paths are not duplicated when discovery is repeated.
    assert plan_file_batches(db, "source-A", "is", 2, ["a", "b", "c"], 1) == 1
