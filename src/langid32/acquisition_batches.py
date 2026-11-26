"""Deterministic, resumable file-batch accounting for source/language acquisition.

Adapters own discovery, download, parsing and policy filtering. This module owns
file batching and durable post-filter unique accounting. A record is counted
only after the adapter has applied all required filters and passed its text.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Iterable, Mapping, Sequence


_RETRYABLE_HTTP_STATUSES = {408, 425, 429, 500, 502, 503, 504}


def is_retryable_remote_error(exc: BaseException) -> bool:
    """Return true only for transient HTTP/transport failures suitable for replay."""
    pending = [exc]
    seen = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        for attr in ("status", "status_code", "code"):
            value = getattr(current, attr, None)
            try:
                if int(value) in _RETRYABLE_HTTP_STATUSES:
                    return True
            except (TypeError, ValueError):
                pass
        for attr in ("response", "__cause__", "__context__"):
            nested = getattr(current, attr, None)
            if nested is not None:
                pending.append(nested)
        if isinstance(current, (TimeoutError, ConnectionError, EOFError, BrokenPipeError)):
            return True
        message = str(current).casefold()
        if any(token in message for token in (
            "http 408", "http 425", "http 429", "http 500", "http 502",
            "http 503", "http 504", "status code 429", "status=429",
            "timed out", "timeout", "connection reset", "connection aborted",
            "server disconnected", "remote end closed", "incomplete read",
            "temporarily unavailable",
        )):
            return True
    return False


def retry_delay_seconds(attempt: int, base_seconds: int, max_seconds: int) -> int:
    """Deterministic capped exponential backoff; attempt numbering starts at one."""
    if attempt < 1 or base_seconds < 1 or max_seconds < 1:
        raise ValueError("attempt, base_seconds and max_seconds must be positive")
    return min(base_seconds * (2 ** (attempt - 1)), max_seconds)


def open_state(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(str(path), timeout=60)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS task (
            source TEXT NOT NULL, language TEXT NOT NULL,
            target INTEGER NOT NULL, exhausted INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(source, language)
        );
        CREATE TABLE IF NOT EXISTS file_batch (
            source TEXT NOT NULL, language TEXT NOT NULL, batch_no INTEGER NOT NULL,
            files_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
            PRIMARY KEY(source, language, batch_no)
        );
        CREATE TABLE IF NOT EXISTS sentence (
            source TEXT NOT NULL, language TEXT NOT NULL, text_sha256 TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY(source, language, text_sha256)
        );
        CREATE TABLE IF NOT EXISTS processed_file (
            source TEXT NOT NULL, language TEXT NOT NULL, path TEXT NOT NULL,
            sha256 TEXT NOT NULL, batch_no INTEGER NOT NULL,
            PRIMARY KEY(source, language, path)
        );
    """)
    return db


def plan_file_batches(db: sqlite3.Connection, source: str, language: str,
                      target: int, files: Sequence[str], files_per_batch: int) -> int:
    """Append deterministic batches; already planned/processed paths are retained."""
    if not source or not language or target < 1 or files_per_batch < 1:
        raise ValueError("source, language, positive target and batch size are required")
    db.execute(
        "INSERT INTO task(source,language,target) VALUES(?,?,?) "
        "ON CONFLICT(source,language) DO UPDATE SET target=excluded.target",
        (source, language, target),
    )
    known = {row[0] for row in db.execute(
        "SELECT path FROM processed_file WHERE source=? AND language=?", (source, language))}
    known.update(path for row in db.execute(
        "SELECT files_json FROM file_batch WHERE source=? AND language=?", (source, language))
        for path in json.loads(row[0]))
    pending = [path for path in sorted({str(item) for item in files}) if path not in known]
    next_no = db.execute(
        "SELECT COALESCE(MAX(batch_no),-1)+1 FROM file_batch WHERE source=? AND language=?",
        (source, language)).fetchone()[0]
    created = 0
    for offset in range(0, len(pending), files_per_batch):
        group = pending[offset:offset + files_per_batch]
        db.execute("INSERT INTO file_batch(source,language,batch_no,files_json) VALUES(?,?,?,?)",
                   (source, language, next_no, json.dumps(group, ensure_ascii=False)))
        next_no += 1
        created += 1
    # A previously exhausted source can acquire new immutable file versions
    # after upstream refresh. New planned work must reopen that task.
    if created:
        db.execute(
            "UPDATE task SET exhausted=0 WHERE source=? AND language=?",
            (source, language),
        )
    db.commit()
    return created


