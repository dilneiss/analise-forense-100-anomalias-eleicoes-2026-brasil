from __future__ import annotations

from urna_forense.cli import main


def test_cli_list(urna, tmp_path, capsys):
    input_dir, _ = urna
    code = main(["--input", str(input_dir), "--list"])
    assert code == 0
    out = capsys.readouterr().out
    assert "1 urna(s) encontrada(s)" in out
    assert "SC-80535-0044-0144" in out


def test_cli_end_to_end_positional(urna, tmp_path, capsys):
    input_dir, _ = urna
    output_dir = tmp_path / "analysis"
    code = main(
        [
            str(input_dir),
            "--output",
            str(output_dir),
            "--uf",
            "sc",
            "--zona",
            "44",
            "--secao",
            "144",
            "--turno",
            "1",
            "--data-eleicao",
            "2026-10-04",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "ANALISE DA URNA" in out
    assert (output_dir / "report.json").is_file()
    assert (output_dir / "report.html").is_file()


def test_cli_requires_csv_for_municipio_name(urna, tmp_path, capsys):
    input_dir, _ = urna
    code = main(["--input", str(input_dir), "--municipio", "Braço do Norte"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--municipios-csv" in err


def test_cli_all(urna, tmp_path, capsys):
    input_dir, _ = urna
    output_dir = tmp_path / "analysis_all"
    code = main(["--input", str(input_dir), "--output", str(output_dir), "--all"])
    assert code == 0
    out = capsys.readouterr().out
    assert "RELATÓRIO GERAL CONSOLIDADO" in out
    assert (output_dir / "general_report.json").is_file()
    assert (output_dir / "general_report.html").is_file()
