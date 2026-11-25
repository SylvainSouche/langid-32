#!/usr/bin/env python3
"""Summarize non-filtering JQL annotations by language and source."""
from __future__ import annotations
import argparse, collections, json, statistics
from pathlib import Path

FIELDS = ("gemma", "mistral", "llama", "mean", "range")

def percentile(values, p):
    xs = sorted(values)
    if not xs: return None
    pos = (len(xs) - 1) * p
    lo = int(pos); hi = min(lo + 1, len(xs))
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)

def stats(values):
    if not values: return {"count":0}
    return {"count":len(values),"mean":statistics.fmean(values),
            "median":statistics.median(values),"p10":percentile(values,.10),
            "p90":percentile(values,.90),"min":min(values),"max":max(values)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,help="Complete anonymized input JSONL")
    ap.add_argument("--ratings",required=True,help="Append-only JQL annotated JSONL")
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    total=sum(1 for line in Path(a.input).open(encoding="utf-8") if line.strip())
    all_values={k:[] for k in FIELDS}
    by_lang=collections.defaultdict(lambda:{k:[] for k in FIELDS})
    by_source=collections.defaultdict(lambda:{k:[] for k in FIELDS})
    by_pair=collections.defaultdict(lambda:{k:[] for k in FIELDS})
    rated=0;missing=0
    with Path(a.ratings).open(encoding="utf-8") as f:
        for n,line in enumerate(f,1):
            if not line.strip(): continue
            row=json.loads(line);ann=row.get("jql_edu")
            if not ann: missing+=1;continue
            scores=ann.get("scores") or {}
            vals={k:float(scores[k]) for k in ("gemma","mistral","llama")}
            vals["mean"]=float(ann.get("mean",statistics.fmean(vals.values())))
            vals["range"]=float(ann.get("range",max(vals.values())-min(vals.values())))
            lang=str(row.get("language","unknown"));source=str(row.get("source","unknown"))
            for key,value in vals.items():
                all_values[key].append(value)
                by_lang[lang][key].append(value)
                by_source[source][key].append(value)
                by_pair[lang+" / "+source][key].append(value)
            rated+=1
    result={
      "input_rows":total,"rated_rows":rated,"remaining_unrated_rows":max(0,total-rated),
      "extra_or_duplicate_rating_rows":max(0,rated-total),"invalid_or_unannotated_output_rows":missing,
      "scores_are_annotations_only":True,
      "score_fields":{k:stats(v) for k,v in all_values.items()},
      "by_language":{k:{f:stats(v[f]) for f in FIELDS} for k,v in sorted(by_lang.items())},
      "by_source":{k:{f:stats(v[f]) for f in FIELDS} for k,v in sorted(by_source.items())},
      "by_language_and_source":{k:{f:stats(v[f]) for f in FIELDS} for k,v in sorted(by_pair.items())},
      "interpretation":"Descriptive QA only. Score distributions must not be used to remove, rank, replace or rebalance sentences."
    }
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"input_rows":total,"rated_rows":rated,
                      "remaining_unrated_rows":max(0,total-rated),"output":str(out)}))

if __name__=="__main__":main()
