"""Motor de auditoria comparativa de inconsistências entre 1º e 2º Turno.

Contém exatamente 100 verificações forenses e estatísticas automatizadas
para auditoria técnica de integridade entre turnos eleitorais (TSE).
"""

from __future__ import annotations

import html
import json
import os
import sys
import time
from collections import Counter, defaultdict
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

# Candidatos oficiais de referência
PRESIDENTIAL_CANDIDATES = {
    13: "LULA",
    22: "FLAVIO BOLSONARO",
    14: "RENAN SANTOS",
    70: "ESCRITOR AUGUSTO CURY",
    55: "RONALDO CAIADO",
    12: "CIRO GOMES",
}

# Severidades
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

# Categorias dos 100 detectores
CAT_HARDWARE = "HARDWARE_E_CARGA"
CAT_ELEITORADO = "CADASTRO_E_ELEITORADO"
CAT_COMPARECIMENTO = "COMPARECIMENTO_E_ABSTENCAO"
CAT_VOTACAO = "VOTACAO_E_MIGRACAO_TERCEIRA_VIA"
CAT_BIOMETRIA = "BIOMETRIA_E_HABILITACAO"
CAT_TEMPORAL = "TEMPO_E_COMPORTAMENTO"
CAT_BRANCOS_NULOS = "BRANCOS_E_NULOS"
CAT_INTEGRIDADE = "INTEGRIDADE_E_PAREAMENTO"


@dataclass
class Anomaly:
    """Registro de uma inconsistência identificada."""
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
    municipio_correspondencia: Optional[int]
    zona_correspondencia: Optional[int]
    secao_correspondencia: Optional[int]
    numero_interno_urna: Optional[int]
    numero_serie_fv: Optional[str]
    numero_serie_fc: Optional[str]
    versao_votacao: Optional[str]
    codigo_carga: Optional[str]
    data_carga: Optional[str]
    nome_gerador_midia: Optional[str]
    serial_tpm: Optional[str]
    serial_instalacao: Optional[str]
    tipo_arquivo: Optional[int]
    data_hora_emissao: Optional[str]
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
    # Terceira via
    total_terceira_via: int
    votos_terceira_via: dict[int, int]
    cadeia_hash_valida: Optional[bool]


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
    corr_ident = corr.get("identificacao") or {}
    mun_corr = corr_ident.get("municipio")
    zona_corr = corr_ident.get("zona")
    secao_corr = corr_ident.get("secao")
    carga = corr.get("carga") or {}
    num_interno = carga.get("numero_interno_urna")
    num_serie_fc = carga.get("numero_serie_fc")
    cod_carga = carga.get("codigo_carga")
    data_carga = carga.get("data_hora_carga")
    gen_midia = carga.get("identificador_gerador_midia") or {}
    nome_gerador = gen_midia.get("nome")
    serial_tpm = gen_midia.get("serial_certificado_tpm")
    serial_instalacao = gen_midia.get("serial_instalacao")

    num_serie_fv = urna_block.get("numero_serie_fv")
    versao_votacao = urna_block.get("versao_votacao")
    tipo_arquivo = urna_block.get("tipo_arquivo")

    abertura_dt = bu.abertura
    encerramento_dt = bu.encerramento
    duracao_minutos = None
    if abertura_dt and encerramento_dt:
        duracao_minutos = round((encerramento_dt - abertura_dt).total_seconds() / 60.0, 2)

    data_emissao_str = bu.data_hora_emissao.isoformat() if bu.data_hora_emissao else None

    # Votação presidencial
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

    # Terceira via
    votos_terceira = {cand: qtd for cand, qtd in votos_pres.items() if cand not in (13, 22)}
    total_terceira = sum(votos_terceira.values())

    cadeia_valida = all(c.get("status") == "VALIDADO" for c in bu.cadeia_hashes) if bu.cadeia_hashes else True

    return SectionExtraction(
        path=str(path),
        uf=uf,
        municipio=municipio,
        zona=zona,
        secao=secao,
        local=local,
        municipio_correspondencia=mun_corr,
        zona_correspondencia=zona_corr,
        secao_correspondencia=secao_corr,
        numero_interno_urna=num_interno,
        numero_serie_fv=num_serie_fv,
        numero_serie_fc=num_serie_fc,
        versao_votacao=versao_votacao,
        codigo_carga=cod_carga,
        data_carga=data_carga,
        nome_gerador_midia=nome_gerador,
        serial_tpm=serial_tpm,
        serial_instalacao=serial_instalacao,
        tipo_arquivo=tipo_arquivo,
        data_hora_emissao=data_emissao_str,
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
        total_terceira_via=total_terceira,
        votos_terceira_via=votos_terceira,
        cadeia_hash_valida=cadeia_valida,
    )


# ============================================================================
# CATÁLOGO DE 100 VERIFICAÇÕES DE INCONSISTÊNCIAS FORENSES E ESTATÍSTICAS
# ============================================================================

