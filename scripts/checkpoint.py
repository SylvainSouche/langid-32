#!/usr/bin/env python3
"""AES-256-GCM authenticated encryption for stage checkpoints."""
import argparse,hashlib,io,os,secrets,tarfile
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
MAGIC=b"L32CP01"
def getkey():
 s=os.environ.get("LANGID32_CHECKPOINT_KEY","")
 if len(s)<32: raise SystemExit("LANGID32_CHECKPOINT_KEY must be configured (>=32 characters)")
 return hashlib.sha256(s.encode()).digest()
p=argparse.ArgumentParser();p.add_argument("mode",choices=["pack","unpack"]);p.add_argument("--root",default=".");p.add_argument("--archive",required=True);a=p.parse_args();root=Path(a.root);archive=Path(a.archive)
if a.mode=="pack":
 b=io.BytesIO()
 with tarfile.open(fileobj=b,mode="w:gz") as t:
  for n in ("input","out"):
   q=root/n
   if q.exists():t.add(q,arcname=n)
 nonce=secrets.token_bytes(12);archive.write_bytes(MAGIC+nonce+AESGCM(getkey()).encrypt(nonce,b.getvalue(),MAGIC))
else:
 raw=archive.read_bytes()
 if not raw.startswith(MAGIC):raise SystemExit("Invalid checkpoint envelope")
 nonce=raw[len(MAGIC):len(MAGIC)+12];plain=AESGCM(getkey()).decrypt(nonce,raw[len(MAGIC)+12:],MAGIC)
 with tarfile.open(fileobj=io.BytesIO(plain),mode="r:gz") as t:
  for m in t.getmembers():
   q=(root/m.name).resolve()
   if root.resolve() not in q.parents:raise SystemExit("Unsafe checkpoint path")
  t.extractall(root,filter="data")
