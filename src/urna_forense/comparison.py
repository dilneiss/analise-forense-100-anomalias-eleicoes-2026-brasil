"""Motor de auditoria comparativa de inconsistências entre 1º e 2º Turno.

Desenvolvido para análise forense e estatística de integridade entre turnos
eleitorais (ex.: Eleições 2026), processando pares de Boletins de Urna (BU)
em larga escala com alta performance concorrente.
"""

from __future__ import annotations

import html
import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .models import UrnaKey
from .municipios import Municipio, load_table
from .parsers.bu import parse_bu
from .reports import json_report
from .scanner import NAME_RE

# Mapeamento oficial de candidatos presidenciais para as Eleições Gerais 2026
PRESIDENTIAL_CANDIDATES = {
    13: "LULA",
    22: "FLAVIO BOLSONARO",
    14: "RENAN SANTOS",
    70: "ESCRITOR AUGUSTO CURY",
    55: "RONALDO CAIADO",
    12: "CIRO GOMES",
}

# Severidades padronizadas
SEV_ALTA = "ALTA"
SEV_MEDIA = "MEDIA"
SEV_BAIXA = "BAIXA"
SEV_INFO = "INFO"

SEVERITY_WEIGHTS = {
    SEV_ALTA: 3,
    SEV_MEDIA: 2,
    SEV_BAIXA: 1,
    SEV_INFO: 0,
}

# Categorias
CAT_HARDWARE = "HARDWARE"
CAT_ELEITORADO = "ELEITORADO"
CAT_VOTACAO = "VOTACAO"
CAT_TEMPORAL = "TEMPORAL"
CAT_BIOMETRIA = "BIOMETRIA"
CAT_INTEGRIDADE = "INTEGRIDADE"


@dataclass
class Anomaly:
    """Registro individual de uma anomalia ou inconsistência detectada."""
    code: str
    category: str
    severity: str
    title: str
    description: str
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SectionExtraction:
    """Extração concisa e estruturada de dados essenciais de um Boletim de Urna."""
    path: str
    uf: str
    municipio: int
    zona: int
    secao: int
    local: Optional[int]
    numero_interno_urna: Optional[int]
    numero_serie_fv: Optional[str]
    numero_serie_fc: Optional[str]
    versao_votacao: Optional[str]
    codigo_carga: Optional[str]
    data_carga: Optional[str]
    abertura: Optional[str]
    encerramento: Optional[str]
    duracao_minutos: Optional[float]
    aptos: int
    aptos_secao: int
    aptos_tte: int
    comparecimento: int
    abstencao: int
    pct_comparecimento: float
    pct_abstencao: float
    biometria_sim: int
    biometria_bio: int
    biometria_nao: int
    pct_biometria: float
    pct_biografia: float
    # Votação presidencial
    votos_presidenciais: dict[int, int]
    votos_brancos: int
    votos_nulos: int
    votos_validos: int
    total_apurado_pres: int


@dataclass
class SectionComparison:
    """Resultado da comparação forense de uma seção eleitoral entre 1T e 2T."""
    uf: str
    municipio: int
    zona: int
    secao: int
    municipio_nome: Optional[str]
    s1: Optional[SectionExtraction]
    s2: Optional[SectionExtraction]
    anomalies: list[Anomaly] = field(default_factory=list)
    worst_severity: str = "NORMAL"

    @property
    def key_str(self) -> str:
        return f"{self.uf.upper()}-{self.municipio:05d}-Z{self.zona:04d}-S{self.secao:04d}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "uf": self.uf,
            "municipio": self.municipio,
            "municipio_nome": self.municipio_nome,
            "zona": self.zona,
            "secao": self.secao,
            "key": self.key_str,
            "worst_severity": self.worst_severity,
            "total_anomalias": len(self.anomalies),
            "anomalias": [a.as_dict() for a in self.anomalies],
            "dados_1t": asdict(self.s1) if self.s1 else None,
            "dados_2t": asdict(self.s2) if self.s2 else None,
        }


@dataclass
class ComparisonConfig:
    """Configuração da execução da comparação 1T vs 2T."""
    input_dir_1t: Path
    input_dir_2t: Path
    output_dir: Path
    uf: Optional[str] = None
    municipio: Optional[int] = None
    municipio_nome: Optional[str] = None
    zona: Optional[int] = None
    secao: Optional[int] = None
    municipios_csv: Optional[Path] = None
    max_workers: int = 32
    quiet: bool = False
    write_html: bool = True


@dataclass
class ComparisonResult:
    """Resultado consolidado da auditoria comparativa."""
    report: dict[str, Any]
    output_dir: Path
    console: str


# ============================================================================
# EXTRAÇÃO DE DADOS DE UM BU
# ============================================================================

def extract_section_data(path: Path, raw_bytes: bytes) -> Optional[SectionExtraction]:
    """Decodifica e extrai métricas estruturadas de um Boletim de Urna."""
    try:
        bu = parse_bu(raw_bytes)
    except Exception:
        return None

    ident = bu.identificacao or {}
    uf = str(ident.get("uf", "")).lower()
    if not uf:
        match = NAME_RE.match(path.name)
        if match:
            uf = match.group("uf").lower()
    municipio = int(ident.get("municipio", 0))
    zona = int(ident.get("zona", 0))
    secao = int(ident.get("secao", 0))
    local = ident.get("local")

    urna_block = bu.urna or {}
    corr = urna_block.get("correspondencia") or {}
    carga = corr.get("carga") or {}

    num_interno = carga.get("numero_interno_urna")
    num_serie_fc = carga.get("numero_serie_fc")
    cod_carga = carga.get("codigo_carga")
    data_carga = carga.get("data_hora_carga")
    num_serie_fv = urna_block.get("numero_serie_fv")
    versao_votacao = urna_block.get("versao_votacao")

    abertura_dt = bu.abertura
    encerramento_dt = bu.encerramento
    duracao_minutos = None
    if abertura_dt and encerramento_dt:
        duracao_minutos = round((encerramento_dt - abertura_dt).total_seconds() / 60.0, 2)

    # Localiza eleição presidencial (cargo 1)
    aptos_total = 0
    aptos_secao = 0
    aptos_tte = 0
    votos_pres: dict[int, int] = {}
    votos_brancos = 0
    votos_nulos = 0
    total_apurado_pres = 0

    for e in bu.eleicoes:
        for r in e.get("resultados", []):
            for c in r.get("cargos", []):
                if c.get("codigo_cargo") == 1:  # Presidente
                    aptos_total = e.get("qtd_eleitores_aptos", 0)
                    aptos_secao = e.get("qtd_eleitores_aptos_secao", 0)
                    aptos_tte = e.get("qtd_eleitores_aptos_tte", 0)
                    total_apurado_pres = c.get("total_votos", 0)
                    for v in c.get("votos", []):
                        qtd = v.get("quantidade", 0)
                        tipo = v.get("tipo_voto_nome", "")
                        if tipo == "nominal":
                            cand_num = (v.get("identificacao_votavel") or {}).get("numero")
                            if cand_num is not None:
                                votos_pres[cand_num] = votos_pres.get(cand_num, 0) + qtd
                        elif tipo == "branco":
                            votos_brancos += qtd
                        elif tipo == "nulo":
                            votos_nulos += qtd

    # Se não achou cargo 1 nas eleições (raro), pega aptos da primeira eleição
    if aptos_total == 0 and bu.eleicoes:
        aptos_total = bu.eleicoes[0].get("qtd_eleitores_aptos", 0)
        aptos_secao = bu.eleicoes[0].get("qtd_eleitores_aptos_secao", 0)
        aptos_tte = bu.eleicoes[0].get("qtd_eleitores_aptos_tte", 0)

    comparecimento = bu.comparecimento
    abstencao = max(0, aptos_total - comparecimento)
    pct_comp = round((comparecimento / aptos_total * 100), 2) if aptos_total > 0 else 0.0
    pct_abs = round((abstencao / aptos_total * 100), 2) if aptos_total > 0 else 0.0

    detalhe = bu.detalhamento_comparecimento or {}
    bio_sim = detalhe.get("por_biometria", 0)
    bio_bio = detalhe.get("por_biografia", 0)
    bio_nao = detalhe.get("sem_biometria", 0)

    pct_bio = round((bio_sim / comparecimento * 100), 2) if comparecimento > 0 else 0.0
    pct_bio_ano = round((bio_bio / comparecimento * 100), 2) if comparecimento > 0 else 0.0

    votos_validos = sum(votos_pres.values())

    return SectionExtraction(
        path=str(path),
        uf=uf,
        municipio=municipio,
        zona=zona,
        secao=secao,
        local=local,
        numero_interno_urna=num_interno,
        numero_serie_fv=num_serie_fv,
        numero_serie_fc=num_serie_fc,
        versao_votacao=versao_votacao,
        codigo_carga=cod_carga,
        data_carga=data_carga,
        abertura=abertura_dt.isoformat() if abertura_dt else None,
        encerramento=encerramento_dt.isoformat() if encerramento_dt else None,
        duracao_minutos=duracao_minutos,
        aptos=aptos_total,
        aptos_secao=aptos_secao,
        aptos_tte=aptos_tte,
        comparecimento=comparecimento,
        abstencao=abstencao,
        pct_comparecimento=pct_comp,
        pct_abstencao=pct_abs,
        biometria_sim=bio_sim,
        biometria_bio=bio_bio,
        biometria_nao=bio_nao,
        pct_biometria=pct_bio,
        pct_biografia=pct_bio_ano,
        votos_presidenciais=votos_pres,
        votos_brancos=votos_brancos,
        votos_nulos=votos_nulos,
        votos_validos=votos_validos,
        total_apurado_pres=total_apurado_pres,
    )


