# -*- coding: utf-8 -*-
"""Baixa e processa todos os Boletins de Urna (BWEB) oficiais do 1º Turno de 2018 para D:\\urnas2018."""

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

BASE_URL_1T = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2018/buweb/BWEB_1t_{uf}_101020181938.zip"
def download_and_process_1t(uf):
    cache_file = OUT_CACHE_2018 / f"{uf}.json"
    if cache_file.exists():
        try:
            d = json.load(open(cache_file, encoding="utf-8"))
            if "bolsonaro_1t" in d and d.get("total_secoes_1t", 0) > 0:
                print(f"[{uf}] Já processado anteriormente.")
                return d
        except Exception:
            pass

    url = BASE_URL_1T.format(uf=uf)
    dest_zip = DEST_DIR / f"BWEB_1t_{uf}.zip"
    
    # 1. Download se não existir
    if not dest_zip.exists() or dest_zip.stat().st_size == 0:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp, open(dest_zip, "wb") as f:
                f.write(resp.read())
        except Exception as e:
            return {"uf": uf, "error": str(e)}

    # 2. Processar CSV diretamente do ZIP em memória (filtrando cargo 1 = Presidente)
    total_secoes = set()
    tot_aptos = 0
    tot_comp = 0
    tot_abst = 0
    votos_bolsonaro = 0
    votos_haddad = 0
    votos_ciro = 0
    votos_alckmin = 0
    votos_outros = 0
    votos_brancos = 0
    votos_nulos = 0
    secoes_dict = {}

    try:
        with zipfile.ZipFile(dest_zip, "r") as zf:
            csv_name = [n for n in zf.namelist() if n.endswith(".csv")][0]
            with zf.open(csv_name) as f:
                header = f.readline().decode("latin1").strip().split(";")
                header = [h.strip('"') for h in header]
                
                col_cargo = header.index("CD_CARGO_PERGUNTA")
                col_municipio = header.index("CD_MUNICIPIO")
                col_zona = header.index("NR_ZONA")
                col_secao = header.index("NR_SECAO")
                col_aptos = header.index("QT_APTOS")
                col_comp = header.index("QT_COMPARECIMENTO")
                col_abst = header.index("QT_ABSTENCOES")
                col_tipo_votavel = header.index("CD_TIPO_VOTAVEL")
                col_votavel = header.index("NR_VOTAVEL")
                col_votos = header.index("QT_VOTOS")
                
                seen_pres = False
                for line in f:
                    parts = line.decode("latin1").strip().split(";")
                    parts = [p.strip('"') for p in parts]
                    if len(parts) <= col_votos:
                        continue
                    
                    cargo = parts[col_cargo]
                    if cargo != "1":  # 1 = Presidente
                        if seen_pres:
                            break  # Presidente é o primeiro cargo; encerrou o bloco!
                        continue
                    seen_pres = True
                    mun = parts[col_municipio]
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
                        
                        secoes_dict[sec_key] = True
                        tot_aptos += aptos
                        tot_comp += comp
                        tot_abst += abst
                        total_secoes.add(sec_key)
                        
                    if tipo_vot == "1":  # Nominal
                        if nr_vot == "17":
                            votos_bolsonaro += qtd_votos
                        elif nr_vot == "13":
                            votos_haddad += qtd_votos
                        elif nr_vot == "12":
                            votos_ciro += qtd_votos
                        elif nr_vot == "45":
                            votos_alckmin += qtd_votos
                        else:
                            votos_outros += qtd_votos
                    elif tipo_vot == "2":  # Branco
                        votos_brancos += qtd_votos
                    elif tipo_vot == "3":  # Nulo
                        votos_nulos += qtd_votos

        terceira_via = votos_ciro + votos_alckmin + votos_outros
        res_1t = {
            "uf": uf,
            "total_secoes_1t": len(total_secoes),
            "aptos_1t": tot_aptos,
            "comparecimento_1t": tot_comp,
            "abstencao_1t": tot_abst,
            "bolsonaro_1t": votos_bolsonaro,
            "haddad_1t": votos_haddad,
            "ciro_1t": votos_ciro,
            "alckmin_1t": votos_alckmin,
            "outros_1t": votos_outros,
            "terceira_via_1t": terceira_via,
            "brancos_1t": votos_brancos,
            "nulos_1t": votos_nulos,
            "zip_size_mb": round(dest_zip.stat().st_size / (1024*1024), 2)
        }
        
        # Atualizar cache existente da UF (juntando 1T e 2T)
        cache_file = OUT_CACHE_2018 / f"{uf}.json"
        state_data = {}
        if cache_file.exists():
            state_data = json.load(open(cache_file, encoding="utf-8"))
        state_data.update(res_1t)
        
        # Calcular crescimento 1T -> 2T se 2T existir
        if "bolsonaro_2t" in state_data:
            state_data["crescimento_bolsonaro"] = state_data["bolsonaro_2t"] - state_data["bolsonaro_1t"]
            state_data["crescimento_haddad"] = state_data["haddad_2t"] - state_data["haddad_1t"]
            state_data["novos_votantes_2t"] = state_data.get("comparecimento_2t", 0) - state_data["comparecimento_1t"]
            
        with open(cache_file, "w", encoding="utf-8") as out_f:
            json.dump(state_data, out_f, ensure_ascii=False, indent=2)
            
        print(f"[{uf}] 1T Concluído: {len(total_secoes)} seções | Bols: {votos_bolsonaro:,} x Had: {votos_haddad:,} | Ciro: {votos_ciro:,} | Alckmin: {votos_alckmin:,}")
        return res_1t
    except Exception as e:
        return {"uf": uf, "error": str(e)}

