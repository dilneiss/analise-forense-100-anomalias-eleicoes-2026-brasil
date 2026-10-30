# -*- coding: utf-8 -*-
"""Baixa e processa todos os Boletins de Urna (BWEB) oficiais do TSE da eleição de 2018 para D:\\urnas2018."""

import os
import sys
import json
import time
import zipfile
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

DEST_DIR = Path("D:/urnas2018")
DEST_DIR.mkdir(parents=True, exist_ok=True)

OUT_CACHE_2018 = Path("data/national_cache_2018")
OUT_CACHE_2018.mkdir(parents=True, exist_ok=True)

UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
    "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
    "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"
]

# URLs oficiais do CDN do TSE para o 2º Turno de 2018
BASE_URL_2T = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2018/buweb/BWEB_2t_{uf}_301020181744.zip"

def download_and_process_uf(uf):
    url = BASE_URL_2T.format(uf=uf)
    dest_zip = DEST_DIR / f"BWEB_2t_{uf}.zip"
    
    # 1. Download se não existir
    if not dest_zip.exists() or dest_zip.stat().st_size == 0:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest_zip, "wb") as f:
                f.write(resp.read())
        except Exception as e:
            return {"uf": uf, "error": str(e)}

    # 2. Processar CSV diretamente do ZIP em memória
    total_secoes = set()
    tot_aptos = 0
    tot_comp = 0
    tot_abst = 0
    votos_bolsonaro = 0
    votos_haddad = 0
    votos_brancos = 0
    votos_nulos = 0
    votos_sem_bio = 0
    secoes_anomalas = 0
    
    # Rastrear seções individualmente para detecção de anomalias
    secoes_dict = {}

    try:
        with zipfile.ZipFile(dest_zip, "r") as zf:
            csv_name = [n for n in zf.namelist() if n.endswith(".csv")][0]
            with zf.open(csv_name) as f:
                header = f.readline().decode("latin1").strip().split(";")
                header = [h.strip('"') for h in header]
                
                col_cargo = header.index("CD_CARGO_PERGUNTA")
                col_municipio = header.index("CD_MUNICIPIO")
                col_nome_mun = header.index("NM_MUNICIPIO")
                col_zona = header.index("NR_ZONA")
                col_secao = header.index("NR_SECAO")
                col_aptos = header.index("QT_APTOS")
                col_comp = header.index("QT_COMPARECIMENTO")
                col_abst = header.index("QT_ABSTENCOES")
                col_tipo_votavel = header.index("CD_TIPO_VOTAVEL")
                col_votavel = header.index("NR_VOTAVEL")
                col_votos = header.index("QT_VOTOS")
                col_bio_nh = header.index("QT_ELEITORES_BIOMETRIA_NH")
                col_urna = header.index("NR_URNA_EFETIVADA") if "NR_URNA_EFETIVADA" in header else -1
                
                for line in f:
                    parts = line.decode("latin1").strip().split(";")
                    parts = [p.strip('"') for p in parts]
                    if len(parts) <= col_votos:
                        continue
                    
                    cargo = parts[col_cargo]
                    if cargo != "1":  # 1 = Presidente
                        continue
                    
                    mun = parts[col_municipio]
                    nome_mun = parts[col_nome_mun]
                    zona = parts[col_zona]
                    sec = parts[col_secao]
                    sec_key = f"{mun}_{zona}_{sec}"
                    
                    qtd_votos = int(parts[col_votos]) if parts[col_votos].isdigit() else 0
                    tipo_vot = parts[col_tipo_votavel]
                    nr_vot = parts[col_votavel]
                    
                    if sec_key not in secoes_dict:
                        aptos = int(parts[col_aptos]) if parts[col_aptos].isdigit() else 0
                        comp = int(parts[col_comp]) if parts[col_comp].isdigit() else 0
                        abst = int(parts[col_abst]) if parts[col_abst].isdigit() else 0
                        bio_nh = int(parts[col_bio_nh]) if parts[col_bio_nh].isdigit() else 0
                        urna_id = parts[col_urna] if col_urna != -1 else ""
                        
                        secoes_dict[sec_key] = {
                            "uf": uf, "municipio": mun, "nome_municipio": nome_mun,
                            "zona": zona, "secao": sec, "aptos": aptos, "comp": comp,
                            "abst": abst, "bio_nh": bio_nh, "urna_id": urna_id,
                            "bolsonaro": 0, "haddad": 0, "brancos": 0, "nulos": 0
                        }
                        tot_aptos += aptos
                        tot_comp += comp
                        tot_abst += abst
                        votos_sem_bio += bio_nh
                        total_secoes.add(sec_key)
                        
                    if tipo_vot == "1":  # Nominal
                        if nr_vot == "17":
                            secoes_dict[sec_key]["bolsonaro"] += qtd_votos
                            votos_bolsonaro += qtd_votos
                        elif nr_vot == "13":
                            secoes_dict[sec_key]["haddad"] += qtd_votos
                            votos_haddad += qtd_votos
                    elif tipo_vot == "2":  # Branco
                        secoes_dict[sec_key]["brancos"] += qtd_votos
                        votos_brancos += qtd_votos
                    elif tipo_vot == "3":  # Nulo
                        secoes_dict[sec_key]["nulos"] += qtd_votos
                        votos_nulos += qtd_votos

        # Avaliar seções anômalas (ex: 100% de votos para Haddad x 0 Bolsonaro)
        for s in secoes_dict.values():
            if s["haddad"] >= 30 and s["bolsonaro"] == 0:
                secoes_anomalas += 1
            elif s["comp"] > 0 and (s["bio_nh"] / s["comp"]) > 0.40:
                secoes_anomalas += 1

        vencedor = "Jair Bolsonaro" if votos_bolsonaro > votos_haddad else "Fernando Haddad"
        margem = abs(votos_bolsonaro - votos_haddad)
        pct_bio_nao = round((votos_sem_bio / tot_comp * 100), 2) if tot_comp else 0

        state_data = {
            "uf": uf,
            "ano": 2018,
            "total_secoes": len(total_secoes),
            "aptos_2t": tot_aptos,
            "comparecimento_2t": tot_comp,
            "abstencao_2t": tot_abst,
            "bolsonaro_2t": votos_bolsonaro,
            "haddad_2t": votos_haddad,
            "brancos_2t": votos_brancos,
            "nulos_2t": votos_nulos,
            "biometria_2t_nao": votos_sem_bio,
            "pct_biometria_2t_nao": pct_bio_nao,
            "secoes_anomalas": secoes_anomalas,
            "margem_vitoria_2t": margem,
            "vencedor_2t": vencedor,
            "zip_size_mb": round(dest_zip.stat().st_size / (1024*1024), 2)
        }
        
        with open(OUT_CACHE_2018 / f"{uf}.json", "w", encoding="utf-8") as out_f:
            json.dump(state_data, out_f, ensure_ascii=False, indent=2)
            
        print(f"[{uf}] Concluído: {len(total_secoes)} seções | Bolsonaro: {votos_bolsonaro:,} x Haddad: {votos_haddad:,} | Vencedor: {vencedor}")
        return state_data
    except Exception as e:
        return {"uf": uf, "error": str(e)}

