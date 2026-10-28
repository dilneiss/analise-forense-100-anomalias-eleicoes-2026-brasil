"""Escrita dos relatorios JSON (separada da orquestracao)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write(path: Path, data: Any) -> None:
    path.write_text(dumps(data), encoding="utf-8")
