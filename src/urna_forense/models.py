"""Modelos de dados da ferramenta de auditoria."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

SEVERITIES = ("INFO", "WARNING", "ERROR")
SEVERITY_ORDER = {name: index for index, name in enumerate(SEVERITIES)}

# Classificacoes permitidas (nunca "fraude"/"fraudado"/"alterado" por inferencia)
VALIDADO = "VALIDADO"
NAO_VALIDADO = "NAO_VALIDADO"
INCONSISTENTE = "INCONSISTENTE"
NAO_VERIFICAVEL = "NAO_FOI_POSSIVEL_VERIFICAR"

ALTERACAO_COMPROVAVEL = "ALTERACAO_COMPROVAVEL"
ALTERACAO_POSSIVEL = "ALTERACAO_POSSIVEL"
SEM_EVIDENCIA = "SEM_EVIDENCIA_DE_ALTERACAO"
ALTERACAO_NAO_VERIFICAVEL = "NAO_VERIFICAVEL"


def iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


@dataclass(frozen=True)
class UrnaKey:
    """Identificacao de uma urna de secao (a que aparece no nome dos arquivos)."""

    uf: str
    municipio: int
    zona: int
    secao: int

    @property
    def compact(self) -> str:
        return f"{self.uf.upper()}-{self.municipio:05d}-{self.zona:04d}-{self.secao:04d}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "uf": self.uf.upper(),
            "municipio_codigo_tse": self.municipio,
            "zona": self.zona,
            "secao": self.secao,
            "chave": self.compact,
        }


@dataclass
class EvidenceFile:
    """Um arquivo de entrada, com identidade criptografica."""

    relpath: str
    size: int
    sha256: str
    sha512: str
    ext: str
    detected_type: str
    mtime_ns: int
    urna: Optional[UrnaKey] = None
    kind: Optional[str] = None
    magic: str = ""
    abs_path: Optional[Path] = field(default=None, repr=False, compare=False)

    def as_dict(self, *, include_hashes: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "path": self.relpath,
            "size": self.size,
            "extension": self.ext,
            "detected_type": self.detected_type,
            "magic": self.magic,
            "mtime_ns": self.mtime_ns,
        }
        if include_hashes:
            data["sha256"] = self.sha256
            data["sha512"] = self.sha512
        if self.urna:
            data["urna"] = self.urna.compact
        if self.kind:
            data["kind"] = self.kind
        return data


@dataclass
class ContainerEntry:
    name: str
    size: int
    compressed_size: int
    crc32: Optional[int]
    sha256: str
    is_nested_container: bool
    depth: int
    date_time: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LogEvent:
    """Uma linha do logd.dat, com a estrutura preservada."""

    offset: int
    line: int
    timestamp: Optional[datetime]
    date: str
    time: str
    level: str
    urna_id: str
    module: str
    message: str
    mac: str
    raw: str
    category: str
    event_id: str
    session: int = 0
    source: str = "logd.dat"
    params: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": iso(self.timestamp),
            "iso": iso(self.timestamp),
            "date": self.date,
            "time": self.time,
            "level": self.level,
            "urna_id": self.urna_id,
            "module": self.module,
            "event_id": self.event_id,
            "category": self.category,
            "event": self.message,
            "session": self.session,
            "source": self.source,
            "params": self.params,
            "mac": self.mac,
            "offset": self.offset,
            "line": self.line,
            "raw": self.raw,
        }


@dataclass
class EventRef:
    """Referencia a um evento de origem (com localizacao no arquivo)."""

    timestamp: Optional[datetime]
    source: str
    offset: Optional[int] = None
    line: Optional[int] = None
    raw: Optional[str] = None
    note: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": iso(self.timestamp),
            "source": self.source,
            "offset": self.offset,
            "line": self.line,
            "raw": self.raw,
            "note": self.note,
        }


@dataclass
class Milestone:
    key: str
    label: str
    status: str  # "identificado" | "nao_identificado"
    timestamp: Optional[datetime] = None
    refs: list[EventRef] = field(default_factory=list)
    interpretation: str = ""
    alternatives: list[EventRef] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "status": self.status,
            "timestamp": iso(self.timestamp),
            "references": [r.as_dict() for r in self.refs],
            "interpretation": self.interpretation,
            "alternatives": [r.as_dict() for r in self.alternatives],
        }


@dataclass
class Finding:
    severity: str
    type: str
    message: str
    details: str = ""
    evidence: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "type": self.type,
            "message": self.message,
            "details": self.details,
            "evidence": self.evidence,
        }


@dataclass
class CheckResult:
    key: str
    label: str
    status: str
    detail: str = ""
    evidence: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "status": self.status,
            "detail": self.detail,
            "evidence": self.evidence,
        }


def worst_status(statuses: list[str]) -> str:
    """Agrega classificacoes na ordem de gravidade definida no relatorio."""
    order = [INCONSISTENTE, NAO_VALIDADO, NAO_VERIFICAVEL, VALIDADO]
    for status in order:
        if status in statuses:
            return status
    return NAO_VERIFICAVEL
