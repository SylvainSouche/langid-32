"""Pinned GreynirCorpus Copper/Silver treebank extraction.

Only the mechanically parsed Copper and Silver partitions are in scope. Gold
development/test files and the extra heading/short-sentence corpora are never
read by this adapter.
"""
from __future__ import annotations

import gzip
import re
from pathlib import Path

REVISION = "deb60c4b2775a4e0c709a6890c28678b913f44aa"
COPPER_FILES = tuple(f"psd/copper/copper{index:02d}.gz" for index in range(1, 11))
PARTITION_FILES = {
    "copper": COPPER_FILES[0],
    "silver": "psd/silver/silver.gz",
}
UPSTREAM = "https://github.com/mideind/GreynirCorpus"

TOKEN = re.compile(r"\(|\)|[^\s()]+")
PUNCTUATION = re.compile(r"^[.,;:!?…]+$")


def _record_blocks(stream):
    """Read one balanced PSD record at a time, bounding memory by one sentence."""
    buffer = []
    depth = 0
    for line_number, line in enumerate(stream, 1):
        if not buffer and not line.strip():
            continue
        buffer.append(line)
        for char in line:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    raise RuntimeError(f"Unbalanced Greynir PSD parentheses near line {line_number}")
        if depth == 0 and buffer:
            yield "".join(buffer)
            buffer.clear()
    if buffer or depth:
        raise RuntimeError("Greynir PSD file ended inside an incomplete tree record")


def _parse_sexpr(source: str):
    tokens = TOKEN.findall(source)
    position = 0

    def parse_node():
        nonlocal position
        if position >= len(tokens) or tokens[position] != "(":
            raise RuntimeError("Expected '(' in Greynir PSD record")
        position += 1
        node = []
        while position < len(tokens) and tokens[position] != ")":
            if tokens[position] == "(":
                node.append(parse_node())
            else:
                node.append(tokens[position])
                position += 1
        if position >= len(tokens):
            raise RuntimeError("Unclosed node in Greynir PSD record")
        position += 1
        return node

    result = parse_node()
    if position != len(tokens):
        raise RuntimeError("Trailing tokens after Greynir PSD record")
    return result


def _walk(node):
    if isinstance(node, list):
        yield node
        for child in node:
            if isinstance(child, list):
                yield from _walk(child)


def _find_node(node, label: str):
    for candidate in _walk(node):
        if candidate and candidate[0] == label:
            return candidate
    return None


def _field(node, label: str) -> str:
    found = _find_node(node, label)
    if found is None or len(found) < 2 or not isinstance(found[1], str):
        raise RuntimeError(f"Greynir PSD record is missing {label}")
    return found[1]


def _contains_heading(node) -> bool:
    return any(candidate and candidate[0] == "S-HEADING" for candidate in _walk(node))


def _terminals(node) -> list[str]:
    result = []
    if not isinstance(node, list) or not node:
        return result
    label = node[0] if isinstance(node[0], str) else ""
    if label in {"lemma", "exp_seg", "META", "ID-CORPUS", "ID-LOCAL", "URL", "COMMENT"}:
        return result
    children = node[1:]
    leading_tokens = []
    for child in children:
        if isinstance(child, str):
            value = child.strip()
            if value:
                leading_tokens.append(value)
        else:
            break
    if leading_tokens:
        if label == "grm":
            result.extend(token for token in leading_tokens if PUNCTUATION.fullmatch(token))
        else:
            result.extend(leading_tokens)
        return result
    for child in children:
        if isinstance(child, list):
            result.extend(_terminals(child))
    return result


def _detokenize(tokens: list[str]) -> str:
    text = " ".join(tokens)
    text = re.sub(r"\s+([,.;:!?…])", r"\1", text)
    text = re.sub(r"([([{])\s+", r"\1", text)
    text = re.sub(r"\s+([)\]}])", r"\1", text)
    text = re.sub(r"\s+([’'])", r"\1", text)
    return " ".join(text.split())


def iter_sentences(path: str | Path, partition: str, source_file: str | None = None):
    """Yield text and non-identifying provenance from one pinned LFS partition."""
    if partition not in PARTITION_FILES:
        raise ValueError(f"Unsupported Greynir partition: {partition}")
    source_file = source_file or PARTITION_FILES[partition]
    path = Path(path)
    with gzip.open(path, "rt", encoding="utf-8", errors="strict", newline=None) as stream:
        for record_number, block in enumerate(_record_blocks(stream), 1):
            tree = _parse_sexpr(block)
            sentence_tree = _find_node(tree, "S0")
            if sentence_tree is None or _contains_heading(sentence_tree):
                continue
            corpus_id = _field(tree, "ID-CORPUS")
            local_id = _field(tree, "ID-LOCAL")
            source_url = _field(tree, "URL")
            text = _detokenize(_terminals(sentence_tree))
            if not text:
                continue
            yield {
                "text": text,
                "group_id": source_url,
                "provenance": {
                    "source_file": source_file,
                    "source_partition": partition,
                    "source_record_number": record_number,
                    "source_corpus_id": corpus_id,
                    "source_local_id": local_id,
                    "source_document_url": source_url,
                    "publisher": "Miðeind ehf.",
                    "upstream_revision": REVISION,
                },
            }