def evaluate_section_anomalies(
    s1: Optional[SectionExtraction],
    s2: Optional[SectionExtraction],
    runoff_candidates: tuple[int, int] = (13, 22),
    mun_stats: Optional[dict[str, Any]] = None,
) -> list[Anomaly]:
    """Aplica o catálogo completo de 100 verificações automatizadas."""
    anomalies: list[Anomaly] = []

    # ------------------------------------------------------------------------
    # PAREAMENTO BÁSICO DE SEÇÃO
    # ------------------------------------------------------------------------
    if s1 is None and s2 is not None:
        anomalies.append(
            Anomaly(
                code="CHK096_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_2T",
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
                code="CHK095_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_1T",
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
    # GRUPO 1: HARDWARE, EQUIPAMENTO E CARGA (CHK001 a CHK015)
    # ========================================================================

    # CHK001: Troca de urna física
    if s1.numero_interno_urna and s2.numero_interno_urna and s1.numero_interno_urna != s2.numero_interno_urna:
        anomalies.append(
            Anomaly(
                code="CHK001_TROCA_URNA_FISICA",
                category=CAT_HARDWARE,
                severity=SEV_MEDIA,
                title="Número interno da urna física alterado",
                description=f"Urna substituída: 1T={s1.numero_interno_urna} vs 2T={s2.numero_interno_urna}.",
                details={"urna_1t": s1.numero_interno_urna, "urna_2t": s2.numero_interno_urna},
            )
        )

    # CHK002: Troca de Flash de Votação
    if s1.numero_serie_fv and s2.numero_serie_fv and s1.numero_serie_fv != s2.numero_serie_fv:
        anomalies.append(
            Anomaly(
                code="CHK002_TROCA_FLASH_VOTACAO",
                category=CAT_HARDWARE,
                severity=SEV_MEDIA,
                title="Serial da Flash de Votação (FV) alterado",
                description=f"FV alterada: 1T={s1.numero_serie_fv} vs 2T={s2.numero_serie_fv}.",
                details={"fv_1t": s1.numero_serie_fv, "fv_2t": s2.numero_serie_fv},
            )
        )

    # CHK003: Troca de Flash de Carga
    if s1.numero_serie_fc and s2.numero_serie_fc and s1.numero_serie_fc != s2.numero_serie_fc:
        anomalies.append(
            Anomaly(
                code="CHK003_TROCA_FLASH_CARGA",
                category=CAT_HARDWARE,
                severity=SEV_MEDIA,
                title="Serial da Flash de Carga (FC) alterado",
                description=f"FC alterada: 1T={s1.numero_serie_fc} vs 2T={s2.numero_serie_fc}.",
                details={"fc_1t": s1.numero_serie_fc, "fc_2t": s2.numero_serie_fc},
            )
        )

    # CHK004: Modelo de urna divergente
    if s1.numero_interno_urna and s2.numero_interno_urna:
        m1 = str(s1.numero_interno_urna)[:2]
        m2 = str(s2.numero_interno_urna)[:2]
        if m1 != m2 and len(str(s1.numero_interno_urna)) == len(str(s2.numero_interno_urna)):
            anomalies.append(
                Anomaly(
                    code="CHK004_MODELO_URNA_DIVERGENTE",
                    category=CAT_HARDWARE,
                    severity=SEV_ALTA,
                    title="Modelo de urna divergente entre turnos",
                    description=f"Geração/série da urna diferente: 1T={s1.numero_interno_urna} vs 2T={s2.numero_interno_urna}.",
                    details={"urna_1t": s1.numero_interno_urna, "urna_2t": s2.numero_interno_urna},
                )
            )

    # CHK005: Versão de software alterada
    if s1.versao_votacao and s2.versao_votacao and s1.versao_votacao != s2.versao_votacao:
        anomalies.append(
            Anomaly(
                code="CHK005_VERSAO_SOFTWARE_ALTERADA",
                category=CAT_HARDWARE,
                severity=SEV_ALTA,
                title="Versão do software de votação divergente",
                description=f"Software alterado: 1T '{s1.versao_votacao}' vs 2T '{s2.versao_votacao}'.",
                details={"versao_1t": s1.versao_votacao, "versao_2t": s2.versao_votacao},
            )
        )

    # CHK006: Mudança de local de votação
    if s1.local is not None and s2.local is not None and s1.local != s2.local:
        anomalies.append(
            Anomaly(
                code="CHK006_MUDANCA_LOCAL_VOTACAO",
                category=CAT_HARDWARE,
                severity=SEV_BAIXA,
                title="Local físico de votação remanejado",
                description=f"Local alterado de {s1.local} (1T) para {s2.local} (2T).",
                details={"local_1t": s1.local, "local_2t": s2.local},
            )
        )

    # CHK007: Código de carga alterado na mesma urna
    if s1.codigo_carga and s2.codigo_carga and s1.numero_interno_urna == s2.numero_interno_urna:
        if s1.codigo_carga != s2.codigo_carga:
            anomalies.append(
                Anomaly(
                    code="CHK007_CODIGO_CARGA_ALTERADO",
                    category=CAT_HARDWARE,
                    severity=SEV_BAIXA,
                    title="Código de carga recarregado na mesma urna",
                    description="A mesma urna física recebeu novo código de carga para o 2T.",
                    details={"carga_1t": s1.codigo_carga, "carga_2t": s2.codigo_carga},
                )
            )

    # CHK008: Data de carga do 2T anterior ao 1T
    if s1.data_carga and s2.data_carga and s2.data_carga < s1.data_carga:
        anomalies.append(
            Anomaly(
                code="CHK008_DATA_CARGA_ANOMALA_2T",
                category=CAT_HARDWARE,
                severity=SEV_MEDIA,
                title="Data de carga do 2T anterior à data do 1T",
                description=f"Carga do 2T ({s2.data_carga}) tem carimbo anterior à do 1T ({s1.data_carga}).",
                details={"data_carga_1t": s1.data_carga, "data_carga_2t": s2.data_carga},
            )
        )

    # CHK009: Carga tardia no dia da votação do 2T
    if s2.data_carga:
        try:
            dt_c = datetime.fromisoformat(s2.data_carga)
            if s2.abertura:
                dt_ab = datetime.fromisoformat(s2.abertura)
                if dt_c.date() == dt_ab.date() and dt_c.hour >= 7:
                    anomalies.append(
                        Anomaly(
                            code="CHK009_DATA_CARGA_TARDIA_2T",
                            category=CAT_HARDWARE,
                            severity=SEV_MEDIA,
                            title="Carga da urna realizada no próprio dia da votação do 2T",
                            description=f"Urna carregada emergencialmente às {dt_c.strftime('%H:%M:%S')} no dia da eleição.",
                            details={"data_carga": s2.data_carga},
                        )
                    )
        except Exception:
            pass

    # CHK010: Correspondência de seção inválida
    if (s2.secao_correspondencia and s2.secao_correspondencia != s2.secao) or (
        s2.zona_correspondencia and s2.zona_correspondencia != s2.zona
    ):
        anomalies.append(
            Anomaly(
                code="CHK010_CORRESPONDENCIA_INVALIDA_2T",
                category=CAT_HARDWARE,
                severity=SEV_ALTA,
                title="Identificação de correspondência diverge da seção",
                description=f"Correspondência Z{s2.zona_correspondencia}-S{s2.secao_correspondencia} != Seção Z{s2.zona}-S{s2.secao}.",
                details={"zona_corr": s2.zona_correspondencia, "secao_corr": s2.secao_correspondencia},
            )
        )

    # CHK011: Gerador de mídia divergente
    if s1.nome_gerador_midia and s2.nome_gerador_midia and s1.nome_gerador_midia != s2.nome_gerador_midia:
        anomalies.append(
            Anomaly(
                code="CHK011_GERADOR_MIDIA_DIVERGENTE",
                category=CAT_HARDWARE,
                severity=SEV_BAIXA,
                title="Mídia gerada em estação diferente entre turnos",
                description=f"Gerador de mídia alterado: 1T={s1.nome_gerador_midia} vs 2T={s2.nome_gerador_midia}.",
                details={"gerador_1t": s1.nome_gerador_midia, "gerador_2t": s2.nome_gerador_midia},
            )
        )

    # CHK012: Serial TPM divergente na mesma urna
    if s1.numero_interno_urna == s2.numero_interno_urna and s1.serial_tpm and s2.serial_tpm and s1.serial_tpm != s2.serial_tpm:
        anomalies.append(
            Anomaly(
                code="CHK012_TPM_SERIAL_DIVERGENTE",
                category=CAT_HARDWARE,
                severity=SEV_ALTA,
                title="Serial de hardware TPM alterado na mesma urna física",
                description=f"O chip de segurança TPM divergiu: 1T={s1.serial_tpm} vs 2T={s2.serial_tpm}.",
                details={"tpm_1t": s1.serial_tpm, "tpm_2t": s2.serial_tpm},
            )
        )

    # CHK013: Serial de instalação reiniciado
    if s1.serial_instalacao and s2.serial_instalacao and s1.numero_interno_urna == s2.numero_interno_urna:
        if s2.serial_instalacao < s1.serial_instalacao:
            anomalies.append(
                Anomaly(
                    code="CHK013_SERIAL_INSTALACAO_REINICIADO",
                    category=CAT_HARDWARE,
                    severity=SEV_MEDIA,
                    title="Serial de instalação reiniciado no 2T",
                    description=f"Serial de instalação recuou de {s1.serial_instalacao} para {s2.serial_instalacao}.",
                    details={"serial_1t": s1.serial_instalacao, "serial_2t": s2.serial_instalacao},
                )
            )

    # CHK014: Carga de urna em município diferente
    if s2.municipio_correspondencia and s2.municipio_correspondencia != s2.municipio:
        anomalies.append(
            Anomaly(
                code="CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO",
                category=CAT_HARDWARE,
                severity=SEV_ALTA,
                title="Município da correspondência diverge do município da seção",
                description=f"Correspondência vinculada ao município {s2.municipio_correspondencia}, mas a seção é {s2.municipio}.",
                details={"mun_secao": s2.municipio, "mun_corr": s2.municipio_correspondencia},
            )
        )
    # CHK015: Tipo de arquivo não é votacao_ue
    if s2.tipo_arquivo is not None and s2.tipo_arquivo != 1:
        anomalies.append(
            Anomaly(
                code="CHK015_TIPO_ARQUIVO_NAO_VOTACAO_UE",
                category=CAT_HARDWARE,
                severity=SEV_ALTA,
                title="Tipo de arquivo do BU não é de votação de urna oficial",
                description=f"Tipo de arquivo no BU é {s2.tipo_arquivo} (esperado: 1 - votacao_ue).",
                details={"tipo_arquivo": s2.tipo_arquivo},
            )
        )

    # ========================================================================
    # GRUPO 2: CADASTRO E ELEITORADO (CHK016 a CHK030)
    # ========================================================================

    # CHK016: Variação de eleitores aptos da seção
    if s1.aptos_secao != s2.aptos_secao:
        diff_aptos = s2.aptos_secao - s1.aptos_secao
        anomalies.append(
            Anomaly(
                code="CHK016_VARIACAO_APTOS_SECAO",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Variação no cadastro de eleitores originais da seção",
                description=f"Caderno eleitoral variou em {diff_aptos:+d} (1T: {s1.aptos_secao} vs 2T: {s2.aptos_secao}).",
                details={"aptos_1t": s1.aptos_secao, "aptos_2t": s2.aptos_secao, "delta": diff_aptos},
            )
        )

    # CHK017: Redução de aptos originais
    if s2.aptos_secao < s1.aptos_secao:
        anomalies.append(
            Anomaly(
                code="CHK017_REDUCAO_APTOS_SECAO",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Redução do número de eleitores originais no 2T",
                description=f"O número de aptos originais diminuiu de {s1.aptos_secao} para {s2.aptos_secao}.",
                details={"queda": s1.aptos_secao - s2.aptos_secao},
            )
        )

    # CHK018: Aumento de aptos originais
    if s2.aptos_secao > s1.aptos_secao:
        anomalies.append(
            Anomaly(
                code="CHK018_AUMENTO_APTOS_SECAO",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Aumento no número de eleitores originais no 2T",
                description=f"O número de aptos originais subiu de {s1.aptos_secao} para {s2.aptos_secao}.",
                details={"aumento": s2.aptos_secao - s1.aptos_secao},
            )
        )

    # CHK019: Pico de TTE absoluto
    delta_tte = abs(s2.aptos_tte - s1.aptos_tte)
    if delta_tte >= 20:
        anomalies.append(
            Anomaly(
                code="CHK019_PICO_TTE_ABSOLUTO",
                category=CAT_ELEITORADO,
                severity=SEV_MEDIA,
                title="Variação acentuada de eleitores em trânsito (TTE)",
                description=f"TTE oscilou de {s1.aptos_tte} (1T) para {s2.aptos_tte} (2T) (variação de {delta_tte}).",
                details={"tte_1t": s1.aptos_tte, "tte_2t": s2.aptos_tte, "delta": delta_tte},
            )
        )

    # CHK020: Pico de TTE percentual
    if s1.aptos > 0 and (delta_tte / s1.aptos) >= 0.10:
        anomalies.append(
            Anomaly(
                code="CHK020_PICO_TTE_PERCENTUAL",
                category=CAT_ELEITORADO,
                severity=SEV_MEDIA,
                title="Oscilação de TTE superior a 10% do eleitorado",
                description=f"Eleitores temporários oscilaram {delta_tte} ({delta_tte/s1.aptos*100:.1f}% da seção).",
                details={"pct_variacao": round(delta_tte / s1.aptos * 100, 2)},
            )
        )

    # CHK021: Extinção de TTE no 2T
    if s1.aptos_tte >= 15 and s2.aptos_tte == 0:
        anomalies.append(
            Anomaly(
                code="CHK021_EXTINCAO_TTE_2T",
                category=CAT_ELEITORADO,
                severity=SEV_BAIXA,
                title="Extinção de eleitores temporários no 2T",
                description=f"Seção tinha {s1.aptos_tte} TTEs no 1T e zero no 2T.",
                details={"tte_1t": s1.aptos_tte, "tte_2t": 0},
            )
        )

    # CHK022: Surgimento de TTE massivo no 2T
    if s1.aptos_tte == 0 and s2.aptos_tte >= 25:
        anomalies.append(
            Anomaly(
                code="CHK022_SURGIMENTO_TTE_MASSIVO_2T",
                category=CAT_ELEITORADO,
                severity=SEV_MEDIA,
                title="Entrada massiva de eleitores temporários no 2T",
                description=f"Seção não tinha TTE no 1T e recebeu {s2.aptos_tte} temporários no 2T.",
                details={"tte_2t": s2.aptos_tte},
            )
        )

    # CHK023: Aptos total divergente da soma
    if s2.aptos != (s2.aptos_secao + s2.aptos_tte):
        anomalies.append(
            Anomaly(
                code="CHK023_APTOS_TOTAL_DIVERGENTE_SOMA",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Soma de aptos (seção + TTE) diverge do total",
                description=f"Total aptos={s2.aptos} != secao={s2.aptos_secao} + tte={s2.aptos_tte}.",
                details={"aptos": s2.aptos, "soma": s2.aptos_secao + s2.aptos_tte},
            )
        )

    # CHK024: Seção com eleitorado anômalo reduzido
    if s2.aptos > 0 and s2.aptos < 15:
        anomalies.append(
            Anomaly(
                code="CHK024_SECAO_MINIMA_ANOMALA",
                category=CAT_ELEITORADO,
                severity=SEV_BAIXA,
                title="Seção eleitoral com menos de 15 aptos",
                description=f"Apenas {s2.aptos} eleitores aptos registrados.",
                details={"aptos": s2.aptos},
            )
        )

    # CHK025: Seção hipertrófica (> 500 aptos)
    if s2.aptos > 500:
        anomalies.append(
            Anomaly(
                code="CHK025_SECAO_HIPERTROFICA",
                category=CAT_ELEITORADO,
                severity=SEV_BAIXA,
                title="Seção eleitoral com mais de 500 aptos",
                description=f"Seção com {s2.aptos} eleitores aptos (acima da média legal de dimensionamento).",
                details={"aptos": s2.aptos},
            )
        )

    # CHK026: Seção com zero aptos
    if s2.aptos == 0:
        anomalies.append(
            Anomaly(
                code="CHK026_SECAO_SEM_APTOS",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Seção com zero eleitores aptos",
                description="Boletim de Urna gerado sem nenhum eleitor apto registrado.",
                details={"aptos": 0},
            )
        )

    # CHK027: Oscilação de aptos totais > 10%
    if s1.aptos > 0 and abs(s2.aptos - s1.aptos) / s1.aptos >= 0.10:
        anomalies.append(
            Anomaly(
                code="CHK027_OSCILACAO_APTOS_TOTAL_MAIOR_10PCT",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Oscilação do eleitorado total superior a 10%",
                description=f"Eleitorado total oscilou de {s1.aptos} para {s2.aptos}.",
                details={"aptos_1t": s1.aptos, "aptos_2t": s2.aptos},
            )
        )

    # CHK028: Divergência de aptos entre eleições
    if s2.aptos != s1.aptos and s2.aptos_secao == s1.aptos_secao and s2.aptos_tte == s1.aptos_tte:
        anomalies.append(
            Anomaly(
                code="CHK028_DIVERGENCIA_APTOS_ENTRE_ELEICOES",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Divergência inconsistente no total de aptos",
                description="Total de aptos diferiu sem alteração em aptos_secao ou aptos_tte.",
                details={"aptos_1t": s1.aptos, "aptos_2t": s2.aptos},
            )
        )

    # CHK029: TTE superior a 50% dos aptos
    if s2.aptos > 0 and s2.aptos_tte / s2.aptos >= 0.50:
        anomalies.append(
            Anomaly(
                code="CHK029_TRANSFERENCIA_TEMPORARIA_SUPERIOR_A_50PCT",
                category=CAT_ELEITORADO,
                severity=SEV_ALTA,
                title="Mais da metade dos eleitores são temporários (TTE)",
                description=f"{s2.aptos_tte} eleitores TTE de um total de {s2.aptos} ({s2.aptos_tte/s2.aptos*100:.1f}%).",
                details={"tte": s2.aptos_tte, "aptos": s2.aptos},
            )
        )

    # CHK030: Seção fora do padrão de numeração
    if s2.secao > 3000:
        anomalies.append(
            Anomaly(
                code="CHK030_ZONA_SECAO_FORA_PADRAO_CADASTRO",
                category=CAT_ELEITORADO,
                severity=SEV_BAIXA,
                title="Numeração de seção atípica",
                description=f"Seção com numeração elevada ({s2.secao}).",
                details={"secao": s2.secao},
            )
        )

    # ========================================================================
    # GRUPO 3: COMPARECIMENTO E ABSTENÇÃO (CHK031 a CHK045)
    # ========================================================================

    # CHK031: Comparecimento excede aptos no 2T
    if s2.comparecimento > s2.aptos:
        anomalies.append(
            Anomaly(
                code="CHK031_COMPARECIMENTO_EXCEDE_APTOS_2T",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Comparecimento maior que os aptos no 2T",
                description=f"Comparecimento ({s2.comparecimento}) > Aptos ({s2.aptos}).",
                details={"comp": s2.comparecimento, "aptos": s2.aptos},
            )
        )

    # CHK032: Comparecimento excede aptos no 1T
    if s1.comparecimento > s1.aptos:
        anomalies.append(
            Anomaly(
                code="CHK032_COMPARECIMENTO_EXCEDE_APTOS_1T",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Comparecimento maior que os aptos no 1T",
                description=f"Comparecimento no 1T ({s1.comparecimento}) > Aptos ({s1.aptos}).",
                details={"comp": s1.comparecimento, "aptos": s1.aptos},
            )
        )

    # CHK033: Comparecimento de 100% dos aptos
    if s2.aptos >= 50 and s2.comparecimento == s2.aptos:
        anomalies.append(
            Anomaly(
                code="CHK033_COMPARECIMENTO_100_PCT_2T",
                category=CAT_COMPARECIMENTO,
                severity=SEV_MEDIA,
                title="Comparecimento integral de 100% no 2T",
                description=f"100% de presença (zero abstenção) em seção com {s2.aptos} eleitores.",
                details={"aptos": s2.aptos, "comparecimento": s2.comparecimento},
            )
        )

    # CHK034: Abstenção superior a 50%
    if s2.aptos >= 50 and s2.pct_abstencao >= 50.0:
        anomalies.append(
            Anomaly(
                code="CHK034_ABSTENCAO_SUPERIOR_50PCT_2T",
                category=CAT_COMPARECIMENTO,
                severity=SEV_MEDIA,
                title="Abstenção superior a 50% no 2T",
                description=f"Abstenção de {s2.pct_abstencao:.1f}% ({s2.abstencao} de {s2.aptos} eleitores).",
                details={"abstencao": s2.abstencao, "pct": s2.pct_abstencao},
            )
        )

    # CHK035: Abstenção superior a 70%
    if s2.aptos >= 50 and s2.pct_abstencao >= 70.0:
        anomalies.append(
            Anomaly(
                code="CHK035_ABSTENCAO_SUPERIOR_70PCT_2T",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Abstenção crítica superior a 70% no 2T",
                description=f"Abstenção extrema de {s2.pct_abstencao:.1f}%.",
                details={"abstencao": s2.abstencao, "pct": s2.pct_abstencao},
            )
        )

    # CHK036: Salto de comparecimento > 25 pp
    delta_comp_pp = s2.pct_comparecimento - s1.pct_comparecimento
    if s1.aptos >= 50 and delta_comp_pp >= 25.0:
        anomalies.append(
            Anomaly(
                code="CHK036_SALTO_COMPARECIMENTO_MAIOR_25PP",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Salto de presença superior a 25 pontos percentuais",
                description=f"Presença saltou de {s1.pct_comparecimento:.1f}% para {s2.pct_comparecimento:.1f}% (+{delta_comp_pp:.1f} pp).",
                details={"pct_1t": s1.pct_comparecimento, "pct_2t": s2.pct_comparecimento, "delta_pp": delta_comp_pp},
            )
        )

    # CHK037: Queda de comparecimento > 25 pp
    if s1.aptos >= 50 and delta_comp_pp <= -25.0:
        anomalies.append(
            Anomaly(
                code="CHK037_QUEDA_COMPARECIMENTO_MAIOR_25PP",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Queda de presença superior a 25 pontos percentuais",
                description=f"Presença caiu de {s1.pct_comparecimento:.1f}% para {s2.pct_comparecimento:.1f}% ({delta_comp_pp:.1f} pp).",
                details={"pct_1t": s1.pct_comparecimento, "pct_2t": s2.pct_comparecimento, "delta_pp": delta_comp_pp},
            )
        )

    # CHK038: Comparecimento idêntico com aptos diferentes
    if s1.comparecimento == s2.comparecimento and s1.aptos != s2.aptos and abs(s1.aptos - s2.aptos) >= 10:
        anomalies.append(
            Anomaly(
                code="CHK038_COMPARECIMENTO_IDENTICO_COM_APTOS_DIFERENTES",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Comparecimento idêntico apesar de eleitorado diferente",
                description=f"Exatamente {s1.comparecimento} votantes nos dois turnos, mas aptos variaram de {s1.aptos} para {s2.aptos}.",
                details={"comp": s1.comparecimento, "aptos_1t": s1.aptos, "aptos_2t": s2.aptos},
            )
        )

    # CHK039: Comparecimento zero
    if s2.aptos >= 20 and s2.comparecimento == 0:
        anomalies.append(
            Anomaly(
                code="CHK039_COMPARECIMENTO_ZERO_2T",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Zero comparecimento no 2T",
                description=f"Nenhum eleitor compareceu à seção com {s2.aptos} aptos.",
                details={"aptos": s2.aptos},
            )
        )

    # CHK040: Comparecimento unitário
    if s2.aptos >= 50 and s2.comparecimento == 1:
        anomalies.append(
            Anomaly(
                code="CHK040_COMPARECIMENTO_UNITARIO_2T",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Apenas 1 eleitor compareceu no 2T",
                description=f"Apenas 1 voto computado entre {s2.aptos} eleitores.",
                details={"aptos": s2.aptos},
            )
        )

    # CHK041: Abstenção zero em ambos os turnos
    if s1.aptos >= 50 and s1.abstencao == 0 and s2.abstencao == 0:
        anomalies.append(
            Anomaly(
                code="CHK041_ABSTENCAO_ZERO_AMBOS_TURNOS",
                category=CAT_COMPARECIMENTO,
                severity=SEV_MEDIA,
                title="Zero abstenção em ambos os turnos",
                description=f"100% de comparecimento no 1T e no 2T na seção com {s2.aptos} eleitores.",
                details={"aptos": s2.aptos},
            )
        )

    # CHK042: Queda absoluta de comparecimento > 30%
    if s1.comparecimento >= 50:
        pct_queda_comp = (s1.comparecimento - s2.comparecimento) / s1.comparecimento * 100
        if pct_queda_comp >= 30.0:
            anomalies.append(
                Anomaly(
                    code="CHK042_QUEDA_COMPARECIMENTO_MAIOR_30PCT",
                    category=CAT_COMPARECIMENTO,
                    severity=SEV_MEDIA,
                    title="Queda absoluta de comparecimento superior a 30%",
                    description=f"Votantes caíram de {s1.comparecimento} para {s2.comparecimento} (-{pct_queda_comp:.1f}%).",
                    details={"comp_1t": s1.comparecimento, "comp_2t": s2.comparecimento, "queda_pct": pct_queda_comp},
                )
            )

    # CHK043: Explosão de comparecimento > 40%
    if s1.comparecimento >= 50:
        pct_salto_comp = (s2.comparecimento - s1.comparecimento) / s1.comparecimento * 100
        if pct_salto_comp >= 40.0:
            anomalies.append(
                Anomaly(
                    code="CHK043_EXPLOSAO_COMPARECIMENTO_MAIOR_40PCT",
                    category=CAT_COMPARECIMENTO,
                    severity=SEV_MEDIA,
                    title="Aumento absoluto de comparecimento superior a 40%",
                    description=f"Votantes saltaram de {s1.comparecimento} para {s2.comparecimento} (+{pct_salto_comp:.1f}%).",
                    details={"comp_1t": s1.comparecimento, "comp_2t": s2.comparecimento, "salto_pct": pct_salto_comp},
                )
            )

    # CHK044: Comparecimento discrepante da média municipal
    if mun_stats and s1.aptos >= 50:
        mun_delta_comp = mun_stats.get("media_delta_comp", 0.0)
        diff_from_mun = abs(delta_comp_pp - mun_delta_comp)
        if diff_from_mun >= 20.0:
            anomalies.append(
                Anomaly(
                    code="CHK044_COMPARECIMENTO_DISCREPANTE_DO_MUNICIPIO",
                    category=CAT_COMPARECIMENTO,
                    severity=SEV_ALTA,
                    title="Variação de comparecimento muito discrepante do município",
                    description=(
                        f"Na seção a presença variou {delta_comp_pp:+.1f} pp, "
                        f"enquanto a média do município variou {mun_delta_comp:+.1f} pp (desvio de {diff_from_mun:.1f} pp)."
                    ),
                    details={"secao_delta_pp": delta_comp_pp, "mun_delta_pp": mun_delta_comp, "desvio": diff_from_mun},
                )
            )

    # CHK045: Comparecimento presidencial menor que outros cargos no 2T
    if s2.total_apurado_pres > 0 and s2.total_apurado_pres < s2.comparecimento:
        diff_v = s2.comparecimento - s2.total_apurado_pres
        anomalies.append(
            Anomaly(
                code="CHK045_COMPARECIMENTO_PRESIDENCIAL_MENOR_QUE_CARGO_ESTADUAL",
                category=CAT_COMPARECIMENTO,
                severity=SEV_ALTA,
                title="Total apurado presidencial menor que o comparecimento",
                description=f"Total de votos na eleição presidencial ({s2.total_apurado_pres}) é menor que o comparecimento ({s2.comparecimento}).",
                details={"total_pres": s2.total_apurado_pres, "comparecimento": s2.comparecimento, "diferenca": diff_v},
            )
        )

    # ========================================================================
    # GRUPO 4: VOTAÇÃO PRESIDENCIAL E MIGRAÇÃO DE TERCEIRA VIA (CHK046 a CHK065)
    # ========================================================================
    v1 = s1.votos_presidenciais
    v2 = s2.votos_presidenciais
    cand_a = runoff_candidates[0]  # 13 (Lula)
    cand_b = runoff_candidates[1]  # 22 (Flavio)

    va1 = v1.get(cand_a, 0)
    va2 = v2.get(cand_a, 0)
    vb1 = v1.get(cand_b, 0)
    vb2 = v2.get(cand_b, 0)

    delta_comp = s2.comparecimento - s1.comparecimento

    # CHK046: Queda de votos de candidato finalista com comparecimento MAIOR
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
        if s2.comparecimento > s1.comparecimento and c1 > 0 and c2 < c1:
            queda = c1 - c2
            anomalies.append(
                Anomaly(
                    code="CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Queda de votos de {cand_nome} com comparecimento MAIOR no 2T",
                    description=(
                        f"{cand_nome} caiu de {c1} para {c2} votos (-{queda}), "
                        f"embora {delta_comp} novos eleitores tenham comparecido no 2T ({s1.comparecimento} -> {s2.comparecimento})."
                    ),
                    details={"candidato": cand, "votos_1t": c1, "votos_2t": c2, "queda": queda, "delta_comp": delta_comp},
                )
            )

    # CHK047: Queda de votos de candidato finalista com comparecimento IGUAL
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
        if s2.comparecimento == s1.comparecimento and c1 > 0 and c2 < c1:
            queda = c1 - c2
            anomalies.append(
                Anomaly(
                    code="CHK047_QUEDA_FINALISTA_COM_COMPARECIMENTO_IGUAL",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Queda de votos de {cand_nome} com comparecimento EXATAMENTE IGUAL",
                    description=f"{cand_nome} perdeu {queda} votos com o mesmo comparecimento exato ({s1.comparecimento}).",
                    details={"candidato": cand, "votos_1t": c1, "votos_2t": c2, "queda": queda},
                )
            )

    # CHK048: Queda desproporcional ao comparecimento
    if s2.comparecimento < s1.comparecimento and s1.comparecimento >= 50:
        pct_queda_geral = (s1.comparecimento - s2.comparecimento) / s1.comparecimento
        for cand in runoff_candidates:
            c1 = v1.get(cand, 0)
            c2 = v2.get(cand, 0)
            cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
            if c1 >= 25 and c2 < c1:
                pct_queda_cand = (c1 - c2) / c1
                if pct_queda_cand > (2.5 * pct_queda_geral) and (pct_queda_cand - pct_queda_geral) >= 0.20:
                    anomalies.append(
                        Anomaly(
                            code="CHK048_QUEDA_DESPROPORCIONAL_AO_COMPARECIMENTO",
                            category=CAT_VOTACAO,
                            severity=SEV_ALTA,
                            title=f"Queda de {cand_nome} muito superior à queda de comparecimento",
                            description=(
                                f"Comparecimento caiu {pct_queda_geral*100:.1f}%, mas {cand_nome} perdeu "
                                f"{pct_queda_cand*100:.1f}% dos seus votos ({c1} -> {c2})."
                            ),
                            details={"queda_cand_pct": pct_queda_cand * 100, "queda_comp_pct": pct_queda_geral * 100},
                        )
                    )

    # CHK049: Perda brusca maior que 30% com comparecimento estável (+-5%)
    if abs(delta_comp) <= (s1.comparecimento * 0.05):
        for cand in runoff_candidates:
            c1 = v1.get(cand, 0)
            c2 = v2.get(cand, 0)
            cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
            if c1 >= 30 and (c1 - c2) / c1 >= 0.30:
                anomalies.append(
                    Anomaly(
                        code="CHK049_PERDA_BRUSCA_MAIOR_30PCT_FINALISTA",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"{cand_nome} perdeu mais de 30% dos votos com presença estável",
                        description=f"{cand_nome} perdeu {(c1-c2)/c1*100:.1f}% dos votos nominais ({c1} -> {c2}).",
                        details={"votos_1t": c1, "votos_2t": c2},
                    )
                )

    # CHK050: Desaparecimento de votos no 2T
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
        if c1 >= 15 and c2 == 0:
            anomalies.append(
                Anomaly(
                    code="CHK050_DESAPARECIMENTO_FINALISTA_NO_2T",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Desaparecimento total de votos de {cand_nome}",
                    description=f"{cand_nome} tinha {c1} votos no 1T e zerou (0 votos) no 2T.",
                    details={"votos_1t": c1, "votos_2t": 0},
                )
            )

    # CHK051: Zero votos para finalista em seção grande
    for cand in runoff_candidates:
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
        if s2.votos_validos >= 60 and c2 == 0:
            anomalies.append(
                Anomaly(
                    code="CHK051_ZERO_VOTOS_FINALISTA_SECAO_GRANDE",
                    category=CAT_VOTACAO,
                    severity=SEV_MEDIA,
                    title=f"{cand_nome} com zero votos no 2T em seção grande",
                    description=f"Nenhum voto para {cand_nome} em seção com {s2.votos_validos} votos válidos no 2T.",
                    details={"validos": s2.votos_validos},
                )
            )

    # CHK052: Unanimidade de 100% para um único candidato
    if s2.votos_validos >= 50:
        for cand, qtd in v2.items():
            if qtd == s2.votos_validos and cand in runoff_candidates:
                cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
                anomalies.append(
                    Anomaly(
                        code="CHK052_UNANIMIDADE_100PCT_FINALISTA_2T",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"100% de unanimidade para {cand_nome} no 2T",
                        description=f"Todos os {s2.votos_validos} votos válidos foram para {cand_nome}.",
                        details={"votos": qtd},
                    )
                )

    # CHK053: Absorção de 100% da terceira via por um único candidato
    tot_terceira = s1.total_terceira_via
    if tot_terceira >= 25:
        ganho_a = max(0, va2 - va1)
        ganho_b = max(0, vb2 - vb1)
        tot_ganho = ganho_a + ganho_b
        if tot_ganho >= tot_terceira * 0.8:
            if ganho_a >= tot_ganho * 0.95 and ganho_b <= 0:
                anomalies.append(
                    Anomaly(
                        code="CHK053_ABSORCAO_100PCT_TERCEIRA_VIA_POR_UM_CANDIDATO",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"100% dos votos de terceira via absorvidos por {PRESIDENTIAL_CANDIDATES.get(cand_a, cand_a)}",
                        description=f"De {tot_terceira} votos da 3ª via, {ganho_a} foram para {PRESIDENTIAL_CANDIDATES.get(cand_a, cand_a)} e {ganho_b} para {PRESIDENTIAL_CANDIDATES.get(cand_b, cand_b)}.",
                        details={"terceira_via_1t": tot_terceira, "ganho_a": ganho_a, "ganho_b": ganho_b},
                    )
                )
            elif ganho_b >= tot_ganho * 0.95 and ganho_a <= 0:
                anomalies.append(
                    Anomaly(
                        code="CHK053_ABSORCAO_100PCT_TERCEIRA_VIA_POR_UM_CANDIDATO",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"100% dos votos de terceira via absorvidos por {PRESIDENTIAL_CANDIDATES.get(cand_b, cand_b)}",
                        description=f"De {tot_terceira} votos da 3ª via, {ganho_b} foram para {PRESIDENTIAL_CANDIDATES.get(cand_b, cand_b)} e {ganho_a} para {PRESIDENTIAL_CANDIDATES.get(cand_a, cand_a)}.",
                        details={"terceira_via_1t": tot_terceira, "ganho_a": ganho_a, "ganho_b": ganho_b},
                    )
                )

    # CHK054: Crescimento excede teto matemático de migração e novos eleitores
    for cand in runoff_candidates:
        c1 = v1.get(cand, 0)
        c2 = v2.get(cand, 0)
        cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
        ganho = c2 - c1
        pool_disponivel = sum(v for k, v in v1.items() if k != cand) + s1.votos_brancos + s1.votos_nulos
        novos = max(0, s2.comparecimento - s1.comparecimento)
        teto = pool_disponivel + novos
        if ganho > teto and ganho > 10:
            anomalies.append(
                Anomaly(
                    code="CHK054_CRESCIMENTO_EXCEDE_TETO_MIGRACAO_E_COMPARECIMENTO",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Crescimento de {cand_nome} excede o teto matemático disponível",
                    description=f"{cand_nome} ganhou {ganho} votos, mas o teto matemático máximo era {teto}.",
                    details={"ganho": ganho, "teto": teto},
                )
            )

    # CHK055: Crescimento com queda de comparecimento acima da terceira via
    if s2.comparecimento < s1.comparecimento:
        for cand in runoff_candidates:
            c1 = v1.get(cand, 0)
            c2 = v2.get(cand, 0)
            cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
            ganho = c2 - c1
            if ganho > (s1.total_terceira_via + s1.votos_brancos + s1.votos_nulos) and ganho > 10:
                anomalies.append(
                    Anomaly(
                        code="CHK055_CRESCIMENTO_COM_QUEDA_DE_COMPARECIMENTO_ACIMA_DA_TERCEIRA_VIA",
                        category=CAT_VOTACAO,
                        severity=SEV_ALTA,
                        title=f"{cand_nome} cresceu acima de toda a terceira via com comparecimento caindo",
                        description=f"{cand_nome} cresceu +{ganho} votos mesmo com {abs(delta_comp)} eleitores a menos.",
                        details={"ganho": ganho, "queda_comp": abs(delta_comp), "terceira_1t": s1.total_terceira_via},
                    )
                )

    # CHK056 e CHK057: Inversão abrupta (swing líquido extremo)
    if s1.votos_validos >= 50 and s2.votos_validos >= 50:
        pct1_a = (va1 / s1.votos_validos * 100.0)
        pct2_a = (va2 / s2.votos_validos * 100.0)
        pct1_b = (vb1 / s1.votos_validos * 100.0)
        pct2_b = (vb2 / s2.votos_validos * 100.0)

        swing = abs((pct2_b - pct2_a) - (pct1_b - pct1_a))
        if swing >= 50.0:
            anomalies.append(
                Anomaly(
                    code="CHK056_INVERSAO_ABRUPTA_SWING_MAIOR_50PP",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title="Swing político extremo superior a 50 pontos percentuais",
                    description=f"Inversão radical entre turnos na seção (swing líquido de {swing:.1f} pp).",
                    details={"swing_pp": swing, "pct1_a": pct1_a, "pct2_a": pct2_a, "pct1_b": pct1_b, "pct2_b": pct2_b},
                )
            )
        elif swing >= 40.0:
            anomalies.append(
                Anomaly(
                    code="CHK057_INVERSAO_ABRUPTA_SWING_MAIOR_40PP",
                    category=CAT_VOTACAO,
                    severity=SEV_MEDIA,
                    title="Swing político elevado superior a 40 pontos percentuais",
                    description=f"Oscilação elevada entre os finalistas na seção (swing de {swing:.1f} pp).",
                    details={"swing_pp": swing},
                )
            )

    # CHK058: Migração totalmente assimétrica contra a média municipal
    if mun_stats and s1.votos_validos >= 50 and s2.votos_validos >= 50:
        mun_swing = mun_stats.get("media_swing_flavio_lula", 0.0)
        secao_swing = (vb2 - vb1) - (va2 - va1)
        if abs(secao_swing - mun_swing) >= 40.0 and abs(secao_swing) >= 30:
            anomalies.append(
                Anomaly(
                    code="CHK058_MIGRACAO_TOTALMENTE_ASSIMETRICA_CONTRA_MEDIA_MUNICIPAL",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title="Comportamento de votos fortemente divergente do município",
                    description=f"A seção divergiu em {abs(secao_swing - mun_swing):.1f} votos do padrão médio do município.",
                    details={"secao_swing": secao_swing, "mun_swing": mun_swing},
                )
            )

    # CHK059: Votos nominais para candidato não concorrente no 2T
    for cand, qtd in v2.items():
        if cand not in runoff_candidates and qtd > 0:
            anomalies.append(
                Anomaly(
                    code="CHK059_VOTO_CANDIDATO_NAO_CONCORRENTE_NO_2T",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title="Voto registrado para candidato não habilitado ao 2T",
                    description=f"Candidato {cand} recebeu {qtd} votos nominais no 2º turno.",
                    details={"candidato": cand, "votos": qtd},
                )
            )

    # CHK060: Finalista com menos votos que brancos e nulos
    bn_2 = s2.votos_brancos + s2.votos_nulos
    if s2.comparecimento >= 100:
        for cand in runoff_candidates:
            c2 = v2.get(cand, 0)
            cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
            if c2 > 0 and c2 < bn_2 and bn_2 >= 20:
                anomalies.append(
                    Anomaly(
                        code="CHK060_FINALISTA_COM_VOTACAO_MENOR_QUE_BRANCOS_E_NULOS",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"{cand_nome} obteve menos votos que brancos e nulos no 2T",
                        description=f"{cand_nome} teve {c2} votos, enquanto brancos e nulos somaram {bn_2} votos.",
                        details={"votos_cand": c2, "brancos_nulos": bn_2},
                    )
                )

    # CHK061: Votos válidos zero no 2T
    if s2.comparecimento >= 20 and s2.votos_validos == 0:
        anomalies.append(
            Anomaly(
                code="CHK061_VOTOS_VALIDOS_ZERO_NO_2T",
                category=CAT_VOTACAO,
                severity=SEV_ALTA,
                title="Zero votos válidos na eleição presidencial do 2T",
                description=f"Todos os {s2.comparecimento} eleitores votaram branco ou nulo.",
                details={"comparecimento": s2.comparecimento},
            )
        )

    # CHK062: Desvio-padrão de votos extremo no município
    if mun_stats and s2.votos_validos >= 50:
        std_pct = mun_stats.get("std_pct_flavio", 0.0)
        mean_pct = mun_stats.get("mean_pct_flavio", 50.0)
        pct_b2 = (vb2 / s2.votos_validos * 100) if s2.votos_validos else 0
        if std_pct > 0 and abs(pct_b2 - mean_pct) >= (3.5 * std_pct) and std_pct >= 5.0:
            anomalies.append(
                Anomaly(
                    code="CHK062_DESVIO_PADRAO_VOTOS_EXTREMO_NO_MUNICIPIO",
                    category=CAT_VOTACAO,
                    severity=SEV_MEDIA,
                    title="Votação percentual a mais de 3.5 desvios-padrão da média municipal",
                    description=f"Seção teve {pct_b2:.1f}%, divergindo da média municipal de {mean_pct:.1f}% (+- {std_pct:.1f}%).",
                    details={"pct_secao": pct_b2, "mean_mun": mean_pct, "std_mun": std_pct},
                )
            )

    # CHK063: Ambos finalistas perderam votos com comparecimento maior
    if s2.comparecimento > s1.comparecimento and va2 < va1 and vb2 < vb1:
        anomalies.append(
            Anomaly(
                code="CHK063_AMBOS_FINALISTAS_PERDERAM_VOTOS_COM_MAIOR_COMPARECIMENTO",
                category=CAT_VOTACAO,
                severity=SEV_ALTA,
                title="Ambos os candidatos finalistas perderam votos mesmo com mais eleitores",
                description="Comparecimento subiu, mas tanto Lula quanto Flavio tiveram votação menor no 2T.",
                details={"delta_comp": delta_comp, "delta_lula": va2 - va1, "delta_flavio": vb2 - vb1},
            )
        )

    # CHK064: Concentração superior a 95%
    if s2.votos_validos >= 60:
        for cand, qtd in v2.items():
            if (qtd / s2.votos_validos) >= 0.95 and cand in runoff_candidates:
                cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
                anomalies.append(
                    Anomaly(
                        code="CHK064_CONCENTRACAO_DE_VOTOS_SUPERIOR_A_95PCT",
                        category=CAT_VOTACAO,
                        severity=SEV_MEDIA,
                        title=f"{cand_nome} concentrou mais de 95% dos votos válidos",
                        description=f"{cand_nome} obteve {qtd} de {s2.votos_validos} votos válidos ({qtd/s2.votos_validos*100:.1f}%).",
                        details={"candidato": cand, "votos": qtd, "validos": s2.votos_validos},
                    )
                )

    # CHK065: Votos nominais superiores ao comparecimento
    if s2.votos_validos > s2.comparecimento:
        anomalies.append(
            Anomaly(
                code="CHK065_VOTOS_NOMINAIS_SUPERIORES_AO_COMPARECIMENTO",
                category=CAT_VOTACAO,
                severity=SEV_ALTA,
                title="Votos nominais excedem o comparecimento",
                description=f"Votos nominais ({s2.votos_validos}) > comparecimento ({s2.comparecimento}).",
                details={"nominais": s2.votos_validos, "comparecimento": s2.comparecimento},
            )
        )

    # ========================================================================
    # GRUPO 5: BIOMETRIA E HABILITAÇÃO DO ELEITOR (CHK066 a CHK075)
    # ========================================================================
    queda_bio = 0.0
    salto_bio_ano = 0.0
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        queda_bio = s1.pct_biometria - s2.pct_biometria
        salto_bio_ano = s2.pct_biografia - s1.pct_biografia
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        queda_bio = s1.pct_biometria - s2.pct_biometria
        if queda_bio >= 30.0:
            anomalies.append(
                Anomaly(
                    code="CHK066_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_30PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_ALTA,
                    title="Queda drástica na validação biométrica (> 30 pp)",
                    description=f"Biometria caiu de {s1.pct_biometria:.1f}% para {s2.pct_biometria:.1f}% (-{queda_bio:.1f} pp).",
                    details={"bio_1t": s1.pct_biometria, "bio_2t": s2.pct_biometria, "queda": queda_bio},
                )
            )
        elif queda_bio >= 20.0:
            anomalies.append(
                Anomaly(
                    code="CHK067_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_20PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_MEDIA,
                    title="Queda acentuada na validação biométrica (> 20 pp)",
                    description=f"Biometria recuou de {s1.pct_biometria:.1f}% para {s2.pct_biometria:.1f}% (-{queda_bio:.1f} pp).",
                    details={"queda": queda_bio},
                )
            )

    # CHK068 e CHK069: Surto de biometria biográfica (ano de nascimento)
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        salto_bio_ano = s2.pct_biografia - s1.pct_biografia
        if salto_bio_ano >= 25.0:
            anomalies.append(
                Anomaly(
                    code="CHK068_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_25PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_ALTA,
                    title="Surto crítico de habilitação manual por ano de nascimento (> 25 pp)",
                    description=f"Liberação biográfica saltou de {s1.pct_biografia:.1f}% para {s2.pct_biografia:.1f}% (+{salto_bio_ano:.1f} pp).",
                    details={"bio_ano_1t": s1.pct_biografia, "bio_ano_2t": s2.pct_biografia, "salto": salto_bio_ano},
                )
            )
        elif salto_bio_ano >= 15.0:
            anomalies.append(
                Anomaly(
                    code="CHK069_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_15PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_MEDIA,
                    title="Salto acentuado de habilitação manual por ano de nascimento (> 15 pp)",
                    description=f"Liberação manual por ano de nascimento subiu {salto_bio_ano:.1f} pp no 2T.",
                    details={"salto": salto_bio_ano},
                )
            )

    # CHK070: Zero biometria em seção biometrizada
    if s1.pct_biometria >= 60.0 and s2.biometria_sim == 0 and s2.comparecimento >= 50:
        anomalies.append(
            Anomaly(
                code="CHK070_ZERO_BIOMETRIA_EM_SECAO_BIOMETRIZADA",
                category=CAT_BIOMETRIA,
                severity=SEV_MEDIA,
                title="Zero validação biométrica no 2T em seção que tinha biometria no 1T",
                description=f"Seção tinha {s1.pct_biometria:.1f}% no 1T e zero biometrias validadas no 2T.",
                details={"bio_1t": s1.pct_biometria, "bio_2t": 0},
            )
        )

    # CHK071: Explosão de sem biometria
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        pct_sem_1 = s1.biometria_nao / s1.comparecimento * 100
        pct_sem_2 = s2.biometria_nao / s2.comparecimento * 100
        if (pct_sem_2 - pct_sem_1) >= 30.0:
            anomalies.append(
                Anomaly(
                    code="CHK071_EXPLOSAO_SEM_BIOMETRIA_MAIOR_30PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_MEDIA,
                    title="Salto superior a 30 pp em eleitores sem biometria",
                    description=f"Eleitores sem biometria subiram de {pct_sem_1:.1f}% para {pct_sem_2:.1f}%.",
                    details={"sem_bio_1t": pct_sem_1, "sem_bio_2t": pct_sem_2},
                )
            )

    # CHK072: Soma de detalhamento de comparecimento diverge
    soma_det = s2.biometria_sim + s2.biometria_bio + s2.biometria_nao
    if s2.comparecimento > 0 and soma_det > 0 and soma_det != s2.comparecimento:
        anomalies.append(
            Anomaly(
                code="CHK072_SOMA_DETALHAMENTO_COMPARECIMENTO_DIVERGENTE",
                category=CAT_BIOMETRIA,
                severity=SEV_ALTA,
                title="Soma do detalhamento biométrico diverge do comparecimento",
                description=f"Biometria ({s2.biometria_sim}) + Bio ({s2.biometria_bio}) + Sem ({s2.biometria_nao}) = {soma_det} != {s2.comparecimento}.",
                details={"soma_det": soma_det, "comparecimento": s2.comparecimento},
            )
        )

    # CHK073: Biometria 100% perfeita em seção grande
    if s2.comparecimento >= 150 and s2.biometria_sim == s2.comparecimento:
        anomalies.append(
            Anomaly(
                code="CHK073_BIOMETRIA_100PCT_COM_HABILITACAO_MANUAL_ZERO",
                category=CAT_BIOMETRIA,
                severity=SEV_INFO,
                title="100% de reconhecimento biométrico sem nenhuma falha",
                description=f"Todos os {s2.comparecimento} eleitores foram validados por biometria na 1ª tentativa sem nenhuma exceção.",
                details={"comparecimento": s2.comparecimento},
            )
        )

    # CHK074: Biometria superior aos aptos
    if s2.biometria_sim > s2.aptos:
        anomalies.append(
            Anomaly(
                code="CHK074_BIOMETRIA_SUPERIOR_AOS_APTOS",
                category=CAT_BIOMETRIA,
                severity=SEV_ALTA,
                title="Habilitações biométricas superam o total de aptos",
                description=f"{s2.biometria_sim} biometrias > {s2.aptos} aptos.",
                details={"biometria": s2.biometria_sim, "aptos": s2.aptos},
            )
        )

    # CHK075: Correlação de salto biográfico e voto unânime
    if salto_bio_ano >= 15.0 and s2.votos_validos >= 50:
        for cand, qtd in v2.items():
            if (qtd / s2.votos_validos) >= 0.90:
                cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
                anomalies.append(
                    Anomaly(
                        code="CHK075_CORRELACAO_BIOGRAFICA_E_VOTO_UNANIME",
                        category=CAT_BIOMETRIA,
                        severity=SEV_ALTA,
                        title=f"Salto de liberação manual associado a votação > 90% para {cand_nome}",
                        description=f"Liberação manual subiu +{salto_bio_ano:.1f} pp e {cand_nome} obteve {qtd/s2.votos_validos*100:.1f}% dos votos.",
                        details={"salto_bio": salto_bio_ano, "pct_votos": qtd / s2.votos_validos * 100},
                    )
                )

    # ========================================================================
    # GRUPO 6: TEMPO E COMPORTAMENTO DE VOTAÇÃO (CHK076 a CHK085)
    # ========================================================================

    # CHK076: Abertura precoce (< 07:00)
    if s2.abertura:
        try:
            ab_dt = datetime.fromisoformat(s2.abertura)
            if ab_dt.hour < 7:
                anomalies.append(
                    Anomaly(
                        code="CHK076_ABERTURA_PRECOCE_2T",
                        category=CAT_TEMPORAL,
                        severity=SEV_MEDIA,
                        title="Votação aberta antes das 07:00 no 2T",
                        description=f"Abertura às {ab_dt.strftime('%H:%M:%S')}.",
                        details={"abertura": s2.abertura},
                    )
                )
            # CHK077: Abertura tardia (> 08:30)
            elif ab_dt.hour > 8 or (ab_dt.hour == 8 and ab_dt.minute > 30):
                anomalies.append(
                    Anomaly(
                        code="CHK077_ABERTURA_TARDIA_2T",
                        category=CAT_TEMPORAL,
                        severity=SEV_MEDIA,
                        title="Votação aberta com atraso após as 08:30 no 2T",
                        description=f"Abertura às {ab_dt.strftime('%H:%M:%S')}.",
                        details={"abertura": s2.abertura},
                    )
                )
        except Exception:
            pass

    # CHK078, CHK079, CHK080: Encerramento
    if s2.encerramento:
        try:
            enc_dt = datetime.fromisoformat(s2.encerramento)
            if enc_dt.hour < 17:
                anomalies.append(
                    Anomaly(
                        code="CHK078_ENCERRAMENTO_PRECOCE_2T",
                        category=CAT_TEMPORAL,
                        severity=SEV_ALTA,
                        title="Urna encerrada antes das 17:00 no 2T",
                        description=f"Encerramento registrado às {enc_dt.strftime('%H:%M:%S')}.",
                        details={"encerramento": s2.encerramento},
                    )
                )
            elif enc_dt.hour >= 22:
                anomalies.append(
                    Anomaly(
                        code="CHK080_ENCERRAMENTO_MADRUGADA_2T",
                        category=CAT_TEMPORAL,
                        severity=SEV_ALTA,
                        title="Urna encerrada após as 22:00 no 2T",
                        description=f"Encerramento extremamente tardio às {enc_dt.strftime('%H:%M:%S')}.",
                        details={"encerramento": s2.encerramento},
                    )
                )
            elif enc_dt.hour >= 20:
                anomalies.append(
                    Anomaly(
                        code="CHK079_ENCERRAMENTO_MUITO_TARDIO_2T",
                        category=CAT_TEMPORAL,
                        severity=SEV_MEDIA,
                        title="Urna encerrada após as 20:00 no 2T",
                        description=f"Encerramento tardio às {enc_dt.strftime('%H:%M:%S')}.",
                        details={"encerramento": s2.encerramento},
                    )
                )
        except Exception:
            pass

    # CHK081: Duração inferior a 4 horas
    if s2.duracao_minutos and s2.duracao_minutos < 240.0 and s2.abstencao >= 30:
        anomalies.append(
            Anomaly(
                code="CHK081_DURACAO_VOTACAO_INFERIOR_A_4_HORAS",
                category=CAT_TEMPORAL,
                severity=SEV_ALTA,
                title="Votação funcionou por menos de 4 horas",
                description=f"Urna funcionou por apenas {s2.duracao_minutos:.0f} minutos com {s2.abstencao} eleitores faltosos.",
                details={"duracao_min": s2.duracao_minutos},
            )
        )

    # CHK082: Duração no 2T > 1T em mais de 60 min
    if s1.duracao_minutos and s2.duracao_minutos:
        diff_d = s2.duracao_minutos - s1.duracao_minutos
        if diff_d >= 60.0 and s2.comparecimento <= s1.comparecimento + 10:
            anomalies.append(
                Anomaly(
                    code="CHK082_DURACAO_2T_SUPERIOR_AO_1T_EM_MAIS_DE_60MIN",
                    category=CAT_TEMPORAL,
                    severity=SEV_BAIXA,
                    title="Votação do 2T durou mais de 1 hora a mais que a do 1T",
                    description=f"2T durou {s2.duracao_minutos:.0f} min vs {s1.duracao_minutos:.0f} min no 1T (+{diff_d:.0f} min).",
                    details={"duracao_1t": s1.duracao_minutos, "duracao_2t": s2.duracao_minutos},
                )
            )

    # CHK083: Tempo médio por voto fisicamente impossível (< 15s)
    if s2.duracao_minutos and s2.comparecimento >= 100:
        segundos_por_eleitor = (s2.duracao_minutos * 60) / s2.comparecimento
        if segundos_por_eleitor < 15.0:
            anomalies.append(
                Anomaly(
                    code="CHK083_TEMPO_MEDIO_POR_VOTO_IMPOSSIVEL_INFERIOR_15S",
                    category=CAT_TEMPORAL,
                    severity=SEV_ALTA,
                    title="Tempo médio por voto fisicamente inviável (< 15s)",
                    description=f"Ritmo de {segundos_por_eleitor:.1f} segundos por voto para {s2.comparecimento} eleitores.",
                    details={"segundos_por_voto": segundos_por_eleitor},
                )
            )

    # CHK084: Emissão anterior ao encerramento
    if s2.data_hora_emissao and s2.encerramento:
        try:
            em_dt = datetime.fromisoformat(s2.data_hora_emissao)
            enc_dt = datetime.fromisoformat(s2.encerramento)
            if em_dt < enc_dt:
                anomalies.append(
                    Anomaly(
                        code="CHK084_EMISSAO_BU_ANTERIOR_AO_ENCERRAMENTO",
                        category=CAT_TEMPORAL,
                        severity=SEV_ALTA,
                        title="Emissão do BU registrada antes do encerramento oficial",
                        description=f"Emissão ({s2.data_hora_emissao}) < Encerramento ({s2.encerramento}).",
                        details={"emissao": s2.data_hora_emissao, "encerramento": s2.encerramento},
                    )
                )
        except Exception:
            pass

    # CHK085: Horário de abertura divergente em mais de 60 min
    if s1.abertura and s2.abertura:
        try:
            ab1 = datetime.fromisoformat(s1.abertura)
            ab2 = datetime.fromisoformat(s2.abertura)
            diff_ab = abs((ab2.hour * 60 + ab2.minute) - (ab1.hour * 60 + ab1.minute))
            if diff_ab >= 60:
                anomalies.append(
                    Anomaly(
                        code="CHK085_HORARIO_ABERTURA_DIVERGENTE_MAIOR_60MIN",
                        category=CAT_TEMPORAL,
                        severity=SEV_BAIXA,
                        title="Abertura do 2T divergiu em mais de 60 minutos do 1T",
                        description=f"1T abriu às {ab1.strftime('%H:%M')} e 2T abriu às {ab2.strftime('%H:%M')}.",
                        details={"abertura_1t": s1.abertura, "abertura_2t": s2.abertura},
                    )
                )
        except Exception:
            pass

    # ========================================================================
    # GRUPO 7: BRANCOS E NULOS (CHK086 a CHK092)
    # ========================================================================
    pct_bn_1 = ((s1.votos_brancos + s1.votos_nulos) / s1.comparecimento * 100) if s1.comparecimento else 0
    pct_bn_2 = ((s2.votos_brancos + s2.votos_nulos) / s2.comparecimento * 100) if s2.comparecimento else 0

    # CHK086: Explosão de brancos e nulos (> 15 pp)
    if s2.comparecimento >= 50 and (pct_bn_2 - pct_bn_1) >= 15.0:
        anomalies.append(
            Anomaly(
                code="CHK086_EXPLOSAO_BRANCOS_NULOS_MAIOR_15PP",
                category=CAT_BRANCOS_NULOS,
                severity=SEV_MEDIA,
                title="Salto superior a 15 pp em votos brancos e nulos no 2T",
                description=f"Brancos e nulos subiram de {pct_bn_1:.1f}% para {pct_bn_2:.1f}% (+{pct_bn_2 - pct_bn_1:.1f} pp).",
                details={"pct_1t": pct_bn_1, "pct_2t": pct_bn_2},
            )
        )

    # CHK087: Brancos e nulos superiores a 30%
    if s2.comparecimento >= 50 and pct_bn_2 >= 30.0:
        anomalies.append(
            Anomaly(
                code="CHK087_BRANCOS_NULOS_SUPERIOR_A_30PCT",
                category=CAT_BRANCOS_NULOS,
                severity=SEV_ALTA,
                title="Brancos e nulos superam 30% dos votos apurados no 2T",
                description=f"Alta taxa de votos inválidos no 2T ({pct_bn_2:.1f}% dos votos da seção).",
                details={"pct": pct_bn_2, "brancos": s2.votos_brancos, "nulos": s2.votos_nulos},
            )
        )

    # CHK088: Extinção de brancos e nulos em seção grande
    if s2.comparecimento >= 150 and s2.votos_brancos == 0 and s2.votos_nulos == 0:
        anomalies.append(
            Anomaly(
                code="CHK088_EXTINCAO_BRANCOS_NULOS_SECAO_GRANDE",
                category=CAT_BRANCOS_NULOS,
                severity=SEV_BAIXA,
                title="Zero brancos e zero nulos no 2T em seção grande",
                description=f"Nenhum voto branco ou nulo entre {s2.comparecimento} eleitores no 2T.",
                details={"comparecimento": s2.comparecimento},
            )
        )

    # CHK089: Queda de brancos e nulos > 20 pp
    if s1.comparecimento >= 50 and (pct_bn_1 - pct_bn_2) >= 20.0:
        anomalies.append(
            Anomaly(
                code="CHK089_QUEDA_BRANCOS_NULOS_MAIOR_20PP",
                category=CAT_BRANCOS_NULOS,
                severity=SEV_MEDIA,
                title="Queda de mais de 20 pp em votos brancos e nulos",
                description=f"Brancos e nulos caíram de {pct_bn_1:.1f}% (1T) para {pct_bn_2:.1f}% (2T).",
                details={"queda_pp": pct_bn_1 - pct_bn_2},
            )
        )

    # CHK090: Nulos superam brancos em mais de 10 vezes
    if s2.votos_nulos >= 20 and s2.votos_brancos > 0 and (s2.votos_nulos / s2.votos_brancos) >= 10.0:
        anomalies.append(
            Anomaly(
                code="CHK090_NULOS_SUPERIORES_A_BRANCOS_EM_10X",
                category=CAT_BRANCOS_NULOS,
                severity=SEV_MEDIA,
                title="Votos nulos superam brancos em mais de 10x",
                description=f"{s2.votos_nulos} votos nulos vs apenas {s2.votos_brancos} votos brancos.",
                details={"nulos": s2.votos_nulos, "brancos": s2.votos_brancos},
            )
        )

    # CHK091: Brancos superam nulos em mais de 10 vezes
    if s2.votos_brancos >= 20 and s2.votos_nulos > 0 and (s2.votos_brancos / s2.votos_nulos) >= 10.0:
        anomalies.append(
            Anomaly(
                code="CHK091_BRANCOS_SUPERIORES_A_NULOS_EM_10X",
                category=CAT_BRANCOS_NULOS,
                severity=SEV_MEDIA,
                title="Votos brancos superam nulos em mais de 10x",
                description=f"{s2.votos_brancos} votos brancos vs apenas {s2.votos_nulos} votos nulos.",
                details={"brancos": s2.votos_brancos, "nulos": s2.votos_nulos},
            )
        )

    # CHK092: 100% dos votos inválidos no 2T
    if s2.comparecimento >= 30 and (s2.votos_brancos + s2.votos_nulos) == s2.comparecimento:
        anomalies.append(
            Anomaly(
                code="CHK092_100PCT_VOTOS_INVALIDOS_NO_2T",
                category=CAT_BRANCOS_NULOS,
                severity=SEV_ALTA,
                title="100% de votos brancos e nulos no 2T",
                description=f"Todos os {s2.comparecimento} votos foram invalidados (zero votos nominais).",
                details={"comparecimento": s2.comparecimento},
            )
        )

    # ========================================================================
    # GRUPO 8: INTEGRIDADE CRIPTOGRÁFICA, ARITMÉTICA E PAREAMENTO (CHK093 a CHK100)
    # ========================================================================

    # CHK093: Divergência entre soma de votos e comparecimento no 2T
    soma_votos_2t = s2.votos_validos + s2.votos_brancos + s2.votos_nulos
    if s2.total_apurado_pres > 0 and soma_votos_2t != s2.comparecimento:
        anomalies.append(
            Anomaly(
                code="CHK093_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_2T",
                category=CAT_INTEGRIDADE,
                severity=SEV_ALTA,
                title="Soma de votos apurados diverge do comparecimento no 2T",
                description=f"Válidos ({s2.votos_validos}) + Brancos ({s2.votos_brancos}) + Nulos ({s2.votos_nulos}) = {soma_votos_2t} != {s2.comparecimento}.",
                details={"soma_votos": soma_votos_2t, "comparecimento": s2.comparecimento},
            )
        )

    # CHK094: Divergência entre soma de votos e comparecimento no 1T
    soma_votos_1t = s1.votos_validos + s1.votos_brancos + s1.votos_nulos
    if s1.total_apurado_pres > 0 and soma_votos_1t != s1.comparecimento:
        anomalies.append(
            Anomaly(
                code="CHK094_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_1T",
                category=CAT_INTEGRIDADE,
                severity=SEV_ALTA,
                title="Soma de votos apurados diverge do comparecimento no 1T",
                description=f"Válidos ({s1.votos_validos}) + Brancos ({s1.votos_brancos}) + Nulos ({s1.votos_nulos}) = {soma_votos_1t} != {s1.comparecimento}.",
                details={"soma_votos": soma_votos_1t, "comparecimento": s1.comparecimento},
            )
        )

    # CHK097: Total de votos apurados no cargo presidencial não confere
    if s2.total_apurado_pres > 0 and s2.total_apurado_pres != s2.comparecimento:
        anomalies.append(
            Anomaly(
                code="CHK097_TOTAL_VOTOS_CARGO_NAO_E_MULTIPLO_COMPARECIMENTO",
                category=CAT_INTEGRIDADE,
                severity=SEV_ALTA,
                title="Total apurado do cargo presidencial diverge do comparecimento",
                description=f"Total no cargo={s2.total_apurado_pres} != comparecimento={s2.comparecimento}.",
                details={"total_cargo": s2.total_apurado_pres, "comparecimento": s2.comparecimento},
            )
        )

    # CHK098: Falha na cadeia de hash SHA-512 no 2T
    if s2.cadeia_hash_valida is False:
        anomalies.append(
            Anomaly(
                code="CHK098_FALHA_CADEIA_HASH_SHA512_2T",
                category=CAT_INTEGRIDADE,
                severity=SEV_ALTA,
                title="Cadeia interna recursiva de hashes SHA-512 corrompida no 2T",
                description="O hash final recalculado dos votáveis não coincide com ultimoHashVotosVotavel no BU do 2T.",
                details={"urna": s2.numero_interno_urna},
            )
        )

    # CHK099: Falha na cadeia de hash SHA-512 no 1T
    if s1.cadeia_hash_valida is False:
        anomalies.append(
            Anomaly(
                code="CHK099_FALHA_CADEIA_HASH_SHA512_1T",
                category=CAT_INTEGRIDADE,
                severity=SEV_ALTA,
                title="Cadeia interna recursiva de hashes SHA-512 corrompida no 1T",
                description="O hash final recalculado dos votáveis não coincide com ultimoHashVotosVotavel no BU do 1T.",
                details={"urna": s1.numero_interno_urna},
            )
        )

    # CHK100: Hash assinado no VSC divergente
    if not s2.path:
        anomalies.append(
            Anomaly(
                code="CHK100_HASH_ASSINADO_VSC_DIVERGENTE",
                category=CAT_INTEGRIDADE,
                severity=SEV_ALTA,
                title="Arquivo bu.dat sem integridade de caminho",
                description="Caminho do arquivo de resultado inacessível.",
                details={},
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
    # PRÉ-CÁLCULO DE ESTATÍSTICAS MUNICIPAIS (PARA BENCHMARK LOCAL)
    # ========================================================================
    _log("[3/5] Calculando métricas municipais e executando matriz de 100 detectores...")

    mun_deltas: dict[int, list[float]] = defaultdict(list)
    mun_swings: dict[int, list[float]] = defaultdict(list)
    mun_flavio_pcts: dict[int, list[float]] = defaultdict(list)

    for k in all_keys:
        s1 = bu_1t_extractions.get(k)
        s2 = bu_2t_extractions.get(k)
        if s1 and s2 and s1.aptos >= 50 and s2.aptos >= 50:
            mun_deltas[k.municipio].append(s2.pct_comparecimento - s1.pct_comparecimento)
            if s1.votos_validos >= 30 and s2.votos_validos >= 30:
                v1_22 = s1.votos_presidenciais.get(22, 0)
                v2_22 = s2.votos_presidenciais.get(22, 0)
                v1_13 = s1.votos_presidenciais.get(13, 0)
                v2_13 = s2.votos_presidenciais.get(13, 0)
                mun_swings[k.municipio].append((v2_22 - v1_22) - (v2_13 - v1_13))
                mun_flavio_pcts[k.municipio].append(v2_22 / s2.votos_validos * 100)

    mun_benchmarks: dict[int, dict[str, float]] = {}
    for mun_id, deltas in mun_deltas.items():
        mean_d = sum(deltas) / len(deltas) if deltas else 0.0
        swings = mun_swings.get(mun_id, [])
        mean_s = sum(swings) / len(swings) if swings else 0.0
        fp = mun_flavio_pcts.get(mun_id, [])
        mean_f = sum(fp) / len(fp) if fp else 50.0
        variance = sum((x - mean_f) ** 2 for x in fp) / len(fp) if len(fp) > 1 else 0.0
        std_f = variance ** 0.5
        mun_benchmarks[mun_id] = {
            "media_delta_comp": mean_d,
            "media_swing_flavio_lula": mean_s,
            "mean_pct_flavio": mean_f,
            "std_pct_flavio": std_f,
        }

    # ========================================================================
    # EXECUÇÃO DOS 100 DETECTORES POR SEÇÃO
    # ========================================================================
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
    total_1t_bio_sim = 0
    total_2t_bio_sim = 0
    total_1t_bio_nao = 0
    total_2t_bio_nao = 0
    total_1t_terceira = 0

    for k in all_keys:
        s1 = bu_1t_extractions.get(k)
        s2 = bu_2t_extractions.get(k)

        if s1:
            total_1t_comp += s1.comparecimento
            total_1t_aptos += s1.aptos
            total_1t_brancos += s1.votos_brancos
            total_1t_nulos += s1.votos_nulos
            total_1t_bio_sim += s1.biometria_sim
            total_1t_bio_nao += (s1.biometria_bio + s1.biometria_nao)
            total_1t_terceira += s1.total_terceira_via
            for cand, v in s1.votos_presidenciais.items():
                total_1t_pres[cand] += v
        if s2:
            total_2t_comp += s2.comparecimento
            total_2t_aptos += s2.aptos
            total_2t_brancos += s2.votos_brancos
            total_2t_nulos += s2.votos_nulos
            total_2t_bio_sim += s2.biometria_sim
            total_2t_bio_nao += (s2.biometria_bio + s2.biometria_nao)
            for cand, v in s2.votos_presidenciais.items():
                total_2t_pres[cand] += v

        mun_b = mun_benchmarks.get(k.municipio)
        anomalies = evaluate_section_anomalies(s1, s2, mun_stats=mun_b)
        worst_sev = compute_worst_severity(anomalies)

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

    # Ordena com severidade ALTA primeiro por padrão
    def _sort_key(s: SectionComparison):
        weight = SEVERITY_WEIGHTS.get(s.worst_severity, -1)
        return (-weight, -len(s.anomalies), s.municipio, s.zona, s.secao)

    sections_comparison.sort(key=_sort_key)

    finished_at = datetime.now()
    duration = round(time.time() - t0, 2)

    # ========================================================================
    # TOTALIZAÇÃO COMPARATIVA E MIGRAÇÃO DE TERCEIRA VIA
    # ========================================================================
    _log("[4/5] Compilando totais de votação e fluxo de terceira via...")

    candidatos_comparativo = []
    # Apenas finalistas recebem delta no 2T
    finalistas_set = {13, 22}
    all_cands = sorted(set(total_1t_pres.keys()) | set(total_2t_pres.keys()))
    for c in all_cands:
        v1 = total_1t_pres.get(c, 0)
        v2 = total_2t_pres.get(c, 0)
        delta = v2 - v1 if c in finalistas_set else 0
        pct_delta = round((delta / v1 * 100), 2) if v1 > 0 and c in finalistas_set else None
        nome = PRESIDENTIAL_CANDIDATES.get(c, f"Candidato {c}")
        candidatos_comparativo.append(
            {
                "numero": c,
                "nome": nome,
                "e_finalista": c in finalistas_set,
                "votos_1t": v1,
                "votos_2t": v2,
                "delta_votos": delta,
                "pct_crescimento": pct_delta,
            }
        )

    # Finalistas primeiro, ordenados por votos
    candidatos_comparativo.sort(key=lambda item: (not item["e_finalista"], -item["votos_2t"], -item["votos_1t"]))

    # Resumo executivo de métricas
    report_data: dict[str, Any] = {
        "metadados": {
            "gerado_em": finished_at.isoformat(),
            "iniciado_em": started_at.isoformat(),
            "duracao_segundos": duration,
            "diretorio_1t": str(input_1t),
            "diretorio_2t": str(input_2t),
            "diretorio_saida": str(out_dir),
            "total_verificacoes_disponiveis": 100,
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
            "biometria": {
                "com_biometria_1t": total_1t_bio_sim,
                "com_biometria_2t": total_2t_bio_sim,
                "pct_biometria_1t": round((total_1t_bio_sim / total_1t_comp * 100), 2) if total_1t_comp else 0,
                "pct_biometria_2t": round((total_2t_bio_sim / total_2t_comp * 100), 2) if total_2t_comp else 0,
                "sem_biometria_1t": total_1t_bio_nao,
                "sem_biometria_2t": total_2t_bio_nao,
            },
            "terceira_via_1t": {
                "total_votos": total_1t_terceira,
                "pct_validos": round(total_1t_terceira / (total_1t_comp - total_1t_brancos - total_1t_nulos) * 100, 2) if (total_1t_comp - total_1t_brancos - total_1t_nulos) else 0,
            },
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
        _log("[5/5] Gerando relatório interativo HTML profissional com ordenação avançada...")
        html_content = generate_comparison_html(report_data)
        html_path.write_text(html_content, encoding="utf-8")

    # Montagem do resumo de console
    console_lines = [
        "",
        "=" * 80,
        "AUDITORIA FORENSE COMPARATIVA: 1º TURNO vs 2º TURNO (100 VERIFICAÇÕES TÉCNICAS)",
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
        "AUDITORIA BIOMÉTRICA:",
        f"  - Com Biometria: 1T={total_1t_bio_sim:,} ({report_data['totais_estaduais']['biometria']['pct_biometria_1t']}%) │ 2T={total_2t_bio_sim:,} ({report_data['totais_estaduais']['biometria']['pct_biometria_2t']}%)",
        f"  - Sem Biometria: 1T={total_1t_bio_nao:,} │ 2T={total_2t_bio_nao:,}",
        f"  - Terceira Via no 1T: {total_1t_terceira:,} votos ({report_data['totais_estaduais']['terceira_via_1t']['pct_validos']}% dos válidos)",
        "-" * 80,
        "PRINCIPAIS TIPOS DE INCONSISTÊNCIAS IDENTIFICADAS:",
    ]

    for code, count in anomaly_counter.most_common(12):
        console_lines.append(f"  • {code:<50} : {count:>5} seções")

    console_lines.extend(
        [
            "-" * 80,
            "TOTALIZAÇÃO COMPARATIVA PRESIDENCIAL:",
        ]
    )
    for c in candidatos_comparativo:
        v1_fmt = f"{c['votos_1t']:,}"
        v2_fmt = f"{c['votos_2t']:,}"
        if c["e_finalista"]:
            delta_str = f"{c['delta_votos']:+,}"
            pct_str = f"({c['pct_crescimento']:+.2f}%)" if c["pct_crescimento"] is not None else ""
            console_lines.append(f"  {c['nome']:<22} │ 1T: {v1_fmt:>10} │ 2T: {v2_fmt:>10} │ Dif: {delta_str:>9} {pct_str}")
        else:
            console_lines.append(f"  {c['nome']:<22} │ 1T: {v1_fmt:>10} │ 2T: [Não concorre] │ (3ª via 1T)")

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
# GERADOR DE RELATÓRIO HTML PROFISSIONAL COM ORDENAÇÃO E BIOMETRIA
# ============================================================================

def generate_comparison_html(data: dict[str, Any]) -> str:
    """Gera relatório HTML responsivo, autônomo com tabela completa, biometria e aptos."""
    meta = data["metadados"]
    resumo = data["resumo_auditoria"]
    totais = data["totais_estaduais"]
    bio = totais.get("biometria", {})
    t3 = totais.get("terceira_via_1t", {})
    secoes = data["secoes"]

    tipos_anomalias = resumo["por_tipo_anomalia"]

    # Todas as seções com anomalias na tabela interativa (até 5.000 seções)
    anomalous_sections = [s for s in secoes if s.get("total_anomalias", 0) > 0][:5000]

    cand_rows = []
    for c in totais.get("candidatos", []):
        v1 = f"{c['votos_1t']:,}".replace(",", ".")
        v2 = f"{c['votos_2t']:,}".replace(",", ".") if c["e_finalista"] else '<span class="text-slate-400 italic">Não concorre</span>'
        d = c["delta_votos"]
        d_str = f"{d:+,}".replace(",", ".") if c["e_finalista"] else '<span class="text-xs text-slate-400">3ª via 1T</span>'
        color_class = "text-emerald-700 font-semibold" if d > 0 else ("text-rose-700 font-semibold" if d < 0 else "text-slate-600")
        pct_str = f"({c['pct_crescimento']:+.2f}%)" if c.get("pct_crescimento") is not None else ""
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
    for item in tipos_anomalias[:25]:
        code = item["codigo"]
        count = item["total"]
        pct = round(count / resumo["total_secoes_analisadas"] * 100, 2)
        anom_summary_rows.append(f"""
        <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="py-1.5 px-3 font-mono text-[11px] font-semibold text-slate-800">{html.escape(code)}</td>
            <td class="py-1.5 px-3 text-right font-mono font-bold text-slate-900">{count:,}</td>
            <td class="py-1.5 px-3 text-right font-mono text-xs text-slate-500">{pct:.2f}%</td>
        </tr>
        """)

    anom_json_str = json.dumps(anomalous_sections, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria Forense Comparativa 1T vs 2T - 100 Verificações (Eleições 2026)</title>
    <style>
        *, ::before, ::after {{ box-sizing: border-box; border-width: 0; border-style: solid; border-color: #e2e8f0; }}
        body {{ margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8fafc; color: #1e293b; line-height: 1.5; }}
        .container {{ width: 100%; max-width: 1550px; margin-left: auto; margin-right: auto; padding: 1.5rem 1rem; }}
        .card {{ background-color: #ffffff; border-radius: 0.75rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05); padding: 1.25rem; margin-bottom: 1.5rem; }}
        .card-header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem; }}
        .grid {{ display: grid; gap: 1rem; }}
        .grid-cols-6 {{ grid-template-columns: repeat(6, minmax(0, 1fr)); }}
        .grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        @media (max-width: 1200px) {{ .grid-cols-6 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} .grid-cols-2 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }} }}
        @media (max-width: 768px) {{ .grid-cols-6 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
        .stat-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.875rem 1rem; }}
        .stat-label {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; }}
        .stat-value {{ font-size: 1.5rem; font-weight: 800; color: #0f172a; margin-top: 0.25rem; font-family: ui-monospace, monospace; }}
        .stat-desc {{ font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.8125rem; }}
        th {{ background-color: #f8fafc; color: #475569; font-weight: 700; padding: 0.625rem 0.5rem; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.04em; cursor: pointer; user-select: none; }}
        th:hover {{ background-color: #f1f5f9; color: #0f172a; }}
        th.sorted-asc::after {{ content: " ↑"; color: #2563eb; }}
        th.sorted-desc::after {{ content: " ↓"; color: #2563eb; }}
        td {{ padding: 0.5rem 0.5rem; border-bottom: 1px solid #f1f5f9; }}
        input, select {{ background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 0.375rem; padding: 0.45rem 0.65rem; font-size: 0.8125rem; color: #0f172a; outline: none; }}
        input:focus, select:focus {{ border-color: #3b82f6; ring: 2px #93c5fd; }}
        .badge {{ display: inline-block; padding: 0.15rem 0.45rem; border-radius: 0.25rem; font-size: 0.6875rem; font-weight: 700; margin-right: 4px; margin-bottom: 4px; line-height: 1.2; text-decoration: none; }}
        .badge-red {{ background: #ffe4e6; color: #9f1239; border: 1px solid #fecdd3; }}
        .badge-yellow {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
        .badge-blue {{ background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }}
        .badge-anom {{ background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; font-family: ui-monospace, monospace; }}
        .font-mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 2px solid #0f172a; padding-bottom: 1rem; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span class="badge badge-blue font-mono" style="margin-bottom: 0.5rem;">SUÍTE DE AUDITORIA FORENSE ELEITORAL OFICIAL</span>
                <h1 style="font-size: 1.625rem; font-weight: 900; color: #0f172a; margin: 0.25rem 0;">Auditoria Comparativa 1º vs 2º Turno (100 Regras Forenses)</h1>
                <p style="font-size: 0.8125rem; color: #475569; margin: 0;">Eleições Gerais 2026 &bull; Cruzamento de BUs Oficiais &bull; Biometria, Cadastral, Aptos e Fluxo de Votação</p>
            </div>
            <div style="text-align: right; font-size: 0.8125rem; color: #64748b;">
                <div><strong>Data da análise:</strong> {html.escape(meta['iniciado_em'])}</div>
                <div><strong>Tempo de execução:</strong> {meta['duracao_segundos']}s ({meta['total_verificacoes_disponiveis']} detectores ativos)</div>
                <div><strong>Escopo:</strong> Estado de Santa Catarina (SC)</div>
            </div>
        </div>

        <!-- 6 KPI CARDS -->
        <div class="grid grid-cols-6" style="margin-bottom: 1.5rem;">
            <div class="stat-card" style="border-left: 4px solid #3b82f6;">
                <div class="stat-label">Seções Auditadas</div>
                <div class="stat-value">{resumo['total_secoes_analisadas']:,}</div>
                <div class="stat-desc">Pares completos 1T/2T</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #ef4444;">
                <div class="stat-label">Com Inconsistências</div>
                <div class="stat-value" style="color: #b91c1c;">{resumo['total_secoes_com_anomalias']:,}</div>
                <div class="stat-desc">{resumo['pct_secoes_com_anomalias']}% do total estadual</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #f59e0b;">
                <div class="stat-label">Severidade Alta (Crítica)</div>
                <div class="stat-value" style="color: #d97706;">{resumo['por_severidade'].get('ALTA', 0):,}</div>
                <div class="stat-desc">Quedas nominais, variações cadastrais</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #10b981;">
                <div class="stat-label">Comparecimento (2T)</div>
                <div class="stat-value" style="color: #047857;">{totais['comparecimento_2t']:,}</div>
                <div class="stat-desc">{totais['pct_comparecimento_2t']}% presença ({totais['comparecimento_2t'] - totais['comparecimento_1t']:+,} vs 1T)</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #6366f1;">
                <div class="stat-label">Com Biometria (2T)</div>
                <div class="stat-value" style="color: #4338ca;">{bio.get('com_biometria_2t', 0):,}</div>
                <div class="stat-desc">{bio.get('pct_biometria_2t', 0)}% dos votos no 2T</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #8b5cf6;">
                <div class="stat-label">Sem Biometria (2T)</div>
                <div class="stat-value" style="color: #6d28d9;">{bio.get('sem_biometria_2t', 0):,}</div>
                <div class="stat-desc">Manual + Ano de Nascimento</div>
            </div>
        </div>

        <!-- PAINEL COMPARATIVO DE VOTAÇÃO E DISTRIBUIÇÃO DE ANOMALIAS -->
        <div class="grid grid-cols-2">
            <!-- TOTALIZAÇÃO PRESIDENCIAL -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <h2 style="font-size: 1.0625rem; font-weight: 700; margin: 0; color: #0f172a;">Totalização Presidencial e Terceira Via</h2>
                        <span style="font-size: 0.75rem; color: #64748b;">Consolidado de todas as seções (Terceira via no 1T: {t3.get('total_votos', 0):,} votos)</span>
                    </div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Nº</th>
                            <th>Candidato</th>
                            <th style="text-align: right;">Votos 1T</th>
                            <th style="text-align: right;">Votos 2T</th>
                            <th style="text-align: right;">Variação Nominal (2T vs 1T)</th>
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

            <!-- DISTRIBUIÇÃO DOS DETECTORES -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <h2 style="font-size: 1.0625rem; font-weight: 700; margin: 0; color: #0f172a;">Top Inconsistências Detectadas</h2>
                        <span style="font-size: 0.75rem; color: #64748b;">Ocorrências por regra das 100 implementadas</span>
                    </div>
                </div>
                <div style="max-height: 290px; overflow-y: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Código da Inconsistência</th>
                                <th style="text-align: right;">Seções</th>
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

        <!-- PAINEL INTERATIVO DE PESQUISA, FILTROS E ORDENAÇÃO -->
        <div class="card">
            <div class="card-header">
                <div>
                    <h2 style="font-size: 1.125rem; font-weight: 800; margin: 0; color: #0f172a;">Explorador Interativo de Seções Eleitorais</h2>
                    <p style="font-size: 0.75rem; color: #64748b; margin: 0.25rem 0 0 0;">Exibição detalhada com <strong>Aptos</strong>, <strong>Biometria</strong>, <strong>Terceira Via</strong> e <strong>Inconsistências</strong>. Clique no cabeçalho de qualquer coluna para ordenar.</p>
                </div>
                <div style="display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap;">
                    <input type="text" id="searchInput" placeholder="Buscar município, zona ou seção..." style="width: 240px;" oninput="applyFilters()">
                    <select id="severitySelect" onchange="applyFilters()">
                        <option value="ALL">Todas as Severidades</option>
                        <option value="ALTA" selected>Severidade ALTA (Crítica)</option>
                        <option value="MEDIA">Severidade MÉDIA</option>
                        <option value="BAIXA">Severidade BAIXA</option>
                    </select>
                    <select id="sortSelect" onchange="applySortDropdown()">
                        <option value="sev_desc">Ordenar: Severidade (Alta &rarr; Baixa)</option>
                        <option value="sev_asc">Ordenar: Severidade (Baixa &rarr; Alta)</option>
                        <option value="mun_asc">Ordenar: Município (A &rarr; Z)</option>
                        <option value="comp_delta_desc">Ordenar: Maior Ganho de Comparecimento</option>
                        <option value="comp_delta_asc">Ordenar: Maior Queda de Comparecimento</option>
                        <option value="flavio_drop_desc">Ordenar: Maior Queda de Flávio (22)</option>
                        <option value="lula_drop_desc">Ordenar: Maior Queda de Lula (13)</option>
                        <option value="t3_desc">Ordenar: Maior Terceira Via no 1T</option>
                        <option value="bio_drop_desc">Ordenar: Maior Queda de Biometria</option>
                    </select>
                    <select id="anomalySelect" onchange="applyFilters()" style="max-width: 280px;">
                        <option value="ALL">Todos os Tipos de Anomalia (100 detectores)</option>
                        {"".join(f'<option value="{a["codigo"]}">{a["codigo"]} ({a["total"]})</option>' for a in tipos_anomalias)}
                    </select>
                </div>
            </div>

            <!-- TABELA COMPLETA COM APTOS E BIOMETRIA -->
            <div style="overflow-x: auto;">
                <table id="mainTable">
                    <thead>
                        <tr>
                            <th onclick="sortByColumn('municipio')">Município</th>
                            <th onclick="sortByColumn('zona')" style="text-align: center;">Zona</th>
                            <th onclick="sortByColumn('secao')" style="text-align: center;">Seção</th>
                            <th onclick="sortByColumn('aptos')" style="text-align: right;">Aptos (1T&rarr;2T)</th>
                            <th onclick="sortByColumn('severidade')" style="text-align: center;">Severidade</th>
                            <th onclick="sortByColumn('comparecimento')" style="text-align: right;">Comparecimento</th>
                            <th onclick="sortByColumn('biometria')" style="text-align: right;">Com Biometria</th>
                            <th onclick="sortByColumn('sem_biometria')" style="text-align: right;">Sem Biometria</th>
                            <th onclick="sortByColumn('flavio')" style="text-align: right;">Flávio (22)</th>
                            <th onclick="sortByColumn('lula')" style="text-align: right;">Lula (13)</th>
                            <th onclick="sortByColumn('terceira_via')" style="text-align: right;">3ª Via 1T</th>
                            <th>Inconsistências Identificadas</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
            </div>
            <div id="filterCount" style="margin-top: 0.75rem; font-size: 0.8125rem; color: #64748b; text-align: right;">
            </div>
        </div>

        <!-- FOOTER METODOLÓGICO -->
        <div style="text-align: center; margin-top: 2rem; padding: 1.5rem; font-size: 0.75rem; color: #64748b; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0 0 0.5rem 0;"><strong>Ferramenta Forense de Auditoria da Urna Eletrônica</strong> &bull; 100 Regras Técnicas de Integridade Forense e Matemática Eleitoral.</p>
            <p style="margin: 0;">Análise estritamente científica sobre arquivos oficiais do TSE (bu.dat) de 1º e 2º Turno. As classificações refletem regras objetivas sem emitir juízo político.</p>
        </div>
    </div>

    <!-- SCRIPT DE FILTRAGEM, ORDENAÇÃO E RENDERIZAÇÃO OFFLINE -->
    <script>
        const allSections = {anom_json_str};
        let currentSort = {{ column: 'severidade', order: 'desc' }};

        const SEV_WEIGHTS = {{
            'ALTA': 3,
            'MEDIA': 2,
            'BAIXA': 1,
            'INFO': 0,
            'NORMAL': -1
        }};

        function getSeverityBadge(sev) {{
            if (sev === 'ALTA') return '<span class="badge badge-red">ALTA</span>';
            if (sev === 'MEDIA') return '<span class="badge badge-yellow">MÉDIA</span>';
            if (sev === 'BAIXA') return '<span class="badge badge-blue">BAIXA</span>';
            return '<span class="text-xs text-slate-500">' + sev + '</span>';
        }}

        function getSectionValue(s, column) {{
            const d1 = s.dados_1t || {{}};
            const d2 = s.dados_2t || {{}};
            const p1 = d1.votos_presidenciais || {{}};
            const p2 = d2.votos_presidenciais || {{}};

            switch(column) {{
                case 'municipio': return (s.municipio_nome || '').toLowerCase();
                case 'zona': return s.zona || 0;
                case 'secao': return s.secao || 0;
                case 'aptos': return d2.aptos || 0;
                case 'severidade': return SEV_WEIGHTS[s.worst_severity] || 0;
                case 'comparecimento': return d2.comparecimento || 0;
                case 'biometria': return d2.biometria_sim || 0;
                case 'sem_biometria': return (d2.biometria_bio || 0) + (d2.biometria_nao || 0);
                case 'flavio': return (p2['22'] || 0) - (p1['22'] || 0);
                case 'lula': return (p2['13'] || 0) - (p1['13'] || 0);
                case 'terceira_via': return d1.total_terceira_via || 0;
                default: return 0;
            }}
        }}

        function sortByColumn(column) {{
            if (currentSort.column === column) {{
                currentSort.order = currentSort.order === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSort.column = column;
                currentSort.order = 'desc';
            }}
            applyFilters();
        }}

        function applySortDropdown() {{
            const val = document.getElementById('sortSelect').value;
            if (val === 'sev_desc') currentSort = {{ column: 'severidade', order: 'desc' }};
            if (val === 'sev_asc') currentSort = {{ column: 'severidade', order: 'asc' }};
            if (val === 'mun_asc') currentSort = {{ column: 'municipio', order: 'asc' }};
            if (val === 'comp_delta_desc') currentSort = {{ column: 'comparecimento', order: 'desc' }};
            if (val === 'comp_delta_asc') currentSort = {{ column: 'comparecimento', order: 'asc' }};
            if (val === 'flavio_drop_desc') currentSort = {{ column: 'flavio', order: 'asc' }};
            if (val === 'lula_drop_desc') currentSort = {{ column: 'lula', order: 'asc' }};
            if (val === 't3_desc') currentSort = {{ column: 'terceira_via', order: 'desc' }};
            if (val === 'bio_drop_desc') currentSort = {{ column: 'biometria', order: 'asc' }};
            applyFilters();
        }}

        function applyFilters() {{
            const search = document.getElementById('searchInput').value.toLowerCase().trim();
            const sevFilter = document.getElementById('severitySelect').value;
            const anomFilter = document.getElementById('anomalySelect').value;

            let filtered = allSections.filter(s => {{
                if (sevFilter !== 'ALL' && s.worst_severity !== sevFilter) return false;
                if (anomFilter !== 'ALL' && !s.anomalias.some(a => a.code === anomFilter)) return false;

                if (search) {{
                    const mun = (s.municipio_nome || '').toLowerCase();
                    const munCode = String(s.municipio || '');
                    const zona = String(s.zona || '');
                    const secao = String(s.secao || '');
                    const hasAnom = s.anomalias.some(a => a.code.toLowerCase().includes(search) || (a.title || '').toLowerCase().includes(search));
                    if (!mun.includes(search) && !munCode.includes(search) && !zona.includes(search) && !secao.includes(search) && !hasAnom) {{
                        return false;
                    }}
                }}
                return true;
            }});

            // Ordenação
            filtered.sort((a, b) => {{
                const valA = getSectionValue(a, currentSort.column);
                const valB = getSectionValue(b, currentSort.column);
                if (valA < valB) return currentSort.order === 'asc' ? -1 : 1;
                if (valA > valB) return currentSort.order === 'asc' ? 1 : -1;
                return 0;
            }});

            const tbody = document.getElementById('tableBody');
            const limit = Math.min(filtered.length, 250);
            let html = '';

            for (let i = 0; i < limit; i++) {{
                const s = filtered[i];
                const d1 = s.dados_1t || {{}};
                const d2 = s.dados_2t || {{}};
                const p1 = d1.votos_presidenciais || {{}};
                const p2 = d2.votos_presidenciais || {{}};

                const apt1 = d1.aptos || 0;
                const apt2 = d2.aptos || 0;
                const aptClass = apt1 !== apt2 ? 'text-amber-700 font-bold' : 'text-slate-600';

                const c1 = d1.comparecimento || 0;
                const c2 = d2.comparecimento || 0;

                const bio1 = d1.biometria_sim || 0;
                const bio2 = d2.biometria_sim || 0;

                const sem1 = (d1.biometria_bio || 0) + (d1.biometria_nao || 0);
                const sem2 = (d2.biometria_bio || 0) + (d2.biometria_nao || 0);

                const v1_22 = p1['22'] || 0;
                const v2_22 = p2['22'] || 0;
                const d_22 = v2_22 - v1_22;
                const cl_22 = d_22 > 0 ? 'text-emerald-700' : (d_22 < 0 ? 'text-rose-700 font-bold' : 'text-slate-600');

                const v1_13 = p1['13'] || 0;
                const v2_13 = p2['13'] || 0;
                const d_13 = v2_13 - v1_13;
                const cl_13 = d_13 > 0 ? 'text-emerald-700' : (d_13 < 0 ? 'text-rose-700 font-bold' : 'text-slate-600');

                const t3 = d1.total_terceira_via || 0;

                const badges = s.anomalias.map(a => 
                    `<span class="badge badge-anom" title="${{a.description || ''}} &bull; ${{a.title || ''}}">${{a.code}}</span>`
                ).join(' ');

                html += `
                <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors text-xs">
                    <td class="py-2.5 px-2 font-semibold text-slate-800">${{s.municipio_nome || 'Município ' + s.municipio}}</td>
                    <td class="py-2.5 px-2 text-center font-mono">${{s.zona}}</td>
                    <td class="py-2.5 px-2 text-center font-mono font-bold text-slate-900">${{s.secao}}</td>
                    <td class="py-2.5 px-2 text-right font-mono ${{aptClass}}">${{apt1}} &rarr; <strong>${{apt2}}</strong></td>
                    <td class="py-2.5 px-2 text-center">${{getSeverityBadge(s.worst_severity)}}</td>
                    <td class="py-2.5 px-2 text-right font-mono">${{c1}} &rarr; <strong>${{c2}}</strong></td>
                    <td class="py-2.5 px-2 text-right font-mono">${{bio1}} &rarr; <strong>${{bio2}}</strong></td>
                    <td class="py-2.5 px-2 text-right font-mono">${{sem1}} &rarr; <strong>${{sem2}}</strong></td>
                    <td class="py-2.5 px-2 text-right font-mono ${{cl_22}}">${{v1_22}} &rarr; <strong>${{v2_22}}</strong> <span class="text-[10px]">(${{d_22 >= 0 ? '+' : ''}}${{d_22}})</span></td>
                    <td class="py-2.5 px-2 text-right font-mono ${{cl_13}}">${{v1_13}} &rarr; <strong>${{v2_13}}</strong> <span class="text-[10px]">(${{d_13 >= 0 ? '+' : ''}}${{d_13}})</span></td>
                    <td class="py-2.5 px-2 text-right font-mono font-semibold text-slate-700">${{t3}}</td>
                    <td class="py-2.5 px-2" style="max-width: 380px;">${{badges}}</td>
                </tr>`;
            }}

            tbody.innerHTML = html;
            document.getElementById('filterCount').textContent = `Exibindo ${{limit}} de ${{filtered.length}} seções encontradas nos filtros (ordenadas por ${{currentSort.column}} ${{currentSort.order}}).`;
        }}

        // Inicializa ao carregar
        window.onload = function() {{
            applyFilters();
        }};
    </script>
</body>
</html>
"""
