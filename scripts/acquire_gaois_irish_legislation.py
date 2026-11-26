#!/usr/bin/env python3
"""Acquire a bounded, deduplicated Irish-side sample from Gaois legislation TMX."""
from __future__ import annotations
import argparse, hashlib, heapq, json, re, sqlite3, tempfile, time, unicodedata, zipfile
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config, acquisition_target
from langid32.merge import EMAIL_RE, URL_RE, IPV4_RE, LONG_NUMBER_RE
from langid32.privacy import screen_text, sanitize_provenance
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from xml.etree.ElementTree import iterparse

SOURCES = [
    ("constitution", "https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-constitution.zip"),
    ("primary_1922_1949", "https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-primary-1922-1949.zip"),
    ("primary_1950_1979", "https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-primary-1950-1979.zip"),
    ("primary_1980_2014", "https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-primary-1980-2014.zip"),
    ("secondary_instruments", "https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-secondary.zip"),
    ("secondary_court_rules", "https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-secondary-court-rules.zip"),
]
EXPECTED_COMBINED_SHA256 = "8d5748a5d55818c05b4f6c925c3851ed7bf4735308f0aca6811fb3a4f57a20b5"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
EMAIL = re.compile(r"(?i)\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b")
URL = re.compile(r"(?i)(https?://|www\.)\S+")
NUMBER = re.compile(r"\d{9,}")
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")

def clean(value, rules):
    text = " ".join(unicodedata.normalize("NFC", str(value or "")).split())
    letters = sum(ch.isalpha() for ch in text)
    if (len(text) < rules["min_characters"] or len(text) > rules["max_characters"] or
        letters < rules["min_alpha_characters"] or
        letters / max(1, len(text)) < rules["min_alpha_ratio"] or
        (rules["exclude_email"] and EMAIL_RE.search(text)) or
        (rules["exclude_url"] and URL_RE.search(text)) or
        (rules["exclude_long_numeric"] and LONG_NUMBER_RE.search(text)) or
        (rules["exclude_ipv4"] and IPV4_RE.search(text))):
        return None
    return text

