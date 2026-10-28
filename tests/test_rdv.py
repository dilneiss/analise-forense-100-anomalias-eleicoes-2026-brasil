from __future__ import annotations

import pytest

from helpers import load
from urna_forense.parsers.rdv import RDVLegivelError, compare_with_bu, parse_rdv


def test_rdv_fixture_parsing(urna):
    _, files = urna
    rdv = parse_rdv(files["rdv"].read_bytes())
    assert rdv.pleito == 3220
    assert rdv.identificacao["municipio"] == 80535
    assert rdv.total_registros() == 13
    cargo = rdv.eleicoes[0]["cargos"][0]
    assert cargo["por_tipo"] == {"nominal": 10, "branco": 2, "nulo": 1}
    assert cargo["nominais_por_numero"] == {"22": 10}


def test_rdv_compare_with_bu(urna):
    _, files = urna
    bundle = load(files)
    rdv = bundle["rdv"]
    checks = compare_with_bu(rdv, {6257: 13})
    assert len(checks) == 1
    assert checks[0]["status"] == "VALIDADO"

    divergent = compare_with_bu(rdv, {6257: 12})
    assert divergent[0]["status"] == "INCONSISTENTE"


def test_rdv_does_not_export_voter_sequence(urna):
    _, files = urna
    rdv = parse_rdv(files["rdv"].read_bytes())
    serialized = rdv.as_dict()
    # Somente agregados: nenhum vetor ordenado de eleitor
    for eleicao in serialized["eleicoes"]:
        for cargo in eleicao["cargos"]:
            assert "votos" not in cargo
            assert "ordem" not in cargo


def test_rdv_rejects_truncated():
    with pytest.raises(RDVLegivelError):
        parse_rdv(b"invalido")
