#!/usr/bin/env python3
"""Create a bounded, document-balanced staging sample from DGT-TM ZIP/TMX volumes."""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import sqlite3
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

from langid32.merge import (
    EMAIL_RE, HTTP_FRAGMENT_RE, IPV4_RE,
    URL_RE, WEB_FRAGMENT_RE, split_for,
)

EU_LANGUAGES = {
    "bg", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "de",
    "el", "hu", "ga", "it", "lv", "lt", "mt", "pl", "pt", "ro",
    "sk", "sl", "es", "sv",
}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
SEED = "langid-32-fineweb2-v1"
LICENCE_ID = "EC-Reuse-Decision-2011-833-EU"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_translation_units(stream):
    stack = []
    processed = 0
    for event, element in ET.iterparse(stream, events=("start", "end")):
        if event == "start":
            stack.append(element)
            continue
        if local_name(element.tag) == "tu":
            yield element
            element.clear()
            processed += 1
            # Clear the <body> child list in batches; repeated Element.remove()
            # is quadratic for large TMX files.
            if processed % 1000 == 0 and len(stack) > 1:
                parent = stack[-2]
                if local_name(parent.tag) == "body":
                    parent.clear()
        stack.pop()


def segments_from_tu(tu):
    for tuv in tu:
        if local_name(tuv.tag) != "tuv":
            continue
        raw_language = tuv.attrib.get(XML_LANG, "").lower()
        language = raw_language.split("-", 1)[0]
        if language not in EU_LANGUAGES:
            continue
        for element in tuv.iter():
            if local_name(element.tag) == "seg":
                text = normalize("".join(element.itertext()))
                if text:
                    yield language, text
                break


def priority_for(language: str, text: str, group_id: str) -> int:
    value = hashlib.sha256(
        f"{SEED}\0{language}\0{text}\0{group_id}".encode("utf-8")
    ).digest()[:8]
    return int.from_bytes(value, "big")


def heap_add(heap, limit: int, priority: int, text_hash: str, record):
    item = (-priority, text_hash, record)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif (item[0], item[1]) > (heap[0][0], heap[0][1]):
        heapq.heapreplace(heap, item)


