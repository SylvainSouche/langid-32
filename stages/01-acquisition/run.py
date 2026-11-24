#!/usr/bin/env python3
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--target",required=True);p.add_argument("--root",default=".");a=p.parse_args();r=Path(a.root)
commands={
"common-voice":[sys.executable,"scripts/download_common_voice_hf.py","--output-dir",str(r/"input/common-voice/source")],
"catalan":[sys.executable,"scripts/acquire_waiting_sources.py","--source","catalan","--out",str(r/"input/waiting/catalan")],
"icelandic":[sys.executable,"scripts/acquire_waiting_sources.py","--source","icelandic","--out",str(r/"input/waiting/icelandic")],
"norwegian":[sys.executable,"scripts/acquire_waiting_sources.py","--source","norwegian","--out",str(r/"input/waiting/norwegian")],
"korean":[sys.executable,"scripts/acquire_waiting_sources.py","--source","korean","--out",str(r/"input/waiting/korean")],
"fineweb2":[sys.executable,"scripts/acquire_waiting_sources.py","--source","fineweb2","--out",str(r/"input/waiting/fineweb2")],
"arabic":[sys.executable,"scripts/acquire_waiting_sources.py","--source","arabic","--out",str(r/"input/waiting/arabic")],
"gaois":[sys.executable,"scripts/acquire_gaois_irish_legislation.py","--out",str(r/"input/waiting/irish/candidates.jsonl"),"--max-sample","50000"]}
if a.target=="common-voice":
 subprocess.run(commands[a.target],check=True)
 subprocess.run([sys.executable,"scripts/curate_common_voice_hf.py","--input-root",str(r/"input/common-voice/source"),"--output",str(r/"input/common-voice"),"--per-language-cap","9000"],check=True)
elif a.target in commands: subprocess.run(commands[a.target],check=True)
else: raise SystemExit("Historical snapshots are fetched by the workflow's historical job; target is not executable locally.")
