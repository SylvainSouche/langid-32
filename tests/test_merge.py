import json
from pathlib import Path

from langid32.merge import merge, split_for


def _args(tmp_path, inputs, cap=0):
    import argparse
    return argparse.Namespace(
        inputs=inputs, output=tmp_path / "out", min_chars=1, max_chars=500,
        max_bytes=1500, max_per_language=cap, validation_fraction=0.1,
        test_fraction=0.1, seed="test-seed", require_exact_counts=False, exclusions=None,\n        preferred_source_share=0.30, max_source_share=0.50,
    )


def _row(text, language, source, group):
    return {
        "text": text, "language": language, "source": source,
        "source_release": "r1", "group_id": group,
        "licence_id": "CC0-1.0", "text_origin": "original",
        "provenance": {"document": "opaque-id"},
    }


def test_same_group_has_same_split_across_languages():
    assert split_for("source:document-1", "seed", 0.1, 0.1) == split_for(
        "source:document-1", "seed", 0.1, 0.1
    )


def test_merge_deduplicates_across_sources_and_retains_internal_provenance(tmp_path):
    input_a = tmp_path / "a.jsonl"
    input_b = tmp_path / "b.jsonl"
    input_a.write_text(json.dumps(_row(" Bonjour  monde ", "fr", "a", "a:doc1")) + "\n"
                       + json.dumps(_row("Hello world", "en", "a", "a:doc1")) + "\n")
    input_b.write_text(json.dumps(_row("Bonjour monde", "fr", "b", "b:doc9")) + "\n")
    args = _args(tmp_path, [input_a, input_b])
    merge(args)
    output = args.output
    public = []
    for split in ("train", "validation", "test"):
        public.extend(json.loads(line) for line in
                      (output / f"{split}.jsonl").read_text().splitlines())
    assert sum(row["language"] == "fr" for row in public) == 1
    assert sum(row["language"] == "en" for row in public) == 1
    internal = [json.loads(line) for line in (output / "records.jsonl").read_text().splitlines()]
    assert all("group_id" in row and "licence_id" in row and "provenance" in row
               for row in internal)
    assert all("group_id" not in row for row in public)


def test_merge_applies_cap_after_dedup(tmp_path):
    source = tmp_path / "source.jsonl"
    rows = [_row(f"Sentence number {i}", "fr", "a", f"a:doc{i}") for i in range(100)]
    source.write_text("".join(json.dumps(row) + "\n" for row in rows))
    args = _args(tmp_path, [source], cap=20)
    args.preferred_source_share = 1.0
    args.max_source_share = 1.0
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    assert sum(v for k, v in manifest["counts"].items() if k.startswith("fr:")) == 20


def test_merge_excludes_obvious_pii_and_flags_numeric_sequences(tmp_path):
    source = tmp_path / "privacy.jsonl"
    rows = [
        _row("Contact team@example.org for more information", "fr", "a", "a:email"),
        _row("Read https://example.org/details for details", "fr", "a", "a:url"),
        _row("The server is at 192.0.2.10 today", "fr", "a", "a:ip"),
        _row("Call us at +33 1 23 45 67 89 today", "fr", "a", "a:phone"),
    ]
    source.write_text("".join(json.dumps(row) + "\n" for row in rows))
    args = _args(tmp_path, [source])
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    assert manifest["rejected"]["email_excluded"] == 1
    assert manifest["rejected"]["url_excluded"] == 1
    assert manifest["rejected"]["ipv4_excluded"] == 1
    internal = [json.loads(line) for line in (args.output / "records.jsonl").read_text().splitlines()]
    assert len(internal) == 1
    assert "phone_like" in internal[0]["provenance"]["privacy_flags"]


def test_privacy_patterns_do_not_treat_legal_numbers_as_ip_or_phone():
    from langid32.merge import IPV4_RE, has_phone_like
    assert IPV4_RE.search("Host 192.0.2.10") is not None
    assert IPV4_RE.search("Reference 2024.1.1.1") is None
    assert has_phone_like("Call +33 1 23 45 67 89")
    assert not has_phone_like("Decision 2024-01-01, article 12345")


def test_privacy_regexes_handle_unicode_email_and_attached_urls():
    from langid32.merge import EMAIL_RE, URL_RE, WEB_FRAGMENT_RE
    assert EMAIL_RE.search("R-phost díolacháin@hmminghe.com")
    assert EMAIL_RE.search("support@takarush.co.jp")
    assert EMAIL_RE.search("support@takarush.co.jpまで")
    assert URL_RE.search("sitehttp://register.consilium.europa.eu")
    assert URL_RE.search("COVID-19https://ec.europa.eu/info/file.pdf")
    assert not URL_RE.search("awww.")
    assert not WEB_FRAGMENT_RE.search("awww.")



