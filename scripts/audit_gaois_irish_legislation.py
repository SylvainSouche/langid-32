#!/usr/bin/env python3
"""Full audit of the downloadable Gaois Irish legislation English-Irish TMX corpus."""
from __future__ import annotations
import collections, hashlib, json, os, re, sqlite3, tempfile, unicodedata, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

SOURCES=[
 ("constitution","https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-constitution.zip"),
 ("primary_1922_1949","https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-primary-1922-1949.zip"),
 ("primary_1950_1979","https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-primary-1950-1979.zip"),
 ("primary_1980_2014","https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-primary-1980-2014.zip"),
 ("secondary_instruments","https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-secondary.zip"),
 ("secondary_court_rules","https://www.gaois.ie/assets/tmx/18.10.25-gaois.ie-crp-tmx-irish-legislation-secondary-court-rules.zip"),
]
OUT=Path("reports/gaois-irish-legislation-tmx-audit.json")
CHUNK=1024*1024
XML_LANG="{http://www.w3.org/XML/1998/namespace}lang"
SENTENCE_SPLIT=re.compile(r"(?<=[.!?。！？])|\\n+")

def norm(s):
    return " ".join(unicodedata.normalize("NFC",s).split())

def main():
    dbfd,dbname=tempfile.mkstemp(prefix="gaois-irish-",suffix=".sqlite"); os.close(dbfd)
    db=sqlite3.connect(dbname); db.execute("PRAGMA journal_mode=OFF"); db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE irish (text TEXT PRIMARY KEY) WITHOUT ROWID")
    reports=[]; grand=collections.Counter()
    try:
        for label,url in SOURCES:
            fd,name=tempfile.mkstemp(prefix="gaois-",suffix=".zip"); os.close(fd)
            path=Path(name); h=hashlib.sha256(); size=0
            local=collections.Counter(); lang_tags=collections.Counter()
            english_units=0; tmx_files=[]
            try:
                with requests.get(url,stream=True,timeout=(60,300),
                                  headers={"User-Agent":"langid-32-source-audit/1"}) as r:
                    r.raise_for_status()
                    with path.open("wb") as out:
                        for b in r.iter_content(CHUNK):
                            if b: out.write(b); h.update(b); size+=len(b)
                with zipfile.ZipFile(path) as z:
                    for member in z.namelist():
                        if not member.lower().endswith((".tmx",".xml")): continue
                        tmx_files.append(member)
                        with z.open(member) as stream:
                            for event,elem in ET.iterparse(stream,events=("end",)):
                                if elem.tag.rsplit("}",1)[-1]!="tu": continue
                                segments={}
                                for tuv in elem:
                                    if tuv.tag.rsplit("}",1)[-1]!="tuv": continue
                                    lang=tuv.attrib.get(XML_LANG) or tuv.attrib.get("lang") or ""
                                    lang=lang.lower()
                                    lang_tags[lang]+=1
                                    seg=next((x for x in tuv if x.tag.rsplit("}",1)[-1]=="seg"),None)
                                    text=" ".join("".join(seg.itertext()).split()) if seg is not None else ""
                                    if lang.startswith("ga"): segments["ga"]=text
                                    elif lang.startswith("en"): segments["en"]=text
                                if segments.get("en"): english_units+=1
                                ga=segments.get("ga","")
                                if ga:
                                    local["irish_segments"]+=1
                                    local["characters"]+=len(ga)
                                    local["whitespace_tokens"]+=len(ga.split())
                                    local["sentence_segments"]+=sum(1 for x in SENTENCE_SPLIT.split(ga) if x.strip())
                                    n=norm(ga)
                                    if n:
                                        cur=db.execute("INSERT OR IGNORE INTO irish VALUES (?)",(n,))
                                        if cur.rowcount: local["new_global_unique_irish_segments"]+=1
                                        else: local["duplicate_irish_segments"]+=1
                                local["translation_units"]+=1
                                elem.clear()
                db.commit()
                row={"source_file":label,"url":url,"zip_bytes":size,"zip_sha256":h.hexdigest(),
                     "tmx_members":tmx_files,"language_tags":dict(lang_tags),
                     "english_units":english_units,"measured":dict(local)}
                reports.append(row); grand.update(local)
            finally:
                path.unlink(missing_ok=True)
        union=db.execute("SELECT COUNT(*) FROM irish").fetchone()[0]
        report={"dataset":"Gaois Parallel English-Irish Corpus of Legislation",
                "source":"Fiontar & Scoil na Gaeilge, Dublin City University",
                "licence":"CC BY 4.0 for the derivative machine-readable aligned translation memories",
                "sources":reports,"totals":dict(grand),
                "distinct_normalized_irish_segments_across_all_files":union,
                "method":"Downloaded and parsed all six public TMX ZIPs; counted translation units, English and Irish language tags, Irish segment text, characters, whitespace tokens, heuristic sentence segments and exact normalized unique Irish segments.",
                "rights_note":"The page states that original legislation is copyright Government of Ireland, while the derivative machine-readable aligned translation memories are copyright DCU and CC BY 4.0. Attribute DCU/Gaois and retain source file/translation-unit provenance; do not treat the underlying Acts as independently licensed CC BY.",
                "quality_note":"This is legal/administrative text and may be repetitive or formulaic. TMX segments are translation units/passages, not necessarily sentences; use only Irish-side text and deduplicate across all six files."}
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        db.close(); Path(dbname).unlink(missing_ok=True)

if __name__=="__main__": main()