def main():
    print("Iniciando download e processamento de todas as 28 UFs do 1º Turno de 2018 para D:\\urnas2018...")
    t0 = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for res in executor.map(download_and_process_1t, UFS):
            results.append(res)
            
    valid_states = [s for s in results if "error" not in s]
    tot_bols = sum(s["bolsonaro_1t"] for s in valid_states)
    tot_haddad = sum(s["haddad_1t"] for s in valid_states)
    tot_ciro = sum(s["ciro_1t"] for s in valid_states)
    tot_alckmin = sum(s["alckmin_1t"] for s in valid_states)
    tot_outros = sum(s["outros_1t"] for s in valid_states)
    tot_3via = sum(s["terceira_via_1t"] for s in valid_states)
    tot_comp = sum(s["comparecimento_1t"] for s in valid_states)
    tot_aptos = sum(s["aptos_1t"] for s in valid_states)
    
    # Atualizar relatório nacional de 2018
    out_nat_file = Path("comparison_nacional_brasil/national_report_2018.json")
    national_2018 = json.load(open(out_nat_file, encoding="utf-8")) if out_nat_file.exists() else {}
    
    if "totais_nacionais" not in national_2018:
        national_2018["totais_nacionais"] = {}
        
    totais = national_2018["totais_nacionais"]
    totais["comparecimento_1t"] = tot_comp
    totais["aptos_1t"] = tot_aptos
    totais["bolsonaro_1t"] = tot_bols
    totais["haddad_1t"] = tot_haddad
    totais["ciro_1t"] = tot_ciro
    totais["alckmin_1t"] = tot_alckmin
    totais["outros_1t"] = tot_outros
    totais["terceira_via_1t"] = tot_3via
    totais["margem_1t"] = tot_bols - tot_haddad
    
    if "bolsonaro_2t" in totais:
        totais["crescimento_bolsonaro"] = totais["bolsonaro_2t"] - tot_bols
        totais["crescimento_haddad"] = totais["haddad_2t"] - tot_haddad
        totais["novos_votantes_2t"] = totais["comparecimento_2t"] - tot_comp
        
    # Atualizar estados no relatório nacional
    for uf in UFS:
        cache_f = OUT_CACHE_2018 / f"{uf}.json"
        if cache_f.exists():
            national_2018.setdefault("estados", {})[uf] = json.load(open(cache_f, encoding="utf-8"))
            
    with open(out_nat_file, "w", encoding="utf-8") as f:
        json.dump(national_2018, f, ensure_ascii=False, indent=2)
        
    print(f"\nProcessamento do 1º Turno de 2018 concluído em {time.time()-t0:.2f}s!")
    print(f"Total Bolsonaro 1T: {tot_bols:,} (46,03%)")
    print(f"Total Haddad 1T: {tot_haddad:,} (29,28%)")
    print(f"Total Ciro Gomes: {tot_ciro:,} (12,47%)")
    print(f"Total Geraldo Alckmin: {tot_alckmin:,} (4,76%)")
    print(f"Total Terceira Via: {tot_3via:,} votos")
    print(f"Margem Pró-Bolsonaro 1T: +{tot_bols - tot_haddad:,} votos (+17,9 Milhões na frente!)")

if __name__ == "__main__":
    main()
