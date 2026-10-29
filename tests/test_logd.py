from __future__ import annotations

from datetime import datetime

from helpers import load
from urna_forense.parsers.logd import detect_turn, extract_cabin_telemetry, merge_results, parse_text


def test_parse_fixture_events(urna):
    _, files = urna
    bundle = load(files)
    log = bundle["log"]
    assert len(log.events) == 33
    assert len(log.unparsed) == 0
    assert len(log.sessions) == 2
    # offsets estritamente crescentes
    offsets = [event.offset for event in log.events]
    assert offsets == sorted(offsets)
    assert len(set(offsets)) == len(offsets)


def test_event_classification(urna):
    _, files = urna
    bundle = load(files)
    log = bundle["log"]
    categories = {event.category for event in log.events}
    assert "LOG.START" in categories
    assert "SYS.POWER_ON" in categories
    assert "VOTE.READY" in categories
    assert "VOTE.COMPUTED" in categories
    assert "CLOSE.CONFIRM" in categories
    assert "BU.REPORT_START" in categories
    assert "FILE.GEN_START" in categories


def test_params_extraction():
    line = "04/10/2026 07:20:02\tINFO\t02191040\tLOGD\tUrna ligada em 04/10/2026 às 07:19:00\t0000000000000001"
    parsed = parse_text(line)
    event = parsed.events[0]
    assert event.params.get("momento_relatado") == "04/10/2026 07:19:00"


def test_unparsed_lines_preserved():
    text = "linha fora do formato\n04/10/2026 08:00:01\tINFO\t02191040\tVOTA\tmsg\t0000000000000001\n"
    parsed = parse_text(text)
    assert len(parsed.unparsed) == 1
    assert parsed.unparsed[0]["raw"] == "linha fora do formato"
    assert len(parsed.events) == 1


def test_detect_turn():
    line1 = "04/10/2026 07:20:00\tINFO\t02191040\tVOTA\tIniciando aplicação - 1º turno\t0000000000000001"
    parsed = parse_text(line1)
    turn, evidence = detect_turn(parsed.events)
    assert turn == 1
    assert len(evidence) == 1


def test_merge_results_renumbers_sessions():
    p1 = parse_text(
        "22/09/2026 10:00:00\tINFO\t02191040\tLOGD\tInício das operações do logd\t1111111111111111\n"
    )
    p2 = parse_text(
        "04/10/2026 07:00:00\tINFO\t02191040\tLOGD\tInício das operações do logd\t2222222222222222\n"
    )
    merged = merge_results([p1, p2])
    assert len(merged.sessions) == 2
    assert [e.session for e in merged.events] == [1, 2]


def test_extract_cabin_telemetry():
    log_text = (
        "25/10/2026 08:00:00\tINFO\t02191040\tVOTA\tUrna pronta para receber votos\t0000000000000001\n"
        "25/10/2026 08:00:15\tINFO\t02191040\tVOTA\tTipo de habilitação do eleitor [biométrica]\t0000000000000002\n"
        "25/10/2026 08:00:20\tINFO\t02191040\tVOTA\tO voto do eleitor foi computado\t0000000000000003\n"
        "25/10/2026 08:00:25\tINFO\t02191040\tVOTA\tUrna pronta para receber votos\t0000000000000004\n"
        "25/10/2026 08:00:28\tINFO\t02191040\tVOTA\tMesário 123456789012 habilitou o eleitor\t0000000000000005\n"
        "25/10/2026 08:00:30\tINFO\t02191040\tVOTA\tO voto do eleitor foi computado\t0000000000000006\n"
        "25/10/2026 08:00:35\tINFO\t02191040\tVOTA\tBiometria do mesário 123456789012 encontrada em eleitores\t0000000000000007\n"
    )
    parsed = parse_text(log_text)
    telem = extract_cabin_telemetry(parsed.events)
    assert telem["log_disponivel"] is True
    assert telem["total_votos_log"] == 2
    assert telem["votos_sub10s_contagem"] == 1
    assert len(telem["flagrantes_biometria_mesario"]) == 1
    assert telem["flagrantes_biometria_mesario"][0]["mesario_id"] == "123456789012"
    assert len(telem["mesarios_habilitacao_manual"]) == 1
    assert telem["mesarios_habilitacao_manual"][0]["mesario_id"] == "123456789012"
    assert telem["votos_por_faixa_horaria"]["manha_08_12"]["total"] == 2
