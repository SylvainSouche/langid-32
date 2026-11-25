#!/usr/bin/env python3
"""Stream every filtered acquisition-pool record into the full JQL Parquet."""
from __future__ import annotations
import argparse, hashlib, json, unicodedata
from collections import Counter
from pathlib import Path


def sentence_id(language: str, source: str, sentence: str) -> str:
    return hashlib.sha256("\\0".join((language, source, sentence)).encode("utf-8")).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--summary", required=True, type=Path)
    p.add_argument("--all", action="store_true", help="Required: sampling is forbidden")
    p.add_argument("--batch-size", type=int, default=8192)
    a = p.parse_args()
    if not a.all: p.error("--all is mandatory")
    if a.batch_size < 1: p.error("--batch-size must be positive")
    if not a.input.is_file(): p.error(f"missing input: {a.input}")
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("Install pyarrow") from exc
    schema = pa.schema([("id",pa.string()),("lang",pa.string()),("sentence",pa.string()),
                        ("source",pa.string()),("source-variant",pa.string())])
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    counts, seen, batch = Counter(), set(), []
    writer = pq.ParquetWriter(a.output, schema, compression="zstd")
    rows = 0
    try:
        with a.input.open(encoding="utf-8") as stream:
            for n, line in enumerate(stream, 1):
                if not line.strip(): continue
                try: row = json.loads(line)
                except json.JSONDecodeError as e: raise ValueError(f"{a.input}:{n}: {e}") from e
                lang = str(row.get("language","")).strip().lower()
                source = str(row.get("source","")).strip()
                sentence = " ".join(unicodedata.normalize("NFC",str(row.get("text",""))).split())
                if not lang or not source or not sentence:
                    raise ValueError(f"{a.input}:{n}: missing language/source/text")
                ident = sentence_id(lang, source, sentence)
                if ident in seen: raise ValueError(f"{a.input}:{n}: duplicate assessment ID {ident}")
                seen.add(ident)
                batch.append({"id":ident,"lang":lang,"sentence":sentence,
                              "source":source,"source-variant":source})
                counts[(lang,source)] += 1
                rows += 1
                if len(batch) >= a.batch_size:
                    writer.write_table(pa.Table.from_pylist(batch,schema=schema)); batch.clear()
        if batch: writer.write_table(pa.Table.from_pylist(batch,schema=schema))
    except Exception:
        writer.close(); a.output.unlink(missing_ok=True); raise
    writer.close()
    summary={"status":"full_filtered_acquisition_pool","sampling":False,"rows":rows,
             "unique_ids":len(seen),"source_identity":"original source identifier",
             "final_30k_selection":"deferred_pending_user_review",
             "counts_by_language_source":[{"language":l,"source":s,"count":n}
                                           for (l,s),n in sorted(counts.items())]}
    a.summary.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"rows":rows},indent=2))


if __name__ == "__main__": main()
