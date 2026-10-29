# -*- coding: utf-8 -*-
"""Extrai a base de seções anômalas individuais de todos os estados do Brasil
para alimentar o Explorador Interativo de Seções e Modais no Relatório Nacional."""

import csv
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "src")
from audit_national_engine import DATA_DIR, UFS, extract_bu_data, read_bus_from_folder

CACHE_DIR = Path("data/national_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Carregar mapa de municípios
tse_map = {}
with open("data/municipio_tse_ibge.csv", encoding="latin-1") as f:
    for line in f.readlines()[1:]:
        p = line.strip().replace('"', "").split(";")
        if len(p) >= 8:
            uf = p[4].upper()
            mun_code = int(p[6])
            mun_nome = p[7]
            tse_map[(uf, mun_code)] = mun_nome

def extract_sections_for_uf(uf: str, max_sections: int = 150):
    cache_file = CACHE_DIR / f"{uf}_sections.json"
    if cache_file.is_file():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    t0 = time.time()
    p1 = DATA_DIR / f"bu_imgbu_logjez_rdv_vscmr_2026_1t_{uf}"
    p2 = DATA_DIR / f"bu_imgbu_logjez_rdv_vscmr_2026_2t_{uf}"
    
    print(f"[{uf}] Lendo e pareando seções para o explorador...")
    b1 = read_bus_from_folder(p1)
    b2 = read_bus_from_folder(p2)
    paired = set(b1.keys()) & set(b2.keys())
    
    anom_list = []
    for k in paired:
        s1 = b1[k]
        s2 = b2[k]
        
        v1_22 = s1["pres"].get(22, 0)
        v2_22 = s2["pres"].get(22, 0)
        v1_13 = s1["pres"].get(13, 0)
        v2_13 = s2["pres"].get(13, 0)
        sec_validos = v2_22 + v2_13
        if sec_validos == 0:
            continue
            
        is_chk046 = (s2["comp"] > s1["comp"] and v2_22 < v1_22 and (v1_22 - v2_22) >= 3)
        pct_man = (s2["bio_nao"] / s2["comp"] * 100.0) if s2["comp"] else 0.0
        is_bio = (pct_man >= 25.0)
        is_troca = (s1["num_urna"] != s2["num_urna"] and s1["num_urna"] > 0 and s2["num_urna"] > 0)
        is_carga_outro_mun = (s2["mun_corr"] != s2["mun"])
        
        if is_chk046 or is_bio or is_troca or is_carga_outro_mun:
            mun_nome = tse_map.get((uf, s2["mun"])) or f"Município {s2['mun']}"
            
            anomalias = []
            if is_chk046:
                anomalias.append({
                    "code": "CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR",
                    "title": "Queda de Votos com MAIOR Comparecimento",
                    "severity": "ALTA",
                    "description": f"Flávio perdeu {v1_22 - v2_22} votos enquanto comparecimento subiu (+{s2['comp'] - s1['comp']} eleitores) e Lula foi a {v2_13 / sec_validos * 100:.1f}%."
                })
            if is_bio:
                anomalias.append({
                    "code": "CHK068_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_25PP",
                    "title": "Surto Crítico de Votos Manuais sem Biometria",
                    "severity": "ALTA",
                    "description": f"{s2['bio_nao']} eleitores ({pct_man:.1f}% do comparecimento) foram liberados manualmente por ano de nascimento."
                })
            if is_troca:
                anomalias.append({
                    "code": "CHK001_TROCA_URNA_FISICA",
                    "title": "Substituição da Urna Física no 2T",
                    "severity": "MEDIA",
                    "description": f"Número da urna física alterado: 1T={s1['num_urna']} vs 2T={s2['num_urna']}."
                })
            if is_carga_outro_mun:
                anomalias.append({
                    "code": "CHK014_CARGA_URNA_EM_OUTRO_MUNICIPIO",
                    "title": "Carga Gerada para Outro Município",
                    "severity": "ALTA",
                    "description": f"Correspondência vinculada ao município {s2['mun_corr']}, mas a seção pertence a {s2['mun']} ({mun_nome})."
                })
                
            score = 90 if is_chk046 else (85 if is_bio else 70)
            label = "Altíssima Probabilidade de Vício" if (is_chk046 or is_bio) else "Inconsistência Relevante"
            
            anom_list.append({
                "uf": uf,
                "municipio": s2["mun"],
                "municipio_nome": mun_nome,
                "zona": s2["zona"],
                "secao": s2["secao"],
                "key": f"{uf}-{s2['mun']:05d}-Z{s2['zona']:04d}-S{s2['secao']:04d}",
                "worst_severity": "ALTA" if (is_chk046 or is_bio or is_carga_outro_mun) else "MEDIA",
                "fraud_score": score,
                "fraud_label": label,
                "total_anomalias": len(anomalias),
                "anomalias": anomalias,
                "dados_1t": {
                    "aptos": s1["aptos"],
                    "comparecimento": s1["comp"],
                    "biometria_sim": s1["bio_sim"],
                    "biometria_nao": s1["bio_nao"],
                    "votos_presidenciais": s1["pres"],
                    "numero_interno_urna": s1["num_urna"],
                },
                "dados_2t": {
                    "aptos": s2["aptos"],
                    "comparecimento": s2["comp"],
                    "biometria_sim": s2["bio_sim"],
                    "biometria_nao": s2["bio_nao"],
                    "votos_presidenciais": s2["pres"],
                    "numero_interno_urna": s2["num_urna"],
                }
            })
            
    # Ordenar por fraud_score desc
    anom_list.sort(key=lambda x: (x["fraud_score"], len(x["anomalias"])), reverse=True)
    selected = anom_list[:max_sections]
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False)
        
    print(f"[{uf}] {len(selected)} seções anômalas salvas em {time.time() - t0:.1f}s!")
    return selected

def run_all_extractions():
    print("Iniciando extração das seções anômalas de todos os estados...")
    for uf in UFS:
        if uf in ("SC", "MG"):
            continue # ja extraidos
        extract_sections_for_uf(uf)
    print("Todas as seções anômalas dos 28 estados foram extraídas com sucesso!")

if __name__ == "__main__":
    run_all_extractions()
