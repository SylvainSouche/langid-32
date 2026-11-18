#!/usr/bin/env python3
"""Acquire bounded waiting-source samples with row-level provenance and rights status."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import heapq
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import unicodedata
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

EMAIL = re.compile(r"(?i)\\b[\\w.+-]+@[\\w.-]+\\.[A-Z]{2,}\\b")
URL = re.compile(r"(?i)(https?://|www\\.)\\S+")
NUMBER = re.compile(r"\\d{9,}")
IPV4 = re.compile(r"(?<![\\w.])(?:\\d{1,3}\\.){3}\\d{1,3}(?![\\w.])")


def clean(value, language):
    text = " ".join(unicodedata.normalize("NFC", str(value or "")).split())
    letters = sum(char.isalpha() for char in text)
    if (len(text) < 40 or len(text) > 12000 or letters < 25
            or letters / len(text) < 0.45 or EMAIL.search(text)
            or URL.search(text) or NUMBER.search(text) or IPV4.search(text)):
        return None
    if language == "ar" and sum("\\u0600" <= char <= "\\u06ff" for char in text) < max(10, letters * 0.35):
        return None
    return text


def fetch(url, destination):
    last_error = None
    for attempt in range(4):
        digest = hashlib.sha256()
        size = 0
        try:
            request = Request(url, headers={"User-Agent": "langid-32-source-audit/1"})
            with urlopen(request, timeout=240) as response, destination.open("wb") as output:
                expected = int(response.headers.get("Content-Length") or 0)
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
                    digest.update(block)
                    size += len(block)
            if expected and size != expected:
                raise IOError(f"incomplete download: {size}/{expected} bytes")
            return {"url": url, "bytes": size, "sha256": digest.hexdigest()}
        except Exception as exc:
            last_error = exc
            destination.unlink(missing_ok=True)
            if attempt < 3:
                time.sleep(5 * (attempt + 1))
    raise last_error


def resolve_hf_revision(repository):
    url = f"https://huggingface.co/api/datasets/{repository}"
    request = Request(url, headers={"User-Agent": "langid-32-source-audit/1"})
    with urlopen(request, timeout=60) as response:
        info = json.load(response)
    revision = info.get("sha")
    if not revision or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise RuntimeError(f"Could not resolve immutable revision for {repository}")
    return revision


def main():
    csv.field_size_limit(10_000_000)
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    temp_root = Path(tempfile.mkdtemp())
    output_root = Path(args.out)
    output_root.mkdir(parents=True, exist_ok=True)
    heaps = defaultdict(list)
    seen = defaultdict(set)
    downloads = []
    notes = []
    scanned = Counter()
    revisions = {}

    def source_metadata(source):
        if source.startswith("temu_cc0:"):
            return (f"catalan_CC0_sentences@git:{revisions.get('temu', 'unresolved')}",
                    "CC0-1.0 (repository claim)", "text extracted from TeMU-BSC constituent file",
                    "hold_constituent_rights_unverified")
        if source.startswith("catalan_dpo_v2:"):
            return (f"Catalan-DPO-V2@{revisions.get('dpo', 'unresolved')}",
                    "Apache-2.0 (dataset-card claim)", "assistant dialogue text from Catalan-DPO-V2",
                    "hold_underlying_dialogue_rights_unverified")
        if source.startswith("bsc_legal:"):
            filename = source.split(":", 1)[1]
            item = next((row for row in downloads if row["url"].endswith(filename)), None)
            revision = f"sha256:{item['sha256']}" if item else "file-hash-unresolved"
            return (f"Legal_Catalan_Spanish_Corpus@{revision}",
                    "CC-BY-4.0 (repository claim)", "text extracted from BSC-LT legal-corpus constituent",
                    "hold_constituent_terms_and_article_rights_unverified")
        if source == "igc":
            item = next((row for row in downloads if "20.500.12537/381" in row["url"]), None)
            revision = f"sha256:{item['sha256']}" if item else "archive-hash-unresolved"
            return (f"IGC2024-Filtered-1@{revision}", "CC-BY-4.0 (corpus-level claim)",
                    "Icelandic corpus text; underlying source-work rights require review",
                    "hold_source_document_rights_unverified")
        if source == "greynir":
            item = next((row for row in downloads if "20.500.12537/119" in row["url"]), None)
            revision = f"sha256:{item['sha256']}" if item else "archive-hash-unresolved"
            return (f"GreynirCorpus-1.1@{revision}", "CC-BY-4.0 (corpus-level claim)",
                    "Icelandic news/government corpus text; underlying article rights require review",
                    "hold_source_article_rights_unverified")
        if source.startswith("maalfrid2026:"):
            language = source.rsplit(":", 1)[1]
            suffix = "nob.tar" if language == "nb" else "nno.tar"
            item = next((row for row in downloads if row["url"].endswith(suffix)), None)
            revision = f"sha256:{item['sha256']}" if item else "archive-hash-unresolved"
            return (f"Maalfrid-2026-{language}@{revision}", "NLOD-2.0;ODC-By-1.0(database rights)",
                    "text extracted from Målfrid 2026 corpus", "hold_database_and_third_party_content_review")
        if source == "korean_wikipedia_20231101":
            return (f"wikipedia-20231101.ko@{revisions.get('wikipedia', 'unresolved')}",
                    "CC-BY-SA-4.0;GFDL-1.3", "paragraph extracted from a Korean Wikipedia article",
                    "hold_share_alike_and_attribution_review")
        if source.startswith("fineweb2:"):
            return (f"FineWeb-2-{source.split(':', 1)[1]}@{revisions.get('fineweb2', 'unresolved')}",
                    "ODC-By-1.0;underlying-crawled-text-rights-unresolved",
                    "web-crawl document text", "hold_underlying_web_text_rights_unresolved")
        if source.startswith("un_arabic_english_filtered:"):
            return (f"UN-Arabic-English-Filtered@{revisions.get('un_arabic', 'unresolved')}",
                    "UNVERIFIED (HF derivative card reports CC-BY-4.0)",
                    "Arabic text from a UN-derived dataset; upstream source terms unverified",
                    "hold_upstream_UN_terms_unverified")
        raise ValueError(f"No source metadata mapping for {source}")

    def add(language, source, value, group_id="", provenance=None):
        text = clean(value, language)
        if not text:
            return
        key = (language, source)
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        scanned[key] += 1
        if text_hash in seen[key]:
            return
        release, licence, origin, rights_status = source_metadata(source)
        source_record_id = str(group_id or text_hash)
        prov = dict(provenance or {})
        prov.update({
            "source_record_id": source_record_id,
            "rights_status": rights_status,
            "privacy_flags": [],
        })
        record = {
            "text": text,
            "language": language,
            "source": source,
            "source_release": release,
            "group_id": f"{source}:{source_record_id}",
            "licence_id": licence,
            "text_origin": origin,
            "provenance": prov,
        }
        rank = int(text_hash, 16)
        heap = heaps[key]
        if len(heap) < 50000:
            heapq.heappush(heap, (-rank, record, text_hash))
            seen[key].add(text_hash)
        elif rank < -heap[0][0]:
            removed = heapq.heapreplace(heap, (-rank, record, text_hash))
            seen[key].remove(removed[2])
            seen[key].add(text_hash)

    def scan(root, language, source):
        for path in ([root] if root.is_file() else root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.name if root.is_file() else path.relative_to(root).as_posix()
            try:
                if path.name.endswith(".jsonl") or path.name.endswith(".jsonl.gz"):
                    opener = gzip.open if path.name.endswith(".gz") else open
                    with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
                        for index, line in enumerate(stream, 1):
                            try:
                                item = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            if isinstance(item, dict):
                                values = []
                                for key in ("fulltext", "text", "content", "sentence", "body", "ca", "text_ar"):
                                    value = item.get(key)
                                    if isinstance(value, str):
                                        values.append(value)
                                    elif isinstance(value, list):
                                        values.extend(part for part in value if isinstance(part, str))
                                if not values:
                                    values = [value for value in item.values()
                                              if isinstance(value, str) and len(value) > 60]
                                document_id = (item.get("doc_id") or item.get("doc_hash")
                                               or item.get("document_id") or item.get("id")
                                               or f"{relative}:line:{index}")
                                provenance = {
                                    "source_file": relative,
                                    "source_record_index": index,
                                    "source_document_id": str(document_id),
                                }
                                for key in ("url", "source_url", "canonical_url", "title",
                                            "author", "date", "published", "publisher", "domain"):
                                    value = item.get(key)
                                    if isinstance(value, (str, int, float)) and value != "":
                                        provenance[key] = value
                                for value in values:
                                    add(language, source, value, str(document_id), provenance)
                            elif isinstance(item, str):
                                add(language, source, item, f"{relative}:line:{index}",
                                    {"source_file": relative, "source_record_index": index})
                elif path.suffix.lower() in (".txt", ".tsv", ".csv"):
                    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
                    with path.open(encoding="utf-8", errors="replace", newline="") as stream:
                        reader = csv.reader(stream, delimiter=delimiter)
                        for index, row in enumerate(reader, 1):
                            if row:
                                add(language, source, row[0], f"{relative}:row:{index}",
                                    {"source_file": relative, "source_record_index": index,
                                     "source_document_id": None})
            except Exception as exc:
                notes.append(f"{path}: {type(exc).__name__}: {exc}")

    try:
        if args.source == "catalan":
            temu_root = temp_root / "temu"
            subprocess.run(["git", "clone", "--depth", "1",
                            "https://github.com/TeMU-BSC/catalan_CC0_sentences.git",
                            str(temu_root)], check=True)
            revisions["temu"] = subprocess.check_output(
                ["git", "-C", str(temu_root), "rev-parse", "HEAD"], text=True
            ).strip()
            files = [
                "catalan_government_crawling_frases_seleccionades_filtrades.txt",
                "datasets_sentences.tsv", "edited_generated_selected_chatbot.txt",
                "edited_selected_chatbot.txt", "frases_spl.txt",
                "generades_spl_seleccionades.txt", "more_intents.txt",
                "plantilles_intents.txt", "literatura.txt",
                "sentences_from_xitxat_corpus.txt", "sentences_from_xitxat_corpus2.txt",
                "wikidata_sentences.txt",
            ]
            for filename in files:
                if (temu_root / filename).exists():
                    scan(temu_root / filename, "ca", f"temu_cc0:{filename}")
            try:
                revisions["dpo"] = resolve_hf_revision("catallama/Catalan-DPO-V2")
                from datasets import load_dataset
                dataset = load_dataset("catallama/Catalan-DPO-V2", split="train",
                                        streaming=True, revision=revisions["dpo"])
                for index, item in enumerate(dataset):
                    row_id = str(item.get("id") or index)
                    base_provenance = {"dataset_repo": "catallama/Catalan-DPO-V2",
                                       "repo_commit": revisions["dpo"], "dataset_row_id": row_id}
                    for message in item.get("messages", []) or []:
                        if isinstance(message, dict) and message.get("role") == "assistant":
                            add("ca", "catalan_dpo_v2:messages", message.get("content"),
                                row_id, {**base_provenance, "field": "messages"})
                    add("ca", "catalan_dpo_v2:chosen", item.get("chosen"),
                        row_id, {**base_provenance, "field": "chosen"})
                    if index >= 23499:
                        break
            except Exception as exc:
                notes.append("DPO: " + repr(exc))
            base = "https://huggingface.co/datasets/BSC-LT/Legal_Catalan_Spanish_Parallel_Corpus/resolve/main/"
            for filename in ("dogc_ca-es.tsv", "legal_ca-es_dataset_clean.tsv", "apdcat_ca-es.docs.jsonl"):
                path = temp_root / filename
                try:
                    downloads.append(fetch(base + filename, path))
                    scan(path, "ca", "bsc_legal:" + filename)
                except Exception as exc:
                    notes.append(filename + ": " + repr(exc))

        elif args.source == "icelandic":
            for name, url, is_zip in [
                ("igc", "https://repository.clarin.is/repository/xmlui/bitstream/handle/20.500.12537/381/igc2024-1-filtered.zip?sequence=1&isAllowed=y", True),
                ("greynir", "https://repository.clarin.is/repository/xmlui/bitstream/handle/20.500.12537/119/GreynirCorpus-1.1.tar.gz?sequence=1&isAllowed=y", False),
            ]:
                archive = temp_root / (name + (".zip" if is_zip else ".tgz"))
                try:
                    downloads.append(fetch(url, archive))
                    extracted = temp_root / name
                    extracted.mkdir()
                    if is_zip:
                        with zipfile.ZipFile(archive) as source_zip:
                            source_zip.extractall(extracted)
                    else:
                        with tarfile.open(archive, "r:gz") as source_tar:
                            source_tar.extractall(extracted, filter="data")
                    scan(extracted, "is", name)
                except Exception as exc:
                    notes.append(name + ": " + repr(exc))

        elif args.source == "norwegian":
            for language, code in (("nb", "nob"), ("nn", "nno")):
                archive = temp_root / (language + ".tar")
                url = f"https://www.nb.no/sbfil/tekst/maalfrid_2026/maalfrid_2026_{code}.tar"
                try:
                    downloads.append(fetch(url, archive))
                    extracted = temp_root / language
                    extracted.mkdir()
                    with tarfile.open(archive) as source_tar:
                        source_tar.extractall(extracted, filter="data")
                    scan(extracted, language, "maalfrid2026:" + language)
                except Exception as exc:
                    notes.append(language + ": " + repr(exc))

        elif args.source == "korean":
            revisions["wikipedia"] = resolve_hf_revision("wikimedia/wikipedia")
            from datasets import load_dataset
            dataset = load_dataset("wikimedia/wikipedia", "20231101.ko", split="train",
                                   streaming=True, revision=revisions["wikipedia"])
            for index, item in enumerate(dataset):
                page_id = str(item.get("id") or index)
                provenance = {"dataset_repo": "wikimedia/wikipedia",
                               "repo_commit": revisions["wikipedia"], "page_id": page_id}
                for key in ("url", "title"):
                    if item.get(key):
                        provenance[key] = item[key]
                for paragraph in re.split(r"(?<=[.!?。！？])\s+|\n+", item.get("text", "")):
                    add("ko", "korean_wikipedia_20231101", paragraph, page_id, provenance)
                if index >= 499999:
                    break
            notes.append("Wikimedia Korean dump: CC BY-SA/GFDL attribution and share-alike obligations retained; release hold remains.")

        elif args.source == "fineweb2":
            revisions["fineweb2"] = resolve_hf_revision("HuggingFaceFW/fineweb-2")
            from datasets import load_dataset
            for language, config in (("ca", "cat_Latn"), ("is", "isl_Latn")):
                try:
                    dataset = load_dataset("HuggingFaceFW/fineweb-2", config, split="train",
                                           streaming=True, revision=revisions["fineweb2"])
                    source = "fineweb2:" + config
                    for index, item in enumerate(dataset):
                        document_id = str(item.get("id") or item.get("url") or index)
                        provenance = {"dataset_repo": "HuggingFaceFW/fineweb-2",
                                      "repo_commit": revisions["fineweb2"],
                                      "document_id": document_id}
                        for key in ("url", "date", "dump", "language_score"):
                            if item.get(key) is not None:
                                provenance[key] = item[key]
                        add(language, source, item.get("text"), document_id, provenance)
                        if index >= 499999:
                            break
                    notes.append(config + ": underlying web-text rights unresolved; technical candidates only.")
                except Exception as exc:
                    notes.append(config + ": " + repr(exc))

        elif args.source == "arabic":
            revisions["un_arabic"] = resolve_hf_revision("ymoslem/UN-Arabic-English-Filtered")
            from datasets import load_dataset
            dataset = load_dataset("ymoslem/UN-Arabic-English-Filtered", split="train",
                                   streaming=True, revision=revisions["un_arabic"])
            for index, item in enumerate(dataset):
                document_id = str(item.get("id") or item.get("url") or index)
                provenance = {"dataset_repo": "ymoslem/UN-Arabic-English-Filtered",
                              "repo_commit": revisions["un_arabic"],
                              "source_record_id": document_id}
                for key in ("url", "date", "title", "source"):
                    if item.get(key) is not None:
                        provenance[key] = item[key]
                add("ar", "un_arabic_english_filtered:text_ar",
                    item.get("text_ar"), document_id, provenance)
                if index % 100000 == 0:
                    print(f"Arabic pairs streamed: {index}", flush=True)
            notes.append("HF derivative reports CC BY 4.0; upstream UN reuse terms remain unverified.")

        else:
            raise ValueError(f"Unknown source group: {args.source}")

        selected = []
        stats = Counter()
        for (language, source), heap in sorted(heaps.items()):
            items = [item[1] for item in heap]
            selected.extend(items)
            stats[f"{language}|{source}|screened"] = scanned[(language, source)]
            stats[f"{language}|{source}|unique_sampled"] = len(items)

        seen_text = set()
        deduplicated = []
        for item in selected:
            key = (item["language"], hashlib.sha256(item["text"].encode("utf-8")).hexdigest())
            if key in seen_text:
                stats[item["language"] + ":cross_source_sample_duplicates"] += 1
                continue
            seen_text.add(key)
            deduplicated.append(item)

        output_path = output_root / "candidates.jsonl"
        with output_path.open("w", encoding="utf-8", newline="\n") as output:
            for item in deduplicated:
                output.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")

        counts = Counter((item["language"], item["source"]) for item in deduplicated)
        report = {
            "source_group": args.source,
            "downloads": downloads,
            "source_revisions": revisions,
            "counts": {"|".join(key): value for key, value in sorted(counts.items())},
            "stats": dict(stats),
            "total_selected": len(deduplicated),
            "notes": notes,
            "stats_note": "Screened counts include repeated texts; deterministic hash-priority sample capped at 50k per source; cross-source dedup applies only to sampled records.",
            "status": "automated candidate only; all source rights statuses remain held or conditional until reviewed",
        }
        (output_root / "manifest.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
