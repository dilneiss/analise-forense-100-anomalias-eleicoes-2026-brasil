from __future__ import annotations

import pytest

from helpers import load
from urna_forense.models import NAO_VERIFICAVEL
from urna_forense.parsers.signature import (
    AssinaturaIlegivelError,
    parse_signature,
    verify_signature,
)


def test_signature_fixture_parsing(urna):
    _, files = urna
    sig = parse_signature(files["vota"].read_bytes())
    assert sig.model == "UE2020"
    assert sig.model_cod == 20
    assert sig.hw_algorithm_cod == 4
    assert sig.hw.algoritmo_assinatura == "eddsa"
    assert sig.sw.algoritmo_assinatura == "cepesc"
    assert sig.sw.auto_hash_confere is True
    assert sig.hw.auto_hash_confere is True
    assert len(sig.hw.files) == 4
    hashes = sig.hashes()
    assert files["bu"].name in hashes
    assert files["rdv"].name in hashes
    assert files["log"].name in hashes
    assert files["imgbu"].name in hashes


def test_signature_unsupported_status_when_no_cert(urna):
    _, files = urna
    sig = parse_signature(files["vota"].read_bytes())
    sig = verify_signature(
        sig,
        present_files={path.name: path for path in files.values()},
        election_date=None,
    )
    # Sem certificado, o status deve ser explicitamente NAO_FOI_POSSIVEL_VERIFICAR
    assert sig.status == NAO_VERIFICAVEL
    assert sig.hw.verification.status == NAO_VERIFICAVEL


def test_signature_rejects_truncated():
    with pytest.raises(AssinaturaIlegivelError):
        parse_signature(b"invalido")
