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
    assert all("speaker-private" not in repr(row) for row in rows)
    assert all("private-speaker" not in repr(row) for row in rows)
    assert {row["group_id"] for row in rows} == {"ParlaMint-IS_2024-01-01-16"}


def test_parlamint_turkish_release_is_wired_to_the_audited_archive(tmp_path):
    from src.langid32.parlamint import SOURCES

    assert SOURCES["tr"]["source"] == "parlamint_tr"
    assert SOURCES["tr"]["md5"] == "82569712b7194216a18012af5bac992c"
    assert SOURCES["tr"]["prefix"] == "ParlaMint-TR_"
    xml = b'''<?xml version="1.0"?>
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <text><body><u xml:id="tr.u1" ana="#regular">
        <seg xml:id="tr.seg1">Bu yeterince uzun bir Türkçe konuşma parçasıdır.</seg>
      </u></body></text>
    </TEI>'''
    archive_path = tmp_path / "turkish.tgz"
    with tarfile.open(archive_path, "w:gz") as archive:
        info = tarfile.TarInfo("ParlaMint-TR_2024-01-01-1.xml")
        info.size = len(xml)
        archive.addfile(info, io.BytesIO(xml))
    rows = list(iter_utterances(archive_path, "tr"))
    assert len(rows) == 1
    assert rows[0]["provenance"]["session_date"] == "2024-01-01"
    assert rows[0]["provenance"]["speaker_roles"] == ["regular"]
