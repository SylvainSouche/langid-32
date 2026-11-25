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
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config, acquisition_target, source_quota_key
from langid32.acquisition_batches import open_state, plan_file_batches, next_batch, finish_batch, add_eligible, retained_count, pending_batch_count, mark_exhausted, export_records, task_report
from langid32.privacy import screen_text
EXECUTION = load_config()["execution"]
from urllib.request import Request, urlopen

EMAIL = re.compile(r"(?i)\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b")
URL = re.compile(r"(?i)(https?://|www\.)\S+")

IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")

SOURCE_FAMILIES = (
    "temu_cc0", "bsc_legal", "maalfrid2026", "fineweb2",
    "un_arabic_english_filtered",
)


def check_global_deadline():
    """Abort long-running acquisition loops before consuming the workflow safety reserve."""
    started = int(__import__("os").environ.get("LANGID32_ACQUISITION_STARTED_EPOCH", "0"))
    if not started:
        return
    budget = int(EXECUTION["acquisition_global_budget_minutes"]) * 60
    reserve = int(EXECUTION["acquisition_safety_margin_minutes"]) * 60
    remaining = budget - (int(time.time()) - started)
    if remaining <= reserve:
        raise SystemExit(
            f"Global acquisition deadline reached; remaining={remaining}s, safety reserve={reserve}s"
        )


def source_bucket(source):
    """Use only explicitly declared dataset quota identities; otherwise keep the source exact."""
    return source_quota_key(load_config(), source)

def clean(value, language, rules=None):
    if rules is None:
        rules = load_config()["acquisition"]["source_rules"]["waiting_sources"]
    text = " ".join(unicodedata.normalize("NFC", str(value or "")).split())
    letters = sum(char.isalpha() for char in text)
    long_number = re.search("[0-9]{" + str(rules["long_numeric_min_digits"]) + ",}", text)
    if (len(text) < rules["min_characters"] or len(text) > rules["max_characters"]
            or letters < rules["min_letters"]
            or letters / max(len(text), 1) < rules["min_letter_ratio"]
            or (rules["exclude_email"] and EMAIL.search(text))
            or (rules["exclude_url"] and URL.search(text))
            or (rules["exclude_ipv4"] and IPV4.search(text))
            or (rules["exclude_long_numeric_sequences"] and long_number)):
        return None
    if language == "ar" and sum(rules["arabic_unicode_start"] <= ord(char) <= rules["arabic_unicode_end"] for char in text) < max(rules["arabic_min_script_characters"], letters * rules["arabic_min_script_ratio"]):
        return None
    return text


