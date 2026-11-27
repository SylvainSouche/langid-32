"""Pinned GreynirCorpus Copper/Silver treebank extraction.

Only the mechanically parsed Copper and Silver partitions are in scope. Gold
development/test files and the extra heading/short-sentence corpora are never
read by this adapter.
"""
from __future__ import annotations

import gzip
import json
import re
import unicodedata
from pathlib import Path

REVISION = "deb60c4b2775a4e0c709a6890c28678b913f44aa"
COPPER_FILES = tuple(f"psd/copper/copper{index:02d}.gz" for index in range(1, 11))
PARTITION_FILES = {
    "copper": COPPER_FILES[0],
    "silver": "psd/silver/silver.gz",
}
LFS_POINTERS = {
    "psd/copper/copper01.gz": ("09726a43b1a4b025960f221db49a6433337667ae42eb88df11d4e2565db724e0", 206750987),
    "psd/copper/copper02.gz": ("fc84fb46d1e71fcdb4a192fdd8dfb811e9fa9183e4bbfaa962e8d7a3f7b1a5cf", 207327631),
    "psd/copper/copper03.gz": ("708269274c4610266d986f929fa922931d8a07cb871f271bbdeb889f70b559e7", 206664163),
    "psd/copper/copper04.gz": ("28a952a0a9471ce68af7d1f68b35227f88067261070e81064c818d25248807f3", 206643909),
    "psd/copper/copper05.gz": ("ebfd66098580adf7bfb0b2e9d6df3a73af7997e77aa3aaf123f71e57f2652d2a", 206684798),
    "psd/copper/copper06.gz": ("b1288f576c456933edc020d7bc32288c1d40992ab51c6a6c4ed458a28b586c7f", 206303316),
    "psd/copper/copper07.gz": ("f0877ef4ba19009749a370d417612a4f7723b3602451cec4843060bc0107bdec", 206406085),
    "psd/copper/copper08.gz": ("b2d8e513df3f7d70800243c0d51b4f11241b0e7ea52e53b1d47232b402403470", 206286129),
    "psd/copper/copper09.gz": ("8b3eb1c2e385e7c2abeb2cfba85e5f605c351e82df67e7aa19bec755fbe1bbe7", 206533799),
    "psd/copper/copper10.gz": ("3abdbd0d84c491207ba18531a593f4117e63b4c7605f1323f08fe2e494b71403", 206029600),
    "psd/silver/silver.gz": ("e0117d5231b0255a9b339b2d638df54414ce940777b4412492f5794cecf443dc", 134779431),
}
UPSTREAM = "https://github.com/mideind/GreynirCorpus"

TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|\\(|\\)|[^\\s()]+')
def is_punctuation_token(value: str) -> bool:
    return bool(value) and all(unicodedata.category(char).startswith("P") for char in value)


def _record_blocks(stream):
    """Read one balanced PSD record at a time, bounding memory by one sentence."""
    buffer = []
    depth = 0
    in_string = False
    escaped = False
    for line_number, line in enumerate(stream, 1):
        if not buffer and not line.strip():
            continue
        buffer.append(line)
        for char in line:
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    raise RuntimeError(f"Unbalanced Greynir PSD parentheses near line {line_number}")
        if depth == 0 and not in_string and buffer:
            yield "".join(buffer)
            buffer.clear()
    if buffer or depth or in_string:
        raise RuntimeError("Greynir PSD file ended inside an incomplete tree record or quoted string")


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
                token = tokens[position]
                node.append(json.loads(token) if token.startswith('"') else token)
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
            result.extend(token for token in leading_tokens if is_punctuation_token(token))
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
            local_id_node = _find_node(tree, "ID-LOCAL")
            local_id = (
                local_id_node[1]
                if local_id_node is not None and len(local_id_node) > 1
                and isinstance(local_id_node[1], str) else None
            )
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
                    **({"source_local_id": local_id} if local_id else {}),
                    "source_document_url": source_url,
                    "publisher": "Miðeind ehf.",
                    "upstream_revision": REVISION,
                },
            }
