"""Hashes de arquivos e comparacao em tempo constante."""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
from typing import BinaryIO, Iterable

CHUNK = 1024 * 1024


def hash_stream(
    stream: BinaryIO,
    algorithms: Iterable[str] = ("sha256", "sha512"),
) -> dict[str, str]:
    """Calcula varios hashes lendo o stream uma unica vez."""
    hashers = {name: hashlib.new(name) for name in algorithms}
    while True:
        block = stream.read(CHUNK)
        if not block:
            break
        for hasher in hashers.values():
            hasher.update(block)
    return {name: hasher.hexdigest() for name, hasher in hashers.items()}


def hash_file(path: Path, algorithms: Iterable[str] = ("sha256", "sha512")) -> dict[str, str]:
    with open(path, "rb") as handle:
        return hash_stream(handle, algorithms)


def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, data).hexdigest()


def digest_bytes(data: bytes, algorithm: str = "sha512") -> bytes:
    return hashlib.new(algorithm, data).digest()


def equal(a: str | bytes, b: str | bytes) -> bool:
    """Comparacao em tempo constante (aceita texto ou bytes)."""
    if isinstance(a, str):
        a = a.encode("ascii", "ignore")
    if isinstance(b, str):
        b = b.encode("ascii", "ignore")
    return hmac.compare_digest(a, b)


def declared_vs_calculated(declared: str, calculated: str) -> dict[str, object]:
    """Resultado objetivo de uma conferencia de hash declarado."""
    return {
        "declared": declared.lower(),
        "calculated": calculated.lower(),
        "match": equal(declared.lower(), calculated.lower()),
    }


def format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"  # pragma: no cover
