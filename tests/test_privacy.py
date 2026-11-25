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
    assert result.status == "quarantined"
    assert "personal_name" in result.flags


def test_normal_sentence_is_not_rejected_by_shared_gate():
    result = screen_text("The weather changed during the afternoon and the road became wet.")
    assert result.accepted
    assert result.status == "clean"


def test_ambiguous_proper_name_is_quarantined_but_year_is_not_pii():
    ambiguous = screen_text("The report was prepared by Alice Martin for the committee.")
    assert not ambiguous.accepted
    assert ambiguous.status == "rejected"  # contextual author attribution is high confidence
    ordinary = screen_text("The 2024 report was published after the annual meeting.")
    assert ordinary.accepted
    uncertain = screen_text("Alice Martin joined the committee during the conference.")
    assert not uncertain.accepted
    assert uncertain.status == "quarantined"
    place = screen_text("The team visited New York during the conference.")
    assert place.accepted


def test_ipv6_and_trailing_number_street_addresses_are_rejected():
    ipv6 = screen_text("The server is reachable at 2001:db8::1 today.")
    assert not ipv6.accepted
    assert "ipv6" in ipv6.flags
    address = screen_text("The meeting is at Rue de Rivoli 12 in Paris.")
    assert not address.accepted
    assert "street_address" in address.flags


def test_malformed_dotted_number_is_not_classified_as_ipv4():
    from langid32.privacy import _has_ipv4
    assert not _has_ipv4("The version marker 999.999.999.999 is malformed and not an IP address.")
