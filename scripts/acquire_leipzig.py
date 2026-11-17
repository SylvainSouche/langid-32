#!/usr/bin/env python3
"""Inventory and sample official Leipzig Corpora Collection bulk archives.

Only follows archive filenames explicitly exposed by Leipzig's public download
pages. Does not solve/bypass anti-bot challenges. All data is quarantined:
licence and underlying-source rights remain PENDING pending corpus-specific review.
"""
import argparse, csv, hashlib, json, os, re, tarfile, time, unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup

BASE = "https://wortschatz.uni-leipzig.de"
ARCHIVE_BASE = "https://pcai056.informatik.uni-leipzig.de/downloads/corpora/"
LANGS = {
 "ar":"Arabic","ca":"Catalan","zh":"Chinese","hr":"Croatian","cs":"Czech",
 "da":"Danish","nl":"Dutch","en":"English","et":"Estonian","fi":"Finnish",
 "fr":"French","de":"German","el":"Greek","ga":"Irish","hu":"Hungarian",
 "is":"Icelandic","it":"Italian","ko":"Korean","lv":"Latvian","lt":"Lithuanian",
 "mt":"Maltese","nb":"Norwegian Bokmål","nn":"Norwegian Nynorsk","pl":"Polish",
 "pt":"Portuguese","ro":"Romanian","ru":"Russian","sk":"Slovak","sl":"Slovenian",
 "es":"Spanish","sv":"Swedish","tr":"Turkish","bg":"Bulgarian"
}
# ISO-639-3 / Leipzig language-page labels seen in public catalogue variants.
ALIASES = {
 "norwegian bokmål":"nb","norwegian nynorsk":"nn","bokmål":"nb","nynorsk":"nn",
 "chinese":"zh","mandarin chinese":"zh","irish":"ga","korean":"ko",
 "icelandic":"is","catalan":"ca","slovenian":"sl","croatian":"hr",
 "finnish":"fi","turkish":"tr","arabic":"ar"
}
HEADERS = {"User-Agent":"langid-32 research corpus audit; public bulk-download links only"}
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d .()/-]{7,}\d)(?!\w)")
LONGNUM = re.compile(r"(?<!\w)\d{9,}(?!\w)")

def request(session, url, stream=False):
    r = session.get(url, headers=HEADERS, timeout=(25,180), stream=stream)
    r.raise_for_status()
    if not stream and ("Anubis" in r.text[:8000] or "Making sure you're not a bot" in r.text):
        raise RuntimeError("Leipzig anti-bot challenge; no bypass attempted")
    return r

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def clean(s):
    return " ".join(unicodedata.normalize("NFC",s).split())

