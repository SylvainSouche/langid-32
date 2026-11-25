"""Conservative multilingual PII screening shared by all acquisition adapters.

This is a deterministic first-pass privacy gate, not a claim of perfect NER.
High-confidence identifiers are rejected; ambiguous person/address indicators
are quarantined and never enter the candidate pool.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

EMAIL = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Z]{2,}(?![A-Za-z0-9_.-])")
URL = re.compile(r"(?i)(?:https?://|www\.)\S+")
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
LONG_NUMBER = re.compile(r"(?<!\w)\+?\d(?:[\d\s()./-]{6,}\d)?(?!\w)")
# Street/address indicators across the target European languages.
STREET = re.compile(
    r"(?i)\b(?:street|st\.?|road|rd\.?|avenue|ave\.?|boulevard|blvd\.?|"
    r"lane|drive|way|strasse|straße|platz|rue|avenue|chemin|route|"
    r"calle|carrer|via|viale|ulica|ul\.?|cesta|ulice|utca|"
    r"gata|gatan|veg(?:en)?|gade|kadun|tie|katu|"
    r"ulica|ul\.?|улица|проспект|شارع)\b"
)
HOUSE_NUMBER = re.compile(
    r"(?i)\\b\\d{1,5}\\s+(?:[\\wÀ-ž.'’-]+\\s+){0,4}"
    r"(?:street|st\\.?|road|rd\\.?|avenue|ave\\.?|boulevard|blvd\\.?|lane|drive|way|"
    r"strasse|straße|platz|rue|chemin|route|calle|carrer|via|viale|ulica|ul\\.?|"
    r"cesta|ulice|utca|gata|gatan|veg(?:en)?|gade|kadun|tie|katu|улица|проспект|شارع)\\b"
)
AMBIGUOUS_PROPER_NAME = re.compile(
    r"(?<![.!?]\\s)(?<!^)\\b[A-ZÀ-ÖØ-Þ][\\wÀ-ÖØ-öø-ÿ'’-]+"
    r"\\s+[A-ZÀ-ÖØ-Þ][\\wÀ-ÖØ-öø-ÿ'’-]+\\b"
)
HONORIFIC = re.compile(
    r"(?i)\b(?:mr|mrs|ms|miss|dr|prof|professor|herr|frau|monsieur|"
    r"madame|signor|signora|señor|señora|señorita|sir|dame)\.?\s+"
    r"[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’-]+(?:\s+[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’-]+){0,2}"
)
PERSON_CONTEXT = re.compile(
    r"(?i)\b(?:contact|ask for|call|email|phone|written by|author|"
    r"submitted by|signed by|prepared by|according to|spoke to|"
    r"patient|customer|employee|recipient)\s*[:,-]?\s*"
    r"([A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’-]+(?:\s+[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’-]+){0,2})"
)
# Source metadata may explicitly carry privacy/sensitive flags.
FLAG_KEYS = ("privacy_flags", "sensitive_info", "sensitive_information",
             "personal_data", "pii", "is_pii", "has_personal_information")


@dataclass(frozen=True)
class PrivacyResult:
    accepted: bool
    status: str
    flags: tuple[str, ...]


def _metadata_flags(record: dict | None) -> list[str]:
    if not isinstance(record, dict):
        return []
    found = []
    for key in FLAG_KEYS:
        value = record.get(key)
        if value in (None, False, "", [], {}):
            continue
        if isinstance(value, (list, tuple, set)):
            found.extend(str(item) for item in value if item)
        elif value is True:
            found.append(key)
        elif isinstance(value, str) and value.strip().lower() not in {"false", "no", "none", "0", "clean"}:
            found.append(f"{key}:{value.strip()}")
        elif value not in (False, 0):
            found.append(key)
    return found


def screen_text(value: str, *, record: dict | None = None,
                uncertain_action: str = "quarantine") -> PrivacyResult:
    text = unicodedata.normalize("NFC", " ".join(str(value or "").split()))
    metadata_flags = _metadata_flags(record)
    if not text:
        return PrivacyResult(False, "rejected", ("empty_text",))
    high_confidence = (
        ("email", EMAIL.search(text)),
        ("url", URL.search(text)),
        ("ipv4", IPV4.search(text)),
        ("phone_or_long_identifier", LONG_NUMBER.search(text)),
        ("street_address", STREET.search(text) and HOUSE_NUMBER.search(text)),
        ("person_name_honorific", HONORIFIC.search(text)),
        ("person_name_context", PERSON_CONTEXT.search(text)),
    )
    rejected = [name for name, matched in high_confidence if matched]
    if rejected:
        return PrivacyResult(False, "rejected", tuple(sorted(set(rejected))))
    uncertain = list(metadata_flags)
    if AMBIGUOUS_PROPER_NAME.search(text):
        uncertain.append("ambiguous_proper_name")
    if uncertain:
        status = "quarantined" if uncertain_action == "quarantine" else "rejected"
        return PrivacyResult(False, status, tuple(sorted(set(uncertain))))
    return PrivacyResult(True, "clean", ())


def screen_record(record: dict, *, uncertain_action: str = "quarantine") -> PrivacyResult:
    provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
    merged = dict(provenance)
    for key in FLAG_KEYS:
        if key in record:
            merged[key] = record[key]
    return screen_text(record.get("text", ""), record=merged,
                       uncertain_action=uncertain_action)
