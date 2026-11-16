#!/usr/bin/env python3
"""Extract a deterministic English sample from FineWeb using remote Parquet ranges."""
from __future__ import annotations
import argparse, hashlib, json, re, statistics, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
from pathlib import Path
import unicodedata

DATASET = "HuggingFaceFW/fineweb"
REVISION = "main"
SEED = "langid-32-fineweb2-v1"  # shared hostname split assignment with FineWeb2
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\\s+")
EMAIL = re.compile(r"(?i)\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b")
URL = re.compile(r"(?i)(?:https?://|www\\.)\\S+")
IPV4 = re.compile(r"(?<![\\d.])(?:25[0-5]|2[0-4]\\d|1?\\d?\\d)(?:\\.(?:25[0-5]|2[0-4]\\d|1?\\d?\\d)){3}(?![\\d.])")
LONG_NUMBER = re.compile(r"\\d{9,}")

def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def request_json(url, timeout):
    req=urllib.request.Request(url,headers={"User-Agent":"langid-32 FineWeb extractor/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        return json.loads(response.read().decode()), {k.lower():v for k,v in response.headers.items()}

def next_link(header):
    for part in header.split(","):
        bits=part.split(";")
        if len(bits)>1 and 'rel="next"' in bits[1]:
            target=bits[0].strip()
            if target.startswith("<") and target.endswith(">"): return target[1:-1]
    return None

def list_files(timeout):
    url=f"https://huggingface.co/api/datasets/{DATASET}/tree/{REVISION}/data?recursive=true&expand=false&limit=1000"
    files=[]
    while url:
        payload,headers=request_json(url,timeout)
        if not isinstance(payload,list): raise RuntimeError(f"Unexpected Hub response: {payload!r}")
        files.extend(x for x in payload if isinstance(x,dict) and str(x.get("path","")).endswith(".parquet"))
        url=next_link(headers.get("link",""))
    if not files: raise FileNotFoundError("No FineWeb Parquet files found below data/")
    return sorted(files,key=lambda x:x["path"])

def normalize(text):
    return " ".join(unicodedata.normalize("NFC",text or "").replace("\n"," ").replace("\r"," ").replace("\t"," ").split())

def candidates(text, rejected, min_chars, max_chars):
    seen=set()
    for part in SENTENCE_SPLIT.split(text or ""):
        sentence=normalize(part).lstrip("-–—•*· ").strip()
        if not sentence: continue
        if sentence in seen: rejected["duplicate_within_document"]+=1; continue
        seen.add(sentence)
        if len(sentence)<min_chars: rejected["too_short"]+=1; continue
        if len(sentence)>max_chars: rejected["too_long"]+=1; continue
        if EMAIL.search(sentence): rejected["email"]+=1; continue
        if URL.search(sentence): rejected["url"]+=1; continue
        if IPV4.search(sentence): rejected["ipv4"]+=1; continue
        letters=sum(c.isalpha() for c in sentence)
        if letters<8 or letters/max(1,len(sentence.replace(" ","")))<0.45:
            rejected["low_letter_ratio"]+=1; continue
        if len(re.findall(r"[A-Za-z]+",sentence))<5:
            rejected["too_few_words"]+=1; continue
        if sentence[-1:] not in ".!?": rejected["no_sentence_ending"]+=1; continue
        yield sentence

def fraction(group_id):
    return int.from_bytes(hashlib.sha256(f"{SEED}\\0{group_id}".encode()).digest()[:8],"big")/2**64

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target",type=int,default=20000)
    ap.add_argument("--shards",type=int,default=24)
    ap.add_argument("--row-groups",type=int,default=4)
    ap.add_argument("--min-score",type=float,default=.90)
    ap.add_argument("--min-chars",type=int,default=25)
    ap.add_argument("--max-chars",type=int,default=400)
    ap.add_argument("--timeout",type=int,default=180)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    if min(args.target,args.shards,args.row_groups)<1: ap.error("target, shards and row-groups must be positive")
    import duckdb
    con=duckdb.connect()
    con.execute("INSTALL httpfs"); con.execute("LOAD httpfs")
    con.execute("CALL enable_logging('HTTP', storage='memory')")
    version=con.execute("SELECT version()").fetchone()[0]
    if not version.startswith("v2."): raise SystemExit(f"DuckDB 2.x required, found {version}")
    files=list_files(args.timeout)
    # Deterministically distribute selected shards over the sorted corpus; this avoids
    # concentrating the sample in one crawl dump or a contiguous range of shards.
    n=min(args.shards,len(files))
    start=int(sha(SEED+"\\0fineweb-shards")[:12],16)%len(files)
    indices=sorted({(start+round(i*len(files)/n))%len(files) for i in range(n)})
    pools=defaultdict(list); seen=set(); rejected=Counter(); reports=[]
    docs=0; domains=set(); max_per_doc=20
    for idx in indices:
        item=files[idx]; path=item["path"]
        url=f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{path}"
        escaped=url.replace("'","''")
        con.execute("CALL truncate_duckdb_logs()")
        metadata=con.execute(f"SELECT row_group_id,max(row_group_num_rows) FROM parquet_metadata('{escaped}') GROUP BY row_group_id ORDER BY row_group_id").fetchall()
        if not metadata: raise RuntimeError(f"No row groups in {path}")
        count=len(metadata); base=int(sha(SEED+"\\0"+path)[:12],16)%count
        rgids=sorted({(base+round(i*count/args.row_groups))%count for i in range(min(args.row_groups,count))})
        con.execute("CALL truncate_duckdb_logs()")
        cur=con.execute(f"SELECT text,id,url,date,dump,language,language_score,token_count,file_row_group_number FROM read_parquet('{escaped}') WHERE file_row_group_number IN ({','.join(map(str,rgids))})")
        shard_docs=0; shard_hosts=set()
        for batch in iter(lambda:cur.fetchmany(256),[]):
            for text,id_,source_url,date,dump,language,score,tokens,rgid in batch:
                docs+=1; shard_docs+=1
                if language and str(language).lower()!="en": rejected["language_code_mismatch"]+=1; continue
                if score is None or float(score)<args.min_score: rejected["document_language_score"]+=1; continue
                host=urllib.parse.urlparse(source_url or "").hostname or ""
                host=host.lower().removeprefix("www.").rstrip(".")
                if not host: rejected["missing_hostname"]+=1; continue
                domains.add(host); shard_hosts.add(host)
                group_id=sha("host:"+host)
                split_value=fraction(group_id)
                split="test" if split_value<.10 else "validation" if split_value<.20 else "train"
                doc_hash=sha(str(id_))
                parts=list(candidates(text,rejected,args.min_chars,args.max_chars))
                parts.sort(key=lambda s:sha(SEED+"\\0"+doc_hash+"\\0"+s))
                if len(parts)>max_per_doc: rejected["document_sentence_cap"]+=len(parts)-max_per_doc
                for sentence in parts[:max_per_doc]:
                    if sentence in seen: rejected["duplicate_sentence"]+=1; continue
                    seen.add(sentence)
                    priority=sha(SEED+"\\0en\\0"+split+"\\0"+sentence)
                    record={"text":sentence,"language":"en","source":"fineweb","split":split,"group_id":group_id,"document_id_hash":doc_hash}
                    provenance={"sentence_sha256":sha(sentence),"document_id_sha256":doc_hash,"group_id":group_id,
                      "source_domain":host,"source_url_sha256":sha(source_url or ""),"crawl_date":str(date or ""),
                      "crawl_dump":str(dump or ""),"language_score":float(score),"token_count":int(tokens or 0),
                      "revision":REVISION,"subset":"default","shard":path,"row_group_id":int(rgid),
                      "shard_oid":str(item.get("oid") or ""),"shard_lfs_oid":str((item.get("lfs") or {}).get("oid","")),
                      "privacy_flags":[*(["long_numeric_sequence"] if LONG_NUMBER.search(sentence) else [])]}
                    pools[split].append((priority,record,provenance))
        reports.append({"shard":path,"bytes":int(item.get("size") or 0),"row_group_count":count,
          "selected_row_group_ids":rgids,"documents_read":shard_docs,"distinct_hostnames":len(shard_hosts)})
    con.close()
    targets={"train":args.target-round(args.target*.1)*2,"validation":round(args.target*.1),"test":round(args.target*.1)}
    chosen=[]
    for split,want in targets.items():
        ordered=sorted(pools[split],key=lambda x:x[0])
        if len(ordered)<want: raise SystemExit(f"English {split} shortfall: {len(ordered)} candidates for {want}; increase --shards/--row-groups")
        chosen.extend((split,*x[1:]) for x in ordered[:want])
    args.output_dir.mkdir(parents=True,exist_ok=True)
    hashes={}
    for split in targets:
        path=args.output_dir/f"{split}.jsonl"
        with path.open("w",encoding="utf-8",newline="\n") as f:
            for _,row,_ in chosen:
                if row["split"]==split: f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
        hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    pp=args.output_dir/"provenance.jsonl"
    with pp.open("w",encoding="utf-8",newline="\\n") as f:
        for _,_,prov in chosen: f.write(json.dumps(prov,ensure_ascii=False,separators=(",",":"))+"\\n")
    hashes[pp.name]=hashlib.sha256(pp.read_bytes()).hexdigest()
    manifest={"schema_version":1,"extractor_version":"0.1.0","project":"langid-32","source":DATASET,
      "source_revision":REVISION,"source_dataset_licence":"ODC-By-1.0 (dataset/compilation; underlying Common Crawl page rights remain separate)",
      "target_per_language":args.target,"split_fractions":{"train":.8,"validation":.1,"test":.1},
      "selection":{"seed":SEED,"selected_shards":len(indices),"row_groups_per_shard":args.row_groups,
        "min_chars":args.min_chars,"max_chars":args.max_chars,"min_language_score":args.min_score,
        "max_sentences_per_document":max_per_doc,"grouping":"hostname hash; split assignment shared with FineWeb2",
        "deduplication":"exact normalized sentence within sampled FineWeb rows",
        "privacy_exclusions":["email","URL","IPv4"],"privacy_review_flags":["9+ digit sequence"]},
      "duckdb_version":version,"documents_read":docs,"distinct_hostnames":len(domains),
      "selected_shards":reports,"candidate_counts_by_split":{k:len(v) for k,v in pools.items()},
      "selected_counts_by_split":targets,"rejected":dict(rejected),"output_sha256":hashes,
      "privacy_note":"Email, URL and IPv4 patterns are excluded. Long numeric sequences are retained with review flags. Regex filtering is not complete PII clearance.",
      "limitation":"Deterministic bounded sample of selected Parquet row groups; not statistically representative of all FineWeb documents."}
    (args.output_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print(json.dumps({"documents_read":docs,"distinct_hostnames":len(domains),"candidate_counts_by_split":{k:len(v) for k,v in pools.items()},
      "selected_counts_by_split":targets,"shards":len(indices),"manifest":"manifest.json"},indent=2))

if __name__=="__main__": main()
