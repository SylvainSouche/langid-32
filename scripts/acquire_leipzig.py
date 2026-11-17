#!/usr/bin/env python3
"""Inventory and acquire Leipzig Corpora Collection sentence corpora for langid-32.

The downloader uses only public, linked Leipzig download URLs. It does not solve,
circumvent, or automate Anubis challenges. All downloaded material is quarantined
as rights-pending until corpus-specific terms are confirmed.
"""
import argparse, csv, hashlib, json, re, time, unicodedata, zipfile, tarfile, io
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import requests
from bs4 import BeautifulSoup

BASE = "https://wortschatz.uni-leipzig.de"
LANGS = {
 "bg":"Bulgarian","cs":"Czech","da":"Danish","de":"German","el":"Greek",
 "en":"English","es":"Spanish","et":"Estonian","fi":"Finnish","fr":"French",
 "ga":"Irish","hr":"Croatian","hu":"Hungarian","is":"Icelandic","it":"Italian",
 "lt":"Lithuanian","lv":"Latvian","mt":"Maltese","nl":"Dutch","pl":"Polish",
 "pt":"Portuguese","ro":"Romanian","sk":"Slovak","sl":"Slovenian","sv":"Swedish",
 "nb":"Norwegian Bokmål","nn":"Norwegian Nynorsk","ru":"Russian","tr":"Turkish",
 "ko":"Korean","ar":"Arabic","ca":"Catalan","zh":"Chinese","ja":"Japanese"
}
HEADERS={"User-Agent":"langid-32 corpus audit (research; contact via repository)"}
def get(session,url):
 r=session.get(url,headers=HEADERS,timeout=90)
 r.raise_for_status()
 if "Making sure you're not a bot" in r.text or "Anubis" in r.text[:5000]:
  raise RuntimeError("Leipzig Anubis anti-bot challenge returned; no challenge bypass attempted")
 return r
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def norm(s):
 return " ".join(unicodedata.normalize("NFC",s).split())
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--out",required=True)
 ap.add_argument("--max-corpora",type=int,default=0,help="0 = all discovered corpora")
 ap.add_argument("--sentences-per-corpus",type=int,default=100000,choices=[10000,30000,100000,300000,1000000])
 args=ap.parse_args()
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 raw=out/"html";raw.mkdir(exist_ok=True)
 sess=requests.Session()
 inventory=[];errors=[]
 for code,name in LANGS.items():
  url=f"{BASE}/en/download/{requests.utils.quote(name,safe='')}"
  try:
   r=get(sess,url)
   (raw/f"{code}.html").write_text(r.text,encoding="utf-8")
   soup=BeautifulSoup(r.text,"html.parser")
   rows=[]
   for tr in soup.select("tr"):
    cells=[" ".join(x.stripped_strings) for x in tr.select("th,td")]
    links=[{"text":" ".join(a.stripped_strings),"href":urljoin(url,a.get("href",""))} for a in tr.select("a[href]")]
    if cells or links: rows.append({"cells":cells,"links":links})
   anchors=[{"text":" ".join(a.stripped_strings),"href":urljoin(url,a.get("href",""))} for a in soup.select("a[href]")]
   inventory.append({"language":code,"language_name":name,"url":url,"title":soup.title.get_text(" ",strip=True) if soup.title else "", "rows":rows,"anchors":anchors,"page_bytes":len(r.content),"status":"ok"})
   time.sleep(.35)
  except Exception as e:
   errors.append({"language":code,"url":url,"error":repr(e)})
 # Discover linked corpus archives, preserving the page context.
 links=[]
 for page in inventory:
  for row in page["rows"]:
   for a in row["links"]:
    if re.search(r"(zip|tar|gz)(?:[?#]|$)",a["href"],re.I) or "download" in a["href"].lower():
     links.append({"language":page["language"],"language_name":page["language_name"],"row":row["cells"],**a})
  for a in page["anchors"]:
   if re.search(r"(zip|tar|gz)(?:[?#]|$)",a["href"],re.I):
    links.append({"language":page["language"],"language_name":page["language_name"],"row":[] ,**a})
 # de-duplicate identical URLs
 uniq={}
 for x in links: uniq[(x["language"],x["href"])]=x
 links=list(uniq.values())
 (out/"inventory.json").write_text(json.dumps({"base":BASE,"languages":inventory,"download_links":links,"errors":errors},ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"language_pages_ok":len(inventory),"language_page_errors":errors,"archive_links_discovered":len(links),"examples":links[:20]},ensure_ascii=False,indent=2))
 if not inventory:
  raise SystemExit("No language pages accessible; see errors and HTML snapshots")
 # Save auditable link inventory even if the download interface exposes no direct archives.
 (out/"download-links.tsv").write_text("language\trow\tlink_text\turl\n"+"".join(
  f"{x['language']}\t{' | '.join(x['row'])}\t{x['text']}\t{x['href']}\n" for x in links),encoding="utf-8")
