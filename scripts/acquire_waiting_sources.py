#!/usr/bin/env python3
"""Acquire bounded waiting-source samples with row-level provenance and rights status."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
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
    """Download with resumable byte ranges; verify the complete payload hash."""
    last_error = None
    expected = 0
    for attempt in range(12):
        try:
            if not expected:
                head = Request(url, method="HEAD", headers={"User-Agent": "langid-32-source-audit/1"})
                try:
                    with urlopen(head, timeout=60) as response:
                        expected = int(response.headers.get("Content-Length") or 0)
                except Exception:
                    expected = 0
            offset = destination.stat().st_size if destination.exists() else 0
            headers = {"User-Agent": "langid-32-source-audit/1"}
            if offset:
                headers["Range"] = f"bytes={offset}-"
            request = Request(url, headers=headers)
            with urlopen(request, timeout=300) as response:
                if offset and response.status != 206:
                    raise IOError(f"server did not honour Range at byte {offset}: HTTP {response.status}")
                if offset:
                    content_range = response.headers.get("Content-Range", "")
                    if not content_range.startswith(f"bytes {offset}-"):
                        raise IOError(f"unexpected Content-Range {content_range!r} at offset {offset}")
                elif response.status != 200:
                    raise IOError(f"unexpected HTTP {response.status}")
                with destination.open("ab" if offset else "wb") as output:
                    while True:
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        output.write(block)
            size = destination.stat().st_size
            if expected and size != expected:
                raise IOError(f"incomplete download: {size}/{expected} bytes")
            digest = hashlib.sha256()
            with destination.open("rb") as source:
                for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
                    digest.update(block)
            return {"url": url, "bytes": size, "sha256": digest.hexdigest()}
        except Exception as exc:
            last_error = exc
            if attempt < 11:
                time.sleep(min(60, 3 * (attempt + 1)))
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
    retained = defaultdict(list)
    seen = defaultdict(set)
    max_per_source = 20000
    downloads = []
    notes = []
    scanned = Counter()
    revisions = {}

    def source_metadata(source):
        if source.startswith("temu_cc0:"):
            return (f"catalan_CC0_sentences@git:{revisions.get('temu', 'unresolved')}",
                    "CC0-1.0 (repository claim)", "text extracted from TeMU-BSC constituent file",
                    "declared_cc0_accepted")
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
                    "declared_cc_by_4_0_accepted")
        if source == "igc":
            item = next((row for row in downloads if "20.500.12537/381" in row["url"]), None)
            revision = f"sha256:{item['sha256']}" if item else "archive-hash-unresolved"
            return (f"IGC2024-Filtered-1@{revision}", "CC-BY-4.0 (corpus-level claim)",
                    "Icelandic corpus text; underlying source-work rights require review",
                    "declared_cc_by_4_0_accepted")
        if source == "greynir":
            item = next((row for row in downloads if "20.500.12537/119" in row["url"]), None)
            revision = f"sha256:{item['sha256']}" if item else "archive-hash-unresolved"
            return (f"GreynirCorpus-1.1@{revision}", "CC-BY-4.0 (corpus-level claim)",
                    "Icelandic news/government corpus text; underlying article rights require review",
                    "declared_cc_by_4_0_accepted")
        if source.startswith("maalfrid2026:"):
            language = source.rsplit(":", 1)[1]
            suffix = "nob.tar" if language == "nb" else "nno.tar"
            item = next((row for row in downloads if row["url"].endswith(suffix)), None)
            revision = f"sha256:{item['sha256']}" if item else "archive-hash-unresolved"
            return (f"Maalfrid-2026-{language}@{revision}", "NLOD-2.0;ODC-By-1.0(database rights)",
                    "text extracted from Målfrid 2026 corpus", "hold_database_and_third_party_content_review")
        if source == "korean_wikipedia_20231101":
            return (f"wikipedia-20231101.ko@{revisions.get('wikipedia', 'unresolved')}",
                    "MIXED: CC-BY-SA-3.0 / CC-BY-SA-4.0; GFDL (unversioned; imported-content exceptions possible)", "paragraph extracted from a Korean Wikipedia article",
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
        if text_hash in seen[key] or len(retained[key]) >= max_per_source:
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
        retained[key].append(record)
        seen[key].add(text_hash)

    def scan(root, language, source):
        key = (language, source)
        for path in ([root] if root.is_file() else root.rglob("*")):
            if len(retained[key]) >= max_per_source:
                break
            if not path.is_file():
                continue
            relative = path.name if root.is_file() else path.relative_to(root).as_posix()
            try:
                if path.name.endswith(".jsonl") or path.name.endswith(".jsonl.gz"):
                    opener = gzip.open if path.name.endswith(".gz") else open
                    with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
                        for index, line in enumerate(stream, 1):
                            if len(retained[key]) >= max_per_source:
                                break
                            try:
                                item = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            if isinstance(item, dict):
                                values = []
                                for key in ("fulltext", "text", "content", "sentence", "body", "ca", "ca_text", "text_ar"):
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
                                for key in ("url", "source_url", "canonical_url", "url_ca", "url_es",
                                            "title", "author", "date", "published", "publisher",
                                            "domain", "doc_hash", "mimetype", "lang", "dataset",
                                            "segment_id", "alignment_score"):
                                    value = item.get(key)
                                    if isinstance(value, (str, int, float)) and value != "":
                                        provenance[key] = value
                                source_url = (item.get("source_url") or item.get("url")
                                              or item.get("canonical_url") or item.get("url_ca"))
                                if source_url:
                                    provenance["source_url"] = source_url
                                for value in values:
                                    add(language, source, value, str(document_id), provenance)
                            elif isinstance(item, str):
                                add(language, source, item, f"{relative}:line:{index}",
                                    {"source_file": relative, "source_record_index": index})
                elif path.suffix.lower() in (".txt", ".tsv", ".csv"):
                    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
                    with path.open(encoding="utf-8", errors="replace", newline="") as stream:
                        reader = csv.reader(stream, delimiter=delimiter)
                        first = next(reader, None)
                        if first and "ca_text" in first:
                            text_index = first.index("ca_text")
                            dataset_index = first.index("dataset") if "dataset" in first else None
                            segment_index = first.index("segment_id") if "segment_id" in first else None
                            alignment_index = first.index("alignment_score") if "alignment_score" in first else None
                            for index, row in enumerate(reader, 2):
                                if len(retained[key]) >= max_per_source:
                                    break
                                if len(row) <= text_index:
                                    continue
                                value = row[text_index]
                                dataset = row[dataset_index] if dataset_index is not None and len(row) > dataset_index else ""
                                segment = row[segment_index] if segment_index is not None and len(row) > segment_index else str(index)
                                group = f"{dataset}:{segment}" if dataset else f"{relative}:row:{index}"
                                provenance = {
                                    "source_file": relative,
                                    "source_record_index": index,
                                    "source_document_id": segment,
                                    "dataset": dataset,
                                    "segment_id": segment,
                                }
                                if alignment_index is not None and len(row) > alignment_index:
                                    provenance["alignment_score"] = row[alignment_index]
                                add(language, source, value, group, provenance)
                        else:
                            if first and first[0].strip().lower() not in {"text"}:
                                add(language, source, first[0], f"{relative}:row:1",
                                    {"source_file": relative, "source_record_index": 1,
                                     "source_document_id": None})
                            for index, row in enumerate(reader, 2):
                                if len(retained[key]) >= max_per_source:
                                    break
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
            notes.append(
                "Catalan-DPO-V2 deliberately skipped: its card reports 40% Catalan / 60% English, "
                "but the schema has no per-row language field and this sampler has no language-ID filter. "
                "The 30,790 rows from the previous run were all mislabeled ca and are quarantined."
            )
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
            # Avoid datasets' threaded streaming reader: it repeatedly aborts the
            # hosted runner with Errno 9 / PyGILState_Release on this repository.
            # Download pinned Parquet shards and iterate them synchronously with
            # PyArrow. The repository revision is immutable and recorded above.
            from huggingface_hub import HfApi, hf_hub_download
            import pyarrow.parquet as pq

            api = HfApi()
            files = sorted(
                name for name in api.list_repo_files(
                    "wikimedia/wikipedia", repo_type="dataset",
                    revision=revisions["wikipedia"]
                )
                if name.startswith("20231101.ko/") and name.endswith(".parquet")
            )
            if not files:
                raise RuntimeError("No Korean Wikipedia Parquet shards found at pinned revision")
            processed = 0
            for filename in files:
                local_path = hf_hub_download(
                    repo_id="wikimedia/wikipedia", repo_type="dataset",
                    filename=filename, revision=revisions["wikipedia"]
                )
                parquet = pq.ParquetFile(local_path)
                columns = set(parquet.schema_arrow.names)
                required = {"id", "text"}
                if not required.issubset(columns):
                    raise RuntimeError(f"Unexpected Wikipedia Parquet schema in {filename}: {sorted(columns)}")
                selected_columns = [name for name in ("id", "url", "title", "text") if name in columns]
                for batch in parquet.iter_batches(batch_size=512, columns=selected_columns):
                    for item in batch.to_pylist():
                        page_id = str(item.get("id") or processed)
                        provenance = {
                            "dataset_repo": "wikimedia/wikipedia",
                            "repo_commit": revisions["wikipedia"],
                            "page_id": page_id,
                            "source_file": filename,
                        }
                        for key in ("url", "title"):
                            if item.get(key):
                                provenance[key] = item[key]
                        for paragraph in re.split(r"(?<=[.!?。！？])\\s+|\\n+", item.get("text", "")):
                            add("ko", "korean_wikipedia_20231101", paragraph, page_id, provenance)
                        processed += 1
                        if processed >= 500000:
                            break
                    if processed >= 500000:
                        break
                Path(local_path).unlink(missing_ok=True)
                if processed >= 500000:
                    break
            if not processed:
                raise RuntimeError("Pinned Korean Wikipedia Parquet shards contained no rows")
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
        for (language, source), items in sorted(retained.items()):
            selected.extend(items)
            stats[f"{language}|{source}|screened"] = scanned[(language, source)]
            stats[f"{language}|{source}|unique_retained"] = len(items)

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
            "stats_note": "Source-order scan: retain the first 20,000 unique records passing acquisition screening per source/language, or exhaust the source; no hash-priority sampling. Global merge performs cross-source deduplication.",
            "status": "automated candidate; declared CC BY/CC0 source terms accepted at corpus level; non-CC-BY/CC0 or explicitly unresolved upstream rights remain held",
        }
        (output_root / "manifest.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
