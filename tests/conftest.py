from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fixtures_build import build_tree  # noqa: E402


@pytest.fixture()
def urna(tmp_path):
    root = tmp_path / "input"
    files = build_tree(root)
    return root, files


@pytest.fixture()
def analysis(urna, tmp_path):
    from urna_forense.pipeline import Config, run

    input_dir, files = urna
    output = tmp_path / "analysis"
    config = Config(
        input_dir=input_dir,
        output_dir=output,
        uf="sc",
        municipio=80535,
        zona=44,
        secao=144,
        turno=1,
        data_eleicao=__import__("datetime").date(2026, 10, 4),
    )
    return run(config), input_dir, output
