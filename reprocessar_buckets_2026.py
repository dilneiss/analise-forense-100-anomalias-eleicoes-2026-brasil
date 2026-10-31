# -*- coding: utf-8 -*-
"""Reprocessa as 28 UFs em paralelo, com buckets de 2/4/6/8/10 s e correlação por seção."""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analise_tempo_6s_2026 import processar, OUT  # noqa: E402

UFS = ["ZZ", "RR", "AP", "AC", "TO", "RO", "SE", "DF", "MS", "MT", "AL", "PI",
       "PB", "SC", "MA", "PA", "CE", "PR", "PE", "GO", "RS", "RJ", "BA",
       "ES", "AM", "MG", "SP"]


def worker(uf):
    try:
        r = processar(uf)
        return uf, {k: r.get(k) for k in (
            "secoes_processadas", "votos_computados",
            "votos_abaixo_2s", "votos_abaixo_4s", "votos_abaixo_6s",
            "votos_abaixo_8s", "votos_abaixo_10s",
            "pct_abaixo_2s", "pct_abaixo_4s", "pct_abaixo_6s",
            "pct_abaixo_8s", "pct_abaixo_10s",
            "secoes_com_ao_menos_1_voto_abaixo_6s",
            "correlacao_taxa_rapida_vs_lula")}
    except Exception as e:
        return uf, {"erro": str(e)}


def main():
    t0 = time.time()
    print(f"reprocessando {len(UFS)} UFs com buckets 2/4/6/8/10 s...", flush=True)
    res = {}
    with ProcessPoolExecutor(max_workers=6) as ex:
        futuros = {ex.submit(worker, uf): uf for uf in UFS}
        for f in as_completed(futuros):
            uf, dados = f.result()
            res[uf] = dados
            if "erro" in dados:
                print(f"[{uf}] ERRO: {dados['erro']}", flush=True)
            else:
                print(f"[{uf}] <2s={dados['votos_abaixo_2s']:,} <4s={dados['votos_abaixo_4s']:,} "
                      f"<6s={dados['votos_abaixo_6s']:,} <8s={dados['votos_abaixo_8s']:,} "
                      f"<10s={dados['votos_abaixo_10s']:,}", flush=True)

    tot = {k: 0 for k in ("secoes_processadas", "votos_computados", "votos_abaixo_2s",
                          "votos_abaixo_4s", "votos_abaixo_6s", "votos_abaixo_8s",
                          "votos_abaixo_10s", "secoes_com_ao_menos_1_voto_abaixo_6s")}
    corr = {"n": 0, "sx": 0.0, "sy": 0.0, "sxy": 0.0, "sxx": 0.0, "syy": 0.0}
    for uf, d in res.items():
        if "erro" in d:
            continue
        for k in tot:
            tot[k] += d.get(k, 0) or 0
        c = d.get("correlacao_taxa_rapida_vs_lula") or {}
        for k in corr:
            corr[k] += c.get(k, 0) or 0

    n, sx, sy, sxy, sxx, syy = corr["n"], corr["sx"], corr["sy"], corr["sxy"], corr["sxx"], corr["syy"]
    r = None
    den = ((n * sxx - sx * sx) * (n * syy - sy * sy)) ** 0.5
    if den > 0:
        r = round((n * sxy - sx * sy) / den, 4)

    saida = {"ano": 2026, "turno": 2, "totais": tot,
             "pct": {f"abaixo_{t}s": round(tot[f"votos_abaixo_{t}s"] / tot["votos_computados"] * 100, 3)
                     for t in (2, 4, 6, 8, 10)},
             "correlacao_pearson_taxa_rapida_vs_lula": r,
             "n_secoes_correlacao": n,
             "estados": res,
             "tempo_s": round(time.time() - t0, 1)}
    for destino in (Path("D:/urnas2026/resultados/nacional_buckets_2026.json"),
                    Path("data/tempo_2026/nacional_buckets_2026.json")):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("concluído em", saida["tempo_s"], "s", flush=True)
    print(json.dumps(saida["totais"], ensure_ascii=False), flush=True)
    print("pct:", json.dumps(saida["pct"], ensure_ascii=False), flush=True)
    print("correlação (Pearson, seção a seção):", r, "| n =", n, flush=True)


if __name__ == "__main__":
    main()
