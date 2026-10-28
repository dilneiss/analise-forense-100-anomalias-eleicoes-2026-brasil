"""Mapeamento dos tipos ASN.1 comuns ao BU, ao RDV e ao arquivo de assinatura."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from .. import der
from ..der import Node

FASE = {1: "simulado", 2: "oficial", 3: "treinamento"}
TIPO_ENVELOPE = {
    1: "boletim_de_urna",
    2: "registro_digital_do_voto",
    4: "boletim_de_urna_impresso",
    5: "imagem_biometria",
}
TIPO_URNA = {
    1: "secao",
    3: "contingencia",
    4: "reserva_secao",
    6: "reserva_encerrando_secao",
}
TIPO_ARQUIVO = {
    1: "votacao_ue",
    2: "votacao_red",
    3: "sa_mista_mr_parcial_cedula",
    4: "sa_mista_bu_impresso_cedula",
    5: "sa_manual",
    6: "sa_eletronica",
}
TIPO_CARGO_CONSULTA = {1: "majoritario", 2: "proporcional", 3: "consulta"}
CARGO_CONSTITUCIONAL = {
    1: "presidente",
    2: "vice-presidente",
    3: "governador",
    4: "vice-governador",
    5: "senador",
    6: "deputado federal",
    7: "deputado estadual",
    8: "deputado distrital",
    9: "primeiro suplente de senador",
    10: "segundo suplente de senador",
    11: "prefeito",
    12: "vice-prefeito",
    13: "vereador",
}
# Enumeracoes do BU (TipoVoto de boletimurna.asn1)
TIPO_VOTO_BU = {
    1: "nominal",
    2: "branco",
    3: "nulo",
    4: "legenda",
    5: "cargo_sem_candidato",
}
# Enumeracoes do RDV (TipoVoto de registrodigitalvoto.asn1) - valores DIFERENTES
TIPO_VOTO_RDV = {
    1: "legenda",
    2: "nominal",
    3: "branco",
    4: "nulo",
    5: "branco_apos_suspensao",
    6: "nulo_apos_suspensao",
    7: "nulo_por_repeticao",
    8: "nulo_cargo_sem_candidato",
    9: "nulo_apos_suspensao_cargo_sem_candidato",
}
MODELO_EQUIPAMENTO = {
    1: "TPM1.2",
    2: "TPM2.0",
    9: "UE2009",
    10: "UE2010",
    11: "UE2011",
    13: "UE2013",
    15: "UE2015",
    20: "UE2020",
    22: "UE2022",
}
ALGORITMO_ASSINATURA = {1: "rsa", 2: "ecdsa", 3: "cepesc", 4: "eddsa"}
ALGORITMO_HASH = {1: "sha1", 2: "sha256", 3: "sha384", 4: "sha512"}


class Asn1Error(ValueError):
    """Estrutura valida como BER, mas fora do esquema esperado."""


def data_hora(text: str) -> datetime:
    """``YYYYMMDDThhmmss`` (DataHoraJE), sem fuso explicito."""
    if len(text) != 15 or text[8] != "T":
        raise Asn1Error(f"DataHoraJE invalida: {text!r}")
    try:
        return datetime.strptime(text, "%Y%m%dT%H%M%S")
    except ValueError as exc:
        raise Asn1Error(f"DataHoraJE invalida: {text!r}") from exc


def require(node: Node, description: str) -> Node:
    if node is None:  # pragma: no cover - defensivo
        raise Asn1Error(f"campo ausente: {description}")
    return node


def parse_id_eleitoral(node: Node) -> dict[str, Any]:
    """CHOICE IDEleitoral: [1] processo, [2] pleito, [3] eleicao."""
    if node.tag_class != 2:
        raise Asn1Error(f"IDEleitoral com tag {node.tag_name}")
    names = {1: "processo_eleitoral", 2: "pleito", 3: "eleicao"}
    return {
        "tipo": names.get(node.tag_number, f"tag_{node.tag_number}"),
        "valor": node.as_int(),
    }


def parse_municipio_zona(node: Node) -> dict[str, int]:
    children = node.children()
    if len(children) < 2:
        raise Asn1Error("MunicipioZona incompleto")
    return {"municipio": children[0].as_int(), "zona": children[1].as_int()}


def parse_secao_eleitoral(node: Node) -> dict[str, Any]:
    """``IdentificacaoSecaoEleitoral`` sem tag CHOICE."""
    children = node.children()
    if len(children) < 3:
        raise Asn1Error("IdentificacaoSecaoEleitoral incompleta")
    base = parse_municipio_zona(children[0])
    return {
        "tipo": "secao",
        **base,
        "local": children[1].as_int(),
        "secao": children[2].as_int(),
    }


def parse_identificacao(node: Node) -> dict[str, Any]:
    """CHOICE IdentificacaoUrna: [0] secao eleitoral, [1] contingencia."""
    if node.tag_class != 2:
        raise Asn1Error(f"IdentificacaoUrna com tag {node.tag_name}")
    if node.tag_number == 0:
        return parse_secao_eleitoral(node)
    if node.tag_number == 1:
        base = parse_municipio_zona(node.children()[0])
        return {"tipo": "contingencia", **base, "local": None, "secao": None}
    raise Asn1Error(f"IdentificacaoUrna desconhecida: {node.tag_name}")


def parse_carga(node: Node) -> dict[str, Any]:
    children = node.children()
    if len(children) < 5:
        raise Asn1Error("Carga incompleta")
    gerador = children[2].children()
    return {
        "numero_interno_urna": children[0].as_int(),
        "numero_serie_fc": children[1].value.hex().upper(),
        "identificador_gerador_midia": {
            "nome": gerador[0].as_text() if len(gerador) > 0 else None,
            "serial_certificado_tpm": gerador[1].as_text() if len(gerador) > 1 else None,
            "serial_instalacao": gerador[2].as_text() if len(gerador) > 2 else None,
        },
        "data_hora_carga": data_hora(children[3].as_text()).isoformat(),
        "codigo_carga": children[4].as_text(),
    }


def parse_urna(node: Node) -> dict[str, Any]:
    children = node.children()
    if len(children) < 5:
        raise Asn1Error("Urna incompleta")
    correspondencia = children[2].children()
    if len(correspondencia) < 2:
        raise Asn1Error("CorrespondenciaResultado incompleta")
    tipo = children[0].as_int()
    tipo_arquivo = children[3].as_int()
    data: dict[str, Any] = {
        "tipo_urna": tipo,
        "tipo_urna_nome": TIPO_URNA.get(tipo, f"desconhecido_{tipo}"),
        "versao_votacao": children[1].as_text(),
        "correspondencia": {
            "identificacao": parse_identificacao(correspondencia[0]),
            "carga": parse_carga(correspondencia[1]),
        },
        "tipo_arquivo": tipo_arquivo,
        "tipo_arquivo_nome": TIPO_ARQUIVO.get(tipo_arquivo, f"desconhecido_{tipo_arquivo}"),
        "numero_serie_fv": children[4].value.hex().upper(),
    }
    if len(children) > 5 and children[5].tag_class == 2:
        data["motivo_utilizacao_sa_tag"] = children[5].tag_name
    return data


def parse_codigo_cargo(node: Node) -> tuple[int, str]:
    """CHOICE CodigoCargoConsulta: [1] constitucional, [2] livre."""
    codigo = node.as_int()
    if node.tag_class == 2 and node.tag_number == 1:
        origem = CARGO_CONSTITUCIONAL.get(codigo, f"cargo_{codigo}")
    elif node.tag_class == 2 and node.tag_number == 2:
        origem = f"consulta_{codigo}"
    else:
        origem = f"tag_{node.tag_name}"
    return codigo, origem


def parse_total_votos_votavel(node: Node) -> dict[str, Any]:
    """``TotalVotosVotavel`` do BU."""
    children = node.children()
    if len(children) < 4:
        raise Asn1Error("TotalVotosVotavel incompleto")
    tipo_node = children[0]
    tipo = tipo_node.as_int()
    quantidade = children[1].as_int()
    identificacao: Optional[dict[str, int]] = None
    idx_ordem = 2
    if len(children) >= 5 and children[2].tag_class == 2 and children[2].tag_number == 3:
        partes = children[2].children()
        identificacao = {
            "partido": partes[0].as_int(),
            "numero": partes[1].as_int(),
        }
        idx_ordem = 3
    ordem = children[idx_ordem].as_int()
    hash_node = children[idx_ordem + 1]
    return {
        "tipo_voto": tipo,
        "tipo_voto_nome": TIPO_VOTO_BU.get(tipo, f"desconhecido_{tipo}"),
        "quantidade": quantidade,
        "identificacao_votavel": identificacao,
        "ordem_geracao_hash": ordem,
        "hash": hash_node.value.hex().upper(),
        "hash_bytes": len(hash_node.value),
    }
