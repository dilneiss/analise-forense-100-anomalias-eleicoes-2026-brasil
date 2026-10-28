"""Interface de linha de comando."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from . import __version__
from .municipios import load_table, resolve
from .pipeline import AnalysisError, Config, run
from .scanner import group_urnas, scan, select_urna


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyzer.py",
        description=(
            "Auditoria tecnica, em modo somente leitura, dos arquivos de uma "
            "urna eletronica (BU, RDV, log, BU impresso e assinatura)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python analyzer.py ./input\n"
            "  python analyzer.py --input ./input --output ./analysis\n"
            "  python analyzer.py --input ./urna --municipios-csv municipio_tse_ibge.csv \\\n"
            "      --uf SC --municipio 'Braco do Norte' --zona 44 --secao 144 \\\n"
            "      --turno 1 --data-eleicao 2026-10-04\n"
            "  python analyzer.py --input ./urna --list\n"
        ),
    )
    parser.add_argument("input_pos", nargs="?", help="pasta de evidencia (input/)")
    parser.add_argument("-i", "--input", dest="input_opt", help="pasta de evidencia")
    parser.add_argument(
        "-o", "--output", default="analysis", help="pasta de saida (padrao: analysis)"
    )
    parser.add_argument("--uf", help="UF da urna (ex.: SC)")
    parser.add_argument(
        "--municipio",
        help="codigo TSE (ex.: 80535) ou nome, com --municipios-csv",
    )
    parser.add_argument("--zona", type=int, help="zona eleitoral")
    parser.add_argument("--secao", type=int, help="secao eleitoral")
    parser.add_argument("--turno", type=int, choices=(1, 2), help="turno esperado")
    parser.add_argument(
        "--data-eleicao", help="data esperada da eleicao (AAAA-MM-DD)"
    )
    parser.add_argument(
        "--municipios-csv",
        help="CSV oficial do TSE (municipio_tse_ibge.csv) para resolver o nome",
    )
    parser.add_argument(
        "--ca",
        action="append",
        default=[],
        help="arquivo ou pasta com certificados das AC (pode repetir)",
    )
    parser.add_argument(
        "--hash-scope",
        choices=("all", "target"),
        default="all",
        help="calcular SHA-256/512 de todos os arquivos (padrao) ou so da urna",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        choices=("all", "hash", "timeline", "verify", "report"),
        default=["all"],
        help="restringe os artefatos gerados",
    )
    parser.add_argument("--hash", action="store_true", help="alias de --only hash")
    parser.add_argument("--timeline", action="store_true", help="alias de --only timeline")
    parser.add_argument("--verify", action="store_true", help="alias de --only verify")
    parser.add_argument("--report", action="store_true", help="alias de --only report")
    parser.add_argument("--list", action="store_true", help="lista urnas sem analisar")
    parser.add_argument("--limit", type=int, default=50, help="limite do --list")
    parser.add_argument("-q", "--quiet", action="store_true", help="sem progresso")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="modo ultra-rapido (<1s): localiza diretamente os arquivos da urna alvo",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="executa o relatorio geral consolidado de todas as urnas da pasta",
    )
    parser.add_argument("--no-html", action="store_true", help="nao gerar report.html")
    parser.add_argument(
        "--audit-state",
        nargs=2,
        metavar=("PASTA_1T", "PASTA_2T"),
        help="comando unico para auditoria completa e unificada do estado (1T e 2T)",
    )
    parser.add_argument(
        "--compare-1t",
        "--1t",
        dest="compare_1t",
        help="pasta de evidencia do 1º Turno para analise comparativa de inconsistencias",
    )
    parser.add_argument(
        "--compare-2t",
        "--2t",
        dest="compare_2t",
        help="pasta de evidencia do 2º Turno para analise comparativa de inconsistencias",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=32,
        help="quantidade de threads para processamento concorrente (padrao: 32)",
    )
    return parser


def _parse_date(text: Optional[str]) -> Optional[date]:
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise AnalysisError(
            f"--data-eleicao invalida: {text!r} (use AAAA-MM-DD)"
        ) from exc


def _municipio(
    value: Optional[str], uf: Optional[str], csv_path: Optional[str]
) -> tuple[Optional[int], Optional[str]]:
    if not value:
        return None, None
    if value.isdigit():
        return int(value), None
    if not csv_path:
        raise AnalysisError(
            "para usar o nome do municipio informe --municipios-csv com a tabela "
            "oficial do TSE, ou passe o codigo TSE"
        )
    table = load_table(Path(csv_path))
    found = resolve(table, uf=uf, municipio=value)
    if found is None:
        raise AnalysisError(
            f"municipio {value!r} nao encontrado na tabela"
            + (f" para a UF {uf}" if uf else "")
        )
    return found.codigo_tse, found.nome


def _list(
    input_dir: Path,
    output_dir: Path,
    municipio: Optional[int],
    args: argparse.Namespace,
) -> int:
    if not input_dir.is_dir():
        raise AnalysisError(f"entrada nao e diretorio: {input_dir}")
    scanned = scan(
        input_dir,
        exclude=output_dir if output_dir.exists() else None,
        compute_hashes=False,
    )
    urnas = group_urnas(scanned.files)
    matches = select_urna(
        urnas, uf=args.uf, municipio=municipio, zona=args.zona, secao=args.secao
    )
    print(f"{len(matches)} urna(s) encontrada(s) de {len(urnas)} no diretorio")
    print(f"{'URNA':<28} {'BU':<3} {'RDV':<4} {'LOG':<4} {'VSC':<4} {'IMGBU':<5}")
    for key in matches[: args.limit]:
        entry = urnas[key]
        marks = [
            "x" if kind in entry else "-"
            for kind in ("bu", "rdv", "log", "vota", "imgbu")
        ]
        print(f"{key.compact:<28} {marks[0]:<3} {marks[1]:<4} {marks[2]:<4} {marks[3]:<4} {marks[4]:<5}")
    if len(matches) > args.limit:
        print(f"... {len(matches) - args.limit} outra(s); use --limit")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    args = _parser().parse_args(argv)
    if args.audit_state:
        args.compare_1t = args.audit_state[0]
        args.compare_2t = args.audit_state[1]

    # Auto-resolucao da tabela de municipios para comparacao/auditoria estadual
    if not args.municipios_csv and (args.compare_1t or args.compare_2t or args.audit_state):
        candidate_csv = Path("data/municipio_tse_ibge.csv")
        if not candidate_csv.is_file():
            candidate_csv = Path(__file__).resolve().parent.parent.parent / "data" / "municipio_tse_ibge.csv"
        if candidate_csv.is_file():
            args.municipios_csv = str(candidate_csv)

    input_arg = args.input_opt or args.input_pos
    is_comparison = bool(args.compare_1t or args.compare_2t)
    if is_comparison:
        if not (args.compare_1t and args.compare_2t):
            _parser().error("para comparar turnos informe ambas as pastas: --compare-1t e --compare-2t")
    elif not input_arg:
        _parser().error("informe a pasta de entrada (posicional ou --input)")

    input_dir = Path(input_arg) if input_arg else Path(".")
    default_out = "relatorio_auditoria_estado" if is_comparison and args.output == "analysis" else args.output
    output_dir = Path(default_out)
    try:
        data_eleicao = _parse_date(args.data_eleicao)
        municipio, municipio_nome = _municipio(
            args.municipio, args.uf, args.municipios_csv
        )
        if args.list:
            return _list(input_dir, output_dir, municipio, args)
        if is_comparison:
            from .comparison import ComparisonConfig, run_comparison

            comp_cfg = ComparisonConfig(
                input_dir_1t=Path(args.compare_1t),
                input_dir_2t=Path(args.compare_2t),
                output_dir=output_dir,
                uf=args.uf,
                municipio=municipio,
                municipio_nome=municipio_nome,
                zona=args.zona,
                secao=args.secao,
                municipios_csv=Path(args.municipios_csv) if args.municipios_csv else None,
                max_workers=args.max_workers,
                quiet=args.quiet,
                write_html=not args.no_html,
            )
            comp_res = run_comparison(comp_cfg)
            print(comp_res.console)
            return 0

        if args.all:
            from .general import run_general

            res_general = run_general(
                input_dir=input_dir,
                output_dir=output_dir,
                municipios_csv=Path(args.municipios_csv) if args.municipios_csv else None,
                hash_scope=args.hash_scope,
                quiet=args.quiet,
            )
            print(res_general.console)
            print(f"\nSaida geral gerada em: {res_general.output_dir}")
            return 0
        only = set(args.only)
        selected = set()
        for flag, phase in (
            ("hash", "hash"),
            ("timeline", "timeline"),
            ("verify", "verify"),
            ("report", "report"),
        ):
            if getattr(args, flag):
                selected.add(phase)
        if selected:
            only = selected

        table = None
        if args.municipios_csv:
            table = load_table(Path(args.municipios_csv))
        resolved = None
        if table and (municipio is not None or args.municipio):
            resolved = resolve(table, uf=args.uf, municipio=municipio or args.municipio)
        if municipio_nome is None and resolved is not None:
            municipio_nome = resolved.nome

        config = Config(
            input_dir=input_dir,
            output_dir=output_dir,
            uf=args.uf,
            municipio=municipio,
            municipio_nome=municipio_nome,
            zona=args.zona,
            secao=args.secao,
            turno=args.turno,
            data_eleicao=data_eleicao,
            ca_paths=[Path(item) for item in args.ca],
            municipios_table=table,
            hash_scope=args.hash_scope,
            only=only,
            quiet=args.quiet,
            write_html=not args.no_html,
            fast=args.fast,
        )
        result = run(config, municipio=resolved)
        print(result.console)
        print(f"\nSaida: {result.output_dir}")
        return 0
    except AnalysisError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:  # pragma: no cover
        print("interrompido", file=sys.stderr)
        return 130
