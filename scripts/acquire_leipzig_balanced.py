#!/usr/bin/env python3
"""Stream up to 20,000 eligible unique entries per Leipzig source and language."""
from __future__ import annotations
import argparse, hashlib, heapq, json, re, tarfile, time
from pathlib import Path
from urllib.parse import quote
import requests
import pyarrow.parquet as pq

INDEX_URL="https://huggingface.co/datasets/imvladikon/leipzig_corpora_collection/resolve/refs%2Fconvert%2Fparquet/links/train/0000.parquet"
BASE="https://downloads.wortschatz-leipzig.de/corpora/"
LANGS={"ar":["ara"],"bg":["bul"],"ca":["cat"],"hr":["hrv"],"cs":["ces","cze"],"da":["dan"],"nl":["nld","dut"],"en":["eng"],"et":["est"],"fi":["fin"],"fr":["fra","fre"],"de":["deu","ger"],"el":["ell","gre"],"hu":["hun"],"is":["isl"],"ga":["gle"],"it":["ita"],"ja":["jpn"],"ko":["kor"],"lv":["lav"],"lt":["lit"],"mt":["mlt"],"nb":["nob"],"nn":["nno"],"pl":["pol"],"pt":["por"],"ro":["ron","rum"],"ru":["rus"],"sk":["slk","slo"],"sl":["slv"],"es":["spa"],"sv":["swe"],"tr":["tur"],"zh":["zho","chi"]}
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def fetch(s,u,p):
 if p.exists() and p.stat().st_size:return
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+".part")
 with s.get(u,stream=True,timeout=(30,300),headers={"User-Agent":"langid-32 corpus acquisition/1.0"}) as r:
  r.raise_for_status()
  with tmp.open("wb") as f:
   for b in r.iter_content(1048576):
    if b:f.write(b)
 tmp.replace(p)
def tsv(tf,m):
 f=tf.extractfile(m)
 if f:
  for raw in f:
   line=raw.decode("utf-8","replace").rstrip("\r\n")
   if line:yield line.split("\t")
