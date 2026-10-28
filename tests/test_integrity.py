from __future__ import annotations

from helpers import load
from urna_forense.analysis.integrity import evaluate
from urna_forense.models import (
    ALTERACAO_COMPROVAVEL,
    ALTERACAO_NAO_VERIFICAVEL,
    INCONSISTENTE,
    NAO_VERIFICAVEL,
    SEM_EVIDENCIA,
    VALIDADO,
)


def test_integrity_clean_fixture(urna):
    _, files = urna
    bundle = load(files)
    integ = bundle["integrity"]
    assert integ.alteration == SEM_EVIDENCIA
    assert integ.authenticity == NAO_VERIFICAVEL
    assert integ.status == NAO_VERIFICAVEL  # worst_status porque assinatura e nao-verificavel
    # Hashes assinados devem estar validados
    hash_check = next(c for c in integ.checks if c.key == "hashes_assinados")
    assert hash_check.status == VALIDADO
    assert all(item["match"] is True for item in integ.hash_checks)


def test_integrity_detects_hash_tampering(urna):
    _, files = urna
    bundle = load(files)
    # Simula adulteracao de um arquivo (modificando o hash calculado)
    tampered_evidence = dict(bundle["evidence"])
    bu_file = tampered_evidence["bu"]
    tampered_evidence["bu"] = type(bu_file)(
        relpath=bu_file.relpath,
        size=bu_file.size,
        sha256="0" * 64,
        sha512="f" * 128,  # hash diferente do assinado
        ext=bu_file.ext,
        detected_type=bu_file.detected_type,
        mtime_ns=bu_file.mtime_ns,
        urna=bu_file.urna,
        kind=bu_file.kind,
        abs_path=bu_file.abs_path,
    )
    integ = evaluate(
        target_files=tampered_evidence,
        signature=bundle["signature"],
        bu=bundle["bu"],
        rdv=bundle["rdv"],
        log=bundle["log"],
        timeline=bundle["timeline"],
    )
    assert integ.alteration == ALTERACAO_COMPROVAVEL
    assert integ.status == INCONSISTENTE
    assert any(item["match"] is False for item in integ.hash_checks)


def test_integrity_without_signature_is_unverifiable(urna):
    _, files = urna
    bundle = load(files)
    integ = evaluate(
        target_files=bundle["evidence"],
        signature=None,
        bu=bundle["bu"],
        rdv=bundle["rdv"],
        log=bundle["log"],
        timeline=bundle["timeline"],
    )
    assert integ.alteration == ALTERACAO_NAO_VERIFICAVEL
    assert integ.authenticity == NAO_VERIFICAVEL
