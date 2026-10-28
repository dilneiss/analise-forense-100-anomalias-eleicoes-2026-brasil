"""Orquestracao da analise: inventario, parsers, verificacoes e relatorios."""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from cryptography.hazmat.primitives import serialization

from . import TOOL_NAME, __version__
from .analysis import consistency as consistency_mod
from .analysis import integrity as integrity_mod
from .analysis.timeline import SOURCE_LOG, Timeline, build_timeline
from .containers.jez import ContainerError, ContainerInfo, LogPayload, read_log_payloads
from .crypto.hashes import format_size, hash_file
from .crypto.signatures import load_ca_bundle
from .models import (
    ALTERACAO_COMPROVAVEL,
    ALTERACAO_NAO_VERIFICAVEL,
    ALTERACAO_POSSIVEL,
    INCONSISTENTE,
    NAO_VALIDADO,
    NAO_VERIFICAVEL,
    SEM_EVIDENCIA,
    VALIDADO,
    EvidenceFile,
    Finding,
    UrnaKey,
)
from .municipios import Municipio
from .parsers.bu import BU, BULegivelError, parse_bu
from .parsers.imgbu import ImgBU, parse_imgbu
from .parsers.logd import LogParseResult, merge_results, parse_text
from .parsers.rdv import RDV, RDVLegivelError, parse_rdv
from .parsers.signature import (
    AssinaturaIlegivelError,
    SignatureFile,
    parse_signature,
    verify_signature,
)
from .reports import json_report

MAX_FILE_BYTES = 128 * 1024 * 1024
PHASES = {"all", "hash", "timeline", "verify", "report"}


class AnalysisError(RuntimeError):
    """Falha de configuracao ou de selecao da urna."""


@dataclass
class Config:
    input_dir: Path
    output_dir: Path
    uf: Optional[str] = None
    municipio: Optional[int] = None
    municipio_nome: Optional[str] = None
    zona: Optional[int] = None
    secao: Optional[int] = None
    turno: Optional[int] = None
    data_eleicao: Optional[date] = None
    ca_paths: list[Path] = field(default_factory=list)
    municipios_table: Optional[dict[Any, Any]] = None
    hash_scope: str = "all"
    only: set[str] = field(default_factory=lambda: {"all"})
    quiet: bool = False
    write_html: bool = True
    fast: bool = False
    def wants(self, phase: str) -> bool:
        return "all" in self.only or phase in self.only


@dataclass
class Result:
    report: dict[str, Any]
    output_dir: Path
    console: str
    findings: list[Finding]
    integrity: integrity_mod.IntegrityReport
    consistency: consistency_mod.ConsistencyReport
    timeline: Timeline


def _log(config: Config, message: str) -> None:
    if not config.quiet:
        print(message, file=sys.stderr, flush=True)


def _write_json(path: Path, data: Any) -> None:
    json_report.write(path, data)


def _safe_name(name: str) -> str:
    return (
        name.replace("!", "__")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("..", "_")
    )


def _read_bytes(path: Path, kind: str) -> bytes:
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise AnalysisError(
            f"{path.name}: {size} bytes excede o limite de {MAX_FILE_BYTES}"
        )
    data = path.read_bytes()
    return data


def _load_previous(output_dir: Path) -> Optional[dict[str, Any]]:
    path = output_dir / "manifest.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _compare_manifests(
    previous: Optional[dict[str, Any]], current_files: list[EvidenceFile]
) -> dict[str, Any]:
    current = {item.relpath: item for item in current_files}
    if not previous or not previous.get("files"):
        return {
            "status": "primeira_execucao",
            "previous_analysis_at": None,
            "changed": [],
            "added": [],
            "removed": [],
            "unchanged": 0,
        }
    old = {item["path"]: item for item in previous.get("files", []) if "path" in item}
    changed = []
    for path, item in current.items():
        other = old.get(path)
        if other and item.sha256 and other.get("sha256") and item.sha256 != other["sha256"]:
            changed.append(
                {
                    "path": path,
                    "previous_sha256": other["sha256"],
                    "current_sha256": item.sha256,
                }
            )
    added = sorted(set(current) - set(old))
    removed = sorted(set(old) - set(current))
    return {
        "status": "comparado",
        "previous_analysis_at": previous.get("analysis_started_at"),
        "changed": changed,
        "added": added[:500],
        "removed": removed[:500],
        "added_count": len(added),
        "removed_count": len(removed),
        "unchanged": sum(
            1
            for path, item in current.items()
            if path in old
            and item.sha256
            and old[path].get("sha256") == item.sha256
        ),
    }


