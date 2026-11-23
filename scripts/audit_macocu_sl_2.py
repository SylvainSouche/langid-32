#!/usr/bin/env python3
"""Full structural audit of the Slovenian MaCoCu-sl 2.0 XML archive."""
from __future__ import annotations
import collections, hashlib, json, os, sqlite3, tempfile, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

URL = "https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1795/MaCoCu-sl-2.0.xml.zip?isAllowed=y&sequence=9"
OUT = Path("reports/macocu-sl-2.0-audit.json")
XML_NAME = "MaCoCu-sl-2.0.xml"
CHUNK = 1024 * 1024

def main() -> None:
    fd, name = tempfile.mkstemp(prefix="macocu-hr-2-", suffix=".zip")
    os.close(fd)
    path = Path(name)
    dbfd, dbname = tempfile.mkstemp(prefix="macocu-audit-", suffix=".sqlite")
    os.close(dbfd)
    db = sqlite3.connect(dbname)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE ids (value TEXT PRIMARY KEY) WITHOUT ROWID")
    db.execute("CREATE TABLE urls (value TEXT PRIMARY KEY) WITHOUT ROWID")
    try:
        h = hashlib.sha256()
        size = 0
        with requests.get(URL, stream=True, timeout=(60, 300), headers={"User-Agent": "langid-32-source-audit/1"}) as response:
            response.raise_for_status()
            with path.open("wb") as f:
                for chunk in response.iter_content(CHUNK):
                    if chunk:
                        f.write(chunk)
                        h.update(chunk)
                        size += len(chunk)
        tag_counts = collections.Counter()
        attr_counts = collections.Counter()
        root_children = collections.Counter()
        doc_tag_candidates = collections.Counter()
        duplicate_ids = duplicate_urls = 0
        elements = 0
        xml_uncompressed = None
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            matches = [n for n in names if n.endswith(XML_NAME)]
            if len(matches) != 1:
                raise RuntimeError(f"Expected one {XML_NAME}; found {matches[:10]}")
            info = archive.getinfo(matches[0])
            xml_uncompressed = info.file_size
            depth = 0
            with archive.open(info, "r") as xml:
                for event, elem in ET.iterparse(xml, events=("start", "end")):
                    tag = elem.tag.rsplit("}", 1)[-1] if isinstance(elem.tag, str) else str(elem.tag)
                    if event == "start":
                        depth += 1
                        elements += 1
                        tag_counts[tag] += 1
                        for key in elem.attrib:
                            attr_counts[key] += 1
                        if depth == 2:
                            root_children[tag] += 1
                        attrs = {k.rsplit("}", 1)[-1].lower(): v for k, v in elem.attrib.items()}
                        if "url" in attrs or "doc_id" in attrs or "docid" in attrs:
                            doc_tag_candidates[tag] += 1
                            if attrs.get("url"):
                                try:
                                    db.execute("INSERT INTO urls VALUES (?)", (attrs["url"],))
                                except sqlite3.IntegrityError:
                                    duplicate_urls += 1
                            ident = attrs.get("id") or attrs.get("doc_id") or attrs.get("docid")
                            if ident:
                                try:
                                    db.execute("INSERT INTO ids VALUES (?)", (ident,))
                                except sqlite3.IntegrityError:
                                    duplicate_ids += 1
                    else:
                        if depth > 1:
                            elem.clear()
                        depth -= 1
        db.commit()
        report = {
            "dataset": "Slovenian web corpus MaCoCu-sl 2.0",
            "record": "https://hdl.handle.net/11356/1806",
            "url": URL, "licence": "CC0-1.0 (CLARIN.SI record)",
            "archive_bytes": size, "archive_sha256": h.hexdigest(),
            "zip_members": names, "xml_member": matches[0], "xml_uncompressed_bytes": xml_uncompressed,
            "xml_element_count": elements, "element_counts": tag_counts.most_common(80),
            "root_child_counts": dict(root_children),
            "attribute_presence_counts": dict(attr_counts),
            "elements_with_document_like_attributes_by_tag": dict(doc_tag_candidates),
            "distinct_ids": db.execute("SELECT COUNT(*) FROM ids").fetchone()[0],
            "distinct_urls": db.execute("SELECT COUNT(*) FROM urls").fetchone()[0],
            "duplicate_id_values": duplicate_ids, "duplicate_url_values": duplicate_urls,
            "method": "Full streaming XML parse without writing the 22GB expanded XML to disk; counts all elements and attribute occurrences, and exact distinct id/url values.",
            "warning": "This is a structural and provenance-metadata audit, not a sentence count or privacy/rights clearance. The corpus notice-and-takedown route and any personal/sensitive content must still be handled."
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        db.close()
        path.unlink(missing_ok=True)
        Path(dbname).unlink(missing_ok=True)

if __name__ == "__main__":
    main()
