# -*- coding: utf-8 -*-
"""Baixa e audita a votação presidencial por seção eleitoral de 2002 a 2026 (TSE)."""

import io
import json
import time
import zipfile
import urllib.request
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = Path("D:/urnas_historico")
BASE_DIR.mkdir(parents=True, exist_ok=True)

OUT_DIR = Path("comparison_nacional_brasil")
OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = Path("data/historico")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

YEARS = [2002, 2006, 2010, 2014, 2018, 2022, 2026]
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_{y}_BR.zip"

UFS = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
       "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO","ZZ"]


def ensure_zip(year):
    dest = BASE_DIR / f"votacao_secao_{year}_BR.zip"
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    req = urllib.request.Request(URL.format(y=year), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1024 * 512)
            if not chunk:
                break
            f.write(chunk)
    return dest


def iter_rows(zip_path):
    """Itera linhas do CSV dentro do zip, retornando (header, gerador de listas)."""
    with zipfile.ZipFile(zip_path) as zf:
        name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
        with zf.open(name) as f:
            raw_header = f.readline().decode("latin1").strip()
            header = [h.strip('"') for h in raw_header.split(";")]
            for line in f:
                parts = [p.strip('"') for p in line.decode("latin1").rstrip("\r\n").split(";")]
                if len(parts) != len(header):
                    continue
                yield header, parts


def col(header, *names):
    for n in names:
        if n in header:
            return header.index(n)
    return -1


