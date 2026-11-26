import io
import tarfile

from src.langid32.parlamint import iter_utterances


def test_parlamint_extracts_paragraph_segments_without_speaker_identity(tmp_path):
    xml = b'''<?xml version="1.0"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <text><body><u xml:id="session.u1" who="#speaker-private" ana="#chair">
        <seg xml:id="session.seg1">This is a sufficiently long Icelandic utterance segment.</seg>
        <seg xml:id="session.seg2">Another sufficiently long utterance segment for testing.</seg>
      </u>
      <u xml:id="session.u2" who="#another-private-speaker" ana="#guest">
        A complete utterance without explicit segment elements is retained as a session record.
      </u></body></text>
    </TEI>'''
    archive_path = tmp_path / "fixture.tgz"
    with tarfile.open(archive_path, "w:gz") as archive:
        info = tarfile.TarInfo("ParlaMint-IS_2024-01-01-16.xml")
        info.size = len(xml)
        archive.addfile(info, io.BytesIO(xml))

    rows = list(iter_utterances(archive_path, "is"))
    assert [row["text"] for row in rows] == [
        "This is a sufficiently long Icelandic utterance segment.",
        "Another sufficiently long utterance segment for testing.",
        "A complete utterance without explicit segment elements is retained as a session record.",
    ]
    assert all("who" not in row["provenance"] for row in rows)
    assert [row["provenance"]["speaker_roles"] for row in rows] == [
        ["chair"], ["chair"], ["guest"],
    ]
    assert all(row["provenance"]["session_date"] == "2024-01-01" for row in rows)
    assert all(row["provenance"]["publisher"] == "ParlaMint consortium / CLARIN.SI" for row in rows)
    assert all("private-speaker" not in repr(row) for row in rows)
    assert {row["group_id"] for row in rows} == {"ParlaMint-IS_2024-01-01-16"}