def _inventory(
    files: list[EvidenceFile],
    urnas: dict[UrnaKey, dict[str, EvidenceFile]],
    target: UrnaKey,
) -> dict[str, Any]:
    by_ext = Counter(item.ext or "(sem extensao)" for item in files)
    by_type = Counter(item.detected_type for item in files)
    by_kind = Counter(item.kind for item in files if item.kind)
    by_uf = Counter(item.urna.uf for item in files if item.urna)
    kinds = ("bu", "rdv", "log", "vota", "imgbu")
    coverage = {
        kind: sum(1 for entry in urnas.values() if kind in entry) for kind in kinds
    }
    absence_samples = []
    absence_counts: Counter[str] = Counter()
    for key, entry in urnas.items():
        missing = [kind for kind in kinds if kind not in entry]
        if missing:
            absence_counts.update(missing)
            if len(absence_samples) < 200:
                absence_samples.append(
                    {"urna": key.compact, "faltando": missing}
                )
    non_urna = [
        item.as_dict(include_hashes=False)
        for item in files
        if item.urna is None
    ]
    return {
        "summary": {
            "files_total": len(files),
            "bytes_total": sum(item.size for item in files),
            "bytes_total_human": format_size(sum(item.size for item in files)),
            "by_extension": dict(sorted(by_ext.items(), key=lambda kv: -kv[1])),
            "by_detected_type": dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
            "by_kind": dict(sorted(by_kind.items(), key=lambda kv: -kv[1])),
            "by_uf": dict(sorted(by_uf.items())),
            "urnas_total": len(urnas),
            "urnas_incompletas": sum(
                1 for entry in urnas.values() if len([k for k in kinds if k in entry]) < len(kinds)
            ),
            "cobertura_por_kind": coverage,
            "ausencias_por_kind": dict(absence_counts),
        },
        "target": {
            **target.as_dict(),
            "files": [item.as_dict() for item in urnas.get(target, {}).values()],
        },
        "urnas_com_ausencia": absence_samples,
        "non_urna_files": non_urna,
    }