def audit_year(year):
    t0 = time.time()
    cached = CACHE_DIR / f"audit_{year}.json"
    if cached.exists():
        try:
            prev = json.load(open(cached, encoding="utf-8"))
            if prev.get("turnos"):
                print(f"[{year}] JÁ PROCESSADO (cache) | turnos={sorted(prev['turnos'])}")
                for t, d in prev["turnos"].items():
                    print(f"    {t}T -> {d['candidato_1']['nome']} {d['candidato_1']['votos']:,} x "
                          f"{d['candidato_2']['nome']} {d['candidato_2']['votos']:,} | "
                          f"unanimidade={d['secoes_unanimidade_vencedor']:,} seções")
                return prev
        except Exception:
            pass

    zpath = ensure_zip(year)

    idx = {}
    # PASSO 1: totalizar votos por (turno, votavel) nacionalmente
    totals = defaultdict(lambda: defaultdict(int))
    names = {}
    for header, parts in iter_rows(zpath):
        if not idx:
            idx = {
                "cargo": col(header, "CD_CARGO"),
                "turno": col(header, "NR_TURNO"),
                "uf": col(header, "SG_UF"),
                "mun": col(header, "CD_MUNICIPIO"),
                "nm_mun": col(header, "NM_MUNICIPIO"),
                "zona": col(header, "NR_ZONA"),
                "secao": col(header, "NR_SECAO"),
                "votavel": col(header, "NR_VOTAVEL"),
                "nm_votavel": col(header, "NM_VOTAVEL"),
                "votos": col(header, "QT_VOTOS"),
            }
        if parts[idx["cargo"]] not in ("1", "1.0"):
            continue
        turno = parts[idx["turno"]]
        votavel = parts[idx["votavel"]]
        try:
            q = int(float(parts[idx["votos"]]))
        except ValueError:
            continue
        if q <= 0:
            continue
        totals[turno][votavel] += q
        names.setdefault(votavel, parts[idx["nm_votavel"]])

    def is_blank(v):
        return names.get(v, "").strip().lower() in ("branco", "nulo", "legenda") or v in ("95", "96", "97")

    ranking = {}
    for turno, d in totals.items():
        nominal = {k: v for k, v in d.items() if not is_blank(k)}
        ordenado = sorted(nominal.items(), key=lambda kv: kv[1], reverse=True)
        ranking[turno] = ordenado

    # PASSO 2: agregar por seção para o turno decisivo
    result = {"ano": year, "turnos": {}}
    for turno in sorted(ranking):
        top = ranking[turno][:2]
        if len(top) < 2:
            continue
        c1, c2 = top[0][0], top[1][0]
        sec_data = {}
        unanim = 0
        unanim_big = 0
        secs_zero_c2 = 0
        secs_big = 0
        estado_tot = defaultdict(lambda: defaultdict(int))

        for header, parts in iter_rows(zpath):
            if parts[idx["cargo"]] not in ("1", "1.0") or parts[idx["turno"]] != turno:
                continue
            uf = parts[idx["uf"]]
            votavel = parts[idx["votavel"]]
            try:
                q = int(float(parts[idx["votos"]]))
            except ValueError:
                continue

            key = (uf, parts[idx["mun"]], parts[idx["zona"]], parts[idx["secao"]])
            par = sec_data.get(key)
            if par is None:
                par = sec_data[key] = [0, 0]
            if votavel == c1:
                par[0] += q
            elif votavel == c2:
                par[1] += q

            if uf not in UFS:
                continue
            if votavel == c1:
                estado_tot[uf]["c1"] += q
            elif votavel == c2:
                estado_tot[uf]["c2"] += q
            elif not is_blank(votavel):
                estado_tot[uf]["terceira"] += q
            elif names.get(votavel, "").lower() == "branco":
                estado_tot[uf]["brancos"] += q
            elif names.get(votavel, "").lower() == "nulo":
                estado_tot[uf]["nulos"] += q

        for (v1, v2) in sec_data.values():
            if v1 >= 20 and v2 == 0:
                unanim += 1
                if v1 >= 100:
                    unanim_big += 1
            if v2 == 0 and (v1 + v2) > 0:
                secs_zero_c2 += 1
            if (v1 + v2) >= 200:
                secs_big += 1

        total_c1 = top[0][1]
        total_c2 = top[1][1]
        terceira_total = sum(v for k, v in totals[turno].items() if k != c1 and k != c2 and not is_blank(k))

        result["turnos"][turno] = {
            "candidato_1": {"numero": c1, "nome": names.get(c1, ""), "votos": total_c1},
            "candidato_2": {"numero": c2, "nome": names.get(c2, ""), "votos": total_c2},
            "margem": abs(total_c1 - total_c2),
            "pct_vencedor": round(max(total_c1, total_c2) / (total_c1 + total_c2 or 1) * 100, 2),
            "vencedor": names.get(c1, "") if total_c1 > total_c2 else names.get(c2, ""),
            "terceira_via_total": terceira_total,
            "top3_terceira_via": [
                {"numero": k, "nome": names.get(k, ""), "votos": v}
                for k, v in ranking[turno][2:5]
            ],
            "total_secoes_presidenciais": len(sec_data),
            "secoes_unanimidade_vencedor": unanim,
            "secoes_unanimidade_com_100_mais_votos": unanim_big,
            "secoes_runner_up_zero": secs_zero_c2,
            "secoes_com_200_mais_votos": secs_big,
            "pct_secoes_unanimidade": round(unanim / (len(sec_data) or 1) * 100, 3),
            "estados": {uf: dict(v) for uf, v in estado_tot.items()},
        }

    elapsed = time.time() - t0
    result["tempo_processamento_s"] = round(elapsed, 1)
    with open(CACHE_DIR / f"audit_{year}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    print(f"[{year}] OK em {elapsed:.0f}s | turnos={sorted(result['turnos'])}")
    for t, d in result["turnos"].items():
        print(f"    {t}T -> {d['candidato_1']['nome']} {d['candidato_1']['votos']:,} x "
              f"{d['candidato_2']['nome']} {d['candidato_2']['votos']:,} | "
              f"unanimidade={d['secoes_unanimidade_vencedor']:,} seções")
    return result


def main():
    print("=== AUDITORIA HISTÓRICA PRESIDENCIAL 2002-2026 (TSE / votação por seção) ===")
    resultados = []
    for y in YEARS:
        try:
            resultados.append(audit_year(y))
        except Exception as e:
            print(f"[{y}] ERRO: {e}")

    consolidado = {"anos": [r["ano"] for r in resultados], "resultados": resultados}
    with open(OUT_DIR / "historico_presidencial_2002_2026.json", "w", encoding="utf-8") as f:
        json.dump(consolidado, f, ensure_ascii=False, indent=1)
    print("\nConsolidado salvo em comparison_nacional_brasil/historico_presidencial_2002_2026.json")


if __name__ == "__main__":
    main()
