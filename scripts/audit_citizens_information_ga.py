#!/usr/bin/env python3
"""Resolve and audit the Citizens Information English-Irish TMX distribution."""
from __future__ import annotations
import hashlib, json, os, re, sys, tempfile, urllib.request, zipfile
from pathlib import Path
from xml.etree.ElementTree import iterparse

DATASET_ID = "elrc_2438"
API = "https://data.europa.eu/api/hub/search/ckan/package_show?id=" + DATASET_ID
OUT = Path("citizens-information-ga-audit.json")
UA = "langid-32-source-audit/1.0 (metadata and corpus structure audit)"

def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()

def norm_lang(value: str | None) -> str:
    if not value:
        return ""
    v = value.lower().replace("_", "-")
    if v in {"ga", "gle", "ga-ie", "gle-ie"} or v.startswith(("ga-", "gle-")):
        return "ga"
    if v in {"en", "eng", "en-ie", "en-gb", "en-us"} or v.startswith("en-"):
        return "en"
    return v

def main() -> None:
    metadata = json.loads(get(API))
    if not metadata.get("success"):
        raise RuntimeError("data.europa.eu package_show did not return success")
    pkg = metadata["result"]
    resources = pkg.get("resources", [])
    selected = []
    for r in resources:
        fmt = str(r.get("format", "")).lower()
        name = str(r.get("name", ""))
        url = r.get("download_url") or r.get("url")
        if url and ("zip" in fmt or name.lower().endswith(".zip") or "tmx" in fmt):
            selected.append({"id": r.get("id"), "name": name, "format": fmt, "url": url,
                             "license": r.get("license"), "size": r.get("size")})
    if not selected:
        print(json.dumps({"dataset": DATASET_ID, "title": pkg.get("title"),
                          "license": pkg.get("license_title"), "resources": resources},
                         ensure_ascii=False, indent=2))
        raise RuntimeError("No downloadable ZIP/TMX resource found in package metadata")
    reports = []
    with tempfile.TemporaryDirectory() as td:
        for ix, resource in enumerate(selected):
            url = resource["url"]
            data = get(url)
            digest = hashlib.sha256(data).hexdigest()
            archive = Path(td) / f"resource-{ix}.zip"
            archive.write_bytes(data)
            files = []
            with zipfile.ZipFile(archive) as zf:
                for member in zf.infolist():
                    if member.is_dir() or not member.filename.lower().endswith((".tmx", ".xml")):
                        continue
                    counts = {"translation_units": 0, "ga_segments": 0, "en_segments": 0,
                              "other_segments": 0, "ga_chars": 0, "en_chars": 0,
                              "ga_whitespace_tokens": 0, "en_whitespace_tokens": 0,
                              "distinct_ga_sha256": 0, "duplicate_ga_segments": 0,
                              "distinct_pairs_sha256": 0}
                    ga_seen, pair_seen = set(), set()
                    with zf.open(member) as stream:
                        # iterparse clears TU nodes; count language-tagged segments and TU pairs.
                        for event, elem in iterparse(stream, events=("end",)):
                            tag = elem.tag.rsplit("}", 1)[-1]
                            if tag == "tu":
                                counts["translation_units"] += 1
                                segs = {}
                                for seg in elem.iter():
                                    if seg.tag.rsplit("}", 1)[-1] == "seg":
                                        lang = norm_lang(seg.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") or seg.attrib.get("lang"))
                                        txt = "".join(seg.itertext()).strip()
                                        if not txt:
                                            continue
                                        if lang == "ga":
                                            segs["ga"] = txt
                                            counts["ga_segments"] += 1
                                            counts["ga_chars"] += len(txt)
                                            counts["ga_whitespace_tokens"] += len(txt.split())
                                            h = hashlib.sha256(txt.encode("utf-8")).hexdigest()
                                            if h in ga_seen: counts["duplicate_ga_segments"] += 1
                                            else: ga_seen.add(h)
                                        elif lang == "en":
                                            segs["en"] = txt
                                            counts["en_segments"] += 1
                                            counts["en_chars"] += len(txt)
                                            counts["en_whitespace_tokens"] += len(txt.split())
                                        else:
                                            counts["other_segments"] += 1
                                if "ga" in segs and "en" in segs:
                                    pair = hashlib.sha256((segs["ga"] + "\0" + segs["en"]).encode("utf-8")).hexdigest()
                                    pair_seen.add(pair)
                                elem.clear()
                    counts["distinct_ga_sha256"] = len(ga_seen)
                    counts["distinct_pairs_sha256"] = len(pair_seen)
                    files.append({"file": member.filename, **counts})
            reports.append({"resource": {k:v for k,v in resource.items() if k != "url"},
                            "download_url": url, "bytes": len(data), "sha256": digest, "files": files})
    report = {"dataset_id": DATASET_ID, "title": pkg.get("title"), "publisher": pkg.get("organization"),
              "license_title": pkg.get("license_title"), "license_url": pkg.get("license_url"),
              "metadata_url": API, "resources": reports,
              "method": "Downloaded the data.europa.eu CKAN package_show distribution(s), SHA-256 hashed each ZIP, streamed TMX/XML translation units, counted language-tagged Irish/English segments, local whitespace tokens and exact-text/pair duplicates. Text is not emitted."}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
