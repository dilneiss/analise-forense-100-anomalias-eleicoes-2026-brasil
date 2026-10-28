#!/usr/bin/env python3
"""Ponto de entrada da ferramenta de auditoria da urna eletronica."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))

from urna_forense.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
