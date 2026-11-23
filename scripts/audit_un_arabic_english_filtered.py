#!/usr/bin/env python3
"""Full shard audit of the UN-Arabic-English-Filtered HF derivative dataset."""
from __future__ import annotations
import collections, hashlib, json, os, sqlite3, tempfile, time
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
CHUNK=4*1024*1024

def download_resumable(session, url, path):
    """Download with HTTP Range resume; retain partial bytes across transient disconnects."""
    head=session.head(url,allow_redirects=True,timeout=(60,180),
                      headers={"User-Agent":"langid-32-source-audit/1","Accept-Encoding":"identity"})
    head.raise_for_status()
    expected=int(head.headers.get("Content-Length","0") or 0)
    attempts=0
    while True:
        offset=path.stat().st_size if path.exists() else 0
        if expected and offset==expected:
            break
        attempts+=1
        if attempts>12:
            raise RuntimeError(f"Download did not complete after 12 attempts: {path.name} ({offset}/{expected} bytes)")
        headers={"User-Agent":"langid-32-source-audit/1","Accept-Encoding":"identity"}
        if offset:
            headers["Range"]=f"bytes={offset}-"
        try:
            with session.get(url,stream=True,timeout=(60,300),headers=headers) as r:
                if offset and r.status_code==200:
                    offset=0
                elif offset and r.status_code==206:
                    cr=r.headers.get("Content-Range","")
                    if not cr.startswith(f"bytes {offset}-"):
                        raise RuntimeError(f"Unexpected Content-Range {cr!r} for offset {offset}")
                else:
                    r.raise_for_status()
                    if r.status_code not in (200,206):
                        raise RuntimeError(f"Unexpected HTTP status {r.status_code}")
                mode="ab" if offset and r.status_code==206 else "wb"
                with path.open(mode) as out:
                    for block in r.iter_content(CHUNK):
                        if block:
                            out.write(block)
            current=path.stat().st_size
            if expected and current!=expected:
                raise IOError(f"Short download: {current}/{expected} bytes")
        except (requests.exceptions.RequestException, IOError) as exc:
            current=path.stat().st_size if path.exists() else 0
            print(f"Transient download error {attempts}/12 for {path.name}: {exc}; retained {current} bytes",flush=True)
            if attempts>=12:
                raise
            time.sleep(min(30,2**min(attempts,5)))
    h=hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda:src.read(CHUNK),b""):
            h.update(block)
    return path.stat().st_size,h.hexdigest()


def digest(s):
    return hashlib.sha256((s or "").encode("utf-8")).digest()

def main():
    fd,dbname=tempfile.mkstemp(prefix="unfiltered-",suffix=".sqlite"); os.close(fd)
    db=sqlite3.connect(dbname); db.execute("PRAGMA journal_mode=OFF"); db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE ar (h BLOB PRIMARY KEY) WITHOUT ROWID")
    db.execute("CREATE TABLE pairs (h BLOB PRIMARY KEY) WITHOUT ROWID")
    session=requests.Session()
    api=session.get("https://huggingface.co/api/datasets/ymoslem/UN-Arabic-English-Filtered/revision/main",
                    timeout=(60,180),headers={"User-Agent":"langid-32-source-audit/1"})
    api.raise_for_status()
    revision=api.json()["sha"]
    base=f"https://huggingface.co/datasets/ymoslem/UN-Arabic-English-Filtered/resolve/{revision}/"
    report={"dataset":"ymoslem/UN-Arabic-English-Filtered","revision":revision,
            "license_declared":"CC BY 4.0","source_claim":"MultiUN + UN Parallel Corpus v1.0",
            "splits":{}}
    try:
        for split,files in SHARDS.items():
            totals=collections.Counter(); shard_reports=[]
            for filename in files:
                fd,name=tempfile.mkstemp(prefix="un-bitext-",suffix=".parquet"); os.close(fd)
                path=Path(name)
                try:
                    size,sha256=download_resumable(session,base+filename,path)
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
                    shard_reports.append({"file":filename,"bytes":size,"sha256":sha256,
                                          "parquet_rows":pf.metadata.num_rows,"measured":dict(local)})
                    totals.update(local)
                finally:
                    path.unlink(missing_ok=True)
            report["splits"][split]={"shards":shard_reports,"totals":dict(totals)}
        report["distinct_arabic_texts_across_all_splits"]=db.execute("SELECT COUNT(*) FROM ar").fetchone()[0]
        report["distinct_pairs_across_all_splits"]=db.execute("SELECT COUNT(*) FROM pairs").fetchone()[0]
        report["method"]="Resolved and recorded the current HF dataset commit SHA, downloaded every Parquet shard from that immutable revision with resumable HTTP Range requests, streamed all rows, measured Arabic/English characters and whitespace tokens, and deduplicated Arabic strings and aligned pairs by SHA-256."
        report["provenance_warning"]="The dataset schema contains only text_en and text_ar; it carries no source document IDs, URLs, dates or per-row source labels. Its card cites MultiUN and UNPC and declares CC BY 4.0, but the original UN source-document mapping is not recoverable from these fields. Keep the derivative attribution and UN acknowledgement/citation; do not call row indices UN document IDs."
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        db.close(); Path(dbname).unlink(missing_ok=True)

if __name__=="__main__": main()
