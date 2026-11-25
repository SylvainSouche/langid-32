#!/usr/bin/env python3
"""Full archive audit of the official UN Arabic-English v1.0 plain-text bitext."""
from __future__ import annotations
import collections, hashlib, json, os, tempfile, tarfile
from pathlib import Path
import requests

BASE = "https://conferences.unite.un.org/UNCORPUS/en/DownloadFile?filename="
PARTS = ["UNv1.0.ar-en.tar.gz.00", "UNv1.0.ar-en.tar.gz.01"]
OUT = Path("reports/un-parallel-corpus-ar-en-audit.json")
CHUNK = 1024 * 1024

def main():
    fd, name = tempfile.mkstemp(prefix="un-ar-en-", suffix=".tar.gz")
    os.close(fd)
    archive_path = Path(name)
    archive_hash = hashlib.sha256()
    archive_size = 0
    part_info = []
    try:
        with archive_path.open("wb") as out:
            for part in PARTS:
                h = hashlib.sha256()
                size = 0
                with requests.get(BASE + part, stream=True, timeout=(60, 240),
                                  headers={"User-Agent":"Mozilla/5.0 langid-32-source-audit/1","Referer":"https://www.un.org/dgacm/content/uncorpus/Download","Accept":"application/octet-stream,*/*"}) as r:
                    r.raise_for_status()
                    first = True
                    for block in r.iter_content(CHUNK):
                        if block:
                            if first:
                                first = False
                                if not block.startswith(bytes([31, 139])):
                                    raise RuntimeError(f"Expected gzip bytes for {part}; HTTP {r.status_code}; final URL {r.url}; content-type {r.headers.get('Content-Type')}; first bytes {block[:240]!r}")
                            out.write(block); h.update(block); archive_hash.update(block)
                            size += len(block); archive_size += len(block)
                part_info.append({"name":part,"bytes":size,"sha256":h.hexdigest()})
        members=[]
        totals=collections.Counter()
        with tarfile.open(archive_path, "r:gz") as tf:
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                f=tf.extractfile(m)
                if f is None:
                    continue
                h=hashlib.sha256(); lines=nonempty=chars=bytes_n=0
                first=None; last=None
                for raw in f:
                    h.update(raw); lines += 1; bytes_n += len(raw)
                    if raw.strip():
                        nonempty += 1
                        try: text=raw.decode("utf-8").rstrip("\r\n")
                        except UnicodeDecodeError: totals["invalid_utf8_lines"] += 1; continue
                        chars += len(text)
                        if first is None: first=text[:160]
                        last=text[:160]
                members.append({"member":m.name,"bytes":m.size,"sha256":h.hexdigest(),
                                "lines":lines,"nonempty_lines":nonempty,"text_characters":chars,
                                "first_nonempty_preview":first,"last_nonempty_preview":last})
                totals["members"] += 1; totals["lines"] += lines
                totals["nonempty_lines"] += nonempty; totals["text_characters"] += chars
                totals["uncompressed_bytes"] += m.size
        OUT.parent.mkdir(parents=True,exist_ok=True)
        report={
          "dataset":"United Nations Parallel Corpus v1.0 Arabic-English plain-text bitext",
          "source":"United Nations DGACM UNCorpus",
          "source_url":"https://www.un.org/dgacm/content/uncorpus/Download",
          "download_base":BASE,"parts":part_info,"archive_bytes":archive_size,
          "archive_sha256":archive_hash.hexdigest(),"members":members,
          "totals":dict(totals),
          "rights":"UN official records and other parliamentary documents stated by UN to be in the public domain; mandatory acknowledgement of the United Nations; retain corpus citation and disclaimer.",
          "method":"Downloaded both official split archive parts, concatenated and fully scanned every regular tar member line-by-line. This is an archive/member count, not a count of unique sentences or distinct documents.",
          "warning":"The source is bilingual aligned material. Arabic text is eligible as a candidate source, but only Arabic member(s) should enter Arabic LID staging; do not count English lines as Arabic. Keep source IDs and attribution."
        }
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        archive_path.unlink(missing_ok=True)

if __name__=="__main__": main()
