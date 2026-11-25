"""Conservative multilingual PII screening shared by all acquisition adapters.

High-confidence identifiers are rejected. Ambiguous person-name candidates and
source-provided privacy flags are quarantined before any acquisition quota.
This deterministic screen is intentionally conservative, not a claim of
perfect multilingual named-entity recognition.
"""
from __future__ import annotations

import ipaddress
import re
import unicodedata
from dataclasses import dataclass

EMAIL = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Z]{2,}(?![A-Za-z0-9_.-])")
URL = re.compile(r"(?i)(?:https?://|www\.)\S+")
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
IPV6_CANDIDATE = re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![\w:])")
LONG_NUMBER = re.compile(r"(?<!\w)\d{9,}(?!\w)")
PHONE_CANDIDATE = re.compile(r"(?<!\w)\+?\d[\d\s()./-]{6,}\d(?!\w)")

STREET = re.compile(
    r"(?i)\b(?:street|st\.?|road|rd\.?|avenue|ave\.?|boulevard|blvd\.?|"
    r"lane|drive|way|strasse|straße|platz|rue|chemin|route|calle|carrer|"
    r"via|viale|ulica|ul\.?|cesta|ulice|utca|gata|gatan|veg(?:en)?|"
    r"gade|kadun|tie|katu|улица|проспект|شارع)\b"
)
HOUSE_NUMBER = re.compile(
    r"(?i)\b\d{1,5}\s+(?:[\wÀ-ž.'’-]+\s+){0,4}"
    r"(?:street|st\.?|road|rd\.?|avenue|ave\.?|boulevard|blvd\.?|lane|drive|way|"
    r"strasse|straße|platz|rue|chemin|route|calle|carrer|via|viale|ulica|ul\.?|"
    r"cesta|ulice|utca|gata|gatan|veg(?:en)?|gade|kadun|tie|katu|улица|проспект|شارع)\b"
)
STREET_TRAILING_NUMBER = re.compile(
    r"(?i)\b(?:street|st\.?|road|rd\.?|avenue|ave\.?|boulevard|blvd\.?|lane|drive|rue|chemin|route|calle|"
    r"carrer|via|viale|ulica|ul\.?|cesta|utca|gata|gatan|veg(?:en)?|gade|"
    r"kadun|tie|katu|улица|проспект|شارع)\s+(?:[\wÀ-ž.'’-]+\s+){0,4}\d{1,5}\b"
)
CJK_ADDRESS = re.compile(
    r"(?:〒\s*\d{3}-?\d{4}|"
    r"[一-龯]{2,}(?:都|道|府|県|市|区|町|村)[一-龯ぁ-んァ-ヶー0-9-]{0,20}\d{1,5}(?:[-丁目番地号]\d{0,5})*|"
    r"[一-龯]{2,}(?:省|市|区|县|縣|镇|鎮|路|街|大道|弄|巷)[一-龯0-9-]{0,20}\d{1,5}(?:号|號|弄|巷|室)?|"
    r"[\uac00-\ud7a3]{2,}(?:로|길)\s*\d{1,5}(?:번길|번지)?)"
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
CAPITALIZED_PAIR = re.compile(
    r"\b([A-ZÀ-ÖØ-ÞΑ-ΩΆΈΉΊΌΎΏА-ЯЁ][\wÀ-ÖØ-öø-ÿ'’-]+)\s+"
    r"([A-ZÀ-ÖØ-ÞΑ-ΩΆΈΉΊΌΎΏА-ЯЁ][\wÀ-ÖØ-öø-ÿ'’-]+)\b"
)
# Compact multilingual given-name lexicon; contextual and source-provided flags
# cover names not present here. Place names such as New York/United States are
# not treated as people merely because they are capitalized.
GIVEN_NAMES = {
    "aaron", "adam", "adrian", "agata", "agnes", "alain", "alberto", "alex",
    "alexander", "alexandra", "alice", "alicia", "amanda", "ana", "andrea",
    "andreas", "andrew", "anna", "anne", "anton", "antonio", "aria", "arno",
    "arthur", "barbara", "ben", "benjamin", "bruno", "carlos", "caroline",
    "catherine", "charles", "christian", "christina", "claire", "daniel",
    "david", "elena", "elias", "elise", "elisabeth", "ella", "emil", "emilia",
    "emma", "erik", "eva", "fabian", "felix", "francesca", "francisco",
    "frank", "frederik", "gabriel", "george", "giulia", "greta", "hanna",
    "hannah", "henri", "henrik", "hugo", "isabel", "isabella", "ivan",
    "jacob", "james", "jan", "jane", "jean", "johan", "johann", "john",
    "jonas", "jose", "julia", "julian", "karen", "karl", "katarina", "kate",
    "laura", "leon", "liam", "linda", "lisa", "luca", "lucas", "lucia",
    "lucy", "luis", "luka", "maria", "marie", "marina", "mark", "marta",
    "martin", "matej", "mathias", "matthew", "max", "michael", "michal",
    "mila", "miriam", "natalia", "nicolas", "nikola", "noah", "olga",
    "oliver", "oscar", "paul", "pavel", "peter", "pierre", "rafael",
    "raquel", "robert", "sara", "sarah", "sofia", "sophie", "stefan",
    "sven", "thomas", "tim", "tomas", "victor", "viktor", "william",
    "yann", "zuzana", "Αλέξανδρος", "Γιώργος", "Ελένη", "Μαρία",
    "Николай", "Александр", "Анна", "Мария",
}
FLAG_KEYS = (
    "privacy_flags", "sensitive_info", "sensitive_information",
    "personal_data", "pii", "is_pii", "has_personal_information",
)


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


def _has_ipv4(text: str) -> bool:
    for match in IPV4.finditer(text):
        try:
            if ipaddress.ip_address(match.group()).version == 4:
                return True
        except ValueError:
            continue
    return False


def _has_ipv6(text: str) -> bool:
    for match in IPV6_CANDIDATE.finditer(text):
        try:
            if ipaddress.ip_address(match.group()).version == 6:
                return True
        except ValueError:
            continue
    return False


def _has_phone_like(text: str) -> bool:
    for match in PHONE_CANDIDATE.finditer(text):
        raw = match.group()
        digits = re.sub(r"\D", "", raw)
        separators = sum(raw.count(char) for char in " -()./")
        if 9 <= len(digits) <= 15 and (separators >= 2 or "+" in raw):
            return True
    return False


def _has_ambiguous_name(text: str) -> bool:
    return any(
        match.group(1).casefold() in GIVEN_NAMES
        for match in CAPITALIZED_PAIR.finditer(text)
    )

def screen_text(value: str, *, record: dict | None = None,
                uncertain_action: str = "quarantine") -> PrivacyResult:
    text = unicodedata.normalize("NFC", " ".join(str(value or "").split()))
    metadata_flags = _metadata_flags(record)
    if not text:
        return PrivacyResult(False, "rejected", ("empty_text",))
    high_confidence = (
        ("email", EMAIL.search(text)),
        ("url", URL.search(text)),
        ("ipv4", _has_ipv4(text)),
        ("ipv6", _has_ipv6(text)),
        ("phone_or_long_identifier", _has_phone_like(text) or LONG_NUMBER.search(text)),
        ("street_address", (STREET.search(text) and (HOUSE_NUMBER.search(text) or STREET_TRAILING_NUMBER.search(text))) or CJK_ADDRESS.search(text)),
        ("person_name_honorific", HONORIFIC.search(text)),
        ("person_name_context", PERSON_CONTEXT.search(text)),
    )
    rejected = [name for name, matched in high_confidence if matched]
    if rejected:
        return PrivacyResult(False, "rejected", tuple(sorted(set(rejected))))
    uncertain = list(metadata_flags)
    if _has_ambiguous_name(text):
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
