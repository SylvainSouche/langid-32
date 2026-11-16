#!/usr/bin/env python3
"""Assemble the complete 640k FineWeb2 sample from base + short-language top-up."""
# Deterministic assembly: base 27 languages plus four complete top-ups.
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

REPLACE={"hr","ga","mt","nn"}
SPLITS=("train","validation","test")
TARGETS={"train":16000,"validation":2000,"test":2000}
LANG_ORDER=["bg","hr","cs","da","nl","et","fi","fr","de","el","hu","ga","it","lv","lt","mt","pl","pt","ro","sk","sl","es","sv","nb","nn","ru","ja","zh","ko","ar","tr"]

def read_jsonl(path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def load_dir(root):
    data={split:[] for split in SPLITS}
    prov=[]
    for split in SPLITS:
        data[split]=list(read_jsonl(root/f"{split}.jsonl"))
    prov=list(read_jsonl(root/"provenance.jsonl"))
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    return data,prov,manifest

def key(row):
    return (row["language"],row["group_id"],row["document_id_hash"],hashlib.sha256(row["text"].encode()).hexdigest())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--topup",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    base,bprov,bmanifest=load_dir(args.base)
    top,tprov,tmanifest=load_dir(args.topup)
    final={split:[r for r in base[split] if r["language"] not in REPLACE] + [r for r in top[split] if r["language"] in REPLACE] for split in SPLITS}
    provenance=[p for p in bprov if p.get("subset","").split("_")[0] not in {"hrv","gle","mlt","nno"}]
    provenance += [p for p in tprov if p.get("subset","").split("_")[0] in {"hrv","gle","mlt","nno"}]
    for split in SPLITS:
        final[split].sort(key=key)
    provenance.sort(key=lambda p:(p.get("subset",""),p.get("group_id",""),p.get("document_id_sha256",""),p.get("sentence_sha256","")))
    counts=Counter()
    seen=defaultdict(set)
    group_split={}
    for split in SPLITS:
        for row in final[split]:
            counts[(row["language"],split)]+=1
            if row["text"] in seen[row["language"]]:
                raise SystemExit(f"duplicate sentence in {row['language']}: {row['text'][:80]!r}")
            seen[row["language"]].add(row["text"])
            gid=row["group_id"]
            previous=group_split.get(gid)
            if previous is not None and previous != split:
                raise SystemExit(f"group assigned to multiple splits: {gid}")
            group_split[gid]=split
    for lang in LANG_ORDER:
        for split in SPLITS:
            expected=TARGETS[split]
            actual=counts[(lang,split)]
            if actual != expected:
                raise SystemExit(f"{lang} {split}: expected {expected}, got {actual}")
    args.output.mkdir(parents=True,exist_ok=True)
    hashes={}
    for split in SPLITS:
        path=args.output/f"{split}.jsonl"
        with path.open("w",encoding="utf-8") as f:
            for row in final[split]:
                f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
        hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    pp=args.output/"provenance.jsonl"
    with pp.open("w",encoding="utf-8") as f:
        for row in provenance:
            f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
    hashes[pp.name]=hashlib.sha256(pp.read_bytes()).hexdigest()
    manifest=dict(bmanifest)
    manifest["assembly"]={
        "base_run_id":43926783433,
        "topup_run_id":43928656525,
        "replacement_languages":sorted(REPLACE),
        "verified_target_counts":dict(TARGETS),
        "global_group_split_consistency":True,
        "exact_sentence_deduplication_verified":True,
    }
    manifest["languages"]=[x for x in bmanifest["languages"] if x["language"] not in REPLACE] + [x for x in tmanifest["languages"] if x["language"] in REPLACE]
    manifest["languages"].sort(key=lambda x:LANG_ORDER.index(x["language"]))
    manifest["output_sha256"]=hashes
    (args.output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"languages":len(LANG_ORDER),"records":sum(len(v) for v in final.values()),"provenance":len(provenance),"hashes":hashes},indent=2))

if __name__=="__main__":
    main()
