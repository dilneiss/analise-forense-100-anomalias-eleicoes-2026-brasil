from __future__ import annotations

import json
import shutil
from datetime import date

import pytest

from fixtures_build import TARGET, build_bu, build_tree
from urna_forense.pipeline import AnalysisError, Config, run


def test_pipeline_end_to_end_generates_all_artifacts(urna, tmp_path):
    input_dir, files = urna
    output_dir = tmp_path / "analysis"
    cfg = Config(
        input_dir=input_dir,
        output_dir=output_dir,
        uf="sc",
        municipio=80535,
        zona=44,
        secao=144,
        turno=1,
        data_eleicao=date(2026, 10, 4),
        hash_scope="all",
    )
    result = run(cfg)
    assert result.output_dir == output_dir
    assert "ANALISE DA URNA" in result.console

    expected_files = [
        "manifest.json",
        "inventory.json",
        "timeline.json",
        "integrity.json",
        "consistency.json",
        "bu.json",
        "rdv.json",
        "signatures.json",
        "report.json",
        "report.html",
    ]
    for name in expected_files:
        assert (output_dir / name).is_file(), f"ausente: {name}"

    bu_doc = json.loads((output_dir / "bu.json").read_text(encoding="utf-8"))
    assert bu_doc["secao"] == 144
    assert bu_doc["zona"] == 44
    assert bu_doc["comparecimento"] == 13
    assert bu_doc["aptos"] == 20
    assert "candidatos" in bu_doc
    assert (output_dir / "extracted" / "logd.dat").is_file()
    assert (output_dir / "extracted" / "imgbu_spool.txt").is_file()

    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["files"] == len(files)
    assert manifest["counts"]["hashed_files"] == len(files)
    assert manifest["read_only"] is True

    # Reexecucao: compara manifestos e relata 0 alteracoes
    result2 = run(cfg)
    comp = result2.report["previous_run_comparison"]
    assert comp["status"] == "comparado"
    assert len(comp["changed"]) == 0
    assert comp["unchanged"] == len(files)


def test_pipeline_detects_tampering_between_runs(urna, tmp_path):
    input_dir, files = urna
    output_dir = tmp_path / "analysis"
    cfg = Config(
        input_dir=input_dir,
        output_dir=output_dir,
        uf="sc",
        municipio=80535,
        zona=44,
        secao=144,
        turno=1,
        data_eleicao=date(2026, 10, 4),
    )
    run(cfg)

    # Modifica o BU no input
    files["bu"].write_bytes(build_bu(comparecimento=14, nominal=11))

    result2 = run(cfg)
    comp = result2.report["previous_run_comparison"]
    assert len(comp["changed"]) == 1
    assert comp["changed"][0]["path"] == files["bu"].name
    types = {f["type"] for f in result2.report["findings"]}
    assert "EVIDENCIA_ALTERADA_ENTRE_EXECUCOES" in types


def test_pipeline_refuses_output_inside_input(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = input_dir / "analysis"
    cfg = Config(input_dir=input_dir, output_dir=output_dir)
    with pytest.raises(AnalysisError, match="dentro da evidencia"):
        run(cfg)


def test_pipeline_selection_error_when_multiple_urnas(tmp_path):
    input_dir = tmp_path / "input"
    build_tree(input_dir)
    # Cria uma segunda urna duplicando com outro nome de secao
    for p in list(input_dir.iterdir()):
        new_name = p.name.replace("0144", "0145")
        (input_dir / new_name).write_bytes(p.read_bytes())

    output_dir = tmp_path / "analysis"
    # Sem especificar a secao, deve recusar selecao ambigua
    cfg = Config(input_dir=input_dir, output_dir=output_dir, uf="sc", zona=44)
    with pytest.raises(AnalysisError, match="correspondem aos filtros"):
        run(cfg)
