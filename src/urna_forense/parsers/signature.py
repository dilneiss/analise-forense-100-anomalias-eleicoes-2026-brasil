"""Parser do arquivo de assinatura da urna (``-vota.vsc``).

Especificacao: ``ModuloAssinaturaResultado`` (ASN.1 v2). O layout observado
nos arquivos de 2026 difere da especificacao publicada em dois pontos: o
modelo da urna vem em uma SEQUENCE no final e os campos opcionais usam tags
de contexto [0] (conjunto de chaves) e [1] (certificado). Ambos os layouts
sao aceitos; o que foi encontrado e declarado em ``layout``.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .. import der
from ..crypto import hashes as hashmod
from ..crypto import signatures as signmod
from ..models import NAO_VALIDADO, NAO_VERIFICAVEL, VALIDADO, worst_status
from . import asn1_common as common


class AssinaturaIlegivelError(ValueError):
    """Arquivo de assinatura fora do esquema esperado."""


@dataclass
class SignedFile:
    name: str
    hash_sha512: str
    signature_length: int
    signature: bytes = field(default=b"", repr=False)

    def as_dict(self) -> dict[str, Any]:
        return {
            "nome": self.name,
            "hash_sha512": self.hash_sha512,
            "tamanho_assinatura": self.signature_length,
        }


@dataclass
class Entity:
    kind: str
    data_hora: datetime
    versao: int
    usuario: str
    serial: int
    algoritmo_hash: str
    algoritmo_assinatura: str
    bits: Optional[int]
    auto_hash: str
    auto_hash_declarado: str
    auto_hash_confere: bool
    auto_signature_length: int
    auto_signature: bytes = field(default=b"", repr=False)
    files: list[SignedFile] = field(default_factory=list)
    conjunto_chave: Optional[str] = None
    certificate_raw: Optional[bytes] = field(default=None, repr=False)
    certificate: Optional[signmod.CertificateInfo] = None
    verification: Optional[signmod.Verification] = None
    file_verifications: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "parte": self.kind,
            "data_hora": self.data_hora.isoformat(),
            "versao_protocolo": self.versao,
            "usuario": self.usuario,
            "serial": self.serial,
            "algoritmo_hash": self.algoritmo_hash,
            "algoritmo_assinatura": self.algoritmo_assinatura,
            "bits": self.bits,
            "hash_autoassinado_declarado": self.auto_hash_declarado,
            "hash_autoassinado_calculado": self.auto_hash,
            "hash_autoassinado_confere": self.auto_hash_confere,
            "tamanho_assinatura": self.auto_signature_length,
            "conjunto_chave": self.conjunto_chave,
            "certificado": self.certificate.as_dict() if self.certificate else None,
            "verificacao": self.verification.as_dict() if self.verification else None,
            "arquivos": [entry.as_dict() for entry in self.files],
            "arquivos_verificados": self.file_verifications,
        }


@dataclass
class SignatureFile:
    raw_sha256: str
    schema: str
    model_cod: Optional[int]
    model: Optional[str]
    hw_algorithm_cod: Optional[int]
    sw: Entity
    hw: Entity
    status: str
    notes: list[str] = field(default_factory=list)
    chain: dict[str, Any] = field(default_factory=dict)

    def hashes(self) -> dict[str, str]:
        merged = {entry.name: entry.hash_sha512 for entry in self.sw.files}
        for entry in self.hw.files:
            merged.setdefault(entry.name, entry.hash_sha512)
        return merged

    def as_dict(self) -> dict[str, Any]:
        return {
            "arquivo_sha256": self.raw_sha256,
            "layout": self.schema,
            "modelo_urna_codigo": self.model_cod,
            "modelo_urna": self.model,
            "algoritmo_hardware_codigo": self.hw_algorithm_cod,
            "assinatura_software": self.sw.as_dict(),
            "assinatura_hardware": self.hw.as_dict(),
            "status": self.status,
            "cadeia_certificacao": self.chain,
            "hashes_assinados": self.hashes(),
            "observacoes": self.notes,
        }


def _parse_entity(node: der.Node, kind: str) -> Entity:
    children = node.children()
    if len(children) < 4:
        raise AssinaturaIlegivelError(f"{kind}: EntidadeAssinatura incompleta")
    data_hora = common.data_hora(children[0].as_text())
    versao = children[1].as_int()
    auto = children[2].children()
    if len(auto) < 4:
        raise AssinaturaIlegivelError(f"{kind}: autoAssinado incompleto")
    usuario = auto[0].children()
    alg_hash = auto[1].children()[0].as_int()
    alg_ass = auto[2].children()
    digest = auto[3].children()
    if len(digest) < 3:
        raise AssinaturaIlegivelError(f"{kind}: AssinaturaDigital incompleta")
    conteudo = children[3].value
    auto_hash_declarado = digest[1].value.hex().upper()
    auto_hash = hashlib.sha512(conteudo).hexdigest().upper()
    entity = Entity(
        kind=kind,
        data_hora=data_hora,
        versao=versao,
        usuario=usuario[0].as_text(),
        serial=usuario[1].as_int(),
        algoritmo_hash=common.ALGORITMO_HASH.get(alg_hash, str(alg_hash)),
        algoritmo_assinatura=common.ALGORITMO_ASSINATURA.get(
            alg_ass[0].as_int(), str(alg_ass[0].as_int())
        ),
        bits=alg_ass[1].as_int() if len(alg_ass) > 1 else None,
        auto_hash=auto_hash,
        auto_hash_declarado=auto_hash_declarado,
        auto_hash_confere=hashmod.equal(auto_hash, auto_hash_declarado),
        auto_signature_length=len(digest[2].value),
        auto_signature=digest[2].value,
        files=_parse_file_list(conteudo, kind),
    )
    for extra in children[4:]:
        if extra.tag_class == 2 and extra.tag_number == 0:
            entity.conjunto_chave = extra.as_text()
        elif extra.tag_class == 2 and extra.tag_number in (1, 4):
            entity.certificate_raw = extra.value
    if entity.certificate_raw:
        try:
            entity.certificate = signmod.certificate_info(entity.certificate_raw)
        except Exception as exc:  # noqa: BLE001 - certificado malformado
            entity.certificate = None
            entity.verification = signmod.Verification(
                NAO_VERIFICAVEL, "x509", f"certificado ilegivel: {exc}"
            )
    return entity


def _parse_file_list(conteudo: bytes, kind: str) -> list[SignedFile]:
    try:
        root = der.parse(conteudo)
    except der.DerError as exc:
        raise AssinaturaIlegivelError(f"{kind}: lista de arquivos invalida: {exc}") from exc
    items = root.children()
    if len(items) == 1 and items[0].is_universal and items[0].tag_number == 16:
        items = items[0].children()
    files: list[SignedFile] = []
    for item in items:
        if not (item.is_universal and item.tag_number == 16):
            continue
        parts = item.children()
        if len(parts) < 2:
            continue
        assinatura = parts[1].children()
        if len(assinatura) < 3:
            continue
        files.append(
            SignedFile(
                name=parts[0].as_text(),
                hash_sha512=assinatura[1].value.hex().upper(),
                signature_length=len(assinatura[2].value),
                signature=assinatura[2].value,
            )
        )
    return files


def parse_signature(raw: bytes) -> SignatureFile:
    try:
        root = der.parse(raw)
    except der.DerError as exc:
        raise AssinaturaIlegivelError(f"BER invalido: {exc}") from exc
    if not (root.is_universal and root.tag_number == 16):
        raise AssinaturaIlegivelError("raiz nao e SEQUENCE")
    children = root.children()
    model_cod: Optional[int] = None
    hw_alg: Optional[int] = None
    schema = "observado_2026 (SW, HW, modelo/algoritmo no fim)"
    if children and children[0].is_universal and children[0].tag_number == 10:
        model_cod = children[0].as_int()
        children = children[1:]
        schema = "especificacao_v2 (modelo no inicio)"
    entities = [
        child
        for child in children
        if child.is_universal and child.tag_number == 16 and child.length > 16
    ]
    for child in children:
        if child.is_universal and child.tag_number == 16 and child.length <= 16:
            tail = child.children()
            if len(tail) >= 1 and tail[0].is_universal and tail[0].tag_number == 10:
                model_cod = tail[0].as_int()
            if len(tail) >= 2 and tail[1].is_universal and tail[1].tag_number == 10:
                hw_alg = tail[1].as_int()
    if len(entities) < 2:
        raise AssinaturaIlegivelError(
            f"assinaturaSW/assinaturaHW ausentes ({len(entities)} entidades)"
        )
    sw = _parse_entity(entities[0], "software")
    hw = _parse_entity(entities[1], "hardware")
    if hw_alg is None:
        hw_alg = next(
            (
                code
                for code, name in common.ALGORITMO_ASSINATURA.items()
                if name == hw.algoritmo_assinatura
            ),
            None,
        )
    result = SignatureFile(
        raw_sha256=hashlib.sha256(raw).hexdigest(),
        schema=schema,
        model_cod=model_cod,
        model=common.MODELO_EQUIPAMENTO.get(model_cod, None) if model_cod else None,
        hw_algorithm_cod=hw_alg,
        sw=sw,
        hw=hw,
        status=NAO_VERIFICAVEL,
    )
    if not result.model:
        result.notes.append("modelo da urna nao identificado no arquivo")
    if sw.auto_hash_confere is False or hw.auto_hash_confere is False:
        result.status = NAO_VALIDADO
        result.notes.append(
            "SHA-512 do conteudo autoassinado difere do hash declarado"
        )
    sw_hashes = {entry.name: entry.hash_sha512 for entry in sw.files}
    hw_hashes = {entry.name: entry.hash_sha512 for entry in hw.files}
    for name in sorted(set(sw_hashes) & set(hw_hashes)):
        if sw_hashes[name] != hw_hashes[name]:
            result.notes.append(f"{name}: hash difere entre as partes SW e HW")
            result.status = NAO_VALIDADO
    return result


def verify_signature(
    signature: SignatureFile,
    *,
    present_files: dict[str, Path],
    election_date: Optional[datetime] = None,
    authorities: Optional[dict[str, Any]] = None,
) -> SignatureFile:
    """Verifica autoassinatura, assinaturas por arquivo e cadeia do certificado."""
    authorities = authorities or {}
    hw = signature.hw
    if hw.certificate is None:
        hw.verification = signmod.Verification(
            NAO_VERIFICAVEL,
            hw.algoritmo_assinatura,
            "arquivo de assinatura sem certificado digital",
        )
        hw.file_verifications = {entry.name: NAO_VERIFICAVEL for entry in hw.files}
    else:
        hw.verification = signmod.verify_entity_signature(
            algorithm=hw.algoritmo_assinatura,
            certificate=hw.certificate,
            message_hash=bytes.fromhex(hw.auto_hash_declarado),
            signature=hw.auto_signature,
            label="autoassinado",
        )
        for entry in hw.files:
            if entry.name not in present_files:
                continue
            verification = signmod.verify_entity_signature(
                algorithm=hw.algoritmo_assinatura,
                certificate=hw.certificate,
                message_hash=bytes.fromhex(entry.hash_sha512),
                signature=entry.signature,
                label=entry.name,
            )
            hw.file_verifications[entry.name] = verification.status
        signature.chain = signmod.verify_chain(
            hw.certificate, authorities, when=election_date
        )
    sw = signature.sw
    sw.verification = signmod.Verification(
        NAO_VERIFICAVEL,
        "CEPESC",
        (
            "assinatura de software CEPESC (algoritmo de governo) nao possui "
            "verificador publico; o hash do conteudo autoassinado foi conferido"
        ),
    )
    statuses = []
    if sw.auto_hash_confere:
        statuses.append(VALIDADO)
    else:
        statuses.append(NAO_VALIDADO)
    if hw.auto_hash_confere:
        statuses.append(VALIDADO)
    else:
        statuses.append(NAO_VALIDADO)
    if hw.verification:
        statuses.append(hw.verification.status)
    if signature.chain:
        statuses.append(signature.chain.get("status", NAO_VERIFICAVEL))
    signature.status = worst_status(statuses)
    return signature
