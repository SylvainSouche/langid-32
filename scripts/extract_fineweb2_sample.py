#!/usr/bin/env python3
"""Extract a deterministic, bounded FineWeb2 sentence sample via remote Parquet ranges.

Only selected row groups and required columns are read. Text is written to
local output files (for a short-lived GitHub Actions artifact), never committed.
The sidecar records hashed document identifiers and hostname-level grouping.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from langid32.fineweb2_inventory import TARGET_SUBSETS

EXTRACTOR_VERSION = "0.3.0"
DATASET = "HuggingFaceFW/fineweb-2"
DEFAULT_REVISION = "v2.1.0"
SEED = "langid-32-fineweb2-v1"
SENTENCE_SPLIT = re.compile(r"(?<=[.!?。！？؟؛।።])\s+|(?<=[。！？])")
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL = re.compile(r"(?i)(?:https?://|www\.)\S+")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PHONE = re.compile(r"(?<!\w)\+?\d[\d .()/-]{7,}\d(?!\w)")
LONG_NUMBER = re.compile(r"\d{9,}")
SCRIPT_PREFIXES = {
    "Latn": ("LATIN",),
    "Cyrl": ("CYRILLIC",),
    "Grek": ("GREEK",),
    "Arab": ("ARABIC",),
    "Hang": ("HANGUL",),
    "Hani": ("CJK UNIFIED IDEOGRAPH",),
    "Jpan": ("CJK UNIFIED IDEOGRAPH", "HIRAGANA", "KATAKANA"),
}


def request_json(url: str, timeout: int) -> tuple[object, dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "langid-32 FineWeb2 extractor/0.1", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
        headers = {key.lower(): value for key, value in response.headers.items()}
        return payload, headers


def next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        bits = part.split(";")
        if len(bits) < 2 or 'rel="next"' not in bits[1]:
            continue
        target = bits[0].strip()
        if target.startswith("<") and target.endswith(">"):
            return target[1:-1]
    return None


def list_train_files(subset: str, revision: str, timeout: int) -> list[dict]:
    url = (
        f"https://huggingface.co/api/datasets/{DATASET}/tree/"
        f"{urllib.parse.quote(revision, safe='')}/data/{subset}/train"
        "?recursive=true&expand=false&limit=1000"
    )
    files = []
    while url:
        payload, headers = request_json(url, timeout)
        if not isinstance(payload, list):
            raise ValueError(f"Unexpected Hub tree response for {subset}: {payload!r}")
        files.extend(
            item for item in payload
            if isinstance(item, dict) and (item.get("type") == "file" or "size" in item)
            and str(item.get("path", "")).endswith(".parquet")
        )
        url = next_link(headers.get("link", ""))
    if not files:
        raise FileNotFoundError(f"No train Parquet files found for {subset}@{revision}")
    return sorted(files, key=lambda item: str(item.get("path", "")))


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_fraction(group_id: str, seed: str) -> float:
    value = int.from_bytes(hashlib.sha256(f"{seed}\0{group_id}".encode()).digest()[:8], "big")
    return value / 2**64


def assign_split(group_id: str, seed: str) -> str:
    value = stable_fraction(group_id, seed)
    if value < 0.10:
        return "test"
    if value < 0.20:
        return "validation"
    return "train"


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def script_ratio(text: str, script: str) -> float:
    prefixes = SCRIPT_PREFIXES.get(script)
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    if not prefixes:
        return 1.0
    matching = sum(
        1 for char in letters
        if unicodedata.name(char, "").startswith(prefixes)
    )
    return matching / len(letters)


def sentence_candidates(text: str, script: str, min_chars: int, max_chars: int,
                        rejected: Counter):
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("\\n", " ").replace("\\r", " ").replace("\\t", " ")
    parts = SENTENCE_SPLIT.split(text)
    seen = set()
    for part in parts:
        sentence = normalize(part).lstrip("-–—•*· ").strip()
        if not sentence:
            continue
        if sentence in seen:
            rejected["duplicate_within_document"] += 1
            continue
        seen.add(sentence)
        if len(sentence) < min_chars:
            rejected["too_short"] += 1
            continue
        if len(sentence) > max_chars:
            rejected["too_long"] += 1
            continue
        if EMAIL.search(sentence):
            rejected["email"] += 1
            continue
        if URL.search(sentence):
            rejected["url"] += 1
            continue
        if IPV4.search(sentence):
            rejected["ipv4"] += 1
            continue
        # Do not discard phone-like or long numeric sequences automatically:
        # broad phone regexes have high false-positive rates. Flag for review.
        if PHONE.search(sentence):
            rejected["phone_like_flagged"] += 1
        if LONG_NUMBER.search(sentence):
            rejected["long_number_flagged"] += 1
        letters = sum(char.isalpha() for char in sentence)
        if letters < 8 or letters / max(1, len(sentence.replace(" ", ""))) < 0.45:
            rejected["low_letter_ratio"] += 1
            continue
        if script_ratio(sentence, script) < 0.70:
            rejected["script_mismatch"] += 1
            continue
        # Avoid navigation fragments and short headings masquerading as sentences.
        words = re.findall(r"[^\W_]+", sentence, flags=re.UNICODE)
        if script in {"Latn", "Cyrl", "Grek", "Arab"} and len(words) < 5:
            rejected["too_few_words"] += 1
            continue
        if sentence[-1:] not in ".!?。！？؟؛।።" and len(sentence) < 80:
            rejected["no_sentence_ending"] += 1
            continue
        yield sentence


def http_stats(connection) -> dict:
    try:
        rows = connection.execute(
            "SELECT request.type, response.status, response.headers "
            "FROM duckdb_logs_parsed('HTTP')"
        ).fetchall()
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    requests = []
    get_bytes = 0
    for method, status, headers in rows:
        headers = headers or {}
        length = headers.get("Content-Length") or headers.get("content-length")
        try:
            size = int(length) if length is not None else 0
        except (TypeError, ValueError):
            size = 0
        if str(method).upper() == "GET":
            get_bytes += size
        requests.append({"method": method, "status": status, "content_length": size})
    return {
        "request_count": len(requests),
        "get_count": sum(1 for item in requests if str(item["method"]).upper() == "GET"),
        "get_content_length_bytes": get_bytes,
        "requests": requests,
    }


def extract_language(connection, language: str, subset: str, revision: str,
                     target: int, max_row_groups: int, shards_per_language: int,
                     min_chars: int, max_chars: int, min_score: float,
                     timeout: int, seed: str) -> tuple[list, list, dict]:
    files = list_train_files(subset, revision, timeout)
    shard_count = min(max(1, shards_per_language), len(files))
    shard_base = int(sha256(f"{seed}\0{subset}\0shards")[:12], 16) % len(files)
    shard_indices = sorted({
        (shard_base + round(i * len(files) / shard_count)) % len(files)
        for i in range(shard_count)
    })
    columns_sql = (
        "text, id, url, date, dump, language, language_score, "
        "language_script, minhash_cluster_size, file_row_group_number"
    )
    split_candidates: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    seen_text: set[str] = set()
    rejected = Counter()
    sentence_rejected = Counter()
    docs = 0
    doc_domains = set()
    docs_by_shard = Counter()
    docs_by_row_group = Counter()
    candidate_sentences_before_cap = 0
    candidate_sentences_after_cap = 0
    shard_reports = []
    max_sentences_per_doc = 20

    for file_index in shard_indices:
        file_item = files[file_index]
        path = str(file_item["path"])
        url = f"https://huggingface.co/datasets/{DATASET}/resolve/{revision}/{path}"
        escaped = url.replace("'", "''")
        connection.execute("CALL truncate_duckdb_logs()")
        metadata = connection.execute(
            "SELECT row_group_id, max(row_group_num_rows) AS rows "
            f"FROM parquet_metadata('{escaped}') "
            "GROUP BY row_group_id ORDER BY row_group_id"
        ).fetchall()
        metadata_stats = http_stats(connection)
        if not metadata:
            raise RuntimeError(f"No row groups found in {path}")
        group_count = len(metadata)
        base = int(sha256(f"{seed}\0{path}\0rowgroups")[:12], 16) % group_count
        row_group_ids = sorted({
            (base + round(i * group_count / max_row_groups)) % group_count
            for i in range(max_row_groups)
        })
        group_ids_sql = ",".join(str(value) for value in row_group_ids)
        connection.execute("CALL truncate_duckdb_logs()")
        cursor = connection.execute(
            f"SELECT {columns_sql} FROM read_parquet('{escaped}') "
            f"WHERE file_row_group_number IN ({group_ids_sql})"
        )
        shard_docs = 0
        shard_domains = set()
        for batch in iter(lambda: cursor.fetchmany(256), []):
            for text, doc_id, source_url, crawl_date, dump, source_language, score, source_script, cluster_size, row_group_id in batch:
                docs += 1
                shard_docs += 1
                docs_by_shard[path] += 1
                docs_by_row_group[f"{path}#{row_group_id}"] += 1
                if score is None or float(score) < min_score:
                    rejected["document_language_score"] += 1
                    continue
                if source_language and str(source_language).lower() != subset.split("_")[0].lower():
                    rejected["document_language_code_mismatch"] += 1
                    continue
                if source_script and str(source_script) != subset.split("_")[1]:
                    rejected["document_script_mismatch"] += 1
                    continue
                hostname = urllib.parse.urlparse(source_url or "").hostname or ""
                hostname = hostname.lower().removeprefix("www.").rstrip(".")
                if hostname:
                    doc_domains.add(hostname)
                    shard_domains.add(hostname)
                    group_material = f"host:{hostname}"
                else:
                    rejected["missing_hostname"] += 1
                    group_material = f"document:{doc_id}"
                group_id = sha256(group_material)
                split = assign_split(group_id, seed)
                doc_hash = sha256(str(doc_id))
                candidates = list(sentence_candidates(
                    text or "", subset.split("_")[1], min_chars, max_chars, sentence_rejected
                ))
                candidate_sentences_before_cap += len(candidates)
                candidates.sort(key=lambda sentence: sha256(f"{seed}\0{doc_hash}\0{sentence}"))
                if len(candidates) > max_sentences_per_doc:
                    rejected["document_sentence_cap"] += len(candidates) - max_sentences_per_doc
                candidates = candidates[:max_sentences_per_doc]
                candidate_sentences_after_cap += len(candidates)
                for sentence in candidates:
                    if sentence in seen_text:
                        rejected["duplicate_sentence"] += 1
                        continue
                    seen_text.add(sentence)
                    sentence_hash = sha256(sentence)
                    priority = sha256(f"{seed}\0{language}\0{split}\0{sentence}")
                    record = {
                        "text": sentence, "language": language, "source": "fineweb2",
                        "split": split, "group_id": group_id, "document_id_hash": doc_hash,
                    }
                    provenance = {
                        "sentence_sha256": sentence_hash, "document_id_sha256": doc_hash,
                        "group_id": group_id, "source_domain": hostname,
                        "source_url_sha256": sha256(source_url or ""),
                        "crawl_date": str(crawl_date or ""), "crawl_dump": str(dump or ""),
                        "language_score": float(score), "language_script": str(source_script or ""),
                        "minhash_cluster_size": int(cluster_size or 0), "revision": revision,
                        "subset": subset, "shard": path, "row_group_id": int(row_group_id),
                        "shard_oid": str(file_item.get("oid") or ""),
                        "shard_lfs_oid": str((file_item.get("lfs") or {}).get("oid", "")),
                        "privacy_flags": [
                            flag for flag, pattern in (
                                ("phone_like", PHONE), ("long_numeric_sequence", LONG_NUMBER)
                            ) if pattern.search(sentence)
                        ],
                    }
                    split_candidates[split].append((priority, {"record": record, "provenance": provenance}))
        shard_reports.append({
            "shard_index": file_index, "shard": path,
            "shard_bytes": int(file_item.get("size") or 0),
            "row_group_count": group_count, "selected_row_group_ids": row_group_ids,
            "selected_row_group_rows": {str(row[0]): int(row[1]) for row in metadata if int(row[0]) in row_group_ids},
            "documents_read": shard_docs, "distinct_hostnames": len(shard_domains),
            "metadata_http": metadata_stats, "sample_http": http_stats(connection),
        })

    caps = {

        "train": target - round(target * 0.10) - round(target * 0.10),
        "validation": round(target * 0.10),
        "test": round(target * 0.10),
    }
    selected_records = []
    selected_provenance = []
    selected_counts = {}
    for split in ("train", "validation", "test"):
        ordered = sorted(split_candidates.get(split, []), key=lambda item: item[0])
        chosen = ordered[:caps[split]]
        selected_counts[split] = len(chosen)
        selected_records.extend(item["record"] for _, item in chosen)
        selected_provenance.extend(item["provenance"] for _, item in chosen)

    rejected.update({f"sentence_{key}": value for key, value in sentence_rejected.items()})
    selected_lengths = sorted(len(item["text"]) for item in selected_records)
    selected_groups = {
        split: len({item["group_id"] for item in selected_records if item["split"] == split})
        for split in caps
    }
    selected_documents = {
        split: len({item["document_id_hash"] for item in selected_records if item["split"] == split})
        for split in caps
    }
    sample_stats = http_stats(connection)
    report = {
        "language": language,
        "subset": subset,
        "revision": revision,
        "shard_count": len(files),
        "selected_shard_count": len(shard_indices),
        "selected_shard_indices": shard_indices,
        "selected_shards": shard_reports,
        "documents_read": docs,
        "documents_by_shard": dict(sorted(docs_by_shard.items())),
        "documents_by_row_group": dict(sorted(docs_by_row_group.items())),
        "distinct_hostnames": len(doc_domains),
        "candidate_sentences_before_document_cap": candidate_sentences_before_cap,
        "candidate_sentences_after_document_cap": candidate_sentences_after_cap,
        "selected_sentence_length_chars": {
            "min": selected_lengths[0] if selected_lengths else 0,
            "median": int(statistics.median(selected_lengths)) if selected_lengths else 0,
            "p95": selected_lengths[int((len(selected_lengths) - 1) * 0.95)] if selected_lengths else 0,
            "max": selected_lengths[-1] if selected_lengths else 0,
        },
        "selected_distinct_groups_by_split": selected_groups,
        "selected_distinct_documents_by_split": selected_documents,
        "candidate_counts_by_split": {
            split: len(values) for split, values in split_candidates.items()
        },
        "selected_counts_by_split": selected_counts,
        "target_counts_by_split": caps,
        "shortfall_by_split": {
            split: max(0, caps[split] - selected_counts[split]) for split in caps
        },
        "rejected": dict(rejected),
        "metadata_http": metadata_stats,
        "sample_http": sample_stats,
        "sample_bytes_total": (
            metadata_stats.get("get_content_length_bytes", 0)
            + sample_stats.get("get_content_length_bytes", 0)
        ),
    }
    return selected_records, selected_provenance, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--languages", nargs="+", default=["es", "tr"])
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument("--target-per-language", type=int, default=20000)
    parser.add_argument("--max-row-groups", type=int, default=1)
    parser.add_argument("--shards-per-language", type=int, default=8)
    parser.add_argument("--min-chars", type=int, default=25)
    parser.add_argument("--max-chars", type=int, default=400)
    parser.add_argument("--min-language-score", type=float, default=0.90)
    parser.add_argument("--seed", default=SEED)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.target_per_language < 1 or args.max_row_groups < 1 or args.shards_per_language < 1:
        parser.error("target, max row groups and shards per language must be positive")
    if args.min_chars < 1 or args.max_chars < args.min_chars:
        parser.error("invalid sentence length limits")
    if not 0 <= args.min_language_score <= 1:
        parser.error("min language score must be in [0,1]")

    import duckdb

    connection = duckdb.connect()
    connection.execute("INSTALL httpfs")
    connection.execute("LOAD httpfs")
    connection.execute("CALL enable_logging('HTTP', storage='memory')")
    version = connection.execute("SELECT version()").fetchone()[0]
    if not version.startswith("v2."):
        raise SystemExit(f"DuckDB 2.x required for row-group pruning; found {version}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    all_records = []
    all_provenance = []
    for language in args.languages:
        if language not in TARGET_SUBSETS or TARGET_SUBSETS[language] is None:
            raise SystemExit(f"No FineWeb2 subset mapping for target language {language}")
        try:
            records, provenance, report = extract_language(
                connection, language, TARGET_SUBSETS[language], args.revision,
                args.target_per_language, args.max_row_groups, args.shards_per_language,
                args.min_chars, args.max_chars, args.min_language_score, args.timeout, args.seed,
            )
            reports.append(report)
            all_records.extend(records)
            all_provenance.extend(provenance)
        except Exception as exc:
            reports.append({
                "language": language,
                "subset": TARGET_SUBSETS[language],
                "revision": args.revision,
                "error": f"{type(exc).__name__}: {exc}",
            })

    connection.close()
    by_split = defaultdict(list)
    for record in all_records:
        by_split[record["split"]].append(record)
    output_hashes = {}
    for split in ("train", "validation", "test"):
        path = args.output_dir / f"{split}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for record in by_split[split]:
                stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        output_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()

    provenance_path = args.output_dir / "provenance.jsonl"
    with provenance_path.open("w", encoding="utf-8", newline="\n") as stream:
        for item in all_provenance:
            stream.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    output_hashes[provenance_path.name] = hashlib.sha256(provenance_path.read_bytes()).hexdigest()

    manifest = {
        "schema_version": 1,
        "extractor_version": EXTRACTOR_VERSION,
        "project": "langid-32",
        "source": "HuggingFaceFW/fineweb-2",
        "source_revision": args.revision,
        "source_dataset_licence": "ODC-By-1.0 (dataset/compilation; underlying web-source rights remain separate)",
        "target_per_language": args.target_per_language,
        "split_fractions": {"train": 0.80, "validation": 0.10, "test": 0.10},
        "selection": {
            "seed": args.seed,
            "row_groups_per_language": args.max_row_groups,
        "shards_per_language": args.shards_per_language,
            "min_chars": args.min_chars,
            "max_chars": args.max_chars,
            "min_language_score": args.min_language_score,
            "max_sentences_per_document": 20,
            "grouping": "hostname-level; group hash shared across languages",
            "deduplication": "exact normalized sentence within language across sampled row groups",
            "privacy_exclusions": ["email", "URL", "IPv4"],
            "privacy_review_flags": ["phone-like sequence", "9+ digit sequence"],
        },
        "duckdb_version": version,
        "languages": reports,
        "output_sha256": output_hashes,
        "privacy_note": "Text-only sample plus provenance sidecar; source URL is hashed, hostname retained. Email, URL and IPv4 patterns are excluded. Phone-like and long numeric sequences are retained with per-sample review flags because broad phone regexes have high false-positive rates. This is not a guarantee of anonymization; review before publication.",
        "limitation": "This is a bounded deterministic sample from selected row groups, not a statistically representative sample of the entire language subset.",
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output_dir": str(args.output_dir),
        "duckdb_version": version,
        "languages": [
            {
                "language": row["language"],
                "selected_counts_by_split": row.get("selected_counts_by_split", {}),
                "shortfall_by_split": row.get("shortfall_by_split", {}),
                "sample_bytes_total": row.get("sample_bytes_total", 0),
                "error": row.get("error"),
            }
            for row in reports
        ],
        "manifest": str(manifest_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
