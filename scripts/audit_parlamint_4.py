#!/usr/bin/env python3
"""Full audit of selected ParlaMint 4.0 parliamentary corpora (IS, SI, TR)."""
from __future__ import annotations
import collections, hashlib, json, os, tarfile, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

SOURCES = {
 "is": {"name":"ParlaMint-IS","url":"https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1859/ParlaMint-IS.tgz?isAllowed=y&sequence=16","md5":"59e4889f7f81b23cbdc96b827bea4a40"},
 "sl": {"name":"ParlaMint-SI","url":"https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1859/ParlaMint-SI.tgz?isAllowed=y&sequence=24","md5":"a710c3869b2aaa89da3b9eaa3c7eb83f"},
 "tr": {"name":"ParlaMint-TR","url":"https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1859/ParlaMint-TR.tgz?isAllowed=y&sequence=25","md5":"82569712b7194216a18012af5bac992c"},
}
OUT=Path("reports/parlamint-4-selected-audit.json")
CHUNK=1024*1024
XML_ID="{http://www.w3.org/XML/1998/namespace}id"

def audit_xml(stream, filename, stats):
    stack=[]
    utterance_depth=None
    for event, elem in ET.iterparse(stream, events=("start","end")):
        tag=elem.tag.rsplit("}",1)[-1] if isinstance(elem.tag,str) else str(elem.tag)
        if event=="start":
            stack.append(elem)
            if tag=="u" and utterance_depth is None:
                utterance_depth=len(stack)
            continue
        depth=len(stack)
        if utterance_depth is not None:
            if depth==utterance_depth and tag=="u":
                text=" ".join("".join(elem.itertext()).split())
                stats["utterances"]+=1
                stats["characters"]+=len(text)
                stats["whitespace_tokens"]+=len(text.split())
                stats["empty_utterances"]+=not bool(text)
                who=elem.attrib.get("who")
                if who: stats["speaker_refs"].add(who)
                uid=elem.attrib.get(XML_ID)
                if uid: stats["utterance_ids"]+=1
                parent=stack[-2] if len(stack)>1 else None
                if parent is not None: parent.remove(elem)
                elem.clear(); utterance_depth=None
        else:
            if len(stack)>1:
                stack[-2].remove(elem)
            elem.clear()
        stack.pop()

def main():
    report={"dataset":"ParlaMint 4.0","record":"https://hdl.handle.net/11356/1859",
            "licence":"CC BY 4.0","sources":{}}
    for lang, meta in SOURCES.items():
        fd,name=tempfile.mkstemp(prefix=f"parlamint-{lang}-",suffix=".tgz")
        os.close(fd); path=Path(name)
        sha=hashlib.sha256(); md5=hashlib.md5(); size=0
        st=collections.Counter(); st["speaker_refs"]=set()
        try:
            with requests.get(meta["url"],stream=True,timeout=(60,300),
                              headers={"User-Agent":"langid-32-source-audit/1"}) as r:
                r.raise_for_status()
                with path.open("wb") as out:
                    for block in r.iter_content(CHUNK):
                        if block:
                            out.write(block); sha.update(block); md5.update(block); size+=len(block)
            xml_files=[]; member_count=0; uncompressed=0
            with tarfile.open(path,"r:gz") as tf:
                for member in tf:
                    if not member.isfile(): continue
                    member_count+=1; uncompressed+=member.size
                    lower=member.name.lower()
                    if lower.endswith(".xml") and "listperson" not in lower and "listorg" not in lower and "taxonomy" not in lower and not lower.endswith(".ana.xml"):
                        f=tf.extractfile(member)
                        if f is None: continue
                        before=st["utterances"]
                        audit_xml(f,member.name,st)
                        xml_files.append({"name":member.name,"bytes":member.size,
                                          "utterances":st["utterances"]-before})
            report["sources"][lang]={
                "name":meta["name"],"download_url":meta["url"],"archive_bytes":size,
                "archive_sha256":sha.hexdigest(),"archive_md5":md5.hexdigest(),
                "catalogue_md5":meta["md5"],"md5_matches":md5.hexdigest()==meta["md5"],
                "tar_regular_members":member_count,"uncompressed_member_bytes":uncompressed,
                "tei_session_files":len(xml_files),"utterances":st["utterances"],
                "characters":st["characters"],"whitespace_tokens":st["whitespace_tokens"],
                "empty_utterances":st["empty_utterances"],"utterance_ids_present":st["utterance_ids"],
                "distinct_speaker_refs":len(st["speaker_refs"]),"session_files":xml_files,
                "method":"Full tar.gz download; parsed every TEI session XML, counted <u> elements and text; metadata/listPerson/taxonomy files excluded from speech counts."
            }
        finally:
            path.unlink(missing_ok=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))

if __name__=="__main__": main()
