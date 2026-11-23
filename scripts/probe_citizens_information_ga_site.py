#!/usr/bin/env python3
"""Probe the current Citizens Information Irish-language website route and robots policy."""
from __future__ import annotations
import hashlib, json, re, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "langid-32-source-audit/1.0 (+https://github.com/SylvainSouche/langid-32)"
ROOTS = ["https://www.citizensinformation.ie", "https://api.uat.citizensinformation.ie"]
PATHS = ["/robots.txt", "/sitemap.xml", "/sitemap_index.xml", "/ga/",
         "/ga/employment/employment-rights-and-conditions/employment-rights-and-duties/employee-rights-and-entitlements/"]
OUT = Path("citizens-information-ga-site-probe.json")

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=False; self.title_text=[]; self.lang=None; self.links=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="html": self.lang=a.get("lang")
        if tag=="title": self.title=True
        if tag=="a" and a.get("href"): self.links.append(a["href"])
    def handle_endtag(self, tag):
        if tag=="title": self.title=False
    def handle_data(self, data):
        if self.title: self.title_text.append(data)

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/xml,text/plain,*/*"})
    try:
        with urllib.request.urlopen(req,timeout=45) as r:
            body=r.read(5_000_000)
            ctype=r.headers.get("Content-Type","")
            result={"status":r.status,"final_url":r.geturl(),"content_type":ctype,
                    "bytes_read":len(body),"sha256":hashlib.sha256(body).hexdigest()}
            if "text" in ctype or "xml" in ctype or "html" in ctype:
                text=body.decode("utf-8","replace")
                result["preview"]=text[:2000]
                if "html" in ctype:
                    p=Page();p.feed(text)
                    result["html_lang"]=p.lang
                    result["title"]=" ".join(" ".join(p.title_text).split())
                    result["links_sample"]=p.links[:100]
                if url.endswith("/robots.txt"):
                    result["sitemap_directives"]=[x.split(":",1)[1].strip() for x in text.splitlines() if x.lower().startswith("sitemap:")]
                    result["disallow_ga"]=[x for x in text.splitlines() if x.lower().startswith(("disallow:","allow:")) and "/ga" in x.lower()]
            return result
    except urllib.error.HTTPError as e:
        return {"status":e.code,"final_url":e.geturl(),"content_type":e.headers.get("Content-Type")}
    except Exception as e:
        return {"error":f"{type(e).__name__}: {e}"}

def main():
    results=[]
    for root in ROOTS:
        for path in PATHS:
            url=root+path
            result=fetch(url)
            results.append({"url":url,**result})
    report={"purpose":"Determine whether the current Citizens Information production Irish-language pages are crawlable under the publisher's CC BY 4.0 reuse statement; UAT host is a separate non-production comparator.",
            "results":results,"method":"GET-only probes of robots.txt, common sitemap endpoints, Irish homepage and one Irish article. No crawl beyond these URLs and no text corpus acquired."}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