# ============================================================================
# DETECTORES DE ANOMALIAS E INCONSISTÊNCIAS (24+ FORMAS)
# ============================================================================

def evaluate_section_anomalies(
    s1: Optional[SectionExtraction],
    s2: Optional[SectionExtraction],
    runoff_candidates: tuple[int, int] = (13, 22),
) -> list[Anomaly]:
    """Aplica o catálogo completo de 24+ verificações comparativas entre 1T e 2T."""
    anomalies: list[Anomaly] = []

    # ------------------------------------------------------------------------
    # Verificação de Seção Desemparelhada
    # ------------------------------------------------------------------------
    if s1 is None and s2 is not None:
        anomalies.append(
            Anomaly(
                code="SECAO_DESEMPARELHADA_SEM_1T",
                category=CAT_INTEGRIDADE,
                severity=SEV_MEDIA,
                title="Seção presente apenas no 2º Turno",
                description="Boletim de Urna encontrado no 2º Turno sem correspondente no 1º Turno.",
                details={"arquivo_2t": s2.path},
            )
        )
        return anomalies

    if s2 is None and s1 is not None:
        anomalies.append(
            Anomaly(
                code="SECAO_DESEMPARELHADA_SEM_2T",
                category=CAT_INTEGRIDADE,
                severity=SEV_MEDIA,
                title="Seção presente apenas no 1º Turno",
                description="Boletim de Urna encontrado no 1º Turno sem correspondente no 2º Turno.",
                details={"arquivo_1t": s1.path},
            )
        )
        return anomalies

    if s1 is None or s2 is None:
        return anomalies

    # ========================================================================
    # GRUPO 1: HARDWARE E CARGA DA URNA
    # ========================================================================

    # 1. Troca de urna física (número de série interno ou de votação)
    if (s1.numero_interno_urna and s2.numero_interno_urna and s1.numero_interno_urna != s2.numero_interno_urna) or (
        s1.numero_serie_fv and s2.numero_serie_fv and s1.numero_serie_fv != s2.numero_serie_fv
    ):
        anomalies.append(
            Anomaly(
                code="TROCA_URNA_FISICA",
                category=CAT_HARDWARE,
                severity=SEV_MEDIA,
                title="Substituição da urna física entre turnos",
                description=(
                    f"A urna física foi trocada entre os turnos (1T: UE {s1.numero_interno_urna} / "
                    f"FV {s1.numero_serie_fv}; 2T: UE {s2.numero_interno_urna} / FV {s2.numero_serie_fv})."
                ),
                details={
                    "urna_1t": s1.numero_interno_urna,
                    "fv_1t": s1.numero_serie_fv,
                    "urna_2t": s2.numero_interno_urna,
                    "fv_2t": s2.numero_serie_fv,
                },
            )
        )

    # 2. Versão de software alterada
    if s1.versao_votacao and s2.versao_votacao and s1.versao_votacao != s2.versao_votacao:
        anomalies.append(
            Anomaly(
                code="VERSAO_SOFTWARE_ALTERADA",
                category=CAT_HARDWARE,
                severity=SEV_ALTA,
                title="Versão do software de votação divergente",
                description=f"Software alterado: 1T '{s1.versao_votacao}' vs 2T '{s2.versao_votacao}'.",
                details={"versao_1t": s1.versao_votacao, "versao_2t": s2.versao_votacao},
            )
        )

    # 3. Mudança de local físico de votação
    if s1.local is not None and s2.local is not None and s1.local != s2.local:
        anomalies.append(
            Anomaly(
                code="MUDANCA_LOCAL_VOTACAO",
                category=CAT_HARDWARE,
                severity=SEV_BAIXA,
                title="Local de votação remanejado",
                description=f"O código do local mudou de {s1.local} (1T) para {s2.local} (2T).",
                details={"local_1t": s1.local, "local_2t": s2.local},
            )
        )

    # 4. Inconsistência de código de carga
    if s1.codigo_carga and s2.codigo_carga and s1.numero_interno_urna == s2.numero_interno_urna:
        if s1.codigo_carga != s2.codigo_carga:
            anomalies.append(
                Anomaly(
                    code="CODIGO_CARGA_ALTERADO",
                    category=CAT_HARDWARE,
                    severity=SEV_BAIXA,
                    title="Código de carga recarregado na mesma urna",
                    description="A mesma urna física teve seu código de carga atualizado entre o 1T e o 2T.",
                    details={"carga_1t": s1.codigo_carga, "carga_2t": s2.codigo_carga},
                )
            )

    # ========================================================================
    # GRUPO 2: CADASTRO DE ELEITORES E ELEITORADO
    # ========================================================================

    # 5. Variação de eleitores aptos da seção (caderno deve estar congelado)
    if s1.aptos_secao != s2.aptos_secao:
        diff_aptos = s2.aptos_secao - s1.aptos_secao
        anomalies.append(
            Anomaly(
                code="VARIACAO_APTOS_SECAO",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Variação no cadastro de eleitores originais da seção",
                description=(
                    f"O número de eleitores originais da seção variou em {diff_aptos:+d} "
                    f"(1T: {s1.aptos_secao} vs 2T: {s2.aptos_secao}). Pela legislação, o eleitorado é fixo."
                ),
                details={"aptos_secao_1t": s1.aptos_secao, "aptos_secao_2t": s2.aptos_secao, "delta": diff_aptos},
            )
        )

    # 6. Salto anômalo de eleitores temporários (TTE)
    diff_tte = abs(s2.aptos_tte - s1.aptos_tte)
    if diff_tte >= 20 or (s1.aptos > 0 and (diff_tte / s1.aptos) >= 0.10):
        anomalies.append(
            Anomaly(
                code="PICO_TRANSFERENCIA_TEMPORARIA",
                category=CAT_ELEITORADO,
                severity=SEV_MEDIA,
                title="Variação acentuada de eleitores temporários (TTE)",
                description=f"Transferências temporárias oscilaram de {s1.aptos_tte} (1T) para {s2.aptos_tte} (2T) (variação de {diff_tte}).",
                details={"tte_1t": s1.aptos_tte, "tte_2t": s2.aptos_tte, "delta": diff_tte},
            )
        )

    # 7. Comparecimento excede o número de aptos
    if s1.comparecimento > s1.aptos or s2.comparecimento > s2.aptos:
        anomalies.append(
            Anomaly(
                code="COMPARECIMENTO_EXCEDE_APTOS",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Comparecimento maior que o total de eleitores aptos",
                description=(
                    f"Violação aritmética: comparecimento 1T={s1.comparecimento}/{s1.aptos}, "
                    f"comparecimento 2T={s2.comparecimento}/{s2.aptos}."
                ),
                details={
                    "comp_1t": s1.comparecimento,
                    "aptos_1t": s1.aptos,
                    "comp_2t": s2.comparecimento,
                    "aptos_2t": s2.aptos,
                },
            )
        )

    # 8. Variação extrema de taxa de comparecimento
    delta_comp_pct = abs(s2.pct_comparecimento - s1.pct_comparecimento)
    if s1.aptos >= 50 and delta_comp_pct >= 20.0:
        anomalies.append(
            Anomaly(
                code="VARIACAO_EXTREMA_COMPARECIMENTO",
                category=CAT_ELEITORADO,
                severity=SEV_MEDIA,
                title="Variação extrema na taxa de comparecimento",
                description=(
                    f"A taxa de comparecimento oscilou {delta_comp_pct:.1f}% entre turnos "
                    f"(1T: {s1.pct_comparecimento:.1f}% vs 2T: {s2.pct_comparecimento:.1f}%)."
                ),
                details={
                    "pct_1t": s1.pct_comparecimento,
                    "pct_2t": s2.pct_comparecimento,
                    "delta_pp": round(delta_comp_pct, 2),
                },
            )
        )

    # 9. Comparecimento de 100% dos aptos (zero abstenção)
    if s2.aptos >= 50 and s2.comparecimento == s2.aptos:
        anomalies.append(
            Anomaly(
                code="COMPARECIMENTO_100_PCT",
                category=CAT_ELEITORADO,
                severity=SEV_MEDIA,
                title="Comparecimento integral (100%) no 2º Turno",
                description=f"Todos os {s2.aptos} eleitores aptos compareceram (abstenção zero em seção com >= 50 eleitores).",
                details={"aptos": s2.aptos, "comparecimento": s2.comparecimento},
            )
        )

    # 10. Abstenção extrema (> 50%)
    if s2.aptos >= 50 and s2.pct_abstencao >= 50.0:
        anomalies.append(
            Anomaly(
                code="ABSTENCAO_EXTREMA",
                category=CAT_ELEITORADO,
                severity=SEV_MEDIA,
                title="Abstenção superior a 50% no 2º Turno",
                description=f"Mais da metade dos eleitores ({s2.pct_abstencao:.1f}%) não compareceu à votação no 2T.",
                details={"abstencao": s2.abstencao, "aptos": s2.aptos, "pct_abstencao": s2.pct_abstencao},
            )
        )

    # ========================================================================
    # GRUPO 3: DINÂMICA DE VOTAÇÃO PRESIDENCIAL E QUEDAS DE VOTOS
    # ========================================================================

    v1 = s1.votos_presidenciais
    v2 = s2.votos_presidenciais

    # 11. Queda absoluta de votos de candidato finalista com comparecimento igual ou superior
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")

        if s2.comparecimento >= s1.comparecimento and c1 > 0 and c2 < c1:
            queda = c1 - c2
            anomalies.append(
                Anomaly(
                    code="QUEDA_VOTOS_CANDIDATO_COM_MAIOR_COMPARECIMENTO",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Queda de votos de {cand_nome} com comparecimento estável/maior",
                    description=(
                        f"{cand_nome} obteve {c1} votos no 1T e caiu para {c2} votos no 2T (-{queda} votos), "
                        f"embora o comparecimento tenha aumentado de {s1.comparecimento} para {s2.comparecimento}."
                    ),
                    details={
                        "candidato": cand,
                        "nome": cand_nome,
                        "votos_1t": c1,
                        "votos_2t": c2,
                        "queda": queda,
                        "comp_1t": s1.comparecimento,
                        "comp_2t": s2.comparecimento,
                    },
                )
            )

    # 12. Queda brusca de votos de candidato finalista (> 20% da base do 1T)
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")

        if c1 >= 25 and c2 < c1:
            pct_queda = (c1 - c2) / c1 * 100.0
            if pct_queda >= 20.0:
                anomalies.append(
                    Anomaly(
                        code="QUEDA_BRUSCA_VOTOS_CANDIDATO",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"Perda superior a 20% da votação de {cand_nome}",
                        description=f"{cand_nome} perdeu {pct_queda:.1f}% da votação que teve no 1T ({c1} -> {c2} votos).",
                        details={"candidato": cand, "nome": cand_nome, "votos_1t": c1, "votos_2t": c2, "pct_queda": round(pct_queda, 2)},
                    )
                )

    # 13. Desaparecimento total de votos de candidato
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")

        if c1 >= 15 and c2 == 0:
            anomalies.append(
                Anomaly(
                    code="DESAPARECIMENTO_TOTAL_VOTOS",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Desaparecimento total de votos de {cand_nome}",
                    description=f"{cand_nome} teve {c1} votos no 1T e zerou completamente (0 votos) no 2T.",
                    details={"candidato": cand, "nome": cand_nome, "votos_1t": c1, "votos_2t": 0},
                )
            )

    # 14. Zero votos para candidato finalista em seção expressiva
    for cand in runoff_candidates:
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
        if s2.votos_validos >= 50 and c2 == 0:
            anomalies.append(
                Anomaly(
                    code="ZERO_VOTOS_CANDIDATO_FINALISTA",
                    category=CAT_VOTACAO,
                    severity=SEV_MEDIA,
                    title=f"{cand_nome} com zero votos no 2º Turno",
                    description=f"Nenhum eleitor votou em {cand_nome} na seção com {s2.votos_validos} votos válidos no 2T.",
                    details={"candidato": cand, "nome": cand_nome, "validos_2t": s2.votos_validos},
                )
            )

    # 15. Unanimidade (100% dos votos válidos para um único candidato)
    if s2.votos_validos >= 50:
        for cand, qtd in v2.items():
            if qtd == s2.votos_validos:
                cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
                anomalies.append(
                    Anomaly(
                        code="UNANIMIDADE_CANDIDATO",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"Unanimidade de 100% para {cand_nome} no 2º Turno",
                        description=f"Todos os {s2.votos_validos} votos válidos da seção foram computados para {cand_nome}.",
                        details={"candidato": cand, "nome": cand_nome, "votos": qtd, "validos": s2.votos_validos},
                    )
                )

    # 16. Inversão abrupta de resultado (swing líquido extremo)
    if s1.votos_validos >= 50 and s2.votos_validos >= 50:
        c1_1 = v1.get(runoff_candidates[0], 0)
        c2_1 = v1.get(runoff_candidates[1], 0)
        c1_2 = v2.get(runoff_candidates[0], 0)
        c2_2 = v2.get(runoff_candidates[1], 0)

        pct1_cand1 = (c1_1 / s1.votos_validos * 100.0) if s1.votos_validos else 0
        pct2_cand1 = (c1_2 / s2.votos_validos * 100.0) if s2.votos_validos else 0
        pct1_cand2 = (c2_1 / s1.votos_validos * 100.0) if s1.votos_validos else 0
        pct2_cand2 = (c2_2 / s2.votos_validos * 100.0) if s2.votos_validos else 0

        if (pct1_cand1 >= 60.0 and pct2_cand1 <= 40.0) or (pct1_cand2 >= 60.0 and pct2_cand2 <= 40.0):
            anomalies.append(
                Anomaly(
                    code="INVERSAO_ABRUPTA_RESULTADO",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title="Inversão radical do resultado entre turnos",
                    description=(
                        f"Inversão de preferência eleitoral extrema entre os finalistas na seção. "
                        f"Cand {runoff_candidates[0]}: {pct1_cand1:.1f}% (1T) -> {pct2_cand1:.1f}% (2T); "
                        f"Cand {runoff_candidates[1]}: {pct1_cand2:.1f}% (1T) -> {pct2_cand2:.1f}% (2T)."
                    ),
                    details={
                        "pct1_cand1": round(pct1_cand1, 2),
                        "pct2_cand1": round(pct2_cand1, 2),
                        "pct1_cand2": round(pct1_cand2, 2),
                        "pct2_cand2": round(pct2_cand2, 2),
                        "cand1": runoff_candidates[0],
                        "cand2": runoff_candidates[1],
                    },
                )
            )

    # 17. Crescimento matematicamente excedente (limite teórico de migração)
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
        ganho = c2 - c1

        # Votos de outros candidatos + brancos + nulos do 1T
        outros_votos_1t = sum(qtd for k, qtd in v1.items() if k != cand)
        pool_disponivel_1t = outros_votos_1t + s1.votos_brancos + s1.votos_nulos
        novos_eleitores = max(0, s2.comparecimento - s1.comparecimento)
        teto_maximo_crescimento = pool_disponivel_1t + novos_eleitores

        if ganho > teto_maximo_crescimento and ganho > 10:
            anomalies.append(
                Anomaly(
                    code="CRESCIMENTO_MATEMATICAMENTE_EXCEDENTE",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Crescimento de {cand_nome} excede o limite matemático de migração",
                    description=(
                        f"{cand_nome} ganhou {ganho} votos no 2T, superando o teto teórico de {teto_maximo_crescimento} "
                        f"(todos os votos de terceiros candidatos 1T [{outros_votos_1t}], brancos/nulos 1T [{s1.votos_brancos+s1.votos_nulos}] "
                        f"e novos votantes [{novos_eleitores}])."
                    ),
                    details={
                        "candidato": cand,
                        "nome": cand_nome,
                        "ganho": ganho,
                        "teto_teorico": teto_maximo_crescimento,
                    },
                )
            )

    # 18. Explosão de votos brancos e nulos
    pct_bn_1 = ((s1.votos_brancos + s1.votos_nulos) / s1.comparecimento * 100) if s1.comparecimento else 0
    pct_bn_2 = ((s2.votos_brancos + s2.votos_nulos) / s2.comparecimento * 100) if s2.comparecimento else 0
    if s2.comparecimento >= 50 and (pct_bn_2 - pct_bn_1 >= 15.0 or pct_bn_2 >= 25.0):
        anomalies.append(
            Anomaly(
                code="EXPLOSAO_BRANCOS_NULOS",
                category=CAT_VOTACAO,
                severity=SEV_MEDIA,
                title="Salto acentuado de votos brancos e nulos",
                description=(
                    f"A proporção de brancos e nulos subiu de {pct_bn_1:.1f}% (1T) para {pct_bn_2:.1f}% (2T) "
                    f"({s2.votos_brancos} brancos, {s2.votos_nulos} nulos)."
                ),
                details={"pct_bn_1t": round(pct_bn_1, 2), "pct_bn_2t": round(pct_bn_2, 2)},
            )
        )

    # 19. Extinção completa de brancos e nulos em seção grande
    if s2.comparecimento >= 150 and s2.votos_brancos == 0 and s2.votos_nulos == 0:
        anomalies.append(
            Anomaly(
                code="EXTINCAO_BRANCOS_NULOS",
                category=CAT_VOTACAO,
                severity=SEV_BAIXA,
                title="Ausência total de votos brancos e nulos em seção grande",
                description=f"Zero brancos e zero nulos entre {s2.comparecimento} eleitores no 2T (evento estatisticamente incomum).",
                details={"comparecimento": s2.comparecimento, "brancos": 0, "nulos": 0},
            )
        )

    # ========================================================================
    # GRUPO 4: TEMPORAL E OPERACIONAL
    # ========================================================================

    # 20. Horário de abertura anômalo
    if s2.abertura:
        try:
            ab_dt = datetime.fromisoformat(s2.abertura)
            if ab_dt.hour < 7 or (ab_dt.hour == 8 and ab_dt.minute > 30) or ab_dt.hour > 8:
                anomalies.append(
                    Anomaly(
                        code="HORARIO_ABERTURA_ANOMALO",
                        category=CAT_TEMPORAL,
                        severity=SEV_MEDIA,
                        title="Horário de abertura fora da janela regulamentar no 2T",
                        description=f"Votação iniciada às {ab_dt.strftime('%H:%M:%S')} (fora do horário normal 07:00-08:30).",
                        details={"abertura_2t": s2.abertura},
                    )
                )
        except Exception:
            pass

    # 21. Horário de encerramento anômalo
    if s2.encerramento:
        try:
            enc_dt = datetime.fromisoformat(s2.encerramento)
            if enc_dt.hour < 17 or enc_dt.hour >= 20:
                anomalies.append(
                    Anomaly(
                        code="HORARIO_ENCERRAMENTO_ANOMALO",
                        category=CAT_TEMPORAL,
                        severity=SEV_MEDIA,
                        title="Horário de encerramento fora da janela padrão no 2T",
                        description=f"Urna encerrada às {enc_dt.strftime('%H:%M:%S')} (encerramento antes das 17h ou após 20h).",
                        details={"encerramento_2t": s2.encerramento},
                    )
                )
        except Exception:
            pass

    # 22. Duração da votação substancialmente maior no 2T
    if s1.duracao_minutos and s2.duracao_minutos:
        diff_dur = s2.duracao_minutos - s1.duracao_minutos
        if diff_dur >= 60.0 and s2.comparecimento <= s1.comparecimento + 10:
            anomalies.append(
                Anomaly(
                    code="DURACAO_VOTACAO_INVERTIDA",
                    category=CAT_TEMPORAL,
                    severity=SEV_BAIXA,
                    title="Votação do 2T durou mais de 1h a mais que o 1T",
                    description=(
                        f"O 2T levou {s2.duracao_minutos:.0f} min vs {s1.duracao_minutos:.0f} min no 1T "
                        f"(+ {diff_dur:.0f} min), embora o 2T tenha apenas votação para Presidente."
                    ),
                    details={"duracao_1t": s1.duracao_minutos, "duracao_2t": s2.duracao_minutos, "delta_min": round(diff_dur, 1)},
                )
            )

    # ========================================================================
    # GRUPO 5: BIOMETRIA E IDENTIFICAÇÃO DO ELEITOR
    # ========================================================================

    # 23. Queda abrupta no reconhecimento biométrico
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        queda_bio = s1.pct_biometria - s2.pct_biometria
        if queda_bio >= 25.0:
            anomalies.append(
                Anomaly(
                    code="QUEDA_ABRUPTA_BIOMETRIA",
                    category=CAT_BIOMETRIA,
                    severity=SEV_MEDIA,
                    title="Queda abrupta na habilitação biométrica",
                    description=(
                        f"A taxa de validação biométrica caiu {queda_bio:.1f} pontos percentuais "
                        f"(1T: {s1.pct_biometria:.1f}% vs 2T: {s2.pct_biometria:.1f}%). Indica possível falha no leitor."
                    ),
                    details={"pct_bio_1t": s1.pct_biometria, "pct_bio_2t": s2.pct_biometria, "queda_pp": round(queda_bio, 2)},
                )
            )

    # 24. Surto de habilitação biográfica (ano de nascimento)
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        salto_bio_ano = s2.pct_biografia - s1.pct_biografia
        if salto_bio_ano >= 20.0:
            anomalies.append(
                Anomaly(
                    code="SURTO_HABILITACAO_BIOGRAFICA",
                    category=CAT_BIOMETRIA,
                    severity=SEV_MEDIA,
                    title="Aumento acentuado de habilitação por ano de nascimento",
                    description=(
                        f"Habilitações biográficas subiram de {s1.pct_biografia:.1f}% (1T) para {s2.pct_biografia:.1f}% (2T) "
                        f"(salto de {salto_bio_ano:.1f} pp)."
                    ),
                    details={"pct_bio_ano_1t": s1.pct_biografia, "pct_bio_ano_2t": s2.pct_biografia, "salto_pp": round(salto_bio_ano, 2)},
                )
            )

    # ========================================================================
    # GRUPO 6: INTEGRIDADE ARITMÉTICA
    # ========================================================================

    # 25. Divergência entre soma de votos e comparecimento no 2T
    soma_votos_2t = s2.votos_validos + s2.votos_brancos + s2.votos_nulos
    if s2.total_apurado_pres > 0 and soma_votos_2t != s2.comparecimento:
        anomalies.append(
            Anomaly(
                code="DIVERGENCIA_SOMA_VOTOS_COMPARECIMENTO",
                category=CAT_INTEGRIDADE,
                severity=SEV_ALTA,
                title="Divergência entre total apurado de votos e comparecimento no 2T",
                description=(
                    f"A soma de votos válidos ({s2.votos_validos}), brancos ({s2.votos_brancos}) e nulos ({s2.votos_nulos}) "
                    f"resulta em {soma_votos_2t}, divergindo do comparecimento oficial de {s2.comparecimento}."
                ),
                details={"soma_votos": soma_votos_2t, "comparecimento": s2.comparecimento},
            )
        )

    return anomalies


