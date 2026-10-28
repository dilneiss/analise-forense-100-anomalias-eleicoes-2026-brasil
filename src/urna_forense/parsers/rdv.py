"""Parser do Registro Digital do Voto (RDV).

O RDV nao permite identificar eleitores: a especificacao guarda apenas o tipo
de voto e a digitacao, embaralhados. Esta ferramenta exporta somente
agregados por cargo/tipo/numero; a sequencia individual NAO e reproduzida.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Optional

from .. import der
from ..der import Node
from . import asn1_common as common


class RDVLegivelError(ValueError):
    """Arquivo nao e um RDV no esquema esperado."""


@dataclass
class RDV:
    raw_sha256: str
    cabecalho: dict[str, Any]
    urna: dict[str, Any]
    pleito: int
    fase: int
    identificacao: dict[str, Any]
    historico_codigos_carga: list[str]
    eleicoes: list[dict[str, Any]]
    tipo_eleicoes: str
    observacoes: list[str] = field(default_factory=list)

    def total_registros(self) -> int:
        return sum(
            cargo["registros"]
            for eleicao in self.eleicoes
            for cargo in eleicao["cargos"]
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "arquivo_sha256": self.raw_sha256,
            "cabecalho": self.cabecalho,
            "urna": self.urna,
            "pleito": self.pleito,
            "fase": self.fase,
            "fase_nome": common.FASE.get(self.fase, f"desconhecida_{self.fase}"),
            "identificacao": self.identificacao,
            "historico_codigos_carga": self.historico_codigos_carga,
            "tipo_eleicoes": self.tipo_eleicoes,
            "eleicoes": self.eleicoes,
            "total_registros": self.total_registros(),
            "observacoes": self.observacoes,
        }


def parse_rdv(raw: bytes) -> RDV:
    try:
        root = der.parse(raw)
    except der.DerError as exc:
        raise RDVLegivelError(f"BER invalido: {exc}") from exc
    if not (root.is_universal and root.tag_number == 16):
        raise RDVLegivelError("raiz nao e SEQUENCE")
    children = root.children()
    if len(children) < 3:
        raise RDVLegivelError(f"RDV com {len(children)} campos")
    cabecalho_node, urna_node, corpo_node = children[0], children[1], children[2]
    cabecalho_children = cabecalho_node.children()
    if len(cabecalho_children) < 2:
        raise RDVLegivelError("cabecalho incompleto")
    corpo_children = corpo_node.children()
    if len(corpo_children) < 5:
        raise RDVLegivelError("EntidadeRegistroDigitalVoto incompleta")

    pleito = corpo_children[0].as_int()
    fase = corpo_children[1].as_int()
    identificacao = common.parse_secao_eleitoral(corpo_children[2])
    historico = [node.as_text() for node in corpo_children[3].children()]
    eleicoes_node = corpo_children[4]

    eleicoes: list[dict[str, Any]] = []
    tipo = "desconhecido"
    if eleicoes_node.tag_class == 2 and eleicoes_node.tag_number == 1:
        tipo = "vota"
        for eleicao_node in eleicoes_node.children():
            eleicoes.append(_parse_eleicao_vota(eleicao_node))
    elif eleicoes_node.tag_class == 2 and eleicoes_node.tag_number == 2:
        tipo = "sistema_de_apuracao"
        for eleicao_node in eleicoes_node.children():
            eleicoes.append(_parse_eleicao_sa(eleicao_node))
    else:
        raise RDVLegivelError(f"CHOICE eleicoes com tag {eleicoes_node.tag_name}")

    rdv = RDV(
        raw_sha256=hashlib.sha256(raw).hexdigest(),
        cabecalho={
            "data_geracao": common.data_hora(cabecalho_children[0].as_text()).isoformat(),
            "id_eleitoral": common.parse_id_eleitoral(cabecalho_children[1]),
        },
        urna=common.parse_urna(urna_node),
        pleito=pleito,
        fase=fase,
        identificacao=identificacao,
        historico_codigos_carga=historico,
        eleicoes=eleicoes,
        tipo_eleicoes=tipo,
    )
    rdv.observacoes.append(
        "O RDV nao contem identificacao de eleitor; apenas tipo de voto e "
        "digitacao, sem ordem vinculada ao eleitor. Nenhuma sequencia "
        "individual e exportada."
    )
    return rdv


def _parse_eleicao_vota(node: Node) -> dict[str, Any]:
    children = node.children()
    if len(children) < 2:
        raise RDVLegivelError("EleicaoVota incompleta")
    cargos = [_parse_votos_cargo(cargo) for cargo in children[1].children()]
    return _summarize(children[0].as_int(), cargos)


def _parse_eleicao_sa(node: Node) -> dict[str, Any]:
    children = node.children()
    if len(children) < 4:
        raise RDVLegivelError("EleicaoSA incompleta")
    cargos = [_parse_votos_cargo(cargo) for cargo in children[3].children()]
    resumo = _summarize(children[0].as_int(), cargos)
    resumo["tipo_cedula_sa"] = children[1].as_int()
    resumo["origem_votos_sa"] = children[2].as_int()
    return resumo


def _parse_votos_cargo(node: Node) -> dict[str, Any]:
    children = node.children()
    if len(children) < 3:
        raise RDVLegivelError("VotosCargo incompleto")
    codigo, origem = common.parse_codigo_cargo(children[0])
    escolhas = children[1].as_int()
    por_tipo: dict[str, int] = {}
    nominais: dict[int, int] = {}
    legendas: dict[int, int] = {}
    registros = 0
    for voto_node in children[2].children():
        partes = voto_node.children()
        if not partes:
            continue
        tipo_valor = partes[0].as_int()
        tipo_nome = common.TIPO_VOTO_RDV.get(tipo_valor, f"desconhecido_{tipo_valor}")
        por_tipo[tipo_nome] = por_tipo.get(tipo_nome, 0) + 1
        registros += 1
        digitacao = None
        if len(partes) > 1 and partes[1].is_universal and partes[1].tag_number == 18:
            digitacao = partes[1].as_text()
        if tipo_nome == "nominal" and digitacao:
            numero = int(digitacao)
            nominais[numero] = nominais.get(numero, 0) + 1
        elif tipo_nome == "legenda" and digitacao:
            partido = int(digitacao[:2]) if len(digitacao) >= 2 else int(digitacao)
            legendas[partido] = legendas.get(partido, 0) + 1
    return {
        "codigo_cargo": codigo,
        "cargo": origem,
        "quantidade_escolhas": escolhas,
        "registros": registros,
        "por_tipo": por_tipo,
        "nominais_por_numero": {str(key): value for key, value in sorted(nominais.items())},
        "legendas_por_partido": {str(key): value for key, value in sorted(legendas.items())},
        "brancos": por_tipo.get("branco", 0) + por_tipo.get("branco_apos_suspensao", 0),
        "nulos": (
            por_tipo.get("nulo", 0)
            + por_tipo.get("nulo_apos_suspensao", 0)
            + por_tipo.get("nulo_por_repeticao", 0)
        ),
        "cargo_sem_candidato": (
            por_tipo.get("nulo_cargo_sem_candidato", 0)
            + por_tipo.get("nulo_apos_suspensao_cargo_sem_candidato", 0)
        ),
    }


def _summarize(id_eleicao: int, cargos: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id_eleicao": id_eleicao,
        "cargos": cargos,
        "total_registros": sum(cargo["registros"] for cargo in cargos),
    }


def compare_with_bu(
    rdv: RDV,
    comparecimento_por_eleicao: dict[int, int],
) -> list[dict[str, Any]]:
    """Confere registros do RDV com o comparecimento do BU, por cargo."""
    checks: list[dict[str, Any]] = []
    for eleicao in rdv.eleicoes:
        comparecimento = comparecimento_por_eleicao.get(eleicao["id_eleicao"])
        for cargo in eleicao["cargos"]:
            esperado: Optional[int] = None
            if comparecimento is not None:
                esperado = comparecimento * cargo["quantidade_escolhas"]
            if esperado is None:
                status = "NAO_FOI_POSSIVEL_VERIFICAR"
                detail = "comparecimento do BU indisponivel para esta eleicao"
            elif cargo["registros"] == esperado:
                status = "VALIDADO"
                detail = (
                    f"{cargo['registros']} registros = comparecimento {comparecimento}"
                    f" x {cargo['quantidade_escolhas']} escolha(s)"
                )
            else:
                status = "INCONSISTENTE"
                detail = (
                    f"{cargo['registros']} registros; esperado {esperado} "
                    f"(comparecimento {comparecimento} x "
                    f"{cargo['quantidade_escolhas']})"
                )
            checks.append(
                {
                    "key": f"rdv_registros_{eleicao['id_eleicao']}_{cargo['codigo_cargo']}",
                    "status": status,
                    "detail": f"cargo {cargo['codigo_cargo']} ({cargo['cargo']}): {detail}",
                }
            )
    return checks