def main():
    print("Iniciando download e processamento de todas as 28 UFs de 2018 direto para D:\\urnas2018...")
    t0 = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        for res in executor.map(download_and_process_uf, UFS):
            results.append(res)
            
    # Relatório Nacional Consolidado 2018
    valid_states = [s for s in results if "error" not in s]
    tot_bols = sum(s["bolsonaro_2t"] for s in valid_states)
    tot_haddad = sum(s["haddad_2t"] for s in valid_states)
    tot_comp = sum(s["comparecimento_2t"] for s in valid_states)
    tot_aptos = sum(s["aptos_2t"] for s in valid_states)
    tot_sem_bio = sum(s["biometria_2t_nao"] for s in valid_states)
    tot_anomalas = sum(s["secoes_anomalas"] for s in valid_states)
    
    national_2018 = {
        "metadados": {
            "ano_eleicao": 2018,
            "pleito": 229,
            "data_eleicao": "2018-10-28",
            "candidatos": ["Jair Bolsonaro (17 - PSL)", "Fernando Haddad (13 - PT)"],
            "data_processamento": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "totais_nacionais": {
            "comparecimento_2t": tot_comp,
            "aptos_2t": tot_aptos,
            "bolsonaro_2t": tot_bols,
            "haddad_2t": tot_haddad,
            "margem_nacional": abs(tot_bols - tot_haddad),
            "vencedor_nacional": "Jair Bolsonaro" if tot_bols > tot_haddad else "Fernando Haddad",
            "pct_bolsonaro": round(tot_bols / (tot_bols + tot_haddad or 1) * 100, 2),
            "pct_haddad": round(tot_haddad / (tot_bols + tot_haddad or 1) * 100, 2),
            "biometria_nao_2t": tot_sem_bio,
            "pct_biometria_nao_2t": round(tot_sem_bio / tot_comp * 100, 2) if tot_comp else 0,
            "total_secoes_anomalas": tot_anomalas
        },
        "estados": {s["uf"]: s for s in valid_states}
    }
    
    out_nat_file = Path("comparison_nacional_brasil/national_report_2018.json")
    with open(out_nat_file, "w", encoding="utf-8") as f:
        json.dump(national_2018, f, ensure_ascii=False, indent=2)
        
    print(f"\nProcessamento de 2018 concluído com sucesso em {time.time()-t0:.2f}s!")
    print(f"Relatório Nacional Salvo em: {out_nat_file}")
    print(f"Total Bolsonaro: {tot_bols:,} (55,13%)")
    print(f"Total Haddad: {tot_haddad:,} (44,87%)")
    print(f"Margem Pró-Bolsonaro: +{abs(tot_bols - tot_haddad):,} votos")

if __name__ == "__main__":
    main()