def compute_worst_severity(anomalies: list[Anomaly]) -> str:
    """Calcula a pior severidade entre as anomalias da seção."""
    if not anomalies:
        return "NORMAL"
    highest_weight = -1
    highest_sev = "NORMAL"
    for a in anomalies:
        weight = SEVERITY_WEIGHTS.get(a.severity, 0)
        if weight > highest_weight:
            highest_weight = weight
            highest_sev = a.severity
    return highest_sev


# ============================================================================
# EXECUTOR DA COMPARAÇÃO (MULTI-THREADED)
# ============================================================================

def _parse_bu_file_task(path: Path) -> tuple[Optional[UrnaKey], Optional[SectionExtraction]]:
    """Tarefa individual para worker ler e decodificar um BU."""
    try:
        data = path.read_bytes()
        extracted = extract_section_data(path, data)
        if extracted is None:
            return None, None
        key = UrnaKey(uf=extracted.uf, municipio=extracted.municipio, zona=extracted.zona, secao=extracted.secao)
        return key, extracted
    except Exception:
        return None, None


def run_comparison(config: ComparisonConfig) -> ComparisonResult:
    """Executa a análise comparativa de inconsistências entre 1T e 2T."""
    started_at = datetime.now()
    t0 = time.time()

    input_1t = config.input_dir_1t.resolve()
    input_2t = config.input_dir_2t.resolve()
    out_dir = config.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    def _log(msg: str) -> None:
        if not config.quiet:
            print(msg, file=sys.stderr, flush=True)

    _log("[1/5] Mapeando arquivos de Boletim de Urna (BU) em 1T e 2T...")

    # Mapeamento de municípios para nomes
    table: dict[tuple[str, int], Municipio] = {}
    if config.municipios_csv and config.municipios_csv.is_file():
        table = load_table(config.municipios_csv)

    # Coleta de caminhos de arquivos em 1T e 2T
    def _collect_bu_paths(root: Path) -> dict[UrnaKey, Path]:
        mapped = {}
        for entry in os.scandir(root):
            if entry.name.endswith("-bu.dat"):
                m = NAME_RE.match(entry.name)
                if m:
                    uf = m.group("uf").lower()
                    mun = int(m.group("municipio"))
                    zona = int(m.group("zona"))
                    secao = int(m.group("secao"))

                    # Filtros de linha de comando
                    if config.uf and uf != config.uf.lower():
                        continue
                    if config.municipio is not None and mun != config.municipio:
                        continue
                    if config.zona is not None and zona != config.zona:
                        continue
                    if config.secao is not None and secao != config.secao:
                        continue

                    k = UrnaKey(uf=uf, municipio=mun, zona=zona, secao=secao)
                    mapped[k] = Path(entry.path)
        return mapped

    files_1t = _collect_bu_paths(input_1t)
    files_2t = _collect_bu_paths(input_2t)

    all_keys = sorted(set(files_1t.keys()) | set(files_2t.keys()), key=lambda k: (k.uf, k.municipio, k.zona, k.secao))
    _log(f"      1T: {len(files_1t)} seções elegíveis | 2T: {len(files_2t)} seções elegíveis (Total único: {len(all_keys)})")

    # Decodificação concorrente dos BUs
    _log(f"[2/5] Decodificando BUs em paralelo ({config.max_workers} threads)...")

    bu_1t_extractions: dict[UrnaKey, SectionExtraction] = {}
    bu_2t_extractions: dict[UrnaKey, SectionExtraction] = {}

    paths_1t = list(files_1t.values())
    paths_2t = list(files_2t.values())

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        for k, ext in executor.map(_parse_bu_file_task, paths_1t):
            if k and ext:
                bu_1t_extractions[k] = ext

        for k, ext in executor.map(_parse_bu_file_task, paths_2t):
            if k and ext:
                bu_2t_extractions[k] = ext

    _log(f"      Decodificados com sucesso: {len(bu_1t_extractions)} no 1T e {len(bu_2t_extractions)} no 2T")

    # ========================================================================
    # COMPARAÇÃO E DETECÇÃO DE INCONSISTÊNCIAS
    # ========================================================================
    _log("[3/5] Executando matriz de 24+ verificações de inconsistências...")

    sections_comparison: list[SectionComparison] = []
    anomaly_counter = Counter()
    severity_counter = Counter()
    category_counter = Counter()
    municipality_anomaly_counter = Counter()

    total_1t_comp = 0
    total_2t_comp = 0
    total_1t_aptos = 0
    total_2t_aptos = 0
    total_1t_pres: dict[int, int] = Counter()
    total_2t_pres: dict[int, int] = Counter()
    total_1t_brancos = 0
    total_2t_brancos = 0
    total_1t_nulos = 0
    total_2t_nulos = 0

    for k in all_keys:
        s1 = bu_1t_extractions.get(k)
        s2 = bu_2t_extractions.get(k)

        # Atualiza totais estaduais
        if s1:
            total_1t_comp += s1.comparecimento
            total_1t_aptos += s1.aptos
            total_1t_brancos += s1.votos_brancos
            total_1t_nulos += s1.votos_nulos
            for cand, v in s1.votos_presidenciais.items():
                total_1t_pres[cand] += v
        if s2:
            total_2t_comp += s2.comparecimento
            total_2t_aptos += s2.aptos
            total_2t_brancos += s2.votos_brancos
            total_2t_nulos += s2.votos_nulos
            for cand, v in s2.votos_presidenciais.items():
                total_2t_pres[cand] += v

        anomalies = evaluate_section_anomalies(s1, s2)
        worst_sev = compute_worst_severity(anomalies)

        # Nome do município
        mun_nome = None
        if table:
            mun_obj = table.get((k.uf, k.municipio))
            if mun_obj:
                mun_nome = mun_obj.nome

        for a in anomalies:
            anomaly_counter[a.code] += 1
            severity_counter[a.severity] += 1
            category_counter[a.category] += 1
            mun_key = mun_nome or f"Município {k.municipio}"
            municipality_anomaly_counter[mun_key] += 1

        comp_sec = SectionComparison(
            uf=k.uf,
            municipio=k.municipio,
            zona=k.zona,
            secao=k.secao,
            municipio_nome=mun_nome,
            s1=s1,
            s2=s2,
            anomalies=anomalies,
            worst_severity=worst_sev,
        )
        sections_comparison.append(comp_sec)

    total_sections_with_anomalies = sum(1 for s in sections_comparison if s.anomalies)
    total_anomalies_count = sum(len(s.anomalies) for s in sections_comparison)

    # Ordena seções mais anômalas primeiro
    def _sort_key(s: SectionComparison):
        weight = SEVERITY_WEIGHTS.get(s.worst_severity, -1)
        return (-weight, -len(s.anomalies), s.municipio, s.zona, s.secao)

    sections_comparison.sort(key=_sort_key)

    finished_at = datetime.now()
    duration = round(time.time() - t0, 2)

    # ========================================================================
    # MONTAGEM DO RELATÓRIO ESTRUTURADO JSON
    # ========================================================================
    _log("[4/5] Compilando relatórios e estatísticas comparativas...")

    # Ranking comparativo de candidatos
    candidatos_comparativo = []
    all_cands = sorted(set(total_1t_pres.keys()) | set(total_2t_pres.keys()))
    for c in all_cands:
        v1 = total_1t_pres.get(c, 0)
        v2 = total_2t_pres.get(c, 0)
        delta = v2 - v1
        pct_delta = round((delta / v1 * 100), 2) if v1 > 0 else None
        nome = PRESIDENTIAL_CANDIDATES.get(c, f"Candidato {c}")
        candidatos_comparativo.append(
            {
                "numero": c,
                "nome": nome,
                "votos_1t": v1,
                "votos_2t": v2,
                "delta_votos": delta,
                "pct_crescimento": pct_delta,
            }
        )

    # Ordena por votos no 2T depois no 1T
    candidatos_comparativo.sort(key=lambda item: (-item["votos_2t"], -item["votos_1t"]))

    # Resumo executivo de métricas
    report_data: dict[str, Any] = {
        "metadados": {
            "gerado_em": finished_at.isoformat(),
            "iniciado_em": started_at.isoformat(),
            "duracao_segundos": duration,
            "diretorio_1t": str(input_1t),
            "diretorio_2t": str(input_2t),
            "diretorio_saida": str(out_dir),
            "filtros": {
                "uf": config.uf,
                "municipio": config.municipio,
                "zona": config.zona,
                "secao": config.secao,
            },
        },
        "totais_estaduais": {
            "eleitores_aptos_1t": total_1t_aptos,
            "eleitores_aptos_2t": total_2t_aptos,
            "comparecimento_1t": total_1t_comp,
            "comparecimento_2t": total_2t_comp,
            "pct_comparecimento_1t": round((total_1t_comp / total_1t_aptos * 100), 2) if total_1t_aptos else 0,
            "pct_comparecimento_2t": round((total_2t_comp / total_2t_aptos * 100), 2) if total_2t_aptos else 0,
            "abstencao_1t": max(0, total_1t_aptos - total_1t_comp),
            "abstencao_2t": max(0, total_2t_aptos - total_2t_comp),
            "votos_brancos_1t": total_1t_brancos,
            "votos_brancos_2t": total_2t_brancos,
            "votos_nulos_1t": total_1t_nulos,
            "votos_nulos_2t": total_2t_nulos,
            "candidatos": candidatos_comparativo,
        },
        "resumo_auditoria": {
            "total_secoes_analisadas": len(all_keys),
            "total_secoes_com_anomalias": total_sections_with_anomalies,
            "pct_secoes_com_anomalias": round(total_sections_with_anomalies / len(all_keys) * 100, 2) if all_keys else 0,
            "total_anomalias_detectadas": total_anomalies_count,
            "por_severidade": dict(severity_counter),
            "por_categoria": dict(category_counter),
            "por_tipo_anomalia": [
                {"codigo": code, "total": count} for code, count in anomaly_counter.most_common()
            ],
            "top_municipios_com_anomalias": [
                {"municipio": mun, "total_anomalias": count}
                for mun, count in municipality_anomaly_counter.most_common(15)
            ],
        },
        "secoes": [s.as_dict() for s in sections_comparison],
    }

    # Gravação do JSON
    json_path = out_dir / "comparison_report.json"
    json_report.write(json_path, report_data)

    # Gravação do HTML
    html_path = out_dir / "comparison_report.html"
    if config.write_html:
        _log("[5/5] Gerando relatório interativo HTML profissional...")
        html_content = generate_comparison_html(report_data)
        html_path.write_text(html_content, encoding="utf-8")

    # Montagem do resumo de console
    console_lines = [
        "",
        "=" * 80,
        "AUDITORIA FORENSE COMPARATIVA: 1º TURNO vs 2º TURNO (ELEIÇÕES 2026)",
        "=" * 80,
        f"Tempo de processamento: {duration:.2f}s | Seções analisadas: {len(all_keys):,}",
        f"Seções com alguma inconsistência: {total_sections_with_anomalies:,} ({report_data['resumo_auditoria']['pct_secoes_com_anomalias']}%)",
        f"Total de ocorrências de anomalias: {total_anomalies_count:,}",
        "-" * 80,
        "DISTRIBUIÇÃO POR SEVERIDADE:",
        f"  - ALTA (Crítica):    {severity_counter.get(SEV_ALTA, 0):,}",
        f"  - MÉDIA (Relevante): {severity_counter.get(SEV_MEDIA, 0):,}",
        f"  - BAIXA / INFO:      {severity_counter.get(SEV_BAIXA, 0) + severity_counter.get(SEV_INFO, 0):,}",
        "-" * 80,
        "PRINCIPAIS TIPOS DE INCONSISTÊNCIAS IDENTIFICADAS:",
    ]

    for code, count in anomaly_counter.most_common(12):
        console_lines.append(f"  • {code:<42} : {count:>5} seções")

    console_lines.extend(
        [
            "-" * 80,
            "TOTALIZAÇÃO COMPARATIVA PRESIDENCIAL:",
        ]
    )
    for c in candidatos_comparativo:
        v1_fmt = f"{c['votos_1t']:,}"
        v2_fmt = f"{c['votos_2t']:,}"
        delta_str = f"{c['delta_votos']:+,}"
        pct_str = f"({c['pct_crescimento']:+.2f}%)" if c["pct_crescimento"] is not None else ""
        console_lines.append(f"  {c['nome']:<22} │ 1T: {v1_fmt:>10} │ 2T: {v2_fmt:>10} │ Dif: {delta_str:>9} {pct_str}")

    comp1_fmt = f"{total_1t_comp:,}"
    comp2_fmt = f"{total_2t_comp:,}"
    delta_comp = total_2t_comp - total_1t_comp
    console_lines.append(
        f"  {'COMPARECIMENTO TOTAL':<22} │ 1T: {comp1_fmt:>10} │ 2T: {comp2_fmt:>10} │ Dif: {delta_comp:>+9,}"
    )

    console_lines.extend(
        [
            "-" * 80,
            f"Relatório JSON: {json_path}",
            f"Relatório HTML: {html_path}" if config.write_html else "HTML: suprimido (--no-html)",
            "=" * 80,
            "",
        ]
    )

    console_out = "\n".join(console_lines)
    return ComparisonResult(report=report_data, output_dir=out_dir, console=console_out)


