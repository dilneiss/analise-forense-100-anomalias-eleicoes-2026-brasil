"""Integridade: hashes assinados, BU, log, assinatura e classificacao.

Vocabulario controlado:
  VALIDADO / NAO_VALIDADO / INCONSISTENTE / NAO_FOI_POSSIVEL_VERIFICAR
Nunca se conclui "fraude" ou "adulteracao" a partir de inconsistencia.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..models import (
    ALTERACAO_COMPROVAVEL,
    ALTERACAO_NAO_VERIFICAVEL,
    ALTERACAO_POSSIVEL,
    INCONSISTENTE,
    NAO_VALIDADO,
    NAO_VERIFICAVEL,
    SEM_EVIDENCIA,
    VALIDADO,
    CheckResult,
    EvidenceFile,
    worst_status,
)
from ..parsers.bu import BU, validate_sums
from ..parsers.logd import LogParseResult
from ..parsers.rdv import RDV
from ..parsers.signature import SignatureFile
from .timeline import Timeline


@dataclass
class IntegrityReport:
    status: str
    alteration: str
    authenticity: str
    checks: list[CheckResult] = field(default_factory=list)
    hash_checks: list[dict[str, Any]] = field(default_factory=list)
    missing_signed_files: list[str] = field(default_factory=list)
    extra_files: list[str] = field(default_factory=list)
    signature_summary: dict[str, Any] = field(default_factory=dict)
    bu_summary: dict[str, Any] = field(default_factory=dict)
    log_summary: dict[str, Any] = field(default_factory=dict)
    timeline_order: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "alteration": self.alteration,
            "authenticity": self.authenticity,
            "checks": [check.as_dict() for check in self.checks],
            "hash_checks": self.hash_checks,
            "missing_signed_files": self.missing_signed_files,
            "extra_files": self.extra_files,
            "signature_summary": self.signature_summary,
            "bu_summary": self.bu_summary,
            "log_summary": self.log_summary,
            "timeline_order": self.timeline_order,
            "limitations": self.limitations,
        }


def _check(key: str, label: str, status: str, detail: str, evidence: Optional[list[str]] = None) -> CheckResult:
    return CheckResult(key=key, label=label, status=status, detail=detail, evidence=evidence or [])


def evaluate(
    *,
    target_files: dict[str, EvidenceFile],
    signature: Optional[SignatureFile],
    bu: Optional[BU],
    rdv: Optional[RDV],
    log: Optional[LogParseResult],
    timeline: Optional[Timeline],
) -> IntegrityReport:
    checks: list[CheckResult] = []
    limitations: list[str] = []
    hash_checks: list[dict[str, Any]] = []
    missing: list[str] = []
    statuses: list[str] = []

    by_name = {item.relpath.split("/")[-1]: item for item in target_files.values()}

    # ---------------- hashes assinados -----------------------------------
    if signature:
        declared = signature.hashes()
        for name in sorted(declared):
            expected = declared[name]
            evidence = by_name.get(name)
            if evidence is None:
                missing.append(name)
                hash_checks.append(
                    {
                        "file": name,
                        "declared_sha512": expected.lower(),
                        "calculated_sha512": None,
                        "match": None,
                        "status": NAO_VERIFICAVEL,
                        "reason": "arquivo assinado ausente no conjunto fornecido",
                    }
                )
                continue
            calculated = evidence.sha512
            match = calculated.lower() == expected.lower() if calculated else False
            status = VALIDADO if match else INCONSISTENTE
            hash_checks.append(
                {
                    "file": name,
                    "declared_sha512": expected.lower(),
                    "calculated_sha512": calculated.lower() if calculated else None,
                    "match": match,
                    "status": status,
                }
            )
            statuses.append(status)
        checks.append(
            _check(
                "hashes_assinados",
                "Hashes SHA-512 assinados",
                worst_status(statuses),
                (
                    f"{sum(1 for item in hash_checks if item['match'])} de "
                    f"{sum(1 for item in hash_checks if item['match'] is not None)} "
                    "arquivos presentes conferem com o hash assinado; "
                    f"{len(missing)} arquivo(s) assinado(s) ausente(s) no conjunto"
                ),
                [item["file"] for item in hash_checks if item["match"] is False],
            )
        )
        extra_files = sorted(
            name for name in set(by_name) - set(declared) if not name.endswith("-vota.vsc")
        )
    else:
        limitations.append(
            "Arquivo de assinatura ausente: nenhum hash assinado pode ser conferido."
        )
        checks.append(
            _check(
                "hashes_assinados",
                "Hashes SHA-512 assinados",
                NAO_VERIFICAVEL,
                "sem -vota.vsc no conjunto",
            )
        )
        statuses.append(NAO_VERIFICAVEL)

    # ---------------- assinatura digital ---------------------------------
    extra_files: list[str] = []
    signature_summary: dict[str, Any] = {}
    authenticity = NAO_VERIFICAVEL
    if signature:
        signature_summary = signature.as_dict()
        checks.append(
            _check(
                "hash_autoassinado_sw",
                "Hash do conteudo autoassinado (software)",
                VALIDADO if signature.sw.auto_hash_confere else INCONSISTENTE,
                (
                    "SHA-512 do conteudo confere com o hash declarado"
                    if signature.sw.auto_hash_confere
                    else "SHA-512 do conteudo difere do hash declarado"
                ),
            )
        )
        checks.append(
            _check(
                "hash_autoassinado_hw",
                "Hash do conteudo autoassinado (hardware)",
                VALIDADO if signature.hw.auto_hash_confere else INCONSISTENTE,
                (
                    "SHA-512 do conteudo confere com o hash declarado"
                    if signature.hw.auto_hash_confere
                    else "SHA-512 do conteudo difere do hash declarado"
                ),
            )
        )
        hw_status = signature.hw.verification.status if signature.hw.verification else NAO_VERIFICAVEL
        checks.append(
            _check(
                "assinatura_hardware",
                "Assinatura digital de hardware",
                hw_status,
                signature.hw.verification.detail if signature.hw.verification else "nao avaliada",
                [signature.hw.certificate.subject] if signature.hw.certificate else [],
            )
        )
        checks.append(
            _check(
                "assinatura_software",
                "Assinatura digital de software (CEPESC)",
                NAO_VERIFICAVEL,
                signature.sw.verification.detail if signature.sw.verification else "nao avaliada",
            )
        )
        chain_status = signature.chain.get("status", NAO_VERIFICAVEL) if signature.chain else NAO_VERIFICAVEL
        checks.append(
            _check(
                "cadeia_certificacao",
                "Cadeia de certificacao",
                chain_status,
                signature.chain.get("detail", "nao avaliada") if signature.chain else "nao avaliada",
            )
        )
        statuses.extend([hw_status, chain_status])
        if hw_status == NAO_VALIDADO or chain_status == NAO_VALIDADO:
            authenticity = NAO_VALIDADO
        elif hw_status == VALIDADO and chain_status in (VALIDADO, NAO_VERIFICAVEL):
            authenticity = VALIDADO
        else:
            authenticity = NAO_VERIFICAVEL
        limitations.append(
            "A assinatura de hardware Ed521 (ICP-Brasil) nao e suportada pela "
            "biblioteca criptografica utilizada; por isso a autenticidade "
            "criptografica do conjunto nao foi confirmada."
        )
        limitations.append(
            "A assinatura de software CEPESC usa algoritmo de governo sem "
            "verificador publico; ela foi lida, nao verificada."
        )
    else:
        checks.append(
            _check(
                "assinatura_hardware",
                "Assinatura digital de hardware",
                NAO_VERIFICAVEL,
                "arquivo de assinatura ausente",
            )
        )
        statuses.append(NAO_VERIFICAVEL)

    # ---------------- BU --------------------------------------------------
    bu_summary: dict[str, Any] = {}
    if bu:
        chain_statuses = [item["status"] for item in bu.cadeia_hashes]
        sums = validate_sums(bu)
        sum_statuses = [item["status"] for item in sums]
        bu_summary = {
            "identificacao": bu.identificacao,
            "fase": bu.fase,
            "fase_nome": bu.envelope.get("fase_nome"),
            "data_hora_emissao": bu.data_hora_emissao.isoformat(),
            "dados_secao": {
                key: value.isoformat() if isinstance(value, datetime) else value
                for key, value in bu.dados_secao.items()
            },
            "comparecimento": bu.comparecimento,
            "detalhamento_comparecimento": bu.detalhamento_comparecimento,
            "eleicoes": [
                {
                    "id_eleicao": eleicao["id_eleicao"],
                    "qtd_eleitores_aptos": eleicao["qtd_eleitores_aptos"],
                    "cargos": [
                        {
                            "codigo_cargo": cargo["codigo_cargo"],
                            "cargo": cargo["cargo"],
                            "total_votos": cargo["total_votos"],
                            "tipos_voto": cargo["tipos_voto"],
                        }
                        for resultado in eleicao["resultados"]
                        for cargo in resultado["cargos"]
                    ],
                }
                for eleicao in bu.eleicoes
            ],
            "cadeia_hashes": bu.cadeia_hashes,
            "checks_aritmeticos": sums,
        }
        checks.append(
            _check(
                "bu_estrutura",
                "Estrutura ASN.1 do BU",
                VALIDADO,
                f"BU de {len(bu.eleicoes)} eleicao(oes) decodificado",
            )
        )
        checks.append(
            _check(
                "bu_cadeia_hashes",
                "Cadeia de hashes SHA-512 do BU",
                worst_status(chain_statuses) if chain_statuses else NAO_VERIFICAVEL,
                "; ".join(
                    f"eleicao {item['id_eleicao']}: {item['registros_verificados']} "
                    f"registros, {len(item['falhas'])} falha(s), "
                    f"ultimo hash {'confere' if item['ultimo_hash_confere'] else 'difere'}"
                    for item in bu.cadeia_hashes
                ),
            )
        )
        checks.append(
            _check(
                "bu_aritmetica",
                "Conferencias aritmeticas do BU",
                worst_status(sum_statuses) if sum_statuses else NAO_VERIFICAVEL,
                "; ".join(item["detail"] for item in sums),
            )
        )
        statuses.extend(chain_statuses)
        statuses.extend(sum_statuses)
    else:
        checks.append(_check("bu_estrutura", "Estrutura ASN.1 do BU", NAO_VERIFICAVEL, "BU ausente ou ilegivel"))
        statuses.append(NAO_VERIFICAVEL)
        limitations.append("BU ausente/ilegivel: nao foi possivel validar a estrutura nem a cadeia de hashes.")

    # ---------------- RDV -------------------------------------------------
    if rdv:
        from ..parsers.rdv import compare_with_bu

        comparecimento = {
            eleicao["id_eleicao"]: eleicao["resultados"][0]["comparecimento"]
            for eleicao in (bu.eleicoes if bu else [])
            if eleicao.get("resultados")
        }
        rdv_checks = compare_with_bu(rdv, comparecimento)
        rdv_statuses = [item["status"] for item in rdv_checks]
        checks.append(
            _check(
                "rdv_estrutura",
                "Estrutura ASN.1 do RDV",
                VALIDADO,
                f"RDV de {len(rdv.eleicoes)} eleicao(oes), "
                f"{rdv.total_registros()} registros agregados",
            )
        )
        checks.append(
            _check(
                "rdv_registros",
                "Registros do RDV x comparecimento do BU",
                worst_status(rdv_statuses) if rdv_statuses else NAO_VERIFICAVEL,
                "; ".join(item["detail"] for item in rdv_checks),
            )
        )
        statuses.append(VALIDADO)
        statuses.extend(rdv_statuses)
    else:
        checks.append(_check("rdv_estrutura", "Estrutura ASN.1 do RDV", NAO_VERIFICAVEL, "RDV ausente ou ilegivel"))
        statuses.append(NAO_VERIFICAVEL)

    # ---------------- log -------------------------------------------------
    log_summary: dict[str, Any] = {}
    if log:
        inversions = 0
        by_session: dict[int, list] = {}
        for event in log.events:
            by_session.setdefault(event.session, []).append(event)
        for session_events in by_session.values():
            previous = None
            for event in session_events:
                if previous and event.timestamp and previous > event.timestamp:
                    inversions += 1
                previous = event.timestamp or previous
        log_summary = {
            "eventos": len(log.events),
            "linhas_nao_interpretadas": len(log.unparsed),
            "sessoes": len(log.sessions),
            "niveis": log.stats.get("levels"),
            "modulos": log.stats.get("modules"),
            "categorias": log.stats.get("categories"),
            "codigos_unicos": log.stats.get("unique_macs"),
            "inversoes_de_relogio": inversions,
            "linhas_repetidas": log.stats.get("duplicated_line_occurrences"),
            "verificacao_do_codigo_de_linha": log.stats.get("mac_verification"),
        }
        checks.append(
            _check(
                "log_legivel",
                "Estrutura do log",
                VALIDADO if not log.unparsed else INCONSISTENTE,
                f"{len(log.events)} eventos; {len(log.unparsed)} linha(s) fora do formato",
            )
        )
        checks.append(
            _check(
                "log_relogio",
                "Monotonicidade dos horarios",
                VALIDADO if inversions == 0 else INCONSISTENTE,
                f"{inversions} inversao(oes) dentro das sessoes",
            )
        )
        checks.append(
            _check(
                "log_codigo_linha",
                "Codigo de 64 bits por linha",
                NAO_VERIFICAVEL,
                log.stats.get("mac_verification", ""),
            )
        )
        statuses.append(VALIDADO if not log.unparsed else INCONSISTENTE)
        statuses.append(VALIDADO if inversions == 0 else INCONSISTENTE)
        statuses.append(NAO_VERIFICAVEL)
    else:
        checks.append(_check("log_legivel", "Estrutura do log", NAO_VERIFICAVEL, "log ausente/ilegivel"))
        statuses.append(NAO_VERIFICAVEL)

    # ---------------- ordem da linha do tempo ----------------------------
    order_items: list[dict[str, Any]] = []
    if timeline:
        sequence = [
            "inicializacao",
            "preparacao",
            "abertura",
            "primeiro_voto",
            "ultimo_voto",
            "encerramento",
            "bu_relatorio",
            "bu_impressao",
            "bu_arquivo",
            "log_empacotado",
            "bu_assinatura",
        ]
        previous = None
        for key in sequence:
            milestone = timeline.milestone(key)
            if not milestone or not milestone.timestamp:
                continue
            current = milestone.timestamp
            status = VALIDADO
            if previous is not None and current < previous[1]:
                status = INCONSISTENTE
            order_items.append(
                {
                    "key": key,
                    "label": milestone.label,
                    "timestamp": current.isoformat(),
                    "status": status,
                    "previous": previous[0] if previous else None,
                }
            )
            if status == INCONSISTENTE:
                statuses.append(INCONSISTENTE)
            previous = (key, current)
        checks.append(
            _check(
                "ordem_temporal",
                "Ordem temporal dos marcos",
                worst_status([item["status"] for item in order_items]) if order_items else NAO_VERIFICAVEL,
                "abertura <= votos <= encerramento <= BU <= arquivo <= assinatura",
            )
        )

    # ---------------- classificacao final --------------------------------
    status = worst_status(statuses) if statuses else NAO_VERIFICAVEL
    if any(item["match"] is False for item in hash_checks):
        alteration = ALTERACAO_COMPROVAVEL
    elif any(item.status == INCONSISTENTE for item in checks):
        alteration = ALTERACAO_POSSIVEL
    elif not signature:
        alteration = ALTERACAO_NAO_VERIFICAVEL
    else:
        alteration = SEM_EVIDENCIA

    if signature and signature.hw.verification and signature.hw.verification.status == NAO_VALIDADO:
        authenticity = NAO_VALIDADO
    elif signature and signature.hw.verification and signature.hw.verification.status == VALIDADO:
        authenticity = VALIDADO
    else:
        authenticity = NAO_VERIFICAVEL

    return IntegrityReport(
        status=status,
        alteration=alteration,
        authenticity=authenticity,
        checks=checks,
        hash_checks=hash_checks,
        missing_signed_files=missing,
        signature_summary=signature_summary,
        bu_summary=bu_summary,
        log_summary=log_summary,
        timeline_order=order_items,
        limitations=limitations,
    )
