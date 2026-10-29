"""Parser do ``logd.dat``.

Formato observado (documentado como "texto simples" no LEIA-ME oficial):
seis campos separados por TAB, em uma linha por evento::

    DD/MM/AAAA HH:MM:SS <TAB> SEVERIDADE <TAB> ID_URNA <TAB> APLICATIVO <TAB> MENSAGEM <TAB> CODIGO

O sexto campo tem 16 hexadecimais (64 bits). Ele NAO e recalculado aqui:
linhas com os mesmos cinco primeiros campos aparecem com codigos diferentes,
o que mostra que nao e uma funcao apenas dos campos visiveis; a construcao
nao esta publicada. O valor e preservado e contado, nunca validado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..models import LogEvent

LINE_RE = re.compile(
    r"^(?P<date>\d{2}/\d{2}/\d{4}) (?P<time>\d{2}:\d{2}:\d{2})\t"
    r"(?P<level>[^\t]*)\t(?P<urna>[^\t]*)\t(?P<module>[^\t]*)\t"
    r"(?P<message>.*)\t(?P<mac>[0-9A-Fa-f]+)\s*$"
)

# Regras ordenadas: a primeira que casa define a categoria. Nao dependem de
# uma frase unica: cada regra cobre uma familia de eventos do mesmo tipo.
RULES: tuple[tuple[str, str], ...] = (
    ("LOG.START", r"^In[ií]cio das opera[çc][õo]es do logd$"),
    ("SYS.POWER_ON", r"^Urna ligada em .+$"),
    ("SYS.APP_START", r"^Iniciando aplica[çc][ãa]o"),
    ("SYS.APP_END", r"^Finaliza[çc][ãa]o de aplicativo$"),
    ("SYS.SHUTDOWN", r"^Desligando a urna$"),
    ("SYS.KEY_OFF", r"^Urna desligada pela chave$"),
    ("SYS.TIME_ADJUST", r"(?i)(ajust|acert)\w*\s+.*(hora|rel[oó]gio)"),
    ("SYS.SUBSTITUTION", r"(?i)(substitui|conting[eê]ncia)"),
    ("PREP.INSPECTION", r"^Inspe[çc][ãa]o da urna"),
    ("PREP.MEDIA_TEST", r"teste (M[ií]dia de Resultado|Comunica[çc][ãa]o TE)"),
    (
        "PREP.SECTION_ID",
        r"^(Munic[ií]pio|Zona Eleitoral|Local de Vota[çc][ãa]o|"
        r"Se[çc][ãa]o Eleitoral|Se[çc][ãa]o informada pelo operador)\s*:",
    ),
    (
        "PREP.LOAD",
        r"^(Modo de carga da UE|M[ií]dia de vota[çc][ãa]o|"
        r"Data e hora da gera[çc][ãa]o da m[ií]dia|Iniciando registro do log)",
    ),
    ("PREP.LOG_COPY", r"^Iniciando c[oó]pia de Log"),
    ("PREP.MEDIA", r"^(Tamanho da m[ií]dia|Tamanho da mem[oó]ria|Espa[çc]o |"
                   r"Quantidade de mem[oó]ria|Urna ligada conectada)"),
    ("SEC.SIGNATURE_APP", r"Verifica[çc][ãa]o de assinatura de aplica[çc][ãa]o"),
    ("SEC.SIGNATURE_DATA", r"Verifica[çc][ãa]o de assinatura de dado"),
    ("SEC.SIGNATURE_FILE", r"^Identifica[çc][ãa]o de assinatura"),
    ("SEC.SIGNATURE_MODEL", r"^Identifica[çc][ãa]o do Modelo de Urna"),
    ("MAINT.TEST_FAIL", r"^Falha do teste"),
    ("VOTE.READY", r"^Urna pronta para receber votos$"),
    ("VOTE.WAIT_ID", r"^Aguardando digita[çc][ãa]o do identificador"),
    ("VOTE.ALERT_MESARIO", r"^Mes[áa]rio indagado"),
    (
        "VOTE.HABILITATION",
        r"^(Eleitor foi habilitado|Identificador do eleitor digitado|"
        r"Identificador digitado pelo mes[áa]rio|Tipo de habilita[çc][ãa]o|"
        r"Foto do eleitor apresentada|Solicita digital|Capturada a digital|"
        r"N[uú]mero de tentativas de reconhecimento|Timeout de reconhecimento|"
        r"Batimento de digitais|Biometria|Mes[áa]rio .* (registrado|habilitou)|"
        r"Pedido de leitura da biometria|Realizada a confer[êe]ncia|"
        r"Digital capturada|Eleitor n[ãa]o encontrado|"
        r"Ano de nascimento|Dado digitado|Dado digitado confere|"
        r"Solicita[çc][ãa]o de dado pessoal|Operador confirmou o registro de mes[áa]rios|"
        r"Operador encerrou ciclo de registro|Registrando mes[áa]rios|"
        r"Operador indagado se continua registrando|"
        r"Operador indagado se finaliza registro|"
        r"Operador indagado se ocorrer[áa] registro|"
        r"Mes[áa]rio indagado sobre qualidade)",
    ),
    ("VOTE.BALLOT", r"^Voto confirmado para"),
    ("VOTE.COMPUTED", r"^O voto do eleitor foi computado$"),
    ("VOTE.IDLE", r"^Eleitor sem atividade"),
    ("VOTE.ERROR", r"^Eleitor corrigiu|^Tecla indevida"),
    ("CLOSE.REQUEST", r"^Operador selecionou: Encerrar vota[çc][ãa]o$"),
    ("CLOSE.QUESTION", r"^Operador indagado se todas as pessoas"),
    ("CLOSE.CONFIRM", r"^Procedimento de encerramento confirmado$"),
    ("CLOSE.START", r"^In[ií]cio do Encerramento$"),
    ("BU.REPORT_START", r"^Gerando relat[oó]rio \[BU\] \[IN[IÍ]CIO\]$"),
    ("BU.REPORT_END", r"^Gerando relat[oó]rio \[BU\] \[T[EÉ]RMINO\]$"),
    ("BU.PRINT_START", r"^In[ií]cio de impress[aã]o$"),
    ("BU.PRINT_END", r"^Fim de impress[aã]o$"),
    ("BU.QUALITY", r"^Mes[áa]rio indicou qualidade OK"),
    ("FILE.GEN_START", r"^Gerando arquivo de resultado \[(.+?)\] \+ \[In[ií]cio\]$"),
    ("FILE.GEN_END", r"^Gerando arquivo de resultado \[(.+?)\] \+ \[T[eé]rmino\]$"),
    ("NET.TRANSMISSION", r"(?i)transmiss"),
    ("MAINT.CYCLE", r"(?i)(ciclo de teste|chave desligada)"),
)

_COMPILED = tuple((name, re.compile(pattern)) for name, pattern in RULES)
_FILENAME_RE = re.compile(r"[\w.-]+\.(?:dat|jez|vsc|ver|vst|vsu)\b", re.IGNORECASE)
_BRACKET_RE = re.compile(r"\[([^\]]+)\]")
_TURN_RE = re.compile(r"(?i)(\d)\s*[ºo°]?\s*turno")
_TURN_WORD_RE = re.compile(r"(?i)(primeiro|segundo)\s+turno")


@dataclass
class Session:
    index: int
    first: Optional[datetime] = None
    last: Optional[datetime] = None
    start_event: Optional[LogEvent] = None
    power_on: Optional[LogEvent] = None
    app_start: Optional[LogEvent] = None
    shutdown: Optional[LogEvent] = None

    def as_dict(self) -> dict[str, object]:
        def ref(event: Optional[LogEvent]):
            return event.as_dict() if event else None

        return {
            "index": self.index,
            "first": self.first.isoformat() if self.first else None,
            "last": self.last.isoformat() if self.last else None,
            "start_event": ref(self.start_event),
            "power_on": ref(self.power_on),
            "app_start": ref(self.app_start),
            "shutdown": ref(self.shutdown),
        }


@dataclass
class LogParseResult:
    events: list[LogEvent] = field(default_factory=list)
    unparsed: list[dict[str, object]] = field(default_factory=list)
    sessions: list[Session] = field(default_factory=list)
    entries: list[str] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)

    def by_category(self, *categories: str) -> list[LogEvent]:
        wanted = set(categories)
        return [event for event in self.events if event.category in wanted]


_RELATED_TIME_RE = re.compile(
    r"(?:Urna ligada em|Data e hora da gera[çc][ãa]o da m[ií]dia de vota[çc][ãa]o:?)\s*"
    r"(?P<date>\d{2}/\d{2}/\d{4})(?:\s*(?:[àa]s)?\s*)"
    r"(?P<time>\d{2}:\d{2}:\d{2})"
)


def _params(message: str) -> dict[str, object]:
    params: dict[str, object] = {}
    bracket = _BRACKET_RE.findall(message)
    if bracket:
        params["campos"] = bracket
    files = _FILENAME_RE.findall(message)
    if files:
        params["arquivos"] = files
    related = _RELATED_TIME_RE.search(message)
    if related:
        params["momento_relatado"] = (
            f"{related.group('date')} {related.group('time')}"
        )
    return params


def _classify(level: str, module: str, message: str) -> str:
    for category, pattern in _COMPILED:
        if pattern.search(message):
            return category
    upper = level.upper()
    if upper in ("ALERTA", "AVISO", "WARN", "WARNING"):
        return "ALERT"
    if upper in ("ERRO", "ERROR", "FALHA", "FATAL"):
        return "ERROR"
    if re.search(r"(?i)\b(erro|falha|falhou)\b", message):
        return "ERROR"
    return f"{module or 'GEN'}.INFO"


def parse_text(text: str, *, source: str = "logd.dat") -> LogParseResult:
    """Converte o texto do log em eventos com offset e linha de origem."""
    result = LogParseResult(entries=[source])
    session_index = 0
    current: Optional[Session] = None
    raw_offset = 0
    for line_number, raw_line in enumerate(text.splitlines(keepends=True), start=1):
        line = raw_line.rstrip("\r\n")
        line_offset = raw_offset
        raw_offset += len(raw_line.encode("latin-1", errors="replace"))
        if not line.strip():
            continue
        match = LINE_RE.match(line)
        if not match:
            result.unparsed.append(
                {
                    "line": line_number,
                    "offset": line_offset,
                    "raw": line,
                    "reason": "linha fora do formato de 6 campos",
                }
            )
            continue
        try:
            timestamp = datetime.strptime(
                f"{match.group('date')} {match.group('time')}", "%d/%m/%Y %H:%M:%S"
            )
        except ValueError:
            result.unparsed.append(
                {
                    "line": line_number,
                    "offset": line_offset,
                    "raw": line,
                    "reason": "data/hora invalida",
                }
            )
            continue
        level = match.group("level")
        module = match.group("module")
        message = match.group("message")
        category = _classify(level, module, message)
        if category == "LOG.START":
            session_index += 1
            current = Session(index=session_index)
            result.sessions.append(current)
        if current is None:
            current = Session(index=session_index)
            result.sessions.append(current)
        event = LogEvent(
            offset=line_offset,
            line=line_number,
            timestamp=timestamp,
            date=match.group("date"),
            time=match.group("time"),
            level=level,
            urna_id=match.group("urna"),
            module=module,
            message=message,
            mac=match.group("mac").upper(),
            raw=line,
            category=category,
            event_id=category,
            session=current.index,
            params=_params(message),
        )
        result.events.append(event)
        current.last = timestamp
        if current.first is None:
            current.first = timestamp
        if category == "LOG.START":
            current.start_event = event
        elif category == "SYS.POWER_ON" and current.power_on is None:
            current.power_on = event
        elif category == "SYS.APP_START" and current.app_start is None:
            current.app_start = event
        elif category in ("SYS.SHUTDOWN", "SYS.KEY_OFF"):
            current.shutdown = event
    _fill_stats(result)
    return result


def _fill_stats(result: LogParseResult) -> None:
    levels: dict[str, int] = {}
    modules: dict[str, int] = {}
    categories: dict[str, int] = {}
    macs: set[str] = set()
    inversions = 0
    previous: Optional[datetime] = None
    identical_lines: dict[str, int] = {}
    for event in result.events:
        levels[event.level] = levels.get(event.level, 0) + 1
        modules[event.module] = modules.get(event.module, 0) + 1
        categories[event.category] = categories.get(event.category, 0) + 1
        macs.add(event.mac)
        if previous and event.timestamp and event.timestamp < previous:
            inversions += 1
        previous = event.timestamp
        identical_lines[event.raw] = identical_lines.get(event.raw, 0) + 1
    duplicated = sum(count - 1 for count in identical_lines.values() if count > 1)
    result.stats = {
        "lines_total": len(result.events) + len(result.unparsed),
        "events": len(result.events),
        "unparsed": len(result.unparsed),
        "levels": levels,
        "modules": modules,
        "categories": categories,
        "unique_macs": len(macs),
        "clock_inversions": inversions,
        "duplicated_line_occurrences": duplicated,
        "sessions": len(result.sessions),
        "mac_verification": (
            "NAO FOI POSSIVEL VERIFICAR: o codigo de 64 bits de cada linha "
            "nao tem construcao publicada e nao e funcao apenas dos campos "
            "visiveis (linhas identicas aparecem com codigos diferentes)."
        ),
    }


def merge_results(results: list[LogParseResult]) -> LogParseResult:
    """Une varios textos de log, preservando a ordem e renumerando sessoes."""
    merged = LogParseResult()
    session_offset = 0
    for parsed in results:
        for event in parsed.events:
            event.session += session_offset
            merged.events.append(event)
        for session in parsed.sessions:
            session.index += session_offset
            merged.sessions.append(session)
        merged.unparsed.extend(parsed.unparsed)
        merged.entries.extend(parsed.entries)
        session_offset += len(parsed.sessions)
    _fill_stats(merged)
    return merged


def detect_turn(events: list[LogEvent]) -> tuple[Optional[int], list[str]]:
    """Turno a partir do texto do log (nao ha campo 'turno' no BU)."""
    votes: dict[int, int] = {}
    evidence: list[str] = []
    for event in events:
        match = _TURN_RE.search(event.message)
        if match:
            value = int(match.group(1))
            votes[value] = votes.get(value, 0) + 1
            if len(evidence) < 5:
                evidence.append(event.raw)
            continue
        word = _TURN_WORD_RE.search(event.message)
        if word:
            value = 1 if word.group(1).lower() == "primeiro" else 2
            votes[value] = votes.get(value, 0) + 1
            if len(evidence) < 5:
                evidence.append(event.raw)
    if not votes:
        return None, []
    return max(votes, key=lambda key: votes[key]), evidence


def extract_cabin_telemetry(events: list[LogEvent]) -> dict[str, Any]:
    """Extrai telemetria de votacao: tempos de cabine, flagrantes de mesarios e distribuicao horaria."""
    MESARIO_HABILITOU_RE = re.compile(r"Mes[áa]rio\s+([0-9A-Za-z]+)\s+habilitou", re.IGNORECASE)
    MESARIO_BIOMETRIA_ALERTA_RE = re.compile(
        r"(?:Biometria do mes[áa]rio\s+([0-9A-Za-z]+)\s+encontrada em eleitores|Digital coletada bate com uma digital gravada ap[oó]s o registro inicial de mes[áa]rio)",
        re.IGNORECASE
    )

    ready_time: Optional[datetime] = None
    prev_vote_time: Optional[datetime] = None
    current_hab_type = "DESCONHECIDO"
    current_mesario_id = None

    duracoes: list[float] = []
    intervalos_troca: list[float] = []

    consecutive_sub10s = 0
    max_consecutive_sub10s = 0
    sub10s_count = 0

    flagrantes_mesario: list[dict[str, Any]] = []
    mesarios_contagem: dict[str, int] = {}

    faixas = {
        "manha_08_12": {"total": 0, "bio": 0, "manual": 0},
        "almoco_12_14": {"total": 0, "bio": 0, "manual": 0},
        "tarde_14_17": {"total": 0, "bio": 0, "manual": 0},
        "noite_apos_17": {"total": 0, "bio": 0, "manual": 0},
    }

    votos_totais = 0

    for e in events:
        msg = e.message
        # 1. Flagrante de mesario tentando biometria em eleitores
        alerta_match = MESARIO_BIOMETRIA_ALERTA_RE.search(msg)
        if alerta_match:
            mid = alerta_match.group(1) or "DESCONHECIDO"
            flagrantes_mesario.append({
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                "mesario_id": mid,
                "mensagem": msg
            })

        # 2. Habilitacao
        if "Tipo de habilitação do eleitor [biométrica]" in msg:
            current_hab_type = "BIOMETRICA"
        elif "Solicitação de dado pessoal do eleitor para habilitação manual" in msg or "Dado digitado confere" in msg:
            current_hab_type = "MANUAL"

        m_hab = MESARIO_HABILITOU_RE.search(msg)
        if m_hab:
            current_mesario_id = m_hab.group(1)
            current_hab_type = "MANUAL"

        # 3. Urna liberada para o eleitor votar na cabine
        if (msg == "Eleitor foi habilitado" or e.category == "VOTE.READY") and e.timestamp:
            ready_time = e.timestamp
            if prev_vote_time:
                diff_troca = (ready_time - prev_vote_time).total_seconds()
                if 0 <= diff_troca <= 600:
                    intervalos_troca.append(diff_troca)

        # 4. Voto computado
        elif e.category == "VOTE.COMPUTED" and e.timestamp:
            votos_totais += 1
            vote_time = e.timestamp
            prev_vote_time = vote_time

            dur = (vote_time - ready_time).total_seconds() if ready_time else 0.0
            ready_time = None

            if dur > 0:
                duracoes.append(dur)
                if dur < 10.0:
                    sub10s_count += 1
                    consecutive_sub10s += 1
                    if consecutive_sub10s > max_consecutive_sub10s:
                        max_consecutive_sub10s = consecutive_sub10s
                else:
                    consecutive_sub10s = 0

            # Contabilizar mesario se foi manual
            if current_hab_type == "MANUAL":
                mid_key = current_mesario_id or "Nao identificado"
                mesarios_contagem[mid_key] = mesarios_contagem.get(mid_key, 0) + 1

            # Faixa horaria
            h = vote_time.hour
            is_bio = (current_hab_type == "BIOMETRICA")
            if h < 12:
                faixa_key = "manha_08_12"
            elif h < 14:
                faixa_key = "almoco_12_14"
            elif h < 17:
                faixa_key = "tarde_14_17"
            else:
                faixa_key = "noite_apos_17"

            faixas[faixa_key]["total"] += 1
            if is_bio:
                faixas[faixa_key]["bio"] += 1
            else:
                faixas[faixa_key]["manual"] += 1

            # Reset por eleitor
            current_hab_type = "DESCONHECIDO"
            current_mesario_id = None

    tempo_medio = round(sum(duracoes) / len(duracoes), 1) if duracoes else 0.0
    pct_sub10s = round(sub10s_count / votos_totais * 100, 2) if votos_totais else 0.0

    distribuicao = {
        "sub_10s": sum(1 for d in duracoes if d < 10.0),
        "de_10s_a_20s": sum(1 for d in duracoes if 10.0 <= d < 20.0),
        "de_20s_a_45s": sum(1 for d in duracoes if 20.0 <= d < 45.0),
        "acima_45s": sum(1 for d in duracoes if d >= 45.0),
    }

    total_manuais = sum(mesarios_contagem.values())
    mesarios_lista = []
    for mid, count in sorted(mesarios_contagem.items(), key=lambda x: x[1], reverse=True):
        pct_man = round(count / total_manuais * 100, 1) if total_manuais else 0.0
        mesarios_lista.append({
            "mesario_id": mid,
            "liberacoes_manuais": count,
            "pct_total_manuais": pct_man
        })

    return {
        "log_disponivel": True,
        "total_votos_log": votos_totais,
        "tempo_medio_cabine_seg": tempo_medio,
        "votos_sub10s_contagem": sub10s_count,
        "votos_sub10s_pct": pct_sub10s,
        "sequencia_max_sub10s": max_consecutive_sub10s,
        "distribuicao_tempo_cabine": distribuicao,
        "flagrantes_biometria_mesario": flagrantes_mesario,
        "mesarios_habilitacao_manual": mesarios_lista,
        "votos_por_faixa_horaria": faixas
    }