def _findings_from_parsers(
    *,
    errors: list[dict[str, str]],
    container: Optional[ContainerInfo],
    integrity: integrity_mod.IntegrityReport,
    log: Optional[LogParseResult],
    target_files: dict[str, EvidenceFile],
    comparison: dict[str, Any],
    post_run_ok: bool,
    municipio: Optional[Municipio],
) -> list[Finding]:
    findings: list[Finding] = []
    for error in errors:
        findings.append(
            Finding(
                severity="ERROR",
                type="ARQUIVO_ILEGIVEL",
                message=f"Nao foi possivel interpretar {error['file']}.",
                details=error["reason"],
                evidence=[error["file"]],
            )
        )
    for kind, label in (
        ("bu", "BU (-bu.dat)"),
        ("rdv", "RDV (-rdv.dat)"),
        ("log", "log (-log.jez)"),
        ("vota", "assinatura (-vota.vsc)"),
        ("imgbu", "BU impresso (-imgbu.dat)"),
    ):
        if kind not in target_files:
            findings.append(
                Finding(
                    severity="WARNING",
                    type="ARQUIVO_AUSENTE",
                    message=f"Arquivo esperado ausente: {label}.",
                    details=(
                        "Sem esse arquivo, as verificacoes que dependem dele nao "
                        "podem ser feitas; a ausencia nao prova alteracao."
                    ),
                )
            )
    if container:
        for note in container.notes:
            findings.append(
                Finding(
                    severity="INFO",
                    type="CONTAINER",
                    message="Observacao no container do log.",
                    details=note,
                    evidence=[container.source],
                )
            )
    if any(item.get("match") is False for item in integrity.hash_checks):
        divergentes = [
            item["file"] for item in integrity.hash_checks if item.get("match") is False
        ]
        findings.append(
            Finding(
                severity="ERROR",
                type="HASH_DIVERGENTE",
                message=(
                    "O SHA-512 de um arquivo nao corresponde ao hash registrado "
                    "no arquivo de assinatura."
                ),
                details=(
                    "Arquivos: "
                    + ", ".join(divergentes)
                    + ". Isso demonstra que o conteudo publicado difere do que a "
                    "urna registrou como assinado; nao identifica a causa nem o autor."
                ),
                evidence=divergentes,
            )
        )
    for chain in integrity.bu_summary.get("cadeia_hashes", []) if integrity.bu_summary else []:
        if chain.get("status") != VALIDADO:
            findings.append(
                Finding(
                    severity="ERROR",
                    type="CADEIA_HASHES_BU",
                    message="A cadeia de hashes interna do BU nao confere.",
                    details=json.dumps(chain, ensure_ascii=False)[:2000],
                )
            )
    if integrity.authenticity == NAO_VERIFICAVEL:
        findings.append(
            Finding(
                severity="INFO",
                type="ASSINATURA_NAO_VERIFICAVEL",
                message=(
                    "ASSINATURA PRESENTE, MAS NAO FOI POSSIVEL VALIDAR "
                    "criptograficamente."
                ),
                details="; ".join(integrity.limitations)
                or "motivo nao detalhado",
            )
        )
    elif integrity.authenticity == NAO_VALIDADO:
        findings.append(
            Finding(
                severity="ERROR",
                type="ASSINATURA_INVALIDA",
                message="A verificacao criptografica da assinatura falhou.",
                details="A assinatura nao confere com a chave publica do certificado.",
            )
        )
    if log:
        if log.unparsed:
            findings.append(
                Finding(
                    severity="WARNING",
                    type="LOG_LINHAS_NAO_INTERPRETADAS",
                    message=f"{len(log.unparsed)} linha(s) do log fora do formato.",
                    details="As linhas foram preservadas em timeline.json.",
                )
            )
        inversions = (integrity.log_summary or {}).get("inversoes_de_relogio", 0)
        if inversions:
            findings.append(
                Finding(
                    severity="WARNING",
                    type="RELATORIO_RELOGIO_INVERTIDO",
                    message=f"{inversions} inversao(oes) de horario dentro de sessoes do log.",
                    details=(
                        "Um horario menor que o anterior pode indicar ajuste de "
                        "relogio ou inconsistencia; exige contexto."
                    ),
                )
            )
    if comparison.get("status") == "comparado" and comparison.get("changed"):
        findings.append(
            Finding(
                severity="ERROR",
                type="EVIDENCIA_ALTERADA_ENTRE_EXECUCOES",
                message=(
                    f"{len(comparison['changed'])} arquivo(s) mudaram de hash "
                    "desde a analise anterior."
                ),
                details=", ".join(item["path"] for item in comparison["changed"][:20]),
            )
        )
    if not post_run_ok:
        findings.append(
            Finding(
                severity="ERROR",
                type="EVIDENCIA_MUDOU_DURANTE_ANALISE",
                message=(
                    "O hash de um arquivo da urna mudou durante a execucao."
                ),
                details=(
                    "Isso indica escrita concorrente no diretorio de evidencia; "
                    "repita a analise em uma copia estavel."
                ),
            )
        )
    if municipio is None:
        findings.append(
            Finding(
                severity="INFO",
                type="MUNICIPIO_NAO_RESOLVIDO",
                message="Nome do municipio nao resolvido.",
                details=(
                    "O nome nao existe nos arquivos da urna. Informe "
                    "--municipios-csv com a tabela oficial do TSE para resolve-lo."
                ),
            )
        )
    return findings


def _dedupe(findings: list[Finding]) -> list[Finding]:
    seen = set()
    out = []
    for finding in findings:
        key = (finding.severity, finding.type, finding.message, finding.details)
        if key in seen:
            continue
        seen.add(key)
        out.append(finding)
    severity_order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    out.sort(key=lambda item: (severity_order.get(item.severity, 3), item.type))
    return out


