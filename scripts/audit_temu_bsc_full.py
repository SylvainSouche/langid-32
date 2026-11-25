#!/usr/bin/env python3
"""Full README-scoped inventory and dedup audit of TeMU-BSC catalan_CC0_sentences."""
from __future__ import annotations
import collections, csv, hashlib, io, json, re, sqlite3, tempfile, unicodedata, zipfile
from pathlib import Path
import requests

URL="https://codeload.github.com/TeMU-BSC/catalan_CC0_sentences/zip/refs/heads/main"
OUT=Path("reports/temu-bsc-catalan-cc0-full-audit.json")
CHUNK=1024*1024
CC0_COMPONENTS={
 "catalan_government_crawling_frases_seleccionades_filtrades.txt",
 "datasets_sentences.tsv","edited_generated_selected_chatbot.txt",
 "edited_selected_chatbot.txt","frases_agenda.txt",
 "frases_diccionaris_enciclopedia.txt","frases_spl.txt",
 "frases_toponimia_valenciana_balear.txt","generades_spl_seleccionades.txt",
 "literatura.txt","more_intents.txt","new_sentences_from_catalan_newswire.txt",
 "plantilles_intents.txt","selected_club.txt","sentences_from_xitxat_corpus.txt",
 "sentences_from_xitxat_corpus2.txt","wikidata_sentences.txt"
}
AGGREGATES={"new_catalan_cc0_corpus.txt","xitxat_and_toponyms.txt"}

def norm(s):
    return " ".join(unicodedata.normalize("NFC",s).split()).casefold()

def main():
    fd,name=tempfile.mkstemp(prefix="temu-full-",suffix=".zip")
    Path(name).unlink(missing_ok=True)
    p=Path(name); h=hashlib.sha256(); size=0
    dbfd,dbname=tempfile.mkstemp(prefix="temu-union-",suffix=".sqlite")
    Path(dbname).unlink(missing_ok=True)
    db=sqlite3.connect(dbname)
    db.execute("PRAGMA journal_mode=OFF"); db.execute("PRAGMA synchronous=OFF")
    db.execute("CREATE TABLE union_text (text TEXT PRIMARY KEY) WITHOUT ROWID")
    try:
        with requests.get(URL,stream=True,timeout=(60,300),
                          headers={"User-Agent":"langid-32-source-audit/1"}) as r:
            r.raise_for_status()
            with p.open("wb") as f:
                for b in r.iter_content(CHUNK):
                    if b: f.write(b); h.update(b); size+=len(b)
        files=[]; global_rows=0; global_union_inserted=0; tsv_labels=collections.Counter()
        with zipfile.ZipFile(p) as z:
            names=z.namelist()
            prefix=next(n.split("/")[0]+"/" for n in names if n.endswith("/README.md"))
            readme=z.read(prefix+"README.md").decode("utf-8","replace")
            for member in sorted(n for n in names if n.startswith(prefix) and not n.endswith("/") and n.lower().endswith((".txt",".tsv"))):
                rel=member[len(prefix):]
                basename=rel.rsplit("/",1)[-1]
                raw=z.read(member)
                text=raw.decode("utf-8","replace")
                rows=collections.Counter(); unique=set()
                if rel.endswith(".tsv"):
                    for row in csv.reader(io.StringIO(text),delimiter="\t"):
                        if not row: continue
                        sent=row[0].strip()
                        if not sent: continue
                        rows["nonempty_sentence_cells"]+=1
                        unique.add(norm(sent))
                        if len(row)>1 and row[1].strip(): tsv_labels[row[1].strip()]+=1
                        if rel in CC0_COMPONENTS:
                            cur=db.execute("INSERT OR IGNORE INTO union_text VALUES (?)",(norm(sent),))
                            if cur.rowcount: global_union_inserted+=1
                else:
                    lines=text.splitlines()
                    for line in lines:
                        s=line.strip()
                        if not s: continue
                        rows["nonempty_lines"]+=1
                        unique.add(norm(s))
                        if rel in CC0_COMPONENTS:
                            cur=db.execute("INSERT OR IGNORE INTO union_text VALUES (?)",(norm(s),))
                            if cur.rowcount: global_union_inserted+=1
                rows["physical_lines"]=len(text.splitlines())
                rows["distinct_normalized_within_file"]=len(unique)
                rows["normalized_duplicates_within_file"]=max(0,rows.get("nonempty_sentence_cells",rows.get("nonempty_lines",0))-len(unique))
                rows["bytes"]=len(raw); rows["sha256"]=hashlib.sha256(raw).hexdigest()
                rows["cc0_constituent_in_union"]=rel in CC0_COMPONENTS
                rows["aggregate_not_added_to_union"]=basename in AGGREGATES
                rows["other_or_rights_unresolved"]=rel not in CC0_COMPONENTS and basename not in AGGREGATES
                files.append({"file":rel,"measured":dict(rows)})
        db.commit()
        union_count=db.execute("SELECT COUNT(*) FROM union_text").fetchone()[0]
        report={
          "dataset":"TeMU-BSC catalan_CC0_sentences",
          "source":"https://github.com/TeMU-BSC/catalan_CC0_sentences",
          "repository_zip_bytes":size,"repository_zip_sha256":h.hexdigest(),
          "readme_scoped_cc0_components":sorted(CC0_COMPONENTS),
          "aggregate_files_excluded_from_union":sorted(AGGREGATES),
          "files":files,"tsv_source_label_counts":dict(tsv_labels),
          "cc0_component_normalized_union":union_count,
          "new_unique_insertions_during_scan":global_union_inserted,
          "normalization":"NFC; Unicode whitespace collapsed; casefold. This is a normalized text union, not a licence or linguistic-quality decision.",
          "rights_classification":"CC0 union includes only README-identified CC0/CC0-waived components. Author-permission Marius Serra files, Pujolar files without explicit CC0 statement, translated Wikipedia, and unexplained auxiliary gencat files are measured individually but excluded. Aggregate files are reported but not added to union to avoid double counting.",
          "caveats":"README describes some aggregate constituent files that are absent from the repository root inventory; their aggregate-only content remains measurable as aggregate but is not separately attributable. Literary source is published under CC0 by the README, but the underlying title-level provenance is not enumerated."
        }
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(OUT.read_text(encoding="utf-8"))
    finally:
        db.close(); p.unlink(missing_ok=True); Path(dbname).unlink(missing_ok=True)

if __name__=="__main__": main()
