import zipfile

from langid32.dgt_tmx_inventory import inventory


def test_dgt_tmx_inventory_counts_languages_groups_and_duplicates(tmp_path):
    root = tmp_path / "volumes"
    root.mkdir()
    xml = """<?xml version="1.0" encoding="UTF-16"?>
    <tmx version="1.4">
      <header srclang="en"/>
      <body>
        <tu tuid="1">
          <tuv xml:lang="en"><seg>Hello, this is a complete sentence.</seg></tuv>
          <tuv xml:lang="fr"><seg>Bonjour, ceci est une phrase complète.</seg></tuv>
        </tu>
        <tu tuid="2">
          <tuv xml:lang="en"><seg>Hello, this is a complete sentence.</seg></tuv>
          <tuv xml:lang="fr"><seg>Bonjour, ceci est une phrase complète.</seg></tuv>
        </tu>
      </body>
    </tmx>"""
    payload = b"\xff\xfe" + xml.encode("utf-16le")
    with zipfile.ZipFile(root / "Vol_2020_1.zip", "w") as archive:
        archive.writestr("CELEX_32020R0001.tmx", payload)
    summary = inventory(root, tmp_path / "dgt.csv", 12, 500, 1500, 0)
    assert summary["tmx_files_processed"] == 1
    with (tmp_path / "dgt.csv").open(encoding="utf-8", newline="") as stream:
        import csv
        rows = {row["language"]: row for row in csv.DictReader(stream)}
    assert rows["en"]["translation_units_with_language_segment"] == "2"
    assert rows["en"]["segments"] == "2"
    assert rows["en"]["unique_eligible_text"] == "1"
    assert rows["fr"]["segments"] == "2"
    assert rows["fr"]["unique_eligible_text"] == "1"
    assert rows["en"]["document_groups"] == "1"
