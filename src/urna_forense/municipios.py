"""Resolucao de municipios pela tabela oficial do TSE (CSV opcional).

O nome do municipio NAO existe nos arquivos da urna; ele so pode ser
resolvido com uma tabela externa. Sem a tabela, a ferramenta mostra o codigo
TSE e diz que o nome nao foi resolvido.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .analysis.consistency import normalize_name


@dataclass(frozen=True)
class Municipio:
    uf: str
    codigo_tse: int
    nome: str
    codigo_ibge: Optional[int] = None

    def as_dict(self) -> dict[str, object]:
        return {
            "uf": self.uf,
            "codigo_tse": self.codigo_tse,
            "nome": self.nome,
            "codigo_ibge": self.codigo_ibge,
        }


def load_table(path: Path) -> dict[tuple[str, int], Municipio]:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - defensivo
        raise ValueError(f"nao foi possivel decodificar {path}")
    table: dict[tuple[str, int], Municipio] = {}
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    for row in reader:
        try:
            uf = (row["SG_UF"] or "").strip().lower()
            code = int((row["CD_MUNICIPIO_TSE"] or "").strip())
            name = (row["NM_MUNICIPIO_TSE"] or "").strip()
        except (KeyError, ValueError, AttributeError):
            continue
        ibge_raw = (row.get("CD_MUNICIPIO_IBGE") or "").strip()
        ibge = int(ibge_raw) if ibge_raw.isdigit() else None
        table[(uf, code)] = Municipio(uf, code, name, ibge)
    return table


def resolve(
    table: dict[tuple[str, int], Municipio],
    *,
    uf: Optional[str],
    municipio: str | int | None,
) -> Optional[Municipio]:
    if municipio is None:
        return None
    text = str(municipio).strip()
    if text.isdigit():
        code = int(text)
        candidates = [
            item for (item_uf, item_code), item in table.items() if item_code == code
        ]
        if uf:
            candidates = [item for item in candidates if item.uf == uf.lower()]
        return candidates[0] if len(candidates) == 1 else None
    wanted = normalize_name(text)
    matches = [
        item
        for item in table.values()
        if normalize_name(item.nome) == wanted and (not uf or item.uf == uf.lower())
    ]
    return matches[0] if len(matches) == 1 else None
