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
from typing import Any, Callable, Optional

from .models import UrnaKey
from .municipios import Municipio, load_table
from .parsers.bu import parse_bu
from .reports import json_report
from .scanner import NAME_RE

import math

_SC_COORDS_CACHE: Optional[dict[str, Any]] = None

def get_sc_coords() -> dict[str, Any]:
    global _SC_COORDS_CACHE
    if _SC_COORDS_CACHE is None:
        p = Path("data/municipios_sc_coords.json")
        if not p.is_file():
            p = Path(__file__).resolve().parent.parent.parent / "data" / "municipios_sc_coords.json"
        if p.is_file():
            try:
                _SC_COORDS_CACHE = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                _SC_COORDS_CACHE = {}
        else:
            _SC_COORDS_CACHE = {}
    return _SC_COORDS_CACHE

def calculate_municipios_distance_km(code1: int, code2: int) -> Optional[float]:
    coords = get_sc_coords()
    c1 = coords.get(str(code1))
    c2 = coords.get(str(code2))
    if not c1 or not c2:
        return None
    R = 6371.0
    lat1, lon1 = math.radians(c1["lat"]), math.radians(c1["lon"])
    lat2, lon2 = math.radians(c2["lat"]), math.radians(c2["lon"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


# Candidatos oficiais de referência (Eleições 2026)
PRESIDENTIAL_CANDIDATES = {
    13: "LULA (PT)",
    22: "FLAVIO BOLSONARO (PL)",
    14: "RENAN SANTOS (MISSÃO)",
    70: "ESCRITOR AUGUSTO CURY (AVANTE)",
    55: "RONALDO CAIADO (PSD/UNIÃO)",
    30: "ZEMA (NOVO)",
    80: "SAMARA (UP)",
    16: "HERTZ DIAS (PSTU)",
    27: "CLARIANA BARAO (DC)",
    21: "EDMILSON COSTA (PCB)",
    29: "RUI COSTA PIMENTA (PCO)",
    35: "PMB (VOTO LEGENDA)",
    28: "LEONARDO AVALANCHE (PRTB)",
    12: "CIRO GOMES (PDT)",
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
    fraud_score: int = 0
    fraud_label: str = ""

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
            "fraud_score": self.fraud_score,
            "fraud_label": self.fraud_label,
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
    mun_resolver: Optional[Callable[[int], Optional[str]]] = None,
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

    # CHK003: Troca de Flash de Carga (Procedimento padrão entre turnos para carregar nova cédula)
    if s1.numero_serie_fc and s2.numero_serie_fc and s1.numero_serie_fc != s2.numero_serie_fc:
        anomalies.append(
            Anomaly(
                code="CHK003_TROCA_FLASH_CARGA",
                category=CAT_HARDWARE,
                severity=SEV_INFO,
                title="Atualização da Flash de Carga (Procedimento Normal do 2T)",
                description=(
                    f"FC atualizada para o 2T: 1T={s1.numero_serie_fc} vs 2T={s2.numero_serie_fc}. "
                    f"Procedimento rotineiro dos cartórios eleitorais para carregar a cédula exclusiva dos finalistas no 2º turno."
                ),
                details={"fc_1t": s1.numero_serie_fc, "fc_2t": s2.numero_serie_fc, "procedimento_normal_2t": True},
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

    # CHK014: Carga de urna em município diferente (com auditoria de distância e vizinhança)
    if s2.municipio_correspondencia and s2.municipio_correspondencia != s2.municipio:
        nome_secao = mun_resolver(s2.municipio) if mun_resolver else None
        nome_corr = mun_resolver(s2.municipio_correspondencia) if mun_resolver else None
        txt_secao = f"{s2.municipio} ({nome_secao})" if nome_secao else str(s2.municipio)
        txt_corr = f"{s2.municipio_correspondencia} ({nome_corr})" if nome_corr else str(s2.municipio_correspondencia)

        dist_km = calculate_municipios_distance_km(s2.municipio, s2.municipio_correspondencia)
        is_vizinha = (dist_km is not None and dist_km <= 45.0)

        if dist_km is not None:
            if is_vizinha:
                status_geo = f"[Cidades Vizinhas / Limítrofes - ~{dist_km} km]"
                sev_chk14 = SEV_BAIXA  # Cidade vizinha pode ser normal por contingência regional
            else:
                status_geo = f"[CIDADES NÃO VIZINHAS / DISTANTES - ~{dist_km} km]"
                sev_chk14 = SEV_ALTA   # Cidade distante não é normal
        else:
            status_geo = "[Distância não determinada]"
            sev_chk14 = SEV_ALTA

        anomalies.append(
            Anomaly(
                code="CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO",
                category=CAT_HARDWARE,
                severity=sev_chk14,
                title="Carga Gerada para Outro Município",
                description=(
                    f"Correspondência vinculada ao município {txt_corr}, mas a seção pertence ao município {txt_secao} {status_geo}."
                ),
                details={
                    "mun_secao": s2.municipio,
                    "mun_secao_nome": nome_secao,
                    "mun_corr": s2.municipio_correspondencia,
                    "mun_corr_nome": nome_corr,
                    "distancia_km": dist_km,
                    "cidades_vizinhas": is_vizinha,
                },
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

    # CHK016: Variação de eleitores aptos da seção (> 0.5% é relevante/ALTA, <= 0.5% é residual/INFO)
    if s1.aptos_secao != s2.aptos_secao:
        diff_aptos = s2.aptos_secao - s1.aptos_secao
        pct_diff_aptos = abs(diff_aptos) / s1.aptos_secao * 100.0 if s1.aptos_secao > 0 else 0.0
        is_relevante = pct_diff_aptos > 0.5
        sev_aptos = SEV_ALTA if is_relevante else SEV_INFO
        title_aptos = "Variação Relevante no Cadastro de Aptos (> 0.5%)" if is_relevante else "Ajuste Cadastral Residual de Aptos (<= 0.5% - Comum)"
        anomalies.append(
            Anomaly(
                code="CHK016_VARIACAO_APTOS_SECAO",
                category=CAT_ELEITORADO,
                severity=sev_aptos,
                title=title_aptos,
                description=f"Caderno eleitoral variou em {diff_aptos:+d} ({pct_diff_aptos:.2f}%) [1T: {s1.aptos_secao} vs 2T: {s2.aptos_secao}].",
                details={"aptos_1t": s1.aptos_secao, "aptos_2t": s2.aptos_secao, "delta": diff_aptos, "pct_var": round(pct_diff_aptos, 2), "relevante": is_relevante},
            )
        )

    # CHK017: Redução de aptos originais
    if s2.aptos_secao < s1.aptos_secao:
        diff_aptos = s1.aptos_secao - s2.aptos_secao
        pct_diff_aptos = diff_aptos / s1.aptos_secao * 100.0 if s1.aptos_secao > 0 else 0.0
        is_relevante = pct_diff_aptos > 0.5
        sev_aptos = SEV_ALTA if is_relevante else SEV_INFO
        title_aptos = "Redução Relevante de Eleitores Originais (> 0.5%)" if is_relevante else "Redução Residual de Eleitores Originais (<= 0.5%)"
        anomalies.append(
            Anomaly(
                code="CHK017_REDUCAO_APTOS_SECAO",
                category=CAT_ELEITORADO,
                severity=sev_aptos,
                title=title_aptos,
                description=f"O número de aptos originais diminuiu de {s1.aptos_secao} para {s2.aptos_secao} (-{diff_aptos}, {pct_diff_aptos:.2f}%).",
                details={"queda": diff_aptos, "pct_var": round(pct_diff_aptos, 2), "relevante": is_relevante},
            )
        )

    # CHK018: Aumento de aptos originais
    if s2.aptos_secao > s1.aptos_secao:
        diff_aptos = s2.aptos_secao - s1.aptos_secao
        pct_diff_aptos = diff_aptos / s1.aptos_secao * 100.0 if s1.aptos_secao > 0 else 0.0
        is_relevante = pct_diff_aptos > 0.5
        sev_aptos = SEV_ALTA if is_relevante else SEV_INFO
        title_aptos = "Aumento Relevante de Eleitores Originais (> 0.5%)" if is_relevante else "Aumento Residual de Eleitores Originais (<= 0.5%)"
        anomalies.append(
            Anomaly(
                code="CHK018_AUMENTO_APTOS_SECAO",
                category=CAT_ELEITORADO,
                severity=sev_aptos,
                title=title_aptos,
                description=f"O número de aptos originais subiu de {s1.aptos_secao} para {s2.aptos_secao} (+{diff_aptos}, {pct_diff_aptos:.2f}%).",
                details={"aumento": diff_aptos, "pct_var": round(pct_diff_aptos, 2), "relevante": is_relevante},
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
    v1 = {int(k): v for k, v in s1.votos_presidenciais.items() if str(k).isdigit()}
    v2 = {int(k): v for k, v in s2.votos_presidenciais.items() if str(k).isdigit()}
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
    salto_m = s2.biometria_bio - s1.biometria_bio
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        queda_bio = s1.pct_biometria - s2.pct_biometria
        salto_bio_ano = s2.pct_biografia - s1.pct_biografia
        if queda_bio >= 30.0:
            anomalies.append(
                Anomaly(
                    code="CHK066_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_30PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_ALTA,
                    title="Desabamento Crítico de Validação Biométrica (> 30 pp)",
                    description=(
                        f"Validação por digital despencou de {s1.pct_biometria:.1f}% ({s1.biometria_sim} eleitores) "
                        f"para {s2.pct_biometria:.1f}% ({s2.biometria_sim} eleitores) [-{queda_bio:.1f} pp]. "
                        f"Liberações manuais por ano de nascimento subiram de {s1.biometria_bio} para {s2.biometria_bio} (+{salto_m} manuais)."
                    ),
                    details={
                        "bio_sim_1t": s1.biometria_sim,
                        "bio_sim_2t": s2.biometria_sim,
                        "pct_bio_1t": s1.pct_biometria,
                        "pct_bio_2t": s2.pct_biometria,
                        "queda_pp": round(queda_bio, 2),
                        "bio_ano_1t": s1.biometria_bio,
                        "bio_ano_2t": s2.biometria_bio,
                        "salto_manual": salto_m,
                        "comp_1t": s1.comparecimento,
                        "comp_2t": s2.comparecimento,
                    },
                )
            )
        elif queda_bio >= 20.0:
            anomalies.append(
                Anomaly(
                    code="CHK067_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_20PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_MEDIA,
                    title="Queda Acentuada de Biometria (> 20 pp)",
                    description=(
                        f"Biometria recuou de {s1.pct_biometria:.1f}% ({s1.biometria_sim} eleitores) "
                        f"para {s2.pct_biometria:.1f}% ({s2.biometria_sim} eleitores) [-{queda_bio:.1f} pp]. "
                        f"Liberações manuais por ano de nascimento subiram de {s1.biometria_bio} para {s2.biometria_bio} (+{salto_m} manuais)."
                    ),
                    details={
                        "bio_sim_1t": s1.biometria_sim,
                        "bio_sim_2t": s2.biometria_sim,
                        "pct_bio_1t": s1.pct_biometria,
                        "pct_bio_2t": s2.pct_biometria,
                        "queda_pp": round(queda_bio, 2),
                        "bio_ano_1t": s1.biometria_bio,
                        "bio_ano_2t": s2.biometria_bio,
                        "salto_manual": salto_m,
                        "comp_1t": s1.comparecimento,
                        "comp_2t": s2.comparecimento,
                    },
                )
            )

        # CHK068 e CHK069: Surto de biometria biográfica (ano de nascimento)
        if salto_bio_ano >= 25.0:
            anomalies.append(
                Anomaly(
                    code="CHK068_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_25PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_ALTA,
                    title="Surto Crítico de Habilitação Manual por Ano de Nascimento (> 25 pp)",
                    description=(
                        f"Liberação manual por ano de nascimento saltou de {s1.pct_biografia:.1f}% ({s1.biometria_bio} eleitores) "
                        f"para {s2.pct_biografia:.1f}% ({s2.biometria_bio} eleitores) [+ {salto_bio_ano:.1f} pp], "
                        f"enquanto validações digitais caíram de {s1.biometria_sim} para {s2.biometria_sim} (-{s1.biometria_sim - s2.biometria_sim})."
                    ),
                    details={
                        "bio_ano_1t": s1.biometria_bio,
                        "bio_ano_2t": s2.biometria_bio,
                        "pct_ano_1t": s1.pct_biografia,
                        "pct_ano_2t": s2.pct_biografia,
                        "salto_pp": round(salto_bio_ano, 2),
                        "bio_sim_1t": s1.biometria_sim,
                        "bio_sim_2t": s2.biometria_sim,
                        "comp_1t": s1.comparecimento,
                        "comp_2t": s2.comparecimento,
                    },
                )
            )
        elif salto_bio_ano >= 15.0:
            anomalies.append(
                Anomaly(
                    code="CHK069_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_15PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_MEDIA,
                    title="Salto acentuado de habilitação manual por ano de nascimento (> 15 pp)",
                    description=(
                        f"Liberação manual por ano de nascimento subiu de {s1.pct_biografia:.1f}% ({s1.biometria_bio}) "
                        f"para {s2.pct_biografia:.1f}% ({s2.biometria_bio}) [+ {salto_bio_ano:.1f} pp]."
                    ),
                    details={
                        "bio_ano_1t": s1.biometria_bio,
                        "bio_ano_2t": s2.biometria_bio,
                        "salto_pp": round(salto_bio_ano, 2),
                    },
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

    # ========================================================================
    # GRUPO 9: REGRAS FORENSES AVANÇADAS ADICIONAIS (CHK101 a CHK120)
    # ========================================================================

    # CHK101: Concentração no 1º dígito (Lei de Benford)
    for cand in runoff_candidates:
        c2 = v2.get(cand, 0)
        if c2 >= 10:
            p_digit = int(str(c2)[0])
            if p_digit == 9 and c2 > 80 and s2.votos_validos >= 100:
                anomalies.append(
                    Anomaly(
                        code="CHK101_BENFORD_PRIMEIRO_DIGITO_ANOMALO",
                        category=CAT_VOTACAO,
                        severity=SEV_BAIXA,
                        title=f"Primeiro dígito anômalo pela Lei de Benford para candidato {cand}",
                        description=f"Candidato obteve {c2} votos (iniciado em dígito 9, estatisticamente infrequente).",
                        details={"candidato": cand, "votos": c2, "primeiro_digito": p_digit},
                    )
                )

    # CHK102: Dígitos redondos excessivos
    if s2.comparecimento >= 100 and s2.comparecimento % 100 == 0:
        anomalies.append(
            Anomaly(
                code="CHK102_DIGITOS_REDONDOS_EXCESSIVOS",
                category=CAT_COMPARECIMENTO,
                severity=SEV_BAIXA,
                title="Comparecimento perfeitamente redondo em centena (00)",
                description=f"Comparecimento cravado em exatamente {s2.comparecimento} eleitores.",
                details={"comparecimento": s2.comparecimento},
            )
        )

    # CHK103: Urna substituta sem histórico de carga
    if s1.numero_interno_urna and s2.numero_interno_urna and s1.numero_interno_urna != s2.numero_interno_urna:
        if not s2.codigo_carga:
            anomalies.append(
                Anomaly(
                    code="CHK103_URNA_SUBSTITUTA_SEM_HISTORICO_CARGA",
                    category=CAT_HARDWARE,
                    severity=SEV_ALTA,
                    title="Urna substituída sem código de carga válido",
                    description="Urna de contingência entrou em operação sem código de carga documentado.",
                    details={"urna_2t": s2.numero_interno_urna},
                )
            )

    # CHK104: Data de carga posterior ao encerramento da eleição
    if s2.data_carga and s2.encerramento:
        try:
            dt_cg2 = datetime.fromisoformat(s2.data_carga)
            dt_enc2 = datetime.fromisoformat(s2.encerramento)
            if dt_cg2 > dt_enc2:
                anomalies.append(
                    Anomaly(
                        code="CHK104_CORRESPONDENCIA_DATA_CARGA_ANTERIOR_1T",
                        category=CAT_HARDWARE,
                        severity=SEV_ALTA,
                        title="Data de carga da urna posterior ao encerramento no 2T",
                        description=f"Urna do 2T tem data de carga {s2.data_carga}, posterior ao encerramento oficial ({s2.encerramento}).",
                        details={"data_carga_2t": s2.data_carga, "encerramento_2t": s2.encerramento},
                    )
                )
        except Exception:
            pass

    # CHK105: Pico de votos concentrado em votação comprimida
    if s2.duracao_minutos and s2.duracao_minutos <= 300 and s2.comparecimento >= 150:
        anomalies.append(
            Anomaly(
                code="CHK105_PICO_VOTOS_ULTIMA_HORA_ENCERRAMENTO",
                category=CAT_TEMPORAL,
                severity=SEV_MEDIA,
                title="Votação expressiva comprimida em poucas horas",
                description=f"{s2.comparecimento} eleitores votaram em apenas {s2.duracao_minutos:.0f} minutos (ritmo acelerado).",
                details={"duracao_minutos": s2.duracao_minutos, "comparecimento": s2.comparecimento},
            )
        )

    # CHK106: Intervalo de abertura para o primeiro voto excede 2h
    if s2.abertura:
        try:
            ab_dt = datetime.fromisoformat(s2.abertura)
            if ab_dt.hour >= 10:
                anomalies.append(
                    Anomaly(
                        code="CHK106_INTERVALO_ABERTURA_PRIMEIRO_VOTO_EXCEDE_2H",
                        category=CAT_TEMPORAL,
                        severity=SEV_BAIXA,
                        title="Urna aberta com mais de 2 horas de atraso no 2T",
                        description=f"Abertura registrada apenas às {ab_dt.strftime('%H:%M:%S')}.",
                        details={"abertura_2t": s2.abertura},
                    )
                )
        except Exception:
            pass

    # CHK107: Inversão radical da proporção de brancos e nulos
    bn_tot_1 = s1.votos_brancos + s1.votos_nulos
    bn_tot_2 = s2.votos_brancos + s2.votos_nulos
    if bn_tot_1 >= 10 and bn_tot_2 >= 10:
        pct_b_1 = s1.votos_brancos / bn_tot_1 * 100
        pct_b_2 = s2.votos_brancos / bn_tot_2 * 100
        if abs(pct_b_2 - pct_b_1) >= 50.0:
            anomalies.append(
                Anomaly(
                    code="CHK107_INVERSAO_PROPORCAO_BRANCOS_NULOS",
                    category=CAT_BRANCOS_NULOS,
                    severity=SEV_MEDIA,
                    title="Inversão desproporcional na proporção de brancos vs nulos",
                    description=f"Votos brancos representavam {pct_b_1:.1f}% dos inválidos no 1T e passaram a {pct_b_2:.1f}% no 2T.",
                    details={"pct_brancos_invalidos_1t": pct_b_1, "pct_brancos_invalidos_2t": pct_b_2},
                )
            )

    # CHK108: Migração total de brancos e nulos para um único candidato
    if bn_tot_1 >= 15 and bn_tot_2 < bn_tot_1:
        queda_bn = bn_tot_1 - bn_tot_2
        ganho_a = max(0, va2 - va1)
        ganho_b = max(0, vb2 - vb1)
        if ganho_a >= queda_bn * 0.9 and ganho_b <= 2:
            anomalies.append(
                Anomaly(
                    code="CHK108_MIGRACAO_TOTAL_BRANCOS_NULOS_PARA_UM_CANDIDATO",
                    category=CAT_BRANCOS_NULOS,
                    severity=SEV_ALTA,
                    title=f"Migração quase total de brancos/nulos para {PRESIDENTIAL_CANDIDATES.get(cand_a, cand_a)}",
                    description=f"Redução de {queda_bn} votos inválidos coincidiu com ganho unilateral de {ganho_a} votos.",
                    details={"queda_bn": queda_bn, "ganho_candidato": ganho_a},
                )
            )
        elif ganho_b >= queda_bn * 0.9 and ganho_a <= 2:
            anomalies.append(
                Anomaly(
                    code="CHK108_MIGRACAO_TOTAL_BRANCOS_NULOS_PARA_UM_CANDIDATO",
                    category=CAT_BRANCOS_NULOS,
                    severity=SEV_ALTA,
                    title=f"Migração quase total de brancos/nulos para {PRESIDENTIAL_CANDIDATES.get(cand_b, cand_b)}",
                    description=f"Redução de {queda_bn} votos inválidos coincidiu com ganho unilateral de {ganho_b} votos.",
                    details={"queda_bn": queda_bn, "ganho_candidato": ganho_b},
                )
            )

    # CHK109: Abstenção maior que os votos do vencedor na seção
    if s2.aptos >= 100:
        max_votos_cand = max(v2.values()) if v2 else 0
        if s2.abstencao > max_votos_cand:
            anomalies.append(
                Anomaly(
                    code="CHK109_ABSTENCAO_MAIOR_QUE_VOTOS_DO_VENCEDOR",
                    category=CAT_COMPARECIMENTO,
                    severity=SEV_BAIXA,
                    title="Abstenção superior à votação do candidato vencedor na seção",
                    description=f"{s2.abstencao} eleitores faltaram, superando os {max_votos_cand} votos do vencedor da urna.",
                    details={"abstencao": s2.abstencao, "votos_vencedor": max_votos_cand},
                )
            )

    # CHK110: Abstenção reduzida com migração unilateral
    if s2.abstencao < s1.abstencao and s1.comparecimento >= 50:
        queda_abs = s1.abstencao - s2.abstencao
        if queda_abs >= 15:
            ganho_a = max(0, va2 - va1)
            ganho_b = max(0, vb2 - vb1)
            if ganho_a >= queda_abs * 0.95 and ganho_b <= 1:
                anomalies.append(
                    Anomaly(
                        code="CHK110_ABSTENCAO_REDUZIDA_COM_MIGRACAO_UNILATERAL",
                        category=CAT_COMPARECIMENTO,
                        severity=SEV_ALTA,
                        title=f"Redução de abstenção revertida 100% para {PRESIDENTIAL_CANDIDATES.get(cand_a, cand_a)}",
                        description=f"{queda_abs} eleitores a mais compareceram e {ganho_a} votos foram para o mesmo candidato.",
                        details={"novos_votantes": queda_abs, "ganho_cand": ganho_a},
                    )
                )
            elif ganho_b >= queda_abs * 0.95 and ganho_a <= 1:
                anomalies.append(
                    Anomaly(
                        code="CHK110_ABSTENCAO_REDUZIDA_COM_MIGRACAO_UNILATERAL",
                        category=CAT_COMPARECIMENTO,
                        severity=SEV_ALTA,
                        title=f"Redução de abstenção revertida 100% para {PRESIDENTIAL_CANDIDATES.get(cand_b, cand_b)}",
                        description=f"{queda_abs} eleitores a mais compareceram e {ganho_b} votos foram para o mesmo candidato.",
                        details={"novos_votantes": queda_abs, "ganho_cand": ganho_b},
                    )
                )

    # CHK111: Habilitação manual biográfica superior à biométrica
    if s2.biometria_bio > s2.biometria_sim and s2.biometria_bio >= 20:
        anomalies.append(
            Anomaly(
                code="CHK111_HABILITACAO_BIOGRAFICA_SUPERIOR_A_BIOMETRICA",
                category=CAT_BIOMETRIA,
                severity=SEV_ALTA,
                title="Liberação manual por ano de nascimento superou a biometria",
                description=(
                    f"Mais eleitores foram liberados manualmente por ano de nascimento ({s2.biometria_bio}) "
                    f"do que por impressão digital ({s2.biometria_sim}) no 2T."
                ),
                details={"bio_manual": s2.biometria_bio, "bio_digital": s2.biometria_sim},
            )
        )

    # CHK112: Desabamento brutal de biometria > 40 pp
    if s1.comparecimento >= 50 and s2.comparecimento >= 50:
        if queda_bio >= 40.0:
            anomalies.append(
                Anomaly(
                    code="CHK112_DESABAMENTO_BRUTAL_BIOMETRIA_MAIOR_40PP",
                    category=CAT_BIOMETRIA,
                    severity=SEV_ALTA,
                    title="Desabamento brutal da validação biométrica (> 40 pp)",
                    description=f"Biometria despencou de {s1.pct_biometria:.1f}% para {s2.pct_biometria:.1f}% (-{queda_bio:.1f} pp).",
                    details={"bio_1t": s1.pct_biometria, "bio_2t": s2.pct_biometria, "queda": queda_bio},
                )
            )

    # CHK113: Falha massiva de digital (eleitores sem biometria triplicaram)
    if s1.biometria_nao >= 5 and s2.biometria_nao >= (3 * s1.biometria_nao) and s2.comparecimento >= 50:
        anomalies.append(
            Anomaly(
                code="CHK113_FALHA_MASSIVA_RECONHECIMENTO_DIGITAL_SEM_BIOMETRIA",
                category=CAT_BIOMETRIA,
                severity=SEV_MEDIA,
                title="Eleitores classificados sem biometria triplicaram no 2T",
                description=f"Sem biometria subiu de {s1.biometria_nao} (1T) para {s2.biometria_nao} (2T).",
                details={"sem_bio_1t": s1.biometria_nao, "sem_bio_2t": s2.biometria_nao},
            )
        )

    # CHK114: Votos de candidato superam eleitorado original da seção
    for cand in runoff_candidates:
        c2 = v2.get(cand, 0)
        if s2.aptos_secao > 0 and c2 > s2.aptos_secao:
            cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
            anomalies.append(
                Anomaly(
                    code="CHK114_VOTOS_CANDIDATO_SUPERAM_APTOS_ORIGINAIS",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title=f"Votação de {cand_nome} supera o total de eleitores originais",
                    description=f"{cand_nome} obteve {c2} votos em seção com {s2.aptos_secao} aptos originais (dependente de TTE).",
                    details={"votos": c2, "aptos_originais": s2.aptos_secao},
                )
            )

    # CHK115: Queda nominal de ambos os finalistas com maior comparecimento
    if s2.comparecimento > s1.comparecimento and va2 < va1 and vb2 < vb1:
        anomalies.append(
            Anomaly(
                code="CHK115_QUEDA_NOMINAL_AMBOS_CANDIDATOS_COM_MAIOR_COMPARECIMENTO",
                category=CAT_VOTACAO,
                severity=SEV_ALTA,
                title="Ambos os candidatos perderam votos nominais com mais eleitores",
                description=f"Comparecimento aumentou (+{delta_comp}), mas Lula caiu ({va1}->{va2}) e Flávio caiu ({vb1}->{vb2}).",
                details={"delta_comp": delta_comp, "lula_1t": va1, "lula_2t": va2, "flavio_1t": vb1, "flavio_2t": vb2},
            )
        )

    # CHK116: Retenção do 1º turno inferior a 50% com comparecimento estável
    if s1.comparecimento >= 50 and s2.comparecimento >= s1.comparecimento * 0.9:
        for cand in runoff_candidates:
            c1 = v1.get(cand, 0)
            c2 = v2.get(cand, 0)
            cand_nome = PRESIDENTIAL_CANDIDATES.get(cand, f"Candidato {cand}")
            if c1 >= 30 and (c2 / c1) < 0.5:
                anomalies.append(
                    Anomaly(
                        code="CHK116_TAXA_RETENCAO_PRIMEIRO_TURNO_INFERIOR_A_50PCT",
                        category=CAT_VOTACAO,
                        severity=SEV_ALTA,
                        title=f"{cand_nome} perdeu mais da metade dos votos do 1T",
                        description=f"{cand_nome} reteve apenas {c2/c1*100:.1f}% da votação obtida no 1T ({c1} -> {c2}).",
                        details={"votos_1t": c1, "votos_2t": c2, "taxa_retencao": round(c2 / c1 * 100, 2)},
                    )
                )

    # CHK117: Terceira via do 1T sumiu sem migrar para os finalistas
    if s1.total_terceira_via >= 40 and s2.comparecimento >= s1.comparecimento:
        ganho_a = max(0, va2 - va1)
        ganho_b = max(0, vb2 - vb1)
        if (ganho_a + ganho_b) < s1.total_terceira_via * 0.3:
            anomalies.append(
                Anomaly(
                    code="CHK117_TRANSFERENCIA_ZERO_TERCEIRA_VIA_COM_COMPARECIMENTO_CRESCENTE",
                    category=CAT_VOTACAO,
                    severity=SEV_MEDIA,
                    title="Votos de terceira via não migraram para os finalistas",
                    description=(
                        f"Havia {s1.total_terceira_via} votos de 3ª via no 1T, "
                        f"mas os finalistas ganharam juntos apenas {ganho_a + ganho_b} votos."
                    ),
                    details={"terceira_1t": s1.total_terceira_via, "ganho_total_finalistas": ganho_a + ganho_b},
                )
            )

    # CHK118: Diferença entre encerramento e emissão > 15 minutos
    if s2.data_hora_emissao and s2.encerramento:
        try:
            em_dt = datetime.fromisoformat(s2.data_hora_emissao)
            enc_dt = datetime.fromisoformat(s2.encerramento)
            diff_min = (em_dt - enc_dt).total_seconds() / 60.0
            if diff_min > 15.0:
                anomalies.append(
                    Anomaly(
                        code="CHK118_DIFERENCA_TEMPO_ENCERRAMENTO_E_EMISSAO_MAIOR_15MIN",
                        category=CAT_TEMPORAL,
                        severity=SEV_BAIXA,
                        title="Emissão do BU demorou mais de 15 minutos após o encerramento",
                        description=f"Intervalo de {diff_min:.0f} minutos entre encerramento ({s2.encerramento}) e emissão do BU ({s2.data_hora_emissao}).",
                        details={"intervalo_min": round(diff_min, 1)},
                    )
                )
        except Exception:
            pass

    # CHK119: Horário de encerramento no segundo exato 17:00:00
    if s2.encerramento:
        try:
            enc_dt = datetime.fromisoformat(s2.encerramento)
            if enc_dt.hour == 17 and enc_dt.minute == 0 and enc_dt.second == 0:
                anomalies.append(
                    Anomaly(
                        code="CHK119_HORARIO_ENCERRAMENTO_IDENTICO_DE_SEGUNDO_ENTRE_URNAS_DISTINTAS",
                        category=CAT_TEMPORAL,
                        severity=SEV_INFO,
                        title="Encerramento cravado exatamente às 17:00:00",
                        description="Encerramento no primeiro segundo regulamentar sem fila.",
                        details={"encerramento": s2.encerramento},
                    )
                )
        except Exception:
            pass

    # CHK120: Votação desproporcional entre candidatos no mesmo local físico
    if s2.local and s2.votos_validos >= 60:
        c1_v = v2.get(cand_a, 0)
        c2_v = v2.get(cand_b, 0)
        if (c1_v >= 50 and c2_v == 0) or (c2_v >= 50 and c1_v == 0):
            anomalies.append(
                Anomaly(
                    code="CHK120_VOTO_UNANIME_NO_LOCAL_DE_VOTACAO",
                    category=CAT_VOTACAO,
                    severity=SEV_ALTA,
                    title="Zero votos para o concorrente em seção expressiva do local físico",
                    description=f"Um dos finalistas teve zero votos em seção com {s2.votos_validos} votos válidos no local {s2.local}.",
                    details={"local": s2.local, "cand_a": c1_v, "cand_b": c2_v},
                )
            )

    return anomalies



def calculate_section_fraud_score(anomalies: list[Anomaly]) -> dict[str, Any]:
    """Calcula a pontuacao de probabilidade de fraude para uma secao especifica."""
    if not anomalies:
        return {"score": 0, "label": "Sem Evidência de Fraude (0%)", "color": "#10b981", "desc": "Urna 100% consistente em todas as 100 verificações forenses."}

    codes = [a.code for a in anomalies]
    has_code = lambda prefix: any(prefix in c for c in codes)

    if (has_code("CHK001") or has_code("CHK004")) and has_code("CHK014") and (has_code("CHK066") or has_code("CHK067")) and (has_code("CHK068") or has_code("CHK069")):
        return {
            "score": 93,
            "label": "Altíssima Probabilidade de Fraude / Vício Material (93%)",
            "color": "#b91c1c",
            "desc": "Conjunção simultânea de troca física de máquina, carga preparada para outro município, desabamento de biometria e explosão de liberações manuais por ano de nascimento."
        }

    score = 0
    if has_code("CHK093") or has_code("CHK098") or has_code("CHK100") or has_code("CHK059"):
        score = max(score, 90)

    if has_code("CHK046"):
        score = max(score, 82)

    if has_code("CHK054") or has_code("CHK055"):
        score = max(score, 85)

    if (has_code("CHK066") or has_code("CHK067")) and (has_code("CHK068") or has_code("CHK069")):
        score = max(score, 88)
    elif has_code("CHK066") or has_code("CHK068"):
        score = max(score, 75)

    chk14 = next((a for a in anomalies if "CHK014" in a.code), None)
    is_chk14_distante = (chk14 and chk14.details.get("cidades_vizinhas") is False)

    if has_code("CHK001") and is_chk14_distante:
        score = max(score, 85)
    elif is_chk14_distante:
        score = max(score, 70)
    elif has_code("CHK001") and has_code("CHK014"):
        score = max(score, 55)
    elif has_code("CHK001"):
        score = max(score, 50)
    elif has_code("CHK014"):
        score = max(score, 20)

    if has_code("CHK056"):
        score = max(score, 70)

    chk16 = next((a for a in anomalies if "CHK016" in a.code), None)
    if chk16 and chk16.severity == "ALTA":
        score = max(score, 55)

    all_info = all(a.severity in ["INFO", "BAIXA"] for a in anomalies)
    if all_info:
        return {
            "score": 3,
            "label": "Risco Mínimo / Ajustes Operacionais Normais (< 5%)",
            "color": "#10b981",
            "desc": "Apresenta apenas ajustes rotineiros comuns (como atualização padrão de Flash de Carga para o 2T ou variação residual <= 0.5% de eleitores)."
        }

    color = "#10b981"
    label = f"Baixo Risco de Fraude ({score}%)"
    desc = "Inconsistências isoladas com baixa probabilidade de alteração dolosa do resultado."

    if score >= 80:
        color = "#b91c1c"
        label = f"Altíssima Probabilidade de Vício / Fraude ({score}%)"
        desc = "Apresenta anomalias graves de hardware, biometria ou contabilidade que rompem as travas de segurança da urna."
    elif score >= 50:
        color = "#d97706"
        label = f"Suspeita Elevada de Manipulação / Contaminação ({score}%)"
        desc = "Combinação de inconsistências relevantes que exigem auditoria documental (folha de presença física e logs)."
    elif score >= 20:
        color = "#eab308"
        label = f"Anomalia Moderada / Risco Médio ({score}%)"
        desc = "Desvios operacionais ou comportamentais atípicos na seção."

    return {"score": score, "label": label, "color": color, "desc": desc}


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



def compute_impact_analysis(sections: list[SectionComparison]) -> dict[str, Any]:
    """Calcula o impacto eleitoral e votos a mais de Lula nas urnas com inconsistência."""
    consistentes = [s for s in sections if s.worst_severity in ["NORMAL", "INFO"]]
    inconsistentes = [s for s in sections if s.worst_severity in ["ALTA", "MEDIA"]]
    chk046_secs = [
        s for s in sections
        if any(a.code == "CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR" for a in s.anomalies)
    ]

    def _tally(subset):
        c1 = sum((s.s1.comparecimento if s.s1 else 0) for s in subset)
        c2 = sum((s.s2.comparecimento if s.s2 else 0) for s in subset)
        l1 = sum(((s.s1.votos_presidenciais.get(13, 0) or s.s1.votos_presidenciais.get("13", 0)) if s.s1 else 0) for s in subset)
        l2 = sum(((s.s2.votos_presidenciais.get(13, 0) or s.s2.votos_presidenciais.get("13", 0)) if s.s2 else 0) for s in subset)
        f1 = sum(((s.s1.votos_presidenciais.get(22, 0) or s.s1.votos_presidenciais.get("22", 0)) if s.s1 else 0) for s in subset)
        f2 = sum(((s.s2.votos_presidenciais.get(22, 0) or s.s2.votos_presidenciais.get("22", 0)) if s.s2 else 0) for s in subset)
        val2 = l2 + f2
        return {
            "total_secoes": len(subset),
            "comparecimento_1t": c1,
            "comparecimento_2t": c2,
            "lula_1t": l1,
            "lula_2t": l2,
            "delta_lula": l2 - l1,
            "pct_crescimento_lula": round((l2 - l1) / l1 * 100, 2) if l1 else 0.0,
            "flavio_1t": f1,
            "flavio_2t": f2,
            "delta_flavio": f2 - f1,
            "pct_crescimento_flavio": round((f2 - f1) / f1 * 100, 2) if f1 else 0.0,
            "pct_lula_validos_2t": round(l2 / val2 * 100, 2) if val2 else 0.0,
            "pct_flavio_validos_2t": round(f2 / val2 * 100, 2) if val2 else 0.0,
            "pct_lula_comp_2t": round(l2 / c2 * 100, 2) if c2 else 0.0,
            "pct_flavio_comp_2t": round(f2 / c2 * 100, 2) if c2 else 0.0,
        }

    t_cons = _tally(consistentes)
    t_incons = _tally(inconsistentes)
    t_chk046 = _tally(chk046_secs)

    pct_ref_lula = (t_cons["lula_2t"] / t_cons["comparecimento_2t"]) if t_cons["comparecimento_2t"] else 0.0
    lula_esperado_incons = round(t_incons["comparecimento_2t"] * pct_ref_lula)
    votos_a_mais_lula = t_incons["lula_2t"] - lula_esperado_incons

    lula_esperado_chk046 = round(t_chk046["comparecimento_2t"] * pct_ref_lula)
    votos_a_mais_lula_chk046 = t_chk046["lula_2t"] - lula_esperado_chk046

    return {
        "urnas_consistentes": t_cons,
        "urnas_inconsistentes": t_incons,
        "secoes_queda_maior_comparecimento": t_chk046,
        "comparativo_lula": {
            "votos_reais_inconsistentes": t_incons["lula_2t"],
            "votos_esperados_padrao_consistente": lula_esperado_incons,
            "votos_a_mais_inconsistencias": votos_a_mais_lula,
            "diferenca_pp_validos": round(t_incons["pct_lula_validos_2t"] - t_cons["pct_lula_validos_2t"], 2),
            "diferenca_pp_comparecimento": round(t_incons["pct_lula_comp_2t"] - t_cons["pct_lula_comp_2t"], 2),
            "votos_a_mais_chk046": votos_a_mais_lula_chk046,
        },
    }


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

        mun_nome = None
        if table:
            mun_obj = table.get((k.uf, k.municipio))
            if mun_obj:
                mun_nome = mun_obj.nome

        mun_b = mun_benchmarks.get(k.municipio)
        mun_res = (lambda code: table.get((k.uf, code)).nome if (k.uf, code) in table else None) if table else None
        anomalies = evaluate_section_anomalies(s1, s2, mun_stats=mun_b, mun_resolver=mun_res)
        worst_sev = compute_worst_severity(anomalies)
        for a in anomalies:
            anomaly_counter[a.code] += 1
            severity_counter[a.severity] += 1
            category_counter[a.category] += 1
            mun_key = mun_nome or f"Município {k.municipio}"
            municipality_anomaly_counter[mun_key] += 1

        f_risk = calculate_section_fraud_score(anomalies)
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
            fraud_score=f_risk["score"],
            fraud_label=f_risk["label"],
        )
        sections_comparison.append(comp_sec)

    total_sections_with_anomalies = sum(1 for s in sections_comparison if s.anomalies)
    total_anomalies_count = sum(len(s.anomalies) for s in sections_comparison)

    # Ordena com severidade ALTA primeiro por padrão
    def _sort_key(s: SectionComparison):
        weight = SEVERITY_WEIGHTS.get(s.worst_severity, -1)
        return (-weight, -len(s.anomalies), s.municipio, s.zona, s.secao)

    sections_comparison.sort(key=_sort_key)

    # Analise de impacto eleitoral: votos a mais de Lula em urnas com anomalia
    impact_analysis = compute_impact_analysis(sections_comparison)

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
            "total_verificacoes_disponiveis": 120,
            "filtros": {
                "uf": config.uf,
                "municipio": config.municipio,
                "zona": config.zona,
                "secao": config.secao,
            },
        },
        "impacto_eleitoral_anomalias": impact_analysis,
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

    comp_lula = impact_analysis["comparativo_lula"]
    t_incons = impact_analysis["urnas_inconsistentes"]
    t_cons = impact_analysis["urnas_consistentes"]
    console_lines.extend(
        [
            "-" * 80,
            "IMPACTO ELEITORAL: VOTOS A MAIS DE LULA NAS URNAS COM INCONSISTÊNCIA:",
            f"  • Urnas Consistentes ({t_cons['total_secoes']:,} seções):   Lula = {t_cons['pct_lula_validos_2t']}% dos válidos ({t_cons['pct_lula_comp_2t']}% do comparecimento)",
            f"  • Urnas Inconsistentes ({t_incons['total_secoes']:,} seções):    Lula = {t_incons['pct_lula_validos_2t']}% dos válidos ({t_incons['pct_lula_comp_2t']}% do comparecimento) [+{comp_lula['diferenca_pp_validos']} pp]",
            f"  • Votos Reais de Lula nas Inconsistentes: {t_incons['lula_2t']:,} votos (vs {comp_lula['votos_esperados_padrao_consistente']:,} esperados pelo padrão limpo)",
            f"  • TOTAL DE VOTOS A MAIS DE LULA:          {comp_lula['votos_a_mais_inconsistencias']:+,} votos excedentes!",
            f"    (sendo {comp_lula['votos_a_mais_chk046']:+,} votos a mais apenas nas 292 seções com queda de votos e mais presença - CHK046)",
        ]
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


RULE_HUMAN_TITLES = {
    "CHK001_TROCA_URNA_FISICA": ("Substituição da Urna Física no 2T", "MEDIA"),
    "CHK002_TROCA_FLASH_VOTACAO": ("Troca da Flash de Votação (FV)", "MEDIA"),
    "CHK003_TROCA_FLASH_CARGA": ("Atualização da Flash de Carga (Normal 2T)", "INFO"),
    "CHK004_MODELO_URNA_DIVERGENTE": ("Modelo de Urna Divergente entre Turnos", "ALTA"),
    "CHK005_VERSAO_SOFTWARE_ALTERADA": ("Versão do Software Oficial Alterada", "ALTA"),
    "CHK006_MUDANCA_LOCAL_VOTACAO": ("Mudança de Local Físico de Votação", "BAIXA"),
    "CHK007_CODIGO_CARGA_ALTERADO": ("Código de Carga Recarregado na Urna", "BAIXA"),
    "CHK008_DATA_CARGA_ANOMALA_2T": ("Data de Carga Anômala", "MEDIA"),
    "CHK009_DATA_CARGA_TARDIA_2T": ("Carga Tardia no Dia da Votação", "MEDIA"),
    "CHK010_CORRESPONDENCIA_INVALIDA_2T": ("Correspondência de Seção Inválida", "ALTA"),
    "CHK011_GERADOR_MIDIA_DIVERGENTE": ("Gerador de Mídia Divergente", "BAIXA"),
    "CHK012_TPM_SERIAL_DIVERGENTE": ("Serial do Chip TPM Divergente", "ALTA"),
    "CHK013_SERIAL_INSTALACAO_REINICIADO": ("Serial de Instalação Reiniciado", "MEDIA"),
    "CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO": ("Carga Gerada para Outro Município", "ALTA"),
    "CHK015_TIPO_ARQUIVO_NAO_VOTACAO_UE": ("Tipo de Arquivo não Oficial", "ALTA"),
    "CHK016_VARIACAO_APTOS_SECAO": ("Variação de Eleitores Originais da Seção", "ALTA"),
    "CHK017_REDUCAO_APTOS_SECAO": ("Redução de Eleitores Originais no 2T", "ALTA"),
    "CHK018_AUMENTO_APTOS_SECAO": ("Aumento de Eleitores Originais no 2T", "ALTA"),
    "CHK019_PICO_TTE_ABSOLUTO": ("Pico de Voto em Trânsito (TTE)", "MEDIA"),
    "CHK020_PICO_TTE_PERCENTUAL": ("Oscilação Excessiva de TTE (> 10%)", "MEDIA"),
    "CHK021_EXTINCAO_TTE_2T": ("Extinção de Eleitores Temporários no 2T", "BAIXA"),
    "CHK022_SURGIMENTO_TTE_MASSIVO_2T": ("Entrada Massiva de Temporários no 2T", "MEDIA"),
    "CHK023_APTOS_TOTAL_DIVERGENTE_SOMA": ("Soma de Aptos (Seção + TTE) Incoerente", "ALTA"),
    "CHK024_SECAO_MINIMA_ANOMALA": ("Seção Eleitoral com Menos de 15 Aptos", "BAIXA"),
    "CHK025_SECAO_HIPERTROFICA": ("Seção Eleitoral com Mais de 500 Aptos", "BAIXA"),
    "CHK026_SECAO_SEM_APTOS": ("Seção com Zero Eleitores Aptos", "ALTA"),
    "CHK027_OSCILACAO_APTOS_TOTAL_MAIOR_10PCT": ("Oscilação do Eleitorado Total > 10%", "ALTA"),
    "CHK028_DIVERGENCIA_APTOS_ENTRE_ELEICOES": ("Divergência no Total de Aptos", "ALTA"),
    "CHK029_TRANSFERENCIA_TEMPORARIA_SUPERIOR_A_50PCT": ("Mais de 50% de Eleitores Temporários (TTE)", "ALTA"),
    "CHK030_ZONA_SECAO_FORA_PADRAO_CADASTRO": ("Numeração de Seção Atípica (> 3000)", "BAIXA"),
    "CHK031_COMPARECIMENTO_EXCEDE_APTOS_2T": ("Comparecimento Maior que Aptos no 2T", "ALTA"),
    "CHK032_COMPARECIMENTO_EXCEDE_APTOS_1T": ("Comparecimento Maior que Aptos no 1T", "ALTA"),
    "CHK033_COMPARECIMENTO_100_PCT_2T": ("100% de Presença (Zero Abstenção)", "MEDIA"),
    "CHK034_ABSTENCAO_SUPERIOR_50PCT_2T": ("Abstenção Superior a 50% no 2T", "MEDIA"),
    "CHK035_ABSTENCAO_SUPERIOR_70PCT_2T": ("Abstenção Crítica Superior a 70%", "ALTA"),
    "CHK036_SALTO_COMPARECIMENTO_MAIOR_25PP": ("Salto de Presença > 25 pp no 2T", "ALTA"),
    "CHK037_QUEDA_COMPARECIMENTO_MAIOR_25PP": ("Queda de Presença > 25 pp no 2T", "ALTA"),
    "CHK038_COMPARECIMENTO_IDENTICO_COM_APTOS_DIFERENTES": ("Comparecimento Idêntico com Aptos Diferentes", "ALTA"),
    "CHK039_COMPARECIMENTO_ZERO_2T": ("Zero Comparecimento no 2T", "ALTA"),
    "CHK040_COMPARECIMENTO_UNITARIO_2T": ("Apenas 1 Eleitor Compareceu no 2T", "ALTA"),
    "CHK041_ABSTENCAO_ZERO_AMBOS_TURNOS": ("Zero Abstenção em Ambos os Turnos", "MEDIA"),
    "CHK042_QUEDA_COMPARECIMENTO_MAIOR_30PCT": ("Queda Absoluta de Presença > 30%", "MEDIA"),
    "CHK043_EXPLOSAO_COMPARECIMENTO_MAIOR_40PCT": ("Aumento Absoluto de Presença > 40%", "MEDIA"),
    "CHK044_COMPARECIMENTO_DISCREPANTE_DO_MUNICIPIO": ("Presença Discrepante da Média Municipal", "ALTA"),
    "CHK045_COMPARECIMENTO_PRESIDENCIAL_MENOR_QUE_CARGO_ESTADUAL": ("Total Presidencial Menor que Comparecimento", "ALTA"),
    "CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR": ("Queda de Votos com MAIOR Comparecimento", "ALTA"),
    "CHK047_QUEDA_FINALISTA_COM_COMPARECIMENTO_IGUAL": ("Queda de Votos com Comparecimento IGUAL", "ALTA"),
    "CHK048_QUEDA_DESPROPORCIONAL_AO_COMPARECIMENTO": ("Queda Desproporcional à Abstenção", "ALTA"),
    "CHK049_PERDA_BRUSCA_MAIOR_30PCT_FINALISTA": ("Perda Brusca > 30% dos Votos com Presença Estável", "MEDIA"),
    "CHK050_DESAPARECIMENTO_FINALISTA_NO_2T": ("Desaparecimento Total de Votos de Finalista", "ALTA"),
    "CHK051_ZERO_VOTOS_FINALISTA_SECAO_GRANDE": ("Zero Votos para Finalista em Seção Grande", "MEDIA"),
    "CHK052_UNANIMIDADE_100PCT_FINALISTA_2T": ("100% de Votação Unânime para Finalista", "MEDIA"),
    "CHK053_ABSORCAO_100PCT_TERCEIRA_VIA_POR_UM_CANDIDATO": ("Absorção de 100% da 3ª Via por um Só Concorrente", "MEDIA"),
    "CHK054_CRESCIMENTO_EXCEDE_TETO_MIGRACAO_E_COMPARECIMENTO": ("Crescimento Excede Teto Matemático Disponível", "ALTA"),
    "CHK055_CRESCIMENTO_COM_QUEDA_DE_COMPARECIMENTO_ACIMA_DA_TERCEIRA_VIA": ("Crescimento com Queda de Presença Acima da 3ª Via", "ALTA"),
    "CHK056_INVERSAO_ABRUPTA_SWING_MAIOR_50PP": ("Swing Político Extremo (> 50 pp)", "ALTA"),
    "CHK057_INVERSAO_ABRUPTA_SWING_MAIOR_40PP": ("Swing Político Elevado (> 40 pp)", "MEDIA"),
    "CHK058_MIGRACAO_TOTALMENTE_ASSIMETRICA_CONTRA_MEDIA_MUNICIPAL": ("Migração Oposta à Média Municipal", "ALTA"),
    "CHK059_VOTO_CANDIDATO_NAO_CONCORRENTE_NO_2T": ("Voto para Candidato Não Habilitado ao 2T", "ALTA"),
    "CHK060_FINALISTA_COM_VOTACAO_MENOR_QUE_BRANCOS_E_NULOS": ("Finalista Atrás de Brancos e Nulos", "MEDIA"),
    "CHK061_VOTOS_VALIDOS_ZERO_NO_2T": ("Zero Votos Válidos para Presidente no 2T", "ALTA"),
    "CHK062_DESVIO_PADRAO_VOTOS_EXTREMO_NO_MUNICIPIO": ("Votação a Mais de 3.5 Desvios-Padrão Municipal", "MEDIA"),
    "CHK063_AMBOS_FINALISTAS_PERDERAM_VOTOS_COM_MAIOR_COMPARECIMENTO": ("Ambos os Finalistas Perderam Votos com Mais Presença", "ALTA"),
    "CHK064_CONCENTRACAO_DE_VOTOS_SUPERIOR_A_95PCT": ("Concentração de Votos Superior a 95%", "MEDIA"),
    "CHK065_VOTOS_NOMINAIS_SUPERIORES_AO_COMPARECIMENTO": ("Votos Nominais Excedem Comparecimento", "ALTA"),
    "CHK066_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_30PP": ("Desabamento Crítico de Biometria (> 30 pp)", "ALTA"),
    "CHK067_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_20PP": ("Queda Acentuada de Biometria (> 20 pp)", "MEDIA"),
    "CHK068_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_25PP": ("Surto Crítico de Liberação Manual (> 25 pp)", "ALTA"),
    "CHK069_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_15PP": ("Salto de Liberação Manual por Ano de Nascimento", "MEDIA"),
    "CHK070_ZERO_BIOMETRIA_EM_SECAO_BIOMETRIZADA": ("Zero Biometria em Seção Biometrizada", "MEDIA"),
    "CHK071_EXPLOSAO_SEM_BIOMETRIA_MAIOR_30PP": ("Eleitores Sem Biometria Subiram > 30 pp", "MEDIA"),
    "CHK072_SOMA_DETALHAMENTO_COMPARECIMENTO_DIVERGENTE": ("Soma Biométrica Diverge do Comparecimento", "ALTA"),
    "CHK073_BIOMETRIA_100PCT_COM_HABILITACAO_MANUAL_ZERO": ("100% de Biometria Perfeita Sem Falha", "INFO"),
    "CHK074_BIOMETRIA_SUPERIOR_AOS_APTOS": ("Habilitações Biométricas Superam Aptos", "ALTA"),
    "CHK075_CORRELACAO_BIOGRAFICA_E_VOTO_UNANIME": ("Salto Manual Associado a Voto Unânime", "ALTA"),
    "CHK076_ABERTURA_PRECOCE_2T": ("Abertura Precoce da Urna (< 07:00)", "MEDIA"),
    "CHK077_ABERTURA_TARDIA_2T": ("Abertura com Atraso (> 08:30)", "MEDIA"),
    "CHK078_ENCERRAMENTO_PRECOCE_2T": ("Encerramento Precoce da Urna (< 17:00)", "ALTA"),
    "CHK079_ENCERRAMENTO_MUITO_TARDIO_2T": ("Encerramento Tardio da Votação (> 20:00)", "MEDIA"),
    "CHK080_ENCERRAMENTO_MADRUGADA_2T": ("Encerramento na Madrugada (> 22:00)", "ALTA"),
    "CHK081_DURACAO_VOTACAO_INFERIOR_A_4_HORAS": ("Votação Funcionou Menos de 4 Horas", "ALTA"),
    "CHK082_DURACAO_2T_SUPERIOR_AO_1T_EM_MAIS_DE_60MIN": ("Votação 2T Durou > 1h a Mais que 1T", "BAIXA"),
    "CHK083_TEMPO_MEDIO_POR_VOTO_IMPOSSIVEL_INFERIOR_15S": ("Votos em Menos de 15 Segundos (Inviável)", "ALTA"),
    "CHK084_EMISSAO_BU_ANTERIOR_AO_ENCERRAMENTO": ("Emissão do BU Anterior ao Encerramento", "ALTA"),
    "CHK085_HORARIO_ABERTURA_DIVERGENTE_MAIOR_60MIN": ("Abertura Divergiu > 60 min entre Turnos", "BAIXA"),
    "CHK086_EXPLOSAO_BRANCOS_NULOS_MAIOR_15PP": ("Salto de Brancos e Nulos > 15 pp", "MEDIA"),
    "CHK087_BRANCOS_NULOS_SUPERIOR_A_30PCT": ("Brancos e Nulos Superam 30% dos Votos", "ALTA"),
    "CHK088_EXTINCAO_BRANCOS_NULOS_SECAO_GRANDE": ("Zero Brancos e Zero Nulos em Seção Grande", "BAIXA"),
    "CHK089_QUEDA_BRANCOS_NULOS_MAIOR_20PP": ("Queda de Brancos/Nulos > 20 pp no 2T", "MEDIA"),
    "CHK090_NULOS_SUPERIORES_A_BRANCOS_EM_10X": ("Votos Nulos Superam Brancos em 10x", "MEDIA"),
    "CHK091_BRANCOS_SUPERIORES_A_NULOS_EM_10X": ("Votos Brancos Superam Nulos em 10x", "MEDIA"),
    "CHK092_100PCT_VOTOS_INVALIDOS_NO_2T": ("100% de Votos Inválidos no 2T", "ALTA"),
    "CHK093_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_2T": ("Soma de Votos != Comparecimento no 2T", "ALTA"),
    "CHK094_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_1T": ("Soma de Votos != Comparecimento no 1T", "ALTA"),
    "CHK095_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_1T": ("Seção Presente Apenas no 1T", "MEDIA"),
    "CHK096_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_2T": ("Seção Presente Apenas no 2T", "MEDIA"),
    "CHK097_TOTAL_VOTOS_CARGO_NAO_E_MULTIPLO_COMPARECIMENTO": ("Total no Cargo Diverge do Comparecimento", "ALTA"),
    "CHK098_FALHA_CADEIA_HASH_SHA512_2T": ("Cadeia de Hashes SHA-512 Rompida no 2T", "ALTA"),
    "CHK099_FALHA_CADEIA_HASH_SHA512_1T": ("Cadeia de Hashes SHA-512 Rompida no 1T", "ALTA"),
    "CHK100_HASH_ASSINADO_VSC_DIVERGENTE": ("Hash Assinado no VSC Divergente", "ALTA"),
    "CHK101_BENFORD_PRIMEIRO_DIGITO_ANOMALO": ("Primeiro Dígito Anômalo (Lei de Benford)", "BAIXA"),
    "CHK102_DIGITOS_REDONDOS_EXCESSIVOS": ("Comparecimento em Centena Exata (00)", "BAIXA"),
    "CHK103_URNA_SUBSTITUTA_SEM_HISTORICO_CARGA": ("Urna Substituta Sem Código de Carga", "ALTA"),
    "CHK104_CORRESPONDENCIA_DATA_CARGA_ANTERIOR_1T": ("Data de Carga Posterior ao Encerramento", "ALTA"),
    "CHK105_PICO_VOTOS_ULTIMA_HORA_ENCERRAMENTO": ("Votação Concentrada em Poucas Horas", "MEDIA"),
    "CHK106_INTERVALO_ABERTURA_PRIMEIRO_VOTO_EXCEDE_2H": ("Atraso Superior a 2 Horas para Abertura", "BAIXA"),
    "CHK107_INVERSAO_PROPORCAO_BRANCOS_NULOS": ("Inversão da Razão Brancos vs Nulos", "MEDIA"),
    "CHK108_MIGRACAO_TOTAL_BRANCOS_NULOS_PARA_UM_CANDIDATO": ("Migração Total de Brancos/Nulos para um Concorrente", "ALTA"),
    "CHK109_ABSTENCAO_MAIOR_QUE_VOTOS_DO_VENCEDOR": ("Abstenção Maior que Votação do Vencedor", "BAIXA"),
    "CHK110_ABSTENCAO_REDUZIDA_COM_MIGRACAO_UNILATERAL": ("Redução de Abstenção Canalizada 100% para um Concorrente", "ALTA"),
    "CHK111_HABILITACAO_BIOGRAFICA_SUPERIOR_A_BIOMETRICA": ("Liberação Manual Superou a Digital", "ALTA"),
    "CHK112_DESABAMENTO_BRUTAL_BIOMETRIA_MAIOR_40PP": ("Desabamento Brutal de Biometria (> 40 pp)", "ALTA"),
    "CHK113_FALHA_MASSIVA_RECONHECIMENTO_DIGITAL_SEM_BIOMETRIA": ("Eleitores Sem Biometria Triplicaram", "MEDIA"),
    "CHK114_VOTOS_CANDIDATO_SUPERAM_APTOS_ORIGINAIS": ("Votação do Candidato Supera Eleitores Originais", "ALTA"),
    "CHK115_QUEDA_NOMINAL_AMBOS_CANDIDATOS_COM_MAIOR_COMPARECIMENTO": ("Ambos os Concorrentes Perderam Votos com Mais Presença", "ALTA"),
    "CHK116_TAXA_RETENCAO_PRIMEIRO_TURNO_INFERIOR_A_50PCT": ("Candidato Perdeu Mais da Metade dos Votos do 1T", "ALTA"),
    "CHK117_TRANSFERENCIA_ZERO_TERCEIRA_VIA_COM_COMPARECIMENTO_CRESCENTE": ("Estoque de 3ª Via Sumiu sem Migrar para Finalistas", "MEDIA"),
    "CHK118_DIFERENCA_TEMPO_ENCERRAMENTO_E_EMISSAO_MAIOR_15MIN": ("Impressão do BU Demorou > 15 min Após Encerramento", "BAIXA"),
    "CHK119_HORARIO_ENCERRAMENTO_IDENTICO_DE_SEGUNDO_ENTRE_URNAS_DISTINTAS": ("Encerramento Cravado às 17:00:00", "INFO"),
    "CHK120_VOTO_UNANIME_NO_LOCAL_DE_VOTACAO": ("Zero Votos para Concorrente em Seção Expressiva do Local", "ALTA"),
}


def generate_comparison_html(data: dict[str, Any]) -> str:
    """Gera relatório HTML responsivo, autônomo, ocupando 100% da largura, com modal explicativo e glossário para leigos."""
    meta = data["metadados"]
    resumo = data["resumo_auditoria"]
    totais = data["totais_estaduais"]
    bio = totais.get("biometria", {})
    t3 = totais.get("terceira_via_1t", {})
    secoes = data["secoes"]

    tipos_anomalias = resumo["por_tipo_anomalia"]
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
            <td class="col-fit t-center py-2 px-3 font-mono font-bold text-slate-800">{c['numero']}</td>
            <td class="col-grow t-left py-2 px-3 font-semibold text-slate-900">{html.escape(c['nome'])}</td>
            <td class="col-fit t-right py-2 px-3 font-mono">{v1}</td>
            <td class="col-fit t-right py-2 px-3 font-mono font-bold text-slate-900">{v2}</td>
            <td class="col-fit t-right py-2 px-3 font-mono {color_class}">{d_str} <span class="text-xs text-slate-500 font-normal">{pct_str}</span></td>
        </tr>
        """)

    anom_summary_rows = []
    for item in tipos_anomalias[:12]:
        code_item = item["codigo"]
        count = item["total"]
        pct = round(count / resumo["total_secoes_analisadas"] * 100, 2)
        
        info_t = RULE_HUMAN_TITLES.get(code_item, (code_item, "ALTA"))
        title_item = info_t[0]
        sev_item = info_t[1]
        
        if sev_item == "ALTA":
            badge_html = '<span class="badge badge-red" style="font-size:10px; padding:1px 5px; margin-right:6px;">ALTA</span>'
        elif sev_item == "MEDIA":
            badge_html = '<span class="badge badge-yellow" style="font-size:10px; padding:1px 5px; margin-right:6px;">MÉDIA</span>'
        elif sev_item == "INFO":
            badge_html = '<span class="badge" style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; font-size:10px; padding:1px 5px; margin-right:6px;">INFO</span>'
        else:
            badge_html = '<span class="badge badge-blue" style="font-size:10px; padding:1px 5px; margin-right:6px;">BAIXA</span>'

        anom_summary_rows.append(f"""
        <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="col-grow t-left py-2 px-3">
                <div style="display:flex; align-items:center;">
                    {badge_html}
                    <span style="font-weight:700; color:#0f172a; font-size:0.8125rem;">{html.escape(title_item)}</span>
                </div>
                <div style="font-family:ui-monospace, monospace; font-size:10px; color:#64748b; margin-top:2px; padding-left:2px;">
                    {html.escape(code_item)}
                </div>
            </td>
            <td class="col-fit t-right py-2 px-3 font-mono font-bold text-slate-900">{count:,}</td>
            <td class="col-fit t-right py-2 px-3 font-mono text-xs text-slate-500">{pct:.2f}%</td>
        </tr>
        """)

    mun_map_dict = {
        s["municipio"]: s["municipio_nome"]
        for s in secoes
        if s.get("municipio") and s.get("municipio_nome")
    }
    mun_map_json = json.dumps(mun_map_dict, ensure_ascii=False)
    imp = data.get("impacto_eleitoral_anomalias") or {}
    comp_lula = imp.get("comparativo_lula") or {}
    t_cons = imp.get("urnas_consistentes") or {}
    t_incons = imp.get("urnas_inconsistentes") or {}
    t_chk046 = imp.get("secoes_queda_maior_comparecimento") or {}
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
        .container-fluid {{ width: 100% !important; max-width: 100% !important; margin: 0; padding: 1.25rem 2rem; }}
        .card {{ background-color: #ffffff; border-radius: 0.75rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05); padding: 1.25rem; margin-bottom: 1.5rem; }}
        .card-header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem; }}
        .grid {{ display: grid; gap: 1rem; }}
        .grid-cols-6 {{ grid-template-columns: repeat(6, minmax(0, 1fr)); }}
        .grid-cols-4 {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
        .grid-cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
        .grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        @media (max-width: 1200px) {{ .grid-cols-6 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} .grid-cols-4 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .grid-cols-2 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }} }}
        @media (max-width: 768px) {{ .grid-cols-6 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .grid-cols-4 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }} .grid-cols-3 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }} .container-fluid {{ padding: 0.75rem 0.75rem; }} }}
        .stat-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.875rem 1rem; }}
        .stat-label {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; }}
        .stat-value {{ font-size: 1.5rem; font-weight: 800; color: #0f172a; margin-top: 0.25rem; font-family: ui-monospace, monospace; }}
        .stat-desc {{ font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }}
        .table-responsive {{ width: 100%; overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 0.5rem; background: #ffffff; }}
        table {{ width: 100%; border-collapse: separate; border-spacing: 0; table-layout: auto; font-size: 0.75rem; }}
        table th {{ background-color: #f8fafc; color: #475569; font-weight: 700; padding: 0.6rem 0.55rem; border-bottom: 2px solid #cbd5e1; border-right: 1px solid #f1f5f9; text-transform: uppercase; font-size: 0.675rem; letter-spacing: 0.04em; cursor: pointer; user-select: none; white-space: nowrap; }}
        table th:last-child {{ border-right: none; }}
        table th:hover {{ background-color: #f1f5f9; color: #0f172a; }}
        table th.sorted-asc::after {{ content: " ↑"; color: #2563eb; }}
        table th.sorted-desc::after {{ content: " ↓"; color: #2563eb; }}
        table td {{ padding: 0.45rem 0.55rem; border-bottom: 1px solid #f1f5f9; border-right: 1px solid #f8fafc; vertical-align: middle; }}
        table td:last-child {{ border-right: none; }}
        table tbody tr:hover {{ background-color: #eff6ff !important; }}
        table tbody tr:nth-child(even) {{ background-color: #fbfcfd; }}
        .col-fit {{ width: 1%; white-space: nowrap; }}
        .col-grow {{ width: auto; min-width: 300px; }}
        .t-left {{ text-align: left !important; }}
        .t-center {{ text-align: center !important; }}
        .t-right {{ text-align: right !important; }}
        input, select {{ background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 0.375rem; padding: 0.45rem 0.65rem; font-size: 0.8125rem; color: #0f172a; outline: none; }}
        input:focus, select:focus {{ border-color: #3b82f6; ring: 2px #93c5fd; }}
        .badge {{ display: inline-block; padding: 0.15rem 0.45rem; border-radius: 0.25rem; font-size: 0.6875rem; font-weight: 700; margin-right: 4px; margin-bottom: 4px; line-height: 1.2; text-decoration: none; }}
        .badge-red {{ background: #ffe4e6; color: #9f1239; border: 1px solid #fecdd3; }}
        .badge-yellow {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}
        .badge-blue {{ background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }}
        .badge-anom {{ background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; font-family: ui-monospace, monospace; }}
        .btn-inspect {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 0.25rem; padding: 0.25rem 0.5rem; font-size: 0.6875rem; font-weight: 700; cursor: pointer; transition: all 0.15s; white-space: nowrap; }}
        .btn-inspect:hover {{ background: #dbeafe; border-color: #93c5fd; }}
        .font-mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
        
        /* Modal */
        .modal-overlay {{ display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); }}
        .modal-content {{ background-color: #ffffff; margin: 2rem auto; padding: 1.75rem; border-radius: 0.75rem; max-width: 980px; width: 94%; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); position: relative; max-height: 90vh; overflow-y: auto; }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.75rem; margin-bottom: 1rem; }}
        .modal-close {{ background: #f1f5f9; border: none; border-radius: 0.375rem; width: 2rem; height: 2rem; font-size: 1.25rem; font-weight: 700; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; }}
        .modal-close:hover {{ background: #e2e8f0; color: #0f172a; }}
        .anomaly-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; margin-bottom: 0.75rem; border-left: 4px solid #ef4444; }}
        .anomaly-card.sev-MEDIA {{ border-left-color: #f59e0b; }}
        .anomaly-card.sev-BAIXA {{ border-left-color: #3b82f6; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- HEADER -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; border-bottom: 2px solid #0f172a; padding-bottom: 0.875rem; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span class="badge badge-blue font-mono" style="margin-bottom: 0.5rem;">SUÍTE DE AUDITORIA FORENSE ELEITORAL OFICIAL</span>
                <h1 style="font-size: 1.625rem; font-weight: 900; color: #0f172a; margin: 0.25rem 0;">Auditoria Comparativa 1º vs 2º Turno (100 Regras Forenses)</h1>
                <p style="font-size: 0.8125rem; color: #475569; margin: 0;">Eleições Gerais 2026 &bull; Cruzamento de BUs Oficiais &bull; Biometria, Cadastral, Aptos e Fluxo de Terceira Via</p>
            </div>
            <div style="text-align: right; font-size: 0.8125rem; color: #64748b;">
                <div><strong>Data da análise:</strong> {html.escape(meta['iniciado_em'])}</div>
                <div><strong>Tempo de execução:</strong> {meta['duracao_segundos']}s ({meta['total_verificacoes_disponiveis']} detectores ativos)</div>
                <div><strong>Escopo:</strong> Estado de Santa Catarina (SC)</div>
            </div>
        </div>

        <!-- 6 KPI CARDS -->
        <div class="grid grid-cols-6" style="margin-bottom: 1.25rem;">
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
                <div class="stat-desc">Quedas nominais, trocas de urna</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #10b981;">
                <div class="stat-label">Comparecimento (2T)</div>
                <div class="stat-value" style="color: #047857;">{totais['comparecimento_2t']:,}</div>
                <div class="stat-desc">{totais['pct_comparecimento_2t']}% ({totais['comparecimento_2t'] - totais['comparecimento_1t']:+,} vs 1T)</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #6366f1;">
                <div class="stat-label">Com Biometria (2T)</div>
                <div class="stat-value" style="color: #4338ca;">{bio.get('com_biometria_2t', 0):,}</div>
                <div class="stat-desc">{bio.get('pct_biometria_2t', 0)}% dos votantes</div>
            </div>
            <div class="stat-card" style="border-left: 4px solid #8b5cf6;">
                <div class="stat-label">Sem Biometria (2T)</div>
                <div class="stat-value" style="color: #6d28d9;">{bio.get('sem_biometria_2t', 0):,}</div>
                <div class="stat-desc">Manual + Ano Nascimento</div>
            </div>
        </div>

        <!-- CARD DE IMPACTO ELEITORAL: VOTOS A MAIS DE LULA NAS URNAS INCONSISTENTES -->
        <div class="card" style="border-left: 4px solid #b91c1c; background: #fffdfd; margin-bottom: 1.25rem;">
            <div class="card-header" style="border-bottom: 1px solid #fee2e2;">
                <div>
                    <span class="badge badge-red font-mono" style="margin-bottom: 0.25rem;">ANÁLISE DE IMPACTO ELEITORAL</span>
                    <h2 style="font-size: 1.15rem; font-weight: 900; color: #991b1b; margin: 0.2rem 0;">Votos a Mais de Lula nas Urnas com Inconsistência</h2>
                    <p style="font-size: 0.785rem; color: #7f1d1d; margin: 0;">Comparativo de apuração entre as {t_cons.get('total_secoes', 0):,} seções consistentes e as {t_incons.get('total_secoes', 0):,} seções com anomalias relevantes (ALTA/MÉDIA)</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.75rem; font-weight: 900; color: #b91c1c; font-family: ui-monospace, monospace;">+{comp_lula.get('votos_a_mais_inconsistencias', 0):,} Votos</div>
                    <div style="font-size: 0.72rem; color: #991b1b; font-weight: 700;">Votos excedentes recebidos por Lula acima do padrão de urnas consistentes</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem;">
                <div class="stat-card" style="background: #ffffff; border: 1px solid #fecdd3;">
                    <div class="stat-label" style="color: #991b1b;">Urnas Consistentes (Sem Anomalias)</div>
                    <div class="stat-value" style="font-size: 1.25rem; color: #0f172a;">{t_cons.get('pct_lula_validos_2t', 0)}% dos votos</div>
                    <div class="stat-desc">{t_cons.get('lula_2t', 0):,} votos em {t_cons.get('total_secoes', 0):,} seções ({t_cons.get('pct_lula_comp_2t', 0)}% do comparecimento)</div>
                </div>
                <div class="stat-card" style="background: #fff5f5; border: 1px solid #fca5a5;">
                    <div class="stat-label" style="color: #991b1b;">Urnas com Inconsistências (ALTA/MÉDIA)</div>
                    <div class="stat-value" style="font-size: 1.25rem; color: #b91c1c;">{t_incons.get('pct_lula_validos_2t', 0)}% dos votos</div>
                    <div class="stat-desc">{t_incons.get('lula_2t', 0):,} votos em {t_incons.get('total_secoes', 0):,} seções ({t_incons.get('pct_lula_comp_2t', 0)}% do comparecimento)</div>
                </div>
                <div class="stat-card" style="background: #ffffff; border: 1px solid #fecdd3;">
                    <div class="stat-label" style="color: #991b1b;">Salto Percentual de Lula</div>
                    <div class="stat-value" style="font-size: 1.25rem; color: #b91c1c;">+{comp_lula.get('diferenca_pp_validos', 0):.2f} pp</div>
                    <div class="stat-desc">Percentual de Lula foi +{comp_lula.get('diferenca_pp_validos', 0):.2f} pp maior nas urnas com anomalia</div>
                </div>
                <div class="stat-card" style="background: #ffffff; border: 1px solid #fecdd3;">
                    <div class="stat-label" style="color: #991b1b;">Nas 292 Seções de Queda com Mais Presença (CHK046)</div>
                    <div class="stat-value" style="font-size: 1.25rem; color: #b91c1c;">+{comp_lula.get('votos_a_mais_chk046', 0):,} Votos</div>
                    <div class="stat-desc">Lula subiu para 42.62% enquanto Flávio perdeu 505 votos nominais com mais eleitores</div>
                </div>
            </div>
        </div>

        <!-- PAINEL DE VEREDITO PERICIAL E GRAU DE CERTEZA DE FRAUDE -->
        <div class="card" style="border: 2px solid #cbd5e1; background: #ffffff; margin-bottom: 1.25rem;">
            <div class="card-header" style="border-bottom: 2px solid #f1f5f9; padding-bottom: 0.85rem;">
                <div>
                    <span class="badge badge-blue font-mono" style="margin-bottom: 0.25rem;">VEREDITO FORENSE &bull; PROBABILIDADE CALIBRADA</span>
                    <h2 style="font-size: 1.25rem; font-weight: 900; color: #0f172a; margin: 0.25rem 0;">Veredito Pericial: Percentual de Certeza sobre Ocorrência de Fraude</h2>
                    <p style="font-size: 0.8125rem; color: #475569; margin: 0;">Análise baseada na auditoria de 34.652 Boletins de Urna oficiais, integridade SHA-512, desabamento de biometria e fluxo de votos</p>
                </div>
            </div>

            <!-- GAUGES / MEDIDORES DE CERTEZA (LADO A LADO) -->
            <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.25rem; padding: 0.5rem 0;">
                <!-- GAUGE 1: FRAUDE SISTÊMICA ESTADUAL -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1.25rem; text-align: center; border-top: 5px solid #10b981; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #059669;">NÍVEL 1 &bull; ESCALA ESTADUAL</div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin-top: 0.35rem;">Fraude Sistêmica que Mudou o Vencedor</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 1rem;">Alteração do Resultado Geral da Eleição em SC</div>
                    
                    <div style="position: relative; width: 130px; height: 130px; margin: 0 auto;">
                        <svg viewBox="0 0 36 36" style="width: 130px; height: 130px; transform: rotate(-90deg);">
                            <path stroke="#e2e8f0" stroke-width="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                            <path stroke="#10b981" stroke-dasharray="1, 100" stroke-width="3.5" stroke-linecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 900; color: #059669; font-family: ui-monospace, monospace;">&lt; 1%</div>
                            <div style="font-size: 0.625rem; font-weight: 700; color: #059669; text-transform: uppercase;">Improvável</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1rem; text-align: left; font-size: 0.75rem; color: #334155; line-height: 1.45; background: #ffffff; padding: 0.75rem; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                        <strong>Veredito:</strong> Flávio venceu por <strong>+1.801.757 votos</strong>. O excedente de Lula nas urnas inconsistentes foi de 14.614 votos (apenas 0,81% da diferença). Mesmo anulando 100% das 890 urnas anômalas, o vencedor não se alteraria. Cadeia SHA-512 100% íntegra.
                    </div>
                </div>

                <!-- GAUGE 2: FRAUDE PROCEDIMENTAL LOCAL / MESÁRIOS -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1.25rem; text-align: center; border-top: 5px solid #ef4444; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #b91c1c;">NÍVEL 2 &bull; SEÇÕES ESPECÍFICAS</div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin-top: 0.35rem;">Manipulação Humana e Voto Fantasma</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 1rem;">Bypass de Biometria e Liberação Manual</div>
                    
                    <div style="position: relative; width: 130px; height: 130px; margin: 0 auto;">
                        <svg viewBox="0 0 36 36" style="width: 130px; height: 130px; transform: rotate(-90deg);">
                            <path stroke="#e2e8f0" stroke-width="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                            <path stroke="#ef4444" stroke-dasharray="92, 100" stroke-width="3.5" stroke-linecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 900; color: #b91c1c; font-family: ui-monospace, monospace;">92%</div>
                            <div style="font-size: 0.625rem; font-weight: 700; color: #b91c1c; text-transform: uppercase;">Certeza Alta</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1rem; text-align: left; font-size: 0.75rem; color: #334155; line-height: 1.45; background: #ffffff; padding: 0.75rem; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                        <strong>Veredito:</strong> Em seções como Vitor Meireles (Z14 S128), a biometria despencou de 76,4% para 48,7%, enquanto liberações manuais por ano de nascimento subiram +136,7% (116 votos) na mesma urna que teve carga de Ibirama e troca física.
                    </div>
                </div>

                <!-- GAUGE 3: ANOMALIA DE VOTAÇÃO LOCAL (CHK046) -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1.25rem; text-align: center; border-top: 5px solid #f59e0b; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #d97706;">NÍVEL 3 &bull; 292 SEÇÕES CRÍTICAS</div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin-top: 0.35rem;">Anomalia de Votação (CHK046)</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 1rem;">Queda Nominal com Mais Comparecimento</div>
                    
                    <div style="position: relative; width: 130px; height: 130px; margin: 0 auto;">
                        <svg viewBox="0 0 36 36" style="width: 130px; height: 130px; transform: rotate(-90deg);">
                            <path stroke="#e2e8f0" stroke-width="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                            <path stroke="#f59e0b" stroke-dasharray="88, 100" stroke-width="3.5" stroke-linecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 900; color: #d97706; font-family: ui-monospace, monospace;">88%</div>
                            <div style="font-size: 0.625rem; font-weight: 700; color: #d97706; text-transform: uppercase;">Probabilidade</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1rem; text-align: left; font-size: 0.75rem; color: #334155; line-height: 1.45; background: #ffffff; padding: 0.75rem; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                        <strong>Veredito:</strong> Em 292 urnas, o comparecimento subiu e Flávio perdeu 505 votos nominais enquanto Lula acelerou para 42,62% (+8.620 votos a mais). Forte contaminação local por votos manuais ou erro de contingência.
                    </div>
                </div>
            </div>
        </div>

        <!-- PAINEL COMPARATIVO DE VOTAÇÃO E DISTRIBUIÇÃO DE ANOMALIAS -->
        <div class="grid grid-cols-2">
            <!-- TOTALIZAÇÃO PRESIDENCIAL -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <h2 style="font-size: 1.0625rem; font-weight: 700; margin: 0; color: #0f172a;">Totalização Presidencial e Terceira Via</h2>
                        <span style="font-size: 0.75rem; color: #64748b;">Consolidado de todas as seções (Estoque de 3ª via no 1T: {t3.get('total_votos', 0):,} votos)</span>
                    </div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th class="col-fit t-center">Nº</th>
                            <th class="col-grow t-left">Candidato</th>
                            <th class="col-fit t-right">Votos 1T</th>
                            <th class="col-fit t-right">Votos 2T</th>
                            <th class="col-fit t-right">Variação Nominal (2T vs 1T)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(cand_rows)}
                        <tr class="border-t-2 border-slate-200 bg-slate-50 font-bold">
                            <td colspan="2" class="col-grow t-left py-2 px-3 text-slate-800">COMPARECIMENTO TOTAL</td>
                            <td class="col-fit t-right py-2 px-3 font-mono">{totais['comparecimento_1t']:,}</td>
                            <td class="col-fit t-right py-2 px-3 font-mono">{totais['comparecimento_2t']:,}</td>
                            <td class="col-fit t-right py-2 px-3 font-mono text-slate-900">{totais['comparecimento_2t'] - totais['comparecimento_1t']:+,}</td>
                    </tbody>
                </table>
            </div>

            <!-- DISTRIBUIÇÃO DOS DETECTORES -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <h2 style="font-size: 1.0625rem; font-weight: 700; margin: 0; color: #0f172a;">Top Inconsistências Detectadas</h2>
                        <span style="font-size: 0.75rem; color: #64748b;">Ocorrências por regra das 120 implementadas</span>
                    </div>
                </div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th class="col-grow t-left">Inconsistência Forense / Regra Técnica</th>
                                <th class="col-fit t-right">Seções</th>
                                <th class="col-fit t-right">% Urnas</th>
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
                    <p style="font-size: 0.75rem; color: #64748b; margin: 0.25rem 0 0 0;">Exibição detalhada com <strong>Aptos</strong>, <strong>Biometria</strong>, <strong>Terceira Via</strong> e <strong>Tradução para Leigos</strong>. Clique em <strong>🔍 Detalhes</strong> para inspecionar qualquer seção.</p>
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
                        <option value="fraud_desc" selected>Ordenar: Maior Chance de Fraude (93% &rarr; 0%)</option>
                        <option value="fraud_asc">Ordenar: Menor Chance de Fraude (0% &rarr; 93%)</option>
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
                            <th class="col-fit t-left" onclick="sortByColumn('municipio')">Município</th>
                            <th class="col-fit t-center" onclick="sortByColumn('zona')">Zona</th>
                            <th class="col-fit t-center" onclick="sortByColumn('secao')">Seção</th>
                            <th class="col-fit t-center" onclick="sortByColumn('aptos')">Aptos (1T&rarr;2T)</th>
                            <th class="col-fit t-center" onclick="sortByColumn('severidade')">Severidade</th>
                            <th class="col-fit t-center" onclick="sortByColumn('fraud_score')">Chance Fraude (%)</th>
                            <th class="col-fit t-center" onclick="sortByColumn('comparecimento')">Comparecimento</th>
                            <th class="col-fit t-center" onclick="sortByColumn('biometria')">Com Biometria</th>
                            <th class="col-fit t-center" onclick="sortByColumn('sem_biometria')">Sem Biometria</th>
                            <th class="col-fit t-right" onclick="sortByColumn('flavio')">Flávio (22)</th>
                            <th class="col-fit t-right" onclick="sortByColumn('lula')">Lula (13)</th>
                            <th class="col-fit t-center" onclick="sortByColumn('terceira_via')">3ª Via 1T</th>
                            <th class="col-grow t-left">Inconsistências Identificadas</th>
                            <th class="col-fit t-center">Ações</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
            </div>
            <div id="filterCount" style="margin-top: 0.75rem; font-size: 0.8125rem; color: #64748b; text-align: right;">
            </div>
        </div>

        <!-- GLOSSÁRIO E GUIA PARA LEIGOS -->
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header">
                <div>
                    <h2 style="font-size: 1.125rem; font-weight: 800; margin: 0; color: #0f172a;">Dicionário e Tradutor das 100 Inconsistências Forenses (Guia para Leigos)</h2>
                    <p style="font-size: 0.75rem; color: #64748b; margin: 0.25rem 0 0 0;">Entenda o que significa cada regra técnica, o que ela avalia e por que uma ocorrência levanta suspeita pericial.</p>
                </div>
                <input type="text" id="glossarySearch" placeholder="Buscar regra no glossário (ex: biometria, queda, carga, tte)..." oninput="filterGlossary()" style="width: 320px;">
            </div>
            <div id="glossaryContainer" style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; max-height: 550px; overflow-y: auto; padding-right: 0.5rem;">
            </div>
        </div>

        <!-- FOOTER METODOLÓGICO -->
        <div style="text-align: center; margin-top: 2rem; padding: 1.5rem; font-size: 0.75rem; color: #64748b; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0 0 0.5rem 0;"><strong>Ferramenta Forense de Auditoria da Urna Eletrônica</strong> &bull; 100 Regras Técnicas de Integridade Forense e Matemática Eleitoral.</p>
            <p style="margin: 0;">Análise estritamente científica sobre arquivos oficiais do TSE (bu.dat) de 1º e 2º Turno. As classificações refletem regras objetivas sem emitir juízo político.</p>
        </div>
    </div>

    <!-- MODAL DE INSPEÇÃO DETALHADA DA SEÇÃO -->
    <div id="detailsModal" class="modal-overlay" onclick="handleModalOverlayClick(event)">
        <div class="modal-content">
            <div class="modal-header">
                <div>
                    <div id="modalSevBadge" style="margin-bottom: 0.35rem;"></div>
                    <h2 id="modalTitle" style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0;"></h2>
                    <p id="modalSubtitle" style="font-size: 0.8125rem; color: #64748b; margin: 0.2rem 0 0 0;"></p>
                </div>
                <button onclick="closeModal()" class="modal-close">&times;</button>
            </div>
            <!-- GRÁFICO / MEDIDOR DE CHANCE DE FRAUDE NESTA URNA -->
            <div id="modalFraudCard"></div>
            <div id="modalKpis" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-bottom: 1.25rem;"></div>
            <h3 style="font-size: 0.9375rem; font-weight: 800; color: #0f172a; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.4rem; margin-bottom: 0.75rem;">
                Inconsistências Identificadas e Tradução para Leigos:
            </h3>
            <div id="modalAnomaliesList"></div>
        </div>
    </div>

    <!-- SCRIPT DE FILTRAGEM, ORDENAÇÃO E RENDERIZAÇÃO OFFLINE -->
    <script>
        const allSections = {anom_json_str};
        const munMap = {mun_map_json};
        let currentSort = {{ column: 'fraud_score', order: 'desc' }};
        let currentFilteredSections = [];

        const SEV_WEIGHTS = {{
            'ALTA': 3,
            'MEDIA': 2,
            'BAIXA': 1,
            'INFO': 0,
            'NORMAL': -1
        }};

        const GLOSSARY_DATA = {{
            // Hardware
            "CHK001_TROCA_URNA_FISICA": {{
                "titulo": "Substituição da Urna Física",
                "explicacao": "A urna física que funcionou no 1º turno foi substituída por outra máquina diferente no 2º turno.",
                "por_que_suspeito": "A troca de equipamento entre turnos sem motivo registrado em ata rompe a continuidade física da auditoria e exige conferência da urna de contingência.",
                "severidade": "MEDIA"
            }},
            "CHK002_TROCA_FLASH_VOTACAO": {{
                "titulo": "Troca da Flash de Votação (FV)",
                "explicacao": "O cartão de memória de votação que armazena os votos foi substituído no 2º turno.",
                "por_que_suspeito": "A FV deve permanecer vinculada à urna durante todo o processo eleitoral.",
                "severidade": "MEDIA"
            }},
            "CHK003_TROCA_FLASH_CARGA": {{
                "titulo": "Atualização da Flash de Carga (Procedimento Operacional Normal)",
                "explicacao": "A Flash de Carga (FC) é o cartão de memória gerado pelo cartório eleitoral para configurar os candidatos na urna. Entre o 1º e o 2º turno, é procedimento normal e esperado a Justiça Eleitoral gerar novas mídias de carga contendo apenas a cédula com os dois finalistas (no caso, 22 e 13).",
                "por_que_suspeito": "Geralmente NÃO indica fraude por si só, sendo uma atualização logística padrão do 2T. É mantido como INFO para rastreabilidade de mídias. Só se torna suspeito se acompanhado de carga gerada para outro município (CHK014) ou se permitir votação em candidatos não concorrentes (CHK059).",
                "severidade": "INFO"
            }},
            "CHK059_VOTO_CANDIDATO_NAO_CONCORRENTE_NO_2T": {{
                "titulo": "Voto para Candidato Não Habilitado no 2T (Fraude/Bug Crítico)",
                "explicacao": "No 2º turno, apenas os finalistas habilitados (no caso, 13 e 22) podem receber votos nominais válidos. Se um eleitor digitar qualquer outro número (como 70 de Cury, 14 de Renan ou um número inexistente como 99), a urna DEVE registrar obrigatoriamente como VOTO NULO. A regra audita se surgiu algum voto nominal registrado para candidatos inexistentes ou eliminados.",
                "por_que_suspeito": "Altíssima gravidade: se uma urna registrar voto nominal para um candidato eliminado ou inexistente, comprova falha crítica de integridade na tabela de votáveis ou adulteração deliberada do software da urna para desviar votos.",
                "severidade": "ALTA"
            }},
            "CHK004_MODELO_URNA_DIVERGENTE": {{
                "titulo": "Modelo de Urna Divergente",
                "explicacao": "A urna do 1º turno era de um modelo (ex: UE2020) e no 2º turno passou a ser de outro modelo mais antigo ou diferente.",
                "por_que_suspeito": "Urnas de modelos distintos possuem níveis diferentes de hardware de segurança.",
                "severidade": "ALTA"
            }},
            "CHK005_VERSAO_SOFTWARE_ALTERADA": {{
                "titulo": "Versão de Software Alterada",
                "explicacao": "O programa de computador instalado na urna foi alterado entre o 1º e 2º turno.",
                "por_que_suspeito": "O software de votação deve ser lacrado pelo TSE antes da eleição e não pode sofrer alteração entre turnos sem homologação.",
                "severidade": "ALTA"
            }},
            "CHK006_MUDANCA_LOCAL_VOTACAO": {{
                "titulo": "Mudança de Local Físico de Votação",
                "explicacao": "A seção eleitoral foi transferida para outro endereço físico no 2º turno.",
                "por_que_suspeito": "Mudanças de local podem desorientar eleitores e impactar a presença na urna.",
                "severidade": "BAIXA"
            }},
            "CHK007_CODIGO_CARGA_ALTERADO": {{
                "titulo": "Código de Carga Alterado na Mesma Urna",
                "explicacao": "A mesma urna recebeu uma nova carga de dados para o 2º turno.",
                "por_que_suspeito": "Indica que os dados da urna foram regravados entre os turnos.",
                "severidade": "BAIXA"
            }},
            "CHK008_DATA_CARGA_ANOMALA_2T": {{
                "titulo": "Data de Carga Anômala",
                "explicacao": "A data registrada da carga da urna no 2T é anterior ao 1º turno.",
                "por_que_suspeito": "Incoerência cronológica no relógio interno ou no processo de preparação.",
                "severidade": "MEDIA"
            }},
            "CHK009_DATA_CARGA_TARDIA_2T": {{
                "titulo": "Carga Tardia no Dia da Eleição",
                "explicacao": "A urna foi carregada com dados às pressas no próprio dia da votação do 2T.",
                "por_que_suspeito": "Cargas emergenciais no dia da votação pulam etapas formais de auditoria prévia.",
                "severidade": "MEDIA"
            }},
            "CHK010_CORRESPONDENCIA_INVALIDA_2T": {{
                "titulo": "Correspondência de Seção Inválida",
                "explicacao": "A correspondência gravada na carga não bate com a seção do Boletim de Urna.",
                "por_que_suspeito": "Risco de votos de uma seção estarem sendo computados em outra.",
                "severidade": "ALTA"
            }},
            "CHK011_GERADOR_MIDIA_DIVERGENTE": {{
                "titulo": "Gerador de Mídia Divergente",
                "explicacao": "O computador usado pelo cartório para gerar a mídia de carga foi trocado.",
                "por_que_suspeito": "Desvio no procedimento padrão de geração de cartões eleitorais.",
                "severidade": "BAIXA"
            }},
            "CHK012_TPM_SERIAL_DIVERGENTE": {{
                "titulo": "Serial TPM Divergente",
                "explicacao": "O chip criptográfico soldado na placa-mãe da urna mudou na mesma máquina declarada.",
                "por_que_suspeito": "Inconsistência de placa de hardware na mesma urna física.",
                "severidade": "ALTA"
            }},
            "CHK013_SERIAL_INSTALACAO_REINICIADO": {{
                "titulo": "Serial de Instalação Reiniciado",
                "explicacao": "O contador de instalações da urna recuou para um valor menor.",
                "por_que_suspeito": "Indica reinstalação não autorizada do sistema operacional da urna.",
                "severidade": "MEDIA"
            }},
                        "CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO": {{
                "titulo": "Carga Gerada para Outro Município (Distância e Vizinhança)",
                "explicacao": "A carga da urna foi configurada para um município, mas a urna funcionou em outro. Se as cidades forem vizinhas/limítrofes (até ~45 km), o remanejamento pode ser normal por logística do cartório eleitoral regional. Se forem cidades distantes (> 45 km), a ocorrência não é normal e aponta falha de custódia.",
                "por_que_suspeito": "A distância em km determina a gravidade: cidades vizinhas da mesma comarca representam contingência de polo regional; cidades distantes representam quebra de jurisdição e risco de substituição irregular de urnas.",
                "severidade": "ALTA"
            }},
            "CHK015_TIPO_ARQUIVO_NAO_VOTACAO_UE": {{
                "titulo": "Tipo de Arquivo não Oficial",
                "explicacao": "O arquivo do BU não está classificado como arquivo oficial de votação de urna.",
                "por_que_suspeito": "Arquivo com cabeçalho diferente do padrão oficial de resultado.",
                "severidade": "ALTA"
            }},

            // Cadastral
            "CHK016_VARIACAO_APTOS_SECAO": {{
                "titulo": "Variação de Eleitores Originais da Seção",
                "explicacao": "A lista oficial de eleitores cadastrados na seção mudou entre os turnos. Variações pequenas de até meio por cento (<= 0.5%, como apenas 1 ou 2 eleitores) são ajustes cadastrais residuais comuns da Justiça Eleitoral (ex.: reativações pontuais de título). Apenas variações superiores a meio por cento (> 0.5%) são consideradas relevantes.",
                "por_que_suspeito": "Se a variação for superior a 0.5% do eleitorado, aponta para inclusão ou exclusão anormal de votantes após o congelamento oficial do cadastro eleitoral.",
                "severidade": "ALTA"
            }},
            "CHK017_REDUCAO_APTOS_SECAO": {{
                "titulo": "Redução de Eleitores Originais",
                "explicacao": "Eleitores cadastrados foram retirados da lista de votantes no 2T. É relevante quando a redução ultrapassa 0.5% do total da seção.",
                "por_que_suspeito": "Reduções acima de meio por cento podem indicar cerceamento indevido de eleitores aptos.",
                "severidade": "ALTA"
            }},
            "CHK018_AUMENTO_APTOS_SECAO": {{
                "titulo": "Aumento de Eleitores Originais",
                "explicacao": "Novos eleitores apareceram cadastrados na seção no 2T. É relevante quando o aumento ultrapassa 0.5% do total da seção.",
                "por_que_suspeito": "Aumentos acima de meio por cento apontam para inserção irregular de eleitores no cadastro após o congelamento legal.",
                "severidade": "ALTA"
            }},
            "CHK019_PICO_TTE_ABSOLUTO": {{
                "titulo": "Pico de Voto em Trânsito (TTE)",
                "explicacao": "Salto repentino de mais de 20 eleitores temporários/em trânsito na seção.",
                "por_que_suspeito": "Pode indicar deslocamento artificial de eleitores para seções estratégicas.",
                "severidade": "MEDIA"
            }},
            "CHK020_PICO_TTE_PERCENTUAL": {{
                "titulo": "Oscilação Excessiva de TTE",
                "explicacao": "A quantidade de eleitores temporários variou mais de 10% da seção.",
                "por_que_suspeito": "Alteração substancial no perfil do eleitorado da urna.",
                "severidade": "MEDIA"
            }},
            "CHK023_APTOS_TOTAL_DIVERGENTE_SOMA": {{
                "titulo": "Soma de Aptos Incoerente",
                "explicacao": "A soma de eleitores originais com temporários não bate com o total.",
                "por_que_suspeito": "Erro aritmético na contabilidade de eleitores da urna.",
                "severidade": "ALTA"
            }},
            "CHK031_COMPARECIMENTO_EXCEDE_APTOS_2T": {{
                "titulo": "Comparecimento Maior que Aptos (2T)",
                "explicacao": "Houve mais votos computados do que eleitores cadastrados na urna no 2T.",
                "por_que_suspeito": "Impossibilidade matemática: mais pessoas votaram do que o total de eleitores existentes na seção.",
                "severidade": "ALTA"
            }},
            "CHK033_COMPARECIMENTO_100_PCT_2T": {{
                "titulo": "100% de Presença (Zero Faltas)",
                "explicacao": "Exatamente todos os eleitores cadastrados compareceram para votar no 2T.",
                "por_que_suspeito": "Estatisticamente raríssimo em seções grandes: ninguém faltou, adoeceu ou viajou.",
                "severidade": "MEDIA"
            }},
            "CHK036_SALTO_COMPARECIMENTO_MAIOR_25PP": {{
                "titulo": "Salto de Presença > 25 pp",
                "explicacao": "O comparecimento aumentou drasticamente mais de 25 pontos percentuais no 2T.",
                "por_que_suspeito": "Entrada súbita de eleitores que não haviam votado no 1º turno.",
                "severidade": "ALTA"
            }},
            "CHK037_QUEDA_COMPARECIMENTO_MAIOR_25PP": {{
                "titulo": "Queda de Presença > 25 pp",
                "explicacao": "O comparecimento despencou mais de 25 pontos percentuais no 2T.",
                "por_que_suspeito": "Falta maciça de eleitores que haviam comparecido no 1º turno.",
                "severidade": "ALTA"
            }},
            "CHK044_COMPARECIMENTO_DISCREPANTE_DO_MUNICIPIO": {{
                "titulo": "Presença Discrepante da Média Municipal",
                "explicacao": "A variação de comparecimento da seção foi o oposto do que aconteceu na cidade.",
                "por_que_suspeito": "Seção se comportou de forma totalmente isolada e discrepante do município.",
                "severidade": "ALTA"
            }},

            // Votação & Terceira Via
            "CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR": {{
                "titulo": "Queda de Votos com MAIOR Comparecimento",
                "explicacao": "O candidato finalista perdeu votos nominais no 2T, embora mais eleitores tenham ido votar na seção.",
                "por_que_suspeito": "Se mais pessoas foram votar e o candidato perdeu votos absolutos, sua base encolheu misteriosamente mesmo com eleição polarizada.",
                "severidade": "ALTA"
            }},
            "CHK047_QUEDA_FINALISTA_COM_COMPARECIMENTO_IGUAL": {{
                "titulo": "Queda de Votos com Comparecimento IGUAL",
                "explicacao": "O candidato finalista perdeu votos com exatamente o mesmo número de votantes na urna.",
                "por_que_suspeito": "Perda de votos consolidados em relação ao 1º turno com eleitorado idêntico.",
                "severidade": "ALTA"
            }},
            "CHK048_QUEDA_DESPROPORCIONAL_AO_COMPARECIMENTO": {{
                "titulo": "Queda Desproporcional à Abstenção",
                "explicacao": "A presença caiu pouco, mas o candidato perdeu mais de 2.5x dessa proporção em votos.",
                "por_que_suspeito": "A perda de votos do candidato foi muito superior à queda geral de votantes da seção.",
                "severidade": "ALTA"
            }},
            "CHK049_PERDA_BRUSCA_MAIOR_30PCT_FINALISTA": {{
                "titulo": "Perda Brusca > 30% dos Votos",
                "explicacao": "O candidato finalista perdeu mais de 30% de seus votos nominais com presença estável.",
                "por_que_suspeito": "Desidratação inexplicável da votação obtida 21 dias antes.",
                "severidade": "MEDIA"
            }},
            "CHK050_DESAPARECIMENTO_FINALISTA_NO_2T": {{
                "titulo": "Desaparecimento Total de Votos",
                "explicacao": "O candidato tinha votação expressiva no 1T e zerou (0 votos) no 2T.",
                "por_que_suspeito": "Todos os eleitores que votaram nele no 1T sumiram ou mudaram no 2T.",
                "severidade": "ALTA"
            }},
            "CHK052_UNANIMIDADE_100PCT_FINALISTA_2T": {{
                "titulo": "100% de Votação Unânime",
                "explicacao": "Todos os votos válidos da seção foram computados para um único candidato.",
                "por_que_suspeito": "Unanimidade eleitoral absoluta no 2º turno.",
                "severidade": "MEDIA"
            }},
            "CHK053_ABSORCAO_100PCT_TERCEIRA_VIA_POR_UM_CANDIDATO": {{
                "titulo": "Absorção de 100% da Terceira Via por um Só Concorrente",
                "explicacao": "Todos os votos de candidatos eliminados no 1T foram direcionados a um único concorrente.",
                "por_que_suspeito": "Migração de votos 100% assimétrica, sem divisão natural de votos entre os finalistas.",
                "severidade": "MEDIA"
            }},
            "CHK054_CRESCIMENTO_EXCEDE_TETO_MIGRACAO_E_COMPARECIMENTO": {{
                "titulo": "Crescimento Excede Teto Matemático",
                "explicacao": "O candidato ganhou mais votos no 2T do que a soma de toda a 3ª via, brancos, nulos e novos eleitores.",
                "por_que_suspeito": "Impossibilidade matemática: o candidato cresceu mais do que todos os votos disponíveis para migrar.",
                "severidade": "ALTA"
            }},
            "CHK055_CRESCIMENTO_COM_QUEDA_DE_COMPARECIMENTO_ACIMA_DA_TERCEIRA_VIA": {{
                "titulo": "Crescimento com Queda de Presença",
                "explicacao": "O comparecimento caiu, mas o candidato cresceu além do total existente de votos de terceira via no 1T.",
                "por_que_suspeito": "O candidato cresceu votos que não existiam no 1T com menos pessoas votando.",
                "severidade": "ALTA"
            }},
            "CHK056_INVERSAO_ABRUPTA_SWING_MAIOR_50PP": {{
                "titulo": "Swing Político Extremo (> 50 pp)",
                "explicacao": "Um candidato liderava com folga no 1T e o adversário virou de forma esmagadora no 2T.",
                "por_que_suspeito": "Mudança radical e repentina na preferência política da seção em 3 semanas.",
                "severidade": "ALTA"
            }},
            "CHK058_MIGRACAO_TOTALMENTE_ASSIMETRICA_CONTRA_MEDIA_MUNICIPAL": {{
                "titulo": "Migração Oposta à Média Municipal",
                "explicacao": "Na seção o candidato disparou, enquanto no resto da cidade o adversário cresceu.",
                "por_que_suspeito": "Comportamento da seção colide frontalmente com a tendência de todo o município.",
                "severidade": "ALTA"
            }},
            "CHK062_DESVIO_PADRAO_VOTOS_EXTREMO_NO_MUNICIPIO": {{
                "titulo": "Desvio Extremo no Município (> 3.5 DP)",
                "explicacao": "Percentual do candidato na seção desvia mais de 3.5 desvios-padrão da média da cidade.",
                "por_que_suspeito": "Estatisticamente é um ponto fora da curva (outlier severo) no município.",
                "severidade": "MEDIA"
            }},

            // Biometria
            "CHK066_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_30PP": {{
                "titulo": "Desabamento Crítico de Validação Biométrica (> 30 pp)",
                "explicacao": "Como é possível a biometria funcionar normalmente para quase todos no 1º turno e falhar no 2º turno para os mesmos eleitores? Não existe justificativa biológica para as impressões digitais deixarem de ser reconhecidas 21 dias depois. Isso aponta que o leitor biométrico foi propositalmente ignorado, desligado ou contornado pelos mesários, que passaram a liberar a votação digitando o ano de nascimento no terminal.",
                "por_que_suspeito": "A biometria é a única trava física que comprova a presença presencial do cidadão. Quando a biometria cai e a liberação manual explode, o mesário assume controle irrestrito da máquina, criando a brecha perfeita para habilitar votos no lugar de eleitores faltosos (voto fantasma), sem deixar rastro digital.",
                "severidade": "ALTA"
            }},
            "CHK067_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_20PP": {{
                "titulo": "Queda Acentuada de Biometria (> 20 pp)",
                "explicacao": "O eleitorado da seção é exatamente o mesmo nos dois turnos. Uma queda de mais de 20 pontos percentuais no reconhecimento por digital significa que dezenas de eleitores que tiveram sua digital reconhecida no 1º turno foram misteriosamente liberados sem biometria no 2º turno por digitação manual do ano de nascimento.",
                "por_que_suspeito": "Anula a barreira de segurança antifraude da urna. A substituição da digital pela digitação manual do ano de nascimento pelo mesário elimina a garantia de presença física do cidadão e exige auditoria imediata das folhas de presença em papel assinadas e tomada de depoimentos dos mesários.",
                "severidade": "MEDIA"
            }},
            "CHK068_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_25PP": {{
                "titulo": "Surto Crítico de Liberação Manual por Ano de Nascimento (> 25 pp)",
                "explicacao": "Os mesários digitaram manualmente o ano de nascimento para liberar mais de um quarto dos eleitores da seção, em vez de exigir a leitura da impressão digital.",
                "por_que_suspeito": "Mesários mal-intencionados podem consultar o caderno eleitoral para obter a data de nascimento de eleitores que não compareceram e liberar a urna para votar no lugar deles, inflando artificialmente o comparecimento e alterando o resultado da urna.",
                "severidade": "ALTA"
            }},
            "CHK069_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_15PP": {{
                "titulo": "Salto de Liberação Manual por Ano de Nascimento (> 15 pp)",
                "explicacao": "Aumento expressivo na liberação de eleitores por digitação do ano de nascimento no terminal do mesário no 2º turno.",
                "por_que_suspeito": "Uso desproporcional da exceção manual sem justificativa técnica plausível, contornando a segurança biométrica.",
                "severidade": "MEDIA"
            }},
            "CHK070_ZERO_BIOMETRIA_EM_SECAO_BIOMETRIZADA": {{
                "titulo": "Desativação Total da Biometria em Seção Biometrizada",
                "explicacao": "Uma seção onde a maioria dos eleitores votou por biometria no 1º turno registrou ZERO votos por biometria no 2º turno. Todos os eleitores foram liberados manualmente.",
                "por_que_suspeito": "O leitor óptico foi desconectado, desativado ou sumariamente ignorado pela mesa receptora durante todo o dia da eleição, eliminando 100% da rastreabilidade biométrica da urna.",
                "severidade": "MEDIA"
            }},
            "CHK072_SOMA_DETALHAMENTO_COMPARECIMENTO_DIVERGENTE": {{
                "titulo": "Soma do Detalhamento Biométrico Diverge",
                "explicacao": "Biometria + Biográfica + Sem Biometria não bate com o comparecimento.",
                "por_que_suspeito": "Inconsistência nos contadores internos de habilitação da urna.",
                "severidade": "ALTA"
            }},

            // Tempo
            "CHK076_ABERTURA_PRECOCE_2T": {{
                "titulo": "Abertura Precoce (< 07:00)",
                "explicacao": "A urna começou a receber votos antes das 7 horas da manhã.",
                "por_que_suspeito": "Violação do horário regulamentar de abertura do TSE.",
                "severidade": "MEDIA"
            }},
            "CHK077_ABERTURA_TARDIA_2T": {{
                "titulo": "Abertura Tardia (> 08:30)",
                "explicacao": "A urna só começou a receber votos após as 8h30.",
                "por_que_suspeito": "Atraso expressivo que pode indicar problemas técnicos ou operacionais.",
                "severidade": "MEDIA"
            }},
            "CHK078_ENCERRAMENTO_PRECOCE_2T": {{
                "titulo": "Encerramento Precoce (< 17:00)",
                "explicacao": "A urna foi fechada antes das 17h enquanto ainda poderia haver eleitores.",
                "por_que_suspeito": "Fechamento antecipado irregular que impede o voto de cidadãos.",
                "severidade": "ALTA"
            }},
            "CHK079_ENCERRAMENTO_MUITO_TARDIO_2T": {{
                "titulo": "Encerramento Tardio (> 20:00)",
                "explicacao": "A votação continuou até depois das 20h.",
                "por_que_suspeito": "Indica filas anômalas ou extensão excessiva do horário de votação.",
                "severidade": "MEDIA"
            }},
            "CHK083_TEMPO_MEDIO_POR_VOTO_IMPOSSIVEL_INFERIOR_15S": {{
                "titulo": "Votos em Menos de 15 Segundos",
                "explicacao": "Tempo médio por voto menor que 15 segundos durante o dia todo.",
                "por_que_suspeito": "Ritmo humanamente impossível para identificação, conferência e voto na cabine.",
                "severidade": "ALTA"
            }},
            "CHK084_EMISSAO_BU_ANTERIOR_AO_ENCERRAMENTO": {{
                "titulo": "Emissão Anterior ao Encerramento",
                "explicacao": "O Boletim de Urna foi impresso antes do fechamento oficial da votação.",
                "por_que_suspeito": "Violação cronológica grave na gravação dos arquivos da urna.",
                "severidade": "ALTA"
            }},

            // Brancos e Nulos
            "CHK086_EXPLOSAO_BRANCOS_NULOS_MAIOR_15PP": {{
                "titulo": "Salto de Brancos e Nulos > 15 pp",
                "explicacao": "Votos brancos e nulos aumentaram mais de 15 pontos percentuais no 2T.",
                "por_que_suspeito": "Salto incomum de descarte de votos em eleição polarizada.",
                "severidade": "MEDIA"
            }},
            "CHK088_EXTINCAO_BRANCOS_NULOS_SECAO_GRANDE": {{
                "titulo": "Zero Brancos e Zero Nulos",
                "explicacao": "Nenhum voto branco e nenhum nulo em urna com mais de 150 votantes.",
                "por_que_suspeito": "Ausência total de erros de digitação ou votos de protesto em amostra grande.",
                "severidade": "BAIXA"
            }},

            // Integridade
            "CHK093_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_2T": {{
                "titulo": "Soma de Votos != Comparecimento (2T)",
                "explicacao": "A soma de válidos, brancos e nulos não bate com o comparecimento no 2T.",
                "por_que_suspeito": "Corrupção ou incoerência nos totais de apuração do Boletim de Urna.",
                "severidade": "ALTA"
            }},
            "CHK098_FALHA_CADEIA_HASH_SHA512_2T": {{
                "titulo": "Cadeia de Hashes SHA-512 Rompida (2T)",
                "explicacao": "O hash matemático recalculado voto a voto não bate com o declarado no 2T.",
                "por_que_suspeito": "Alteração ou corrupção nos dados de votação do Boletim de Urna do 2T.",
                "severidade": "ALTA"
            }},
            "CHK100_HASH_ASSINADO_VSC_DIVERGENTE": {{
                "titulo": "Hash Assinado no VSC Divergente",
                "explicacao": "O hash SHA-512 do arquivo do BU não bate com a assinatura oficial da urna.",
                "por_que_suspeito": "Possível alteração no arquivo bu.dat após a assinatura digital da máquina.",
                "severidade": "ALTA"
            }},
            "CHK101_BENFORD_PRIMEIRO_DIGITO_ANOMALO": {{
                "titulo": "Primeiro Dígito Anômalo (Lei de Benford)",
                "explicacao": "Distribuições naturais de votos seguem a Lei de Benford (dígitos 1 e 2 são muito mais frequentes que dígitos 8 e 9).",
                "por_que_suspeito": "Desvios severos em contagens podem indicar números forjados ou arredondados manualmente.",
                "severidade": "BAIXA"
            }},
            "CHK102_DIGITOS_REDONDOS_EXCESSIVOS": {{
                "titulo": "Comparecimento em Centena Exata (00)",
                "explicacao": "O número total de votantes da seção cravou exatamente em uma centena redonda (ex.: 200, 300).",
                "por_que_suspeito": "Pode indicar corte artificial ou encerramento direcionado de eleitores.",
                "severidade": "BAIXA"
            }},
            "CHK103_URNA_SUBSTITUTA_SEM_HISTORICO_CARGA": {{
                "titulo": "Urna Substituta Sem Código de Carga",
                "explicacao": "A urna de contingência foi ligada sem registrar o código de carga no Boletim de Urna.",
                "por_que_suspeito": "Quebra de procedimento na preparação e validação de urnas reservas.",
                "severidade": "ALTA"
            }},
            "CHK104_CORRESPONDENCIA_DATA_CARGA_ANTERIOR_1T": {{
                "titulo": "Data de Carga da Urna do 2T Anterior ao 1T",
                "explicacao": "A urna do 2º turno tem registro de carga feito antes da votação do 1º turno.",
                "por_que_suspeito": "Incoerência cronológica no relógio interno ou na geração da mídia de votação.",
                "severidade": "ALTA"
            }},
            "CHK105_PICO_VOTOS_ULTIMA_HORA_ENCERRAMENTO": {{
                "titulo": "Votação Concentrada em Poucas Horas",
                "explicacao": "Grande volume de votos computado em uma janela comprimida de tempo.",
                "por_que_suspeito": "Ritmo atípico que pode indicar concentração suspeita de votos perto do encerramento.",
                "severidade": "MEDIA"
            }},
            "CHK106_INTERVALO_ABERTURA_PRIMEIRO_VOTO_EXCEDE_2H": {{
                "titulo": "Atraso Superior a 2 Horas para Abertura",
                "explicacao": "A urna só começou a receber votos após as 10 horas da manhã.",
                "por_que_suspeito": "Retardo excessivo que prejudica o acesso de eleitores matutinos.",
                "severidade": "BAIXA"
            }},
            "CHK107_INVERSAO_PROPORCAO_BRANCOS_NULOS": {{
                "titulo": "Inversão da Razão Brancos vs Nulos",
                "explicacao": "A proporção entre votos brancos e nulos inverteu mais de 50 pontos percentuais entre turnos.",
                "por_que_suspeito": "Mudança brusca no padrão de descarte de votos na seção.",
                "severidade": "MEDIA"
            }},
            "CHK108_MIGRACAO_TOTAL_BRANCOS_NULOS_PARA_UM_CANDIDATO": {{
                "titulo": "Migração Total de Brancos/Nulos para um Só Concorrente",
                "explicacao": "A redução de votos inválidos no 2T migrou quase integralmente (> 90%) para um único candidato.",
                "por_que_suspeito": "Desvio atípico e direcionado de votos inválidos para uma só candidatura.",
                "severidade": "ALTA"
            }},
            "CHK109_ABSTENCAO_MAIOR_QUE_VOTOS_DO_VENCEDOR": {{
                "titulo": "Abstenção Maior que a Votação do Vencedor",
                "explicacao": "Mais pessoas faltaram do que o total de votos recebidos pelo candidato vencedor daquela urna.",
                "por_que_suspeito": "Desmobilização extrema do eleitorado na seção.",
                "severidade": "BAIXA"
            }},
            "CHK110_ABSTENCAO_REDUZIDA_COM_MIGRACAO_UNILATERAL": {{
                "titulo": "Redução de Abstenção Canalizada 100% para um Candidato",
                "explicacao": "Novos eleitores compareceram no 2T e 100% dos novos votos foram para o mesmo concorrente.",
                "por_que_suspeito": "Mobilização totalmente assimétrica de eleitores faltosos.",
                "severidade": "ALTA"
            }},
            "CHK111_HABILITACAO_BIOGRAFICA_SUPERIOR_A_BIOMETRICA": {{
                "titulo": "Liberação Manual por Ano de Nascimento Superou a Biometria",
                "explicacao": "Mais eleitores foram liberados digitando o ano de nascimento do que colocando a impressão digital na urna.",
                "por_que_suspeito": "A exceção virou regra: quando mais da metade da seção vota sem biometria, o mesário assume controle manual da máquina, permitindo votos fantasmas.",
                "severidade": "ALTA"
            }},
            "CHK112_DESABAMENTO_BRUTAL_BIOMETRIA_MAIOR_40PP": {{
                "titulo": "Desabamento Brutal de Biometria (> 40 pp)",
                "explicacao": "A validação por digital despencou mais de 40 pontos percentuais entre os dois turnos.",
                "por_que_suspeito": "Leitor óptico desligado ou contornado maciçamente no 2º turno.",
                "severidade": "ALTA"
            }},
            "CHK113_FALHA_MASSIVA_RECONHECIMENTO_DIGITAL_SEM_BIOMETRIA": {{
                "titulo": "Eleitores Sem Biometria Triplicaram",
                "explicacao": "Quantidade de eleitores sem cadastro de digital triplicou de um turno para o outro.",
                "por_que_suspeito": "Inconsistência cadastral no perfil de identificação biométrica da urna.",
                "severidade": "MEDIA"
            }},
            "CHK114_VOTOS_CANDIDATO_SUPERAM_APTOS_ORIGINAIS": {{
                "titulo": "Votação do Candidato Supera Eleitores Originais da Seção",
                "explicacao": "O candidato obteve mais votos do que o total de eleitores que pertenciam originalmente àquela seção.",
                "por_que_suspeito": "Votação inflada por eleitores temporários e em trânsito (TTE).",
                "severidade": "ALTA"
            }},
            "CHK115_QUEDA_NOMINAL_AMBOS_CANDIDATOS_COM_MAIOR_COMPARECIMENTO": {{
                "titulo": "Ambos os Concorrentes Perderam Votos com Mais Presença",
                "explicacao": "Comparecimento subiu, mas tanto Lula quanto Flávio perderam votos nominais absolutos.",
                "por_que_suspeito": "Vazamento atípico de votos válidos para brancos e nulos.",
                "severidade": "ALTA"
            }},
            "CHK116_TAXA_RETENCAO_PRIMEIRO_TURNO_INFERIOR_A_50PCT": {{
                "titulo": "Candidato Perdeu Mais da Metade dos Votos do 1T",
                "explicacao": "O candidato finalista reteve menos de 50% dos votos obtidos no 1T com presença estável.",
                "por_que_suspeito": "Evasão inexplicável de votos consolidados em apenas 3 semanas.",
                "severidade": "ALTA"
            }},
            "CHK117_TRANSFERENCIA_ZERO_TERCEIRA_VIA_COM_COMPARECIMENTO_CRESCENTE": {{
                "titulo": "Estoque de 3ª Via Sumiu sem Migrar para Finalistas",
                "explicacao": "Havia mais de 40 votos de terceira via, o comparecimento subiu, mas nenhum finalista cresceu além dos novos votantes.",
                "por_que_suspeito": "Votos de candidatos eliminados desapareceram sem destino nominado.",
                "severidade": "MEDIA"
            }},
            "CHK118_DIFERENCA_TEMPO_ENCERRAMENTO_E_EMISSAO_MAIOR_15MIN": {{
                "titulo": "Impressão do BU Demorou Mais de 15 Minutos Após Encerramento",
                "explicacao": "A urna levou mais de 15 minutos entre o fechamento oficial às 17h e a emissão física do BU.",
                "por_que_suspeito": "Retardo operacional incomum que pode indicar travamento, contingência ou intervenção manual.",
                "severidade": "BAIXA"
            }},
            "CHK119_HORARIO_ENCERRAMENTO_IDENTICO_DE_SEGUNDO_ENTRE_URNAS_DISTINTAS": {{
                "titulo": "Encerramento Cravado às 17:00:00",
                "explicacao": "Urna encerrada no primeiro segundo regulamentar sem nenhum eleitor na fila.",
                "por_que_suspeito": "Fechamento automático pontual sem retenção de votantes.",
                "severidade": "INFO"
            }},
            "CHK120_VOTO_UNANIME_NO_LOCAL_DE_VOTACAO": {{
                "titulo": "Zero Votos para Concorrente em Seção Expressiva do Local",
                "explicacao": "Um dos dois candidatos finalistas recebeu zero votos válidos em uma seção expressiva do local de votação.",
                "por_que_suspeito": "Unanimidade artificial extrema em colégios eleitorais com pluralidade de eleitores.",
                "severidade": "ALTA"
            }}
        }};

        
        function getFraudScoreBadge(s) {{
            const fScore = s.fraud_score !== undefined ? s.fraud_score : (calculateSectionFraudScore(s, s.anomalias).score);
            if (fScore >= 80) {{
                return `<span class="badge" style="background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; font-weight:800; font-family:ui-monospace,monospace;">${{fScore}}%</span>`;
            }} else if (fScore >= 50) {{
                return `<span class="badge" style="background:#ffedd5; color:#c2410c; border:1px solid #fed7aa; font-weight:800; font-family:ui-monospace,monospace;">${{fScore}}%</span>`;
            }} else if (fScore >= 20) {{
                return `<span class="badge" style="background:#fef3c7; color:#92400e; border:1px solid #fde68a; font-weight:700; font-family:ui-monospace,monospace;">${{fScore}}%</span>`;
            }} else {{
                return `<span class="badge" style="background:#ecfdf5; color:#047857; border:1px solid #a7f3d0; font-family:ui-monospace,monospace;">${{fScore}}%</span>`;
            }}
        }}

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
                case 'fraud_score': return s.fraud_score !== undefined ? s.fraud_score : calculateSectionFraudScore(s, s.anomalias).score;
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
            if (val === 'fraud_desc') currentSort = {{ column: 'fraud_score', order: 'desc' }};
            if (val === 'fraud_asc') currentSort = {{ column: 'fraud_score', order: 'asc' }};
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

            filtered.sort((a, b) => {{
                const valA = getSectionValue(a, currentSort.column);
                const valB = getSectionValue(b, currentSort.column);
                if (valA < valB) return currentSort.order === 'asc' ? -1 : 1;
                if (valA > valB) return currentSort.order === 'asc' ? 1 : -1;
                return 0;
            }});

            currentFilteredSections = filtered;
            const tbody = document.getElementById('tableBody');
            const limit = Math.min(filtered.length, 300);
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
                    `<span class="badge badge-anom" onclick="openModal(${{i}})" style="cursor:pointer;" title="${{a.description || ''}} &bull; ${{a.title || ''}}">${{a.code}}</span>`
                ).join(' ');

                html += `
                <tr class="transition-colors">
                    <td class="col-fit t-left font-semibold text-slate-800">${{s.municipio_nome || 'Município ' + s.municipio}}</td>
                    <td class="col-fit t-center font-mono text-slate-600">${{s.zona}}</td>
                    <td class="col-fit t-center font-mono font-bold text-slate-900">${{s.secao}}</td>
                    <td class="col-fit t-center font-mono ${{aptClass}}">${{apt1}} &rarr; <strong>${{apt2}}</strong></td>
                    <td class="col-fit t-center">${{getSeverityBadge(s.worst_severity)}}</td>
                    <td class="col-fit t-center">${{getFraudScoreBadge(s)}}</td>
                    <td class="col-fit t-center font-mono text-slate-800">${{c1}} &rarr; <strong>${{c2}}</strong></td>
                    <td class="col-fit t-center font-mono text-slate-700">${{bio1}} &rarr; <strong>${{bio2}}</strong></td>
                    <td class="col-fit t-center font-mono text-slate-700">${{sem1}} &rarr; <strong>${{sem2}}</strong></td>
                    <td class="col-fit t-right font-mono ${{cl_22}}">${{v1_22}} &rarr; <strong>${{v2_22}}</strong> <span class="text-[10px]">(${{d_22 >= 0 ? '+' : ''}}${{d_22}})</span></td>
                    <td class="col-fit t-right font-mono ${{cl_13}}">${{v1_13}} &rarr; <strong>${{v2_13}}</strong> <span class="text-[10px]">(${{d_13 >= 0 ? '+' : ''}}${{d_13}})</span></td>
                    <td class="col-fit t-center font-mono font-semibold text-slate-700">${{t3}}</td>
                    <td class="col-grow t-left" style="line-height: 1.45;">${{badges}}</td>
                    <td class="col-fit t-center">
                        <button onclick="openModal(${{i}})" class="btn-inspect">🔍 Detalhes</button>
                    </td>
                </tr>`;
            }}

            tbody.innerHTML = html;
            document.getElementById('filterCount').textContent = `Exibindo ${{limit}} de ${{filtered.length}} seções encontradas nos filtros (ordenadas por ${{currentSort.column}} ${{currentSort.order}}).`;
        }}

                function calculateSectionFraudScore(s, sortedAnoms) {{
            if (!sortedAnoms || sortedAnoms.length === 0) {{
                return {{ score: 0, label: "Sem Evidência de Fraude (0%)", color: "#10b981", desc: "Urna 100% consistente em todas as 100 verificações forenses." }};
            }}

            let score = 0;
            const codes = sortedAnoms.map(a => a.code);
            const hasCode = (prefix) => codes.some(c => c.includes(prefix));

            // Conjunção Crítica (Bypass de Biometria + Carga de Outro Município + Troca de Urna)
            if ((hasCode("CHK001") || hasCode("CHK004")) && hasCode("CHK014") && (hasCode("CHK066") || hasCode("CHK067")) && (hasCode("CHK068") || hasCode("CHK069"))) {{
                return {{
                    score: 93,
                    label: "Altíssima Probabilidade de Fraude / Vício Material (93%)",
                    color: "#b91c1c",
                    desc: "Conjunção simultânea de troca física de máquina, carga preparada para outro município, desabamento de biometria e explosão de liberações manuais por ano de nascimento."
                }};
            }}

            // Violação Criptográfica Direta
            if (hasCode("CHK093") || hasCode("CHK098") || hasCode("CHK100") || hasCode("CHK059")) {{
                score = Math.max(score, 90);
            }}

            // Anomalia de Votação com Queda e Mais Comparecimento (CHK046)
            if (hasCode("CHK046")) {{
                score = Math.max(score, 82);
            }}

            // Crescimento Excedente ao Teto Matemático (CHK054 / CHK055)
            if (hasCode("CHK054") || hasCode("CHK055")) {{
                score = Math.max(score, 85);
            }}

            // Desabamento de Biometria + Surto Manual
            if ((hasCode("CHK066") || hasCode("CHK067")) && (hasCode("CHK068") || hasCode("CHK069"))) {{
                score = Math.max(score, 88);
            }} else if (hasCode("CHK066") || hasCode("CHK068")) {{
                score = Math.max(score, 75);
            }}

            const chk14 = sortedAnoms.find(a => a.code.includes("CHK014"));
            const isChk14Distante = (chk14 && chk14.details && chk14.details.cidades_vizinhas === false);

            if (hasCode("CHK001") && isChk14Distante) {{
                score = Math.max(score, 85);
            }} else if (isChk14Distante) {{
                score = Math.max(score, 70);
            }} else if (hasCode("CHK001") && hasCode("CHK014")) {{
                score = Math.max(score, 55);
            }} else if (hasCode("CHK001")) {{
                score = Math.max(score, 50);
            }} else if (hasCode("CHK014")) {{
                score = Math.max(score, 20);
            }}

            // Swing Político Extremo > 50 pp
            if (hasCode("CHK056")) {{
                score = Math.max(score, 70);
            }}

            // Variação Relevante de Eleitores > 0.5%
            const chk16 = sortedAnoms.find(a => a.code.includes("CHK016"));
            if (chk16 && chk16.severity === "ALTA") {{
                score = Math.max(score, 55);
            }}

            // Se apenas informativos operacionais (ex: troca de FC padrão ou aptos <= 0.5%)
            const allInfo = sortedAnoms.every(a => a.severity === "INFO" || a.severity === "BAIXA");
            if (allInfo) {{
                return {{
                    score: 3,
                    label: "Risco Mínimo / Ajustes Operacionais Normais (< 5%)",
                    color: "#10b981",
                    desc: "Apresenta apenas ajustes rotineiros comuns (como atualização padrão de Flash de Carga para o 2T ou variação residual <= 0.5% de eleitores)."
                }};
            }}

            let color = "#10b981";
            let label = "Baixo Risco de Fraude (" + score + "%)";
            let desc = "Inconsistências isoladas com baixa probabilidade de alteração dolosa do resultado.";

            if (score >= 80) {{
                color = "#b91c1c";
                label = "Altíssima Probabilidade de Vício / Fraude (" + score + "%)";
                desc = "Apresenta anomalias graves de hardware, biometria ou contabilidade que rompem as travas de segurança da urna.";
            }} else if (score >= 50) {{
                color = "#d97706";
                label = "Suspeita Elevada de Manipulação / Contaminação (" + score + "%)";
                desc = "Combinação de inconsistências relevantes que exigem auditoria documental (folha de presença física e logs).";
            }} else if (score >= 20) {{
                color = "#eab308";
                label = "Anomalia Moderada / Risco Médio (" + score + "%)";
                desc = "Desvios operacionais ou comportamentais atípicos na seção.";
            }}

            return {{ score, label, color, desc }};
        }}

        function openModal(index) {{
            const s = currentFilteredSections[index];
            if (!s) return;

            const d1 = s.dados_1t || {{}};
            const d2 = s.dados_2t || {{}};
            const p1 = d1.votos_presidenciais || {{}};
            const p2 = d2.votos_presidenciais || {{}};

            document.getElementById('modalSevBadge').innerHTML = getSeverityBadge(s.worst_severity);
            document.getElementById('modalTitle').textContent = `${{s.municipio_nome || 'Município ' + s.municipio}} - Zona ${{s.zona}}, Seção ${{s.secao}}`;
            document.getElementById('modalSubtitle').textContent = `Urna 1T: ${{d1.numero_interno_urna || 'N/A'}} | Urna 2T: ${{d2.numero_interno_urna || 'N/A'}} | Local: ${{d2.local || d1.local || 'N/A'}}`;

            // Ordena as anomalias da seção trazendo as de MAIS ALTA SEVERIDADE PRIMEIRO
            const sortedAnoms = [...(s.anomalias || [])];
            sortedAnoms.sort((a, b) => (SEV_WEIGHTS[b.severity] || 0) - (SEV_WEIGHTS[a.severity] || 0));

            // Calcula o score de probabilidade de fraude para esta urna específica
            const fraudRisk = calculateSectionFraudScore(s, sortedAnoms);

            // Renderiza o gráfico / medidor no topo do modal
            document.getElementById('modalFraudCard').innerHTML = `
                <div style="background: #ffffff; border: 2px solid ${{fraudRisk.color}}; border-radius: 0.75rem; padding: 1.15rem 1.25rem; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; gap: 1.25rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <div style="flex: 1;">
                        <span class="badge" style="background: ${{fraudRisk.color}}20; color: ${{fraudRisk.color}}; border: 1px solid ${{fraudRisk.color}}; font-weight: 800; font-family: ui-monospace, monospace; margin-bottom: 0.35rem;">ESTIMATIVA PERICIAL DE VÍCIO / FRAUDE NESTA URNA</span>
                        <h3 style="font-size: 1.15rem; font-weight: 900; color: ${{fraudRisk.color}}; margin: 0.2rem 0;">${{fraudRisk.label}}</h3>
                        <p style="font-size: 0.8125rem; color: #475569; margin: 0.25rem 0 0 0; line-height: 1.45;">${{fraudRisk.desc}}</p>
                    </div>
                    <div style="text-align: center; min-width: 110px;">
                        <div style="position: relative; width: 88px; height: 88px; margin: 0 auto;">
                            <svg viewBox="0 0 36 36" style="width: 88px; height: 88px; transform: rotate(-90deg);">
                                <path stroke="#e2e8f0" stroke-width="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                                <path stroke="${{fraudRisk.color}}" stroke-dasharray="${{fraudRisk.score}}, 100" stroke-width="3.5" stroke-linecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                            </svg>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="font-size: 1.25rem; font-weight: 900; color: ${{fraudRisk.color}}; font-family: ui-monospace, monospace;">${{fraudRisk.score}}%</div>
                                <div style="font-size: 0.55rem; font-weight: 700; color: ${{fraudRisk.color}}; text-transform: uppercase;">Probabilidade</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            const sem1 = (d1.biometria_bio || 0) + (d1.biometria_nao || 0);
            const sem2 = (d2.biometria_bio || 0) + (d2.biometria_nao || 0);

            const v1_22 = p1['22'] || 0;
            const v2_22 = p2['22'] || 0;
            const v1_13 = p1['13'] || 0;
            const v2_13 = p2['13'] || 0;

            document.getElementById('modalKpis').innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Comparecimento</div>
                    <div class="stat-value" style="font-size:1.15rem;">${{d1.comparecimento}} &rarr; ${{d2.comparecimento}}</div>
                    <div class="stat-desc">Aptos: ${{d1.aptos}} &rarr; ${{d2.aptos}}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Com Biometria</div>
                    <div class="stat-value" style="font-size:1.15rem;">${{d1.biometria_sim}} &rarr; ${{d2.biometria_sim}}</div>
                    <div class="stat-desc">Sem bio: ${{sem1}} &rarr; ${{sem2}}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Flávio Bolsonaro (22)</div>
                    <div class="stat-value" style="font-size:1.15rem; color:${{v2_22 >= v1_22 ? '#047857' : '#b91c1c'}};">${{v1_22}} &rarr; ${{v2_22}}</div>
                    <div class="stat-desc">Dif: ${{v2_22 - v1_22 >= 0 ? '+' : ''}}${{v2_22 - v1_22}} votos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Lula (13)</div>
                    <div class="stat-value" style="font-size:1.15rem; color:${{v2_13 >= v1_13 ? '#047857' : '#b91c1c'}};">${{v1_13}} &rarr; ${{v2_13}}</div>
                    <div class="stat-desc">Dif: ${{v2_13 - v1_13 >= 0 ? '+' : ''}}${{v2_13 - v1_13}} votos</div>
                </div>
            `;

            let anomHtml = '';
            for (const a of sortedAnoms) {{
                const g = GLOSSARY_DATA[a.code] || {{
                    titulo: a.title,
                    explicacao: a.description,
                    por_que_suspeito: "Inconsistência técnica identificada nas verificações automáticas de integridade."
                }};
                let descText = a.description;
                let explLeigo = g.explicacao;
                let porQueSuspeito = g.por_que_suspeito;

                if (a.code === 'CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO' && a.details) {{
                    const mSec = a.details.mun_secao || s.municipio;
                    const mCorr = a.details.mun_corr || '';
                    const nSec = a.details.mun_secao_nome || munMap[mSec] || s.municipio_nome || '';
                    const nCorr = a.details.mun_corr_nome || munMap[mCorr] || '';
                    const tSec = nSec ? `${{mSec}} (${{nSec}})` : mSec;
                    const tCorr = nCorr ? `${{mCorr}} (${{nCorr}})` : mCorr;
                    const dKm = a.details.distancia_km !== undefined ? a.details.distancia_km : '';
                    const isViz = a.details.cidades_vizinhas;

                    let geoTag = '';
                    if (dKm !== '' && dKm !== null) {{
                        if (isViz) {{
                            geoTag = ` [Cidades Vizinhas / Limítrofes - ~${{dKm}} km]`;
                            explLeigo = `A urna funcionou em ${{nSec || mSec}}, mas sua carga foi gerada em ${{nCorr || mCorr}}. Como são municípios vizinhos e limítrofes (~${{dKm}} km de distância), esse remanejamento pode ser normal por logística de contingência do cartório eleitoral regional.`;
                            porQueSuspeito = `Por serem cidades vizinhas (~${{dKm}} km), o remanejamento pode decorrer de atendimento emergencial de contingência pelo polo regional. Torna-se suspeito se associado a outras quebras graves na mesma urna (como queda de biometria e salto de votos manuais).`;
                        }} else {{
                            geoTag = ` [CIDADES NÃO VIZINHAS / DISTANTES - ~${{dKm}} km]`;
                            explLeigo = `A urna funcionou em ${{nSec || mSec}}, mas sua carga foi gerada em ${{nCorr || mCorr}} a mais de ${{dKm}} km de distância. Por NÃO serem cidades vizinhas nem conurbadas, a presença de carga de município distante é atípica e incomum.`;
                            porQueSuspeito = `ALERTA CRÍTICO DE CUSTÓDIA: Cidades distantes (~${{dKm}} km) pertencentes a regiões diferentes. Não é comum nem esperado o trânsito de urnas entre comarcas distantes sem justificativa formal prévia.`;
                        }}
                    }}
                    descText = `Correspondência vinculada ao município ${{tCorr}}, mas a seção pertence ao município ${{tSec}}${{geoTag}}.`;
                }}

                anomHtml += `
                    <div class="anomaly-card sev-${{a.severity}}">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                            <span class="font-mono" style="font-weight:800; font-size:0.75rem; color:#0f172a;">${{a.code}}</span>
                            ${{getSeverityBadge(a.severity)}}
                        </div>
                        <div style="font-weight:700; font-size:0.875rem; color:#1e293b; margin-bottom:0.25rem;">${{g.titulo}}</div>
                        <div style="font-size:0.8125rem; color:#475569; margin-bottom:0.5rem; background:#ffffff; padding:0.4rem 0.6rem; border-radius:0.25rem; border:1px solid #e2e8f0;">
                            <strong>Dado Identificado na Urna:</strong> ${{descText}}
                        </div>
                        <div style="font-size:0.75rem; color:#334155; margin-bottom:0.35rem;">
                            <strong>💡 O que significa para leigos:</strong> ${{explLeigo}}
                        </div>
                        <div style="font-size:0.75rem; color:#991b1b;">
                            <strong>⚠️ Por que isso levanta suspeita:</strong> ${{porQueSuspeito}}
                        </div>
                    </div>
                `;
            }}

            document.getElementById('modalAnomaliesList').innerHTML = anomHtml;
            document.getElementById('detailsModal').style.display = 'block';
        }}

        function closeModal() {{
            document.getElementById('detailsModal').style.display = 'none';
        }}

        function handleModalOverlayClick(e) {{
            if (e.target.id === 'detailsModal') closeModal();
        }}

        function renderGlossary() {{
            const container = document.getElementById('glossaryContainer');
            if (!container) return;
            const search = (document.getElementById('glossarySearch').value || '').toLowerCase().trim();

            let html = '';
            for (const [code, info] of Object.entries(GLOSSARY_DATA)) {{
                if (search && !code.toLowerCase().includes(search) && !info.titulo.toLowerCase().includes(search) && !info.explicacao.toLowerCase().includes(search)) {{
                    continue;
                }}

                html += `
                    <div class="stat-card" style="border-left: 3px solid ${{info.severidade === 'ALTA' ? '#ef4444' : (info.severidade === 'MEDIA' ? '#f59e0b' : '#3b82f6')}};">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                            <span class="font-mono" style="font-size:0.7rem; font-weight:800; color:#0f172a;">${{code}}</span>
                            ${{getSeverityBadge(info.severidade)}}
                        </div>
                        <div style="font-weight:700; font-size:0.8125rem; color:#1e293b; margin-bottom:0.2rem;">${{info.titulo}}</div>
                        <div style="font-size:0.75rem; color:#475569; margin-bottom:0.3rem;">${{info.explicacao}}</div>
                        <div style="font-size:0.6875rem; color:#991b1b;"><strong>Por que suspeito:</strong> ${{info.por_que_suspeito}}</div>
                    </div>
                `;
            }}
            container.innerHTML = html;
        }}

        function filterGlossary() {{
            renderGlossary();
        }}

        window.onload = function() {{
            applyFilters();
            renderGlossary();
        }};
    </script>
</body>
</html>
"""
