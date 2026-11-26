"""MaCoCu 2.0 monolingual XML paragraph extraction.

The adapter preserves source/document/paragraph provenance and paragraph quality
metadata. It never emits document titles or other author/contributor metadata.
Sensitive paragraphs and headings are filtered by the acquisition caller before
privacy screening and exact source/language quota accounting.
"""
from __future__ import annotations

import math
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCES = {
    "hr": {
        "source": "macocu_hr_2",
        "url": "https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1806/MaCoCu-hr-2.0.xml.zip?isAllowed=y&sequence=3",
        "md5": "fea674896b4f36c8cc59fc0b4c3976a7",
        "sha256": "6ea86d64c737cdcb99711ad91d37a6fd659a71ae034f9a56cfdae24182364679",
        "xml_member": "MaCoCu-hr-2.0.xml",
    },
    "mt": {
        "source": "macocu_mt_2",
        "url": "https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1803/MaCoCu-mt-2.0.xml.zip?isAllowed=y&sequence=3",
        "md5": "e7dd66e2df6c3e832680e6407a6a2565",
        "sha256": "56cb0058d2d23609821d115b6a8221ddac77217558631e1afce2f8355543045e",
        "xml_member": "MaCoCu-mt-2.0.xml",
    },
    "sl": {
        "source": "macocu_sl_2",
        "url": "https://www.clarin.si/repository/xmlui/bitstream/handle/11356/1795/MaCoCu-sl-2.0.xml.zip?isAllowed=y&sequence=9",
        "md5": "b2c73ad9a16de41790add26ab588afa0",
        "sha256": "638a0ff6d68211293dd2b54a6da2bd52a190f37480474c9b8efb20aa27d7c47f",
        "xml_member": "MaCoCu-sl-2.0.xml",
    },
}

FALSE_VALUES = {"", "0", "false", "no", "none", "null", "[]", "{}", "clean"}
TRUE_VALUES = {"1", "true", "yes", "y"}
SENSITIVE_ATTRIBUTE_TOKENS = ("sensitive", "biroamer", "personal_info", "personal_data", "pii")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _attrs(element: ET.Element) -> dict[str, str]:
    return {key.rsplit("}", 1)[-1].lower().replace("-", "_"): value
            for key, value in element.attrib.items()}


def _required(attrs: dict[str, str], *names: str) -> str:
    for name in names:
        value = attrs.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    raise RuntimeError(f"MaCoCu paragraph is missing required attribute: {'/'.join(names)}")


def _boolean(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise RuntimeError(f"Unrecognized MaCoCu {field} flag value: {value!r}")


def _sensitive_flag(attrs: dict[str, str]) -> bool:
    matches = [(key, value) for key, value in attrs.items()
               if any(token in key for token in SENSITIVE_ATTRIBUTE_TOKENS)]
    if len(matches) != 1:
        raise RuntimeError(
            "MaCoCu paragraph must expose exactly one sensitive-information flag; "
            f"found {[key for key, _ in matches]}"
        )
    key, value = matches[0]
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES or normalized in FALSE_VALUES:
        return normalized in TRUE_VALUES
    # BiROAMer entity lists are empty when no sensitive entity was detected.
    return bool(normalized)


def iter_paragraphs(archive_path: str | Path, language: str):
    """Yield all MaCoCu paragraphs with flags; callers apply filters before quotas."""
    if language not in SOURCES:
        raise ValueError(f"Unsupported MaCoCu language: {language}")
    meta = SOURCES[language]
    with zipfile.ZipFile(archive_path) as archive:
        matches = [name for name in archive.namelist()
                   if Path(name).name == meta["xml_member"]]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one {meta['xml_member']} in MaCoCu {language.upper()} archive; "
                f"found {matches[:5]}"
            )
        with archive.open(matches[0], "r") as stream:
            stack: list[ET.Element] = []
            document: dict[str, str] | None = None
            for event, element in ET.iterparse(stream, events=("start", "end")):
                tag = _local_name(element.tag)
                if event == "start":
                    stack.append(element)
                    if tag == "doc":
                        document_attrs = _attrs(element)
                        document = {
                            "id": _required(document_attrs, "id", "doc_id", "document_id"),
                            "url": _required(document_attrs, "url"),
                        }
                    continue

                if tag == "p":
                    if document is None:
                        raise RuntimeError("MaCoCu paragraph occurs outside a document")
                    attrs = _attrs(element)
                    paragraph_id = _required(attrs, "id", "paragraph_id")
                    language_value = attrs.get("lang") or attrs.get("language")
                    paragraph_language = language_value.strip().lower() if language_value else None
                    quality = _required(attrs, "quality", "quality_label")
                    fluency_raw = _required(attrs, "lm_score", "fluency", "fluency_score")
                    try:
                        fluency = float(fluency_raw)
                    except ValueError as exc:
                        raise RuntimeError(f"Invalid MaCoCu fluency score: {fluency_raw!r}") from exc
                    if not math.isfinite(fluency):
                        raise RuntimeError(f"Non-finite MaCoCu fluency score: {fluency_raw!r}")
                    heading_value = attrs.get("heading", attrs.get("is_heading"))
                    heading = _boolean(heading_value, "heading") if heading_value is not None else False
                    sensitive = _sensitive_flag(attrs)
                    text = " ".join("".join(element.itertext()).split())
                    if text:
                        yield {
                            "text": text,
                            "group_id": document["id"],
                            "provenance": {
                                "source_file": matches[0],
                                "source_document_id": document["id"],
                                "source_paragraph_id": paragraph_id,
                                "source_document_url": document["url"],
                                "paragraph_quality": quality,
                                "paragraph_fluency": fluency,
                                "paragraph_language": paragraph_language,
                                "paragraph_heading": heading,
                                "paragraph_sensitive": sensitive,
                            },
                        }
                    if len(stack) > 1:
                        stack[-2].remove(element)
                    element.clear()
                elif tag == "doc":
                    document = None
                    if len(stack) > 1:
                        stack[-2].remove(element)
                    element.clear()
                stack.pop()