def _conclusion(
    *,
    urna: UrnaKey,
    municipio: Optional[Municipio],
    timeline: Timeline,
    bu: Optional[BU],
    integrity: integrity_mod.IntegrityReport,
    consistency: consistency_mod.ConsistencyReport,
    findings: list[Finding],
) -> dict[str, Any]:
    abertura = timeline.milestone("abertura")
    encerramento = timeline.milestone("encerramento")
    partes = []
    if abertura and abertura.timestamp and encerramento and encerramento.timestamp:
        partes.append(
            "A votacao foi aberta em "
            f"{abertura.timestamp.strftime('%d/%m/%Y %H:%M:%S')} e encerrada em "
            f"{encerramento.timestamp.strftime('%d/%m/%Y %H:%M:%S')}."
        )
    if bu:
        partes.append(
            f"O BU declara comparecimento {bu.comparecimento} e "
            f"{len(bu.eleicoes)} eleicao(oes)."
        )
    if integrity.alteration == SEM_EVIDENCIA:
        partes.append(
            "Nenhuma evidencia de alteracao foi encontrada nas verificacoes "
            "disponiveis."
        )
    elif integrity.alteration == ALTERACAO_COMPROVAVEL:
        partes.append(
            "Ha uma referencia criptografica que nao corresponde ao arquivo "
            "analisado (ver alertas)."
        )
    elif integrity.alteration == ALTERACAO_POSSIVEL:
        partes.append(
            "Ha inconsistencias sem referencia criptografica suficiente para "
            "afirmar alteracao."
        )
    else:
        partes.append(
            "Nao foi possivel verificar a autenticidade criptografica do conjunto."
        )
    nao_verificado = list(integrity.limitations)
    if any(f.severity == "ERROR" and f.type.startswith("DIVERGENCIA") for f in findings):
        nao_verificado.append(
            "Ha divergencias entre fontes; ver a secao de alertas."
        )
    return {
        "resumo": " ".join(partes),
        "alteracao": integrity.alteration,
        "integridade": integrity.status,
        "autenticidade": integrity.authenticity,
        "identificacao": {
            **urna.as_dict(),
            "municipio_nome": municipio.nome if municipio else None,
        },
        "respostas": {
            "o_que_aconteceu": " ".join(partes),
            "horario_de_encerramento": (
                encerramento.timestamp.isoformat()
                if encerramento and encerramento.timestamp
                else None
            ),
            "evidencia_de_alteracao": integrity.alteration,
            "nao_foi_possivel_verificar": nao_verificado,
        },
        "limitacoes": integrity.limitations,
    }


def _console(report: dict[str, Any]) -> str:
    ident = report["conclusion"]["identificacao"]
    timeline = report["timeline"]
    milestones = {item["key"]: item for item in timeline["milestones"]}
    bu = report.get("bu") or {}
    integrity = report["integrity"]
    matrix = report["consistency"]["matrix"]
    findings = report["findings"]

    def ts(key: str, fmt: str = "%H:%M:%S") -> str:
        item = milestones.get(key)
        if not item or not item.get("timestamp"):
            return "NAO IDENTIFICADO"
        return datetime.fromisoformat(item["timestamp"]).strftime(fmt)

    def dur(seconds: Optional[int]) -> str:
        if seconds is None:
            return "NAO IDENTIFICADO"
        seconds = int(seconds)
        return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"

    alertas = [item for item in findings if item["severity"] in ("ERROR", "WARNING")]
    info = [item for item in findings if item["severity"] == "INFO"]
    lines = [
        "========================================",
        "ANALISE DA URNA",
        "========================================",
        "",
        f"Municipio : {ident.get('municipio_nome') or '(nome nao resolvido)'}"
        f" (codigo TSE {ident['municipio_codigo_tse']})",
        f"UF        : {ident['uf']}",
        f"Zona      : {ident['zona']:04d}",
        f"Secao     : {ident['secao']:04d}",
        f"Turno     : {timeline.get('turn') if timeline.get('turn') is not None else 'NAO IDENTIFICADO'}"
        + (" (deduzido)" if timeline.get("turn") is not None else ""),
        f"Data      : {report['timeline'].get('election_date') or 'NAO IDENTIFICADA'}",
        "",
        "----------------------------------------",
        "VOTACAO",
        "----------------------------------------",
        "",
        f"Inicio da votacao : {ts('abertura', '%d/%m/%Y %H:%M:%S')}",
        f"Encerramento      : {ts('encerramento', '%d/%m/%Y %H:%M:%S')}",
        f"Duracao           : {dur(timeline.get('voting', {}).get('duracao_votacao_segundos'))}",
        f"Votos computados  : {timeline.get('voting', {}).get('votos_computados', 'NAO IDENTIFICADO')}",
        "",
        "----------------------------------------",
        "BOLETIM DE URNA",
        "----------------------------------------",
        "",
    ]
    if bu:
        eleicoes = bu.get("eleicoes", [])
        cargos = [
            cargo
            for eleicao in eleicoes
            for resultado in eleicao.get("resultados", [])
            for cargo in resultado.get("cargos", [])
        ]
        president = next(
            (cargo for cargo in cargos if cargo["codigo_cargo"] == 1), None
        )
        nominal = sum(cargo["tipos_voto"].get("nominal", 0) for cargo in cargos)
        brancos = sum(cargo["tipos_voto"].get("branco", 0) for cargo in cargos)
        nulos = sum(cargo["tipos_voto"].get("nulo", 0) for cargo in cargos)
        lines += [
            f"Aptos            : {eleicoes[0]['qtd_eleitores_aptos'] if eleicoes else 'NAO IDENTIFICADO'}",
            f"Comparecimento   : {bu.get('comparecimento')}",
            f"Votos nominais   : {nominal}",
            f"Brancos          : {brancos}",
            f"Nulos            : {nulos}",
        ]
        if president:
            tipos = president.get("tipos_voto", {})
            lines.append(
                f"Presidente       : {president['total_votos']} votos "
                f"({tipos.get('nominal', 0)} nominais, "
                f"{tipos.get('branco', 0)} brancos, {tipos.get('nulo', 0)} nulos)"
            )
        lines += [
            f"BU emitido       : {ts('bu_relatorio', '%d/%m/%Y %H:%M:%S')}",
            f"BU impresso      : {ts('bu_impressao', '%d/%m/%Y %H:%M:%S')}",
            f"bu.dat gerado    : {ts('bu_arquivo', '%d/%m/%Y %H:%M:%S')}",
        ]
    else:
        lines.append("BU nao disponivel ou ilegivel.")
    lines += [
        "",
        "----------------------------------------",
        "INTEGRIDADE",
        "----------------------------------------",
        "",
        f"Arquivos analisados : {len(report['target']['files'])}",
        f"Hashes SHA-256/512  : {len(report['target']['files'])} arquivos",
        f"Assinaturas         : {len((report.get('signatures') or {}).get('assinatura_hardware', {}).get('arquivos', []))} arquivo(s) assinado(s) listados",
        f"Hash assinado OK    : {sum(1 for item in integrity['hash_checks'] if item.get('match'))}/{sum(1 for item in integrity['hash_checks'] if item.get('match') is not None)} presentes",
        f"Classificacao       : {integrity['status']}",
        f"Autenticidade       : {integrity['authenticity']}",
        "",
        "----------------------------------------",
        "CONSISTENCIA",
        "----------------------------------------",
        "",
    ]
    labels = {
        VALIDADO: "OK",
        INCONSISTENTE: "INCONSISTENTE",
        NAO_VERIFICAVEL: "NAO VERIFICADO",
        NAO_VALIDADO: "NAO VALIDADO",
    }
    for item in matrix:
        lines.append(f"{item['relacao']:<32} {labels.get(item['status'], item['status'])}")
    lines += [
        "",
        "----------------------------------------",
        "CONCLUSAO",
        "----------------------------------------",
        "",
        report["conclusion"]["resumo"],
    ]
    if alertas:
        lines += ["", "ATENCAO", ""]
        for item in alertas:
            lines.append(f"[{item['severity']}] {item['message']}")
            if item.get("details"):
                lines.append(f"    {item['details'][:500]}")
            lines.append(
                "    Isso NAO permite concluir, isoladamente, que houve adulteracao."
            )
        lines += [
            "",
            "Dados adicionais necessarios para uma conclusao:",
        ]
        for item in report["conclusion"]["respostas"]["nao_foi_possivel_verificar"]:
            lines.append(f"  - {item}")
    else:
        lines += [
            "",
            "Nenhuma inconsistencia foi encontrada nos dados disponiveis.",
        ]
    if info:
        lines += ["", "Observacoes:"]
        for item in info:
            lines.append(f"  - {item['message']}")
    lines += ["", "========================================"]
    return "\n".join(lines)


