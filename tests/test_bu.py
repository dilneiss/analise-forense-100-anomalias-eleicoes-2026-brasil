from __future__ import annotations

import pytest

from helpers import load
from urna_forense.parsers.bu import BULegivelError, parse_bu, validate_sums


def test_bu_fixture_parsing(urna):
    _, files = urna
    bu = parse_bu(files["bu"].read_bytes())
    assert bu.identificacao["municipio"] == 80535
    assert bu.identificacao["zona"] == 44
    assert bu.identificacao["secao"] == 144
    assert bu.comparecimento == 13
    assert bu.abertura.strftime("%H:%M:%S") == "08:00:01"
    assert bu.encerramento.strftime("%H:%M:%S") == "17:00:00"
    assert bu.detalhamento_comparecimento == {
        "sem_biometria": 2,
        "por_biometria": 8,
        "por_biografia": 3,
    }


def test_bu_hash_chain_validates(urna):
    _, files = urna
    bu = parse_bu(files["bu"].read_bytes())
    assert len(bu.cadeia_hashes) == 1
    chain = bu.cadeia_hashes[0]
    assert chain["status"] == "VALIDADO"
    assert chain["registros_verificados"] == 3
    assert chain["ultimo_hash_confere"] is True


def test_bu_validate_sums_matches(urna):
    _, files = urna
    bu = parse_bu(files["bu"].read_bytes())
    results = {item["key"]: item["status"] for item in validate_sums(bu)}
    assert results["comparecimento_detalhamento"] == "VALIDADO"
    assert results["aptos_6257"] == "VALIDADO"
    assert results["total_cargo_6257_1"] == "VALIDADO"


def test_bu_rejects_truncated_data():
    with pytest.raises(BULegivelError):
        parse_bu(b"dados-truncados")
