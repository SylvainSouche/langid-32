#!/usr/bin/env python3
"""Download only validated_sentences.tsv from authorised Common Voice MDC datasets.

Archives are temporary, checksum-checked when MDC supplies a SHA-256, and
deleted immediately after extraction. Successful locales are recorded
incrementally so a later locale failure never discards earlier work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tarfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile

API = "https://mozilladatacollective.com/api"
MAX_DOWNLOADS_PER_RUN = 7


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_manifest(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".part")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def load_datasets(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    datasets = data.get("datasets")
    if not isinstance(datasets, list):
        raise RuntimeError(f"{path} has no datasets array.")
    return datasets


def api_download_url(dataset_id: str, api_key: str) -> dict:
    request = urllib.request.Request(
        f"{API}/datasets/{dataset_id}/download", data=b"",
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json",
                 "User-Agent": "langid-32/0.3"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", "replace")
        messages = {
            401: "MDC rejected this dataset's API key (401).",
            402: "MDC reports payment required (402).",
            403: "MDC has not recorded the required profile/terms/access approval (403).",
            404: "Dataset ID not found (404).",
            410: "Dataset is no longer available (410).",
            429: "MDC download quota/rate limit reached (429). Respect Retry-After.",
        }
        raise RuntimeError(f"{messages.get(exc.code, f'MDC API error {exc.code}.')} {detail}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected MDC API response (expected a JSON object).")
    return payload


def download_archive(url: str, path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(url, timeout=240) as response, path.open("wb") as target:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            target.write(block)
            digest.update(block)
            size += len(block)
        target.flush()
        os.fsync(target.fileno())
    return size, digest.hexdigest()


def extract_validated_tsv(archive_path: Path, destination: Path) -> tuple[int, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    found = False
    digest = hashlib.sha256()
    count = 0
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            for member in archive:
                if not member.isfile() or PurePosixPath(member.name).name != "validated_sentences.tsv":
                    continue
                if found:
                    raise RuntimeError("Archive contains multiple validated_sentences.tsv files.")
                source = archive.extractfile(member)
                if source is None:
                    raise RuntimeError("Could not read validated_sentences.tsv.")
                with source, partial.open("wb") as target:
                    while True:
                        block = source.read(1024 * 1024)
                        if not block:
                            break
                        target.write(block)
                        digest.update(block)
                        count += len(block)
                    target.flush()
                    os.fsync(target.fileno())
                found = True
        if not found:
            raise RuntimeError("validated_sentences.tsv was not found in the archive.")
        partial.replace(destination)
    except Exception:
        partial.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)
        raise
    return count, digest.hexdigest()


def choose_batch(datasets: list[dict], locales: set[str] | None,
                 batch_index: int, batch_size: int) -> list[dict]:
    eligible = []
    for item in datasets:
        locale = item.get("locale")
        if locales is not None and locale not in locales:
            continue
        if item.get("scope_status") == "outside_current_32_language_target_set":
            continue
        if item.get("download_status") in {"do_not_download", "already_downloaded_by_user"}:
            continue
        if item.get("terms_reviewed_by_user") is not True:
            continue
        if not item.get("dataset_id") or not item.get("api_key_env"):
            raise RuntimeError(f"Manifest entry {locale!r} lacks dataset_id/api_key_env.")
        eligible.append(item)
    start = batch_index * batch_size
    return eligible[start:start + batch_size]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
        default=Path(__file__).resolve().parents[1] / "data/common-voice-mdc-datasets.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--locales")
    parser.add_argument("--batch-index", type=int, default=0)
    parser.add_argument("--max-downloads", type=int, default=MAX_DOWNLOADS_PER_RUN)
    parser.add_argument("--retries", type=int, choices=[0], default=0, help="Fixed at zero: each MDC download request is attempted exactly once.")
    args = parser.parse_args()
    if not 1 <= args.max_downloads <= MAX_DOWNLOADS_PER_RUN:
        parser.error(f"--max-downloads must be between 1 and {MAX_DOWNLOADS_PER_RUN}.")
    if args.batch_index < 0:
        parser.error("--batch-index must be zero or greater.")
    locales = None if not args.locales else {v.strip() for v in args.locales.split(",") if v.strip()}
    if args.locales and not locales:
        parser.error("--locales did not contain any locale codes.")

    batch = choose_batch(load_datasets(args.manifest), locales, args.batch_index, args.max_downloads)
    if not batch:
        print("No eligible datasets in this batch.")
        return 0
    missing = sorted({x["api_key_env"] for x in batch if not os.environ.get(x["api_key_env"])})
    if missing:
        parser.error("Missing API-key environment variable(s): " + ", ".join(missing))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "mdc-download-manifest.json"
    local = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {
        "source": "Mozilla Common Voice Scripted Speech 27.0",
        "method": "official MDC API; temporary archive; validated_sentences.tsv only",
        "results": [], "failures": []}
    local.setdefault("results", [])
    local.setdefault("failures", [])

    failed = False
    for item in batch:
        locale, dataset_id, key_env = item["locale"], item["dataset_id"], item["api_key_env"]
        destination = args.output_dir / locale / "validated_sentences.tsv"
        existing = next((r for r in local["results"]
                         if r.get("locale") == locale and r.get("dataset_id") == dataset_id), None)
        if existing and destination.is_file():
            actual = hashlib.sha256(destination.read_bytes()).hexdigest()
            if actual == existing.get("extracted_sha256"):
                print(f"Skipping {locale}: existing TSV matches its recorded SHA-256.", flush=True)
                continue
        print(f"Requesting MDC download: {locale} ({dataset_id}) using ${key_env}...", flush=True)
        success = False
        last_error = None
        for attempt in range(1):
            archive_path = args.output_dir / f".{locale}.archive.part"
            archive_path.unlink(missing_ok=True)
            try:
                access = api_download_url(dataset_id, os.environ[key_env])
                url = access.get("downloadUrl")
                if not url:
                    raise RuntimeError(f"MDC response for {locale} did not contain downloadUrl.")
                archive_size, archive_sha = download_archive(url, archive_path)
                expected = str(access.get("checksum") or "").strip().lower()
                checksum_verified = False
                if len(expected) == 64 and all(ch in "0123456789abcdef" for ch in expected):
                    if archive_sha != expected:
                        raise RuntimeError(f"Archive SHA-256 mismatch for {locale}: expected checksum did not match.")
                    checksum_verified = True
                size, sha = extract_validated_tsv(archive_path, destination)
                row = {
                    "locale": locale, "target_language_code": item.get("target_language_code"),
                    "dataset_id": dataset_id, "api_key_env": key_env,
                    "filename": access.get("filename"), "archive_size_bytes": archive_size,
                    "archive_checksum_sha256_expected": access.get("checksum"),
                    "archive_sha256_actual": archive_sha, "archive_checksum_verified": checksum_verified,
                    "extracted_file": str(destination), "extracted_bytes": size,
                    "extracted_sha256": sha, "access_record_id": access.get("accessRecordId"),
                    "downloaded_at_utc": now(),
                    "note": "Archive deleted after extraction; only validated_sentences.tsv persisted; no audio saved."
                }
                local["results"] = [r for r in local["results"]
                                    if not (r.get("locale") == locale and r.get("dataset_id") == dataset_id)]
                local["results"].append(row)
                local["failures"] = [r for r in local["failures"]
                                     if not (r.get("locale") == locale and r.get("dataset_id") == dataset_id)]
                save_manifest(manifest_path, local)
                print(f"Extracted {locale}: {size:,} bytes; TSV sha256={sha}; archive sha256={archive_sha}; checksum_verified={checksum_verified}", flush=True)
                success = True
                break
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                destination.unlink(missing_ok=True)
            finally:
                archive_path.unlink(missing_ok=True)
        if not success:
            failed = True
            local["failures"] = [r for r in local["failures"]
                                 if not (r.get("locale") == locale and r.get("dataset_id") == dataset_id)]
            local["failures"].append({"locale": locale, "dataset_id": dataset_id,
                                      "download_attempts": 1, "error": last_error,
                                      "failed_at_utc": now()})
            save_manifest(manifest_path, local)
            print(f"FAILED {locale} after its single download attempt: {last_error}", file=sys.stderr, flush=True)
    local["updated_at_utc"] = now()
    save_manifest(manifest_path, local)
    print(f"Local manifest: {manifest_path}")
    print("Temporary archives removed; raw source TSVs remain private to this runner.")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, urllib.error.URLError, tarfile.TarError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
