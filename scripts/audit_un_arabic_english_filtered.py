#!/usr/bin/env python3
"""Full shard audit of the UN-Arabic-English-Filtered HF derivative dataset."""
from __future__ import annotations
import collections, hashlib, json, os, sqlite3, tempfile, unicodedata
from pathlib import Path
import requests
import pyarrow.parquet as pq

BASE="https://huggingface.co/datasets/ymoslem/UN-Arabic-English-Filtered/resolve/main/"
SHARDS={
 "train":[f"data/train-{i:05d}-of-00019.parquet" for i in range(19)],
 "dev":["data/dev-00000-of-00001.parquet"],
 "test":["data/test-00000-of-00001.parquet"],
}
OUT=Path("reports/un-arabic-english-filtered-full-audit.json")
CHUNK=1024*1024

def digest(s):
    return hashlib.sha256((s or "").encode("utf-8")).digest()

def main():
    fd,dbname=tempfile.mkstemp(prefix="unfiltered-",suffix=".sqlite"); os.close(fd)
    db=sqlite3.connect(dbname); db.execute("PRAGMA journal_mode=OFF"); db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE ar (h BLOB PRIMARY KEY) WITHOUT ROWID")
    db.execute("CREATE TABLE pairs (h BLOB PRIMARY KEY) WITHOUT ROWID")
    report={"dataset":"ymoslem/UN-Arabic-English-Filtered","revision":"main",
            "license_declared":"CC BY 4.0","source_claim":"MultiUN + UN Parallel Corpus v1.0",
            "splits":{}}
    session=requests.Session()
    try:
        for split,files in SHARDS.items():
            totals=collections.Counter(); shard_reports=[]
            for filename in files:
                fd,name=tempfile.mkstemp(prefix="un-bitext-",suffix=".parquet"); os.close(fd)
                path=Path(name); h=hashlib.sha256(); size=0
                try:
                    with session.get(BASE+filename,stream=True,timeout=(60,300),
                                     headers={"User-Agent":"langid-32-source-audit/1"}) as r:
                        r.raise_for_status()
                        with path.open("wb") as out:
                            for b in r.iter_content(CHUNK):
                                if b: out.write(b); h.update(b); size+=len(b)
                    pf=pq.ParquetFile(path); local=collections.Counter()
                    for batch in pf.iter_batches(batch_size=8192,columns=["text_en","text_ar"]):
                        cols=batch.to_pydict()
                        for en,ar in zip(cols["text_en"],cols["text_ar"]):
                            en=en or ""; ar=ar or ""
                            local["rows"]+=1
                            local["ar_characters"]+=len(ar); local["en_characters"]+=len(en)
                            local["ar_whitespace_tokens"]+=len(ar.split())
                            local["en_whitespace_tokens"]+=len(en.split())
                            local["empty_ar"]+=not bool(ar.strip()); local["empty_en"]+=not bool(en.strip())
                            if ar.strip():
                                cur=db.execute("INSERT OR IGNORE INTO ar VALUES (?)",(digest(ar),))
                                local["new_unique_arabic_texts"]+=cur.rowcount
                            if ar.strip() and en.strip():
                                cur=db.execute("INSERT OR IGNORE INTO pairs VALUES (?)",(digest(ar+"\x00"+en),))
                                local["new_unique_pairs"]+=cur.rowcount
                    db.commit()
                    shard_reports.append({"file":filename,"bytes":size,"sha256":h.hexdigest(),
                                          "parquet_rows":pf.metadata.num_rows,"measured":dict(local)})
                    totals.update(local)
                finally:
                    path.unlink(missing_ok=True)
            report["splits"][split]={"shards":shard_reports,"totals":dict(totals)}
        report["distinct_arabic_texts_across_all_splits"]=db.execute("SELECT COUNT(*) FROM ar").fetchone()[0]
        report["distinct_pairs_across_all_splits"]=db.execute("SELECT COUNT(*) FROM pairs").fetchone()[0]
        report["method"]="Downloaded every Parquet shard from the pinned HF repository main revision, streamed all rows, measured Arabic/English characters and whitespace tokens, and deduplicated Arabic strings and aligned pairs by SHA-256."
        report["provenance_warning"]="The dataset schema contains only text_en and text_ar; it carries no source document IDs, URLs, dates or per-row source labels. Its card cites MultiUN and UNPC and declares CC BY 4.0, but the original UN source-document mapping is not recoverable from these fields. Keep the derivative attribution and UN acknowledgement/citation; do not call row indices UN document IDs."
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        db.close(); Path(dbname).unlink(missing_ok=True)

if __name__=="__main__": main()
