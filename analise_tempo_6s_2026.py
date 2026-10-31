# -*- coding: utf-8 -*-
"""2026 2º turno: votos computados em menos de 6 s e padrão sequencial Lula→Flávio→Lula.

Lê diretamente dos pacotes oficiais do TSE (arqurnatot), sem extrair para disco:
  - <secao>-log.jez  -> logd.dat (timestamps de VOTE.READY e VOTE.COMPUTED)
  - <secao>-rdv.dat  -> sequência ordenada dos votos (Registro Digital do Voto)

Uso:
    python analise_tempo_6s_2026.py --uf RR
    python analise_tempo_6s_2026.py --uf RR --limite 100
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
import zipfile
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "src")
from urna_forense import der  # noqa: E402

BASE_URL = ("https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/"
            "arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t_{uf}.zip")
DDIR = Path("D:/urnas2026")
OUT = Path("D:/urnas2026/resultados")
OUT.mkdir(parents=True, exist_ok=True)

LULA, FLAVIO = 13, 22
MSG_READY = "Eleitor foi habilitado"
MSG_DONE = "O voto do eleitor foi computado"
DIA_2T = (25, 10, 2026)   # data oficial do 2º turno de 2026


def baixar(uf: str, tentativas: int = 4) -> Path:
    """Baixa o pacote garantindo integridade (tamanho e ZIP válido)."""
    DDIR.mkdir(parents=True, exist_ok=True)
    dst = DDIR / f"{uf}_2t.zip"

    def valido(caminho: Path) -> bool:
        if not caminho.exists() or caminho.stat().st_size < 10_000_000:
            return False
        try:
            with zipfile.ZipFile(caminho) as z:
                z.namelist()
            return True
        except Exception:
            return False

    if valido(dst):
        return dst

    if dst.exists():
        print(f"  {uf}: pacote inválido ({dst.stat().st_size/1048576:.0f} MB) — rebaixando", flush=True)
        dst.unlink(missing_ok=True)

    for t in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(BASE_URL.format(uf=uf), headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3600) as r:
                esperado = int(r.headers.get("Content-Length") or 0)
                with open(dst, "wb") as f:
                    while True:
                        ch = r.read(1 << 20)
                        if not ch:
                            break
                        f.write(ch)
            obtido = dst.stat().st_size
            if esperado and obtido != esperado:
                print(f"  {uf}: incompleto ({obtido/1048576:.0f}/{esperado/1048576:.0f} MB) tentativa {t}", flush=True)
                dst.unlink(missing_ok=True)
                continue
            if valido(dst):
                return dst
            print(f"  {uf}: ZIP inválido na tentativa {t}", flush=True)
            dst.unlink(missing_ok=True)
        except Exception as e:
            print(f"  {uf}: erro no download (tentativa {t}): {e}", flush=True)
            dst.unlink(missing_ok=True)
    raise RuntimeError(f"não foi possível baixar o pacote de {uf} após {tentativas} tentativas")


def eventos_log(raw_jez: bytes) -> list[tuple[datetime, str]]:
    """Retorna [(timestamp, marcador)] na ordem do arquivo: 'R' pronto, 'C' computado."""
    try:
        with zipfile.ZipFile(io.BytesIO(raw_jez)) as z:
            nome = next(n for n in z.namelist() if "logd" in n.lower())
            txt = z.read(nome).decode("latin1", "replace")
    except Exception:
        return []
    out = []
    for linha in txt.splitlines():
        if MSG_DONE in linha:
            marca = "C"
        elif MSG_READY in linha:
            marca = "R"
        else:
            continue
        try:
            ts = datetime.strptime(linha[:19], "%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue
        if (ts.day, ts.month, ts.year) != DIA_2T:
            continue
        out.append((ts, marca))
    return out


def sequencia_votos(raw_rdv: bytes, cargo_alvo: int = 1) -> list[int]:
    """Lista ordenada dos votos do cargo (1 = Presidente), no turno do arquivo.

    Em estados com segundo turno estadual a urna registra mais de um cargo no
    mesmo RDV; sem filtrar por cargo os votos de governador contaminam a conta.
    """
    try:
        root = der.parse(raw_rdv)
    except Exception:
        return []

    votos: list[int] = []

    def extrair_votos(no) -> None:
        def walk(n, d=0):
            if d > 18 or not getattr(n, "constructed", False):
                return
            f = n.children()
            if (len(f) in (1, 2) and f[0].tag_class == 0 and f[0].tag_number == 10
                    and (len(f) == 1 or f[1].tag_name == "NumericString")):
                if len(f) == 2:
                    try:
                        votos.append(int(f[1].value.decode()))
                    except (ValueError, AttributeError):
                        votos.append(0)
                else:
                    votos.append(0)
                return
            for x in f:
                walk(x, d + 1)
        walk(no)

    def procurar_cargos(no, d=0):
        if d > 14 or not getattr(no, "constructed", False):
            return False
        f = no.children()
        # nó de cargo: { [1] codigoCargo, INTEGER ordem, SEQUENCE votos }
        if (len(f) >= 3 and f[0].tag_class == 2 and f[0].tag_number == 1
                and getattr(f[2], "constructed", False)):
            try:
                codigo = f[0].as_int()
            except Exception:
                codigo = None
            if codigo == cargo_alvo:
                extrair_votos(f[2])
                return True
            return False
        for x in f:
            procurar_cargos(x, d + 1)
        return False

    procurar_cargos(root)
    return votos


def processar(uf: str, limite: int | None = None) -> dict:
    t0 = time.time()
    zp = baixar(uf)
    zf = zipfile.ZipFile(zp)
    logs = sorted(n for n in zf.namelist() if n.endswith("-log.jez"))
    if limite:
        logs = logs[:limite]

    LIMITES = (2, 4, 6, 8, 10)
    buckets = {t: 0 for t in LIMITES}
    total_votos = 0
    votos_6s = 0
    votos_10s = 0
    # somas para correlação por seção (taxa de votos rápidos x % de Lula)
    corr = {"n": 0, "sx": 0.0, "sy": 0.0, "sxy": 0.0, "sxx": 0.0, "syy": 0.0}
    secoes_com_6s = 0
    secoes_total = 0
    secoes_desalinhadas = 0
    sanduiche_secoes = 0
    sanduiche_votos_lula = 0
    sanduiche_votos_flavio = 0
    detalhes_6s = []
    detalhes_sanduiche = []

    for nome in logs:
        sec = nome[: -len("-log.jez")]
        secoes_total += 1
        try:
            ev = eventos_log(zf.read(nome))
            votos = sequencia_votos(zf.read(sec + "-rdv.dat"))
        except KeyError:
            continue

        # pareia habilitacao -> computado
        dur: list[float] = []
        pendente = None
        for ts, marca in ev:
            if marca == "R":
                pendente = ts
            elif marca == "C" and pendente is not None:
                dur.append((ts - pendente).total_seconds())
                pendente = None
        total_votos += len(dur)
        n6 = sum(1 for d in dur if d < 6.0)
        n10 = sum(1 for d in dur if d < 10.0)
        for t in LIMITES:
            buckets[t] += sum(1 for d in dur if d < t)
        votos_6s += n6
        votos_10s += n10
        if n6:
            secoes_com_6s += 1
            if len(detalhes_6s) < 5000:
                detalhes_6s.append({"secao": sec, "votos_abaixo_6s": n6,
                                    "tempo_total_registrado": round(sum(dur), 1),
                                    "votos": len(dur)})

        if len(votos) != len(dur):
            secoes_desalinhadas += 1
            continue

        # correlação por seção: taxa de votos rápidos vs proporção de Lula
        if votos:
            lula = sum(1 for x in votos if x == LULA)
            flavio = sum(1 for x in votos if x == FLAVIO)
            if lula + flavio >= 50:
                x = n6 / (lula + flavio)          # taxa de <6s na seção
                y = lula / (lula + flavio)        # proporção de Lula
                corr["n"] += 1; corr["sx"] += x; corr["sy"] += y
                corr["sxy"] += x * y; corr["sxx"] += x * x; corr["syy"] += y * y

        # padrão: bloco de Lula (>=3) -> bloco de Flávio (>=1) -> bloco de Lula (>=3)
        i = 0
        achou = False
        while i < len(votos):
            if votos[i] != LULA:
                i += 1
                continue
            a = i
            while i < len(votos) and votos[i] == LULA:
                i += 1
            bloco_a = i - a
            if bloco_a < 3 or i >= len(votos) or votos[i] != FLAVIO:
                continue
            b = i
            while i < len(votos) and votos[i] == FLAVIO:
                i += 1
            bloco_b = i - b
            c = i
            while i < len(votos) and votos[i] == LULA:
                i += 1
            bloco_c = i - c
            if bloco_c >= 3:
                achou = True
                sanduiche_votos_lula += bloco_a + bloco_c
                sanduiche_votos_flavio += bloco_b
                if len(detalhes_sanduiche) < 5000:
                    detalhes_sanduiche.append({
                        "secao": sec, "lula_antes": bloco_a, "flavio_meio": bloco_b,
                        "lula_depois": bloco_c, "posicao": a + 1, "total_secao": len(votos),
                    })
        if achou:
            sanduiche_secoes += 1

    res = {
        "uf": uf,
        "turno": 2,
        "ano": 2026,
        "secoes_processadas": secoes_total,
        "secoes_em_que_o_log_e_o_rdv_nao_casam": secoes_desalinhadas,
        "votos_computados": total_votos,
        "votos_abaixo_2s": buckets[2],
        "votos_abaixo_4s": buckets[4],
        "votos_abaixo_6s": buckets[6],
        "votos_abaixo_8s": buckets[8],
        "votos_abaixo_10s": buckets[10],
        "pct_abaixo_2s": round(buckets[2] / total_votos * 100, 3) if total_votos else 0,
        "pct_abaixo_4s": round(buckets[4] / total_votos * 100, 3) if total_votos else 0,
        "pct_abaixo_8s": round(buckets[8] / total_votos * 100, 3) if total_votos else 0,
        "correlacao_taxa_rapida_vs_lula": corr,
        "pct_abaixo_6s": round(votos_6s / total_votos * 100, 3) if total_votos else 0,
        "votos_abaixo_10s": votos_10s,
        "secoes_com_ao_menos_1_voto_abaixo_6s": secoes_com_6s,
        "sanduiche_lula_flavio_lula_secoes": None,
        "sanduiche_lula_flavio_lula_votos_lula": None,
        "sanduiche_lula_flavio_lula_votos_flavio": None,
        "sanduiche_observacao": ("NAO MENSURAVEL: o RDV agrupa os votos por candidato, sem ordem cronologica."),
        "tempo_s": round(time.time() - t0, 1),
        "detalhes_6s": detalhes_6s,
        "detalhes_sanduiche": detalhes_sanduiche,
    }
    (OUT / f"{uf}_2t_tempo.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--uf", default="RR")
    ap.add_argument("--limite", type=int, default=None)
    a = ap.parse_args()
    r = processar(a.uf, a.limite)
    r.pop("detalhes_6s", None)
    r.pop("detalhes_sanduiche", None)
    print(json.dumps(r, ensure_ascii=False, indent=2))
