#!/usr/bin/env python3
"""Full audit of Soranoha v0.2 Japanese public-domain literature snapshot."""
from __future__ import annotations
import collections, csv, hashlib, io, json, re, tempfile, unicodedata, zipfile, os
from pathlib import Path
import requests

URL="https://zenodo.org/records/23469644/files/soranoha-plaintext.zip?download=1"
OUT=Path("reports/soranoha-v0.2-audit.json")
CHUNK=1024*1024
SENTENCE_END=re.compile(r"(?<=[。！？!?])|\\n+")

def norm(s):
    return " ".join(unicodedata.normalize("NFC",s).split())

def main():
    fd,name=tempfile.mkstemp(prefix="soranoha-",suffix=".zip"); os.close(fd)
    path=Path(name); h=hashlib.sha256(); size=0
    try:
        with requests.get(URL,stream=True,timeout=(60,300),
                          headers={"User-Agent":"langid-32-source-audit/1"}) as r:
            r.raise_for_status()
            with path.open("wb") as f:
                for b in r.iter_content(CHUNK):
                    if b: f.write(b); h.update(b); size+=len(b)
        files=[]; totals=collections.Counter()
        ids=set(); text_hashes=set(); catalog_rows=[]
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            catalog_name=next((n for n in names if n.endswith("catalog.csv")),None)
            if not catalog_name: raise RuntimeError("catalog.csv missing")
            catalog=z.read(catalog_name).decode("utf-8-sig","replace")
            for row in csv.DictReader(io.StringIO(catalog)):
                catalog_rows.append(row)
                for key in ("Aozora identifier","identifier","aozora_id","id"):
                    if row.get(key): ids.add(row[key]); break
            text_members=[n for n in names if n.lower().endswith(".txt")]
            for member in sorted(text_members):
                raw=z.read(member)
                body=raw.decode("utf-8","replace")
                paragraphs=[p.strip() for p in body.splitlines() if p.strip()]
                sentences=[s.strip() for s in SENTENCE_END.split(body) if s.strip()]
                normalized=norm(body)
                digest=hashlib.sha256(normalized.encode("utf-8")).hexdigest()
                duplicate=digest in text_hashes; text_hashes.add(digest)
                stats={"bytes":len(raw),"characters":len(body),
                       "whitespace_tokens":len(body.split()),
                       "nonempty_paragraphs":len(paragraphs),
                       "sentence_segments":len(sentences),
                       "duplicate_normalized_text":duplicate,
                       "sha256":hashlib.sha256(raw).hexdigest()}
                files.append({"file":member,"measured":stats})
                for k,v in stats.items():
                    if isinstance(v,int) and k not in ("bytes","characters","sha256"):
                        totals[k]+=v
                totals["bytes"]+=len(raw); totals["characters"]+=len(body)
            report={
              "dataset":"Soranoha release snapshot c373bb08 v0.2",
              "doi":"10.5281/zenodo.23469644","source":"Aozora Bunko",
              "download_url":URL,"zip_bytes":size,"zip_sha256":h.hexdigest(),
              "catalog_rows":len(catalog_rows),"catalog_distinct_ids":len(ids),
              "text_files":len(text_members),"distinct_normalized_texts":len(text_hashes),
              "totals":dict(totals),"files":files,
              "rights":"All 17,308 works are stated by Soranoha to be public domain in Japan; Soranoha's plaintext encoding and catalogue structure are CC0-1.0. Bibliographic metadata derives from Aozora Bunko under CC BY 4.0 and requires attribution.",
              "method":"Downloaded complete plaintext ZIP, hashed archive and every work, counted characters, whitespace tokens, nonempty paragraphs and Japanese punctuation-based sentence segments. Sentence count is a heuristic, not a gold segmentation.",
              "caveat":"Public-domain status is asserted for Japan. Retain per-work author/title/source-edition metadata and assess applicable term-of-protection rules for the intended redistribution jurisdictions; do not assume that CC0 on the encoding licenses in-copyright underlying works."
            }
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        path.unlink(missing_ok=True)

if __name__=="__main__": main()
