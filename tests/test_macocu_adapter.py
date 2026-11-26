import zipfile

import pytest

from src.langid32.macocu import iter_paragraphs


def _archive(path, xml):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("MaCoCu-hr-2.0.xml", xml)


def test_macocu_extracts_paragraph_metadata_and_flags_before_filtering(tmp_path):
    path = tmp_path / "macocu.zip"
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <corpus id="MaCoCu-hr-2.0">
      <doc id="macocu.hr.doc1" url="https://example.hr/article/1">
        <p id="macocu.hr.doc1.1" quality="good" lm_score="0.91"
           heading="no" lang="hr" contains_sensitive="false">
          Ovo je dovoljno duga hrvatska recenica za provjeru izvora.
        </p>
        <p id="macocu.hr.doc1.2" quality="good" lm_score="0.72"
           heading="yes" lang="hr" contains_sensitive="false">Naslov</p>
        <p id="macocu.hr.doc1.3" quality="good" lm_score="0.88"
           heading="no" lang="hr" contains_sensitive="true">Osobni podatci</p>
        <p id="macocu.hr.doc1.4" quality="short" lm_score="0.43"
           heading="no" lang="hr" contains_sensitive="false">Kratko</p>
        <p id="macocu.hr.doc1.5" quality="good" lm_score="0.84"
           heading="no" lang="en" contains_sensitive="false">Wrong language</p>
      </doc>
    </corpus>"""
    _archive(path, xml)

    rows = list(iter_paragraphs(path, "hr"))
    assert len(rows) == 5
    first = rows[0]
    assert first["text"].startswith("Ovo je dovoljno duga hrvatska")
    assert first["group_id"] == "macocu.hr.doc1"
    assert first["provenance"] == {
        "source_file": "MaCoCu-hr-2.0.xml",
        "source_document_id": "macocu.hr.doc1",
        "source_paragraph_id": "macocu.hr.doc1.1",
        "source_document_url": "https://example.hr/article/1",
        "paragraph_quality": "good",
        "paragraph_fluency": 0.91,
        "paragraph_language": "hr",
        "paragraph_heading": False,
        "paragraph_sensitive": False,
    }
    assert rows[1]["provenance"]["paragraph_heading"] is True
    assert rows[2]["provenance"]["paragraph_sensitive"] is True
    assert rows[3]["provenance"]["paragraph_quality"] == "short"
    assert rows[4]["provenance"]["paragraph_language"] == "en"


def test_macocu_fails_closed_when_sensitive_flag_is_missing(tmp_path):
    path = tmp_path / "macocu.zip"
    xml = b"""<corpus><doc id="d1" url="https://example.hr/">
      <p id="p1" quality="good" lm_score="0.9" heading="no" lang="hr">Text</p>
    </doc></corpus>"""
    _archive(path, xml)

    with pytest.raises(RuntimeError, match="sensitive-information flag"):
        list(iter_paragraphs(path, "hr"))


def test_macocu_rejects_unknown_heading_values(tmp_path):
    path = tmp_path / "macocu.zip"
    xml = b"""<corpus><doc id="d1" url="https://example.hr/">
      <p id="p1" quality="good" lm_score="0.9" heading="maybe"
         lang="hr" contains_sensitive="false">Text</p>
    </doc></corpus>"""
    _archive(path, xml)

    with pytest.raises(RuntimeError, match="heading flag"):
        list(iter_paragraphs(path, "hr"))
