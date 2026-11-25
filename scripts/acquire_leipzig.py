#!/usr/bin/env python3
"""Fetch and inspect a small Leipzig CC BY 4.0 pilot for Icelandic and Croatian.

The official downloadable-corpora usage page states CC BY 4.0:
https://wortschatz.uni-leipzig.de/en/usage
Preserve the original archives and sentence-to-source provenance. This pilot
does not claim that every sentence is suitable for the classifier; downstream
language, privacy, duplication and source-balance checks remain required.
"""
import argparse, csv, hashlib, json, re, tarfile, time
from pathlib import Path
from urllib.parse import quote
import requests
import pyarrow.parquet as pq

INDEX_URL = "https://huggingface.co/datasets/imvladikon/leipzig_corpora_collection/resolve/refs%2Fconvert%2Fparquet/links/train/0000.parquet"
TARGETS = {"hr": ("Croatian", "hrv"), "is": ("Icelandic", "isl")}
HEADERS = {"User-Agent": "langid-32 Leipzig corpus research; contact: abuse@souche.fr"}
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d .()/-]{7,}\d)(?!\w)")
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def get(session,url,path):
    if path.exists(): return
    with session.get(url,headers=HEADERS,stream=True,timeout=(30,240)) as r:
        r.raise_for_status()
        with open(path,"wb") as f:
            for chunk in r.iter_content(1024*1024):
                if chunk: f.write(chunk)
def inspect_archive(path, data_id):
    out={"members":[],"sentence_member":None,"sources_member":None,
         "sentence_rows":0,"source_rows":0,"sentence_examples":[],"source_examples":[]}
    with tarfile.open(path,"r:gz") as tf:
        files=[m for m in tf.getmembers() if m.isfile()]
        out["members"]=[m.name for m in files]
        sent=next((m for m in files if m.name.endswith("-sentences.txt")),None)
        src=next((m for m in files if m.name.endswith("-sources.txt")),None)
        out["sentence_member"]=sent.name if sent else None
        out["sources_member"]=src.name if src else None
        if sent:
            fh=tf.extractfile(sent)
            for raw in fh:
                out["sentence_rows"]+=1
                if len(out["sentence_examples"])<12:
                    line=raw.decode("utf-8","replace").rstrip("\r\n")
                    parts=line.split("\t",1)
                    if len(parts)==2:
                        text=parts[1]
                        out["sentence_examples"].append({
                          "sentence_id":parts[0],"text_preview":text[:220],
                          "has_email":bool(EMAIL.search(text)),
                          "has_url":bool(URL.search(text)),
                          "has_phone_pattern":bool(PHONE.search(text))})
        if src:
            fh=tf.extractfile(src)
            for raw in fh:
                out["source_rows"]+=1
                if len(out["source_examples"])<12:
                    line=raw.decode("utf-8","replace").rstrip("\r\n")
                    out["source_examples"].append(line[:500])
    return out
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--max-archives-per-language",type=int,default=3)
    ap.add_argument("--sample-per-archive",type=int,default=12)
    args=ap.parse_args()
    out=Path(args.out); archives=out/"archives";archives.mkdir(parents=True,exist_ok=True)
    sess=requests.Session()
    index=out/"links.parquet";get(sess,INDEX_URL,index)
    table=pq.read_table(index); rows=table.to_pylist()
    selected=[]
    for code,(name,iso3) in TARGETS.items():
        matches=[r for r in rows if str(r.get("language_short","")).lower()==iso3 or str(r.get("language","")).strip().lower()==name.lower()]
        # Select varied nominal corpus sizes and years, preferring 100K/300K/30K.
        rank={"100K":0,"300K":1,"30K":2,"1M":3,"10K":4}
        matches.sort(key=lambda r:(rank.get(str(r.get("size","")).upper(),9),str(r.get("year","")),str(r.get("data_id",""))))
        selected.extend((code,r) for r in matches[:args.max_archives_per_language])
    manifest=[]
    for i,(code,row) in enumerate(selected,1):
        data_id=str(row["data_id"]);url=str(row.get("url") or f"https://downloads.wortschatz-leipzig.de/corpora/{quote(data_id,safe='._-')}.tar.gz")
        path=archives/(data_id+".tar.gz")
        rec={"target_label":code,"language":row.get("language"),"language_short":row.get("language_short"),
             "data_id":data_id,"year":row.get("year"),"nominal_size":row.get("size"),
             "archive_url":url,"archive_file":path.name}
        try:
            get(sess,url,path)
            rec["archive_bytes"]=path.stat().st_size;rec["archive_sha256"]=sha(path)
            rec["download_status"]="downloaded"
            rec["inspection"]=inspect_archive(path,data_id)
            rec["inspection_status"]="parsed" if rec["inspection"]["sentence_member"] else "missing_sentence_member"
        except Exception as e:
            rec["download_status"]="error";rec["error"]=repr(e)
        manifest.append(rec)
        print(f"[{i}/{len(selected)}] {code} {data_id}: {rec['download_status']} {rec.get('inspection',{}).get('sentence_rows',0)} sentences")
        time.sleep(1.0)
    (out/"manifest.json").write_text(json.dumps({
      "source":"Leipzig Corpora Collection","licence":"CC BY 4.0",
      "licence_url":"https://wortschatz.uni-leipzig.de/en/usage",
      "index_url":INDEX_URL,"index_sha256":sha(index),
      "index_rows":len(rows),"target_languages":list(TARGETS),
      "archives":manifest,
      "note":"Pilot acquisition. Retain attribution; downstream filtering, PII, language verification, deduplication and source balance remain pending."
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"ATTRIBUTION.txt").write_text(
      "Leipzig Corpora Collection, Leipzig University. Downloadable text corpora licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).\n"
      "Licence: https://creativecommons.org/licenses/by/4.0/\n"
      "Usage statement: https://wortschatz.uni-leipzig.de/en/usage\n"
      "Citation: Goldhahn, Dirk; Eckart, Thomas; Quasthoff, Uwe (2012), Building Large Monolingual Dictionaries at the Leipzig Corpora Collection: From 100 to 200 Languages, LREC 2012, pp. 759–765.\n",
      encoding="utf-8")
    print(json.dumps({"index_rows":len(rows),"target_archives":len(selected),
      "downloaded":sum(x.get("download_status")=="downloaded" for x in manifest),
      "parsed":sum(x.get("inspection_status")=="parsed" for x in manifest)},indent=2))
    if not selected: raise SystemExit("No Icelandic or Croatian rows found in the pinned HF Parquet index")
    if any(x.get("download_status")!="downloaded" or x.get("inspection_status")!="parsed" for x in manifest):
        raise SystemExit("One or more pilot archives failed; see manifest")
if __name__=="__main__": main()
