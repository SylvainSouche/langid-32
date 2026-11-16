#!/usr/bin/env python3
"""Probe stratified row-group reads from original FineWeb2 Parquet via HTTP ranges."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import fsspec
import pyarrow.parquet as pq

DATASET="HuggingFaceFW/fineweb-2"
REVISION="v2.1.0"
SHARDS={
 "spa_Latn":"data/spa_Latn/train/000_00000.parquet",
 "tur_Latn":"data/tur_Latn/train/000_00000.parquet",
}
COLUMNS=["text","id","dump","url","date","file_path","language","language_score","language_script","minhash_cluster_size","top_langs"]

def pick_groups(pf, n=4):
    total=pf.metadata.num_row_groups
    if total <= n:
        return list(range(total))
    return sorted(set(round(i*(total-1)/(n-1)) for i in range(n)))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--rows-per-group",type=int,default=100)
    args=ap.parse_args()
    out={"dataset":DATASET,"revision":REVISION,"columns":COLUMNS,"results":{}}
    for lang,path in SHARDS.items():
        url=f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{path}"
        fs=fsspec.filesystem("http")
        with fs.open(url,"rb",block_size=1024*1024,cache_type="readahead") as fh:
            pf=pq.ParquetFile(fh)
            groups=pick_groups(pf)
            rows=[pf.metadata.row_group(i).num_rows for i in range(pf.metadata.num_row_groups)]
            table=pf.read_row_groups(groups,columns=COLUMNS)
            # Keep only compact diagnostics; never persist text.
            lengths=table.column("text").cast("string").to_pylist()
            ids=table.column("id").cast("string").to_pylist()
            out["results"][lang]={
                "path":path,
                "row_groups_total":pf.metadata.num_row_groups,
                "row_groups_selected":groups,
                "selected_group_rows":[rows[i] for i in groups],
                "rows_read":table.num_rows,
                "first_text_lengths": [len(x) for x in lengths[:10]],
                "first_id_lengths": [len(x) for x in ids[:10]],
                "schema":[{"name":f.name,"type":str(f.type)} for f in table.schema],
            }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":
    main()
