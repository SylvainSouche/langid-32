#!/usr/bin/env python3
"""Fetch only Common Voice 22 validated sentence TSVs from the Hugging Face text tree.

No audio, clips, speaker IDs, demographic metadata, or full dataset archive is fetched.
"""
from __future__ import annotations
import argparse, hashlib, json, os, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "fsicoli/common_voice_22_0"
BASE = f"https://huggingface.co/datasets/{REPO}/resolve"
# One or more upstream locale directories per langid-32 class.
LOCALES = {
    "bg": ["bg"], "hr": ["hr"], "is": ["is"], "cs": ["cs"], "da": ["da"], "nl": ["nl"],
    "en": ["en"], "et": ["et"], "fi": ["fi"], "fr": ["fr"], "de": ["de"],
    "el": ["el"], "hu": ["hu"], "ga": ["ga-IE"], "it": ["it"], "lv": ["lv"],
    "lt": ["lt"], "mt": ["mt"], "pl": ["pl"], "pt": ["pt"], "ro": ["ro"],
    "sk": ["sk"], "sl": ["sl"], "es": ["es"], "sv": ["sv-SE"],
    "nb": ["nb-NO"], "nn": ["nn-NO"], "ru": ["ru"], "ja": ["ja"],
    "zh": ["zh-CN", "zh-TW"], "ko": ["ko"], "ar": ["ar"], "tr": ["tr"],
}
def now():
    return datetime.now(timezone.utc).isoformat()
def fetch(locale, revision, destination, attempts=3):
    url = f"{BASE}/{revision}/transcript/{locale}/validated_sentences.tsv"
    last = None
    for attempt in range(1, attempts + 1):
        part = destination.with_suffix(destination.suffix + ".part")
        part.unlink(missing_ok=True)
        digest, size = hashlib.sha256(), 0
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"langid-32/0.4","Accept":"text/tab-separated-values"})
            with urllib.request.urlopen(req, timeout=90) as response, part.open("wb") as out:
                resolved_url = response.geturl()
                headers = dict(response.headers.items())
                while True:
                    block = response.read(1024 * 1024)
                    if not block: break
                    out.write(block); digest.update(block); size += len(block)
                out.flush(); os.fsync(out.fileno())
            if size < 64:
                raise RuntimeError(f"Unexpectedly small TSV ({size} bytes)")
            part.replace(destination)
            return {"locale":locale,"url":url,"resolved_url":resolved_url,
                    "repo_commit":headers.get("X-Repo-Commit"),
                    "etag":headers.get("ETag"),"bytes":size,
                    "sha256":digest.hexdigest(),"downloaded_at_utc":now()}
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}: {exc.reason}"
            if exc.code in (404, 410): break
            retry = exc.headers.get("Retry-After")
            delay = min(int(retry), 120) if retry and retry.isdigit() else 5 * attempt
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            delay = 5 * attempt
        finally:
            part.unlink(missing_ok=True)
        if attempt < attempts:
            print(f"Retry {attempt}/{attempts-1} for {locale} after {last}", flush=True)
            time.sleep(delay)
    raise RuntimeError(last or "download failed")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--revision",default="main")
    p.add_argument("--languages",default=",".join(LOCALES))
    a=p.parse_args()
    wanted=[x.strip() for x in a.languages.split(",") if x.strip()]
    unknown=sorted(set(wanted)-set(LOCALES))
    if unknown: p.error("Unknown target language(s): "+", ".join(unknown))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    manifest_path=a.output_dir/"hf-common-voice-download-manifest.json"
    manifest={"source":REPO,"release":"Common Voice Corpus 22.0 (unofficial HF conversion)",
              "revision_requested":a.revision,"method":"direct HTTP fetch of transcript/<locale>/validated_sentences.tsv only; no audio",
              "results":[],"failures":[],"started_at_utc":now()}
    for language in wanted:
        pieces=[]
        for locale in LOCALES[language]:
            dest=a.output_dir/language/f"{locale}.validated_sentences.tsv"
            dest.parent.mkdir(parents=True,exist_ok=True)
            try:
                row=fetch(locale,a.revision,dest)
                row["language"]=language
                pieces.append(row); manifest["results"].append(row)
                print(f"Fetched {language}/{locale}: {row['bytes']:,} bytes sha256={row['sha256']} commit={row['repo_commit']}",flush=True)
            except Exception as exc:
                failure={"language":language,"locale":locale,"error":str(exc),"failed_at_utc":now()}
                manifest["failures"].append(failure)
                print(f"FAILED {language}/{locale}: {exc}",flush=True)
        # Build the curator's canonical input, combining both Chinese locales.
        if pieces:
            import csv, io
            combined=a.output_dir/language/"validated_sentences.tsv"
            with combined.open("wb") as out:
                for i,row in enumerate(pieces):
                    with (a.output_dir/language/f"{row['locale']}.validated_sentences.tsv").open("rb") as src:
                        header=src.readline()
                        if i==0: out.write(header)
                        for line in src:
                            if line.strip(): out.write(line)
            manifest.setdefault("combined",{})[language]={"locales":[x["locale"] for x in pieces],
                "bytes":combined.stat().st_size,"sha256":hashlib.sha256(combined.read_bytes()).hexdigest()}
    manifest["finished_at_utc"]=now()
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    print(f"Success locales: {len(manifest['results'])}; failed locales: {len(manifest['failures'])}")
    return 1 if manifest["failures"] else 0
if __name__=="__main__":
    raise SystemExit(main())
