"""Testes unitários e de integração do motor de comparação 1T vs 2T."""

from __future__ import annotations

from pathlib import Path

from urna_forense.cli import main
from urna_forense.comparison import (
    ComparisonConfig,
    SectionExtraction,
    compute_worst_severity,
    evaluate_section_anomalies,
    run_comparison,
)


def _make_sample(
    *,
    comparecimento: int = 200,
    aptos: int = 250,
    aptos_secao: int = 250,
    aptos_tte: int = 0,
    votos_22: int = 110,
    votos_13: int = 80,
    brancos: int = 6,
    nulos: int = 4,
    num_urna: int = 2000000,
    num_fv: str = "AABBCCDD",
    versao: str = "10.23.0.0",
    local: int = 1010,
    abertura: str = "2026-10-04T08:00:00",
    encerramento: str = "2026-10-04T17:01:00",
    duracao_minutos: float = 541.0,
    pct_bio: float = 85.0,
    pct_bio_ano: float = 10.0,
) -> SectionExtraction:
    votos_pres = {22: votos_22, 13: votos_13}
    validos = sum(votos_pres.values())
    abstencao = max(0, aptos - comparecimento)
    return SectionExtraction(
        path="test.bu.dat",
        uf="sc",
        municipio=80535,
        zona=44,
        secao=144,
        local=local,
        numero_interno_urna=num_urna,
        numero_serie_fv=num_fv,
        numero_serie_fc="11223344",
        versao_votacao=versao,
        codigo_carga="123456789012345678901234",
        data_carga="2026-09-20T10:00:00",
        abertura=abertura,
        encerramento=encerramento,
        duracao_minutos=duracao_minutos,
        aptos=aptos,
        aptos_secao=aptos_secao,
        aptos_tte=aptos_tte,
        comparecimento=comparecimento,
        abstencao=abstencao,
        pct_comparecimento=round(comparecimento / aptos * 100, 2),
        pct_abstencao=round(abstencao / aptos * 100, 2),
        biometria_sim=int(comparecimento * (pct_bio / 100.0)),
        biometria_bio=int(comparecimento * (pct_bio_ano / 100.0)),
        biometria_nao=comparecimento - int(comparecimento * (pct_bio / 100.0)) - int(comparecimento * (pct_bio_ano / 100.0)),
        pct_biometria=pct_bio,
        pct_biografia=pct_bio_ano,
        votos_presidenciais=votos_pres,
        votos_brancos=brancos,
        votos_nulos=nulos,
        votos_validos=validos,
        total_apurado_pres=comparecimento,
    )


def test_evaluate_unpaired():
    s = _make_sample()
    anoms_1t_only = evaluate_section_anomalies(s, None)
    assert len(anoms_1t_only) == 1
    assert anoms_1t_only[0].code == "SECAO_DESEMPARELHADA_SEM_2T"

    anoms_2t_only = evaluate_section_anomalies(None, s)
    assert len(anoms_2t_only) == 1
    assert anoms_2t_only[0].code == "SECAO_DESEMPARELHADA_SEM_1T"


def test_normal_section_no_anomalies():
    s1 = _make_sample(comparecimento=200, votos_22=110, votos_13=80)
    # 2T com pequeno aumento coerente de votos e comparecimento estável
    s2 = _make_sample(
        comparecimento=205,
        votos_22=115,
        votos_13=84,
        brancos=4,
        nulos=2,
        abertura="2026-10-25T08:00:00",
        encerramento="2026-10-25T17:02:00",
        duracao_minutos=542.0,
    )
    anoms = evaluate_section_anomalies(s1, s2)
    assert len(anoms) == 0
    assert compute_worst_severity(anoms) == "NORMAL"


def test_hardware_anomalies():
    s1 = _make_sample(num_urna=1000, num_fv="AAAA", versao="10.23.0.0", local=10)
    s2 = _make_sample(num_urna=2000, num_fv="BBBB", versao="10.24.0.0", local=20)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "TROCA_URNA_FISICA" in codes
    assert "VERSAO_SOFTWARE_ALTERADA" in codes
    assert "MUDANCA_LOCAL_VOTACAO" in codes


def test_electorate_anomalies():
    # Variação de eleitores originais e TTE
    s1 = _make_sample(aptos_secao=300, aptos_tte=5, comparecimento=250, aptos=305)
    s2 = _make_sample(aptos_secao=320, aptos_tte=35, comparecimento=310, aptos=355)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "VARIACAO_APTOS_SECAO" in codes
    assert "PICO_TRANSFERENCIA_TEMPORARIA" in codes


def test_turnout_extreme_and_exceeding():
    # Comparecimento excede aptos
    s1 = _make_sample(aptos=100, comparecimento=110)
    s2 = _make_sample(aptos=100, comparecimento=100)  # 100% dos aptos
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "COMPARECIMENTO_EXCEDE_APTOS" in codes
    assert "COMPARECIMENTO_100_PCT" in codes


