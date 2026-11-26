import io
import tarfile

from src.langid32.parlamint import iter_utterances


def test_parlamint_extracts_paragraph_segments_without_speaker_identity(tmp_path):
    xml = b'''<?xml version="1.0"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <text><body><u xml:id="session.u1" who="#speaker-private" ana="#chair">
        <seg xml:id="session.seg1">This is a sufficiently long Icelandic utterance segment.</seg>
        <seg xml:id="session.seg2">Another sufficiently long utterance segment for testing.</seg>
      </u></body></text>
    </TEI>'''
    archive_path = tmp_path / "fixture.tgz"
    with tarfile.open(archive_path, "w:gz") as archive:
        info = tarfile.TarInfo("ParlaMint-IS_2024-01-01.xml")
        info.size = len(xml)
        archive.addfile(info, io.BytesIO(xml))

    rows = list(iter_utterances(archive_path, "is"))
    assert [row["text"] for row in rows] == [
        "This is a sufficiently long Icelandic utterance segment.",
        "Another sufficiently long utterance segment for testing.",
    ]
    assert all("who" not in row["provenance"] for row in rows)
    assert all(row["provenance"]["speaker_roles"] == ["chair"] for row in rows)
    assert all("speaker-private" not in repr(row) for row in rows)
    assert {row["group_id"] for row in rows} == {"session.u1"}
