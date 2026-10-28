"""Leitura do "BU impresso" (``-imgbu.dat``).

O conteudo nao e uma imagem raster: e o spool de impressao do BU, um fluxo
de texto com bytes de controle. A decodificacao aqui e apenas textual e
serve de fonte independente para turno, data, municipio, horarios e totais.
Nao se usa OCR.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .bu import BULegivelError, parse_envelope

OFFICE_CODES = {
    "PRESIDENTE": 1,
    "GOVERNADOR": 3,
    "SENADOR": 5,
    "DEPUTADO FEDERAL": 6,
    "DEPUTADO ESTADUAL": 7,
    "DEPUTADO DISTRITAL": 8,
    "PREFEITO": 11,
    "VEREADOR": 13,
}

_OFFICE_HEADER = re.compile(r"^-{3,}\s*(.+?)\s*-{3,}$")


@dataclass
class ImgBU:
    raw_sha256: str
    spool_sha256: str
    envelope: dict[str, Any]
    text: str
    summary: dict[str, Any]
    offices: dict[str, Any] = field(default_factory=dict)
    candidates: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    spool: bytes = field(default=b"", repr=False)

    def as_dict(self, *, include_text: bool = False) -> dict[str, Any]:
        data = {
            "arquivo_sha256": self.raw_sha256,
            "spool_sha256": self.spool_sha256,
            "envelope": self.envelope,
            "resumo_impresso": self.summary,
            "totais_por_cargo_impresso": self.offices,
            "candidatos_impresso": self.candidates,
            "observacoes": self.notes,
        }
        if include_text:
            data["texto"] = self.text
        return data


def _decode_spool(content: bytes) -> str:
    """Mantem texto e quebras de linha; bytes de controle viram espaco."""
    return "".join(
        chr(byte) if byte >= 32 or byte in (9, 10) else " " for byte in content
    )


def _first_int(line: str) -> Optional[int]:
    match = re.search(r"(\d[\d.]*)", line)
    if not match:
        return None
    return int(re.sub(r"\D", "", match.group(1)) or "0")


def _value_after(lines: list[str], label: str) -> Optional[str]:
    pattern = re.compile(re.escape(label) + r"\s*(.*)$")
    for index, line in enumerate(lines):
        match = pattern.search(line)
        if match and match.group(1).strip():
            return match.group(1).strip()
        if match and index + 1 < len(lines):
            return lines[index + 1].strip()
    return None


def _parse_office_totals(lines: list[str]) -> dict[str, Any]:
    offices: dict[str, list[str]] = {}
    current: Optional[str] = None
    for line in lines:
        header = _OFFICE_HEADER.match(line.strip())
        if header and header.group(1).strip().upper() in OFFICE_CODES:
            current = header.group(1).strip().upper()
            offices.setdefault(current, [])
            continue
        if current:
            offices[current].append(line)
    result: dict[str, Any] = {}
    for office, block in offices.items():
        values: dict[str, int] = {}
        labels = {
            "nominais": "Total de votos Nominais",
            "legenda": "Total de votos de Legenda",
            "brancos": "Brancos",
            "nulos": "Nulos",
            "total_apurado": "Total Apurado",
        }
        for key, label in labels.items():
            for line in block:
                if label in line:
                    value = _first_int(line.split(label, 1)[1])
                    if value is not None:
                        values[key] = value
                    break
        if values:
            result[office] = {"codigo_cargo_sugerido": OFFICE_CODES[office], **values}
    return result


_PARTY_RE = re.compile(r"^Partido:\s*(\d+)\s*-\s*(.+?)\s*$")
_CAND_RE = re.compile(r"^\s{2,}([^\d]{2,}?)\s+(\d{2,5})\s+(\d{4})\s*$")


def _parse_candidate_names(lines: list[str]) -> dict[str, Any]:
    """Nomes de candidatos lidos do BU impresso (o ASN.1 nao traz nomes).

    A busca e conservadora: so aceita linhas com numero e votos nas colunas
    esperadas; linhas quebradas pela impressora ficam de fora.
    """
    out: dict[str, Any] = {}
    party_number: Optional[int] = None
    party_name: Optional[str] = None
    office: Optional[str] = None
    for line in lines:
        header = _OFFICE_HEADER.match(line.strip())
        if header and header.group(1).strip().upper() in OFFICE_CODES:
            office = header.group(1).strip().upper()
            continue
        party = _PARTY_RE.match(line)
        if party:
            party_number = int(party.group(1))
            party_name = party.group(2).strip()
            continue
        if any(text in line for text in ("Votos de legenda", "Total do partido", "Não há votos")):
            continue
        candidate = _CAND_RE.match(line)
        if candidate:
            name = " ".join(candidate.group(1).split())
            out[candidate.group(2)] = {
                "nome": name,
                "partido_numero": party_number,
                "partido_nome": party_name,
                "cargo_impresso": office,
                "votos_impresso": int(candidate.group(3)),
            }
    return out


def parse_imgbu(raw: bytes) -> ImgBU:
    envelope = parse_envelope(raw)
    tipo = envelope["envelope"]["tipo_envelope"]
    if tipo != 4:
        raise BULegivelError(
            f"tipoEnvelope {tipo} nao e BU impresso (4); arquivo nao e imgbu"
        )
    content = envelope["conteudo"]
    text = _decode_spool(content)
    lines = [line.rstrip() for line in text.splitlines()]
    summary: dict[str, Any] = {}

    turn_match = re.search(r"(\d+)\s*[°ºo]\s*Turno", text)
    if turn_match:
        summary["turno"] = int(turn_match.group(1))
    date_match = re.search(r"\((\d{2}/\d{2}/\d{4})\)", text)
    if date_match:
        summary["data_eleicao"] = date_match.group(1)

    municipio = _value_after(lines, "Município")
    if municipio:
        code_match = re.match(r"(\d+)", municipio)
        if code_match:
            summary["municipio_codigo"] = int(code_match.group(1))
            for index, line in enumerate(lines):
                if "Município" in line and str(summary["municipio_codigo"]) in line:
                    for candidate in lines[index + 1:index + 4]:
                        if candidate.strip() and not candidate.strip().isdigit():
                            summary["municipio_nome"] = candidate.strip()
                            break
                    break
    zona = _value_after(lines, "Zona Eleitoral")
    if zona:
        summary["zona"] = _first_int(zona)
    local = _value_after(lines, "Local de Votação")
    if local:
        summary["local"] = _first_int(local)
    secao = _value_after(lines, "Seção Eleitoral")
    if secao:
        summary["secao"] = _first_int(secao)
    urna = _value_after(lines, "Código identificação UE")
    if urna:
        summary["numero_interno_urna"] = _first_int(urna)
    for key, label in (
        ("aptos", "Eleitores aptos"),
        ("aptos_secao", "Originais da seção"),
        ("aptos_tte", "Temporários na seção"),
        ("comparecimento", "Comparecimento"),
        ("habilitados_biometria", "Habilitação biométrica"),
        ("habilitados_biografia", "Habilitação biográfica"),
        ("sem_biometria", "Habilitação sem biometria"),
        ("faltosos", "Eleitores faltosos"),
    ):
        value = _value_after(lines, label)
        if value:
            parsed = _first_int(value)
            if parsed is not None:
                summary[key] = parsed
    for key, label in (
        ("data_abertura_impressa", "Data de abertura da UE"),
        ("hora_abertura_impressa", "Horário de abertura"),
        ("data_fechamento_impressa", "Data de fechamento da UE"),
        ("hora_fechamento_impressa", "Horário de fechamento"),
    ):
        value = _value_after(lines, label)
        if value:
            summary[key] = value
    carga = _value_after(lines, "Código de identificação da carga")
    if not carga:
        carga = _value_after(lines, "Código identificação da carga")
    if not carga:
        try:
            idx = next(i for i, line in enumerate(lines) if "Código de identificação da carga" in line)
            carga = next((line.strip() for line in lines[idx + 1:] if line.strip()), None)
        except StopIteration:
            carga = None
    if carga:
        digits = re.sub(r"\D", "", carga)
        if digits:
            summary["codigo_carga"] = digits

    return ImgBU(
        raw_sha256=hashlib.sha256(raw).hexdigest(),
        spool_sha256=hashlib.sha256(content).hexdigest(),
        envelope=envelope["envelope"],
        text=text,
        summary=summary,
        offices=_parse_office_totals(lines),
        candidates=_parse_candidate_names(lines),
        spool=content,
        notes=[
            "O conteudo do imgbu e o spool de impressao (texto + bytes de "
            "controle), nao uma imagem raster; a leitura e textual, sem OCR."
        ],
    )
