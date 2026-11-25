import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPS = ROOT / "scripts" / "corpus_ops.py"


def run_ops(*args):
    return subprocess.run(
        [sys.executable, str(OPS), *map(str, args)],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )


def test_filter_keeps_duplicates_and_only_drops_news_digits(tmp_path):
    source = tmp_path / "input.jsonl"
    rows = [
        {"text": "A news sentence dated 2026.", "language": "en", "source": "leipzig_news"},
        {"text": "Contact a.person@example.org for details.", "language": "en", "source": "leipzig_wikipedia"},
        {"text": "Contact a.person@example.org for details.", "language": "en", "source": "leipzig_wikipedia"},
        {"text": "A plain news sentence without digits.", "language": "en", "source": "leipzig_news"},
    ]
    source.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    filtered = tmp_path / "filtered.jsonl"
    report = tmp_path / "filter.json"
    run_ops("filter", "--input", source, "--output", filtered, "--report", report,
            "--min-chars", "1", "--max-chars", "0")
    kept = [json.loads(line) for line in filtered.read_text(encoding="utf-8").splitlines()]
    stats = json.loads(report.read_text(encoding="utf-8"))
    assert len(kept) == 3
    assert stats["counts"]["news_decimal_digit"] == 1
    assert stats["counts"]["duplicate_within_language_kept"] == 1


def test_redaction_preserves_rows_and_marks_redactions(tmp_path):
    source = tmp_path / "input.jsonl"
    source.write_text(json.dumps({
        "text": "Contact a.person@example.org or https://example.org",
        "language": "en", "source": "test",
    }) + "\n", encoding="utf-8")
    output = tmp_path / "redacted.jsonl"
    report = tmp_path / "redaction.json"
    run_ops("anonymize", "--input", source, "--output", output, "--report", report)
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert "[REDACTED_EMAIL]" in rows[0]["text"]
    assert "[REDACTED_URL]" in rows[0]["text"]
    assert rows[0]["anonymization"]["redaction_count"] == 2