def sample(archive,data_id,label,family,quota,seed):
 with tarfile.open(archive,"r:gz") as tf:
  ms=[m for m in tf.getmembers() if m.isfile()]
  sent=next((m for m in ms if m.name.endswith("-sentences.txt")),None)
  inv=next((m for m in ms if m.name.endswith("-inv_so.txt")),None)
  src=next((m for m in ms if m.name.endswith("-sources.txt")),None)
  if not sent:raise RuntimeError("missing sentences member")
  invmap={p[0]:p[1] for p in tsv(tf,inv) if len(p)>1} if inv else {}
  sources={p[0]:{"url":p[1],"timestamp":p[2] if len(p)>2 else ""} for p in tsv(tf,src) if len(p)>1} if src else {}
  archive_sha=sha(archive);heap=[];eligible=digits=0
  for p in tsv(tf,sent):
   if len(p)<2:continue
   sid=p[0];text="\t".join(p[1:]).strip()
   if not text:continue
   if family=="news" and any(c.isdecimal() for c in text):digits+=1;continue
   eligible+=1;rank=int(hashlib.sha256((seed+"\0"+label+"\0"+family+"\0"+sid+"\0"+text).encode()).hexdigest(),16)
   item=(-rank,sid,text)
   if len(heap)<quota:heapq.heappush(heap,item)
   elif rank < -heap[0][0]:heapq.heapreplace(heap,item)
  rows=[]
  for _,sid,text in sorted(heap):
   so=invmap.get(sid);meta=sources.get(so,{})
   rows.append({"text":text,"language":label,"source":"leipzig_"+family,"source_release":data_id,
    "group_id":"leipzig:"+data_id+":source:"+(so or sid),"licence_id":"CC-BY-4.0",
    "text_origin":"news/web text" if family=="news" else "Wikipedia text",
    "provenance":{"collection":"Leipzig Corpora Collection","data_id":data_id,"sentence_id":sid,
     "source_id":so,"source_url":meta.get("url"),"source_timestamp":meta.get("timestamp"),
     "archive_sha256":archive_sha,"archive_url":BASE+quote(data_id,safe="._-")+".tar.gz",
     "index_url":INDEX_URL,"selection_seed":seed,
     "digit_filter":"Unicode decimal digits excluded" if family=="news" else "not applied"}})
 return rows,{"eligible_sentences":eligible,"rejected_digit_sentences":digits,"selected":len(rows),
  "source_mapping_rows":len(invmap),"source_metadata_rows":len(sources),"has_inverse_source_member":bool(inv),"has_sources_member":bool(src)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);ap.add_argument("--quota",type=int,default=20000)
 ap.add_argument("--seed",default="langid-32-leipzig-2026-11-18");ap.add_argument("--pause",type=float,default=1);ap.add_argument("--labels",default="",help="Comma-separated target labels; default is all 34")
 a=ap.parse_args();out=Path(a.out);ar=out/"archives";sm=out/"samples";ar.mkdir(parents=True,exist_ok=True);sm.mkdir(parents=True,exist_ok=True)
 s=requests.Session();idx=out/"links.parquet";fetch(s,INDEX_URL,idx);idxsha=sha(idx);cat=pq.read_table(idx).to_pylist()
 selected_labels={x.strip() for x in a.labels.split(",") if x.strip()}
 unknown=selected_labels-set(LANGS)
 if unknown:raise SystemExit("Unknown labels: "+", ".join(sorted(unknown)))
 manifest={"collection":"Leipzig Corpora Collection","licence":"CC BY 4.0","licence_url":"https://wortschatz.uni-leipzig.de/en/usage",
  "index_url":INDEX_URL,"index_sha256":idxsha,"index_rows":len(cat),"quota_per_family":a.quota,
  "policy":"3,000 news + 3,000 Wikipedia per language; Unicode decimal digits excluded from news only","archives":[]}
 todo=[]
 for label,codes in LANGS.items():
  if selected_labels and label not in selected_labels:continue
  rows=[r for r in cat if str(r.get("language_short","")).lower() in codes]
  for fam,pat in [("news",re.compile("news|newscrawl",re.I)),("wikipedia",re.compile("wikipedia",re.I))]:
   choices=[r for r in rows if pat.search(str(r.get("data_id","")))]
   pref={"100K":0,"300K":1,"30K":2,"1M":3,"10K":4}
   choices.sort(key=lambda r:(pref.get(str(r.get("size","")).upper(),8),str(r.get("year","")),str(r.get("data_id",""))))
   todo.append((label,fam,choices[0] if choices else None))
 for i,(label,fam,r) in enumerate(todo,1):
  if r is None:
   manifest["archives"].append({"label":label,"family":fam,"status":"missing_catalogue_entry"});print(f"{i}/{len(todo)} missing {label}/{fam}");continue
  did=str(r["data_id"]);url=str(r.get("url") or BASE+quote(did,safe="._-")+".tar.gz");arc=ar/(did+".tar.gz")
  rec={"label":label,"family":fam,"data_id":did,"catalogue_language":r.get("language"),
   "language_short":r.get("language_short"),"year":r.get("year"),"nominal_size":r.get("size"),"archive_url":url}
  try:
   fetch(s,url,arc);rec.update({"archive_file":str(arc.relative_to(out)),"archive_bytes":arc.stat().st_size,"archive_sha256":sha(arc)})
   rows,stats=sample(arc,did,label,fam,a.quota,a.seed);rec["selection"]=stats
   rec["status"]="sampled" if len(rows)==a.quota else "short_sample"
   p=sm/(label+"-"+fam+".jsonl")
   with p.open("w",encoding="utf-8") as f:
    for row in rows:f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
   rec["sample_file"]=str(p.relative_to(out));rec["sample_sha256"]=sha(p)
   print(f"{i}/{len(todo)} {label}/{fam} {did}: {len(rows)}/{a.quota}")
  except Exception as e:rec["status"]="error";rec["error"]=repr(e);print(f"{i}/{len(todo)} ERROR {did}: {e}")
  manifest["archives"].append(rec);time.sleep(a.pause)
 with (out/"leipzig-candidates.jsonl").open("w",encoding="utf-8") as f:
  for p in sorted(sm.glob("*.jsonl")):
   with p.open(encoding="utf-8") as src:
    for line in src:f.write(line)
 manifest["sample_rows"]=sum(x.get("selection",{}).get("selected",0) for x in manifest["archives"])
 manifest["successful_archives"]=sum(x.get("status")=="sampled" for x in manifest["archives"])
 manifest["missing_or_failed"]=sum(x.get("status")!="sampled" for x in manifest["archives"])
 (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (out/"ATTRIBUTION.txt").write_text("Leipzig Corpora Collection, Leipzig University. Downloadable text corpora are made available under Creative Commons Attribution 4.0 International (CC BY 4.0).\nLicence: https://creativecommons.org/licenses/by/4.0/\nUsage statement: https://wortschatz.uni-leipzig.de/en/usage\nCitation: Goldhahn, Dirk; Eckart, Thomas; Quasthoff, Uwe (2012), Building Large Monolingual Dictionaries at the Leipzig Corpora Collection: From 100 to 200 Languages, LREC 2012, pp. 759–765.\n",encoding="utf-8")
 print(json.dumps({"index_rows":len(cat),"target_labels":len({x[0] for x in todo}),"archive_slots":len(todo),
  "successful_archives":manifest["successful_archives"],"sample_rows":manifest["sample_rows"],
  "missing_or_failed":manifest["missing_or_failed"]},indent=2))
 if manifest["missing_or_failed"]:print("WARNING: partial acquisition; missing/failed slots are recorded in manifest.json")
if __name__=="__main__":main()
