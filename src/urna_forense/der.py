"""Leitor ASN.1 BER/DER estrito o suficiente para os arquivos da urna.

Nao interpreta o significado dos campos: apenas a estrutura TLV (tag,
comprimento, valor). Os modulos ``parsers`` mapeiam a estrutura segundo as
especificacoes do TSE.

Formatos com comprimento indefinido (BER indefinido) nao aparecem nos
arquivos da urna; se aparecerem, o erro e explicito em vez de silencioso.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional

__all__ = [
    "DerError",
    "Node",
    "parse",
    "parse_children",
    "pretty",
]

_CLASSES = {0: "universal", 1: "application", 2: "context", 3: "private"}


class DerError(ValueError):
    """Estrutura BER/DER invalida ou truncada."""


@dataclass(frozen=True)
class Node:
    """Um elemento TLV dentro de um buffer."""

    buf: bytes
    start: int  # offset do primeiro byte da tag
    value_start: int  # offset do primeiro byte do valor
    end: int  # offset logo apos o ultimo byte do valor
    tag_class: int
    constructed: bool
    tag_number: int

    # -- identidade ---------------------------------------------------------
    @property
    def length(self) -> int:
        return self.end - self.value_start

    @property
    def header_length(self) -> int:
        return self.value_start - self.start

    @property
    def raw(self) -> bytes:
        return self.buf[self.start:self.end]

    @property
    def value(self) -> bytes:
        return self.buf[self.value_start:self.end]

    @property
    def tag_name(self) -> str:
        """Nome curto: ``SEQUENCE``, ``[0]``, ``INTEGER``..."""
        if self.tag_class == 0:
            return _UNIVERSAL_NAMES.get(self.tag_number, f"UNIVERSAL[{self.tag_number}]")
        prefix = _CLASSES[self.tag_class]
        if self.tag_class == 2:
            return f"[{self.tag_number}]"
        return f"{prefix}[{self.tag_number}]"

    @property
    def is_universal(self) -> bool:
        return self.tag_class == 0

    # -- acesso a filhos ----------------------------------------------------
    def children(self) -> list["Node"]:
        if not self.constructed:
            return []
        return parse_children(self.buf, self.value_start, self.end)

    def child(self, index: int) -> "Node":
        kids = self.children()
        try:
            return kids[index]
        except IndexError as exc:  # pragma: no cover - mensagem de diagnostico
            raise DerError(
                f"{self.tag_name} nao tem filho {index} (tem {len(kids)})"
            ) from exc

    def find(self, tag_number: int, tag_class: int = 2) -> Optional["Node"]:
        for node in self.children():
            if node.tag_class == tag_class and node.tag_number == tag_number:
                return node
        return None

    def findall(self, tag_number: int, tag_class: int = 2) -> Iterator["Node"]:
        for node in self.children():
            if node.tag_class == tag_class and node.tag_number == tag_number:
                yield node

    # -- valores ------------------------------------------------------------
    def as_int(self) -> int:
        """Inteiro de um INTEGER/ENUMERATED, inclusive com tag implicita.

        Nos modulos do TSE ha ``IMPLICIT TAGS`` e varios campos aparecem com
        tag de contexto (ex.: ``[1] TipoVoto``); nesses casos o valor e o
        proprio conteudo do primitivo.
        """
        universal_int = self.tag_class == 0 and self.tag_number in (2, 10)
        implicit = self.tag_class == 2 and not self.constructed
        if not (universal_int or implicit):
            raise DerError(f"{self.tag_name} nao e INTEGER/ENUMERATED")
        if not self.value:
            raise DerError("INTEGER vazio")
        return int.from_bytes(self.value, "big", signed=True)

    def as_octets(self) -> bytes:
        if self.tag_class == 0 and self.tag_number == 4:  # OCTET STRING
            return self.value
        if self.tag_class == 2 and not self.constructed:  # implicito
            return self.value
        raise DerError(f"{self.tag_name} nao e OCTET STRING")

    def as_text(self) -> str:
        """Decodifica strings ASN.1 (GeneralString, UTF8, Numeric, ...)."""
        raw = self.value
        if self.tag_number == 30:  # BMPString
            return raw.decode("utf-16-be", errors="replace")
        for encoding in ("utf-8", "latin-1"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("latin-1", errors="replace")

    def as_bool(self) -> bool:
        if not self.is_universal or self.tag_number != 1:
            raise DerError(f"{self.tag_name} nao e BOOLEAN")
        return self.value != b"\x00"

    def __repr__(self) -> str:  # pragma: no cover - conveniencia
        return (
            f"<Node {self.tag_name} len={self.length} "
            f"@{self.start}-{self.end}>"
        )


_UNIVERSAL_NAMES = {
    1: "BOOLEAN",
    2: "INTEGER",
    3: "BIT STRING",
    4: "OCTET STRING",
    5: "NULL",
    6: "OID",
    10: "ENUMERATED",
    12: "UTF8String",
    16: "SEQUENCE",
    17: "SET",
    18: "NumericString",
    19: "PrintableString",
    20: "TeletexString",
    22: "IA5String",
    23: "UTCTime",
    24: "GeneralizedTime",
    26: "VisibleString",
    27: "GeneralString",
    30: "BMPString",
}


def _read_tag(buf: bytes, offset: int) -> tuple[int, int, bool, int]:
    if offset >= len(buf):
        raise DerError(f"fim do buffer lendo tag @{offset}")
    first = buf[offset]
    tag_class = (first & 0xC0) >> 6
    constructed = bool(first & 0x20)
    number = first & 0x1F
    cursor = offset + 1
    if number == 0x1F:  # high-tag-number form
        number = 0
        while True:
            if cursor >= len(buf):
                raise DerError(f"tag truncada @{offset}")
            byte = buf[cursor]
            cursor += 1
            number = (number << 7) | (byte & 0x7F)
            if not byte & 0x80:
                break
    return tag_class, number, constructed, cursor


def _read_length(buf: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(buf):
        raise DerError(f"fim do buffer lendo comprimento @{offset}")
    first = buf[offset]
    cursor = offset + 1
    if first < 0x80:
        return first, cursor
    count = first & 0x7F
    if count == 0:
        raise DerError(f"comprimento BER indefinido @{offset} nao suportado")
    if count > 4:
        raise DerError(f"comprimento BER com {count} bytes @{offset}")
    if cursor + count > len(buf):
        raise DerError(f"comprimento truncado @{offset}")
    length = int.from_bytes(buf[cursor:cursor + count], "big")
    return length, cursor + count


def parse_tlv(buf: bytes, offset: int = 0) -> tuple[Node, int]:
    """Le um TLV em ``offset``; devolve o no e o offset seguinte."""
    tag_class, number, constructed, after_tag = _read_tag(buf, offset)
    length, value_start = _read_length(buf, after_tag)
    end = value_start + length
    if end > len(buf):
        raise DerError(
            f"TLV truncado @{offset}: comprimento {length} passa do buffer "
            f"({len(buf)})"
        )
    return (
        Node(
            buf=buf,
            start=offset,
            value_start=value_start,
            end=end,
            tag_class=tag_class,
            constructed=constructed,
            tag_number=number,
        ),
        end,
    )


def parse_children(buf: bytes, start: int, end: int) -> list[Node]:
    out: list[Node] = []
    cursor = start
    while cursor < end:
        node, cursor = parse_tlv(buf, cursor)
        out.append(node)
    if cursor != end:  # pragma: no cover - defensivo
        raise DerError(f"filhos terminam em {cursor}, esperado {end}")
    return out


def parse(buf: bytes, *, require_all: bool = True) -> Node:
    """Interpreta ``buf`` como um unico elemento DER."""
    node, end = parse_tlv(buf, 0)
    if require_all and end != len(buf):
        raise DerError(
            f"{len(buf) - end} byte(s) apos o elemento raiz (@{end})"
        )
    return node


def pretty(
    node: Node,
    *,
    max_depth: int = 6,
    max_value: int = 48,
    _depth: int = 0,
) -> str:
    """Arvore legivel do TLV, com offsets. Util para diagnostico."""
    indent = "  " * _depth
    if node.constructed:
        head = f"{indent}{node.tag_name} @{node.start} len={node.length}"
        if _depth >= max_depth:
            return head + " ..."
        kids = node.children()
        lines = [head]
        for kid in kids:
            lines.append(
                pretty(
                    kid,
                    max_depth=max_depth,
                    max_value=max_value,
                    _depth=_depth + 1,
                )
            )
        return "\n".join(lines)

    value = node.value
    if node.tag_class == 0 and node.tag_number in (2, 10):
        shown = str(int.from_bytes(value, "big", signed=True))
    elif node.tag_class == 0 and node.tag_number in (12, 18, 19, 20, 22, 26, 27, 30):
        shown = repr(node.as_text())
    else:
        shown = value[:max_value].hex(" ")
        if len(value) > max_value:
            shown += f" ... ({len(value)} bytes)"
        else:
            shown += f" ({len(value)} bytes)"
    return f"{indent}{node.tag_name} @{node.start} len={node.length}: {shown}"
