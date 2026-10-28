from __future__ import annotations

import hashlib

from urna_forense.crypto.hashes import (
    declared_vs_calculated,
    equal,
    format_size,
    hash_bytes,
    hash_file,
    hash_stream,
)


def test_sha256_and_sha512_known_vectors():
    assert hash_bytes(b"abc") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    assert hash_bytes(b"abc", "sha512") == (
        "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
        "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
    )
    assert hash_bytes(b"") == hashlib.sha256(b"").hexdigest()


def test_hash_file_matches_stream(tmp_path):
    path = tmp_path / "amostra.bin"
    path.write_bytes(b"conteudo" * 1000)
    with path.open("rb") as handle:
        streamed = hash_stream(handle)
    direct = hash_file(path)
    assert streamed == direct
    assert direct["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_equal_accepts_str_and_bytes():
    assert equal("AB", "ab") is False
    assert equal("ab", b"ab") is True


def test_declared_vs_calculated_reports_match():
    result = declared_vs_calculated("AA", "aa")
    assert result == {"declared": "aa", "calculated": "aa", "match": True}
    result = declared_vs_calculated("aa", "bb")
    assert result["match"] is False


def test_format_size():
    assert format_size(512) == "512 B"
    assert format_size(2048) == "2.0 KB"
    assert format_size(5 * 1024 * 1024) == "5.0 MB"
