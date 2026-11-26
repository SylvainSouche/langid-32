import json
import zipfile

from langid32.dgt_tmx_stage import stage


def test_stage_dgt_tmx_keeps_document_group_across_languages(tmp_path):
    archive = tmp_path / "Vol_2020_1.zip"
    tmx = """<?xml version="1.0" encoding="UTF-8"?>
    <tmx version="1.4"><body>
      <tu tuid="1">
        <tuv xml:lang="en"><seg>This is an English sentence.</seg></tuv>
        <tuv xml:lang="fr"><seg>Voici une phrase française.</seg></tuv>
      </tu>
      <tu tuid="2">
        <tuv xml:lang="en"><seg>Another English sentence.</seg></tuv>
        <tuv xml:lang="fr"><seg>Une autre phrase française.</seg></tuv>
      </tu>
    </body></tmx>"""
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("DOC001.tmx", tmx)
    import argparse
    output = tmp_path / "dgt.jsonl"
    args = argparse.Namespace(
        archives=[archive], output=output, source_release="fixture", languages=["en", "fr"],
        target_per_language=10, max_per_document_language=20,
        min_chars=1, max_chars=500, max_bytes=1500,
    )
    stage(args)
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert len(rows) == 4
    assert {row["language"] for row in rows} == {"en", "fr"}
    assert len({row["group_id"] for row in rows}) == 1
    assert all(row["text_origin"] == "unknown" for row in rows)
    assert all(row["licence_id"] == "EC-Reuse-Decision-2011-833-EU" for row in rows)
