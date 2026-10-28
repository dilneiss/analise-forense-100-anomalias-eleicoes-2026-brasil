"""Parser do Boletim de Urna (envelope + EntidadeBoletimUrna).

Especificacao: modulo ``ModuloBU`` (ASN.1 v2) do TSE, com ``IMPLICIT TAGS``.
O envelope generico pode ou nao trazer o bloco ``urna``; o BU de secao traz
``identificacao`` [0] e ``conteudo`` (OCTET STRING) com a entidade do BU.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .. import der
from ..der import Node
from . import asn1_common as common

BU_HASH_CHAIN_HEADER = (
    "idPleito(5)|idEleicao(5)|municipio(5)|zona(4)|secao(4)|codigoCarga(24)"
)


class BULegivelError(ValueError):
    """Arquivo nao e um BU no esquema esperado."""


@dataclass
class BU:
    raw_sha256: str
    envelope: dict[str, Any]
    cabecalho: dict[str, Any]
    fase: int
    urna: Optional[dict[str, Any]]
    identificacao: dict[str, Any]
    tipo_envelope: int
    conteudo_offset: int
    conteudo_size: int
    data_hora_emissao: datetime
    dados_secao: dict[str, Any]
    comparecimento: int
    detalhamento_comparecimento: Optional[dict[str, int]]
    eleicoes: list[dict[str, Any]] = field(default_factory=list)
    historico_codigos_carga: list[str] = field(default_factory=list)
    observacoes: list[str] = field(default_factory=list)
    cadeia_hashes: list[dict[str, Any]] = field(default_factory=list)
    offsets: dict[str, int] = field(default_factory=dict)

    # -- atalhos ------------------------------------------------------------
    @property
    def abertura(self) -> Optional[datetime]:
        value = self.dados_secao.get("abertura")
        return value

    @property
    def encerramento(self) -> Optional[datetime]:
        value = self.dados_secao.get("encerramento")
        return value

    def as_dict(self) -> dict[str, Any]:
        return {
            "arquivo_sha256": self.raw_sha256,
            "envelope": self.envelope,
            "cabecalho": self.cabecalho,
            "fase": self.fase,
            "fase_nome": common.FASE.get(self.fase, f"desconhecida_{self.fase}"),
            "urna": self.urna,
            "identificacao": self.identificacao,
            "tipo_envelope": self.tipo_envelope,
            "tipo_envelope_nome": common.TIPO_ENVELOPE.get(
                self.tipo_envelope, f"desconhecido_{self.tipo_envelope}"
            ),
            "conteudo": {
                "offset_no_arquivo": self.conteudo_offset,
                "tamanho": self.conteudo_size,
            },
            "data_hora_emissao": self.data_hora_emissao.isoformat(),
            "dados_secao": {
                key: value.isoformat() if isinstance(value, datetime) else value
                for key, value in self.dados_secao.items()
            },
            "comparecimento": self.comparecimento,
            "detalhamento_comparecimento": self.detalhamento_comparecimento,
            "eleicoes": self.eleicoes,
            "historico_codigos_carga": self.historico_codigos_carga,
            "cadeia_hashes": self.cadeia_hashes,
            "offsets": self.offsets,
            "observacoes": self.observacoes,
        }


def parse_envelope(raw: bytes) -> dict[str, Any]:
    """Le ``EntidadeEnvelopeGenerico`` e devolve o conteudo binario."""
    try:
        root = der.parse(raw)
    except der.DerError as exc:
        raise BULegivelError(f"BER invalido: {exc}") from exc
    if not (root.is_universal and root.tag_number == 16):
        raise BULegivelError("raiz nao e SEQUENCE")
    children = root.children()
    if len(children) < 5:
        raise BULegivelError(f"envelope com {len(children)} campos")
    index = 0
    cabecalho_node = children[index]
    index += 1
    fase_node = children[index]
    index += 1
    urna_node: Optional[Node] = None
    if children[index].tag_class == 0 and children[index].tag_number == 16:
        urna_node = children[index]
        index += 1
    if index >= len(children):
        raise BULegivelError("identificacao ausente")
    identificacao_node = children[index]
    index += 1
    if index >= len(children):
        raise BULegivelError("tipoEnvelope ausente")
    tipo_node = children[index]
    index += 1
    seguranca_node: Optional[Node] = None
    if index < len(children) and children[index].is_universal and children[index].tag_number == 16:
        seguranca_node = children[index]
        index += 1
    if index >= len(children):
        raise BULegivelError("conteudo ausente")
    conteudo_node = children[index]
    if not (conteudo_node.is_universal and conteudo_node.tag_number == 4):
        raise BULegivelError("campo conteudo nao e OCTET STRING")
    if index + 1 != len(children):
        raise BULegivelError("campos extras apos o conteudo")

    cabecalho_children = cabecalho_node.children()
    if len(cabecalho_children) < 2:
        raise BULegivelError("cabecalho incompleto")
    envelope = {
        "data_geracao": common.data_hora(cabecalho_children[0].as_text()).isoformat(),
        "data_geracao_offset": cabecalho_children[0].start,
        "id_eleitoral": common.parse_id_eleitoral(cabecalho_children[1]),
        "fase": fase_node.as_int(),
        "fase_nome": common.FASE.get(fase_node.as_int(), "desconhecida"),
        "urna": common.parse_urna(urna_node) if urna_node is not None else None,
        "identificacao": common.parse_identificacao(identificacao_node),
        "tipo_envelope": tipo_node.as_int(),
        "tipo_envelope_nome": common.TIPO_ENVELOPE.get(
            tipo_node.as_int(), f"desconhecido_{tipo_node.as_int()}"
        ),
        "seguranca_presente": seguranca_node is not None,
        "conteudo_offset": conteudo_node.value_start,
    }
    return {
        "root": root,
        "children": children,
        "envelope": envelope,
        "conteudo": conteudo_node.value,
        "conteudo_offset": conteudo_node.value_start,
        "conteudo_node": conteudo_node,
    }


def parse_bu(raw: bytes) -> BU:
    envelope = parse_envelope(raw)
    if envelope["envelope"]["tipo_envelope"] not in (1, 4):
        raise BULegivelError(
            "tipoEnvelope "
            f"{envelope['envelope']['tipo_envelope']} nao e BU (1) nem BU impresso (4)"
        )
    inner_raw = envelope["conteudo"]
    try:
        inner = der.parse(inner_raw)
    except der.DerError as exc:
        raise BULegivelError(f"conteudo do BU nao e BER valido: {exc}") from exc
    if not (inner.is_universal and inner.tag_number == 16):
        raise BULegivelError("conteudo do BU nao e SEQUENCE")
    children = inner.children()
    if len(children) < 10:
        raise BULegivelError(f"BU com {len(children)} campos")
    index = 0
    cabecalho_node = children[index]
    index += 1
    fase_node = children[index]
    index += 1
    urna_node = children[index]
    index += 1
    identificacao_node = children[index]
    index += 1
    emissao_node = children[index]
    index += 1
    dados_node = children[index]
    index += 1
    comparecimento_node = children[index]
    index += 1
    detalhamento: Optional[dict[str, int]] = None
    if index < len(children) and children[index].tag_class == 2 and children[index].tag_number == 1:
        partes = children[index].children()
        if len(partes) >= 3:
            detalhamento = {
                "sem_biometria": partes[0].as_int(),
                "por_biometria": partes[1].as_int(),
                "por_biografia": partes[2].as_int(),
            }
        index += 1
    if index >= len(children):
        raise BULegivelError("resultados da votacao ausentes")
    resultados_node = children[index]
    index += 1
    historico_node = children[index] if index < len(children) else None
    index += 1
    voto_impresso = children[index] if index < len(children) else None

    cabecalho_children = cabecalho_node.children()
    dados_secao: dict[str, Any] = {}
    if dados_node.tag_class == 2 and dados_node.tag_number == 0:
        partes = dados_node.children()
        dados_secao["abertura"] = common.data_hora(partes[0].as_text())
        dados_secao["encerramento"] = common.data_hora(partes[1].as_text())
        if len(partes) > 2:
            dados_secao["desligamento_voto_impresso"] = common.data_hora(partes[2].as_text())
    elif dados_node.tag_class == 2 and dados_node.tag_number == 1:
        partes = dados_node.children()
        dados_secao = {
            "tipo": "sistema_de_apuracao",
            "junta_apuradora": partes[0].as_int(),
            "turma_apuradora": partes[1].as_int(),
            "numero_interno_urna_origem": partes[2].as_int() if len(partes) > 2 else None,
        }
    else:
        raise BULegivelError(f"dadosSecaoSA com tag inesperada {dados_node.tag_name}")

    bu = BU(
        raw_sha256=hashlib.sha256(raw).hexdigest(),
        envelope={key: value for key, value in envelope["envelope"].items()},
        cabecalho={
            "data_geracao": common.data_hora(cabecalho_children[0].as_text()).isoformat(),
            "id_eleitoral": common.parse_id_eleitoral(cabecalho_children[1]),
        },
        fase=fase_node.as_int(),
        urna=common.parse_urna(urna_node),
        identificacao=common.parse_secao_eleitoral(identificacao_node),
        tipo_envelope=envelope["envelope"]["tipo_envelope"],
        conteudo_offset=envelope["conteudo_offset"],
        conteudo_size=len(inner_raw),
        data_hora_emissao=common.data_hora(emissao_node.as_text()),
        dados_secao=dados_secao,
        comparecimento=comparecimento_node.as_int(),
        detalhamento_comparecimento=detalhamento,
        historico_codigos_carga=[node.as_text() for node in historico_node.children()]
        if historico_node is not None and historico_node.is_universal and historico_node.tag_number == 16
        else [],
    )
    bu.observacoes.append(
        "Nao ha campo 'turno' na especificacao do BU; o turno e deduzido do "
        "log e do texto do BU impresso."
    )
    if voto_impresso is not None:
        bu.observacoes.append("historicoVotoImpresso presente")
    bu.offsets = {
        "envelope_data_geracao": envelope["envelope"].get("data_geracao_offset"),
        "conteudo_inicio": envelope["conteudo_offset"],
        "identificacao": identificacao_node.start,
        "data_hora_emissao": emissao_node.start,
        "comparecimento": comparecimento_node.start,
        "resultados_votacao": resultados_node.start,
    }
    if dados_node.tag_class == 2:
        partes = dados_node.children()
        bu.offsets["dados_secao"] = dados_node.start
        if len(partes) > 0:
            bu.offsets["abertura"] = partes[0].start
        if len(partes) > 1:
            bu.offsets["encerramento"] = partes[1].start
    bu.eleicoes = [_parse_eleicao(node) for node in resultados_node.children()]
    bu.cadeia_hashes = verify_hash_chains(bu)
    return bu


def _parse_eleicao(node: Node) -> dict[str, Any]:
    children = node.children()
    if len(children) < 7:
        raise BULegivelError("ResultadoVotacaoPorEleicao incompleto")
    resultados: list[dict[str, Any]] = []
    for resultado_node in children[4].children():
        partes = resultado_node.children()
        tipo_cargo = partes[0].as_int()
        cargos = []
        for cargo_node in partes[2].children():
            cargo_children = cargo_node.children()
            codigo, origem = common.parse_codigo_cargo(cargo_children[0])
            votos = [
                common.parse_total_votos_votavel(voto)
                for voto in cargo_children[2].children()
            ]
            total = sum(voto["quantidade"] for voto in votos)
            cargos.append(
                {
                    "codigo_cargo": codigo,
                    "cargo": origem,
                    "ordem_impressao": cargo_children[1].as_int(),
                    "votos": votos,
                    "total_votos": total,
                    "tipos_voto": _sum_by_type(votos),
                }
            )
        resultados.append(
            {
                "tipo_cargo": tipo_cargo,
                "tipo_cargo_nome": common.TIPO_CARGO_CONSULTA.get(
                    tipo_cargo, f"desconhecido_{tipo_cargo}"
                ),
                "comparecimento": partes[1].as_int(),
                "cargos": cargos,
            }
        )
    return {
        "id_eleicao": children[0].as_int(),
        "qtd_eleitores_aptos": children[1].as_int(),
        "qtd_eleitores_aptos_secao": children[2].as_int(),
        "qtd_eleitores_aptos_tte": children[3].as_int(),
        "resultados": resultados,
        "ultimo_hash_votos_votavel": children[5].value.hex().upper(),
        "assinatura_ultimo_hash": {
            "tamanho": len(children[6].value),
            "sha256": hashlib.sha256(children[6].value).hexdigest(),
        },
    }


def _sum_by_type(votos: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for voto in votos:
        name = voto["tipo_voto_nome"]
        totals[name] = totals.get(name, 0) + voto["quantidade"]
    return totals


def _header_string(pleito: int, eleicao: int, municipio: int, zona: int, secao: int, carga: str) -> str:
    carga_txt = str(carga)
    if carga_txt.isdigit():
        carga_txt = carga_txt.zfill(24)
    return (
        f"{pleito:05d}|{eleicao:05d}|{municipio:05d}|{zona:04d}|"
        f"{secao:04d}|{carga_txt}"
    )


def verify_hash_chains(bu: BU) -> list[dict[str, Any]]:
    """Recalcula a cadeia SHA-512 documentada em ``TotalVotosVotavel.hash``.

    Cabecalho: ``idPleito|idEleicao|municipio|zona|secao|codigoCarga``.
    Bloco: ``HASH_ANTERIOR|ordemGeracaoHash|codigoCargo|tipoVoto|quantidade``
    e, quando existe identificacao do votavel, ``|codigo|partido`` (ordem
    documentada). Se a formula documentada nao casar, a variante
    ``|partido|codigo`` e testada e reportada como formula alternativa.
    """
    pleito = bu.cabecalho.get("id_eleitoral", {}).get("valor")
    if pleito is None:
        return []
    municipio = bu.identificacao.get("municipio")
    zona = bu.identificacao.get("zona")
    secao = bu.identificacao.get("secao")
    carga = bu.historico_codigos_carga[-1] if bu.historico_codigos_carga else ""
    results: list[dict[str, Any]] = []
    for eleicao in bu.eleicoes:
        header = _header_string(pleito, eleicao["id_eleicao"], municipio, zona, secao, carga)
        current = hashlib.sha512(header.encode("ascii")).digest()
        failures: list[dict[str, Any]] = []
        checked = 0
        variant_used = "documentada"
        grupos: list[tuple[int, int, list[dict[str, Any]]]] = []
        for resultado in eleicao["resultados"]:
            for cargo in resultado["cargos"]:
                grupos.append(
                    (cargo["ordem_impressao"], cargo["codigo_cargo"], cargo["votos"])
                )
        grupos.sort(key=lambda item: item[0])
        for ordem, codigo, votos in grupos:
            votos = sorted(votos, key=lambda item: item["ordem_geracao_hash"])
            for voto in votos:
                if len(bytes.fromhex(voto["hash"])) != 64:
                    failures.append(
                        {
                            "motivo": "hash nao tem 64 bytes (SHA-512)",
                            "cargo": codigo,
                            "ordem": voto["ordem_geracao_hash"],
                        }
                    )
                    continue
                base = (
                    f"{current.hex().upper()}|{voto['ordem_geracao_hash']}|"
                    f"{codigo}|{voto['tipo_voto']}|{voto['quantidade']}"
                )
                identificacao = voto["identificacao_votavel"]
                if identificacao:
                    documented = (
                        base + f"|{identificacao['numero']}|{identificacao['partido']}"
                    )
                    alternative = (
                        base + f"|{identificacao['partido']}|{identificacao['numero']}"
                    )
                else:
                    documented = alternative = base
                declared = voto["hash"].lower()
                if hashlib.sha512(documented.encode("ascii")).hexdigest() == declared:
                    current = bytes.fromhex(declared)
                    checked += 1
                elif hashlib.sha512(alternative.encode("ascii")).hexdigest() == declared:
                    variant_used = "alternativa (partido|codigo)"
                    current = bytes.fromhex(declared)
                    checked += 1
                else:
                    failures.append(
                        {
                            "motivo": "hash declarado difere do recalculado",
                            "cargo": codigo,
                            "ordem": voto["ordem_geracao_hash"],
                            "declarado": declared.upper(),
                            "recalculado": hashlib.sha512(
                                documented.encode("ascii")
                            ).hexdigest().upper(),
                        }
                    )
                    current = bytes.fromhex(declared)
        declared_last = eleicao["ultimo_hash_votos_votavel"].lower()
        results.append(
            {
                "id_eleicao": eleicao["id_eleicao"],
                "algoritmo": "SHA-512",
                "cabecalho": header,
                "hash_cabecalho": hashlib.sha512(header.encode("ascii")).hexdigest().upper(),
                "registros_verificados": checked,
                "falhas": failures,
                "formula": variant_used,
                "ultimo_hash_declarado": declared_last.upper(),
                "ultimo_hash_recalculado": current.hex().upper(),
                "ultimo_hash_confere": current.hex() == declared_last,
                "status": "VALIDADO" if not failures and current.hex() == declared_last else "INCONSISTENTE",
            }
        )
    return results


def validate_sums(bu: BU) -> list[dict[str, Any]]:
    """Conferencias aritmeticas internas do BU (sem interpretar intencao)."""
    checks: list[dict[str, Any]] = []
    checks.append(
        {
            "key": "comparecimento_detalhamento",
            "status": "VALIDADO"
            if bu.detalhamento_comparecimento
            and sum(bu.detalhamento_comparecimento.values()) == bu.comparecimento
            else ("NAO_FOI_POSSIVEL_VERIFICAR" if not bu.detalhamento_comparecimento else "INCONSISTENTE"),
            "detail": (
                f"comparecimento={bu.comparecimento}; detalhamento="
                f"{bu.detalhamento_comparecimento}"
            ),
        }
    )
    for eleicao in bu.eleicoes:
        aptos = eleicao["qtd_eleitores_aptos"]
        soma_aptos = eleicao["qtd_eleitores_aptos_secao"] + eleicao["qtd_eleitores_aptos_tte"]
        checks.append(
            {
                "key": f"aptos_{eleicao['id_eleicao']}",
                "status": "VALIDADO" if soma_aptos == aptos else "INCONSISTENTE",
                "detail": (
                    f"aptos={aptos}; secao+tte={soma_aptos} "
                    f"({eleicao['qtd_eleitores_aptos_secao']}+"
                    f"{eleicao['qtd_eleitores_aptos_tte']})"
                ),
            }
        )
        if bu.comparecimento > aptos:
            checks.append(
                {
                    "key": f"comparecimento_maior_que_aptos_{eleicao['id_eleicao']}",
                    "status": "INCONSISTENTE",
                    "detail": f"comparecimento {bu.comparecimento} > aptos {aptos}",
                }
            )
        for resultado in eleicao["resultados"]:
            for cargo in resultado["cargos"]:
                total = cargo["total_votos"]
                comp = resultado["comparecimento"]
                if comp and total % comp == 0:
                    status = "VALIDADO"
                    detail = f"total {total} = {total // comp} x comparecimento {comp}"
                elif comp:
                    status = "INCONSISTENTE"
                    detail = f"total {total} nao e multiplo do comparecimento {comp}"
                else:
                    status = "NAO_FOI_POSSIVEL_VERIFICAR"
                    detail = "comparecimento zero"
                checks.append(
                    {
                        "key": f"total_cargo_{eleicao['id_eleicao']}_{cargo['codigo_cargo']}",
                        "status": status,
                        "detail": f"cargo {cargo['codigo_cargo']} ({cargo['cargo']}): {detail}",
                    }
                )
    return checks
