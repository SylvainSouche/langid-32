#!/usr/bin/env python3
"""Stream Common Voice MDC archives and extract only validated_sentences.tsv.

No full archive is written to disk. The extracted TSV is written to the
user-selected local output directory and must not be re-hosted or shared
where the dataset terms prohibit that.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tarfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

API = "https://mozilladatacollective.com/api"
MAX_DAILY_DOWNLOADS = 7


def api_download_url(dataset_id: str, api_key: str) -> dict:
    request = urllib.request.Request(
        f"{API}/datasets/{dataset_id}/download",
        data=b"",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "langid-32/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read(4096).decode("utf-8", "replace")
        messages = {
            401: "MDC rejected the API key (401).",
            402: "MDC reports payment required (402).",
            403: "MDC has not recorded the required profile/terms/access approval (403).",
            404: "Dataset ID not found (404).",
            410: "Dataset is no longer available (410).",
            429: "MDC download quota/rate limit reached (429). Respect Retry-After.",
        }
        raise RuntimeError(f"{messages.get(exc.code, f'MDC API error {exc.code}')} {detail}") from exc


def extract_tsv_stream(url: str, destination: Path) -> tuple[int, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    found = False
    digest = hashlib.sha256()
    byte_count = 0
    try:
        with urllib.request.urlopen(url, timeout=180) as response:
            with tarfile.open(fileobj=response, mode="r|gz") as archive:
                for member in archive:
                    if not member.isfile():
                        continue
                    if PurePosixPath(member.name).name != "validated_sentences.tsv":
                        continue
                    if found:
                        raise RuntimeError("Archive contains multiple validated_sentences.tsv files.")
                    source = archive.extractfile(member)
                    if source is None:
                        raise RuntimeError("Could not read validated_sentences.tsv from archive.")
                    with source, destination.open("wb") as target:
                        while True:
                            block = source.read(1024 * 1024)
                            if not block:
                                break
                            target.write(block)
                            digest.update(block)
                            byte_count += len(block)
                    found = True
                    break
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    if not found:
        destination.unlink(missing_ok=True)
        raise RuntimeError("validated_sentences.tsv was not found in the archive.")
    return byte_count, digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", action="append", required=True, metavar="LOCALE=DATASET_ID",
        help="Repeat for each user-approved locale; maximum 7 per UTC day.",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-downloads", type=int, default=MAX_DAILY_DOWNLOADS)
    args = parser.parse_args()

    if len(args.dataset) > min(args.max_downloads, MAX_DAILY_DOWNLOADS):
        parser.error(
            f"Refusing {len(args.dataset)} download requests: current documented "
            f"daily default is {MAX_DAILY_DOWNLOADS}. Run in batches."
        )
    api_key = os.environ.get("MDC_API_KEY")
    if not api_key:
        parser.error("Set MDC_API_KEY in the local environment; never put the key in a file or command line.")

    pairs = []
    seen = set()
    for item in args.dataset:
        if "=" not in item:
            parser.error(f"Invalid --dataset {item!r}; expected LOCALE=DATASET_ID")
        locale, dataset_id = item.split("=", 1)
        if not locale or not dataset_id or locale in seen:
            parser.error(f"Invalid or repeated locale in --dataset {item!r}")
        seen.add(locale)
        pairs.append((locale, dataset_id))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for locale, dataset_id in pairs:
        print(f"Requesting authorised MDC download for {locale} ({dataset_id})...", flush=True)
        access = api_download_url(dataset_id, api_key)
        url = access.get("downloadUrl")
        if not url:
            raise RuntimeError(f"MDC response for {locale} did not contain downloadUrl.")
        destination = args.output_dir / locale / "validated_sentences.tsv"
        size, sha256 = extract_tsv_stream(url, destination)
        results.append({
            "locale": locale,
            "dataset_id": dataset_id,
            "filename": access.get("filename"),
            "archive_size_bytes": access.get("sizeBytes"),
            "archive_checksum_sha256_expected": access.get("checksum"),
            "archive_checksum_verified": False,
            "extracted_file": str(destination),
            "extracted_bytes": size,
            "extracted_sha256": sha256,
            "access_record_id": access.get("accessRecordId"),
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "note": "Archive streamed; only validated_sentences.tsv persisted. No audio or contributor metadata extracted.",
        })
        print(f"Extracted {locale}: {size:,} bytes; sha256={sha256}", flush=True)

    manifest_path = args.output_dir / "mdc-download-manifest.json"
    manifest_path.write_text(
        json.dumps({
            "source": "Mozilla Common Voice Scripted Speech 27.0",
            "method": "official MDC API; streamed archive; validated_sentences.tsv only",
            "results": results,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Manifest: {manifest_path}")
    print("Do not upload, commit, or share the extracted dataset files.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, urllib.error.URLError, tarfile.TarError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