def run(config: Config, *, municipio: Optional[Municipio] = None) -> Result:
    started = datetime.now()
    input_dir = config.input_dir.resolve()
    output_dir = config.output_dir.resolve()
    if not input_dir.is_dir():
        raise AnalysisError(f"entrada nao e diretorio: {input_dir}")
    if output_dir == input_dir or input_dir in output_dir.parents:
        raise AnalysisError(
            "o diretorio de saida nao pode ficar dentro da evidencia; "
            "escolha uma pasta fora da entrada"
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    _log(config, f"[1/6] Inventariando {input_dir} ...")
    from .scanner import group_urnas, scan, scan_target, select_urna

    def progress(count: int, total: int) -> None:
        _log(config, f"      {count} arquivos, {format_size(total)}")

    compute_all = (config.hash_scope == "all") and not config.fast
    if config.fast:
        parts = []
        if config.uf:
            parts.append(config.uf.lower())
        if config.municipio:
            parts.append(f"{config.municipio:05d}")
        if config.zona is not None:
            parts.append(f"{config.zona:04d}")
        if config.secao is not None:
            parts.append(f"{config.secao:04d}")
        pattern = "".join(parts)
        if not pattern:
            raise AnalysisError("--fast requer pelo menos --secao ou outro filtro para identificar a urna")
        scanned = scan_target(input_dir, pattern, exclude=output_dir)
    else:
        scanned = scan(input_dir, exclude=output_dir, compute_hashes=compute_all, progress=progress)
    urnas = group_urnas(scanned.files)
    if not urnas:
        raise AnalysisError(
            "nenhum arquivo no padrao de nomes da urna foi encontrado "
            "(o{municipio}{uf}{zona}{secao}-{tipo}.{ext})"
        )
    matches = select_urna(
        urnas,
        uf=config.uf,
        municipio=config.municipio,
        zona=config.zona,
        secao=config.secao,
    )
    if not matches:
        raise AnalysisError(
            "nenhuma urna corresponde aos filtros informados; use --list para ver "
            f"as {len(urnas)} urnas disponiveis"
        )
    if len(matches) > 1:
        sample = ", ".join(key.compact for key in matches[:12])
        raise AnalysisError(
            f"{len(matches)} urnas correspondem aos filtros ({sample}...); "
            "informe --municipio e/ou --zona/--secao para selecionar uma"
        )
    target = matches[0]
    target_files = urnas[target]
    _log(config, f"      urna selecionada: {target.compact}")
    if municipio is None and config.municipios_table:
        municipio = config.municipios_table.get((target.uf, target.municipio))

    if not compute_all:
        for item in target_files.values():
            if not item.sha256:
                hashes = hash_file(item.abs_path)  # type: ignore[arg-type]
                item.sha256 = hashes["sha256"]
                item.sha512 = hashes["sha512"]

    previous = _load_previous(output_dir)
    comparison = _compare_manifests(previous, scanned.files)

    _log(config, "[2/6] Lendo containers e parsers ...")
    errors: list[dict[str, str]] = []
    container: Optional[ContainerInfo] = None
    payloads: list[LogPayload] = []
    log: Optional[LogParseResult] = None
    bu: Optional[BU] = None
    rdv: Optional[RDV] = None
    imgbu: Optional[ImgBU] = None
    signature: Optional[SignatureFile] = None

    if "log" in target_files:
        try:
            container, payloads = read_log_payloads(target_files["log"].abs_path)
            parsed = [
                parse_text(payload.text, source=payload.entry_path)
                for payload in payloads
            ]
            log = merge_results(parsed) if parsed else None
        except (ContainerError, OSError, ValueError) as exc:
            errors.append({"file": target_files["log"].relpath, "reason": str(exc)})

    if "bu" in target_files:
        try:
            bu = parse_bu(_read_bytes(target_files["bu"].abs_path, "bu"))
        except (BULegivelError, OSError, ValueError) as exc:
            errors.append({"file": target_files["bu"].relpath, "reason": str(exc)})
    if "rdv" in target_files:
        try:
            rdv = parse_rdv(_read_bytes(target_files["rdv"].abs_path, "rdv"))
        except (RDVLegivelError, OSError, ValueError) as exc:
            errors.append({"file": target_files["rdv"].relpath, "reason": str(exc)})
    if "imgbu" in target_files:
        try:
            imgbu = parse_imgbu(_read_bytes(target_files["imgbu"].abs_path, "imgbu"))
        except (BULegivelError, OSError, ValueError) as exc:
            errors.append({"file": target_files["imgbu"].relpath, "reason": str(exc)})

    present_names = {item.relpath.split("/")[-1]: item.abs_path for item in target_files.values()}
    if "vota" in target_files:
        try:
            signature = parse_signature(_read_bytes(target_files["vota"].abs_path, "vota"))
            authorities = load_ca_bundle(config.ca_paths)
            signature = verify_signature(
                signature,
                present_files=present_names,
                election_date=(bu.abertura if bu and bu.abertura else None),
                authorities=authorities,
            )
        except (AssinaturaIlegivelError, OSError, ValueError) as exc:
            errors.append({"file": target_files["vota"].relpath, "reason": str(exc)})

    _log(config, "[3/6] Construindo linha do tempo ...")
    timeline = build_timeline(log or LogParseResult(), bu=bu, imgbu=imgbu, signature=signature)

    _log(config, "[4/6] Verificando integridade e coerencia ...")
    integrity = integrity_mod.evaluate(
        target_files=target_files,
        signature=signature,
        bu=bu,
        rdv=rdv,
        log=log,
        timeline=timeline,
    )
    requested = consistency_mod.Requested(
        uf=config.uf or target.uf,
        municipio=config.municipio or target.municipio,
        municipio_nome=config.municipio_nome or (municipio.nome if municipio else None),
        zona=config.zona if config.zona is not None else target.zona,
        secao=config.secao if config.secao is not None else target.secao,
        turno=config.turno,
        data_eleicao=config.data_eleicao,
    )
    consistency = consistency_mod.evaluate(
        urna=target,
        requested=requested,
        bu=bu,
        rdv=rdv,
        imgbu=imgbu,
        log=log,
        timeline=timeline,
        signature=signature,
        integrity=integrity,
    )
    consistency_mod.build_matrix(consistency, integrity)

    _log(config, "[5/6] Verificacao pos-execucao da evidencia ...")
    post_run = []
    post_run_ok = True
    for item in target_files.values():
        current = hash_file(item.abs_path)  # type: ignore[arg-type]
        ok = current["sha256"] == item.sha256 and current["sha512"] == item.sha512
        post_run_ok = post_run_ok and ok
        post_run.append(
            {
                "path": item.relpath,
                "sha256_unchanged": current["sha256"] == item.sha256,
                "sha512_unchanged": current["sha512"] == item.sha512,
            }
        )

    findings = list(consistency.findings)
    findings += _findings_from_parsers(
        errors=errors,
        container=container,
        integrity=integrity,
        log=log,
        target_files=target_files,
        comparison=comparison,
        post_run_ok=post_run_ok,
        municipio=municipio,
    )
    findings = _dedupe(findings)

    # ---- artefatos extraidos --------------------------------------------
    extracted_dir = output_dir / "extracted"
    extracted: list[dict[str, Any]] = []
    if log and payloads:
        extracted_dir.mkdir(exist_ok=True)
        for payload in payloads:
            name = _safe_name(payload.entry_path)
            path = extracted_dir / name
            path.write_bytes(payload.text.encode("latin-1", errors="replace"))
            extracted.append(
                {
                    "entry": payload.entry_path,
                    "path": str(path.relative_to(output_dir)),
                    "size": path.stat().st_size,
                    "sha256": payload.sha256,
                }
            )
    if imgbu and imgbu.spool:
        extracted_dir.mkdir(exist_ok=True)
        spool_path = extracted_dir / "imgbu_spool.bin"
        spool_path.write_bytes(imgbu.spool)
        text_path = extracted_dir / "imgbu_spool.txt"
        text_path.write_text(imgbu.text, encoding="utf-8")
        extracted.append(
            {
                "entry": "imgbu.dat#spool",
                "path": str(spool_path.relative_to(output_dir)),
                "size": spool_path.stat().st_size,
                "sha256": imgbu.spool_sha256,
            }
        )
    if signature and signature.hw.certificate_raw and signature.hw.certificate:
        cert_dir = output_dir / "certificates"
        cert_dir.mkdir(exist_ok=True)
        cert_raw = signature.hw.certificate_raw
        try:
            from .crypto.signatures import load_certificate

            cert = load_certificate(cert_raw)
            pem = cert.public_bytes(serialization.Encoding.PEM)
        except Exception:  # noqa: BLE001
            pem = cert_raw
        cert_path = cert_dir / f"{signature.hw.certificate.sha256}.pem"
        cert_path.write_bytes(pem)
        signature.hw.certificate.pem_path = str(cert_path.relative_to(output_dir))

    _log(config, "[6/6] Gravando relatorios ...")
    finished = datetime.now()
    report: dict[str, Any] = {
        "tool": {
            "name": TOOL_NAME,
            "version": __version__,
            "python": sys.version.split()[0],
        },
        "analysis": {
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "duration_seconds": round((finished - started).total_seconds(), 3),
            "input_root": str(input_dir),
            "output_dir": str(output_dir),
            "read_only": True,
            "hash_scope": config.hash_scope,
        },
        "request": requested.as_dict(),
        "target": {
            **target.as_dict(),
            "municipio_nome": municipio.nome if municipio else None,
            "municipio_ibge": municipio.codigo_ibge if municipio else None,
            "files": [item.as_dict() for item in target_files.values()],
        },
        "container": container.as_dict() if container else None,
        "log": {
            "events_total": len(log.events) if log else 0,
            "sessions": len(log.sessions) if log else 0,
            "stats": log.stats if log else {},
            "unparsed": log.unparsed if log else [],
            "entries": log.entries if log else [],
        },
        "bu": bu.as_dict() if bu else None,
        "rdv": rdv.as_dict() if rdv else None,
        "imgbu": imgbu.as_dict(include_text=False) if imgbu else None,
        "signatures": signature.as_dict() if signature else None,
        "timeline": timeline.as_dict(include_events=False),
        "integrity": integrity.as_dict(),
        "consistency": consistency.as_dict(),
        "findings": [item.as_dict() for item in findings],
        "post_run_verification": {
            "ok": post_run_ok,
            "files": post_run,
        },
        "previous_run_comparison": comparison,
        "provenance": {
            "format_documentation": [
                "LEIA-ME oficial que acompanha o conjunto (leiame.pdf)",
                "Especificacao ASN.1 v2 do TSE para BU, RDV e assinatura "
                "(ModuloBU, ModuloRegistroDigitalVoto, "
                "ModuloAssinaturaResultado), espelhada em DataUrnas-BR spec/v2",
                "Formato do log: texto simples com 6 campos, observado nos "
                "arquivos e compativel com leitores publicos",
            ],
            "inferred": [
                "O container .jez observado e ZIP (o LEIA-ME cita 7z)",
                "O codigo de 64 bits de cada linha do log nao tem construcao "
                "publicada; nao e verificado",
            ],
        },
        "extracted": extracted,
    }
    report["conclusion"] = _conclusion(
        urna=target,
        municipio=municipio,
        timeline=timeline,
        bu=bu,
        integrity=integrity,
        consistency=consistency,
        findings=findings,
    )

    # ---- grava artefatos ------------------------------------------------
    manifest = {
        "analysis_started_at": started.isoformat(),
        "analysis_finished_at": finished.isoformat(),
        "tool": report["tool"],
        "input_root": str(input_dir),
        "output_dir": str(output_dir),
        "read_only": True,
        "hash_scope": config.hash_scope,
        "counts": {
            "files": len(scanned.files),
            "bytes": scanned.total_bytes,
            "hashed_files": sum(1 for item in scanned.files if item.sha256),
        },
        "files": [item.as_dict() for item in scanned.files],
        "previous_run_comparison": comparison,
        "notes": scanned.notes,
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(
        output_dir / "inventory.json",
        {**_inventory(scanned.files, urnas, target), "input_root": str(input_dir)},
    )
    if config.wants("timeline"):
        _write_json(output_dir / "timeline.json", timeline.as_dict(include_events=True))
    if config.wants("verify"):
        _write_json(output_dir / "integrity.json", integrity.as_dict())
        _write_json(output_dir / "consistency.json", consistency.as_dict())
    if config.wants("report"):
        # bu.json formatado conforme Requisito #7 + detalhes completos
        bu_summary: dict[str, Any] = {}
        if bu:
            eleicoes = bu.eleicoes
            cargos = [
                cargo
                for eleicao in eleicoes
                for resultado in eleicao.get("resultados", [])
                for cargo in resultado.get("cargos", [])
            ]
            pres = next((c for c in cargos if c["codigo_cargo"] == 1), None)
            cand_names = (imgbu.candidates if imgbu else {})
            cands_list = []
            if pres:
                for voto in pres["votos"]:
                    if voto["tipo_voto_nome"] == "nominal":
                        ident = voto.get("identificacao_votavel") or {}
                        num = ident.get("numero")
                        cands_list.append(
                            {
                                "cargo": "presidente",
                                "numero": num,
                                "nome": (cand_names.get(str(num)) or {}).get("nome"),
                                "partido": ident.get("partido"),
                                "votos": voto["quantidade"],
                            }
                        )
            cands_list.sort(key=lambda item: -item["votos"])
            pres_tipos = pres.get("tipos_voto", {}) if pres else {}
            bu_summary = {
                "municipio": (municipio.nome if municipio else str(target.municipio)),
                "municipio_codigo": target.municipio,
                "zona": target.zona,
                "secao": target.secao,
                "turno": timeline.turn,
                "data_eleicao": (
                    timeline.election_date.isoformat()
                    if timeline.election_date
                    else None
                ),
                "aptos": (
                    eleicoes[0]["qtd_eleitores_aptos"] if eleicoes else None
                ),
                "comparecimento": bu.comparecimento,
                "validos": pres_tipos.get("nominal", 0) + pres_tipos.get("legenda", 0),
                "brancos": pres_tipos.get("branco", 0),
                "nulos": pres_tipos.get("nulo", 0),
                "candidatos": cands_list,
                "estrutura_completa": bu.as_dict(),
            }
        _write_json(output_dir / "bu.json", bu_summary)
        if rdv:
            _write_json(output_dir / "rdv.json", rdv.as_dict())
        if signature:
            _write_json(output_dir / "signatures.json", signature.as_dict())
        _write_json(output_dir / "report.json", report)
        if config.write_html:
            from .reports.html_report import render_html

            (output_dir / "report.html").write_text(render_html(report), encoding="utf-8")
    console = _console(report)
    return Result(
        report=report,
        output_dir=output_dir,
        console=console,
        findings=findings,
        integrity=integrity,
        consistency=consistency,
        timeline=timeline,
    )
