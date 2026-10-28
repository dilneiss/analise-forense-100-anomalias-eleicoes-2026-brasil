from __future__ import annotations

from pathlib import Path

from urna_forense.models import UrnaKey
from urna_forense.scanner import detect_type, group_urnas, parse_name, scan, select_urna


def test_parse_name_extracts_all_fields():
    result = parse_name("o03220sc8053500440144-bu.dat")
    assert result is not None
    urna, kind = result
    assert urna == UrnaKey(uf="sc", municipio=80535, zona=44, secao=144)
    assert kind == "bu"


def test_parse_name_rejects_other_names():
    assert parse_name("leiame.pdf") is None
    assert parse_name("o03220sc80535-bu.dat") is None
    assert parse_name("arquivo.txt") is None


def test_detect_type_by_magic():
    assert detect_type(b"PK\x03\x04restante") == "zip"
    assert detect_type(b"7z\xbc\xaf\x27\x1c") == "7z"
    assert detect_type(b"%PDF-1.4") == "pdf"
    assert detect_type(b"") == "vazio"
    assert detect_type(b"0\x82\x01\x00resto") == "asn1-ber"
    log_sample = b"04/10/2026 08:00:01\tINFO\t02191040\tVOTA\tmsg\tMAC"
    assert detect_type(log_sample) == "log-texto"


def test_scan_discovers_and_hashes(urna):
    root, files = urna
    result = scan(root, compute_hashes=True)
    assert len(result.files) == len(files)
    assert all(item.sha256 for item in result.files)
    urnas = group_urnas(result.files)
    assert len(urnas) == 1
    target = list(urnas.keys())[0]
    assert target.uf == "sc"
    assert target.municipio == 80535
    assert target.zona == 44
    assert target.secao == 144
    matches = select_urna(urnas, uf="sc", zona=44, secao=144)
    assert matches == [target]
    assert select_urna(urnas, secao=999) == []


def test_scan_read_only_leaves_files_untouched(urna):
    root, _ = urna
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in root.iterdir()}
    scan(root, compute_hashes=True)
    after = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in root.iterdir()}
    assert before == after
