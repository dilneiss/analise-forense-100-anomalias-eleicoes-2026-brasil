"""Testes unitários e de integração do motor de comparação 1T vs 2T com 100 regras."""

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
    total_terceira_via: int = 0,
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
        municipio_correspondencia=80535,
        zona_correspondencia=44,
        secao_correspondencia=144,
        numero_interno_urna=num_urna,
        numero_serie_fv=num_fv,
        numero_serie_fc="11223344",
        versao_votacao=versao,
        codigo_carga="123456789012345678901234",
        data_carga="2026-10-18T10:00:00" if "2026-10-25" in encerramento else "2026-09-20T10:00:00",
        nome_gerador_midia="CSC077W058300",
        serial_tpm="367A7A6587EFF2070249",
        serial_instalacao="B8B53007",
        tipo_arquivo=1,
        data_hora_emissao="2026-10-25T17:03:00" if "2026-10-25" in encerramento else "2026-10-04T17:03:00",
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
        total_terceira_via=total_terceira_via,
        votos_terceira_via={},
        cadeia_hash_valida=True,
    )


def test_evaluate_unpaired():
    s = _make_sample()
    anoms_1t_only = evaluate_section_anomalies(s, None)
    assert len(anoms_1t_only) == 1
    assert anoms_1t_only[0].code == "CHK095_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_1T"

    anoms_2t_only = evaluate_section_anomalies(None, s)
    assert len(anoms_2t_only) == 1
    assert anoms_2t_only[0].code == "CHK096_SECAO_DESEMPARELHADA_PRESENTE_APENAS_NO_2T"


def test_normal_section_no_anomalies():
    s1 = _make_sample(comparecimento=200, votos_22=110, votos_13=80)
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
    assert "CHK001_TROCA_URNA_FISICA" in codes
    assert "CHK005_VERSAO_SOFTWARE_ALTERADA" in codes
    assert "CHK006_MUDANCA_LOCAL_VOTACAO" in codes


def test_electorate_anomalies():
    s1 = _make_sample(aptos_secao=300, aptos_tte=5, comparecimento=250, aptos=305)
    s2 = _make_sample(aptos_secao=320, aptos_tte=35, comparecimento=310, aptos=355)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK016_VARIACAO_APTOS_SECAO" in codes
    assert "CHK019_PICO_TTE_ABSOLUTO" in codes

def test_aptos_secao_threshold_half_percent():
    # +1 eleitor em 361 (= 0.27% <= 0.5%): severidade INFO (não relevante)
    s1 = _make_sample(aptos_secao=361, comparecimento=250, aptos=361)
    s2 = _make_sample(aptos_secao=362, comparecimento=250, aptos=362)
    anoms = evaluate_section_anomalies(s1, s2)
    chk16 = next((a for a in anoms if a.code == "CHK016_VARIACAO_APTOS_SECAO"), None)
    assert chk16 is not None
    assert chk16.severity == "INFO"
    assert chk16.details["relevante"] is False

    # +3 eleitores em 300 (= 1.0% > 0.5%): severidade ALTA (relevante)
    s3 = _make_sample(aptos_secao=300, comparecimento=250, aptos=300)
    s4 = _make_sample(aptos_secao=303, comparecimento=250, aptos=303)
    anoms_rel = evaluate_section_anomalies(s3, s4)
    chk16_rel = next((a for a in anoms_rel if a.code == "CHK016_VARIACAO_APTOS_SECAO"), None)
    assert chk16_rel is not None
    assert chk16_rel.severity == "ALTA"
    assert chk16_rel.details["relevante"] is True

def test_turnout_extreme_and_exceeding():
    s1 = _make_sample(aptos=100, comparecimento=110)
    s2 = _make_sample(aptos=100, comparecimento=100)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK032_COMPARECIMENTO_EXCEDE_APTOS_1T" in codes
    assert "CHK033_COMPARECIMENTO_100_PCT_2T" in codes


def test_flavio_vote_drop_with_higher_turnout():
    s1 = _make_sample(comparecimento=200, votos_22=130, votos_13=60)
    s2 = _make_sample(comparecimento=205, votos_22=115, votos_13=84)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK046_QUEDA_FINALISTA_COM_COMPARECIMENTO_MAIOR" in codes


def test_disappearance_and_zero_votes():
    s1 = _make_sample(comparecimento=200, votos_22=100, votos_13=30)
    s2 = _make_sample(comparecimento=190, votos_22=180, votos_13=0)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK050_DESAPARECIMENTO_FINALISTA_NO_2T" in codes
    assert "CHK051_ZERO_VOTOS_FINALISTA_SECAO_GRANDE" in codes


def test_unanimity_and_mathematical_excess():
    s1 = _make_sample(comparecimento=200, votos_22=100, votos_13=90, brancos=5, nulos=5)
    s2 = _make_sample(comparecimento=200, votos_22=200, votos_13=0, brancos=0, nulos=0)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK052_UNANIMIDADE_100PCT_FINALISTA_2T" in codes
    assert "CHK088_EXTINCAO_BRANCOS_NULOS_SECAO_GRANDE" in codes


def test_extreme_blank_and_null_spike():
    s1 = _make_sample(comparecimento=200, brancos=2, nulos=2)
    s2 = _make_sample(comparecimento=200, brancos=35, nulos=35)
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK086_EXPLOSAO_BRANCOS_NULOS_MAIOR_15PP" in codes


def test_abnormal_hours_and_biometrics():
    s1 = _make_sample(pct_bio=90.0, pct_bio_ano=5.0)
    s2 = _make_sample(
        abertura="2026-10-25T06:30:00",
        encerramento="2026-10-25T20:15:00",
        pct_bio=50.0,
        pct_bio_ano=35.0,
    )
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK076_ABERTURA_PRECOCE_2T" in codes
    assert "CHK079_ENCERRAMENTO_MUITO_TARDIO_2T" in codes
    assert "CHK066_QUEDA_ABRUPTA_BIOMETRIA_MAIOR_30PP" in codes
    assert "CHK068_SURTO_HABILITACAO_BIOGRAFICA_MAIOR_25PP" in codes


def test_arithmetic_integrity_divergence():
    s1 = _make_sample()
    s2 = _make_sample()
    s2.votos_validos = 150
    s2.votos_brancos = 5
    s2.votos_nulos = 5
    s2.total_apurado_pres = 200
    s2.comparecimento = 200
    anoms = evaluate_section_anomalies(s1, s2)
    codes = {a.code for a in anoms}
    assert "CHK093_DIVERGENCIA_SOMA_VOTOS_E_COMPARECIMENTO_2T" in codes


def test_run_comparison_e2e(tmp_path):
    dir_1t = tmp_path / "1t"
    dir_2t = tmp_path / "2t"
    out_dir = tmp_path / "comp_out"
    dir_1t.mkdir()
    dir_2t.mkdir()

    fixtures_dir = Path("tests/fixtures")
    real_bu = list(fixtures_dir.glob("*-bu.dat"))
    if real_bu:
        bu_data = real_bu[0].read_bytes()
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
