import hashlib
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_gaois_irish_legislation.py"
SPEC = importlib.util.spec_from_file_location("acquire_gaois_irish_legislation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _archive(xml_text):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("legislation.tmx", xml_text)
    return buffer.getvalue()


def _tu(identifier, gaelic, english):
    return (
        f'<tu tuid="{identifier}">'
        f'<tuv xml:lang="ga"><seg>{gaelic}</seg></tuv>'
        f'<tuv xml:lang="en"><seg>{english}</seg></tuv>'
        "</tu>"
    )


def _run_sample(tmp_path, monkeypatch, cap):
    first = _archive(
        "<tmx><body>"
        + _tu("ga-1", "Tá an córas oideachais ag freastal ar phobal na tíre ar fud na bliana.",
              "English translation that must never be emitted as candidate text.")
        + _tu("ga-2", "Tá seirbhísí poiblí ar fáil do dhaoine ar fud na tíre agus i ngach ceantar.",
              "A second English translation retained only as a hash.")
        + "</body></tmx>"
    )
    second = _archive(
        "<tmx><body>"
        + _tu("ga-3", "Tá an córas oideachais ag freastal ar phobal na tíre ar fud na bliana.",
              "Duplicate Irish translation with another English rendering.")
        + _tu("en-only", "", "English-only unit must not enter the Irish candidate pool.")
        + "</body></tmx>"
    )
    payloads = {"https://fixture.invalid/first.zip": first,
                "https://fixture.invalid/second.zip": second}
    downloads = {}

    def fake_download(url, path, execution):
        payload = payloads[url]
        path.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        downloads[url] = digest
        return {"url": url, "bytes": len(payload), "sha256": digest}

    monkeypatch.setattr(MODULE, "SOURCES", [
        ("constitution", "https://fixture.invalid/first.zip"),
        ("primary", "https://fixture.invalid/second.zip"),
    ])
    monkeypatch.setattr(MODULE, "download", fake_download)
    combined = hashlib.sha256("".join(downloads.get(url, hashlib.sha256(payloads[url]).hexdigest())
                                      for url in payloads).encode()).hexdigest()
    monkeypatch.setattr(MODULE, "EXPECTED_COMBINED_SHA256", combined)
    output = tmp_path / f"gaois-{cap}" / "candidates.jsonl"
    monkeypatch.setattr(sys, "argv", [
        "acquire_gaois_irish_legislation.py", "--out", str(output),
        "--max-sample", str(cap), "--seed", "gaois-test-seed",
    ])
    MODULE.main()
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    manifest = json.loads(output.with_name("manifest.json").read_text(encoding="utf-8"))
    return rows, manifest


def test_gaois_emits_only_deterministic_irish_sample_and_hashes_english_side(tmp_path, monkeypatch):
    rows, manifest = _run_sample(tmp_path, monkeypatch, 2)

    assert len(rows) == 2
    assert {row["language"] for row in rows} == {"ga"}
    assert {row["source"] for row in rows} == {"gaois_irish_legislation"}
    assert manifest["counts"]["distinct_clean_irish_segments"] == 2
    assert manifest["counts"]["duplicate_irish_segments"] == 1
    assert manifest["quota_status"] == "quota_reached"
    assert manifest["quota_reached"] is True
    assert manifest["source_exhausted"] is False
    assert manifest["source_language_counts"] == {"gaois_irish_legislation:ga": 2}
    serialized = json.dumps(rows, ensure_ascii=False)
    assert "English translation" not in serialized
    assert all(row["provenance"]["english_segment_sha256"] for row in rows)
    assert all(row["provenance"]["english_segment_characters"] > 0 for row in rows)
    assert all(row["source_release"].endswith(manifest["combined_release_sha256"]) for row in rows)
    assert manifest["combined_release_sha256"] == MODULE.EXPECTED_COMBINED_SHA256


def test_gaois_reports_source_exhaustion_when_fewer_than_50k_eligible_segments(tmp_path, monkeypatch):
    rows, manifest = _run_sample(tmp_path, monkeypatch, 5)

    assert len(rows) == 2
    assert manifest["quota_status"] == "source_exhausted"
    assert manifest["quota_reached"] is False
    assert manifest["source_exhausted"] is True
