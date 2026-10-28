from __future__ import annotations

import io
import zipfile

import pytest

from urna_forense.containers.jez import (
    ContainerError,
    detect_container,
    list_container,
    read_log_payloads,
)


def test_detect_container_magic():
    assert detect_container(b"PK\x03\x04") == "zip"
    assert detect_container(b"7z\xbc\xaf\x27\x1c") == "7z"
    assert detect_container(b"Rar!\x1a\x07") == "rar"
    assert detect_container(b"outros-bytes") == "desconhecido"


def test_list_container_finds_nested(tmp_path):
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as archive:
        archive.writestr("logd.dat", b"log-substituida\n")
    outer = tmp_path / "pacote.jez"
    with zipfile.ZipFile(outer, "w") as archive:
        archive.writestr("1234567820261004120000.jez", inner.getvalue())
        archive.writestr("logd.dat", b"log-atual\n")
    info = list_container(outer.read_bytes(), source="pacote.jez")
    assert info.format == "zip"
    names = [entry.name for entry in info.entries]
    assert "1234567820261004120000.jez" in names
    assert "1234567820261004120000.jez!logd.dat" in names
    assert "logd.dat" in names


def test_read_log_payloads_orders_nested_first(tmp_path):
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as archive:
        archive.writestr("logd.dat", b"substituida\n")
    outer = tmp_path / "pacote.jez"
    with zipfile.ZipFile(outer, "w") as archive:
        archive.writestr("1234567820261004120000.jez", inner.getvalue())
        archive.writestr("logd.dat", b"atual\n")
    info, payloads = read_log_payloads(outer)
    assert [p.entry_path for p in payloads] == [
        "1234567820261004120000.jez!logd.dat",
        "logd.dat",
    ]
    assert payloads[0].text.strip() == "substituida"
    assert payloads[1].text.strip() == "atual"


def test_path_traversal_name_is_retained_in_memory(tmp_path):
    outer = tmp_path / "traversal.jez"
    with zipfile.ZipFile(outer, "w") as archive:
        archive.writestr("../../escape.txt", b"conteudo\n")
    info = list_container(outer.read_bytes())
    assert info.entries[0].name == "../../escape.txt"
    # Nenhum arquivo deve ter sido gravado fora de outer
    assert not (tmp_path.parent / "escape.txt").exists()


def test_encrypted_entry_raises():
    from urna_forense.containers.jez import ContainerError, _read_zip_entry

    zinfo = zipfile.ZipInfo("segredo.txt")
    zinfo.flag_bits = 0x1
    with pytest.raises(ContainerError, match="cifrada"):
        _read_zip_entry(b"", zinfo)
