"""Extract only validated_sentences.tsv from Common Voice MDC tar.gz archives.

Audio and other archive members are streamed past and are never written to disk.
Supply one or more --archive LOCALE=PATH arguments.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tarfile
from pathlib import Path, PurePosixPath

from .common_voice_inventory import TARGET_LOCALES


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_archive_spec(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected LOCALE=PATH")
    locale, path = value.split("=", 1)
    locale = locale.strip()
    if locale not in {code for codes in TARGET_LOCALES.values() for code in codes}:
        raise argparse.ArgumentTypeError(f"unsupported target locale: {locale}")
    archive_path = Path(path).expanduser()
    if not archive_path.is_file():
        raise argparse.ArgumentTypeError(f"archive not found: {archive_path}")
    return locale, archive_path


def extract_text_tsv(locale: str, archive_path: Path, output_root: Path) -> dict:
    destination = output_root / locale / "validated_sentences.tsv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    found = False
    try:
        with tarfile.open(archive_path, mode="r|gz") as archive:
            for member in archive:
                if not member.isfile():
                    continue
                if PurePosixPath(member.name).name != "validated_sentences.tsv":
                    continue
                if found:
                    raise ValueError(
                        f"{archive_path}: more than one validated_sentences.tsv"
                    )
                source = archive.extractfile(member)
                if source is None:
                    raise ValueError(f"cannot read {member.name} from {archive_path}")
                with source, destination.open("wb") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
                found = True
                break
    except (tarfile.TarError, OSError) as exc:
        destination.unlink(missing_ok=True)
        raise ValueError(f"cannot extract {archive_path}: {exc}") from exc
    if not found:
        destination.unlink(missing_ok=True)
        raise ValueError(f"{archive_path}: validated_sentences.tsv not found")
    return {
        "locale": locale,
        "archive_name": archive_path.name,
        "archive_bytes": archive_path.stat().st_size,
        "tsv_path": str(destination),
        "tsv_bytes": destination.stat().st_size,
        "tsv_sha256": sha256_file(destination),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive", action="append", required=True, type=parse_archive_spec,
        metavar="LOCALE=PATH", help="MDC archive; repeat for each locale",
    )
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--manifest", type=Path,
                        help="Optional extraction manifest JSON")
    args = parser.parse_args()
    seen = set()
    results = []
    for locale, archive_path in args.archive:
        if locale in seen:
            parser.error(f"locale supplied more than once: {locale}")
        seen.add(locale)
        results.append(extract_text_tsv(locale, archive_path, args.output_root))
    manifest = {
        "source": "Mozilla Common Voice Scripted Speech 27.0",
        "extraction": "validated_sentences.tsv only; no audio members written",
        "archives": results,
    }
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "locales_extracted": len(results),
        "output_root": str(args.output_root),
        "manifest": str(args.manifest) if args.manifest else None,
    }, indent=2))


if __name__ == "__main__":
    main()
