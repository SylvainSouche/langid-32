"""Inventory current Korean statutes through the Law Open Data API.

Requires a user-registered OC key in the LAW_API_OC environment variable.
Only metadata and counts are written; no legal text is exported.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


BASE_URL = "https://www.law.go.kr/DRF"
SENTENCE_END = re.compile(r"[.!?。！？](?=\s|$)")


def text_of(element: ET.Element, tag: str) -> str:
    found = element.find(tag)
    if found is None:
        return ""
    return "".join(found.itertext()).strip()


def parse_law_list(payload: bytes) -> tuple[int, list[dict[str, str]]]:
    root = ET.fromstring(payload)
    total = int(text_of(root, "totalCnt") or "0")
    records = []
    for law in root.findall(".//law"):
        serial = text_of(law, "법령일련번호")
        if not serial:
            continue
        records.append({
            "source_id": "korean-law-open-api",
            "source_release": f"current-as-of-{date.today().isoformat()}",
            "group_id": f"KR-LAW:{serial}",
            "source_licence": "Korean Copyright Act Article 7 for listed official legal works; API terms apply separately",
            "source_attribution": "Ministry of Government Legislation, National Law Information Center",
            "law_id": serial,
            "law_name": text_of(law, "법령명한글"),
            "law_short_name": text_of(law, "법령약칭명"),
            "promulgation_date": text_of(law, "공포일자"),
            "effective_date": text_of(law, "시행일자"),
            "law_type": text_of(law, "법령구분명"),
            "department": text_of(law, "소관부처명"),
            "source_url": text_of(law, "법령상세링크"),
        })
    return total, records


def parse_law_body(payload: bytes) -> dict[str, int | str]:
    root = ET.fromstring(payload)
    articles = root.findall(".//조문단위")
    if not articles:
        articles = root.findall(".//조문")
    chars = 0
    rough_sentences = 0
    for article in articles:
        text = " ".join("".join(article.itertext()).split())
        chars += len(text)
        rough_sentences += len(SENTENCE_END.findall(text))
    return {
        "article_count": len(articles),
        "article_text_chars": chars,
        "rough_sentence_count": rough_sentences,
        "body_sha256": hashlib.sha256(payload).hexdigest(),
    }


def request_xml(endpoint: str, params: dict[str, str], timeout: int) -> bytes:
    query = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/{endpoint}?{query}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "langid-32-corpus-inventory/0.1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()
    try:
        ET.fromstring(payload)
    except ET.ParseError as exc:
        preview = payload[:300].decode("utf-8", errors="replace")
        raise RuntimeError(f"Law Open API returned non-XML content: {preview}") from exc
    return payload


def inventory(oc: str, output: Path, max_documents: int,
              delay: float, timeout: int, list_only: bool) -> dict:
    rows = []
    page = 1
    total = None
    seen = set()
    while total is None or len(seen) < total:
        payload = request_xml("lawSearch.do", {
            "OC": oc, "target": "law", "type": "XML",
            "display": "100", "page": str(page),
        }, timeout)
        page_total, records = parse_law_list(payload)
        if total is None:
            total = page_total
        if not records:
            break
        for record in records:
            law_id = record["law_id"]
            if law_id in seen:
                continue
            seen.add(law_id)
            result = dict(record)
            if not list_only:
                body = request_xml("lawService.do", {
                    "OC": oc, "target": "law", "MST": law_id, "type": "XML",
                }, timeout)
                result.update(parse_law_body(body))
                time.sleep(delay)
            rows.append(result)
            if max_documents and len(rows) >= max_documents:
                break
        if max_documents and len(rows) >= max_documents:
            break
        if total is not None and len(seen) >= total:
            break
        page += 1
        time.sleep(delay)

    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else [
        "source_id", "source_release", "group_id", "source_licence",
        "source_attribution", "law_id", "law_name", "law_short_name",
        "promulgation_date", "effective_date", "law_type", "department",
        "source_url",
    ]
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return {
        "output": str(output),
        "api_total_documents": total,
        "documents_inventoried": len(rows),
        "list_only": list_only,
        "article_count": sum(int(row.get("article_count", 0)) for row in rows),
        "rough_sentence_count": sum(int(row.get("rough_sentence_count", 0)) for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-documents", type=int, default=0,
                        help="0 means all current statutes")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Seconds between API calls (default: 1.0)")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--list-only", action="store_true",
                        help="Inventory list metadata without fetching law bodies")
    args = parser.parse_args()
    if args.max_documents < 0 or args.delay < 0 or args.timeout < 1:
        parser.error("invalid limit, delay or timeout")
    oc = os.environ.get("LAW_API_OC", "").strip()
    if not oc:
        parser.error("set LAW_API_OC to the OC key registered with Law Open Data")
    print(json.dumps(
        inventory(oc, args.output, args.max_documents,
                  args.delay, args.timeout, args.list_only),
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
