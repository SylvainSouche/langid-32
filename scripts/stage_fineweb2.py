#!/usr/bin/env python3
"""Convert the FineWeb2 extractor artifact to the source-neutral staging schema."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

LANGUAGE_BY_SUBSET = {
    "bul": "bg", "hrv": "hr", "ces": "cs", "dan": "da", "nld": "nl",
    "ekk": "et", "fin": "fi", "fra": "fr", "deu": "de", "ell": "el",
    "hun": "hu", "gle": "ga", "ita": "it", "lvs": "lv", "lit": "lt",
    "mlt": "mt", "pol": "pl", "por": "pt", "ron": "ro", "slk": "sk",
    "slv": "sl", "spa": "es", "swe": "sv", "nob": "nb", "nno": "nn",
    "rus": "ru", "jpn": "ja", "cmn": "zh", "kor": "ko", "arb": "ar",
    "tur": "tr",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.input
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    revision = manifest.get("source_revision", "v2.1.0")
    licence = "ODC-By-1.0;underlying-crawled-text-rights-unresolved"
    provenance = {}
    with (root / "provenance.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            prefix = str(row.get("subset", "")).split("_")[0]\n            source_language = LANGUAGE_BY_SUBSET.get(prefix)\n            if source_language:\n                provenance[(row["sentence_sha256"], source_language)] = row
    count = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        for split in ("train", "validation", "test"):
            with (root / f"{split}.jsonl").open(encoding="utf-8") as stream:
                for line in stream:
                    row = json.loads(line)
                    subset = row.get("subset", "")
                    # The extractor stores subset in the provenance sidecar.
                    text_hash = hashlib.sha256(row["text"].encode("utf-8")).hexdigest()
                    prov = provenance.get((text_hash, row["language"]))
                    if not prov:
                        raise ValueError(f"missing provenance for {text_hash}")
                    prefix = str(prov.get("subset", "")).split("_")[0]
                    language = LANGUAGE_BY_SUBSET.get(prefix)
                    if language != row["language"]:
                        raise ValueError(f"subset/language mismatch: {prefix}/{row['language']}")
                    group_id = f"fineweb2:{prov['group_id']}"
                    record = {
                        "text": row["text"], "language": language,
                        "source": "fineweb2", "source_release": revision,
                        "group_id": group_id, "licence_id": licence,
                        "text_origin": "original",
                        "provenance": {
                            key: prov.get(key) for key in (
                                "document_id_sha256", "source_domain", "source_url_sha256",
                                "crawl_date", "crawl_dump", "language_score", "language_script",
                                "minhash_cluster_size", "subset", "shard", "row_group_id",
                                "shard_oid", "shard_lfs_oid", "privacy_flags"
                            )
                        } | {"upstream_split": split},
                    }
                    output.write(json.dumps(record, ensure_ascii=False,
                                             separators=(",", ":")) + "\n")
                    count += 1
    print(json.dumps({"records": count, "revision": revision,
                      "licence_id": licence, "languages": len(LANGUAGE_BY_SUBSET)}))


if __name__ == "__main__":
    main()
