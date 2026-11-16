#!/usr/bin/env python3
"""Extract a deterministic, bounded FineWeb2 sample from original Parquet shards.

Reads only selected Parquet row groups through HTTP range requests. It does not
download whole shards. Output is JSONL suitable for later corpus normalization.
"""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.parse, urllib.request
from pathlib import Path
import fsspec
import pyarrow.parquet as pq

DATASET="HuggingFaceFW/fineweb-2"
REVISION="v2.1.0"
LANGS={"spa_Latn":"es","tur_Latn":"tr"}
MIN_CHARS=100
MAX_CHARS=5000
ROW_GROUP_FRACTIONS=(0.25,0.75)
TARGET=20000

def tree(path):
    url=f"https://huggingface.co/api/datasets/{DATASET}/tree/{REVISION}/{path}?recursive=true&expand=false&limit=1000"
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"langid-32 FineWeb2 extractor/0.1"}),timeout=60) as r:
        return [x["path"] for x in json.load(r) if x.get("type")=="file"]

def selected_groups(pf):
    n=pf.metadata.num_row_groups
    return sorted(set(round(f*(n-1)) for f in ROW_GROUP_FRACTIONS))

def keep(row, expected):
    text=row.get("text")
    if not isinstance(text,str):
        return False
    text=" ".join(text.replace("\u0000"," ").split())
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        return False
    if row.get("language") != expected or row.get("language_script") != "Latn":
        return False
    if not row.get("url") or not row.get("id"):
        return False
    return True, text

def rank(doc_id):
    return hashlib.sha256(doc_id.encode("utf-8")).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--target",type=int,default=TARGET)
    args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    columns=["text","id","dump","url","date","file_path","language","language_score","language_script","minhash_cluster_size","top_langs"]
    report={"dataset":DATASET,"revision":REVISION,"selection":{"row_group_fractions":ROW_GROUP_FRACTIONS,"min_chars":MIN_CHARS,"max_chars":MAX_CHARS,"target":args.target},"languages":{}}
    fs=fsspec.filesystem("http",client_kwargs={"headers":{"User-Agent":"langid-32 FineWeb2 extractor/0.1"}})
    for subset,lang in LANGS.items():
        candidates={}
        shards=tree(f"data/{subset}/train")
        for idx,path in enumerate(shards):
            url=f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{path}"
            with fs.open(url,"rb",block_size=1024*1024,cache_type="readahead") as fh:
                pf=pq.ParquetFile(fh)
                groups=selected_groups(pf)
                table=pf.read_row_groups(groups,columns=columns)
            rows=table.to_pylist()
            for row in rows:
                kept=keep(row,subset)
                if kept is True:
                    continue
                if not kept:
                    continue
                text=kept[1]
                doc_id=str(row["id"])
                if doc_id not in candidates:
                    candidates[doc_id]={
                        "text":text,"id":doc_id,"url":str(row["url"]),
                        "date":row.get("date"),"dump":row.get("dump"),
                        "file_path":row.get("file_path"),"language_score":row.get("language_score"),
                        "language_script":row.get("language_script"),
                        "minhash_cluster_size":row.get("minhash_cluster_size"),
                        "top_langs":row.get("top_langs"),
                        "source":"fineweb2","revision":REVISION,"subset":subset,
                    }
            print(f"{lang}: {idx+1}/{len(shards)} shards, unique candidates={len(candidates)}",flush=True)
        ordered=sorted(candidates.values(),key=lambda r:rank(r["id"]))
        selected=ordered[:args.target]
        out=args.output_dir/f"{lang}.jsonl"
        with out.open("w",encoding="utf-8") as f:
            for row in selected:
                f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
        report["languages"][lang]={"shards":len(shards),"unique_candidates":len(candidates),"selected":len(selected),"output":str(out)}
    (args.output_dir/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
