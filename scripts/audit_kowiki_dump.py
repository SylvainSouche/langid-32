#!/usr/bin/env python3
import bz2, hashlib, json, re, urllib.request
from pathlib import Path
URL="https://dumps.wikimedia.org/kowiki/latest/kowiki-latest-pages-articles.xml.bz2"
OUT=Path("reports/kowiki-latest-audit.json")
def main():
    req=urllib.request.Request(URL,headers={"User-Agent":"langid-32-source-audit/1"})
    h=hashlib.sha256(); compressed=0; pages=0; ns0=0; redirects=0; chars=0
    with urllib.request.urlopen(req,timeout=120) as r:
        total=r.headers.get("Content-Length")
        dec=bz2.BZ2Decompressor(); buf=b""
        while True:
            b=r.read(1024*1024)
            if not b: break
            compressed+=len(b); h.update(b)
            buf += dec.decompress(b)
            while b"</page>" in buf:
                x,buf=buf.split(b"</page>",1)
                x+=b"</page>"
                pages+=1
                if b"<ns>0</ns>" in x: ns0+=1
                if b"<redirect " in x or b"<redirect>" in x: redirects+=1
                m=re.search(br"<text[^>]*>(.*?)</text>",x,re.S)
                if m: chars+=len(m.group(1).decode("utf-8","replace"))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"dataset":"Korean Wikipedia XML dump","url":URL,"compressed_bytes":compressed,"http_content_length":total,"sha256":h.hexdigest(),"page_records":pages,"namespace_0_pages":ns0,"redirect_pages":redirects,"raw_text_characters":chars,"licence":"Wikipedia text: CC BY-SA; GFDL also generally applicable per Wikimedia Foundation. This audit is a dump/volume audit, not release clearance.","method":"Streaming BZ2/XML page-record scan; counts pages and raw text characters without storing the dump."},ensure_ascii=False,indent=2)+"\n")
    print(OUT.read_text())
if __name__=="__main__": main()
