#!/usr/bin/env python3
"""Full row/text audit of the cleaned Korean Wikipedia 2026-07-01 parquet release."""
from __future__ import annotations
import collections, hashlib, json, re, tempfile
from pathlib import Path
import requests
import pyarrow.parquet as pq

BASE = "https://huggingface.co/datasets/shopkeeper/kowiki-cleaned-070126/resolve/main/"
FILES = [
 "data/train-00000-of-00003.parquet",
 "data/train-00001-of-00003.parquet",
 "data/train-00002-of-00003.parquet",
]
OUT = Path("reports/kowiki-cleaned-070126-audit.json")
CHUNK = 1024 * 1024
SENTENCE_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")

def main():
    out = {"dataset":"Korean Wikipedia cleaned 2026-07-01",
           "source_dump":"kowiki-20260701-pages-articles.xml.bz2",
           "source_revision":"shopkeeper/kowiki-cleaned-070126",
           "licence_declared":"CC BY-SA 4.0 and GFDL",
           "files":[]}
    totals=collections.Counter()
    id_hashes=set(); url_hashes=set(); text_hashes=set()
    for filename in FILES:
        fd,name=tempfile.mkstemp(prefix="kowiki-",suffix=".parquet")
        Path(name).unlink(missing_ok=True)
        p=Path(name)
        h=hashlib.sha256(); size=0
        try:
            with requests.get(BASE+filename,stream=True,timeout=(60,300),
                              headers={"User-Agent":"langid-32-source-audit/1"}) as r:
                r.raise_for_status()
                with p.open("wb") as f:
                    for block in r.iter_content(CHUNK):
                        if block:
                            f.write(block); h.update(block); size+=len(block)
            pf=pq.ParquetFile(p)
            fc=collections.Counter()
            for batch in pf.iter_batches(batch_size=4096,columns=["id","url","title","text"]):
                cols=batch.to_pydict()
                for ident,url,title,body in zip(cols["id"],cols["url"],cols["title"],cols["text"]):
                    fc["rows"]+=1
                    for label,val in (("id",ident),("url",url),("text",body)):
                        if val is not None:
                            digest=hashlib.sha256(str(val).encode("utf-8")).digest()
                            if label=="id":
                                if digest in id_hashes: fc["duplicate_ids"]+=1
                                id_hashes.add(digest)
                            elif label=="url":
                                if digest in url_hashes: fc["duplicate_urls"]+=1
                                url_hashes.add(digest)
                            else:
                                if digest in text_hashes: fc["duplicate_texts"]+=1
                                text_hashes.add(digest)
                    body=body or ""
                    fc["characters"]+=len(body)
                    paragraphs=[x.strip() for x in body.splitlines() if x.strip()]
                    fc["nonempty_paragraphs"]+=len(paragraphs)
                    fc["whitespace_tokens"]+=len(body.split())
                    fc["sentence_segments"]+=sum(1 for x in SENTENCE_SPLIT.split(body) if x.strip())
                    fc["empty_text_rows"]+=not bool(body.strip())
            out["files"].append({"file":filename,"bytes":size,"sha256":h.hexdigest(),
                                 "parquet_rows":pf.metadata.num_rows,"measured":dict(fc)})
            totals.update(fc)
        finally:
            p.unlink(missing_ok=True)
    out["totals"]=dict(totals)
    out["distinct_ids"]=len(id_hashes)
    out["distinct_urls"]=len(url_hashes)
    out["distinct_texts"]=len(text_hashes)
    out["method"]="All three Parquet shards downloaded and iterated in batches. Sentence count is a deterministic punctuation/line-break segmentation proxy, not gold sentence annotation; retain article-level provenance."
    out["rights_warning"]="Source card declares CC BY-SA 4.0 and GFDL. This is not a permissive CC BY/CC0 source; sentence extraction/redistribution must be assessed for share-alike obligations before any release. Article IDs and URLs retained."
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))

if __name__=="__main__": main()
