"""Carrega todos os artefatos sinteticos para testes de analise."""

from __future__ import annotations

import hashlib
from pathlib import Path

from urna_forense.analysis.integrity import evaluate as evaluate_integrity
from urna_forense.analysis.timeline import build_timeline
from urna_forense.containers.jez import read_log_payloads
from urna_forense.models import EvidenceFile, UrnaKey
from urna_forense.parsers.bu import parse_bu
from urna_forense.parsers.imgbu import parse_imgbu
from urna_forense.parsers.logd import merge_results, parse_text
from urna_forense.parsers.rdv import parse_rdv
from urna_forense.parsers.signature import parse_signature, verify_signature

KIND_BY_KEY = {
    "bu": "bu",
    "rdv": "rdv",
    "log": "log",
    "vota": "vota",
    "imgbu": "imgbu",
}


def load(files: dict[str, Path]) -> dict:
    target = UrnaKey("sc", 80535, 44, 144)
    evidence: dict[str, EvidenceFile] = {}
    for kind, path in files.items():
        raw = path.read_bytes()
        evidence[kind] = EvidenceFile(
            relpath=path.name,
            size=len(raw),
            sha256=hashlib.sha256(raw).hexdigest(),
            sha512=hashlib.sha512(raw).hexdigest(),
            ext=path.suffix,
            detected_type="teste",
            mtime_ns=0,
            urna=target,
            kind=kind,
            abs_path=path,
        )
    bu = parse_bu(files["bu"].read_bytes())
    rdv = parse_rdv(files["rdv"].read_bytes())
    imgbu = parse_imgbu(files["imgbu"].read_bytes())
    container, payloads = read_log_payloads(files["log"])
    log = merge_results(
        [parse_text(payload.text, source=payload.entry_path) for payload in payloads]
    )
    signature = parse_signature(files["vota"].read_bytes())
    signature = verify_signature(
        signature,
        present_files={path.name: path for path in files.values()},
        election_date=bu.abertura,
    )
    timeline = build_timeline(log, bu=bu, imgbu=imgbu, signature=signature)
    integrity = evaluate_integrity(
        target_files=evidence,
        signature=signature,
        bu=bu,
        rdv=rdv,
        log=log,
        timeline=timeline,
    )
    return {
        "target": target,
        "files": files,
        "evidence": evidence,
        "bu": bu,
        "rdv": rdv,
        "imgbu": imgbu,
        "log": log,
        "container": container,
        "payloads": payloads,
        "signature": signature,
        "timeline": timeline,
        "integrity": integrity,
    }
