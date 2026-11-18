#!/usr/bin/env python3
"""Probe the Leipzig Corpora Collection REST API without retaining corpus text."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urljoin

import requests

API_ROOT = "https://api.wortschatz-leipzig.de/ws"
OPENAPI_URL = API_ROOT + "/v3/api-docs"
CORPORA_URL = API_ROOT + "/corpora/availableCorpora"
ISO3_TO_LANG = {
    "bul": "bg", "hrv": "hr", "ces": "cs", "cze": "cs", "dan": "da",
    "nld": "nl", "dut": "nl", "eng": "en", "est": "et", "fin": "fi",
    "fra": "fr", "fre": "fr", "deu": "de", "ger": "de", "ell": "el",
    "gre": "el", "hun": "hu", "gle": "ga", "ita": "it", "lav": "lv",
    "lit": "lt", "mlt": "mt", "pol": "pl", "por": "pt", "ron": "ro",
    "rum": "ro", "slk": "sk", "slo": "sk", "slv": "sl", "spa": "es",
    "swe": "sv", "nob": "nb", "nno": "nn", "rus": "ru", "jpn": "ja",
    "zho": "zh", "chi": "zh", "kor": "ko", "ara": "ar", "tur": "tr",
    "cat": "ca", "isl": "is",
}
HEADERS = {
    "User-Agent": "langid-32 Leipzig REST API research probe/1.0",
    "Accept": "application/json",
}


def get_json(session, url, params=None):
    response = session.get(url, params=params, headers=HEADERS, timeout=(20, 60))
    response.raise_for_status()
    return response.json(), response.url, response.status_code


def find_corpora(value):
    found = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item.get("corpusName"):
                found.append(item)
            else:
                found.extend(find_corpora(item))
    elif isinstance(value, dict):
        if value.get("corpusName"):
            found.append(value)
        else:
            for child in value.values():
                found.extend(find_corpora(child))
    unique = {}
    for item in found:
        unique[str(item["corpusName"])] = item
    return list(unique.values())


def language_for_corpus(name):
    prefix = str(name).split("_", 1)[0].lower()
    return ISO3_TO_LANG.get(prefix)


def operation(openapi, path):
    paths = openapi.get("paths", {})
    item = paths.get(path)
    if not isinstance(item, dict):
        return None
    return item.get("get")


def query_parameters(op, preferred_limit):
    params = {}
    for item in (op or {}).get("parameters", []):
        if item.get("in") == "query" and item.get("name") == "limit":
            params["limit"] = preferred_limit
    return params


def extract_words(value):
    words = []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        for item in value:
            words.extend(extract_words(item))
    elif isinstance(value, dict):
        for key in ("word", "words", "randomWord"):
            if key in value:
                words.extend(extract_words(value[key]))
    return [word for word in words if isinstance(word, str) and word.strip()]


def extract_sentences(value):
    sentences = []
    source_keys = set()
    def walk(item):
        if isinstance(item, dict):
            for key, child in item.items():
                lower = str(key).lower()
                if lower in {"sentence", "text", "sentencetext"} and isinstance(child, str):
                    sentences.append(child)
                if "source" in lower and isinstance(child, dict):
                    source_keys.update(str(k) for k in child.keys())
                elif "source" in lower and isinstance(child, list):
                    for entry in child:
                        if isinstance(entry, dict):
                            source_keys.update(str(k) for k in entry.keys())
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
    walk(value)
    # Preserve response order while removing duplicate fields surfaced by recursion.
    unique = list(dict.fromkeys(text for text in sentences if text.strip()))
    return unique, sorted(source_keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--probe-languages", default="bg,hr,cs,da,nl,en,et,fi,fr,de,el,hu,ga,it,lv,lt,mt,pl,pt,ro,sk,sl,es,sv,nb,nn,ru,ja,zh,ko,ar,tr,ca,is")
    parser.add_argument("--max-corpora-per-language", type=int, default=1)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    languages = {item.strip() for item in args.probe_languages.split(",") if item.strip()}
    session = requests.Session()
    report = {
        "status": "running",
        "api_root": API_ROOT,
        "openapi_url": OPENAPI_URL,
        "corpora_url": CORPORA_URL,
        "api_documentation_terms_label": "CC BY 4.0",
        "rights_note": (
            "The API documentation displays CC BY 4.0, but the Leipzig portal says corpus material "
            "is collected from selected publicly available sources and authors remain responsible "
            "for content. This probe does not treat the API label as clearance of underlying works."
        ),
        "corpus_count": 0,
        "target_corpora_by_language": {},
        "sentence_service_probes": [],
        "errors": [],
    }
    try:
        openapi, openapi_final_url, _ = get_json(session, OPENAPI_URL)
        (args.out / "openapi.json").write_text(
            json.dumps(openapi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        corpus_payload, corpora_final_url, _ = get_json(session, CORPORA_URL)
        (args.out / "available-corpora.json").write_text(
            json.dumps(corpus_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        corpora = find_corpora(corpus_payload)
        report["openapi_final_url"] = openapi_final_url
        report["corpora_final_url"] = corpora_final_url
        report["corpus_count"] = len(corpora)
        report["schema_names"] = sorted(openapi.get("components", {}).get("schemas", {}).keys())
        report["corpus_information_schema"] = openapi.get("components", {}).get("schemas", {}).get("CorpusInformation", {})
        by_language = {}
        for corpus in corpora:
            language = language_for_corpus(corpus.get("corpusName"))
            if language in languages:
                by_language.setdefault(language, []).append(corpus)
        selected = {}
        for language, entries in by_language.items():
            entries.sort(
                key=lambda item: (
                    int(item.get("numberOfSentences") or 0),
                    str(item.get("corpusName") or ""),
                ),
                reverse=True,
            )
            selected[language] = entries[:args.max_corpora_per_language]
        report["target_corpora_by_language"] = {
            language: [
                {
                    "corpusName": item.get("corpusName"),
                    "numberOfSentences": item.get("numberOfSentences"),
                    "numberOfTokens": item.get("numberOfTokens"),
                    "numberOfTypes": item.get("numberOfTypes"),
                    "dataBy": item.get("dataBy"),
                    "description": item.get("description"),
                    "thanksTo": item.get("thanksTo"),
                }
                for item in entries
            ]
            for language, entries in sorted(selected.items())
        }
        random_path = "/words/{corpusName}/randomword/"
        sentences_path = "/sentences/{corpusName}/sentences/{word}"
        random_op = operation(openapi, random_path)
        sentences_op = operation(openapi, sentences_path)
        report["randomword_operation"] = random_op
        report["sentences_operation"] = sentences_op
        if not random_op or not sentences_op:
            raise RuntimeError("OpenAPI spec does not expose the expected randomword and sentences operations")
        for language, entries in sorted(selected.items()):
            for corpus in entries:
                name = str(corpus["corpusName"])
                result = {
                    "language": language,
                    "corpusName": name,
                    "randomword_status": "pending",
                    "sentence_status": "not_attempted",
                    "sample_sentence_count": 0,
                }
                try:
                    random_url = API_ROOT + random_path.replace("{corpusName}", quote(name, safe=""))
                    random_payload, random_final_url, _ = get_json(
                        session, random_url, query_parameters(random_op, 1)
                    )
                    words = extract_words(random_payload)
                    result["randomword_status"] = "success" if words else "no_word_returned"
                    result["randomword_response_keys"] = sorted(random_payload.keys()) if isinstance(random_payload, dict) else []
                    if words:
                        word = words[0]
                        sentence_url = API_ROOT + sentences_path.replace(
                            "{corpusName}", quote(name, safe="")
                        ).replace("{word}", quote(word, safe=""))
                        sentence_payload, sentence_final_url, _ = get_json(
                            session, sentence_url, query_parameters(sentences_op, 10)
                        )
                        sentences, source_keys = extract_sentences(sentence_payload)
                        digest = hashlib.sha256("\n".join(sentences).encode("utf-8")).hexdigest()
                        result.update({
                            "sentence_status": "success" if sentences else "no_sentence_text_found",
                            "sample_sentence_count": len(sentences),
                            "sample_sentence_sha256": digest,
                            "sentence_response_keys": sorted(sentence_payload.keys()) if isinstance(sentence_payload, dict) else [],
                            "source_information_keys": source_keys,
                            "randomword_final_url": random_final_url,
                            "sentence_final_url": sentence_final_url,
                        })
                    time.sleep(0.15)
                except Exception as exc:
                    result["error"] = f"{type(exc).__name__}: {exc}"
                    report["errors"].append({"language": language, "corpusName": name, "error": result["error"]})
                report["sentence_service_probes"].append(result)
        report["languages_with_corpora"] = sorted(selected)
        report["languages_without_corpora"] = sorted(languages - set(selected))
        report["status"] = "probe_complete"
    except Exception as exc:
        report["status"] = "probe_failed"
        report["errors"].append({"stage": "api_probe", "error": f"{type(exc).__name__}: {exc}"})
        (args.out / "probe-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        raise
    (args.out / "probe-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "corpus_count": report["corpus_count"],
        "languages_with_corpora": report.get("languages_with_corpora", []),
        "languages_without_corpora": report.get("languages_without_corpora", []),
        "successful_sentence_probes": sum(x.get("sentence_status") == "success" for x in report["sentence_service_probes"]),
        "errors": len(report["errors"]),
    }, ensure_ascii=False, indent=2))
    if report["status"] != "probe_complete":
        sys.exit(1)


if __name__ == "__main__":
    main()
