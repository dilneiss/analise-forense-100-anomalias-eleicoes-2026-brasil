"""Coerencia entre arquivos e entre a solicitacao e a evidencia.

Cada verificacao devolve um status objetivo. Divergencias geram achados com
severidade, sem converter divergencia em conclusao de fraude.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from ..models import (
    INCONSISTENTE,
    NAO_VERIFICAVEL,
    VALIDADO,
    CheckResult,
    Finding,
    UrnaKey,
    worst_status,
)
from ..parsers.bu import BU
from ..parsers.imgbu import ImgBU
from ..parsers.logd import LogParseResult
from ..parsers.rdv import RDV
from ..parsers.signature import SignatureFile
from .integrity import IntegrityReport
from .timeline import Timeline


@dataclass
class Requested:
    uf: Optional[str] = None
    municipio: Optional[int] = None
    municipio_nome: Optional[str] = None
    zona: Optional[int] = None
    secao: Optional[int] = None
    turno: Optional[int] = None
    data_eleicao: Optional[date] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "uf": self.uf,
            "municipio_codigo_tse": self.municipio,
            "municipio_nome": self.municipio_nome,
            "zona": self.zona,
            "secao": self.secao,
            "turno": self.turno,
            "data_eleicao": self.data_eleicao.isoformat() if self.data_eleicao else None,
        }


@dataclass
class ConsistencyReport:
    checks: list[CheckResult] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    matrix: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "checks": [check.as_dict() for check in self.checks],
            "findings": [finding.as_dict() for finding in self.findings],
            "matrix": self.matrix,
        }


def normalize_name(text: Optional[str]) -> str:
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    return " ".join(
        "".join(char for char in decomposed if not unicodedata.combining(char)).split()
    ).upper()


def _check(
    key: str,
    label: str,
    status: str,
    detail: str,
    evidence: Optional[list[str]] = None,
) -> CheckResult:
    return CheckResult(key=key, label=label, status=status, detail=detail, evidence=evidence or [])


def _compare_values(
    key: str,
    label: str,
    values: dict[str, Any],
    *,
    normalizer=None,
    severity: str = "ERROR",
    report: ConsistencyReport,
    note: str = "",
) -> CheckResult:
    present = {source: value for source, value in values.items() if value is not None}
    if normalizer:
        normalized = {source: normalizer(value) for source, value in present.items()}
    else:
        normalized = dict(present)
    distinct = set(normalized.values())
    if len(present) < 2:
        status = NAO_VERIFICAVEL
        detail = "fonte unica; sem segunda fonte para comparar"
    elif len(distinct) == 1:
        status = VALIDADO
        detail = "; ".join(f"{source}={value}" for source, value in present.items())
    else:
        status = INCONSISTENTE
        detail = "; ".join(f"{source}={value}" for source, value in present.items())
        report.findings.append(
            Finding(
                severity=severity,
                type=f"DIVERGENCIA_{key.upper()}",
                message=f"{label}: fontes divergem.",
                details=(detail + (" " + note if note else "")).strip(),
                evidence=list(present.keys()),
            )
        )
    check = _check(key, label, status, detail, list(present.keys()))
    report.checks.append(check)
    return check


def _ints_from_log(log: Optional[LogParseResult], label: str, day: Optional[date]) -> Optional[int]:
    if not log:
        return None
    values = []
    for event in log.events:
        if day and event.timestamp and event.timestamp.date() != day:
            continue
        if event.message.startswith(label):
            match = re.search(r"(\d+)", event.message.split(":", 1)[-1])
            if match:
                values.append(int(match.group(1)))
    return values[-1] if values else None


def _text_from_log(log: Optional[LogParseResult], prefix: str, day: Optional[date]) -> Optional[str]:
    if not log:
        return None
    values = []
    for event in log.events:
        if day and event.timestamp and event.timestamp.date() != day:
            continue
        if event.message.startswith(prefix):
            values.append(event.message.split(":", 1)[-1].strip())
    return values[-1] if values else None


def _bu_votes_by_cargo(bu: BU) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for eleicao in bu.eleicoes:
        for resultado in eleicao["resultados"]:
            for cargo in resultado["cargos"]:
                entry = out.setdefault(
                    cargo["codigo_cargo"],
                    {"nominal": {}, "legenda": {}, "branco": 0, "nulo": 0, "cargo_sem_candidato": 0, "total": 0},
                )
                for voto in cargo["votos"]:
                    entry["total"] += voto["quantidade"]
                    tipo = voto["tipo_voto_nome"]
                    if tipo == "nominal":
                        numero = (voto["identificacao_votavel"] or {}).get("numero")
                        if numero is not None:
                            entry["nominal"][numero] = entry["nominal"].get(numero, 0) + voto["quantidade"]
                    elif tipo == "legenda":
                        partido = (voto["identificacao_votavel"] or {}).get("partido")
                        if partido is not None:
                            entry["legenda"][partido] = entry["legenda"].get(partido, 0) + voto["quantidade"]
                    elif tipo == "branco":
                        entry["branco"] += voto["quantidade"]
                    elif tipo == "nulo":
                        entry["nulo"] += voto["quantidade"]
                    elif tipo == "cargo_sem_candidato":
                        entry["cargo_sem_candidato"] += voto["quantidade"]
    return out


def _rdv_votes_by_cargo(rdv: RDV) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for eleicao in rdv.eleicoes:
        for cargo in eleicao["cargos"]:
            entry = out.setdefault(
                cargo["codigo_cargo"],
                {"nominal": {}, "legenda": {}, "branco": 0, "nulo": 0, "cargo_sem_candidato": 0, "total": 0},
            )
            entry["nominal"] = {int(key): value for key, value in cargo["nominais_por_numero"].items()}
            entry["legenda"] = {int(key): value for key, value in cargo["legendas_por_partido"].items()}
            entry["branco"] = cargo["brancos"]
            entry["nulo"] = cargo["nulos"]
            entry["cargo_sem_candidato"] = cargo["cargo_sem_candidato"]
            entry["total"] += cargo["registros"]
    return out


def _candidate_comparison(bu: BU, rdv: RDV, report: ConsistencyReport) -> list[str]:
    bu_votes = _bu_votes_by_cargo(bu)
    rdv_votes = _rdv_votes_by_cargo(rdv)
    problems: list[str] = []
    for codigo in sorted(set(bu_votes) & set(rdv_votes)):
        b = bu_votes[codigo]
        r = rdv_votes[codigo]
        for kind in ("nominal", "legenda"):
            keys = sorted(set(b[kind]) | set(r[kind]))
            for key in keys:
                if b[kind].get(key, 0) != r[kind].get(key, 0):
                    problems.append(
                        f"cargo {codigo} {kind} {key}: BU={b[kind].get(key, 0)} RDV={r[kind].get(key, 0)}"
                    )
        for kind in ("branco", "nulo", "cargo_sem_candidato"):
            if b[kind] != r[kind]:
                problems.append(f"cargo {codigo} {kind}: BU={b[kind]} RDV={r[kind]}")
        if b["total"] != r["total"]:
            problems.append(f"cargo {codigo} total: BU={b['total']} RDV={r['total']}")
    for codigo in sorted(set(bu_votes) ^ set(rdv_votes)):
        problems.append(f"cargo {codigo}: presente em apenas um dos arquivos")
    status = VALIDADO if not problems else INCONSISTENTE
    report.checks.append(
        _check(
            "bu_rdv_votos",
            "Votos por cargo: BU x RDV",
            status,
            (
                f"{sum(len(item['nominal']) + len(item['legenda']) for item in bu_votes.values())} "
                "grupos nominal/legenda comparados; sem diferenca"
                if not problems
                else "; ".join(problems[:20])
            ),
            problems[:20],
        )
    )
    if problems:
        report.findings.append(
            Finding(
                severity="ERROR",
                type="DIVERGENCIA_BU_RDV",
                message="A contagem por cargo difere entre o BU e o RDV.",
                details=(
                    "; ".join(problems[:20])
                    + ". O RDV e o BU sao duas representacoes do mesmo conjunto "
                    "de votos; a diferenca pode ter origem operacional e exige "
                    "explicacao."
                ),
            )
        )
    return problems


def evaluate(
    *,
    urna: UrnaKey,
    requested: Requested,
    bu: Optional[BU],
    rdv: Optional[RDV],
    imgbu: Optional[ImgBU],
    log: Optional[LogParseResult],
    timeline: Optional[Timeline],
    signature: Optional[SignatureFile],
    integrity: IntegrityReport,
) -> ConsistencyReport:
    report = ConsistencyReport()
    for check in integrity.checks:
        if check.key in ("hashes_assinados", "bu_cadeia_hashes", "bu_aritmetica"):
            report.checks.append(check)
    day = timeline.election_date if timeline else (bu.abertura.date() if bu and bu.abertura else None)

    # -- identificacao: nome do arquivo x BU x BU impresso ----------------
    bu_ident = bu.identificacao if bu else {}
    bu_envelope_ident = bu.envelope.get("identificacao", {}) if bu else {}
    corr = (
        bu.urna["correspondencia"]["identificacao"]
        if bu and bu.urna and bu.urna.get("correspondencia")
        else {}
    )
    rdv_ident = rdv.identificacao if rdv else {}
    rdv_corr = (
        rdv.urna["correspondencia"]["identificacao"]
        if rdv and rdv.urna and rdv.urna.get("correspondencia")
        else {}
    )
    img = imgbu.summary if imgbu else {}
    log_municipio = _ints_from_log(log, "Município", day)
    log_zona = _ints_from_log(log, "Zona Eleitoral", day)
    log_local = _ints_from_log(log, "Local de Votação", day)
    log_secao = _ints_from_log(log, "Seção Eleitoral", day)
    if log_secao is None:
        log_secao = _ints_from_log(log, "Seção informada pelo operador", day)

    _compare_values(
        "municipio",
        "Município (código TSE)",
        {
            "nome do arquivo": urna.municipio,
            "BU (envelope)": bu_envelope_ident.get("municipio"),
            "BU (conteúdo)": bu_ident.get("municipio"),
            "BU (carga)": corr.get("municipio"),
            "RDV": rdv_ident.get("municipio"),
            "RDV (carga)": rdv_corr.get("municipio"),
            "BU impresso": img.get("municipio_codigo"),
            "log": log_municipio,
        },
        report=report,
    )
    _compare_values(
        "zona",
        "Zona eleitoral",
        {
            "nome do arquivo": urna.zona,
            "BU (envelope)": bu_envelope_ident.get("zona"),
            "BU (conteúdo)": bu_ident.get("zona"),
            "BU (carga)": corr.get("zona"),
            "RDV": rdv_ident.get("zona"),
            "RDV (carga)": rdv_corr.get("zona"),
            "BU impresso": img.get("zona"),
            "log": log_zona,
        },
        report=report,
    )
    _compare_values(
        "secao",
        "Seção eleitoral",
        {
            "nome do arquivo": urna.secao,
            "BU (envelope)": bu_envelope_ident.get("secao"),
            "BU (conteúdo)": bu_ident.get("secao"),
            "BU (carga)": corr.get("secao"),
            "RDV": rdv_ident.get("secao"),
            "RDV (carga)": rdv_corr.get("secao"),
            "BU impresso": img.get("secao"),
            "log": log_secao,
        },
        report=report,
    )
    _compare_values(
        "local",
        "Local de votação",
        {
            "BU (envelope)": bu_envelope_ident.get("local"),
            "BU (conteúdo)": bu_ident.get("local"),
            "BU impresso": img.get("local"),
            "log": log_local,
        },
        report=report,
    )

    urna_interna = (
        bu.urna["correspondencia"]["carga"]["numero_interno_urna"] if bu and bu.urna else None
    )
    cert_cn = signature.hw.certificate.common_name if signature and signature.hw.certificate else None
    _compare_values(
        "urna_id",
        "Número interno da urna",
        {
            "BU": urna_interna,
            "RDV": rdv.urna["correspondencia"]["carga"]["numero_interno_urna"] if rdv and rdv.urna else None,
            "BU impresso": img.get("numero_interno_urna"),
            "log": int(log.events[0].urna_id) if log and log.events and log.events[0].urna_id.isdigit() else None,
            "certificado (CN)": cert_cn,
        },
        normalizer=lambda value: (
            int(re.sub(r"\D", "", str(value))) if str(value).upper().startswith("UEAO") else value
        ),
        report=report,
        note="O CN do certificado segue o padrao UEAO + numero interno da urna.",
    )

    if bu and rdv:
        _compare_values(
            "versao_votacao",
            "Versão do software de votação",
            {
                "BU": bu.urna.get("versao_votacao") if bu.urna else None,
                "RDV": rdv.urna.get("versao_votacao") if rdv.urna else None,
                "log": _text_from_log(log, "Versão da aplicação", day),
            },
            normalizer=lambda value: str(value).strip(),
            report=report,
        )
        _compare_values(
            "codigo_carga",
            "Código de carga",
            {
                "BU": bu.historico_codigos_carga[-1] if bu.historico_codigos_carga else None,
                "RDV": rdv.historico_codigos_carga[-1] if rdv.historico_codigos_carga else None,
                "BU impresso": img.get("codigo_carga"),
            },
            report=report,
        )
        bu_eleicoes = {eleicao["id_eleicao"] for eleicao in bu.eleicoes}
        rdv_eleicoes = {eleicao["id_eleicao"] for eleicao in rdv.eleicoes}
        if bu_eleicoes == rdv_eleicoes:
            report.checks.append(
                _check(
                    "eleicoes",
                    "Identificadores de eleição (BU x RDV)",
                    VALIDADO,
                    "idPleito " + str(bu.cabecalho["id_eleitoral"]["valor"])
                    + "; eleicoes " + ", ".join(map(str, sorted(bu_eleicoes))),
                )
            )
        else:
            report.checks.append(
                _check(
                    "eleicoes",
                    "Identificadores de eleição (BU x RDV)",
                    INCONSISTENTE,
                    f"BU={sorted(bu_eleicoes)} RDV={sorted(rdv_eleicoes)}",
                )
            )
            report.findings.append(
                Finding(
                    severity="ERROR",
                    type="DIVERGENCIA_ELEICOES",
                    message="O conjunto de eleições difere entre BU e RDV.",
                    details=f"BU={sorted(bu_eleicoes)} RDV={sorted(rdv_eleicoes)}",
                )
            )
        _candidate_comparison(bu, rdv, report)

    # -- log x BU ---------------------------------------------------------
    if bu and log:
        bu_abertura = bu.abertura
        bu_encerramento = bu.encerramento
        log_abertura = timeline.milestone("abertura") if timeline else None
        log_encerramento = timeline.milestone("encerramento") if timeline else None
        _compare_values(
            "abertura_bu_log",
            "Abertura (BU x log)",
            {
                "BU": bu_abertura,
                "log": log_abertura.timestamp if log_abertura else None,
            },
            report=report,
            note="BU dataHoraAbertura e 'Urna pronta para receber votos'.",
        )
        _compare_values(
            "encerramento_bu_log",
            "Encerramento (BU x log)",
            {
                "BU": bu_encerramento,
                "log": log_encerramento.timestamp if log_encerramento else None,
            },
            report=report,
            note="BU dataHoraEncerramento e 'Procedimento de encerramento confirmado'.",
        )
        votos_log = sum(
            1
            for event in (timeline.events if timeline else [])
            if event.category == "VOTE.COMPUTED"
            and (day is None or (event.timestamp and event.timestamp.date() == day))
        )
        _compare_values(
            "comparecimento_bu_log",
            "Comparecimento (BU x votos computados no log)",
            {"BU": bu.comparecimento, "log": votos_log},
            report=report,
            note="Cada eleitor habilitado gera exatamente um evento de voto computado.",
        )

    # -- BU x BU impresso (spool) -----------------------------------------
    if bu and imgbu:
        summary = imgbu.summary
        _compare_values(
            "aptos_bu_impresso",
            "Eleitores aptos (BU x BU impresso)",
            {
                "BU": bu.eleicoes[0]["qtd_eleitores_aptos"] if bu.eleicoes else None,
                "BU impresso": summary.get("aptos"),
            },
            report=report,
        )
        _compare_values(
            "comparecimento_bu_impresso",
            "Comparecimento (BU x BU impresso)",
            {"BU": bu.comparecimento, "BU impresso": summary.get("comparecimento")},
            report=report,
        )
        bu_abertura_txt = bu.abertura.strftime("%d/%m/%Y %H:%M:%S") if bu.abertura else None
        impresso_abertura = None
        if summary.get("data_abertura_impressa") and summary.get("hora_abertura_impressa"):
            impresso_abertura = (
                f"{summary['data_abertura_impressa']} {summary['hora_abertura_impressa']}"
            )
        _compare_values(
            "abertura_bu_impresso",
            "Abertura (BU x BU impresso)",
            {"BU": bu_abertura_txt, "BU impresso": impresso_abertura},
            report=report,
        )
        bu_fechamento_txt = bu.encerramento.strftime("%d/%m/%Y %H:%M:%S") if bu.encerramento else None
        impresso_fechamento = None
        if summary.get("data_fechamento_impressa") and summary.get("hora_fechamento_impressa"):
            impresso_fechamento = (
                f"{summary['data_fechamento_impressa']} {summary['hora_fechamento_impressa']}"
            )
        _compare_values(
            "encerramento_bu_impresso",
            "Encerramento (BU x BU impresso)",
            {"BU": bu_fechamento_txt, "BU impresso": impresso_fechamento},
            report=report,
        )
        bu_totals = {}
        for eleicao in bu.eleicoes:
            for resultado in eleicao["resultados"]:
                for cargo in resultado["cargos"]:
                    bu_totals[cargo["codigo_cargo"]] = {
                        "nominais": cargo["tipos_voto"].get("nominal", 0),
                        "legenda": cargo["tipos_voto"].get("legenda", 0),
                        "brancos": cargo["tipos_voto"].get("branco", 0),
                        "nulos": cargo["tipos_voto"].get("nulo", 0),
                        "total_apurado": cargo["total_votos"],
                    }
        problems = []
        for office, values in imgbu.offices.items():
            codigo = values["codigo_cargo_sugerido"]
            structured = bu_totals.get(codigo)
            if not structured:
                problems.append(f"{office}: sem cargo correspondente no BU")
                continue
            for key in ("nominais", "legenda", "brancos", "nulos", "total_apurado"):
                if values.get(key) is not None and structured.get(key) != values.get(key):
                    problems.append(
                        f"{office} {key}: BU={structured.get(key)} impresso={values.get(key)}"
                    )
        report.checks.append(
            _check(
                "bu_impresso_totais",
                "Totais por cargo: BU x BU impresso",
                VALIDADO if not problems else INCONSISTENTE,
                "; ".join(problems[:20]) if problems else "todos os totais conferem",
            )
        )
        if problems:
            report.findings.append(
                Finding(
                    severity="ERROR",
                    type="DIVERGENCIA_BU_IMPRESSO",
                    message="Os totais do BU estruturado diferem do BU impresso.",
                    details="; ".join(problems[:20]),
                )
            )
    # -- log x imagem -----------------------------------------------------
    if imgbu and log:
        _compare_values(
            "municipio_nome",
            "Nome do município (BU impresso x tabela oficial)",
            {
                "BU impresso": img.get("municipio_nome"),
                "tabela TSE": requested.municipio_nome,
            },
            normalizer=normalize_name,
            severity="WARNING",
            report=report,
        )

    # -- turno e data -----------------------------------------------------
    turn_values = {
        "log": timeline.turn if timeline else None,
        "BU impresso": img.get("turno"),
        "solicitacao": requested.turno,
    }
    _compare_values(
        "turno",
        "Turno",
        turn_values,
        report=report,
        note=(
            "O turno nao existe como campo do BU; e lido do texto do log e do "
            "BU impresso. A solicitacao e uma expectativa externa."
        ),
    )
    requested_date = requested.data_eleicao
    date_values = {
        "BU (abertura)": bu.abertura.date() if bu and bu.abertura else None,
        "BU impresso": (
            datetime.strptime(img["data_eleicao"], "%d/%m/%Y").date()
            if img.get("data_eleicao")
            else None
        ),
        "log": day,
        "solicitacao": requested_date,
    }
    _compare_values(
        "data_eleicao",
        "Data da eleição",
        date_values,
        report=report,
        note="Divergencia entre a data pedida e a data dos arquivos nao e adulteracao; e premissa incorreta.",
    )

    # -- premissa: UF/municipio/zona/secao pedidos ------------------------
    if requested.uf and requested.uf.lower() != urna.uf.lower():
        report.findings.append(
            Finding(
                severity="ERROR",
                type="PREMISSA_DIVERGENTE",
                message="A UF solicitada difere da UF dos arquivos analisados.",
                details=f"solicitacao={requested.uf.upper()} arquivos={urna.uf.upper()}",
            )
        )
    for label, requested_value, actual in (
        ("municipio", requested.municipio, urna.municipio),
        ("zona", requested.zona, urna.zona),
        ("secao", requested.secao, urna.secao),
    ):
        if requested_value is not None and requested_value != actual:
            report.findings.append(
                Finding(
                    severity="ERROR",
                    type="PREMISSA_DIVERGENTE",
                    message=f"A {label} solicitada difere da {label} dos arquivos analisados.",
                    details=f"solicitacao={requested_value} arquivos={actual}",
                )
            )

    # -- assinatura x modelo da urna --------------------------------------
    if signature and signature.model and log:
        log_model = _text_from_log(log, "Identificação do Modelo de Urna", day)
        if log_model:
            _compare_values(
                "modelo_urna",
                "Modelo da urna (log x assinatura)",
                {"log": log_model.replace("UE", "UE").strip(), "assinatura": signature.model},
                report=report,
            )

    # -- arquivos ausentes -------------------------------------------------
    if integrity.missing_signed_files:
        report.findings.append(
            Finding(
                severity="INFO",
                type="ARQUIVOS_ASSINADOS_AUSENTES",
                message=(
                    f"{len(integrity.missing_signed_files)} arquivo(s) listado(s) "
                    "na assinatura nao estao no conjunto fornecido."
                ),
                details=(
                    ", ".join(integrity.missing_signed_files)
                    + ". A ausencia impede conferir o hash desses arquivos; nao "
                    "indica alteracao dos arquivos presentes."
                ),
            )
        )
    return report

# ---------------------------------------------------------------------------
# matriz de relacoes
# ---------------------------------------------------------------------------


def _status_of(report: ConsistencyReport, key: str) -> str:
    for check in report.checks:
        if check.key == key:
            return check.status
    return NAO_VERIFICAVEL


def _statuses_of(report: ConsistencyReport, keys: list[str]) -> str:
    return worst_status([_status_of(report, key) for key in keys])


def build_matrix(report: ConsistencyReport, integrity: IntegrityReport) -> list[dict[str, Any]]:
    matrix = [
        {
            "relacao": "BU <-> RDV",
            "status": _statuses_of(report, ["bu_rdv_votos", "eleicoes"]),
            "detalhe": "contagem por cargo e total de registros",
        },
        {
            "relacao": "BU <-> LOG",
            "status": _statuses_of(
                report,
                ["abertura_bu_log", "encerramento_bu_log", "comparecimento_bu_log", "secao"],
            ),
            "detalhe": "horarios de abertura/encerramento e votos computados",
        },
        {
            "relacao": "BU <-> BU impresso",
            "status": _status_of(report, "bu_impresso_totais"),
            "detalhe": "totais por cargo e identificacao",
        },
        {
            "relacao": "ARQUIVOS <-> HASHES ASSINADOS",
            "status": _status_of(report, "hashes_assinados"),
            "detalhe": "SHA-512 de cada arquivo contra o valor da assinatura",
        },
        {
            "relacao": "ASSINATURA DIGITAL",
            "status": integrity.authenticity,
            "detalhe": "assinatura de hardware e cadeia de certificacao",
        },
        {
            "relacao": "TIMELINE",
            "status": worst_status([item["status"] for item in integrity.timeline_order])
            if integrity.timeline_order
            else NAO_VERIFICAVEL,
            "detalhe": "ordem dos marcos e monotonicidade do log",
        },
    ]
    report.matrix = matrix
    return matrix
