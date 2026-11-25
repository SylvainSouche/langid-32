#!/usr/bin/env python3
"""Chunked AES-256-GCM authenticated encryption for large stage checkpoints."""
import argparse
import hashlib
import io
import os
import secrets
import struct
import tarfile
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"L32CP02"
LEGACY_MAGIC = b"L32CP01"
CHUNK_SIZE = 64 * 1024 * 1024


def getkey():
    secret = os.environ.get("LANGID32_CHECKPOINT_KEY", "")
    if len(secret) < 32:
        raise SystemExit("LANGID32_CHECKPOINT_KEY must be configured (>=32 characters)")
    return hashlib.sha256(secret.encode()).digest()


def read_exact(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise SystemExit("Truncated checkpoint archive")
    return data


def pack(root, archive):
    key = getkey()
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() as plain:
        with tarfile.open(fileobj=plain, mode="w:gz") as tar:
            for name in ("input", "out"):
                path = root / name
                if path.exists():
                    tar.add(path, arcname=name)
        plain.seek(0)
        with archive.open("wb") as encrypted:
            encrypted.write(MAGIC)
            while True:
                chunk = plain.read(CHUNK_SIZE)
                if not chunk:
                    break
                nonce = secrets.token_bytes(12)
                ciphertext = AESGCM(key).encrypt(nonce, chunk, MAGIC)
                encrypted.write(struct.pack(">I", len(chunk)))
                encrypted.write(nonce)
                encrypted.write(ciphertext)
            encrypted.write(struct.pack(">I", 0))


def unpack(root, archive):
    key = getkey()
    with archive.open("rb") as encrypted, tempfile.TemporaryFile() as plain:
        magic = read_exact(encrypted, len(MAGIC))
        if magic == LEGACY_MAGIC:
            nonce = read_exact(encrypted, 12)
            ciphertext = encrypted.read()
            plain.write(AESGCM(key).decrypt(nonce, ciphertext, LEGACY_MAGIC))
        elif magic == MAGIC:
            while True:
                length = struct.unpack(">I", read_exact(encrypted, 4))[0]
                if length == 0:
                    if encrypted.read(1):
                        raise SystemExit("Unexpected trailing checkpoint data")
                    break
                nonce = read_exact(encrypted, 12)
                ciphertext = read_exact(encrypted, length + 16)
                plain.write(AESGCM(key).decrypt(nonce, ciphertext, MAGIC))
        else:
            raise SystemExit("Invalid checkpoint envelope")
        plain.seek(0)
        with tarfile.open(fileobj=plain, mode="r:gz") as tar:
            root_resolved = root.resolve()
            for member in tar.getmembers():
                destination = (root / member.name).resolve()
                if destination != root_resolved and root_resolved not in destination.parents:
                    raise SystemExit("Unsafe checkpoint path")
            tar.extractall(root, filter="data")


parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=("pack", "unpack"))
parser.add_argument("--root", default=".")
parser.add_argument("--archive", required=True)
args = parser.parse_args()
root = Path(args.root)
archive = Path(args.archive)
if args.mode == "pack":
    pack(root, archive)
else:
    unpack(root, archive)
