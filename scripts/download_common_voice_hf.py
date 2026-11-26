#!/usr/bin/env python3
"""Fetch only Common Voice 22 validated sentence TSVs from the Hugging Face text tree.

No audio, clips, speaker IDs, demographic metadata, or full dataset archive is fetched.
"""
from __future__ import annotations
import argparse,os, csv, hashlib, json, os, re, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config

REPO = "fsicoli/common_voice_22_0"
BASE = f"https://huggingface.co/datasets/{REPO}/resolve"
# One or more upstream locale directories per langid-32 class.
LOCALES = {
    "bg": ["bg"], "is": ["is"], "ca": ["ca"], "cs": ["cs"], "da": ["da"], "nl": ["nl"],
    "en": ["en"], "et": ["et"], "fi": ["fi"], "fr": ["fr"], "de": ["de"],
    "el": ["el"], "hu": ["hu"], "ga": ["ga-IE"], "it": ["it"], "lv": ["lv"],
    "lt": ["lt"], "mt": ["mt"], "pl": ["pl"], "pt": ["pt"], "ro": ["ro"],
    "sk": ["sk"], "sl": ["sl"], "es": ["es"], "sv": ["sv-SE"],
    "nb": ["nb-NO"], "nn": ["nn-NO"], "ru": ["ru"], "ja": ["ja"],
    "zh": ["zh-CN", "zh-TW"], "ko": ["ko"], "ar": ["ar"], "tr": ["tr"],
}
def now():
    return datetime.now(timezone.utc).isoformat()
def digest_file(path):
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()
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
                    "repo_commit":headers.get("X-Repo-Commit") or revision,
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
    p.add_argument("--languages",default=None)
    p.add_argument("--config",type=Path,default=Path(os.environ.get("LANGID32_CONFIG", ROOT / "config/langid32.toml")))
    a=p.parse_args()
    cfg = load_config(a.config)
    project_languages = set(cfg["project"]["languages"])
    requested = a.languages if a.languages is not None else ",".join(sorted(project_languages))
    wanted=[x.strip() for x in requested.split(",") if x.strip()]
    unknown=sorted(set(wanted)-project_languages)
    if unknown: p.error("Unknown project target language(s): "+", ".join(unknown))
    unavailable=sorted(set(wanted)-set(LOCALES))
    wanted=[language for language in wanted if language in LOCALES]
    a.output_dir.mkdir(parents=True,exist_ok=True)
    api_url = f"https://huggingface.co/api/datasets/{REPO}"
    request = urllib.request.Request(api_url, headers={"User-Agent": "langid-32/0.4"})
    with urllib.request.urlopen(request, timeout=60) as response:
        repo_info = json.load(response)
    resolved_revision = repo_info.get("sha")
    if not resolved_revision or not re.fullmatch(r"[0-9a-f]{40}", resolved_revision):
        raise RuntimeError(f"Could not resolve immutable revision for {REPO}@{a.revision}")
    manifest_path=a.output_dir/"hf-common-voice-download-manifest.json"
    previous={}
    if manifest_path.is_file():
        try:
            candidate=json.loads(manifest_path.read_text(encoding="utf-8"))
            if candidate.get("revision_resolved")==resolved_revision:
                previous=candidate
        except (OSError, ValueError):
            previous={}
    previous_results={row["locale"]:row for row in previous.get("results",[]) if row.get("locale")}
    manifest={"source":REPO,"dataset_url":f"https://huggingface.co/datasets/{REPO}","source_license_claim":"CC0-1.0","release":"Common Voice Corpus 22.0 (unofficial HF conversion)",
              "revision_requested":a.revision,"revision_resolved":resolved_revision,"method":"direct HTTP fetch of transcript/<locale>/validated_sentences.tsv only; no audio",
              "results":[],"failures":[],"unavailable_languages":[{"language":language,"reason":"No Common Voice 22 locale directory in the HF conversion"} for language in unavailable],"started_at_utc":now()}
    for language in wanted:
        pieces=[]
        for locale in LOCALES[language]:
            dest=a.output_dir/language/f"{locale}.validated_sentences.tsv"
            dest.parent.mkdir(parents=True,exist_ok=True)
            try:
                row=previous_results.get(locale)
                if row and dest.is_file():
                    digest=digest_file(dest)
                    if dest.stat().st_size != row.get("bytes") or digest != row.get("sha256"):
                        row=None
                else:
                    row=None
                if row is None:
                    row=fetch(locale,resolved_revision,dest)
                    row["language"]=language
                    print(f"Fetched {language}/{locale}: {row['bytes']:,} bytes sha256={row['sha256']} commit={row['repo_commit']}",flush=True)
                else:
                    print(f"Reused verified {language}/{locale}: {row['bytes']:,} bytes sha256={row['sha256']}",flush=True)
                pieces.append(row); manifest["results"].append(row)
            except Exception as exc:
                failure={"language":language,"locale":locale,"error":str(exc),"failed_at_utc":now()}
                manifest["failures"].append(failure)
                print(f"FAILED {language}/{locale}: {exc}",flush=True)
        # Build the curator's canonical input, combining both Chinese locales.
        if pieces:
            combined=a.output_dir/language/"validated_sentences.tsv"
            with combined.open("w",encoding="utf-8",newline="") as out:
                writer=None
                for piece in pieces:
                    source=a.output_dir/language/f"{piece['locale']}.validated_sentences.tsv"
                    with source.open(encoding="utf-8-sig",newline="") as inp:
                        reader=csv.DictReader(inp,delimiter="\t")
                        if not reader.fieldnames or not {"sentence_id","sentence"}.issubset(reader.fieldnames):
                            raise RuntimeError(f"Unexpected Common Voice TSV schema: {source}")
                        if writer is None:
                            fields=list(reader.fieldnames)+["source_locale"]
                            writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n")
                            writer.writeheader()
                        for record in reader:
                            writer.writerow({**record,"source_locale":piece["locale"]})
            manifest.setdefault("combined",{})[language]={"locales":[x["locale"] for x in pieces],
                "repo_commit":resolved_revision,"bytes":combined.stat().st_size,
                "sha256":hashlib.sha256(combined.read_bytes()).hexdigest()}
    manifest["finished_at_utc"]=now()
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    print(f"Success locales: {len(manifest['results'])}; failed locales: {len(manifest['failures'])}")
    return 1 if manifest["failures"] else 0
if __name__=="__main__":
    raise SystemExit(main())
