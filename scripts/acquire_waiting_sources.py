import argparse,csv,gzip,hashlib,json,re,shutil,subprocess,tarfile,tempfile,unicodedata,zipfile
from pathlib import Path
from urllib.request import Request,urlopen
from collections import Counter,defaultdict
import heapq
E=re.compile(r"(?i)\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b"); U=re.compile(r"(?i)(https?://|www\.)\S+"); N=re.compile(r"\d{9,}")
def clean(s,l):
 s=" ".join(unicodedata.normalize("NFC",str(s or "")).split()); a=sum(c.isalpha() for c in s)
 if len(s)<40 or len(s)>12000 or a<25 or a/len(s)<.45 or E.search(s) or U.search(s) or N.search(s) or IP.search(s):return None
 if LID is not None and l in {"ca","is","ar","ko"}:
  try:
   labels,probs=LID.predict(s.replace("\\n"," ")[:4000],k=1)
   if labels[0] != "__label__"+l or probs[0] < .55:return None
  except Exception:return None
 if l=="ar" and sum("\u0600"<=c<="\u06ff" for c in s)<max(10,a*.35):return None
 return s
def fetch(u,p):
 h=hashlib.sha256();n=0
 with urlopen(Request(u,headers={"User-Agent":"langid-32-source-audit/1"}),timeout=180) as r,p.open("wb") as f:
  while True:
   b=r.read(1048576)
   if not b:break
   f.write(b);h.update(b);n+=len(b)
 return {"url":u,"bytes":n,"sha256":h.hexdigest()}
