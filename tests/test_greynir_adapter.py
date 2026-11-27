import gzip

import pytest

from src.langid32.greynir import COPPER_FILES, LFS_POINTERS, PARTITION_FILES, REVISION, _terminals, iter_sentences


def _write(path, records):
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        stream.write("\n\n".join(records) + "\n")


def test_greynir_declares_all_copper_files_and_extracts_terminal_text(tmp_path):
    assert len(COPPER_FILES) == 10
    assert COPPER_FILES[0] == PARTITION_FILES["copper"]
    assert set(LFS_POINTERS) == set(COPPER_FILES) | {PARTITION_FILES["silver"]}
    assert LFS_POINTERS[PARTITION_FILES["copper"]][0] == "09726a43b1a4b025960f221db49a6433337667ae42eb88df11d4e2565db724e0"
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
                (grm .))))""",
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
    assert rows[0]["group_id"] == "https://example.is/private/path"
    assert rows[0]["provenance"] == {
        "source_file": PARTITION_FILES["copper"],
        "source_partition": "copper",
        "source_record_number": 1,
        "source_corpus_id": "abc-123.1",
        "source_local_id": "greynir_corpus_00001.psd,.1",
        "source_document_url": "https://example.is/private/path",
        "publisher": "Miðeind ehf.",
        "upstream_revision": REVISION,
    }


def test_greynir_silver_partition_is_explicit_and_gold_is_not_supported(tmp_path):
    path = tmp_path / "silver.gz"
    _write(path, [
        """( (META (ID-CORPUS silver-1)
                (ID-LOCAL silver.psd,.1)
                (URL https://example.is/silver)
                (COMMENT ))
            (S0 (S-MAIN (IP (VP (so_1_þf_fh_p3_et_nt_gm Prófar (lemma prófa))
                                (NP-OBJ (no_et_þf_hk útdrátt (lemma útdrátt))))))))""",
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



def test_greynir_preserves_multiword_terminal_nodes():
    node = ["person_ef_kvk", "Anna", "Jónsdóttir", ["lemma", "Anna Jónsdóttir"]]
    assert _terminals(node) == ["Anna", "Jónsdóttir"]
    assert _terminals(["grm", "„"]) == ["„"]
    assert _terminals(["grm", "—"]) == ["—"]


def test_greynir_quoted_parentheses_do_not_change_tree_depth(tmp_path):
    path = tmp_path / "quoted-parentheses.gz"
    _write(path, [
        """( (META (ID-CORPUS quoted-1)
                (ID-LOCAL quoted.psd,.1)
                (URL https://example.is/quoted)
                (COMMENT "literal ( and ) parentheses"))
            (S0 (S-MAIN (IP (NP-SUBJ (no_et_nf_hk "Próf (A)" (lemma próf)))
                            (VP (so_1_þf_fh_p3_et_nt_gm virkar (lemma virka))
                                (grm .))))))"""
    ])
    rows = list(iter_sentences(path, "copper"))
    assert len(rows) == 1
    assert rows[0]["text"] == "Próf (A) virkar."


def test_greynir_escaped_parenthesis_in_unquoted_atom(tmp_path):
    from src.langid32.greynir import _parse_sexpr, _record_blocks

    record = r"""(
        (META (ID-CORPUS escaped-1)
              (URL https://example.is/escaped)
              (COMMENT ))
        (S0
            (S-PREFIX (sequence 5 (lemma 5)) (grm \)))
            (S-MAIN (IP (NP (no_et_hk_nf Próf (lemma próf)))))
            (grm .))
    )"""
    blocks = list(_record_blocks(record.splitlines(keepends=True)))
    assert len(blocks) == 1

    tree = _parse_sexpr(blocks[0])
    sentence = next(child for child in tree if isinstance(child, list) and child[0] == "S0")
    prefix = next(child for child in sentence if isinstance(child, list) and child[0] == "S-PREFIX")
    assert prefix[2] == ["grm", ")"]
