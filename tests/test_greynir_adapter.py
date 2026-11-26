import gzip

import pytest

from src.langid32.greynir import PARTITION_FILES, REVISION, iter_sentences


def _write(path, records):
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        stream.write("\n\n".join(records) + "\n")


def test_greynir_extracts_terminal_text_and_nonidentifying_provenance(tmp_path):
    path = tmp_path / "copper01.gz"
    _write(path, [
        """( (META (ID-CORPUS abc-123.1)
                (ID-LOCAL greynir_corpus_00001.psd,.1)
                (URL https://example.is/private/path)
                (COMMENT ))
            (S0 (S-MAIN
                    (IP (NP-SUBJ (pfn_et_nf_hk_p3 Hann (lemma hann)))
                        (VP (so_1_þf_fh_p3_et_nt_gm segir (lemma segja))
                            (NP-OBJ (no_et_þf_hk sannleikann (lemma sannleikur)))))
                (grm .)))""",
        """( (META (ID-CORPUS abc-123.2)
                (ID-LOCAL greynir_corpus_00001.psd,.2)
                (URL https://example.is/heading)
                (COMMENT ))
            (S0 (S-HEADING (NP (no_ft_nf_kk Fyrirsagnir (lemma fyrirsögn))))))
        """,
    ])

    rows = list(iter_sentences(path, "copper"))
    assert len(rows) == 1
    assert rows[0]["text"] == "Hann segir sannleikann."
    assert rows[0]["group_id"] == "abc-123.1"
    assert rows[0]["provenance"] == {
        "source_file": PARTITION_FILES["copper"],
        "source_partition": "copper",
        "source_record_number": 1,
        "source_corpus_id": "abc-123.1",
        "source_local_id": "greynir_corpus_00001.psd,.1",
        "publisher": "Miðeind ehf.",
        "upstream_revision": REVISION,
    }
    assert "private/path" not in repr(rows[0])


def test_greynir_silver_partition_is_explicit_and_gold_is_not_supported(tmp_path):
    path = tmp_path / "silver.gz"
    _write(path, [
        """( (META (ID-CORPUS silver-1)
                (ID-LOCAL silver.psd,.1)
                (COMMENT ))
            (S0 (S-MAIN (IP (VP (so_1_þf_fh_p3_et_nt_gm Prófar (lemma prófa))
                                (NP-OBJ (no_et_þf_hk útdrátt (lemma útdrátt)))))))""",
    ])

    rows = list(iter_sentences(path, "silver"))
    assert len(rows) == 1
    assert rows[0]["provenance"]["source_partition"] == "silver"

    with pytest.raises(ValueError, match="Unsupported Greynir partition"):
        list(iter_sentences(path, "gold"))


def test_greynir_rejects_unbalanced_records(tmp_path):
    path = tmp_path / "broken.gz"
    _write(path, ["( (META (ID-CORPUS broken)"])
    with pytest.raises(RuntimeError, match="incomplete tree record"):
        list(iter_sentences(path, "copper"))