def next_batch(db: sqlite3.Connection, source: str, language: str):
    """Return and mark the next incomplete batch; interrupted running batches are retryable."""
    if task_complete(db, source, language):
        return None
    row = db.execute(
        "SELECT batch_no,files_json FROM file_batch "
        "WHERE source=? AND language=? AND status IN ('pending','running') "
        "ORDER BY batch_no LIMIT 1", (source, language)).fetchone()
    if row is None:
        return None
    db.execute(
        "UPDATE file_batch SET status='running' WHERE source=? AND language=? AND batch_no=?",
        (source, language, row[0]))
    db.commit()
    return row[0], json.loads(row[1])


def pending_batch_count(db: sqlite3.Connection, source: str, language: str) -> int:
    return db.execute(
        "SELECT COUNT(*) FROM file_batch WHERE source=? AND language=? AND status!='complete'",
        (source, language)).fetchone()[0]


def retained_count(db: sqlite3.Connection, source: str, language: str) -> int:
    return db.execute("SELECT COUNT(*) FROM sentence WHERE source=? AND language=?",
                      (source, language)).fetchone()[0]


def task_complete(db: sqlite3.Connection, source: str, language: str) -> bool:
    row = db.execute("SELECT target,exhausted FROM task WHERE source=? AND language=?",
                     (source, language)).fetchone()
    return bool(row and (retained_count(db, source, language) >= row[0] or row[1]))


def add_eligible(db: sqlite3.Connection, source: str, language: str,
                 records: Iterable[Mapping]) -> int:
    """Insert screened records; the enclosing file/row-group batch commits them."""
    task = db.execute("SELECT target FROM task WHERE source=? AND language=?",
                      (source, language)).fetchone()
    if task is None:
        raise ValueError(f"Unplanned source/language task: {source}/{language}")
    inserted = 0
    count = retained_count(db, source, language)
    for record in records:
        if count >= task[0]:
            break
        if str(record.get("source", source)) != source or str(record.get("language", language)) != language:
            raise ValueError("Record source/language does not match its exact acquisition task")
        text = " ".join(str(record.get("text", "")).split())
        if not text:
            continue
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        payload = dict(record)
        payload["text"] = text
        cursor = db.execute(
            "INSERT OR IGNORE INTO sentence(source,language,text_sha256,payload_json) VALUES(?,?,?,?)",
            (source, language, digest, json.dumps(payload, ensure_ascii=False, sort_keys=True)))
        if cursor.rowcount:
            inserted += 1
            count += 1
    # Deliberately do not commit here. finish_batch commits the complete
    # file/row-group transaction; interrupted batches roll back and replay.
    return inserted


def finish_batch(db: sqlite3.Connection, source: str, language: str, batch_no: int,
                 file_hashes: Mapping[str, str]) -> None:
    row = db.execute(
        "SELECT files_json FROM file_batch WHERE source=? AND language=? AND batch_no=?",
        (source, language, batch_no)).fetchone()
    if row is None:
        raise KeyError((source, language, batch_no))
    expected = set(json.loads(row[0]))
    valid_hashes = all(
        len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())
        for value in file_hashes.values()
    )
    if set(file_hashes) != expected or not valid_hashes:
        raise ValueError("A batch can complete only when every planned file has a valid SHA-256")
    db.executemany(
        "INSERT OR REPLACE INTO processed_file(source,language,path,sha256,batch_no) VALUES(?,?,?,?,?)",
        [(source, language, path, file_hashes[path], batch_no) for path in sorted(expected)])
    db.execute("UPDATE file_batch SET status='complete' WHERE source=? AND language=? AND batch_no=?",
               (source, language, batch_no))
    db.commit()


def mark_exhausted(db: sqlite3.Connection, source: str, language: str) -> int:
    pending = pending_batch_count(db, source, language)
    if pending:
        raise RuntimeError(f"Cannot mark {source}/{language} exhausted with {pending} incomplete batches")
    db.execute("UPDATE task SET exhausted=1 WHERE source=? AND language=?", (source, language))
    db.commit()
    row = db.execute("SELECT target FROM task WHERE source=? AND language=?",
                     (source, language)).fetchone()
    if row is None:
        raise KeyError((source, language))
    return max(0, row[0] - retained_count(db, source, language))


def export_records(db: sqlite3.Connection, source: str, language: str) -> list[dict]:
    return [json.loads(row[0]) for row in db.execute(
        "SELECT payload_json FROM sentence WHERE source=? AND language=? ORDER BY rowid",
        (source, language))]



def task_report(db: sqlite3.Connection, source: str, language: str) -> dict:
    row = db.execute(
        "SELECT target,exhausted FROM task WHERE source=? AND language=?",
        (source, language)).fetchone()
    if row is None:
        raise KeyError((source, language))
    retained = retained_count(db, source, language)
    return {
        "source": source,
        "language": language,
        "target": row[0],
        "retained_unique_post_filter": retained,
        "shortfall": max(0, row[0] - retained),
        "source_exhausted": bool(row[1]),
        "complete": bool(retained >= row[0] or row[1]),
        "incomplete_file_batches": pending_batch_count(db, source, language),
    }
