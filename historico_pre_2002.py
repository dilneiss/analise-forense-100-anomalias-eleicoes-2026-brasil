# -*- coding: utf-8 -*-
"""Auditoria histórica pré-2002: eleições presidenciais de 1998, 1994, 1989 e 1960 (TSE)."""

import io
import json
import time
import zipfile
import urllib.request
from pathlib import Path
from collections import defaultdict

BASE = Path("D:/urnas_historico")
BASE.mkdir(parents=True, exist_ok=True)
CACHE = Path("data/historico")
CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path("comparison_nacional_brasil")
OUT.mkdir(parents=True, exist_ok=True)

CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
UFS = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
       "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO","ZZ"]


def baixar(url, dest):
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        while True:
            ch = r.read(1 << 18)
            if not ch:
                break
            f.write(ch)
    return dest


def num(x):
    try:
        return int(float(str(x).strip('"')))
    except (ValueError, TypeError):
        return 0


# ---------------------------------------------------------------- 1998 (seção)
def audit_1998():
    """1998: presidente só existe no arquivo BR (seções) e em votacao_candidato_munzona (UF)."""
    cache = CACHE / "audit_1998.json"
    if cache.exists():
        print("[1998] cache")
        return json.load(open(cache, encoding="utf-8"))

    t0 = time.time()

    # (1) Totais nacionais: arquivo BR de seções (presidente não existe nos arquivos por UF em 1998)
    zbr0 = baixar(f"{CDN}/votacao_secao/votacao_secao_1998_BR.zip", BASE / "vs_1998_BR.zip")
    tot = defaultdict(int)
    nomes = {}
    est = defaultdict(lambda: defaultdict(int))
    with zipfile.ZipFile(zbr0) as zf:
        fn = [n for n in zf.namelist() if n.lower().endswith((".csv", ".txt"))][0]
        with zf.open(fn) as f:
            for line in f:
                p = [x.strip('"') for x in line.decode("latin1").rstrip("\r\n").split(";")]
                if len(p) < 15 or p[12].upper() != "PRESIDENTE":
                    continue
                q = num(p[14])
                if q <= 0:
                    continue
                t, v = p[3], p[13]
                tot[(t, v)] += q
                nomes.setdefault(v, {"13": "LUIZ INACIO LULA DA SILVA",
                                     "45": "FERNANDO HENRIQUE CARDOSO",
                                     "14": "CIRO GOMES", "16": "ENÉAS CARNEIRO",
                                     "95": "BRANCO", "96": "NULO"}.get(v, f"cand_{v}"))

    # (2) Unanimidade por seção: arquivo BR (layout posicional de 15 colunas)
    zbr = baixar(f"{CDN}/votacao_secao/votacao_secao_1998_BR.zip", BASE / "vs_1998_BR.zip")
    sec = defaultdict(lambda: [0, 0])
    ranque_pre = defaultdict(int)
    with zipfile.ZipFile(zbr) as zf:
        fn = [n for n in zf.namelist() if n.lower().endswith((".csv", ".txt"))][0]
        with zf.open(fn) as f:
            for line in f:
                p = [x.strip('"') for x in line.decode("latin1").rstrip("\r\n").split(";")]
                if len(p) < 15 or p[12].upper() != "PRESIDENTE":
                    continue
                q = num(p[14])
                if q <= 0:
                    continue
                ranque_pre[(p[3], p[13])] += q

    res = {"ano": 1998, "nivel": "secao+uf", "turnos": {}}
    for t in sorted({k[0] for k in tot}):
        d = {v: q for (tt, v), q in tot.items() if tt == t}
        if len(d) < 2:
            continue
        rank = sorted(d.items(), key=lambda kv: -kv[1])
        c1, c2 = rank[0][0], rank[1][0]
        nomes_pre = {"13": "LUIZ INACIO LULA DA SILVA", "45": "FERNANDO HENRIQUE CARDOSO",
                     "14": "CIRO GOMES", "16": "ENÉAS CARNEIRO", "95": "BRANCO", "96": "NULO"}
        pares = defaultdict(lambda: [0, 0])
        with zipfile.ZipFile(zbr) as zf:
            fn = [n for n in zf.namelist() if n.lower().endswith((".csv", ".txt"))][0]
            with zf.open(fn) as f:
                for line in f:
                    p = [x.strip('"') for x in line.decode("latin1").rstrip("\r\n").split(";")]
                    if len(p) < 15 or p[12].upper() != "PRESIDENTE" or p[3] != t:
                        continue
                    v = p[13]
                    if v not in (c1, c2):
                        continue
                    q = num(p[14])
                    k = (p[6], p[9], p[10])
                    pares[k][0 if v == c1 else 1] += q
        un = sum(1 for a, b in pares.values() if a >= 20 and b == 0)
        un_inv = sum(1 for a, b in pares.values() if b >= 20 and a == 0)
        res["turnos"][t] = {
            "candidato_1": {"numero": c1, "nome": nomes.get(c1, ""), "votos": rank[0][1]},
            "candidato_2": {"numero": c2, "nome": nomes.get(c2, ""), "votos": rank[1][1]},
            "margem": abs(rank[0][1] - rank[1][1]),
            "vencedor": nomes.get(c1, ""),
            "terceira_via_total": sum(q for v, q in d.items() if v not in (c1, c2)),
            "total_secoes_presidenciais": len(pares),
            "secoes_unanimidade_vencedor": un,
            "secoes_unanimidade_reverso": un_inv,
            "pct_secoes_unanimidade": round(un / (len(pares) or 1) * 100, 3),
            "top_5": [{"nome": nomes.get(v, ""), "votos": q} for v, q in rank[:5]],
            "estados": {},
            "limitacao": "Parcial: o pacote de dados abertos do TSE para 1998 entrega apenas um recorte do arquivo BR de secoes (20,9 milhoes de votos, ~31% do eleitorado). Nao ha arquivo presidencial por UF. Numeros NAO utilizaveis para comparacao nacional.",
        }
    res["tempo_processamento_s"] = round(time.time() - t0, 1)
    json.dump(res, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[1998] OK {res['tempo_processamento_s']}s")
    return res


# ------------------------------------------- 1994 (município/zona) e 1989/1960 (UF)
def audit_agregado(ano, url, nivel):
    cache = CACHE / f"audit_{ano}.json"
    if cache.exists():
        print(f"[{ano}] cache")
        return json.load(open(cache, encoding="utf-8"))

    t0 = time.time()
    z = baixar(url, BASE / f"hist_{ano}.zip")
    tot = defaultdict(int)
    nomes = {}
    uf_tot = defaultdict(lambda: defaultdict(int))
    turnos = set()

    with zipfile.ZipFile(z) as zf:
        for name in [n for n in zf.namelist() if n.lower().endswith((".csv", ".txt"))]:
            up = name.upper()
            if "_BRASIL" in up or "_BR." in up:
                continue
            with zf.open(name) as f:
                first = f.readline().decode("latin1").strip()
                has_header = "DT_GERACAO" in first.upper() or "ANO_ELEICAO" in first.upper()
                if has_header:
                    h = [c.strip('"') for c in first.split(";")]
                    def gi(*ks):
                        for k in ks:
                            if k in h:
                                return h.index(k)
                        return -1
                    i_t, i_cg = gi("NR_TURNO"), gi("CD_CARGO")
                    i_uf, i_v, i_nm = gi("SG_UF"), gi("NR_VOTAVEL", "NR_CANDIDATO"), gi("NM_VOTAVEL", "NM_CANDIDATO")
                    i_ds, i_q = gi("DS_CARGO"), gi("QT_VOTOS", "QT_VOTOS_NOMINAIS", "QT_VOTOS_NOMINAIS_VALIDOS")
                    for line in f:
                        p = [c.strip('"') for c in line.decode("latin1").rstrip("\r\n").split(";")]
                        if len(p) != len(h):
                            continue
                        cargo_ok = (p[i_cg] == "1") if i_cg >= 0 else ("PRESIDENTE" in p[i_ds].upper())
                        if not cargo_ok:
                            continue
                        q = num(p[i_q])
                        if q <= 0:
                            continue
                        t = p[i_t]
                        turnos.add(t)
                        tot[(t, p[i_v])] += q
                        nomes.setdefault(p[i_v], p[i_nm])
                        uf_tot[p[i_uf]][(t, p[i_v])] += q
                else:
                    # sem cabeçalho: layout posicional (votacao_candidato_uf)
                    for line in f:
                        p = [c.strip('"') for c in line.decode("latin1").rstrip("\r\n").split(";")]
                        if len(p) < 26:
                            continue
                        if "PRESIDENTE" not in p[12].upper():
                            continue
                        q = num(p[25])
                        if q <= 0:
                            continue
                        t = p[3]
                        turnos.add(t)
                        chave = f"{p[20]}|{p[10]}"
                        tot[(t, chave)] += q
                        nomes.setdefault(chave, p[10])
                        uf_tot[p[5]][(t, chave)] += q

    def vazio(v):
        return nomes.get(v, "").upper().startswith(("BRANCO", "NULO"))

    res = {"ano": ano, "nivel": nivel, "turnos": {}}
    for t in sorted(turnos):
        d = {v: q for (tt, v), q in tot.items() if tt == t and not vazio(v)}
        if len(d) < 2:
            continue
        rank = sorted(d.items(), key=lambda kv: -kv[1])
        terceira = sum(q for (tt, v), q in tot.items() if tt == t and v not in (rank[0][0], rank[1][0]) and not vazio(v))
        res["turnos"][t] = {
            "candidato_1": {"chave": rank[0][0], "nome": nomes.get(rank[0][0], ""), "votos": rank[0][1]},
            "candidato_2": {"chave": rank[1][0], "nome": nomes.get(rank[1][0], ""), "votos": rank[1][1]},
            "margem": abs(rank[0][1] - rank[1][1]),
            "vencedor": nomes.get(rank[0][0], ""),
            "terceira_via_total": terceira,
            "top_5": [{"nome": nomes.get(v, ""), "votos": q} for v, q in rank[:5]],
            "estados": {uf: {f"{k[0]}T|{k[1]}": v for k, v in dd.items()} for uf, dd in uf_tot.items()},
        }
    res["tempo_processamento_s"] = round(time.time() - t0, 1)
    json.dump(res, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[{ano}] OK {res['tempo_processamento_s']}s | turnos {sorted(res['turnos'])}")
    return res


if __name__ == "__main__":
    out = []
    out.append(audit_1998())
    out.append(audit_agregado(1994,
        f"{CDN}/votacao_candidato_munzona/votacao_candidato_munzona_1994.zip", "municipio_zona"))
    out.append(audit_agregado(1989,
        f"{CDN}/votacao_candidato_uf/votacao_candidato_uf_1989.zip", "uf"))
    out.append(audit_agregado(1960,
        f"{CDN}/votacao_candidato_uf/votacao_candidato_uf_1960.zip", "uf"))
    out.append(audit_agregado(1955,
        f"{CDN}/votacao_candidato_uf/votacao_candidato_uf_1955.zip", "uf"))
    out.append(audit_agregado(1950,
        f"{CDN}/votacao_candidato_uf/votacao_candidato_uf_1950.zip", "uf"))

    consolidado = {"resultados": out}
    json.dump(consolidado, open(OUT / "historico_presidencial_1960_1998.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for r in out:
        for t, d in r["turnos"].items():
            print(f"{r['ano']} {t}T: {d['candidato_1']['nome'][:28]:28s} {d['candidato_1']['votos']:>11,} x "
                  f"{d['candidato_2']['nome'][:28]:28s} {d['candidato_2']['votos']:>11,} | margem {d['margem']:,}")
