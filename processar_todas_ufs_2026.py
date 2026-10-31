# -*- coding: utf-8 -*-
"""Processa o 2º turno de 2026 em todas as UFs (download + análise de tempo e sequência)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from analise_tempo_6s_2026 import processar, OUT

UFS = ["SE", "AL", "PB", "PI", "RN", "MA", "CE", "PE", "BA", "TO",
       "AC", "AP", "AM", "RO", "DF", "ES", "MT", "MS", "GO",
       "SC", "PR", "RS", "RJ", "MG", "PA", "SP", "ZZ", "RR"]


def main():
    print("=== ANÁLISE 2º TURNO 2026 — TODAS AS UFs ===", flush=True)
    acumulado = {
        "ano": 2026, "turno": 2,
        "secoes_processadas": 0, "votos_computados": 0,
        "votos_abaixo_6s": 0, "votos_abaixo_10s": 0,
        "secoes_com_ao_menos_1_voto_abaixo_6s": 0,
        "sanduiche_secoes": None,  # nao mensuravel: RDV agrupado por candidato
        "ufs": {},
    }
    for uf in UFS:
        destino = OUT / f"{uf}_2t_tempo.json"
        try:
            if destino.exists():
                r = json.loads(destino.read_text(encoding="utf-8"))
                print(f"[{uf}] já processado", flush=True)
            else:
                print(f"[{uf}] baixando e processando...", flush=True)
                r = processar(uf)
            acumulado["ufs"][uf] = {k: r[k] for k in (
                "secoes_processadas", "votos_computados", "votos_abaixo_6s",
                "votos_abaixo_10s", "secoes_com_ao_menos_1_voto_abaixo_6s",
                ) if k in r}
            acumulado["secoes_processadas"] += r["secoes_processadas"]
            acumulado["votos_computados"] += r["votos_computados"]
            acumulado["votos_abaixo_6s"] += r["votos_abaixo_6s"]
            acumulado["votos_abaixo_10s"] += r["votos_abaixo_10s"]
            acumulado["secoes_com_ao_menos_1_voto_abaixo_6s"] += r["secoes_com_ao_menos_1_voto_abaixo_6s"]
            print(f"[{uf}] OK | votos<6s={r['votos_abaixo_6s']:,}", flush=True)
            (OUT / "nacional_tempo_6s_2026.json").write_text(
                json.dumps(acumulado, ensure_ascii=False, indent=1), encoding="utf-8")
        except Exception as e:
            print(f"[{uf}] ERRO: {e}", flush=True)
        time.sleep(1)
    # SINCRONIZAR_PROJETO: cópia consolidada para o repositório (na C:), que é pequena
    try:
        destino = Path("data/tempo_2026")
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "nacional_tempo_6s_2026.json").write_text(
            json.dumps(acumulado, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as e:
        print("aviso: falha ao sincronizar consolidado no projeto:", e, flush=True)
    print("=== CONCLUÍDO ===", flush=True)
    print(json.dumps({k: v for k, v in acumulado.items() if k != "ufs"}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