def test_flavio_vote_drop_with_higher_turnout():
    # Caso citado pelo usuário: Flavio teve votos no 1T mas caiu no 2T mesmo com comparecimento maior
    s1 = _make_sample(comparecimento=200, votos_22=130, votos_13=60)
    s2 = _make_sample(comparecimento=205, votos_22=115, votos_13=84)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "QUEDA_VOTOS_CANDIDATO_COM_MAIOR_COMPARECIMENTO" in codes


def test_disappearance_and_zero_votes():
    s1 = _make_sample(comparecimento=200, votos_22=100, votos_13=30)
    s2 = _make_sample(comparecimento=190, votos_22=180, votos_13=0)  # Lula zerou
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "DESAPARECIMENTO_TOTAL_VOTOS" in codes
    assert "ZERO_VOTOS_CANDIDATO_FINALISTA" in codes


def test_unanimity_and_mathematical_excess():
    s1 = _make_sample(comparecimento=200, votos_22=100, votos_13=90, brancos=5, nulos=5)
    # Candidato 22 ganha 95 votos, mas só havia 90 (Lula) + 10 (BN) disponíveis
    s2 = _make_sample(comparecimento=200, votos_22=200, votos_13=0, brancos=0, nulos=0)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "UNANIMIDADE_CANDIDATO" in codes
    assert "EXTINCAO_BRANCOS_NULOS" in codes


def test_extreme_blank_and_null_spike():
    s1 = _make_sample(comparecimento=200, brancos=2, nulos=2)
    s2 = _make_sample(comparecimento=200, brancos=35, nulos=35)  # 70/200 = 35% BN
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "EXPLOSAO_BRANCOS_NULOS" in codes


def test_abnormal_hours_and_biometrics():
    s1 = _make_sample(pct_bio=90.0, pct_bio_ano=5.0)
    s2 = _make_sample(
        abertura="2026-10-25T06:30:00",  # antes das 7h
        encerramento="2026-10-25T20:15:00",  # depois das 20h
        pct_bio=50.0,  # queda de 40 pp
        pct_bio_ano=35.0,  # salto de 30 pp
    )
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "HORARIO_ABERTURA_ANOMALO" in codes
    assert "HORARIO_ENCERRAMENTO_ANOMALO" in codes
    assert "QUEDA_ABRUPTA_BIOMETRIA" in codes
    assert "SURTO_HABILITACAO_BIOGRAFICA" in codes


def test_arithmetic_integrity_divergence():
    s1 = _make_sample()
    s2 = _make_sample()
    # Adulterar soma de votos
    s2.votos_validos = 150
    s2.votos_brancos = 5
    s2.votos_nulos = 5
    s2.total_apurado_pres = 200
    s2.comparecimento = 200  # 150 + 5 + 5 = 160 != 200
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "DIVERGENCIA_SOMA_VOTOS_COMPARECIMENTO" in codes


def test_run_comparison_e2e(tmp_path):
    # Cria estrutura de teste com 1 arquivo em 1T e 1 em 2T
    dir_1t = tmp_path / "1t"
    dir_2t = tmp_path / "2t"
    out_dir = tmp_path / "comp_out"
    dir_1t.mkdir()
    dir_2t.mkdir()

    # Copia uma fixture válida existente
    fixtures_dir = Path("tests/fixtures")
    real_bu = list(fixtures_dir.glob("*-bu.dat"))
    if real_bu:
        bu_data = real_bu[0].read_bytes()
        # Salva em 1T e 2T com nomes correspondentes
        (dir_1t / "o03220sc8053500440144-bu.dat").write_bytes(bu_data)
        (dir_2t / "o03221sc8053500440144-bu.dat").write_bytes(bu_data)

        cfg = ComparisonConfig(
            input_dir_1t=dir_1t,
            input_dir_2t=dir_2t,
            output_dir=out_dir,
            quiet=True,
            write_html=True,
        )
        res = run_comparison(cfg)
        assert res.report["resumo_auditoria"]["total_secoes_analisadas"] == 1
        assert (out_dir / "comparison_report.json").is_file()
        assert (out_dir / "comparison_report.html").is_file()


def test_cli_comparison_options(tmp_path, capsys):
    dir_1t = tmp_path / "1t"
    dir_2t = tmp_path / "2t"
    out_dir = tmp_path / "cli_comp_out"
    dir_1t.mkdir()
    dir_2t.mkdir()

    fixtures_dir = Path("tests/fixtures")
    real_bu = list(fixtures_dir.glob("*-bu.dat"))
    if real_bu:
        bu_data = real_bu[0].read_bytes()
        (dir_1t / "o03220sc8053500440144-bu.dat").write_bytes(bu_data)
        (dir_2t / "o03221sc8053500440144-bu.dat").write_bytes(bu_data)

        code = main([
            "--compare-1t", str(dir_1t),
            "--compare-2t", str(dir_2t),
            "--output", str(out_dir),
            "--quiet",
        ])
        assert code == 0
        out = capsys.readouterr().out
        assert "AUDITORIA FORENSE COMPARATIVA" in out
        assert (out_dir / "comparison_report.json").is_file()
        assert (out_dir / "comparison_report.html").is_file()