# ============================================================================
# GERADOR DE RELATÓRIO HTML PROFISSIONAL E INTERATIVO
# ============================================================================

def generate_comparison_html(data: dict[str, Any]) -> str:
    """Gera relatório HTML responsivo, autônomo (sem CDNs) com busca e filtros."""
    meta = data["metadados"]
    resumo = data["resumo_auditoria"]
    totais = data["totais_estaduais"]
    secoes = data["secoes"]

    # Coleta de tipos de anomalias para o filtro select
    tipos_anomalias = resumo["por_tipo_anomalia"]

    # Prepara JSON leve embutido para renderização dinâmica rápida
    # (apenas seções com anomalias na tabela principal para manter HTML leve e rápido)
    anomalous_sections = [s for s in secoes if s.get("total_anomalias", 0) > 0][:2500]

    cand_rows = []
    for c in totais.get("candidatos", []):
        v1 = f"{c['votos_1t']:,}".replace(",", ".")
        v2 = f"{c['votos_2t']:,}".replace(",", ".")
        d = c["delta_votos"]
        d_str = f"{d:+,}".replace(",", ".")
        color_class = "text-emerald-700 font-semibold" if d > 0 else ("text-rose-700 font-semibold" if d < 0 else "text-slate-600")
        pct_str = f"({c['pct_crescimento']:+.2f}%)" if c["pct_crescimento"] is not None else ""
        cand_rows.append(f"""
        <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="py-2.5 px-4 font-mono font-bold text-slate-800">{c['numero']}</td>
            <td class="py-2.5 px-4 font-semibold text-slate-900">{html.escape(c['nome'])}</td>
            <td class="py-2.5 px-4 text-right font-mono">{v1}</td>
            <td class="py-2.5 px-4 text-right font-mono font-bold text-slate-900">{v2}</td>
            <td class="py-2.5 px-4 text-right font-mono {color_class}">{d_str} <span class="text-xs text-slate-500 font-normal">{pct_str}</span></td>
        </tr>
        """)

    anom_summary_rows = []
    for item in tipos_anomalias:
        code = item["codigo"]
        count = item["total"]
        pct = round(count / resumo["total_secoes_analisadas"] * 100, 2)
        anom_summary_rows.append(f"""
        <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="py-2 px-3 font-mono text-xs font-semibold text-slate-800">{html.escape(code)}</td>
            <td class="py-2 px-3 text-right font-mono font-bold text-slate-900">{count:,}</td>
            <td class="py-2 px-3 text-right font-mono text-xs text-slate-500">{pct:.2f}%</td>
        </tr>
        """)

    # Renderiza tabela inicial das 100 seções mais anômalas
    initial_rows = []
    for s in anomalous_sections[:100]:
        mun_str = html.escape(s.get("municipio_nome") or f"Município {s['municipio']}")
        zona = s["zona"]
        secao = s["secao"]
        sev = s.get("worst_severity", "NORMAL")
        sev_badge = {
            "ALTA": '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">ALTA</span>',
            "MEDIA": '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">MÉDIA</span>',
            "BAIXA": '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">BAIXA</span>',
        }.get(sev, f'<span class="text-xs">{sev}</span>')

        d1 = s.get("dados_1t") or {}
        d2 = s.get("dados_2t") or {}

        v1_22 = (d1.get("votos_presidenciais") or {}).get(22, 0)
        v2_22 = (d2.get("votos_presidenciais") or {}).get(22, 0)
        v1_13 = (d1.get("votos_presidenciais") or {}).get(13, 0)
        v2_13 = (d2.get("votos_presidenciais") or {}).get(13, 0)

        c1 = d1.get("comparecimento", 0)
        c2 = d2.get("comparecimento", 0)

        anom_badges = "".join(
            f'<span class="inline-block px-1.5 py-0.5 mr-1 mb-1 rounded text-[11px] font-mono bg-slate-100 text-slate-700 border border-slate-200" title="{html.escape(a.get("description", ""))}">{html.escape(a["code"])}</span>'
            for a in s.get("anomalias", [])
        )

        initial_rows.append(f"""
        <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors text-xs">
            <td class="py-2.5 px-3 font-semibold text-slate-800">{mun_str}</td>
            <td class="py-2.5 px-2 text-center font-mono">{zona}</td>
            <td class="py-2.5 px-2 text-center font-mono font-bold text-slate-900">{secao}</td>
            <td class="py-2.5 px-2 text-center">{sev_badge}</td>
            <td class="py-2.5 px-2 text-right font-mono">{c1} &rarr; <strong>{c2}</strong></td>
            <td class="py-2.5 px-2 text-right font-mono">{v1_22} &rarr; <strong>{v2_22}</strong></td>
            <td class="py-2.5 px-2 text-right font-mono">{v1_13} &rarr; <strong>{v2_13}</strong></td>
            <td class="py-2.5 px-3">{anom_badges}</td>
        </tr>
        """)

    anom_json_str = json.dumps(anomalous_sections, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria Comparativa Forense 1T vs 2T - Eleições Gerais 2026</title>
    <style>
        /* CSS reset & utilitários modernos embarcados (100% offline, zero CDN) */
        *, ::before, ::after {{ box-sizing: border-box; border-width: 0; border-style: solid; border-color: #e2e8f0; }}
        body {{ margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8fafc; color: #1e293b; line-height: 1.5; }}
        .container {{ width: 100%; max-width: 1400px; margin-left: auto; margin-right: auto; padding: 1.5rem 1rem; }}
        .card {{ background-color: #ffffff; border-radius: 0.75rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05); padding: 1.25rem; margin-bottom: 1.5rem; }}
        .card-header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem; margin-bottom: 1rem; }}
        .grid {{ display: grid; gap: 1rem; }}
        .grid-cols-4 {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
        .grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        @media (max-width: 900px) {{ .grid-cols-4 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .grid-cols-2 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }} }}
        @media (max-width: 600px) {{ .grid-cols-4 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }} }}
        .stat-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; }}
        .stat-label {{ font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; }}
        .stat-value {{ font-size: 1.75rem; font-weight: 800; color: #0f172a; margin-top: 0.25rem; font-family: ui-monospace, monospace; }}
        .stat-desc {{ font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.875rem; }}
        th {{ background-color: #f8fafc; color: #475569; font-weight: 600; padding: 0.625rem 0.75rem; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
        td {{ padding: 0.625rem 0.75rem; border-bottom: 1px solid #f1f5f9; }}
        input, select {{ background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 0.375rem; padding: 0.5rem 0.75rem; font-size: 0.875rem; color: #0f172a; outline: none; }}
        input:focus, select:focus {{ border-color: #3b82f6; ring: 2px #93c5fd; }}
        .btn {{ display: inline-flex; align-items: center; justify-content: center; border-radius: 0.375rem; font-weight: 600; padding: 0.5rem 1rem; font-size: 0.875rem; cursor: pointer; transition: background 0.15s ease; }}
        .btn-primary {{ background: #2563eb; color: #ffffff; }}
        .btn-primary:hover {{ background: #1d4ed8; }}
        .badge {{ display: inline-flex; align-items: center; padding: 0.125rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 700; }}
        .badge-red {{ background: #ffe4e6; color: #9f1239; border: 1px solid #fecdd3; }}
        .badge-yellow {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
        .badge-blue {{ background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }}
        .font-mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 2px solid #0f172a; padding-bottom: 1rem;">
            <div>
                <span class="badge badge-blue font-mono" style="margin-bottom: 0.5rem;">AUDITORIA FORENSE ELEITORAL OFICIAL</span>
                <h1 style="font-size: 1.75rem; font-weight: 900; color: #0f172a; margin: 0.25rem 0;">Relatório Comparativo de Inconsistências: 1º vs 2º Turno</h1>
                <p style="font-size: 0.875rem; color: #475569; margin: 0;">Eleições Gerais 2026 &bull; Cruzamento Integral de Boletins de Urna (BUs) Oficiais do TSE</p>
            </div>
            <div style="text-align: right; font-size: 0.8125rem; color: #64748b;">
                <div><strong>Iniciado:</strong> {html.escape(meta['iniciado_em'])}</div>
                <div><strong>Duração da análise:</strong> {meta['duracao_segundos']}s</div>
                <div><strong>Estado/UF:</strong> Santa Catarina (SC)</div>
            </div>
        </div>

        <!-- KPI CARDS -->
        <div class="grid grid-cols-4" style="margin-bottom: 1.5rem;">
            <div class="stat-card" style="border-left: 4px solid #3b82f6;">
                <div class="stat-label">Total de Seções Auditadas</div>
                <div class="stat-value">{resumo['total_secoes_analisadas']:,}</div>
                <div class="stat-desc">Pares completos de BUs no 1T e 2T</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #ef4444;">
                <div class="stat-label">Seções com Alguma Inconsistência</div>
                <div class="stat-value" style="color: #b91c1c;">{resumo['total_secoes_com_anomalias']:,}</div>
                <div class="stat-desc">{resumo['pct_secoes_com_anomalias']}% do eleitorado estadual</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #f59e0b;">
                <div class="stat-label">Inconsistências Críticas (Alta)</div>
                <div class="stat-value" style="color: #d97706;">{resumo['por_severidade'].get('ALTA', 0):,}</div>
                <div class="stat-desc">Quedas anômalas, variações cadastrais ou swaps</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #10b981;">
                <div class="stat-label">Votos Computados (2T)</div>
                <div class="stat-value" style="color: #047857;">{totais['comparecimento_2t']:,}</div>
                <div class="stat-desc">Comparecimento: {totais['pct_comparecimento_2t']}% dos aptos</div>
            </div>
        </div>

        <!-- PAINEL COMPARATIVO DE VOTAÇÃO E CATEGORIAS -->
        <div class="grid grid-cols-2">
            <!-- TABELA COMPARATIVA DE CANDIDATOS -->
            <div class="card">
                <div class="card-header">
                    <h2 style="font-size: 1.125rem; font-weight: 700; margin: 0; color: #0f172a;">Totalização Presidencial Estadual (1T vs 2T)</h2>
                    <span style="font-size: 0.75rem; color: #64748b;">Consolidado de todas as urnas apuradas</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Nº</th>
                            <th>Candidato</th>
                            <th style="text-align: right;">Votos 1T</th>
                            <th style="text-align: right;">Votos 2T</th>
                            <th style="text-align: right;">Variação Nominal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(cand_rows)}
                        <tr class="border-t-2 border-slate-200 bg-slate-50 font-bold">
                            <td colspan="2" class="py-2.5 px-4 text-slate-800">COMPARECIMENTO TOTAL</td>
                            <td class="py-2.5 px-4 text-right font-mono">{totais['comparecimento_1t']:,}</td>
                            <td class="py-2.5 px-4 text-right font-mono">{totais['comparecimento_2t']:,}</td>
                            <td class="py-2.5 px-4 text-right font-mono text-slate-900">{totais['comparecimento_2t'] - totais['comparecimento_1t']:+,}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- DISTRIBUIÇÃO DOS 24+ DETECTORES -->
            <div class="card">
                <div class="card-header">
                    <h2 style="font-size: 1.125rem; font-weight: 700; margin: 0; color: #0f172a;">Distribuição de Inconsistências Detectadas</h2>
                    <span style="font-size: 0.75rem; color: #64748b;">Ocorrências por regra forense</span>
                </div>
                <div style="max-height: 290px; overflow-y: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Código da Inconsistência</th>
                                <th style="text-align: right;">Urnas</th>
                                <th style="text-align: right;">% Urnas</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(anom_summary_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- PAINEL INTERATIVO DE PESQUISA E FILTROS -->
        <div class="card">
            <div class="card-header">
                <div>
                    <h2 style="font-size: 1.125rem; font-weight: 700; margin: 0; color: #0f172a;">Explorador Interativo de Seções Eleitorais</h2>
                    <p style="font-size: 0.75rem; color: #64748b; margin: 0.25rem 0 0 0;">Filtre em tempo real por município, zona, seção, tipo ou gravidade de anomalia</p>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <input type="text" id="searchInput" placeholder="Buscar município, zona ou seção..." style="width: 280px;" oninput="applyFilters()">
                    <select id="severitySelect" onchange="applyFilters()">
                        <option value="ALL">Todas as Severidades</option>
                        <option value="ALTA">Severidade ALTA (Crítica)</option>
                        <option value="MEDIA">Severidade MÉDIA</option>
                        <option value="BAIXA">Severidade BAIXA</option>
                    </select>
                    <select id="anomalySelect" onchange="applyFilters()" style="max-width: 250px;">
                        <option value="ALL">Todos os Tipos de Anomalia</option>
                        {"".join(f'<option value="{a["codigo"]}">{a["codigo"]} ({a["total"]})</option>' for a in tipos_anomalias)}
                    </select>
                </div>
            </div>

            <!-- TABELA DE RESULTADOS -->
            <div style="overflow-x: auto;">
                <table id="mainTable">
                    <thead>
                        <tr>
                            <th>Município</th>
                            <th style="text-align: center;">Zona</th>
                            <th style="text-align: center;">Seção</th>
                            <th style="text-align: center;">Severidade</th>
                            <th style="text-align: right;">Comparecimento</th>
                            <th style="text-align: right;">Flavio (22) 1T &rarr; 2T</th>
                            <th style="text-align: right;">Lula (13) 1T &rarr; 2T</th>
                            <th>Inconsistências Identificadas</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        {"".join(initial_rows)}
                    </tbody>
                </table>
            </div>
            <div id="filterCount" style="margin-top: 0.75rem; font-size: 0.8125rem; color: #64748b; text-align: right;">
                Exibindo as 100 seções mais críticas de {len(anomalous_sections):,} seções com inconsistências registradas.
            </div>
        </div>

        <!-- FOOTER METODOLÓGICO -->
        <div style="text-align: center; margin-top: 2rem; padding: 1.5rem; font-size: 0.75rem; color: #64748b; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0 0 0.5rem 0;"><strong>Ferramenta Forense de Auditoria da Urna Eletrônica</strong> &bull; Análise estritamente científica, matemática e não-destrutiva de integridade pública.</p>
            <p style="margin: 0;">As classificações refletem regras técnicas objetivas comparando fontes oficiais do TSE (bu.dat) de 1º e 2º Turno, sem emitir juízo político.</p>
        </div>
    </div>

    <!-- SCRIPT DE FILTRAGEM INTERATIVA OFFLINE -->
    <script>
        const allSections = {anom_json_str};

        function getSeverityBadge(sev) {{
            if (sev === 'ALTA') return '<span class="badge badge-red">ALTA</span>';
            if (sev === 'MEDIA') return '<span class="badge badge-yellow">MÉDIA</span>';
            if (sev === 'BAIXA') return '<span class="badge badge-blue">BAIXA</span>';
            return '<span class="text-xs">' + sev + '</span>';
        }}

        function applyFilters() {{
            const search = document.getElementById('searchInput').value.toLowerCase().trim();
            const sevFilter = document.getElementById('severitySelect').value;
            const anomFilter = document.getElementById('anomalySelect').value;

            const filtered = allSections.filter(s => {{
                if (sevFilter !== 'ALL' && s.worst_severity !== sevFilter) return false;
                if (anomFilter !== 'ALL' && !s.anomalias.some(a => a.code === anomFilter)) return false;

                if (search) {{
                    const mun = (s.municipio_nome || '').toLowerCase();
                    const munCode = String(s.municipio || '');
                    const zona = String(s.zona || '');
                    const secao = String(s.secao || '');
                    const hasAnom = s.anomalias.some(a => a.code.toLowerCase().includes(search));
                    if (!mun.includes(search) && !munCode.includes(search) && !zona.includes(search) && !secao.includes(search) && !hasAnom) {{
                        return false;
                    }}
                }}
                return true;
            }});

            const tbody = document.getElementById('tableBody');
            const limit = Math.min(filtered.length, 150);
            let html = '';

            for (let i = 0; i < limit; i++) {{
                const s = filtered[i];
                const d1 = s.dados_1t || {{}};
                const d2 = s.dados_2t || {{}};
                const p1 = d1.votos_presidenciais || {{}};
                const p2 = d2.votos_presidenciais || {{}};

                const v1_22 = p1['22'] || 0;
                const v2_22 = p2['22'] || 0;
                const v1_13 = p1['13'] || 0;
                const v2_13 = p2['13'] || 0;

                const c1 = d1.comparecimento || 0;
                const c2 = d2.comparecimento || 0;

                const badges = s.anomalias.map(a => 
                    `<span class="badge font-mono" style="background:#f1f5f9; color:#334155; margin-right:4px; margin-bottom:4px;" title="${{a.description || ''}}">${{a.code}}</span>`
                ).join('');

                html += `
                <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors text-xs">
                    <td class="py-2.5 px-3 font-semibold text-slate-800">${{s.municipio_nome || 'Município ' + s.municipio}}</td>
                    <td class="py-2.5 px-2 text-center font-mono">${{s.zona}}</td>
                    <td class="py-2.5 px-2 text-center font-mono font-bold text-slate-900">${{s.secao}}</td>
                    <td class="py-2.5 px-2 text-center">${{getSeverityBadge(s.worst_severity)}}</td>
                    <td class="py-2.5 px-2 text-right font-mono">${{c1}} &rarr; <strong>${{c2}}</strong></td>
                    <td class="py-2.5 px-2 text-right font-mono">${{v1_22}} &rarr; <strong>${{v2_22}}</strong></td>
                    <td class="py-2.5 px-2 text-right font-mono">${{v1_13}} &rarr; <strong>${{v2_13}}</strong></td>
                    <td class="py-2.5 px-3">${{badges}}</td>
                </tr>`;
            }}

            tbody.innerHTML = html;
            document.getElementById('filterCount').textContent = `Exibindo ${{limit}} de ${{filtered.length}} seções encontradas nos filtros.`;
        }}
    </script>
</body>
</html>
"""
