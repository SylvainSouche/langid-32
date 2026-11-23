#!/usr/bin/env python3
"""Small, metadata-only feasibility audit of Irish text in Oireachtas debate XML."""
from __future__ import annotations
import hashlib, json
from collections import Counter
from pathlib import Path
import requests
from xml.etree import ElementTree as ET

OUT=Path("reports/oireachtas-ga-pilot.json")
API="https://api.oireachtas.ie/v1/debates"
XML_LANG="{http://www.w3.org/XML/1998/namespace}lang"

def main():
    s=requests.Session()
    r=s.get(API,params={"date_start":"2024-01-01","date_end":"2024-12-31","limit":25,"skip":0},
             timeout=(30,120),headers={"User-Agent":"langid-32-source-audit/1"})
    r.raise_for_status()
    payload=r.json()
    records=payload.get("results",[])
    report={"source":API,"query":{"date_start":"2024-01-01","date_end":"2024-12-31","limit":25,"skip":0},
            "api_counts":payload.get("head",{}).get("counts",{}),"returned_records":len(records),
            "xml_documents":[],"method":"Downloads at most five official debateRecord XML files; counts inherited xml:lang values and speech elements, and stores no source text."}
    urls=[]
    for item in records:
        rec=item.get("debateRecord",{})
        uri=rec.get("formats",{}).get("xml",{}).get("uri")
        if uri and uri not in urls: urls.append(uri)
    report["xml_uris_found"]=len(urls)
    for uri in urls[:5]:
        try:
            x=s.get(uri,stream=True,timeout=(30,180),headers={"User-Agent":"langid-32-source-audit/1"})
            x.raise_for_status()
            path=Path("/tmp/oireachtas.xml"); h=hashlib.sha256(); size=0
            with path.open("wb") as out:
                for b in x.iter_content(1024*1024):
                    if b:
                        size+=len(b)
                        if size>100*1024*1024: raise RuntimeError("XML exceeds 100 MiB pilot limit")
                        out.write(b); h.update(b)
            x.close()
            tags=Counter(); lang_tags=Counter(); speech=Counter(); speech_chars=Counter(); speech_tokens=Counter(); attribute_names=Counter(); language_attr_values=Counter()
            stack=[]; speech_stack=[]
            for event,el in ET.iterparse(path,events=("start","end")):
                tag=el.tag.rsplit("}",1)[-1]
                if event=="start":
                    lang=el.attrib.get(XML_LANG,stack[-1] if stack else "")
                    stack.append(lang)
                    if lang: lang_tags[lang]+=1
                    tags[tag]+=1
                    for key,value in el.attrib.items():
                        attribute_names[key.rsplit("}",1)[-1]]+=1
                        if "lang" in key.lower():
                            language_attr_values[value]+=1
                    if tag.lower()=="speech":
                        speech_stack.append({"lang":lang,"parts":[]})
                else:
                    if speech_stack:
                        if el.text and el.text.strip():
                            speech_stack[-1]["parts"].append(el.text)
                        if tag.lower()!="speech" and el.tail and el.tail.strip():
                            speech_stack[-1]["parts"].append(el.tail)
                    if tag.lower()=="speech" and speech_stack:
                        frame=speech_stack.pop()
                        lang=frame["lang"]
                        speech[lang]+=1
                        if lang=="ga":
                            text=" ".join(frame["parts"])
                            speech_chars["ga"]+=len(text)
                            speech_tokens["ga"]+=len(text.split())
                    if stack: stack.pop()
                    el.clear()
            report["xml_documents"].append({"uri":uri,"bytes":size,"sha256":h.hexdigest(),
                "element_tags":dict(tags.most_common(30)),"attribute_names":dict(attribute_names),
                "language_attribute_values":dict(language_attr_values),
                "xml_lang_inherited_element_counts":dict(lang_tags),
                "speech_elements_by_language":dict(speech),"ga_speech_characters":speech_chars.get("ga",0),
                "ga_speech_whitespace_tokens":speech_tokens.get("ga",0)})
        except Exception as e:
            report["xml_documents"].append({"uri":uri,"error":f"{type(e).__name__}: {e}"})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))

if __name__=="__main__": main()
