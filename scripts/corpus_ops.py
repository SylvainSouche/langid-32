#!/usr/bin/env python3
"""Deterministic JSONL corpus filtering, pattern-based redaction and QA reports."""
from __future__ import annotations
import argparse, collections, hashlib, json, re, statistics
from pathlib import Path

EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
PHONE = re.compile(r"(?<!\w)(?:\+\d[\d .()/-]{7,}\d)(?!\w)")
PATTERNS = (("email", EMAIL), ("url", URL), ("ipv4", IPV4), ("phone", PHONE))

def read_rows(path: Path):
    with path.open(encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                try: yield n, json.loads(line)
                except json.JSONDecodeError as e: raise ValueError(f"{path}:{n}: {e}") from e

def write_row(f, row):
    f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

def text_key(text: str) -> str:
    normalized = " ".join(text.casefold().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def cmd_filter(a):
    src, dst = Path(a.input), Path(a.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    counts = collections.Counter()
    lengths = []
    with dst.open("w", encoding="utf-8") as out:
        for _, row in read_rows(src):
            counts["input"] += 1
            text = row.get("text")
            if not isinstance(text, str) or not text.strip():
                counts["empty"] += 1; continue
            text = " ".join(text.split())
            if len(text) < a.min_chars:
                counts["too_short"] += 1; continue
            if a.max_chars and len(text) > a.max_chars:
                counts["too_long"] += 1; continue
            source = str(row.get("source", "")).lower()
            if "news" in source and any(ch.isdecimal() for ch in text):
                counts["news_decimal_digit"] += 1; continue
            lang = str(row.get("language", ""))
            key = (lang, text_key(text))
            if key in seen:
                counts["duplicate_within_language_kept"] += 1
            seen.add(key)
            row["text"] = text
            write_row(out, row)
            counts["kept"] += 1
            lengths.append(len(text))
    report = {"operation":"filter","input":str(src),"output":str(dst),
              "policy":{"min_chars":a.min_chars,"max_chars":a.max_chars or None,
                        "news_decimal_digit_filter":True,"deduplicate_within_language":True},
              "counts":dict(counts),
              "text_length":{"min":min(lengths) if lengths else None,
                             "median":statistics.median(lengths) if lengths else None,
                             "max":max(lengths) if lengths else None}}
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

def cmd_anonymize(a):
    src, dst = Path(a.input), Path(a.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    counts = collections.Counter()
    with dst.open("w", encoding="utf-8") as out:
        for _, row in read_rows(src):
            counts["rows"] += 1
            text = row.get("text", "")
            if not isinstance(text, str): text = str(text)
            total = 0
            for name, pattern in PATTERNS:
                text, n = pattern.subn("[REDACTED_"+name.upper()+"]", text)
                counts[name] += n
                total += n
            row["text"] = text
            if total:
                row["anonymization"] = {"method":"regex_pattern_redaction_v1",
                                        "redaction_count":total,
                                        "scope":"email,url,ipv4,phone"}
            write_row(out, row)
    report = {"operation":"anonymize","input":str(src),"output":str(dst),
              "counts":dict(counts),
              "warning":"Pattern-based redaction only. It does not identify personal names, addresses, indirect identifiers or all phone/email formats; do not describe this as complete anonymization."}
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

def cmd_count(a):
    langs=collections.Counter();sources=collections.Counter();families=collections.Counter()
    lengths=[];rows=0
    for _,row in read_rows(Path(a.input)):
        rows+=1;lang=str(row.get("language","unknown"));src=str(row.get("source","unknown"))
        langs[lang]+=1;sources[src]+=1
        families[src.removeprefix("leipzig_")]+=1
        lengths.append(len(str(row.get("text",""))))
    result={"rows":rows,"languages":dict(sorted(langs.items())),
            "sources":dict(sorted(sources.items())),"families":dict(sorted(families.items())),
            "text_length":{"min":min(lengths) if lengths else None,
                           "median":statistics.median(lengths) if lengths else None,
                           "max":max(lengths) if lengths else None}}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

def cmd_assess(a):
    counts=collections.Counter();per=collections.defaultdict(collections.Counter)
    groups=collections.Counter();missing_prov=collections.Counter()
    exact=collections.Counter();lengths=collections.defaultdict(list)
    digit_news=0;redaction_residuals=collections.Counter()
    for _,row in read_rows(Path(a.input)):
        counts["rows"]+=1
        lang=str(row.get("language","unknown"));source=str(row.get("source","unknown"))
        per[lang]["rows"]+=1;per[lang][source]+=1
        txt=str(row.get("text",""));lengths[lang].append(len(txt))
        exact[(lang,text_key(txt))]+=1
        if "news" in source and any(c.isdecimal() for c in txt):digit_news+=1
        prov=row.get("provenance") or {}
        for field in ("data_id","sentence_id","archive_sha256"):
            if not prov.get(field):missing_prov[field]+=1
        if row.get("group_id"):groups[(lang,str(row["group_id"]))]+=1
        for name,pattern in PATTERNS:
            if pattern.search(txt):redaction_residuals[name]+=1
    dup=sum(n-1 for n in exact.values() if n>1)
    language_report={}
    for lang,c in sorted(per.items()):
        vals=lengths[lang]
        language_report[lang]={**dict(c),"min_chars":min(vals),"median_chars":statistics.median(vals),
                               "max_chars":max(vals),"below_minimum":c["rows"]<a.minimum_per_language,
                               "below_target":c["rows"]<a.target_per_language}
    result={"operation":"assessment","input":a.input,"total_rows":counts["rows"],
            "language_count":len(per),"languages":language_report,
            "duplicate_rows_within_language":dup,"news_rows_still_containing_decimal_digits":digit_news,
            "missing_provenance_fields":dict(missing_prov),
            "remaining_pattern_matches_after_redaction":dict(redaction_residuals),
            "source_group_count":len(groups),
            "thresholds":{"minimum_per_language":a.minimum_per_language,"target_per_language":a.target_per_language},
            "note":"Assessment reports issues and coverage; it does not silently remove or down-rank rows."}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True)
    f=sub.add_parser("filter");f.add_argument("--input",required=True);f.add_argument("--output",required=True);f.add_argument("--report",default="out/reports/filter.json");f.add_argument("--min-chars",type=int,default=20);f.add_argument("--max-chars",type=int,default=1000);f.set_defaults(func=cmd_filter)
    z=sub.add_parser("anonymize");z.add_argument("--input",required=True);z.add_argument("--output",required=True);z.add_argument("--report",default="out/reports/anonymize.json");z.set_defaults(func=cmd_anonymize)
    c=sub.add_parser("count");c.add_argument("--input",required=True);c.add_argument("--output",default="out/reports/counts.json");c.set_defaults(func=cmd_count)
    q=sub.add_parser("assess");q.add_argument("--input",required=True);q.add_argument("--output",default="out/reports/assessment.json");q.add_argument("--minimum-per-language",type=int,default=20000);q.add_argument("--target-per-language",type=int,default=30000);q.set_defaults(func=cmd_assess)
    a=p.parse_args();a.func(a)
if __name__=="__main__":main()
