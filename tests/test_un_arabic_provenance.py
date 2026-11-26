import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "acquire_waiting_sources.py"
SPEC = importlib.util.spec_from_file_location("acquire_waiting_sources_provenance_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_un_arabic_row_index_is_not_misrepresented_as_source_document_id():
    provenance = MODULE.un_arabic_provenance(
        {
            "text_ar": "نص عربي تجريبي طويل بما يكفي لاختبار حفظ البيانات الوصفية",
            "text_en": "English text must not be copied into provenance",
        },
        17,
        "a" * 40,
    )
    safe = MODULE.sanitize_provenance(provenance)

    assert safe["source_row_index"] == 17
    assert "source_record_id" not in safe
    assert "source_document_url" not in safe
    assert "text_en" not in safe
    assert "text_ar" not in safe
    assert safe["publisher"] == "United Nations"
    assert safe["attribution_required"] is True
    assert safe["required_citation_id"] == "ziemski-junczys-dowmunt-pouliquen-2016"


def test_un_arabic_preserves_real_source_id_and_document_url_only_when_present():
    provenance = MODULE.un_arabic_provenance(
        {
            "id": "official-record-123",
            "url": "https://example.invalid/official-record-123",
            "date": "2024-01-02",
            "title": "Official record",
            "source": "United Nations",
            "text_en": "not copied",
        },
        19,
        "b" * 40,
    )

    assert provenance["source_record_id"] == "official-record-123"
    assert provenance["source_document_url"] == "https://example.invalid/official-record-123"
    assert provenance["source_row_index"] == 19
    assert provenance["date"] == "2024-01-02"
    assert "text_en" not in provenance


def test_un_arabic_stream_cursor_is_stored_inside_checkpointed_source_directory():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'state_path = output_root / f"un-arabic-stream-state-' in source
    assert 'source_record_id_from_group=False' in source
