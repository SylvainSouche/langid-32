#!/usr/bin/env python3
"""Convert the English FineWeb artifact to the source-neutral staging schema."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

from langid32.merge import LONG_NUMBER_RE, has_phone_like

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    root=args.input
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    revision=manifest.get("source_revision","main")
    licence="ODC-By-1.0;underlying-crawled-text-rights-unresolved"
    provenance={}
    with (root/"provenance.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row=json.loads(line)
            provenance[(row["sentence_sha256"],"en")]=row
    count=0
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8",newline="\n") as output:
        for split in ("train","validation","test"):
            with (root/f"{split}.jsonl").open(encoding="utf-8") as stream:
                for line in stream:
                    row=json.loads(line)
                    text_hash=hashlib.sha256(row["text"].encode("utf-8")).hexdigest()
                    prov=provenance.get((text_hash,row["language"]))
                    if not prov: raise ValueError(f"missing FineWeb provenance for {text_hash}")
                    if row["language"]!="en" or prov.get("group_id")!=row.get("group_id"):
                        raise ValueError("FineWeb record/provenance mismatch")
                    flags=[]
                    if has_phone_like(row["text"]): flags.append("phone_like")
                    if LONG_NUMBER_RE.search(row["text"]): flags.append("long_numeric_sequence")
                    record={
                      "text":row["text"],"language":"en","source":"fineweb","source_release":revision,
                      "group_id":f"fineweb:{prov['group_id']}","split_group_id":prov["group_id"],
                      "licence_id":licence,"text_origin":"original",
                      "provenance":{key:prov.get(key) for key in (
                        "document_id_sha256","source_domain","source_url_sha256","crawl_date",
                        "crawl_dump","language_score","token_count","subset","shard","row_group_id",
                        "shard_oid","shard_lfs_oid")} | {"upstream_split":split,"privacy_flags":flags}
                    }
                    output.write(json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n")
                    count+=1
    print(json.dumps({"records":count,"source":"HuggingFaceFW/fineweb","revision":revision,
                      "licence_id":licence},indent=2))

if __name__=="__main__": main()
