"""Construcao de fixtures sinteticas (sem dados reais de eleicao)."""

from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path
from typing import Iterable

TARGET = "o03220sc8053500440144"
UF = "sc"
MUNICIPIO = 80535
ZONA = 44
SECAO = 144
CARGA = "000000000000000000000001"
URNA_ID = 2191040
PLEITO = 3220
ELEICAO = 6257
APTOS = 20
APTOS_SECAO = 15
APTOS_TTE = 5
COMPARECIMENTO = 13
ABERTURA = "20261004T080001"
ENCERRAMENTO = "20261004T170000"
EMISSAO = "20261004T170002"
ENVELOPE = "20261004T170006"
ASSINATURA = "20261004T170008"


# ---------------------------------------------------------------------------
# codificador DER minimo
# ---------------------------------------------------------------------------
def _length(size: int) -> bytes:
    if size < 0x80:
        return bytes([size])
    raw = size.to_bytes((size.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(raw)]) + raw


def tlv(tag: int, value: bytes) -> bytes:
    return bytes([tag]) + _length(len(value)) + value


def seq(*items: bytes) -> bytes:
    return tlv(0x30, b"".join(items))


def integer(value: int) -> bytes:
    size = max(1, (value.bit_length() + 8) // 8)
    return tlv(0x02, value.to_bytes(size, "big", signed=True))


def enum(value: int) -> bytes:
    size = max(1, (value.bit_length() + 8) // 8)
    return tlv(0x0A, value.to_bytes(size, "big", signed=True))


def octets(value: bytes) -> bytes:
    return tlv(0x04, value)


def general(value: str) -> bytes:
    return tlv(0x1B, value.encode("latin-1"))


def numeric(value: str) -> bytes:
    return tlv(0x12, value.encode("ascii"))


def ctx(number: int, value: bytes, *, constructed: bool = False) -> bytes:
    return tlv(0x80 | (0x20 if constructed else 0) | number, value)


def _content(data: bytes) -> bytes:
    """Conteudo de um TLV (para tag implicita que substitui a tag original)."""
    index = 1
    length = data[index]
    index += 1
    if length & 0x80:
        count = length & 0x7F
        index += count
    return data[index:]


def ctx_implicit(number: int, inner: bytes, *, constructed: bool = True) -> bytes:
    return ctx(number, _content(inner), constructed=constructed)


def ctx_value(number: int, encoded: bytes) -> bytes:
    """Tag de contexto primitiva implicita (substitui INTEGER/ENUMERATED)."""
    return ctx(number, _content(encoded))


# ---------------------------------------------------------------------------
# BU
# ---------------------------------------------------------------------------
def _chain(
    votos: list[tuple[int, int, int | None, int | None]],
) -> tuple[list[str], str]:
    """Calcula a cadeia SHA-512 documentada; devolve hashes e ultimo hash."""
    header = (
        f"{PLEITO:05d}|{ELEICAO:05d}|{MUNICIPIO:05d}|{ZONA:04d}|"
        f"{SECAO:04d}|{CARGA}"
    )
    current = hashlib.sha512(header.encode("ascii")).digest()
    hashes: list[str] = []
    for ordem, (tipo, qtd, numero, partido) in enumerate(votos, start=1):
        block = f"{current.hex().upper()}|{ordem}|1|{tipo}|{qtd}"
        if numero is not None:
            block += f"|{numero}|{partido}"
        current = hashlib.sha512(block.encode("ascii")).digest()
        hashes.append(current.hex().upper())
    return hashes, current.hex().upper()


def _voto(tipo: int, qtd: int, numero: int | None, partido: int | None, ordem: int, hash_hex: str) -> bytes:
    parts = [ctx_value(1, integer(tipo)), ctx_value(2, integer(qtd))]
    if numero is not None:
        parts.append(ctx_implicit(3, seq(integer(partido), integer(numero))))
    parts.append(integer(ordem))
    parts.append(octets(bytes.fromhex(hash_hex)))
    return seq(*parts)


def _secao_ident() -> bytes:
    return seq(seq(integer(MUNICIPIO), integer(ZONA)), integer(1236), integer(SECAO))


def _carga() -> bytes:
    return seq(
        integer(URNA_ID),
        octets(bytes.fromhex("B9152115")),
        seq(general("CSC044W057495"), general("54514D04F35BF8BD5435"), general("F59C5677")),
        general("20260922T145300"),
        general(CARGA),
    )


def _urna() -> bytes:
    return seq(
        enum(1),
        general("10.23.0.0 - TESTE SINTETICO"),
        seq(ctx_implicit(0, _secao_ident()), _carga()),
        enum(1),
        octets(bytes.fromhex("9A190E59")),
    )


def build_bu(
    *,
    comparecimento: int = COMPARECIMENTO,
    brancos: int = 2,
    nulos: int = 1,
    nominal: int = 10,
) -> bytes:
    votos = [(1, nominal, 22, 22), (2, brancos, None, None), (3, nulos, None, None)]
    hashes, last_hash = _chain(votos)
    total = nominal + brancos + nulos
    votos_nodes = [
        _voto(tipo, qtd, numero, partido, index + 1, hashes[index])
        for index, (tipo, qtd, numero, partido) in enumerate(votos)
    ]
    cargo = seq(ctx_value(1, integer(1)), integer(1), seq(*votos_nodes))
    resultado = seq(enum(1), integer(total), seq(cargo))
    eleicao = seq(
        integer(ELEICAO),
        integer(APTOS),
        integer(APTOS_SECAO),
        integer(APTOS_TTE),
        seq(resultado),
        octets(bytes.fromhex(last_hash)),
        octets(b"assinatura-do-ultimo-hash"),
    )
    detalhamento = ctx_implicit(1, seq(integer(2), integer(8), integer(3)))
    inner = seq(
        seq(general(EMISSAO), ctx_value(2, integer(PLEITO))),
        enum(2),
        _urna(),
        _secao_ident(),
        general(EMISSAO),
        ctx_implicit(0, seq(general(ABERTURA), general(ENCERRAMENTO))),
        integer(comparecimento),
        detalhamento,
        seq(eleicao),
        seq(general(CARGA)),
    )
    return seq(
        seq(general(ENVELOPE), ctx_value(2, integer(PLEITO))),
        enum(2),
        ctx_implicit(0, _secao_ident()),
        enum(1),
        octets(inner),
    )


# ---------------------------------------------------------------------------
# RDV
# ---------------------------------------------------------------------------
def build_rdv() -> bytes:
    def voto(tipo: int, digitacao: str | None = None) -> bytes:
        parts = [enum(tipo)]
        if digitacao is not None:
            parts.append(numeric(digitacao))
        return seq(*parts)

    votos = [voto(2, "22") for _ in range(10)] + [voto(3), voto(3), voto(4)]
    cargo = seq(ctx_value(1, integer(1)), integer(1), seq(*votos))
    eleicao = seq(integer(ELEICAO), seq(cargo))
    corpo = seq(
        integer(PLEITO),
        enum(2),
        _secao_ident(),
        seq(general(CARGA)),
        ctx_implicit(1, seq(eleicao)),
    )
    return seq(
        seq(general(EMISSAO), ctx_value(2, integer(PLEITO))),
        _urna(),
        corpo,
    )


# ---------------------------------------------------------------------------
# assinatura
# ---------------------------------------------------------------------------
def _assinatura_list(hashes: dict[str, str]) -> bytes:
    entries = []
    for name, sha in hashes.items():
        entries.append(
            seq(
                general(name),
                seq(integer(64), octets(bytes.fromhex(sha)), octets(b"assinatura-sintetica")),
            )
        )
    return seq(seq(*entries))


def _entidade(
    conteudo: bytes,
    usuario: str,
    alg_ass: int = 3,
    bits: int = 256,
) -> bytes:
    auto = seq(
        seq(general(usuario), integer(URNA_ID if usuario == "UEAO" else 20260708)),
        seq(enum(4)),
        seq(enum(alg_ass), integer(bits)),
        seq(
            integer(len(conteudo)),
            octets(hashlib.sha512(conteudo).digest()),
            octets(b"assinatura-auto-sintetica"),
        ),
    )
    return seq(
        general(ASSINATURA),
        integer(2),
        auto,
        octets(conteudo),
        ctx(0, general("202607021654")),
    )


def build_vsc(hashes: dict[str, str]) -> bytes:
    conteudo = _assinatura_list(hashes)
    sw = _entidade(conteudo, "SEVIN", alg_ass=3, bits=256)
    hw = _entidade(conteudo, "UEAO", alg_ass=4, bits=521)
    return seq(sw, hw, seq(enum(20), enum(4)))


# ---------------------------------------------------------------------------
# log
# ---------------------------------------------------------------------------
def build_log() -> bytes:
    entries = [
        ("22/09/2026 10:00:00", "INFO", "LOGD", "Início das operações do logd"),
        ("22/09/2026 10:00:01", "INFO", "LOGD", "Urna ligada em 22/09/2026 às 09:59:00"),
        ("04/10/2026 07:20:00", "INFO", "LOGD", "Início das operações do logd"),
        ("04/10/2026 07:20:02", "INFO", "LOGD", "Urna ligada em 04/10/2026 às 07:19:00"),
        ("04/10/2026 07:21:00", "INFO", "GAP", "Município: 80535"),
        ("04/10/2026 07:21:01", "INFO", "GAP", "Zona Eleitoral: 0044"),
        ("04/10/2026 07:21:02", "INFO", "GAP", "Local de Votação: 1236"),
        ("04/10/2026 07:21:03", "INFO", "GAP", "Seção Eleitoral: 0144"),
        ("04/10/2026 07:21:10", "INFO", "SCUE", "Versão da aplicação: 10.23.0.0 - TESTE SINTETICO"),
        ("04/10/2026 08:00:01", "INFO", "VOTA", "Urna pronta para receber votos"),
    ]
    for index in range(13):
        entries.append(
            (
                f"04/10/2026 08:10:{index:02d}",
                "INFO",
                "VOTA",
                "O voto do eleitor foi computado",
            )
        )
    entries += [
        ("04/10/2026 16:59:00", "INFO", "VOTA", "Operador selecionou: Encerrar votação"),
        ("04/10/2026 17:00:00", "INFO", "VOTA", "Procedimento de encerramento confirmado"),
        ("04/10/2026 17:00:01", "INFO", "VOTA", "Início do Encerramento"),
        ("04/10/2026 17:00:02", "INFO", "VOTA", "Gerando relatório [BU] [INÍCIO]"),
        ("04/10/2026 17:00:03", "INFO", "VOTA", "Gerando relatório [BU] [TÉRMINO]"),
        ("04/10/2026 17:00:04", "INFO", "VOTA", "Início de impressão"),
        ("04/10/2026 17:00:05", "INFO", "VOTA", "Fim de impressão"),
        ("04/10/2026 17:00:06", "INFO", "VOTA", "Gerando arquivo de resultado [bu.dat] + [Início]"),
        ("04/10/2026 17:00:06", "INFO", "VOTA", "Gerando arquivo de resultado [bu.dat] + [Término]"),
        ("04/10/2026 17:00:07", "INFO", "VOTA", "Gerando arquivo de resultado [log.jez] + [Início]"),
    ]
    lines = [
        f"{stamp}\t{level}\t02191040\t{module}\t{message}\t{index + 1:016X}"
        for index, (stamp, level, module, message) in enumerate(entries)
    ]
    return ("\r\n".join(lines) + "\r\n").encode("latin-1")


def build_jez(log: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("logd.dat", date_time=(2026, 10, 4, 17, 0, 7))
        archive.writestr(info, log)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# BU impresso (spool)
# ---------------------------------------------------------------------------
def build_imgbu() -> bytes:
    spool = """   Justiça Eleitoral
    Tribunal Regional Eleitoral [SC]

           Boletim de Urna

         Eleições Gerais 2026
               1° Turno
             (04/10/2026)

Município                        80535
            BRAÇO DO NORTE

Zona Eleitoral                    0044
Local de Votação                  1236
Seção Eleitoral                   0144

Eleitores aptos                   0020
          Originais da seção      0015
          Temporários na seção    0005
Comparecimento                    0013
        Habilitação biométrica    0008
        Habilitação biográfica    0003
        Habilitação sem biometria 0002

Código identificação UE       02191040
Data de abertura da UE      04/10/2026
Horário de abertura           08:00:01
Data de fechamento da UE    04/10/2026
Horário de fechamento         17:00:00

-----------PRESIDENTE-----------
Partido: 22 - PL
Nome do candidato       Num cand Votos

  CANDIDATO TESTE           22  0010
    Votos de legenda              0000
    Total do partido              0010

Total de votos Nominais           0010
Total de votos de Legenda         0000
Brancos                           0002
Nulos                             0001
Total Apurado                     0013

   Código de identificação da carga
   000.000.000.000.000.000.000.001
"""
    content = spool.encode("latin-1").replace(b"\n", b"\r\n")
    inner = seq(
        seq(general(EMISSAO), ctx_value(2, integer(PLEITO))),
        enum(2),
        _urna(),
        _secao_ident(),
        enum(4),
        octets(content),
    )
    return seq(
        seq(general(ENVELOPE), ctx_value(2, integer(PLEITO))),
        enum(2),
        _urna(),
        ctx_implicit(0, _secao_ident()),
        enum(4),
        octets(inner),
    )


def build_tree(root: Path) -> dict[str, Path]:
    """Cria a arvore sintetica e devolve nome logico -> caminho."""
    root.mkdir(parents=True, exist_ok=True)
    bu = build_bu()
    rdv = build_rdv()
    log = build_log()
    imgbu = build_imgbu()
    jez = build_jez(log)
    files = {
        "bu": root / f"{TARGET}-bu.dat",
        "rdv": root / f"{TARGET}-rdv.dat",
        "log": root / f"{TARGET}-log.jez",
        "imgbu": root / f"{TARGET}-imgbu.dat",
    }
    hashes = {
        files["bu"].name: hashlib.sha512(bu).hexdigest(),
        files["rdv"].name: hashlib.sha512(rdv).hexdigest(),
        files["log"].name: hashlib.sha512(jez).hexdigest(),
        files["imgbu"].name: hashlib.sha512(imgbu).hexdigest(),
    }
    files["vota"] = root / f"{TARGET}-vota.vsc"
    vsc = build_vsc(hashes)
    files["bu"].write_bytes(bu)
    files["rdv"].write_bytes(rdv)
    files["log"].write_bytes(jez)
    files["imgbu"].write_bytes(imgbu)
    files["vota"].write_bytes(vsc)
    return files
