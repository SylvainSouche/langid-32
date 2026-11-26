"""ParlaMint 4.0 TEI extraction with identity-bearing speaker metadata excluded."""
from __future__ import annotations

import re
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

SAFE_SPEAKER_ROLES = {"chair", "regular", "guest"}


def _safe_speaker_roles(utterance: ET.Element) -> list[str]:
    """Keep only the fixed non-identifying role vocabulary; discard speaker refs."""
    raw = utterance.attrib.get("ana", "").split()
    roles = {token.rsplit("#", 1)[-1].lower() for token in raw}
    return sorted(roles & SAFE_SPEAKER_ROLES)

SOURCES = {
    "is": {
        "source": "parlamint_is",
        "url": "https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1859/ParlaMint-IS.tgz?isAllowed=y&sequence=16",
        "md5": "59e4889f7f81b23cbdc96b827bea4a40",
        "prefix": "ParlaMint-IS_",
    },
    "sl": {
        "source": "parlamint_sl",
        "url": "https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1859/ParlaMint-SI.tgz?isAllowed=y&sequence=24",
        "md5": "a710c3869b2aaa89da3b9eaa3c7eb83f",
        "prefix": "ParlaMint-SI_",
    },
}


def iter_utterances(archive_path: str | Path, language: str):
    """Yield paragraph records from plain TEI session files; never expose speaker IDs/names."""
    if language not in SOURCES:
        raise ValueError(f"Unsupported ParlaMint language: {language}")
    meta = SOURCES[language]
    with tarfile.open(archive_path, "r:gz") as archive:
        members = [
            member for member in archive
            if member.isfile()
            and member.name.lower().endswith(".xml")
            and Path(member.name).name.startswith(meta["prefix"])
            and not member.name.lower().endswith(".ana.xml")
            and "/listperson" not in member.name.lower()
            and "/listorg" not in member.name.lower()
            and "/taxonomy" not in member.name.lower()
            and "/schema/" not in member.name.lower()
            and "/samples/" not in member.name.lower()
        ]
        if not members:
            raise RuntimeError(f"No plain ParlaMint {language.upper()} session XML files found")

        for member in members:
            session_id = Path(member.name).stem
            date_match = re.search(r"_(\d{4}-\d{2}-\d{2})(?:-|_|$)", session_id)
            if date_match is None:
                raise RuntimeError(f"ParlaMint session filename lacks a date: {member.name}")
            session_date = date_match.group(1)
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"Cannot read ParlaMint archive member {member.name}")
            try:
                stack = []
                for event, elem in ET.iterparse(stream, events=("start", "end")):
                    if event == "start":
                        stack.append(elem)
                        continue
                    if elem.tag != TEI + "u":
                        stack.pop()
                        continue
                    utterance_id = elem.attrib.get(XML_ID)
                    if not utterance_id:
                        raise RuntimeError(
                            f"ParlaMint utterance has no xml:id in {member.name}"
                        )
                    speaker_roles = _safe_speaker_roles(elem)
                    segments = elem.findall(".//" + TEI + "seg")
                    if segments:
                        for index, segment in enumerate(segments, 1):
                            value = " ".join("".join(segment.itertext()).split())
                            if value:
                                segment_id = segment.attrib.get(XML_ID) or f"{utterance_id}.seg{index}"
                                yield {
                                    "text": value,
                                    "group_id": session_id,
                                    "provenance": {
                                        "source_file": member.name,
                                        "session_id": session_id,
                                        "session_date": session_date,
                                        "publisher": "ParlaMint consortium / CLARIN.SI",
                                        "utterance_id": utterance_id,
                                        "segment_id": segment_id,
                                        "record_structure": "ParlaMint TEI utterance segment",
                                        **({"speaker_roles": speaker_roles} if speaker_roles else {}),
                                    },
                                }
                    else:
                        value = " ".join("".join(elem.itertext()).split())
                        if value:
                            yield {
                                "text": value,
                                "group_id": session_id,
                                "provenance": {
                                    "source_file": member.name,
                                    "session_id": session_id,
                                    "session_date": session_date,
                                    "publisher": "ParlaMint consortium / CLARIN.SI",
                                    "utterance_id": utterance_id,
                                    "record_structure": "ParlaMint TEI utterance",
                                    **({"speaker_roles": speaker_roles} if speaker_roles else {}),
                                },
                            }
                    if len(stack) > 1:
                        stack[-2].remove(elem)
                    elem.clear()
                    stack.pop()
            finally:
                stream.close()
