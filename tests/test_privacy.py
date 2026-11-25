from langid32.privacy import screen_record, screen_text


def test_high_confidence_identifiers_are_rejected():
    base = "This is an ordinary sentence long enough to pass quality screening"
    for suffix, flag in [
        (" contact alice@example.org", "email"),
        (" visit https://example.org/page", "url"),
        (" from 192.168.1.42", "ipv4"),
        (" call +33 6 12 34 56 78", "phone_or_long_identifier"),
        (" at 14 Main Street", "street_address"),
        (" ask Dr. Alice Martin", "person_name_honorific"),
        (" contact John Smith", "person_name_context"),
    ]:
        result = screen_text(base + suffix)
        assert not result.accepted
        assert flag in result.flags


def test_upstream_sensitive_flags_fail_closed():
    row = {
        "text": "This is a clean-looking sentence with enough ordinary words",
        "provenance": {"privacy_flags": ["personal_name"]},
    }
    result = screen_record(row)
    assert not result.accepted
    assert result.status == "rejected"
    assert "personal_name" in result.flags


def test_normal_sentence_is_not_rejected_by_shared_gate():
    result = screen_text("The weather changed during the afternoon and the road became wet.")
    assert result.accepted
    assert result.status == "clean"