def test_source_exclusion_registry_removes_document_and_all_derived_split_group(tmp_path):
    source = tmp_path / "source.jsonl"
    rows = [
        _row("First sentence from document", "fr", "web", "web:doc1"),
        _row("Second sentence from same document", "fr", "web", "web:doc1"),
        _row("Independent document sentence", "fr", "web", "web:doc2"),
    ]
    rows[0]["provenance"]["source_url"] = "https://example.org/a"
    rows[1]["provenance"]["source_url"] = "https://example.org/a"
    rows[2]["provenance"]["source_url"] = "https://example.org/b"
    source.write_text("".join(json.dumps(row) + "\n" for row in rows))
    registry = tmp_path / "exclusions.jsonl"
    registry.write_text(json.dumps({
        "scope": "url", "source_url": "https://example.org/a",
        "reason_code": "rights_notice", "case_id": "CASE-1",
        "effective_at": "2026-11-18T00:00:00Z", "status": "active",
    }) + "\n")
    args = _args(tmp_path, [source])
    args.exclusions = registry
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    internal = [json.loads(line) for line in (args.output / "records.jsonl").read_text().splitlines()]
    assert len(internal) == 1
    assert internal[0]["group_id"] == "web:doc2"
    assert manifest["rejected"]["source_exclusion_registry"] == 2
    assert manifest["exclusion_registry"]["active_rules_loaded"] == 1


def test_source_exclusion_registry_domain_matches_subdomains(tmp_path):
    source = tmp_path / "source.jsonl"
    row = _row("Sentence from blocked host", "fr", "web", "web:doc1")
    row["provenance"]["source_url"] = "https://news.example.org/article"
    source.write_text(json.dumps(row) + "\n")
    registry = tmp_path / "exclusions.jsonl"
    registry.write_text(json.dumps({
        "scope": "domain", "domain": "example.org",
        "reason_code": "provider_restriction", "effective_at": "2026-11-18",
    }) + "\n")
    args = _args(tmp_path, [source])
    args.exclusions = registry
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    assert manifest["rejected"]["source_exclusion_registry"] == 1


def test_merge_removes_text_collisions_across_language_labels(tmp_path):
    source = tmp_path / "cross-language.jsonl"
    rows = [
        _row("The same sentence appears in two language labels", "en", "a", "a:en1"),
        _row("The same sentence appears in two language labels", "fr", "b", "b:fr1"),
        _row("A separate French sentence remains available", "fr", "b", "b:fr2"),
    ]
    source.write_text("".join(json.dumps(row) + "\\n" for row in rows))
    args = _args(tmp_path, [source])
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    internal = [json.loads(line) for line in (args.output / "records.jsonl").read_text().splitlines()]
    assert manifest["cross_language_collision_strings_removed"] == 1
    assert manifest["rejected"]["cross_language_collision"] == 2
    assert len(internal) == 1
    assert internal[0]["text"] == "A separate French sentence remains available"


def test_merge_prefers_thirty_percent_source_share_and_never_exceeds_fifty(tmp_path):
    source = tmp_path / "balanced.jsonl"
    rows = [
        _row(f"Sentence from source {source_name} number {index}", "fr",
             source_name, f"{source_name}:doc{index}")
        for source_name in ("a", "b", "c") for index in range(30)
    ]
    source.write_text("".join(json.dumps(row) + "\\n" for row in rows))
    args = _args(tmp_path, [source], cap=20)
    args.validation_fraction = 0
    args.test_fraction = 0
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    counts = {key.split(":")[0]: value for key, value in manifest["source_counts"].items()}
    assert sum(counts.values()) == 20
    assert set(counts) == {"a", "b", "c"}
    assert max(counts.values()) <= 10
    assert min(counts.values()) >= 6


def test_merge_underfills_instead_of_exceeding_hard_source_share(tmp_path):
    source = tmp_path / "single-source.jsonl"
    rows = [_row(f"Only source sentence number {index}", "fr", "sole",
                 f"sole:doc{index}") for index in range(40)]
    source.write_text("".join(json.dumps(row) + "\\n" for row in rows))
    args = _args(tmp_path, [source], cap=20)
    args.validation_fraction = 0
    args.test_fraction = 0
    merge(args)
    manifest = json.loads((args.output / "manifest.json").read_text())
    internal = [json.loads(line) for line in (args.output / "records.jsonl").read_text().splitlines()]
    assert len(internal) == 10
    assert manifest["source_quota_shortfalls"]["fr:train"]["expected"] == 20
    assert manifest["source_quota_shortfalls"]["fr:train"]["actual"] == 10
