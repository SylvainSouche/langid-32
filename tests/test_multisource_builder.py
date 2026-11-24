import json

import pytest

from scripts.build_multisource_candidate import normalize_file, source_family


def test_source_family_uses_dataset_not_file_or_config():
    assert source_family("fineweb2:cat_Latn") == ("fineweb2", "cat_Latn")
    assert source_family("temu_cc0:literatura.txt") == ("temu_cc0", "literatura.txt")
    assert source_family("bsc_legal:dogc_ca-es.tsv") == ("bsc_legal", "dogc_ca-es.tsv")
    assert source_family("dgt-tm-2021") == ("dgt-tm-2021", None)


def test_normalize_file_preserves_component_provenance_and_group_id(tmp_path):
    source = tmp_path / "input.jsonl"
    output = tmp_path / "normalized.jsonl"
    row = {
        "text": "A sufficiently long sentence for the source-family test.",
        "language": "ca",
        "source": "fineweb2:cat_Latn",
        "source_release": "FineWeb2@revision",
        "group_id": "fineweb2:cat_Latn:doc-1",
        "licence_id": "ODC-By-1.0",
        "text_origin": "web text",
        "provenance": {"document_id": "doc-1"},
    }
    source.write_text(json.dumps(row) + "\n", encoding="utf-8")
    report = normalize_file(source, output)
    normalized = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert report["rows_out"] == 1
    assert normalized["source"] == "fineweb2"
    assert normalized["group_id"] == row["group_id"]
    assert normalized["provenance"]["source_component"] == "cat_Latn"
    assert normalized["provenance"]["source_original_name"] == "fineweb2:cat_Latn"


def test_normalize_file_unifies_dpo_fields_to_one_dataset_row_group(tmp_path):
    source = tmp_path / "dpo.jsonl"
    output = tmp_path / "normalized.jsonl"
    row = {
        "text": "A sufficiently long Catalan assistant response for this test.",
        "language": "ca",
        "source": "catalan_dpo_v2:chosen",
        "source_release": "Catalan-DPO-V2@revision",
        "group_id": "catalan_dpo_v2:chosen:row-7",
        "licence_id": "Apache-2.0",
        "text_origin": "dialogue",
        "provenance": {"dataset_row_id": "row-7", "field": "chosen"},
    }
    source.write_text(json.dumps(row) + "\n", encoding="utf-8")
    normalize_file(source, output)
    normalized = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert normalized["source"] == "catalan_dpo_v2"
    assert normalized["group_id"] == "catalan_dpo_v2:row-7"
    assert normalized["split_group_id"] == normalized["group_id"]
    assert normalized["provenance"]["source_component"] == "chosen"


def test_normalize_file_rejects_unmapped_source_component(tmp_path):
    source = tmp_path / "input.jsonl"
    output = tmp_path / "normalized.jsonl"
    row = {
        "text": "A sufficiently long sentence for this source component test.",
        "language": "fr",
        "source": "unknown:component",
        "source_release": "r1",
        "group_id": "unknown:component:1",
        "licence_id": "CC0-1.0",
        "text_origin": "test",
        "provenance": {},
    }
    source.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unmapped source component"):
        normalize_file(source, output)



def test_normalize_dgt_rows_adds_eurlex_celex_provenance(tmp_path):
    source = tmp_path / "dgt.jsonl"
    output = tmp_path / "normalized.jsonl"
    row = {
        "text": "A sufficiently long EU legislative sentence for this provenance test.",
        "language": "en",
        "source": "dgt-tm-2021",
        "source_release": "DGT-TM-release-2021",
        "group_id": "dgt-tm-2021:Vol_2020_4.zip:22020D0933",
        "licence_id": "EC-Reuse-Decision-2011-833-EU",
        "text_origin": "unknown",
        "provenance": {"tmx_member": "22020D0933.tmx"},
    }
    source.write_text(json.dumps(row) + "\n", encoding="utf-8")
    normalize_file(source, output)
    normalized = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
    assert normalized["text_origin"] == "eu_international_agreement"
    assert normalized["provenance"]["source_document_id"] == "22020D0933"
    assert normalized["provenance"]["numdoc_sector"] == "2"
    assert normalized["provenance"]["numdoc_year"] == 2020
    assert normalized["provenance"]["identifier_scheme"] == "EUR-Lex NumDoc (CELEX-compatible)"
    assert normalized["provenance"]["source_url_verification_status"] == "derived_from_numdoc_not_http_verified"
    assert normalized["provenance"]["source_url"].endswith("CELEX:22020D0933")
    assert normalized["provenance"]["source_latest_update"] == "DGT-TM release 2021; exact day/month not stated on JRC page"