def stage(args):
    for path in args.archives:
        if not path.is_file():
            raise FileNotFoundError(path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    samples = defaultdict(list)
    sample_caps = {
        "train": args.target_per_language - 2 * round(args.target_per_language * 0.10),
        "validation": round(args.target_per_language * 0.10),
        "test": round(args.target_per_language * 0.10),
    }

    with tempfile.TemporaryDirectory(prefix="langid32-dgt-stage-") as temp:
        db = sqlite3.connect(Path(temp) / "unique.sqlite")
        db.execute("PRAGMA journal_mode=OFF")
        db.execute("PRAGMA synchronous=OFF")
        db.execute("CREATE TABLE seen (language TEXT, text_hash TEXT, PRIMARY KEY(language,text_hash))")

        for archive_path in sorted(args.archives):
            with zipfile.ZipFile(archive_path) as archive:
                for member in sorted(archive.namelist()):
                    if not member.lower().endswith(".tmx"):
                        continue
                    counts["tmx_files_processed"] += 1
                    group_id = f"dgt-tm-2021:{archive_path.name}:{PurePosixPath(member).stem}"
                    group_split = split_for(group_id, SEED, 0.10, 0.10)
                    per_document = defaultdict(list)
                    try:
                        with archive.open(member) as stream:
                            for tu in iter_translation_units(stream):
                                counts["translation_units"] += 1
                                tu_id = tu.attrib.get("tuid", "")
                                for language, text in segments_from_tu(tu):
                                    counts[f"segments::{language}"] += 1
                                    if len(text) < args.min_chars or len(text) > args.max_chars:
                                        counts[f"outside_character_limits::{language}"] += 1
                                        continue
                                    if len(text.encode("utf-8")) > args.max_bytes:
                                        counts[f"outside_byte_limit::{language}"] += 1
                                        continue
                                    if EMAIL_RE.search(text):
                                        counts[f"email_excluded::{language}"] += 1
                                        continue
                                    if URL_RE.search(text) or WEB_FRAGMENT_RE.search(text) or HTTP_FRAGMENT_RE.search(text):
                                        counts[f"url_excluded::{language}"] += 1
                                        continue
                                    if IPV4_RE.search(text):
                                        counts[f"ipv4_excluded::{language}"] += 1
                                        continue
                                    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
                                    cursor = db.execute(
                                        "INSERT OR IGNORE INTO seen VALUES (?,?)",
                                        (language, text_hash),
                                    )
                                    if cursor.rowcount == 0:
                                        counts[f"duplicate_text::{language}"] += 1
                                        continue
                                    counts[f"eligible_unique::{language}"] += 1
                                    # Numeric/phone flags are recomputed by the
                                    # global merge on the bounded sample, not on every
                                    # translation-memory segment.
                                    flags = []
                                    priority = priority_for(language, text, group_id)
                                    record = {
                                        "text": text,
                                        "language": language,
                                        "source": "dgt-tm-2021",
                                        "source_release": args.source_release,
                                        "group_id": group_id,
                                        "split_group_id": group_id,
                                        "licence_id": LICENCE_ID,
                                        "text_origin": "unknown",
                                        "provenance": {
                                            "archive": archive_path.name,
                                            "tmx_member": member,
                                            "translation_unit_id": tu_id,
                                            "privacy_flags": flags,
                                        },
                                    }
                                    heap_add(per_document[language],
                                             args.max_per_document_language,
                                             priority, text_hash, record)
                    except (ET.ParseError, UnicodeError, OSError, zipfile.BadZipFile):
                        counts["malformed_tmx_files"] += 1
                        continue

                    for language, heap in per_document.items():
                        counts[f"document_groups::{language}"] += 1
                        for neg_priority, text_hash, record in heap:
                            heap_add(samples[(language, group_split)],
                                     sample_caps[group_split],
                                     -neg_priority, text_hash, record)
            db.commit()
        db.close()

    output_count = 0
    selected_counts = {}
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        for language in sorted(EU_LANGUAGES):
            for split in ("train", "validation", "test"):
                heap = samples[(language, split)]
                records = sorted(
                    ((-neg_priority, text_hash, record)
                     for neg_priority, text_hash, record in heap),
                    key=lambda item: (item[0], item[1]),
                )
                selected_counts[f"{language}:{split}"] = len(records)
                for _, _, record in records:
                    output.write(json.dumps(record, ensure_ascii=False,
                                            separators=(",", ":")) + "\n")
                    output_count += 1

    archive_info = [
        {"name": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(args.archives)
    ]
    manifest = {
        "schema_version": 1,
        "source": "European Commission DGT Translation Memory",
        "source_release": args.source_release,
        "source_release_note": "The 2021 package is the release described by the JRC technical download table; 2025 catalogue volumes are tracked separately pending archive inspection.",
        "source_licence": LICENCE_ID,
        "attribution": "European Commission, Directorate-General for Translation, DGT Translation Memory; reuse under Commission Decision 2011/833/EU. Preserve attribution and source release information.",
        "archives": archive_info,
        "output_sha256": sha256_file(args.output),
        "output_records": output_count,
        "languages": sorted(EU_LANGUAGES),
        "selection": {
            "seed": SEED,
            "target_per_language": args.target_per_language,
            "selected_counts_by_language_split": selected_counts,
            "max_segments_per_tmx_document_language": args.max_per_document_language,
            "grouping": "all language segments from the same TMX file share a group_id",
            "split": "same deterministic group hash used by the global merge",
            "sampling": "deterministic hash-priority within each document, then within each language/split",
            "min_chars": args.min_chars,
            "max_chars": args.max_chars,
            "max_bytes": args.max_bytes,
        },
        "counts": dict(sorted(counts.items())),
        "text_origin": "unknown; English-centred translation memory, original language not identified by this extraction",
        "privacy": "Email, URL and IPv4 matches excluded; phone-like and 9+ digit sequences retained with flags. This is not full PII review.",
        "quality_note": "Translation-memory segments can be fragments, boilerplate, legal formulae or repeated clauses. Review sentence quality and translationese before training.",
        "rights_note": "This is a reuse decision, not a CC0/CC-BY label. Check current Commission reuse conditions and attribution before redistribution.",
    }
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "records": output_count,
        "selected_counts_by_language_split": selected_counts,
        "manifest": str(manifest_path),
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", dest="archives", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-release", default="DGT-TM-release-2021")
    parser.add_argument("--target-per-language", type=int, default=20000)
    parser.add_argument("--max-per-document-language", type=int, default=20)
    parser.add_argument("--min-chars", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=1500)
    args = parser.parse_args()
    if args.target_per_language < 1 or args.max_per_document_language < 1:
        parser.error("target and per-document cap must be positive")
    if args.min_chars < 1 or args.max_chars < args.min_chars or args.max_bytes < 1:
        parser.error("invalid text length limits")
    stage(args)


if __name__ == "__main__":
    main()