def main():
 global LID
 import csv as _csv
 _csv.field_size_limit(10000000)
 import fasttext
 model=Path(tempfile.gettempdir())/"lid.176.ftz"
 if not model.exists():fetch("https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz",model)
 LID=fasttext.load_model(str(model))
 q=argparse.ArgumentParser();q.add_argument("--source",required=True);q.add_argument("--out",required=True);a=q.parse_args();t=Path(tempfile.mkdtemp());o=Path(a.out);o.mkdir(parents=True,exist_ok=True);R=defaultdict(list);S=defaultdict(set);D=[];notes=[];scanned=Counter()
 def add(l,s,x,g=""):
  x=clean(x,l)
  if not x:return
  key=(l,s);h=hashlib.sha256(x.encode()).hexdigest();scanned[key]+=1
  if h in S[key]:return
  rank=int(h,16);item={"text":x,"language":l,"source":s,"group_id":g or hashlib.sha256((s+x).encode()).hexdigest()}
  heap=R[key]
  if len(heap)<50000:
   heapq.heappush(heap,(-rank,item,h));S[key].add(h)
  elif rank < -heap[0][0]:
   removed=heapq.heapreplace(heap,(-rank,item,h));S[key].remove(removed[2]);S[key].add(h)
 def scan(root,l,s):
  for p in ([root] if root.is_file() else root.rglob("*")):
   if not p.is_file():continue
   try:
    if p.name.endswith(".jsonl") or p.name.endswith(".jsonl.gz"):
     op=gzip.open if p.name.endswith(".gz") else open
     with op(p,"rt",encoding="utf8",errors="replace") as f:
      for i,line in enumerate(f):
       try:x=json.loads(line)
       except:continue
       if isinstance(x,dict):
        vals=[]
        for k in ("fulltext","text","content","sentence","body"):
         v=x.get(k)
         if isinstance(v,str):vals.append(v)
         elif isinstance(v,list):vals += [z for z in v if isinstance(z,str)]
        if not vals:vals=[v for v in x.values() if isinstance(v,str) and len(v)>60]
        for v in vals:add(l,s,v,str(x.get("doc_id") or x.get("doc_hash") or i))
       elif isinstance(x,str):add(l,s,x)
    elif p.suffix.lower() in (".txt",".tsv",".csv"):
     with p.open(encoding="utf8",errors="replace") as f:
      for row in (csv.reader(f,delimiter="\t") if p.suffix.lower()==".tsv" else f):
       if isinstance(row,list):
        if row:add(l,s,row[0])
       else:add(l,s,row)
   except Exception as e:notes.append(str(p)+": "+str(e))
 try:
  if a.source=="catalan":
   r=t/"temu";subprocess.run(["git","clone","--depth","1","https://github.com/TeMU-BSC/catalan_CC0_sentences.git",str(r)],check=True)
   fs=["catalan_government_crawling_frases_seleccionades_filtrades.txt","datasets_sentences.tsv","edited_generated_selected_chatbot.txt","edited_selected_chatbot.txt","frases_spl.txt","generades_spl_seleccionades.txt","more_intents.txt","plantilles_intents.txt","literatura.txt","sentences_from_xitxat_corpus.txt","sentences_from_xitxat_corpus2.txt","wikidata_sentences.txt"]
   for n in fs:
    if (r/n).exists():scan(r/n,"ca","temu_cc0:"+n)
   try:
    from datasets import load_dataset
    for i,x in enumerate(load_dataset("catallama/Catalan-DPO-V2",split="train",streaming=True)):
     for m in x.get("messages",[]) or []:
      if isinstance(m,dict) and m.get("role")=="assistant":add("ca","catalan_dpo_v2:messages",m.get("content"))
     add("ca","catalan_dpo_v2:chosen",x.get("chosen"))
     if i>=23499:break
   except Exception as e:notes.append("DPO: "+repr(e))
   base="https://huggingface.co/datasets/BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus/resolve/main/"
   for n in ("dogc_ca-es.tsv","legal_ca-es_dataset_clean.tsv","apdcat_ca-es.docs.jsonl"):
    p=t/n
    try:D.append(fetch(base+n,p));scan(p,"ca","bsc_legal:"+n)
    except Exception as e:notes.append(n+": "+repr(e))
  elif a.source=="icelandic":
   for n,u,z in [("igc","https://repository.clarin.is/repository/xmlui/bitstream/handle/20.500.12537/381/igc2024-1-filtered.zip?sequence=1&isAllowed=y",1),("greynir","https://repository.clarin.is/repository/xmlui/bitstream/handle/20.500.12537/119/GreynirCorpus-1.1.tar.gz?sequence=1&isAllowed=y",0)]:
    p=t/(n+(".zip" if z else ".tgz"))
    try:
     D.append(fetch(u,p));d=t/n;d.mkdir()
     if z:
      with zipfile.ZipFile(p) as f:f.extractall(d)
     else:
      with tarfile.open(p,"r:gz") as f:f.extractall(d,filter="data")
     scan(d,"is",n)
    except Exception as e:notes.append(n+": "+repr(e))
  elif a.source=="norwegian":
   for l,c in [("nb","nob"),("nn","nno")]:
    p=t/(l+".tar");u="https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026_"+c+".tar"
    try:
     D.append(fetch(u,p));d=t/l;d.mkdir()
     with tarfile.open(p) as f:f.extractall(d,filter="data")
     scan(d,l,"maalfrid2026:"+l)
    except Exception as e:notes.append(l+": "+repr(e))
  elif a.source=="korean":
   from datasets import load_dataset
   # CC BY-SA/GFDL candidate; keep separate from permissive sources.
   ds=load_dataset("wikimedia/wikipedia","20231101.ko",split="train",streaming=True)
   import re as _re
   for i,x in enumerate(ds):
    for para in _re.split(r"(?<=[.!?。！？])\\s+|\\n+",x.get("text","")):
     add("ko","korean_wikipedia_20231101",para,str(x.get("id") or i))
    if i>=499999:break
   notes.append("Wikimedia Korean dump streamed up to 500k articles; CC BY-SA/GFDL attribution and share-alike obligations retained.")
  elif a.source=="fineweb2":
   from datasets import load_dataset
   for lang,config in (("ca","cat_Latn"),("is","isl_Latn")):
    try:
     ds=load_dataset("HuggingFaceFW/fineweb-2",config,split="train",streaming=True)
     src="fineweb2:"+config
     for i,x in enumerate(ds):
      add(lang,src,x.get("text"))
      if i>=499999:break
     notes.append(config+": streamed up to 500k documents; underlying web-text rights unresolved, technical candidates only.")
    except Exception as e:notes.append(config+": "+repr(e))
  elif a.source=="arabic":
   from datasets import load_dataset
   for i,x in enumerate(load_dataset("ymoslem/UN-Arabic-English-Filtered",split="train",streaming=True)):
    add("ar","un_arabic_english_filtered:text_ar",x.get("text_ar"))
    if i%100000==0:print(f"Arabic pairs streamed: {i}",flush=True)
   notes.append("Full training split streamed; output capped at 50,000 unique candidate passages.")
  chosen=[];stats=Counter()
  for (l,s),heap in sorted(R.items()):
   items=[x[1] for x in heap];chosen.extend(items)
   stats[l+"|"+s+"|screened"]=scanned[(l,s)]
   stats[l+"|"+s+"|unique_sampled"]=len(items)
  seen=set();dedup=[]
  for x in chosen:
   k=(x["language"],hashlib.sha256(x["text"].encode()).hexdigest())
   if k in seen:stats[x["language"]+":cross_source_sample_duplicates"]+=1;continue
   seen.add(k);dedup.append(x)
  chosen=dedup
  with (o/"candidates.jsonl").open("w",encoding="utf8") as f:
   for x in chosen:f.write(json.dumps(x,ensure_ascii=False)+"\n")
  c=Counter((x["language"],x["source"]) for x in chosen)
  report={"source_group":a.source,"downloads":D,"counts":{"|".join(k):v for k,v in sorted(c.items())},"stats":dict(stats),"total_selected":len(chosen),"notes":notes,"stats_note":"screened counts include repeated texts; unique_sampled is a deterministic hash-priority sample capped at 50k per source; cross-source dedup applies to sampled records only.","status":"automated candidate only; legal and human quality review remain"}
  (o/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n");print(json.dumps(report,ensure_ascii=False,indent=2))
 finally:shutil.rmtree(t,ignore_errors=True)
if __name__=="__main__":main()
