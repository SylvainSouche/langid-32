import gzip
import io
import json
import tarfile

from langid32.maalfrid_inventory import inventory


def test_maalfrid_inventory_counts_paragraphs_and_document_hashes(tmp_path):
    archive_path = tmp_path / "maalfrid_nno.tar"
    payload = (
        json.dumps({
            "doc_id": "nno-1", "doc_hash": "hash-1", "domain": "example.no",
            "lang": "nno",
            "fulltext": ["Dette er ei nynorsk setning.", "Ei anna setning er her."],
        }, ensure_ascii=False).encode("utf-8") + b"\n"
    )
    compressed = gzip.compress(payload)
    with tarfile.open(archive_path, "w") as archive:
        info = tarfile.TarInfo("nno/example.no/html/part-000.jsonl.gz")
        info.size = len(compressed)
        archive.addfile(info, io.BytesIO(compressed))
    rows = inventory([("nn", archive_path)], 12, 500, 1500)
    row = rows[0]
    assert row["documents"] == 1
    assert row["paragraphs"] == 2
    assert row["eligible_paragraphs"] == 2
    assert row["unique_eligible_paragraphs"] == 2
    assert row["unique_documents_by_hash"] == 1
    assert row["domains"] == 1
    assert row["pii_screening"] == "not_performed"