def fetch(url, destination, max_attempts=None):
    """Download with resumable byte ranges; verify the complete payload hash."""
    max_attempts = max_attempts or load_config()["execution"]["max_download_attempts"]
    last_error = None
    expected = 0
    for attempt in range(max_attempts):
        try:
            if not expected:
                head = Request(url, method="HEAD", headers={"User-Agent": "langid-32-source-audit/1"})
                try:
                    with urlopen(head, timeout=EXECUTION["http_probe_timeout_seconds"]) as response:
                        expected = int(response.headers.get("Content-Length") or 0)
                except Exception:
                    expected = 0
            offset = destination.stat().st_size if destination.exists() else 0
            if expected and offset == expected:
                digest = hashlib.sha256()
                with destination.open("rb") as existing:
                    for block in iter(lambda: existing.read(EXECUTION["file_copy_chunk_bytes"]), b""):
                        digest.update(block)
                return {"url": url, "bytes": offset, "sha256": digest.hexdigest()}
            headers = {"User-Agent": "langid-32-source-audit/1"}
            if offset:
                headers["Range"] = f"bytes={offset}-"
            request = Request(url, headers=headers)
            with urlopen(request, timeout=EXECUTION["http_read_timeout_seconds"]) as response:
                if offset and response.status != 206:
                    destination.unlink(missing_ok=True)
                    raise IOError(f"server did not honour Range at byte {offset}: HTTP {response.status}; restarting download")
                if offset:
                    content_range = response.headers.get("Content-Range", "")
                    if not content_range.startswith(f"bytes {offset}-"):
                        raise IOError(f"unexpected Content-Range {content_range!r} at offset {offset}")
                elif response.status != 200:
                    raise IOError(f"unexpected HTTP {response.status}")
                with destination.open("ab" if offset else "wb") as output:
                    while True:
                        block = response.read(EXECUTION["download_chunk_bytes"])
                        if not block:
                            break
                        output.write(block)
            size = destination.stat().st_size
            if expected and size != expected:
                raise IOError(f"incomplete download: {size}/{expected} bytes")
            digest = hashlib.sha256()
            with destination.open("rb") as source:
                for block in iter(lambda: source.read(EXECUTION["file_copy_chunk_bytes"]), b""):
                    digest.update(block)
            return {"url": url, "bytes": size, "sha256": digest.hexdigest()}
        except Exception as exc:
            last_error = exc
            if getattr(exc, "code", None) == 416 and destination.exists():
                destination.unlink()
            if attempt < max_attempts - 1:
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
    parser.add_argument("--fineweb2-config")
    parser.add_argument("--config", type=Path, default=ROOT / "config/langid32.toml")
    parser.add_argument("--state-db", type=Path, help="Durable SQLite acquisition state (defaults inside --out)")
    args = parser.parse_args()
    cfg = load_config(args.config)
    waiting_text_rules = cfg["acquisition"]["source_rules"]["waiting_sources"]
    fineweb2_languages = {
        "cat_Latn": "ca", "isl_Latn": "is", "nob_Latn": "nb",
        "nno_Latn": "nn", "arb_Arab": "ar", "hrv_Latn": "hr",
        "fin_Latn": "fi", "ell_Grek": "el", "mlt_Latn": "mt",
        "slv_Latn": "sl",
    }
    if args.source == "fineweb2" and args.fineweb2_config not in fineweb2_languages:
        parser.error("--fineweb2-config must name exactly one supported FineWeb-2 configuration")

    output_root = Path(args.out)
    output_root.mkdir(parents=True, exist_ok=True)
    temp_root = output_root / ".work"
    temp_root.mkdir(parents=True, exist_ok=True)
    state_path = args.state_db or (output_root / "acquisition-state.sqlite")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_db = open_state(state_path)
    retained = defaultdict(list)
    seen = defaultdict(set)
    initialized_tasks = set()
    def limit_for(language, source):
        return acquisition_target(cfg, source, language)

    def initialize_task(bucket_key):
        if bucket_key in initialized_tasks:
            return
        language, source = bucket_key
        target = limit_for(language, source)
        plan_file_batches(
            state_db, source, language, target, [],
            int(EXECUTION["acquisition_files_per_batch"]),
        )
        existing = export_records(state_db, source, language)
        retained[bucket_key].extend(existing)
        seen[bucket_key].update(
            hashlib.sha256(item["text"].encode("utf-8")).hexdigest()
            for item in existing
        )
        initialized_tasks.add(bucket_key)

    def quota_reached(bucket_key):
        check_global_deadline()
        initialize_task(bucket_key)
        return retained_count(state_db, bucket_key[1], bucket_key[0]) >= limit_for(*bucket_key)

    def begin_remote_file(bucket_key, repository, revision, filename):
        """Create a revision-pinned, resumable one-shard acquisition batch."""
        language, source = bucket_key
        locator = f"hf://{repository}@{revision}/{filename}"
        locator_hash = hashlib.sha256(locator.encode("utf-8")).hexdigest()
        logical_file = f"{locator}#sha256={locator_hash}"
        plan_file_batches(
            state_db, source, language, limit_for(*bucket_key), [logical_file], 1
        )
        batch = next_batch(state_db, source, language)
        if batch is None:
            return None
        batch_no, planned = batch
        if planned != [logical_file]:
            raise RuntimeError(f"Unexpected pending remote batch for {source}/{language}: {planned}")
        return batch_no, logical_file, locator_hash

    def finish_remote_file(bucket_key, batch):
        if batch is not None:
            batch_no, logical_file, locator_hash = batch
            finish_batch(
                state_db, bucket_key[1], bucket_key[0], batch_no,
                {logical_file: locator_hash},
            )

    downloads = []
    notes = []
    privacy_counts = Counter()
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
                    "CC-BY-4.0 (HF dataset card claim)",
                    "Arabic text from a UN-derived dataset; upstream source terms unverified",
                    "declared_cc_by_4_0_accepted")
        raise ValueError(f"No source metadata mapping for {source}")

    def add(language, source, value, group_id="", provenance=None):
        text = clean(value, language, waiting_text_rules)
        if not text:
            privacy_counts["source_quality_rejected"] += 1
            return
        global_text_rules = cfg["acquisition"]["text"]
        letters = sum(char.isalpha() for char in text)
        if (len(text) < global_text_rules["min_characters"]
                or len(text) > global_text_rules["max_characters"]
                or len(text.encode("utf-8")) > global_text_rules["max_utf8_bytes"]
                or letters < global_text_rules["min_letter_characters"]
                or letters / max(len(text), 1) < global_text_rules["min_letter_ratio"]):
            privacy_counts["global_quality_rejected"] += 1
            return
        privacy = screen_text(
            text, record=provenance or {},
            uncertain_action=global_text_rules["privacy_uncertain_action"],
        )
        if not privacy.accepted:
            privacy_counts[privacy.status] += 1
            for flag in privacy.flags:
                privacy_counts["flag:" + flag] += 1
            return
        bucket_key = (language, source_bucket(source))
        initialize_task(bucket_key)
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        scanned[bucket_key] += 1
        if text_hash in seen[bucket_key] or quota_reached(bucket_key):
            return
        release, licence, origin, rights_status = source_metadata(source)
        source_record_id = str(group_id or text_hash)
        prov = dict(provenance or {})
        prov.update({
            "source_record_id": source_record_id,
            "rights_status": rights_status,
            "privacy_flags": list(privacy.flags),
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
        inserted = add_eligible(state_db, bucket_key[1], language, [record])
        if inserted:
            retained[bucket_key].append(record)
            seen[bucket_key].add(text_hash)

    def scan_one_file(path, root, language, source, bucket_key):
        relative = path.name if root.is_file() else path.relative_to(root).as_posix()
        try:
            if path.name.endswith(".jsonl") or path.name.endswith(".jsonl.gz"):
                opener = gzip.open if path.name.endswith(".gz") else open
                with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
                    for index, line in enumerate(stream, 1):
                        if quota_reached(bucket_key):
                            break
                        try:
                            item = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(item, dict):
                            values = []
                            for field_name in ("fulltext", "text", "content", "sentence", "body", "ca", "ca_text", "text_ar"):
                                value = item.get(field_name)
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
                            for field_name in ("url", "source_url", "canonical_url", "url_ca", "url_es",
                                        "title", "author", "date", "published", "publisher",
                                        "domain", "doc_hash", "mimetype", "lang", "dataset",
                                        "segment_id", "alignment_score", "privacy_flags",
                                        "sensitive_info", "sensitive_information", "personal_data",
                                        "pii", "is_pii", "has_personal_information"): 
                                field_value = item.get(field_name)
                                if isinstance(field_value, (str, int, float, list, tuple, bool)) and field_value != "":
                                    provenance[field_name] = field_value
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
                            if quota_reached(bucket_key):
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
                            if quota_reached(bucket_key):
                                break
                            if row:
                                add(language, source, row[0], f"{relative}:row:{index}",
                                    {"source_file": relative, "source_record_index": index,
                                     "source_document_id": None})

        except Exception as exc:
            notes.append(f"{path}: {type(exc).__name__}: {exc}")
            return False

        return True

    def scan(root, language, source):
        bucket_key = (language, source_bucket(source))
        paths = sorted([root] if root.is_file() else root.rglob("*"))
        files = [str(path.resolve()) for path in paths if path.is_file()]
        batch_size = int(EXECUTION["acquisition_files_per_batch"])
        for offset in range(0, len(files), batch_size):
            if quota_reached(bucket_key):
                break
            batch_files = files[offset:offset + batch_size]
            # Include the content digest in each logical file identity. A changed
            # upstream file is therefore a new resumable batch, not silently
            # skipped because its pathname was processed in an earlier run.
            file_versions = {}
            file_stats = {}
            for filename in batch_files:
                path = Path(filename)
                before = path.stat()
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(EXECUTION["file_copy_chunk_bytes"]), b""):
                        digest.update(block)
                after = path.stat()
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise RuntimeError(f"Source file changed while hashing: {filename}")
                file_versions[filename] = digest.hexdigest()
                file_stats[filename] = (after.st_size, after.st_mtime_ns)
            logical_files = [f"{filename}#sha256={file_versions[filename]}" for filename in batch_files]
            plan_file_batches(
                state_db, bucket_key[1], language, limit_for(*bucket_key),
                logical_files, batch_size,
            )
            batch = next_batch(state_db, bucket_key[1], language)
            if batch is None:
                continue
            batch_no, planned_files = batch
            hashes = {}
            failed = False
            for logical_filename in planned_files:
                check_global_deadline()
                if "#sha256=" in logical_filename:
                    filename, expected_hash = logical_filename.rsplit("#sha256=", 1)
                else:  # migrate an interrupted batch created by the pre-versioned workflow
                    filename = logical_filename
                    expected_hash = file_versions.get(filename)
                path = Path(filename)
                if not path.is_file():
                    failed = True
                    notes.append(f"Planned source file disappeared before processing: {filename}")
                    break
                if filename not in file_stats:
                    # Recover an older pending batch even if upstream discovery
                    # has inserted files ahead of it in the current sorted list.
                    before = path.stat()
                    digest = hashlib.sha256()
                    with path.open("rb") as stream:
                        for block in iter(lambda: stream.read(EXECUTION["file_copy_chunk_bytes"]), b""):
                            digest.update(block)
                    after_hash = path.stat()
                    if (before.st_size, before.st_mtime_ns) != (after_hash.st_size, after_hash.st_mtime_ns):
                        failed = True
                        notes.append(f"Source file changed while validating resumed batch: {filename}")
                        break
                    actual_hash = digest.hexdigest()
                    if expected_hash and actual_hash != expected_hash:
                        failed = True
                        notes.append(f"Source file content no longer matches planned batch: {filename}")
                        break
                    expected_hash = actual_hash
                    file_stats[filename] = (after_hash.st_size, after_hash.st_mtime_ns)
                if not quota_reached(bucket_key):
                    if not scan_one_file(path, root, language, source, bucket_key):
                        failed = True
                        break
                after = path.stat()
                if (after.st_size, after.st_mtime_ns) != file_stats[filename]:
                    failed = True
                    notes.append(f"Source file changed during processing: {filename}")
                    break
                hashes[logical_filename] = expected_hash
            if failed:
                break
            finish_batch(state_db, bucket_key[1], language, batch_no, hashes)
            if quota_reached(bucket_key):
                break


    try:
        if args.source == "catalan":
            temu_root = temp_root / "temu"
            if not temu_root.exists():
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
                    extracted.mkdir(parents=True, exist_ok=True)
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
                if quota_reached(("ko", "korean_wikipedia_20231101")):
                    break
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
                        if quota_reached(("ko", "korean_wikipedia_20231101")):
                            break
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
                        for paragraph in re.split(r"(?<=[.!?。！？])\s+|\n+", item.get("text", "")):
                            add("ko", "korean_wikipedia_20231101", paragraph, page_id, provenance)
                        processed += 1
                        if quota_reached(("ko", "korean_wikipedia_20231101")):
                            break
                    if quota_reached(("ko", "korean_wikipedia_20231101")):
                        break
                Path(local_path).unlink(missing_ok=True)
                if quota_reached(("ko", "korean_wikipedia_20231101")):
                    break
            if not processed:
                raise RuntimeError("Pinned Korean Wikipedia Parquet shards contained no rows")
            notes.append("Wikimedia Korean dump: CC BY-SA/GFDL attribution and share-alike obligations retained; release hold remains.")

        elif args.source == "fineweb2":
            revisions["fineweb2"] = resolve_hf_revision("HuggingFaceFW/fineweb-2")
            # Avoid datasets' threaded streaming reader: it can abort hosted
            # runners during interpreter teardown after an early quota stop
            # (Errno 9 / PyGILState_Release). Read pinned Parquet shards via
            # synchronous HTTP range requests instead of downloading 4.8GB
            # shards in full or leaving reader worker threads behind.
            from huggingface_hub import HfApi, hf_hub_url
            import fsspec
            import pyarrow.parquet as pq

            config = args.fineweb2_config
            language = fineweb2_languages[config]
            source = "fineweb2:" + config
            bucket_key = (language, source_bucket(source))
            api = HfApi()
            files = sorted(
                name for name in api.list_repo_files(
                    "HuggingFaceFW/fineweb-2", repo_type="dataset",
                    revision=revisions["fineweb2"]
                )
                if name.startswith(f"data/{config}/train/") and name.endswith(".parquet")
            )
            if not files:
                raise RuntimeError(f"No FineWeb-2 train Parquet shards found for {config} at pinned revision")
            http = fsspec.filesystem("https")
            processed = 0
            for filename in files:
                if quota_reached(bucket_key):
                    break
                url = hf_hub_url(
                    repo_id="HuggingFaceFW/fineweb-2", filename=filename,
                    repo_type="dataset", revision=revisions["fineweb2"]
                )
                with http.open(url, "rb", block_size=EXECUTION["fsspec_block_bytes"],
                               cache_type="readahead") as remote_file:
                    parquet = pq.ParquetFile(remote_file)
                    columns = set(parquet.schema_arrow.names)
                    if "text" not in columns:
                        raise RuntimeError(
                            f"Unexpected FineWeb-2 Parquet schema in {filename}: {sorted(columns)}"
                        )
                    selected_columns = [
                        name for name in ("text", "id", "url", "date", "dump", "language_score")
                        if name in columns
                    ]
                    for batch in parquet.iter_batches(batch_size=512, columns=selected_columns):
                        for item in batch.to_pylist():
                            if quota_reached(bucket_key):
                                break
                            document_id = str(item.get("id") or item.get("url") or processed)
                            provenance = {
                                "dataset_repo": "HuggingFaceFW/fineweb-2",
                                "repo_commit": revisions["fineweb2"],
                                "document_id": document_id,
                                "fineweb2_config": config,
                                "source_file": filename,
                                "source_record_index": processed,
                            }
                            for key in ("url", "date", "dump", "language_score"):
                                if item.get(key) is not None:
                                    provenance[key] = item[key]
                            add(language, source, item.get("text"), document_id, provenance)
                            processed += 1
                        if quota_reached(bucket_key):
                            break
                if processed and processed % 100000 == 0:
                    print(f"{config}: read {processed}; retained {len(retained[bucket_key])}", flush=True)
            if not quota_reached(bucket_key):
                notes.append(f"{config}: source exhausted at {len(retained[bucket_key])} retained records.")
            else:
                notes.append(f"{config}: reached the {limit_for(*bucket_key)}-record source/language quota.")
            notes.append(config + ": underlying web-text rights unresolved; technical candidates only.")

        elif args.source == "arabic":
            revisions["un_arabic"] = resolve_hf_revision("ymoslem/UN-Arabic-English-Filtered")
            from datasets import load_dataset
            dataset = load_dataset("ymoslem/UN-Arabic-English-Filtered", split="train",
                                   streaming=True, revision=revisions["un_arabic"])
            for index, item in enumerate(dataset):
                if quota_reached(("ar", "un_arabic_english_filtered:text_ar")):
                    break
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
            notes.append("HF dataset card declares CC BY 4.0; publisher-level declaration accepted.")

        else:
            raise ValueError(f"Unknown source group: {args.source}")

        # The adapter has now completed discovery/streaming for every initialized
        # exact source-language task. Only declare exhaustion when no file batch
        # remains incomplete; failed files stay resumable and report as incomplete.
        for language, source in sorted(initialized_tasks):
            if (retained_count(state_db, source, language) < limit_for(language, source)
                    and pending_batch_count(state_db, source, language) == 0):
                mark_exhausted(state_db, source, language)

        expected_languages = {
            "catalan": {"ca"},
            "icelandic": {"is"},
            "norwegian": {"nb", "nn"},
            "korean": {"ko"},
            "fineweb2": {fineweb2_languages[args.fineweb2_config]} if args.source == "fineweb2" else set(),
            "arabic": {"ar"},
        }
        actual_languages = {language for (language, _bucket), items in retained.items() if items}
        missing_languages = sorted(expected_languages.get(args.source, set()) - actual_languages)
        total_retained = sum(len(items) for items in retained.values())
        if missing_languages or total_retained < cfg["acquisition"]["source_rules"]["waiting_sources"]["minimum_retained_records"]:
            notes.append(
                f"{args.source} completed with underfilled source-language tasks: "
                f"missing_languages={missing_languages}, total_retained={total_retained}; "
                "inspect source_language_status for exact retained counts and shortfalls"
            )

        selected = []
        stats = Counter()
        unexpected_keys = [repr(key) for key in retained if not (isinstance(key, tuple) and len(key) == 2)]
        if unexpected_keys:
            raise RuntimeError(f"Unexpected source bucket keys: {unexpected_keys[:10]}")
        for bucket_key, items in sorted(retained.items(), key=lambda pair: (str(pair[0][0]), str(pair[0][1]))):
            if not isinstance(bucket_key, tuple) or len(bucket_key) != 2:
                raise RuntimeError(f"Invalid source bucket key at serialization: {bucket_key!r}")
            language, source = bucket_key
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
            "source_language_status": [task_report(state_db, source, language)
                                      for language, source in sorted(initialized_tasks)],
            "stats": dict(stats),
            "total_selected": len(deduplicated),
            "notes": notes,
            "privacy_screening": {
                "counts": dict(sorted(privacy_counts.items())),
                "policy": "shared langid32.privacy screen before exact-source quota counting; rejected and uncertain records are not retained",
            },
            "stats_note": "Source-order scan: retain the first 20,000 unique records passing acquisition screening per source/language, or exhaust the source; no hash-priority sampling. Global merge performs cross-source deduplication.",
            "status": "automated candidate; declared CC BY/CC0 source terms accepted at corpus level; non-CC-BY/CC0 or explicitly unresolved upstream rights remain held",
        }
        (output_root / "manifest.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        state_db.close()


if __name__ == "__main__":
    main()
