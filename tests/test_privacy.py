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


def test_east_asian_postal_and_street_addresses_are_rejected():
    for text in (
        "The correspondence address is 東京都千代田区千代田1-1.",
        "Please deliver to 北京市朝阳区建国路88号.",
        "The office is at 서울특별시 강남구 테헤란로 123.",
        "Mail to 〒100-0001.",
    ):
        result = screen_text(text)
        assert not result.accepted, text
        assert "street_address" in result.flags, text


def test_east_asian_labelled_personal_names_are_rejected():
    for text in ("担当者: 山田太郎", "联系人：张伟", "담당자: 김민수"):
        result = screen_text(text)
        assert not result.accepted, text
        assert "person_name_context" in result.flags, text


def test_greek_and_cyrillic_person_name_candidates_are_quarantined():
    for text in (
        "Αλέξανδρος Παπαδόπουλος joined the committee.",
        "Анна Иванова joined the committee.",
    ):
        result = screen_text(text)
        assert not result.accepted, text
        assert result.status == "quarantined", text
        assert "ambiguous_proper_name" in result.flags, text


def test_provenance_sanitizer_removes_personal_names_but_keeps_source_references():
    from langid32.privacy import sanitize_provenance
    cleaned, removed = sanitize_provenance({
        "author": "Alice Martin",
        "speaker_name": "Jean Dupont",
        "title": "Alice Martin interview transcript",
        "speaker_ref": "SPEAKER_0042",
        "speaker_role": "member of parliament",
        "source_url": "https://example.org/document/42",
    })
    assert "author" not in cleaned
    assert "speaker_name" not in cleaned
    assert "title" not in cleaned
    assert cleaned["speaker_ref"] == "SPEAKER_0042"
    assert cleaned["speaker_role"] == "member of parliament"
    assert cleaned["source_url"] == "https://example.org/document/42"
    assert {"author", "speaker_name", "title"}.issubset(set(removed))
