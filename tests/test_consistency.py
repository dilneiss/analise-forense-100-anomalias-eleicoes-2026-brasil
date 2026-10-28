from __future__ import annotations

from datetime import date

from helpers import load
from urna_forense.analysis.consistency import Requested, build_matrix, evaluate
from urna_forense.models import INCONSISTENTE, VALIDADO


def test_consistency_clean_fixture(urna):
    _, files = urna
    bundle = load(files)
    req = Requested(
        uf="sc",
        municipio=80535,
        zona=44,
        secao=144,
        turno=1,
        data_eleicao=date(2026, 10, 4),
    )
    cons = evaluate(
        urna=bundle["target"],
        requested=req,
        bu=bundle["bu"],
        rdv=bundle["rdv"],
        imgbu=bundle["imgbu"],
        log=bundle["log"],
        timeline=bundle["timeline"],
        signature=bundle["signature"],
        integrity=bundle["integrity"],
    )
    matrix = build_matrix(cons, bundle["integrity"])
    status_map = {item["relacao"]: item["status"] for item in matrix}
    assert status_map["BU <-> RDV"] == VALIDADO
    assert status_map["BU <-> LOG"] == VALIDADO
    assert status_map["BU <-> BU impresso"] == VALIDADO
    assert status_map["TIMELINE"] == VALIDADO
    # Sem erros de premissa quando os dados solicitados sao compativeis
    errors = [f for f in cons.findings if f.severity == "ERROR"]
    assert len(errors) == 0


def test_consistency_detects_premise_divergence(urna):
    _, files = urna
    bundle = load(files)
    # Solicitacao de 2o turno em 25/10/2026 sobre urna de 1o turno em 04/10/2026
    req = Requested(
        uf="sc",
        municipio=80535,
        zona=44,
        secao=144,
        turno=2,
        data_eleicao=date(2026, 10, 25),
    )
    cons = evaluate(
        urna=bundle["target"],
        requested=req,
        bu=bundle["bu"],
        rdv=bundle["rdv"],
        imgbu=bundle["imgbu"],
        log=bundle["log"],
        timeline=bundle["timeline"],
        signature=bundle["signature"],
        integrity=bundle["integrity"],
    )
    types = {f.type for f in cons.findings if f.severity == "ERROR"}
    assert "DIVERGENCIA_TURNO" in types
    assert "DIVERGENCIA_DATA_ELEICAO" in types


def test_consistency_detects_zone_mismatch(urna):
    _, files = urna
    bundle = load(files)
    req = Requested(
        uf="sc",
        municipio=80535,
        zona=99,  # zona diferente
        secao=144,
    )
    cons = evaluate(
        urna=bundle["target"],
        requested=req,
        bu=bundle["bu"],
        rdv=bundle["rdv"],
        imgbu=bundle["imgbu"],
        log=bundle["log"],
        timeline=bundle["timeline"],
        signature=bundle["signature"],
        integrity=bundle["integrity"],
    )
    types = {f.type for f in cons.findings if f.severity == "ERROR"}
    assert "PREMISSA_DIVERGENTE" in types
