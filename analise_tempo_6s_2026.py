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
OUT = Path("data/tempo_2026")
OUT.mkdir(parents=True, exist_ok=True)

LULA, FLAVIO = 13, 22
MSG_READY = "Eleitor foi habilitado"
MSG_DONE = "O voto do eleitor foi computado"
DIA_2T = (25, 10, 2026)   # data oficial do 2º turno de 2026


def baixar(uf: str) -> Path:
    DDIR.mkdir(parents=True, exist_ok=True)
    dst = DDIR / f"{uf}_2t.zip"
    if dst.exists() and dst.stat().st_size > 10_000_000:
        return dst
    req = urllib.request.Request(BASE_URL.format(uf=uf), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=3600) as r, open(dst, "wb") as f:
        while True:
            ch = r.read(1 << 20)
            if not ch:
                break
            f.write(ch)
    return dst


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


def sequencia_votos(raw_rdv: bytes) -> list[int]:
    """Lista ordenada do número votado por voto computado (13/22/95/96...)."""
    try:
        root = der.parse(raw_rdv)
    except Exception:
        return []

    votos: list[int] = []

    def procurar(no, prof=0):
        if prof > 12 or not getattr(no, "constructed", False):
            return
        filhos = no.children()
        # Um Voto = SEQUENCE { [1] tipoVoto, INTEGER numero }
        if (len(filhos) in (1, 2) and filhos[0].tag_class == 0 and filhos[0].tag_number == 10
                and (len(filhos) == 1 or filhos[1].tag_name == "NumericString")):
            if len(filhos) == 2:
                try:
                    votos.append(int(filhos[1].value.decode()))
                except (ValueError, AttributeError):
                    votos.append(0)
            else:
                votos.append(0)
            return
        for f in filhos:
            procurar(f, prof + 1)

    procurar(root)
    return votos


def processar(uf: str, limite: int | None = None) -> dict:
    t0 = time.time()
    zp = baixar(uf)
    zf = zipfile.ZipFile(zp)
    logs = sorted(n for n in zf.namelist() if n.endswith("-log.jez"))
    if limite:
        logs = logs[:limite]

    total_votos = 0
    votos_6s = 0
    votos_10s = 0
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
        "votos_abaixo_6s": votos_6s,
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
