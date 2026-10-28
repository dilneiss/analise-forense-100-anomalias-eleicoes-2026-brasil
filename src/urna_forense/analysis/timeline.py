"""Construcao da linha do tempo a partir do log, do BU e do BU impresso."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from ..models import EventRef, LogEvent, Milestone
from ..parsers.bu import BU
from ..parsers.imgbu import ImgBU
from ..parsers.logd import LogParseResult, Session, detect_turn
from ..parsers.signature import SignatureFile

SOURCE_LOG = "log.jez!logd.dat"


@dataclass
class Timeline:
    election_date: Optional[date]
    turn: Optional[int]
    turn_sources: list[str]
    sessions: list[dict[str, Any]]
    milestones: list[Milestone]
    events: list[LogEvent]
    voting: dict[str, Any]
    stats: dict[str, Any]

    def milestone(self, key: str) -> Optional[Milestone]:
        return next((item for item in self.milestones if item.key == key), None)

    def as_dict(self, *, include_events: bool = True) -> dict[str, Any]:
        data = {
            "election_date": self.election_date.isoformat() if self.election_date else None,
            "turn": self.turn,
            "turn_sources": self.turn_sources,
            "sessions": self.sessions,
            "milestones": [item.as_dict() for item in self.milestones],
            "voting": self.voting,
            "stats": self.stats,
        }
        if include_events:
            data["events"] = [event.as_dict() for event in self.events]
        return data


def _ref(event: LogEvent, note: Optional[str] = None) -> EventRef:
    return EventRef(
        timestamp=event.timestamp,
        source=f"{SOURCE_LOG}:{event.source}" if event.source != "logd.dat" else SOURCE_LOG,
        offset=event.offset,
        line=event.line,
        raw=event.raw,
        note=note,
    )


def _bu_ref(timestamp: Optional[datetime], source: str, offset: Optional[int], note: str) -> EventRef:
    return EventRef(
        timestamp=timestamp, source=source, offset=offset, raw=None, note=note
    )


def _first(events: list[LogEvent], category: str) -> Optional[LogEvent]:
    return next((event for event in events if event.category == category), None)


def _last(events: list[LogEvent], category: str) -> Optional[LogEvent]:
    found = [event for event in events if event.category == category]
    return found[-1] if found else None


def _identified(
    key: str,
    label: str,
    timestamp: Optional[datetime],
    refs: list[EventRef],
    interpretation: str,
    alternatives: Optional[list[EventRef]] = None,
) -> Milestone:
    return Milestone(
        key=key,
        label=label,
        status="identificado" if timestamp else "nao_identificado",
        timestamp=timestamp,
        refs=refs,
        interpretation=interpretation if timestamp else "NAO IDENTIFICADO",
        alternatives=alternatives or [],
    )


def _date_from_brazilian(text: Optional[str]) -> Optional[date]:
    if not text:
        return None
    try:
        return datetime.strptime(text, "%d/%m/%Y").date()
    except ValueError:
        return None


def build_timeline(
    log: LogParseResult,
    *,
    bu: Optional[BU] = None,
    imgbu: Optional[ImgBU] = None,
    signature: Optional[SignatureFile] = None,
    log_source: str = "log.jez",
) -> Timeline:
    events = log.events
    election_date: Optional[date] = None
    if bu and bu.abertura:
        election_date = bu.abertura.date()
    elif imgbu and imgbu.summary.get("data_eleicao"):
        election_date = _date_from_brazilian(imgbu.summary["data_eleicao"])
    if election_date is None:
        ready = _first(events, "VOTE.READY")
        if ready:
            election_date = ready.timestamp.date() if ready.timestamp else None
    if election_date is None:
        dated = [event.timestamp.date() for event in events if event.timestamp]
        election_date = max(dated) if dated else None

    day_events = [
        event
        for event in events
        if event.timestamp and event.timestamp.date() == election_date
    ]
    turn, turn_evidence = detect_turn(events)
    turn_sources = [f"log: {raw}" for raw in turn_evidence]
    if imgbu and imgbu.summary.get("turno"):
        if turn is not None and imgbu.summary["turno"] != turn:
            turn_sources.append(
                f"conflito: BU impresso indica turno {imgbu.summary['turno']}"
            )
        else:
            turn = imgbu.summary["turno"]
            turn_sources.append(
                f"BU impresso: {imgbu.summary['turno']}o turno"
            )

    power_on = _first(day_events, "SYS.POWER_ON")
    log_start = _first(day_events, "LOG.START")
    app_start = _first(day_events, "SYS.APP_START")
    power_on_time = power_on.timestamp if power_on else None
    if power_on and power_on.params.get("momento_relatado"):
        try:
            power_on_time = datetime.strptime(
                str(power_on.params["momento_relatado"]), "%d/%m/%Y %H:%M:%S"
            )
        except ValueError:
            pass
    inicializacao_ts = (
        power_on_time
        if power_on_time
        else (log_start or app_start).timestamp
        if (log_start or app_start)
        else (day_events[0].timestamp if day_events else None)
    )
    inicializacao_refs = []
    if power_on is not None:
        note = None
        if power_on_time and power_on.timestamp and power_on_time != power_on.timestamp:
            note = (
                "hora de energização informada no texto; a linha do log foi "
                f"gravada {int((power_on.timestamp - power_on_time).total_seconds())}s depois"
            )
        inicializacao_refs.append(_ref(power_on, note))
    inicializacao_refs.extend(
        _ref(event) for event in (log_start, app_start) if event is not None
    )

    section_id = next(
        (
            event
            for event in day_events
            if event.category == "PREP.SECTION_ID" and event.message.startswith("Município")
        ),
        None,
    )
    load_event = _first(day_events, "PREP.LOAD")

    ready = _first(day_events, "VOTE.READY")
    votes = [event for event in day_events if event.category == "VOTE.COMPUTED"]
    first_vote = votes[0] if votes else None
    last_vote = votes[-1] if votes else None
    close_confirm = _last(day_events, "CLOSE.CONFIRM")
    close_start = _last(day_events, "CLOSE.START")
    report_start = _last(day_events, "BU.REPORT_START")
    report_end = _last(day_events, "BU.REPORT_END")
    print_start = next(
        (
            event
            for event in day_events
            if event.category == "BU.PRINT_START"
            and report_start
            and event.timestamp
            and event.timestamp >= report_start.timestamp
        ),
        None,
    )
    print_end = next(
        (
            event
            for event in day_events
            if event.category == "BU.PRINT_END"
            and print_start
            and event.timestamp
            and event.timestamp >= print_start.timestamp
        ),
        None,
    )
    bu_file_start = next(
        (event for event in day_events if event.category == "FILE.GEN_START" and "bu.dat" in event.message),
        None,
    )
    bu_file_end = next(
        (event for event in day_events if event.category == "FILE.GEN_END" and "bu.dat" in event.message),
        None,
    )
    log_pack_start = next(
        (event for event in day_events if event.category == "FILE.GEN_START" and "log.jez" in event.message),
        None,
    )
    transmission = [event for event in day_events if event.category == "NET.TRANSMISSION"]
    shutdown = _last(day_events, "SYS.SHUTDOWN") or _last(day_events, "SYS.KEY_OFF")

    milestones: list[Milestone] = [
        _identified(
            "inicializacao",
            "Inicialização da urna",
            inicializacao_ts,
            inicializacao_refs,
            (
                "Primeira evidência de energia/aplicação no dia da eleição. "
                "'Urna ligada em' é o evento de energização; 'Início das "
                "operações do logd' é o início do registro; 'Iniciando "
                "aplicação' é a carga do software."
            ),
            [],
        ),
        _identified(
            "preparacao",
            "Preparação e identificação da seção",
            section_id.timestamp if section_id else (load_event.timestamp if load_event else None),
            [ref for ref in (
                _ref(section_id) if section_id else None,
                _ref(load_event) if load_event else None,
            ) if ref],
            (
                "Identificação de município, zona, local e seção e carga da "
                "mídia de votação, antes da abertura."
            ),
            [],
        ),
        _identified(
            "abertura",
            "Abertura da votação",
            ready.timestamp if ready else None,
            [_ref(ready)] if ready else [],
            (
                "Evento 'Urna pronta para receber votos' no dia da eleição. "
                "É o início efetivo do recebimento de votos."
            ),
            [],
        ),
        _identified(
            "primeiro_voto",
            "Primeiro voto computado",
            first_vote.timestamp if first_vote else None,
            [_ref(first_vote)] if first_vote else [],
            "Primeiro evento 'O voto do eleitor foi computado' do dia.",
            [],
        ),
        _identified(
            "ultimo_voto",
            "Último voto computado",
            last_vote.timestamp if last_vote else None,
            [_ref(last_vote)] if last_vote else [],
            "Último evento 'O voto do eleitor foi computado' do dia.",
            [],
        ),
        _identified(
            "encerramento",
            "Encerramento da votação",
            (
                close_confirm.timestamp
                if close_confirm
                else (bu.encerramento if bu else None)
            ),
            [ref for ref in (
                _ref(close_confirm) if close_confirm else None,
                _bu_ref(
                    bu.encerramento,
                    "bu.dat",
                    bu.offsets.get("encerramento"),
                    "dataHoraEncerramento (fim da aquisição de votos)",
                ) if bu and bu.encerramento else None,
            ) if ref],
            (
                "Fim da aquisição de votos. No log, 'Procedimento de "
                "encerramento confirmado'; no BU, dataHoraEncerramento. Não "
                "confundir com 'Início do Encerramento' (procedimento de "
                "fechamento) nem com geração/impressão do BU."
            ),
            [
                _ref(close_start, "início do procedimento de encerramento (não é o fim da votação)")
            ] if close_start else [],
        ),
        _identified(
            "bu_relatorio",
            "Geração do relatório do BU",
            report_start.timestamp if report_start else (bu.data_hora_emissao if bu else None),
            [ref for ref in (
                _ref(report_start) if report_start else None,
                _ref(report_end) if report_end else None,
                _bu_ref(
                    bu.data_hora_emissao,
                    "bu.dat",
                    bu.offsets.get("data_hora_emissao"),
                    "dataHoraEmissao declarada dentro do BU",
                ) if bu else None,
            ) if ref],
            (
                "'Gerando relatório [BU]' e dataHoraEmissao do BU. É a "
                "emissão do boletim, anterior à impressão e à gravação do "
                "arquivo."
            ),
            [],
        ),
        _identified(
            "bu_impressao",
            "Impressão do BU",
            print_start.timestamp if print_start else None,
            [ref for ref in (
                _ref(print_start) if print_start else None,
                _ref(print_end) if print_end else None,
            ) if ref],
            "Início e fim da impressão física do BU.",
            [],
        ),
        _identified(
            "bu_arquivo",
            "Gravação do arquivo bu.dat",
            bu_file_start.timestamp if bu_file_start else None,
            [ref for ref in (
                _ref(bu_file_start) if bu_file_start else None,
                _ref(bu_file_end) if bu_file_end else None,
            ) if ref],
            (
                "'Gerando arquivo de resultado [bu.dat]'. O instante do "
                "arquivo assinado (envelope) é posterior à emissão."
            ),
            [],
        ),
        _identified(
            "bu_assinatura",
            "Assinatura do conjunto (vota.vsc)",
            signature.sw.data_hora if signature else (
                datetime.fromisoformat(bu.envelope["data_geracao"]) if bu else None
            ),
            [ref for ref in (
                _bu_ref(
                    signature.sw.data_hora if signature else None,
                    "vota.vsc",
                    None,
                    "dataHoraCriacao da assinatura de software",
                ) if signature else None,
                _bu_ref(
                    datetime.fromisoformat(bu.envelope["data_geracao"]) if bu else None,
                    "bu.dat",
                    bu.offsets.get("envelope_data_geracao") if bu else None,
                    "dataGeracao do envelope do BU",
                ) if bu else None,
            ) if ref],
            (
                "Assinatura digital dos arquivos de resultado. O envelope do "
                "bu.dat e o vota.vsc têm horários próprios."
            ),
            [],
        ),
        _identified(
            "log_empacotado",
            "Empacotamento do log.jez",
            log_pack_start.timestamp if log_pack_start else None,
            [_ref(log_pack_start)] if log_pack_start else [],
            (
                "Início da geração do log.jez. O término não aparece no "
                "próprio log (a última linha é gravada durante o empacotamento)."
            ),
            [],
        ),
        _identified(
            "transmissao_inicio",
            "Transmissão iniciada",
            transmission[0].timestamp if transmission else None,
            [_ref(event) for event in transmission[:1]],
            "Evento de transmissão no log.",
            [],
        ),
        _identified(
            "transmissao_fim",
            "Transmissão concluída",
            transmission[-1].timestamp if len(transmission) > 1 else None,
            [_ref(event) for event in transmission[-1:]],
            "Evento de transmissão no log.",
            [],
        ),
        _identified(
            "desligamento",
            "Desligamento da urna",
            shutdown.timestamp if shutdown else None,
            [_ref(shutdown)] if shutdown else [],
            "Evento de desligamento no dia da eleição.",
            [],
        ),
    ]

    if not day_events and events:
        milestones.append(
            _identified(
                "fim_do_log",
                "Último evento registrado",
                events[-1].timestamp,
                [_ref(events[-1])],
                "Não há eventos compatíveis com o dia da eleição.",
                [],
            )
        )
    elif events:
        last_event = day_events[-1] if day_events else events[-1]
        milestones.append(
            _identified(
                "fim_do_log",
                "Último evento do log no dia",
                last_event.timestamp,
                [_ref(last_event)],
                "Última linha registrada antes do empacotamento do log.",
                [],
            )
        )

    # ---- votacao: estatisticas -------------------------------------------
    voting: dict[str, Any] = {}
    if ready and close_confirm:
        voting["duracao_votacao_segundos"] = int(
            (close_confirm.timestamp - ready.timestamp).total_seconds()
        )
    if ready and first_vote:
        voting["abertura_ate_primeiro_voto_segundos"] = int(
            (first_vote.timestamp - ready.timestamp).total_seconds()
        )
    intervals = []
    for previous, current in zip(votes, votes[1:]):
        if previous.timestamp and current.timestamp:
            intervals.append((current.timestamp - previous.timestamp).total_seconds())
    voting["votos_computados"] = len(votes)
    if intervals:
        ordered = sorted(intervals)
        voting["intervalo_entre_votos_s"] = {
            "min": ordered[0],
            "mediana": ordered[len(ordered) // 2],
            "max": ordered[-1],
        }
        voting["maior_intervalo_s"] = max(intervals)
    if ready and votes:
        voting["votos_antes_da_abertura"] = sum(
            1 for event in votes if event.timestamp < ready.timestamp
        )
    if close_confirm and votes:
        voting["votos_apos_encerramento"] = sum(
            1 for event in votes if event.timestamp > close_confirm.timestamp
        )
    voting["reinicios_abertura_no_dia"] = len(
        [event for event in day_events if event.category == "VOTE.READY"]
    )
    voting["alertas_no_dia"] = len(
        [event for event in day_events if event.level.upper() == "ALERTA"]
    )
    votos_por_hora: dict[str, int] = {}
    eventos_por_hora: dict[str, int] = {}
    for event in day_events:
        if not event.timestamp:
            continue
        hour = f"{event.timestamp.hour:02d}"
        eventos_por_hora[hour] = eventos_por_hora.get(hour, 0) + 1
        if event.category == "VOTE.COMPUTED":
            votos_por_hora[hour] = votos_por_hora.get(hour, 0) + 1
    voting["votos_por_hora"] = dict(sorted(votos_por_hora.items()))
    voting["eventos_por_hora"] = dict(sorted(eventos_por_hora.items()))

    sessions = [
        {
            **session.as_dict(),
            "date": session.first.date().isoformat() if session.first else None,
            "is_election_day": bool(
                session.first and election_date and session.first.date() == election_date
            ),
        }
        for session in log.sessions
    ]

    return Timeline(
        election_date=election_date,
        turn=turn,
        turn_sources=turn_sources,
        sessions=sessions,
        milestones=milestones,
        events=events,
        voting=voting,
        stats=log.stats,
    )