def lang_code(label, page_url):
    key=clean(label).lower()
    if key in ALIASES: return ALIASES[key]
    for c,n in LANGS.items():
        if key == n.lower(): return c
    # Language pages may use ISO3 slugs rather than English names.
    slug=page_url.rstrip("/").split("/")[-1].lower()
    iso3={"cat":"ca","isl":"is","nob":"nb","nno":"nn","gle":"ga","slv":"sl",
          "hrv":"hr","fin":"fi","kor":"ko","tur":"tr","ara":"ar","zho":"zh"}
    return iso3.get(slug)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--max-archives-per-language",type=int,default=3)
    ap.add_argument("--max-archive-gb",type=float,default=1.5)
    ap.add_argument("--sample-per-archive",type=int,default=100000)
    args=ap.parse_args()
    out=Path(args.out); downloads=out/"archives";downloads.mkdir(parents=True,exist_ok=True)
    sess=requests.Session(); pages=[]; errors=[]; archive_links=[]
    # First crawl the complete language catalogue; then fetch target language pages.
    try:
        root=request(sess,BASE+"/en/download")
        (out/"download-index.html").write_text(root.text,encoding="utf-8")
        soup=BeautifulSoup(root.text,"html.parser")
        for a in soup.select(".list-group-item a[href]"):
            label=clean(a.get_text(" ",strip=True)); href=urljoin(BASE,a["href"])
            code=lang_code(label,href)
            pages.append({"label":label,"code":code,"url":href})
    except Exception as e:
        errors.append({"stage":"language_index","error":repr(e)})
    # Use exact known target labels if the index is inaccessible/incomplete.
    seen={p["code"] for p in pages if p["code"]}
    for c,n in LANGS.items():
        if c not in seen:
            pages.append({"label":n,"code":c,"url":BASE+"/en/download/"+quote(n,safe="")})
    # Save all catalogue labels, including languages outside the target set.
    catalogue=[]
    for p in pages:
        catalogue.append(p)
        if not p["code"] or p["code"] not in LANGS: continue
        try:
            r=request(sess,p["url"])
            (out/f"page-{p['code']}.html").write_text(r.text,encoding="utf-8")
            ps=BeautifulSoup(r.text,"html.parser")
            for a in ps.select("a[data-corpora-file]"):
                fn=a.get("data-corpora-file","").strip()
                if not fn: continue
                # Attribute is the authoritative archive basename; do not guess paths.
                archive_links.append({
                    "language":p["code"],"language_name":LANGS[p["code"]],
                    "page_url":p["url"],"label":clean(a.get_text(" ",strip=True)),
                    "filename":fn,"url":urljoin(ARCHIVE_BASE,quote(fn,safe="._-")),
                    "corpus_meta":{k:v for k,v in a.attrs.items() if k.startswith("data-")}
                })
            time.sleep(.25)
        except Exception as e:
            errors.append({"stage":"language_page","language":p["code"],"url":p["url"],"error":repr(e)})
    # Keep inventory for all linked target corpora; download a bounded representative set.
    dedup={}
    for x in archive_links: dedup[(x["language"],x["filename"])]=x
    archive_links=list(dedup.values())
    archive_links.sort(key=lambda x:(x["language"],x["filename"]))
    (out/"catalogue.json").write_text(json.dumps({
      "catalogue_languages":catalogue,"target_archive_links":archive_links,
      "errors":errors,"licence_status":"PENDING: API terms do not establish rights in underlying corpus texts"
    },ensure_ascii=False,indent=2)+"\n")
    selected=[]
    per=Counter()
    for x in archive_links:
        c=x["language"]
        if per[c] >= args.max_archives_per_language: continue
        selected.append(x);per[c]+=1
    manifest=[]; quality=[]
    for i,x in enumerate(selected,1):
        rec={**x,"download_status":"pending","licence_status":"PENDING","sha256":None,
             "bytes":None,"sentence_member":None,"sentences_seen":0,"candidate_rows":0}
        try:
            dest=downloads/x["filename"]
            if not dest.exists():
                with request(sess,x["url"],stream=True) as r, open(dest,"wb") as f:
                    for chunk in r.iter_content(1024*1024):
                        if chunk: f.write(chunk)
            size=dest.stat().st_size
            rec["bytes"]=size;rec["sha256"]=sha256(dest)
            if size > args.max_archive_gb*1024**3:
                rec["download_status"]="downloaded_size_cap_exceeded"
                rec["note"]="Downloaded for size/hash inventory; not parsed due configured cap"
            else:
                try:
                    tf=tarfile.open(dest,"r:*")
                except tarfile.TarError:
                    tf=None
                if tf is None:
                    rec["download_status"]="downloaded_unrecognized_archive"
                else:
                    sentmembers=[m for m in tf.getmembers() if m.isfile() and "sentences" in Path(m.name).name.lower()]
                    if not sentmembers:
                        rec["download_status"]="downloaded_no_sentences_member"
                    else:
                        m=sentmembers[0];rec["sentence_member"]=m.name
                        fh=tf.extractfile(m); seen=set(); counts=Counter(); sources=Counter()
                        total=eligible=0; bad={"email":0,"url":0,"ip":0,"phone":0,"long_number":0}
                        for raw in fh:
                            total+=1
                            try: line=raw.decode("utf-8").rstrip("\r\n")
                            except UnicodeDecodeError: continue
                            parts=line.split("\t",1)
                            if len(parts)!=2: continue
                            sid,text=parts[0],clean(parts[1])
                            if not text or len(text)<8: continue
                            if EMAIL.search(text): bad["email"]+=1;continue
                            if URL.search(text): bad["url"]+=1;continue
                            if IP.search(text): bad["ip"]+=1;continue
                            if PHONE.search(text): bad["phone"]+=1;continue
                            if LONGNUM.search(text): bad["long_number"]+=1;continue
                            key=text.casefold()
                            if key in seen: continue
                            seen.add(key);eligible+=1
                            if len(quality)<1: pass
                            if len(seen)<=args.sample_per_archive: sources[sid]+=1
                        rec["sentences_seen"]=total;rec["candidate_rows"]=eligible
                        rec["pii_rejected"]=bad
                        rec["download_status"]="downloaded_parsed"
                        rec["sample_cap"]=args.sample_per_archive
                        rec["candidate_count_is_sentence_level_pre_global_dedup"]=True
                    tf.close()
            manifest.append(rec)
            print(f"[{i}/{len(selected)}] {x['language']} {x['filename']}: {rec['download_status']} {rec['candidate_rows']}")
        except Exception as e:
            rec["download_status"]="error";rec["error"]=repr(e);manifest.append(rec)
            errors.append({"stage":"archive","language":x["language"],"filename":x["filename"],"error":repr(e)})
    (out/"archive-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    # Aggregate per language/source; do not present this as globally deduplicated yield.
    agg=Counter()
    for x in manifest:
        if x["download_status"]=="downloaded_parsed": agg[x["language"]]+=x["candidate_rows"]
    with open(out/"language-summary.tsv","w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,delimiter="\t");w.writerow(["language","archive_count_downloaded","candidate_rows_sum_pre_global_dedup"])
        for c in LANGS: w.writerow([c,sum(1 for x in manifest if x["language"]==c and x["download_status"].startswith("downloaded")),agg[c]])
    (out/"errors.json").write_text(json.dumps(errors,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"catalogue_pages":len(catalogue),"target_archives_found":len(archive_links),
      "archives_selected":len(selected),"archives_parsed":sum(x["download_status"]=="downloaded_parsed" for x in manifest),
      "languages_with_candidates":sum(v>0 for v in agg.values()),"candidate_rows_sum_pre_global_dedup":sum(agg.values()),
      "errors":len(errors),"licence_status":"PENDING"},ensure_ascii=False,indent=2))
    if not archive_links: raise SystemExit("No data-corpora-file archive links found; inventory/error report retained")

if __name__=="__main__": main()
