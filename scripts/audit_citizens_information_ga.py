#!/usr/bin/env python3
"""Resolve the EU catalogue record and test the retired ELRC-SHARE access route."""
from __future__ import annotations
import hashlib, json, urllib.error, urllib.request
from pathlib import Path

DATASET_ID = "elrc_2438"
API = "https://data.europa.eu/api/hub/search/ckan/package_show?id=" + DATASET_ID
OUT = Path("citizens-information-ga-audit.json")
UA = "langid-32-source-audit/1.0 (metadata and access-route audit)"

def request(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/zip,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read(2_000_000)
            return {"status": response.status, "final_url": response.geturl(),
                    "content_type": response.headers.get("Content-Type"),
                    "content_length": response.headers.get("Content-Length"),
                    "body_bytes_read": len(body), "body_sha256": hashlib.sha256(body).hexdigest(),
                    "body_preview": body[:1200].decode("utf-8", "replace")}
    except urllib.error.HTTPError as exc:
        body = exc.read(2_000_000)
        return {"status": exc.code, "final_url": exc.geturl(),
                "content_type": exc.headers.get("Content-Type"),
                "body_bytes_read": len(body), "body_sha256": hashlib.sha256(body).hexdigest(),
                "body_preview": body[:1200].decode("utf-8", "replace")}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}

def main() -> None:
    api_result = request(API)
    if api_result.get("status") != 200:
        raise RuntimeError(f"package_show failed: {api_result}")
    metadata = json.loads(api_result.pop("body_preview") + "") if False else None
    req = urllib.request.Request(API, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        metadata = json.loads(response.read())
    if not metadata.get("success"):
        raise RuntimeError("data.europa.eu package_show did not return success")
    pkg = metadata["result"]
    resources = []
    for r in pkg.get("resources", []):
        raw = r.get("access_url") or r.get("url") or r.get("download_url")
        urls = []
        if isinstance(raw, list):
            urls = raw
        elif isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                urls = parsed if isinstance(parsed, list) else [raw]
            except json.JSONDecodeError:
                urls = [raw]
        for url in urls:
            if not isinstance(url, str) or not url.startswith(("https://", "http://")):
                continue
            resources.append({
                "id": r.get("id"), "format": r.get("format"), "access_url": url,
                "license": r.get("license"), "date_updated": r.get("date_updated"),
                "probe": request(url)
            })
    report = {
        "dataset_id": DATASET_ID, "title": pkg.get("title"),
        "license_title": pkg.get("license_title"), "license_url": pkg.get("license_url"),
        "publisher": pkg.get("organization"), "metadata_url": API,
        "resources": resources,
        "catalogue_claim": "10,297 manually cleaned parallel English-Irish sentences; ZIP/TMX; CC BY 4.0",
        "result": "ACCESS_ROUTE_RETIRED_OR_UNAVAILABLE" if not any(r["probe"].get("content_type", "").lower().startswith(("application/zip", "application/x-zip")) for r in resources) else "POSSIBLE_ARCHIVE_ACCESS",
        "method": "Read the official data.europa.eu CKAN package_show record, decoded the resource access_url field, and probed each published URL. No source text was downloaded or counted."
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
