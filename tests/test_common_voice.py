import importlib.util
import hashlib
import json
import sys
from pathlib import Path

from langid32.settings import load_config


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "curate_common_voice_hf.py"
SPEC = importlib.util.spec_from_file_location("curate_common_voice_hf", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_common_voice_expected_script_filter():
    assert MODULE.script_ratio("Καλημέρα σε όλους", "GREEK") > 0.95
    assert MODULE.script_ratio("Terve kaikille ystäville", "LATIN") > 0.95
    assert MODULE.script_ratio("Hello Καλημέρα", "LATIN") < 0.70


def test_common_voice_script_policy_covers_enabled_locales():
    cfg = load_config()
    languages = set(cfg["acquisition"]["source_rules"]["common_voice_v22"]["languages"])
    scripts = cfg["acquisition"]["source_rules"]["common_voice_v22"]["script"]["by_language"]
    assert set(scripts) == languages
    assert cfg["acquisition"]["source_rules"]["common_voice_v22"]["script"]["minimum_ratio"] == 0.70


def test_common_voice_checkpoint_is_bound_to_acquisition_policy():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "policy_hash = hashlib.sha256()" in source
    assert "download_common_voice_hf.py" in source
    assert "targets/common-voice.py" in source
    assert "common-voice-acquisition-{resolved_revision[:12]}-{policy_digest}.sqlite" in source
    assert '"acquisition_policy_digest": policy_digest' in source



def test_common_voice_curation_retains_safe_sentence_provenance_only(tmp_path, monkeypatch):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    locale_dir = input_root / "fi"
    locale_dir.mkdir(parents=True)
    tsv_content = (
        "sentence_id\\tsentence\\tvariant\\tsentence_domain\\tsource\\tis_used\\tclips_count\\tsource_locale\\n"
        "fi-1\\tTämä on riittävän pitkä suomenkielinen testilause.\\tstandard\\teveryday\\tuser\\ttrue\\t2\\tfi\\n"
    )
    tsv_bytes = tsv_content.encode("utf-8")
    (locale_dir / "validated_sentences.tsv").write_bytes(tsv_bytes)
    tsv_sha256 = hashlib.sha256(tsv_bytes).hexdigest()
    (input_root / "hf-common-voice-download-manifest.json").write_text(
        json.dumps({
            "source": "fsicoli/common_voice_22_0",
            "revision_resolved": "b" * 40,
            "results": [{
                "locale": "fi", "repo_commit": "b" * 40,
                "sha256": tsv_sha256, "bytes": len(tsv_bytes),
            }],
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", [
        "curate_common_voice_hf.py", "--input-root", str(input_root),
        "--output", str(output_root),
    ])
    MODULE.main()

    rows = [json.loads(line) for line in
            (output_root / "common_voice_candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    provenance = rows[0]["provenance"]
    assert provenance["source_locale"] == "fi"
    assert provenance["sentence_id"] == "fi-1"
    assert provenance["sentence_source"] == "user"
    assert provenance["sentence_variant"] == "standard"
    assert provenance["sentence_domain"] == "everyday"
    assert provenance["repo_commit"] == "b" * 40
    assert provenance["source_tsv_sha256"] == tsv_sha256
    assert not {"client_id", "path", "age", "gender", "accent"} & set(provenance)
