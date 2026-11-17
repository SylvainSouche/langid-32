#!/usr/bin/env python3
"""Download Common Voice MDC datasets and persist only validated_sentences.tsv.

The script reads dataset IDs and per-dataset API-key environment-variable names
from data/common-voice-mdc-datasets.json. It streams each archive, writes only
the validated text TSV, and keeps a local hash/provenance manifest. No audio is
saved. Respect the terms accepted for each dataset; never mirror the source
datasets or identify contributors.
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

API = "https://mozilladatacollective.com/api"
MAX_DOWNLOADS_PER_RUN = 7


def load_datasets(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    datasets = data.get("datasets")
    if not isinstance(datasets, list):
        raise RuntimeError(f"{path} has no datasets array.")
    return datasets


def api_download_url(dataset_id: str, api_key: str) -> dict:
    request = urllib.request.Request(
        f"{API}/datasets/{dataset_id}/download",
        data=b"",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "langid-32/0.2",
        },
        method="POST",
    )
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
        raise RuntimeError(
            f"{messages.get(exc.code, f'MDC API error {exc.code}.')} {detail}"
        ) from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Unexpected MDC API response (expected a JSON object).")
    return payload


def extract_validated_tsv(url: str, destination: Path) -> tuple[int, str]:
    """Stream the tarball; persist only the target TSV and consume the full archive."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    found = False
    digest = hashlib.sha256()
    byte_count = 0
    try:
        with urllib.request.urlopen(url, timeout=180) as response:
            # Streaming through the end also lets gzip validate its trailer/CRC.
            with tarfile.open(fileobj=response, mode="r|gz") as archive:
                for member in archive:
                    if not member.isfile():
                        continue
                    if PurePosixPath(member.name).name != "validated_sentences.tsv":
                        continue
                    if found:
                        raise RuntimeError(
                            "Archive contains multiple validated_sentences.tsv files."
                        )
                    source = archive.extractfile(member)
                    if source is None:
                        raise RuntimeError("Could not read validated_sentences.tsv.")
                    with source, destination.open("wb") as target:
                        while True:
                            block = source.read(1024 * 1024)
                            if not block:
                                break
                            target.write(block)
                            digest.update(block)
                            byte_count += len(block)
                    found = True
        if not found:
            raise RuntimeError("validated_sentences.tsv was not found in the archive.")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return byte_count, digest.hexdigest()


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
    parser.add_argument(
        "--manifest", type=Path,
        default=Path(__file__).resolve().parents[1] / "data/common-voice-mdc-datasets.json",
        help="Dataset manifest (default: repository data/common-voice-mdc-datasets.json).",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--locales", help="Optional comma-separated locale allow-list, e.g. fr,de,pl."
    )
    parser.add_argument(
        "--batch-index", type=int, default=0,
        help="Zero-based batch number; each batch contains at most seven datasets.",
    )
    parser.add_argument(
        "--max-downloads", type=int, default=MAX_DOWNLOADS_PER_RUN,
        help="Maximum downloads in this invocation (1-7).",
    )
    args = parser.parse_args()
    if not 1 <= args.max_downloads <= MAX_DOWNLOADS_PER_RUN:
        parser.error(f"--max-downloads must be between 1 and {MAX_DOWNLOADS_PER_RUN}.")
    if args.batch_index < 0:
        parser.error("--batch-index must be zero or greater.")

    locales = None
    if args.locales:
        locales = {value.strip() for value in args.locales.split(",") if value.strip()}
        if not locales:
            parser.error("--locales did not contain any locale codes.")

    datasets = load_datasets(args.manifest)
    batch = choose_batch(datasets, locales, args.batch_index, args.max_downloads)
    if not batch:
        print("No eligible datasets in this batch.")
        return 0

    # Validate all credentials before making the first API request.
    missing = sorted({
        item["api_key_env"] for item in batch if not os.environ.get(item["api_key_env"])
    })
    if missing:
        parser.error(
            "Missing API-key environment variable(s): " + ", ".join(missing)
            + ". Set them locally; never put secret values in the manifest or command line."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "mdc-download-manifest.json"
    if manifest_path.exists():
        local_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        local_manifest = {
            "source": "Mozilla Common Voice Scripted Speech 27.0",
            "method": "official MDC API; streamed archive; validated_sentences.tsv only",
            "results": [],
        }
    previous = {
        (row.get("locale"), row.get("dataset_id"))
        for row in local_manifest.get("results", [])
    }

    for item in batch:
        locale = item["locale"]
        dataset_id = item["dataset_id"]
        if (locale, dataset_id) in previous:
            print(f"Skipping {locale}: already recorded in local download manifest.")
            continue
        key_env = item["api_key_env"]
        print(f"Requesting MDC download: {locale} ({dataset_id}) using ${key_env}...", flush=True)
        access = api_download_url(dataset_id, os.environ[key_env])
        url = access.get("downloadUrl")
        if not url:
            raise RuntimeError(f"MDC response for {locale} did not contain downloadUrl.")
        destination = args.output_dir / locale / "validated_sentences.tsv"
        size, sha256 = extract_validated_tsv(url, destination)
        local_manifest["results"].append({
            "locale": locale,
            "target_language_code": item.get("target_language_code"),
            "dataset_id": dataset_id,
            "api_key_env": key_env,
            "filename": access.get("filename"),
            "archive_size_bytes": access.get("sizeBytes"),
            "archive_checksum_sha256_expected": access.get("checksum"),
            "archive_checksum_verified": False,
            "extracted_file": str(destination),
            "extracted_bytes": size,
            "extracted_sha256": sha256,
            "access_record_id": access.get("accessRecordId"),
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "note": "Only validated_sentences.tsv persisted; archive streamed to completion; no audio saved.",
        })
        previous.add((locale, dataset_id))
        print(f"Extracted {locale}: {size:,} bytes; sha256={sha256}", flush=True)

    local_manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(
        json.dumps(local_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Local manifest: {manifest_path}")
    print("Source archives and audio were not saved. Keep extracted source TSVs private.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, urllib.error.URLError, tarfile.TarError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