def download(url, path, execution):
    attempts = int(execution["acquisition_retry_attempts"])
    for attempt in range(1, attempts + 1):
        req = Request(url, headers={"User-Agent": "langid-32-source-acquisition/1.0"})
        digest = hashlib.sha256()
        size = 0
        try:
            with urlopen(req, timeout=execution["http_read_timeout_seconds"]) as response, path.open("wb") as out:
                expected = int(response.headers.get("Content-Length") or 0)
                while True:
                    block = response.read(execution["download_chunk_bytes"])
                    if not block:
                        break
                    out.write(block)
                    digest.update(block)
                    size += len(block)
            if expected and size != expected:
                raise IOError(f"truncated download {url}: {size}/{expected}")
            return {"url": url, "bytes": size, "sha256": digest.hexdigest()}
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts:
                raise
            retry_after = exc.headers.get("Retry-After", "")
            delay = min(int(retry_after), 120) if retry_after.isdigit() else min(5 * (2 ** (attempt - 1)), 60)
            time.sleep(delay)
    raise RuntimeError(f"Download retry budget exhausted for {url}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-sample", type=int, default=None)
    parser.add_argument("--seed", default=None)
    parser.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    args.max_sample = args.max_sample if args.max_sample is not None else acquisition_target(cfg, "gaois_irish_legislation", "ga")
    args.seed = args.seed or cfg["acquisition"]["seed"]
    execution = cfg["execution"]
    text_rules = cfg["acquisition"]["source_rules"]["gaois_irish_legislation"]["text"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix="gaois-stage-"))
    db = sqlite3.connect(temp / "dedup.sqlite")
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE seen (digest TEXT PRIMARY KEY) WITHOUT ROWID")
    heap, serial = [], 0
    downloads, totals = [], {"translation_units": 0, "irish_segments": 0,
        "empty_or_missing_irish": 0, "filtered_irish_segments": 0,
        "privacy_rejected": 0, "privacy_quarantined": 0,
        "personal_metadata_fields_removed": 0, "clean_irish_segments": 0,
        "duplicate_irish_segments": 0, "selected": 0}
    try:
        for label, url in SOURCES:
            archive = temp / (label + ".zip")
            info = download(url, archive, execution)
            downloads.append({"component": label, **info})
            with zipfile.ZipFile(archive) as zf:
                for member in zf.namelist():
                    if not member.lower().endswith((".tmx", ".xml")): continue
                    with zf.open(member) as stream:
                        tu_index = 0
                        for _, tu in iterparse(stream, events=("end",)):
                            if tu.tag.rsplit("}", 1)[-1] != "tu": continue
                            tu_index += 1
                            segments = {}
                            for tuv in tu:
                                if tuv.tag.rsplit("}", 1)[-1] != "tuv": continue
                                lang = (tuv.attrib.get(XML_LANG) or tuv.attrib.get("lang") or "").lower()
                                seg = next((x for x in tuv if x.tag.rsplit("}", 1)[-1] == "seg"), None)
                                value = " ".join("".join(seg.itertext()).split()) if seg is not None else ""
                                if lang.startswith("ga"): segments["ga"] = value
                                elif lang.startswith("en"): segments["en"] = value
                            totals["translation_units"] += 1
                            raw_ga = " ".join(unicodedata.normalize("NFC", segments.get("ga", "")).split())
                            if not raw_ga:
                                totals["empty_or_missing_irish"] += 1
                                tu.clear()
                                continue
                            totals["irish_segments"] += 1
                            ga = clean(raw_ga, text_rules)
                            if not ga:
                                totals["filtered_irish_segments"] += 1
                                tu.clear()
                                continue
                            privacy = screen_text(
                                ga,
                                uncertain_action=cfg["acquisition"]["text"]["privacy_uncertain_action"],
                            )
                            if not privacy.accepted:
                                totals["privacy_" + privacy.status] += 1
                                tu.clear()
                                continue
                            totals["clean_irish_segments"] += 1
                            digest = hashlib.sha256(ga.encode("utf-8")).hexdigest()
                            cur = db.execute("INSERT OR IGNORE INTO seen VALUES (?)", (digest,))
                            if cur.rowcount == 0:
                                totals["duplicate_irish_segments"] += 1
                                tu.clear()
                                continue
                            english = segments.get("en", "")
                            record_id = str(tu.attrib.get("tuid") or tu.attrib.get("id") or f"{label}:{member}:{tu_index}")
                            group_id = f"gaois_irish_legislation:{label}:{record_id}"
                            provenance = {
                                "source_file": member,
                                "source_archive_component": label,
                                "source_archive_url": url,
                                "source_archive_sha256": info["sha256"],
                                "source_archive_bytes": info["bytes"],
                                "source_translation_unit_id": record_id,
                                "source_record_index": tu_index,
                                "source_export_date": "2018-10-25",
                                "publisher": "Fiontar & Scoil na Gaeilge, Dublin City University",
                                "language_tag": "ga",
                                "english_segment_sha256": hashlib.sha256(english.encode("utf-8")).hexdigest() if english else None,
                                "english_segment_characters": len(english) if english else 0,
                            }
                            safe_provenance, removed_fields = sanitize_provenance(provenance)
                            totals["personal_metadata_fields_removed"] += len(removed_fields)
                            safe_provenance["source_original_name"] = "gaois_irish_legislation"
                            safe_provenance["rights_status"] = "attribution_required"
                            safe_provenance["privacy_flags"] = list(privacy.flags)
                            row = {
                                "text": ga, "language": "ga", "source": "gaois_irish_legislation",
                                "source_release": "Gaois-Parallel-English-Irish-Legislation@sha256:pending",
                                "group_id": group_id,
                                "licence_id": "CC-BY-4.0 (DCU/Gaois derivative TMX)",
                                "text_origin": "Irish legal/administrative translation-memory segment",
                                "provenance": safe_provenance,
                            }
                            rank_material = "\0".join((args.seed, group_id, digest))
                            rank = int(hashlib.sha256(rank_material.encode()).hexdigest(), 16)
                            entry = (-rank, serial, row); serial += 1
                            if len(heap) < args.max_sample: heapq.heappush(heap, entry)
                            elif rank < -heap[0][0]: heapq.heapreplace(heap, entry)
                            tu.clear()
            db.commit()
        combined = hashlib.sha256("".join(x["sha256"] for x in downloads).encode()).hexdigest()
        if combined != EXPECTED_COMBINED_SHA256:
            raise RuntimeError(
                f"Gaois six-file release hash mismatch: {combined} != {EXPECTED_COMBINED_SHA256}"
            )
        selected = [entry[2] for entry in heap]
        selected.sort(key=lambda x: (x["group_id"], x["text"]))
        for row in selected:
            row["source_release"] = f"Gaois-Parallel-English-Irish-Legislation@sha256:{combined}"
            row["provenance"]["rights_status"] = "attribution_required"
            row["provenance"]["privacy_flags"] = []
        with args.out.open("w", encoding="utf-8", newline="\n") as out:
            for row in selected:
                out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        totals["selected"] = len(selected)
        totals["distinct_clean_irish_segments"] = totals["clean_irish_segments"] - totals["duplicate_irish_segments"]
        manifest = {
            "source": "Gaois Parallel English-Irish Corpus of Legislation",
            "status": "technical_candidate_not_rights_cleared",
            "licence_scope": "CC BY 4.0 applies to the derivative machine-readable aligned translation memories; original legislation remains Government of Ireland copyright.",
            "attribution": "Fiontar & Scoil na Gaeilge, Dublin City University (DCU), Gaois",
            "downloads": downloads, "combined_release_sha256": combined,
            "source_original_name": "gaois_irish_legislation",
            "counts": totals, "sample_cap": args.max_sample, "seed": args.seed,
            "quota_status": "quota_reached" if totals["distinct_clean_irish_segments"] >= args.max_sample else "source_exhausted",
            "quota_reached": totals["distinct_clean_irish_segments"] >= args.max_sample,
            "source_exhausted": totals["distinct_clean_irish_segments"] < args.max_sample,
            "source_language_counts": {"gaois_irish_legislation:ga": totals["selected"]},
            "privacy_policy": "shared langid32.privacy screen_text before deduplication and the 50,000 source-language quota; provenance sanitized before output",
            "candidate_file": str(args.out),
            "sampling": "Exact NFC/whitespace-normalized Irish text dedup across all six archives, then deterministic SHA-256 priority sample; English side is not emitted.",
            "provenance": "Each candidate retains archive component/hash/URL, TMX member, translation-unit ID/index, export date and English-side hash."
        }
        args.out.with_name("manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    finally:
        db.close()
        import shutil
        shutil.rmtree(temp, ignore_errors=True)

if __name__ == "__main__":
    main()
