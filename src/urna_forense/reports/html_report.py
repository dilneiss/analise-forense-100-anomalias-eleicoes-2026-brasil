"""Relatorio HTML autocontido, sem recursos externos."""

from __future__ import annotations

import html
from datetime import datetime
from typing import Any, Optional

STATUS_LABEL = {
    "VALIDADO": "VALIDADO",
    "INCONSISTENTE": "INCONSISTENTE",
    "NAO_VALIDADO": "NÃO VALIDADO",
    "NAO_FOI_POSSIVEL_VERIFICAR": "NÃO FOI POSSÍVEL VERIFICAR",
}
STATUS_CLASS = {
    "VALIDADO": "ok",
    "INCONSISTENTE": "err",
    "NAO_VALIDADO": "err",
    "NAO_FOI_POSSIVEL_VERIFICAR": "warn",
}
ALTERATION_LABEL = {
    "SEM_EVIDENCIA_DE_ALTERACAO": "SEM EVIDÊNCIA DE ALTERAÇÃO",
    "ALTERACAO_COMPROVAVEL": "ALTERAÇÃO COMPROVÁVEL",
    "ALTERACAO_POSSIVEL": "ALTERAÇÃO POSSÍVEL",
    "NAO_VERIFICAVEL": "NÃO VERIFICÁVEL",
}


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _badge(status: str) -> str:
    return (
        f'<span class="badge {STATUS_CLASS.get(status, "warn")}">'
        f"{_e(STATUS_LABEL.get(status, status))}</span>"
    )


def _time(value: Optional[str], fmt: str = "%d/%m/%Y %H:%M:%S") -> str:
    if not value:
        return "NÃO IDENTIFICADO"
    try:
        return datetime.fromisoformat(value).strftime(fmt)
    except ValueError:
        return value


def _duration(seconds: Optional[int]) -> str:
    if seconds is None:
        return "NÃO IDENTIFICADO"
    seconds = int(seconds)
    return (
        f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
    )


def _status_sort(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    return sorted(findings, key=lambda item: (order.get(item["severity"], 3), item["type"]))


CSS = """
:root{
  --bg:#f4f6f8;--card:#ffffff;--fg:#16202b;--muted:#5d6b7a;--border:#d9e1e8;
  --accent:#0b57d0;--ok:#18794e;--warn:#8a5a00;--err:#b3261e;--soft:#eef2f6;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#0f141a;--card:#161d25;--fg:#e8eef5;--muted:#98a6b5;--border:#273241;
  --accent:#7aa7ff;--ok:#4ac486;--warn:#e0b04a;--err:#ff7b72;--soft:#1d2631;}
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{background:var(--card);border-bottom:1px solid var(--border);padding:28px 20px}
main{max-width:1120px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:24px;margin:0 0 4px;letter-spacing:-.2px}
h2{font-size:18px;margin:34px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border)}
h3{font-size:15px;margin:18px 0 8px}
p{margin:8px 0}
.sub{color:var(--muted);font-size:13px}
.mono{font-family:var(--mono);font-size:12.5px;word-break:break-all}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px}
.card .label{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.card .value{font-size:24px;font-weight:650;margin-top:4px;font-variant-numeric:tabular-nums}
.card .note{color:var(--muted);font-size:12.5px;margin-top:4px}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;letter-spacing:.03em}
.badge.ok{background:color-mix(in srgb,var(--ok) 16%,transparent);color:var(--ok)}
.badge.warn{background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn)}
.badge.err{background:color-mix(in srgb,var(--err) 16%,transparent);color:var(--err)}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.callout{border:1px solid var(--border);border-left:4px solid var(--warn);background:var(--card);border-radius:8px;padding:14px 16px;margin:18px 0}
.callout.err{border-left-color:var(--err)}
.callout.info{border-left-color:var(--accent)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--border);border-radius:8px;overflow:hidden}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border);font-size:13.5px;vertical-align:top}
th{background:var(--soft);font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
tr:last-child td{border-bottom:none}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.timeline{list-style:none;margin:0;padding:0 0 0 22px;border-left:2px solid var(--border)}
.timeline li{position:relative;padding:0 0 20px 14px}
.timeline li::before{content:"";position:absolute;left:-8px;top:5px;width:10px;height:10px;border-radius:50%;background:var(--accent);border:2px solid var(--card)}
.timeline .when{font-family:var(--mono);font-size:13px;font-weight:650}
.timeline .what{font-weight:600}
.timeline .src{color:var(--muted);font-size:12px;word-break:break-word}
.timeline details{margin-top:4px;color:var(--muted);font-size:12px}
.split{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:760px){.split{grid-template-columns:1fr}}
details.box{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin:8px 0}
details.box summary{cursor:pointer;font-weight:600}
.bars{display:flex;align-items:flex-end;gap:3px;height:90px;margin-top:10px}
.bar{flex:1;background:var(--accent);opacity:.75;border-radius:2px 2px 0 0;min-height:1px;position:relative}
.bar:hover{opacity:1}
.bar span{display:none;position:absolute;bottom:100%;left:50%;transform:translateX(-50%);background:var(--card);border:1px solid var(--border);padding:2px 5px;border-radius:4px;font-size:11px;white-space:nowrap}
.bar:hover span{display:block}
.hours{display:flex;gap:3px;font-size:10.5px;color:var(--muted);margin-top:4px}
.hours span{flex:1;text-align:center}
ul.tight{margin:6px 0;padding-left:20px}
ul.tight li{margin:4px 0}
pre{background:var(--soft);border:1px solid var(--border);border-radius:8px;padding:12px;overflow:auto;font-family:var(--mono);font-size:12px}
footer{color:var(--muted);font-size:12px;border-top:1px solid var(--border);margin-top:36px;padding-top:14px}
@media print{
  body{background:#fff;color:#000;font-size:11pt}
  header,main{max-width:none;padding:0}
  .card,table{break-inside:avoid}
  h2{break-after:avoid}
  details.box{break-inside:avoid}
  details.box>summary{list-style:none}
}
"""


def _header(report: dict[str, Any]) -> str:
    target = report["target"]
    conclusion = report["conclusion"]
    integrity = report["integrity"]
    badges = [
        _badge(integrity["status"]),
        f'<span class="badge {"ok" if integrity["authenticity"] == "VALIDADO" else "warn"}">'
        f"ASSINATURA: {_e(STATUS_LABEL.get(integrity['authenticity'], integrity['authenticity']))}</span>",
        f'<span class="badge {"ok" if integrity["alteration"] == "SEM_EVIDENCIA_DE_ALTERACAO" else "warn" if integrity["alteration"] == "NAO_VERIFICAVEL" else "err"}">'
        f"{_e(ALTERATION_LABEL.get(integrity['alteration'], integrity['alteration']))}</span>",
    ]
    return f"""
<header>
  <div style="max-width:1120px;margin:0 auto">
    <div class="sub">Auditoria técnica de arquivos da urna eletrônica</div>
    <h1>Urna {_e(target['uf'])} · {_e(target.get('municipio_nome') or 'Município ' + str(target['municipio_codigo_tse']))} · Zona {target['zona']:04d} · Seção {target['secao']:04d}</h1>
    <div class="sub">
      Eleição de {_e(_time(report['timeline'].get('election_date'), '%d/%m/%Y'))} ·
      turno {_e(report['timeline'].get('turn') if report['timeline'].get('turn') is not None else 'não identificado')} ·
      análise em {_e(_time(report['analysis']['started_at']))}
    </div>
    <div class="badges">{''.join(badges)}</div>
  </div>
</header>"""


def _premise(report: dict[str, Any]) -> str:
    findings = [
        item
        for item in report["findings"]
        if item["type"] in ("DIVERGENCIA_TURNO", "DIVERGENCIA_DATA_ELEICAO", "PREMISSA_DIVERGENTE")
    ]
    if not findings:
        return ""
    items = "".join(
        f"<li><strong>{_e(item['type'])}</strong>: {_e(item['message'])}<br>"
        f'<span class="sub mono">{_e(item.get("details", ""))}</span></li>'
        for item in findings
    )
    return f"""
<div class="callout err">
  <strong>Divergência entre a solicitação e o conteúdo dos arquivos</strong>
  <p>Os arquivos analisados não correspondem a todos os dados pedidos. Isso não é,
  por si, sinal de adulteração: o pedido e a evidência apontam para pleitos/turnos
  diferentes. A análise abaixo é a dos arquivos realmente presentes.</p>
  <ul class="tight">{items}</ul>
</div>"""


def _results(report: dict[str, Any]) -> str:
    bu = report.get("bu")
    if not bu:
        return '<p class="sub">BU indisponível.</p>'
    eleicoes = bu.get("eleicoes", [])
    cargos = [
        (eleicao["id_eleicao"], cargo)
        for eleicao in eleicoes
        for resultado in eleicao["resultados"]
        for cargo in resultado["cargos"]
    ]
    aptos = eleicoes[0]["qtd_eleitores_aptos"] if eleicoes else None
    comparecimento = bu.get("comparecimento")
    faltosos = (aptos - comparecimento) if aptos is not None and comparecimento is not None else None
    president = next((cargo for _, cargo in cargos if cargo["codigo_cargo"] == 1), None)
    headline = president or (cargos[0][1] if cargos else None)
    if not headline:
        return '<p class="sub">BU sem cargos.</p>'
    tipos = headline["tipos_voto"]
    validos = tipos.get("nominal", 0) + tipos.get("legenda", 0)
    cards = [
        ("Eleitores aptos", aptos, "caderno da seção + transferências"),
        ("Comparecimento", comparecimento, f"habilitação biométrica {bu.get('detalhamento_comparecimento', {}).get('por_biometria', '—')}"),
        ("Votos válidos", validos, f"cargo {headline['cargo']}"),
        ("Brancos", tipos.get("branco", 0), f"cargo {headline['cargo']}"),
        ("Nulos", tipos.get("nulo", 0), f"cargo {headline['cargo']}"),
        ("Abstenção", faltosos, "aptos − comparecimento"),
    ]
    cards_html = "".join(
        f'<div class="card"><div class="label">{_e(label)}</div>'
        f'<div class="value">{_e(value if value is not None else "—")}</div>'
        f'<div class="note">{_e(note)}</div></div>'
        for label, value, note in cards
    )
    candidates = (report.get("imgbu") or {}).get("candidatos_impresso") or {}
    blocks = []
    for eleicao_id, cargo in cargos:
        votos = cargo["votos"]
        nominal = [voto for voto in votos if voto["tipo_voto_nome"] == "nominal"]
        nominal.sort(key=lambda item: -item["quantidade"])
        linhas = []
        for voto in nominal:
            ident = voto.get("identificacao_votavel") or {}
            numero = ident.get("numero")
            info = candidates.get(str(numero)) or {}
            nome = info.get("nome") or "—"
            partido = ident.get("partido")
            linhas.append(
                f"<tr><td class='num'>{_e(numero)}</td><td>{_e(nome)}</td>"
                f"<td class='num'>{_e(partido)}</td><td class='num'>{voto['quantidade']}</td></tr>"
            )
        legenda = [voto for voto in votos if voto["tipo_voto_nome"] == "legenda"]
        for voto in legenda:
            ident = voto.get("identificacao_votavel") or {}
            linhas.append(
                f"<tr><td class='num'>{_e(ident.get('partido'))}</td>"
                f"<td><em>voto de legenda</em></td>"
                f"<td class='num'>{_e(ident.get('partido'))}</td>"
                f"<td class='num'>{voto['quantidade']}</td></tr>"
            )
        others = [
            ("Brancos", "branco"),
            ("Nulos", "nulo"),
            ("Cargo sem candidato", "cargo_sem_candidato"),
        ]
        for label, kind in others:
            value = cargo["tipos_voto"].get(kind, 0)
            if value:
                linhas.append(
                    f"<tr><td class='num'>—</td><td>{_e(label)}</td>"
                    f"<td class='num'>—</td><td class='num'>{value}</td></tr>"
                )
        blocks.append(
            f"""
<details class="box">
  <summary>{_e(cargo['cargo'])} · cargo {cargo['codigo_cargo']} · eleição {eleicao_id} · total {cargo['total_votos']}</summary>
  <table style="margin-top:10px">
    <thead><tr><th class="num">Número</th><th>Nome (BU impresso)</th><th class="num">Partido</th><th class="num">Votos</th></tr></thead>
    <tbody>{''.join(linhas)}</tbody>
  </table>
  <p class="sub">O BU estruturado não contém nomes de candidatos; os nomes vêm do BU impresso e são exibidos quando a linha foi reconhecida com segurança.</p>
</details>"""
        )
    return f"""
<div class="grid">{cards_html}</div>
<h3>Votos por cargo</h3>
{''.join(blocks)}
"""


def _timeline(report: dict[str, Any]) -> str:
    timeline = report["timeline"]
    items = []
    for milestone in timeline["milestones"]:
        stamp = milestone.get("timestamp")
        status = milestone.get("status")
        when = _time(stamp) if stamp else "NÃO IDENTIFICADO"
        refs = milestone.get("references") or []
        source = "; ".join(
            f"{ref.get('source')}" + (f" @offset {ref.get('offset')}" if ref.get("offset") is not None else "")
            for ref in refs
        )
        alternatives = milestone.get("alternatives") or []
        alt_html = ""
        if alternatives:
            alt_html = (
                '<details><summary>Outros eventos relacionados</summary><ul class="tight">'
                + "".join(
                    f"<li>{_e(ref.get('note') or '')} — {_e(ref.get('raw') or '')}</li>"
                    for ref in alternatives
                )
                + "</ul></details>"
            )
        detail = ""
        if refs and refs[0].get("raw"):
            detail = f'<details><summary>Linha do log</summary><pre>{_e(refs[0]["raw"])}</pre></details>'
        items.append(
            f'<li><div class="when">{_e(when)}</div>'
            f'<div class="what">{_e(milestone["label"])} '
            f'<span class="badge {"ok" if status == "identificado" else "warn"}">'
            f'{"IDENTIFICADO" if status == "identificado" else "NÃO IDENTIFICADO"}</span></div>'
            f'<div class="src">{_e(milestone["interpretation"])}</div>'
            f'<div class="src mono">{_e(source)}</div>{detail}{alt_html}</li>'
        )
    voting = timeline.get("voting", {})
    hours = voting.get("votos_por_hora") or {}
    bars = ""
    if hours:
        maximum = max(hours.values()) or 1
        bars = '<div class="bars">' + "".join(
            f'<div class="bar" style="height:{max(2, round(value / maximum * 88))}px">'
            f"<span>{_e(hour)}:00 · {value}</span></div>"
            for hour, value in hours.items()
        ) + "</div><div class='hours'>" + "".join(
            f"<span>{_e(hour)}</span>" for hour in hours
        ) + "</div>"
    stats = [
        ("Duração da votação", _duration(voting.get("duracao_votacao_segundos"))),
        ("Votos computados", voting.get("votos_computados", "—")),
        ("Abertura → 1º voto", f"{voting.get('abertura_ate_primeiro_voto_segundos', '—')} s"),
        ("Aberturas (reinícios)", voting.get("reinicios_abertura_no_dia", "—")),
        ("Alertas no dia", voting.get("alertas_no_dia", "—")),
        ("Votos antes da abertura", voting.get("votos_antes_da_abertura", "—")),
        ("Votos após encerramento", voting.get("votos_apos_encerramento", "—")),
        (
            "Maior intervalo entre votos",
            f"{voting.get('maior_intervalo_s', '—')} s",
        ),
    ]
    stats_html = "".join(
        f'<div class="card"><div class="label">{_e(label)}</div><div class="value" style="font-size:18px">{_e(value)}</div></div>'
        for label, value in stats
    )
    return f"""
<div class="split">
  <div>
    <h3>Marcos</h3>
    <ul class="timeline">{''.join(items)}</ul>
  </div>
  <div>
    <h3>Operação no dia</h3>
    <div class="grid">{stats_html}</div>
    <h3>Votos computados por hora</h3>
    {bars or '<p class="sub">Sem eventos de voto para o dia da eleição.</p>'}
  </div>
</div>"""


def _integrity(report: dict[str, Any]) -> str:
    integrity = report["integrity"]
    checks = "".join(
        f'<div class="card"><div class="label">{_e(check["label"])}</div>'
        f'<div style="margin:6px 0">{_badge(check["status"])}</div>'
        f'<div class="note">{_e(check["detail"])}</div></div>'
        for check in integrity["checks"]
        if check["key"]
        in {
            "hashes_assinados",
            "hash_autoassinado_sw",
            "hash_autoassinado_hw",
            "assinatura_hardware",
            "assinatura_software",
            "cadeia_certificacao",
            "bu_cadeia_hashes",
            "bu_aritmetica",
            "rdv_registros",
            "log_legivel",
            "log_relogio",
            "log_codigo_linha",
            "ordem_temporal",
        }
    )
    hashes = "".join(
        f"<tr><td class='mono'>{_e(item['file'])}</td>"
        f"<td class='mono'>{_e(item['declared_sha512'])}</td>"
        f"<td class='mono'>{_e(item['calculated_sha512'] or '—')}</td>"
        f"<td>{_badge('VALIDADO' if item['match'] else ('NAO_FOI_POSSIVEL_VERIFICAR' if item['match'] is None else 'INCONSISTENTE'))}</td></tr>"
        for item in integrity["hash_checks"]
    )
    signature = report.get("signatures") or {}
    hw = signature.get("assinatura_hardware") or {}
    cert = hw.get("certificado") or {}
    cert_rows = ""
    if cert:
        cert_rows = (
            f"<tr><th>Titular</th><td class='mono'>{_e(cert.get('subject'))}</td></tr>"
            f"<tr><th>Emissor</th><td class='mono'>{_e(cert.get('issuer'))}</td></tr>"
            f"<tr><th>Número de série</th><td class='mono'>{_e(cert.get('serial_hex'))}</td></tr>"
            f"<tr><th>SHA-256</th><td class='mono'>{_e(cert.get('sha256'))}</td></tr>"
            f"<tr><th>Validade</th><td>{_e(cert.get('not_before'))} — {_e(cert.get('not_after'))}</td></tr>"
            f"<tr><th>Chave</th><td>{_e(cert.get('public_key_type'))} · OID {_e(cert.get('public_key_oid'))}</td></tr>"
        )
    model = signature.get("modelo_urna")
    return f"""
<div class="grid">{checks}</div>
<h3>Hashes SHA-512 assinados</h3>
<p class="sub">O arquivo de assinatura registra o SHA-512 de cada arquivo gerado pela urna.
O valor é recalculado sobre o arquivo fornecido. Arquivos listados e ausentes não
podem ser conferidos.</p>
<table>
  <thead><tr><th>Arquivo</th><th>SHA-512 assinado</th><th>SHA-512 calculado</th><th>Situação</th></tr></thead>
  <tbody>{hashes}</tbody>
</table>
<h3>Assinatura e certificado</h3>
<div class="callout info">
  <p><strong>Modelo da urna:</strong> {_e(model or 'não identificado')} ·
  <strong>Algoritmo de hardware:</strong> {_e(hw.get('algoritmo_assinatura'))}
  ({_e(hw.get('bits'))} bits) · <strong>Algoritmo de software:</strong>
  {_e((signature.get('assinatura_software') or {}).get('algoritmo_assinatura'))}.</p>
  <p>{_e((hw.get('verificacao') or {}).get('detail') or '')}</p>
  <p>{_e((signature.get('cadeia_certificacao') or {}).get('detail') or '')}</p>
</div>
<table><tbody>{cert_rows}</tbody></table>
"""


def _matrix(report: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{_e(item['relacao'])}</td><td>{_badge(item['status'])}</td>"
        f"<td class='sub'>{_e(item['detalhe'])}</td></tr>"
        for item in report["consistency"]["matrix"]
    )
    return f"""
<table>
  <thead><tr><th>Relação verificada</th><th>Situação</th><th>O que foi comparado</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""


def _findings(report: dict[str, Any]) -> str:
    findings = _status_sort(report["findings"])
    if not findings:
        return '<div class="callout info"><strong>Nenhum alerta.</strong> As verificações disponíveis não encontraram inconsistência.</div>'
    blocks = []
    for item in findings:
        css = "err" if item["severity"] == "ERROR" else "warn" if item["severity"] == "WARNING" else "info"
        evidence = ""
        if item.get("evidence"):
            evidence = (
                '<div class="sub mono">'
                + _e(", ".join(str(value) for value in item["evidence"][:12]))
                + "</div>"
            )
        blocks.append(
            f'<div class="callout {css}"><strong>[{_e(item["severity"])}] {_e(item["type"])}</strong>'
            f"<p>{_e(item['message'])}</p>"
            + (f'<p class="sub">{_e(item["details"])}</p>' if item.get("details") else "")
            + evidence
            + "</div>"
        )
    blocks.append(
        '<p class="sub">Uma inconsistência não autoriza, isoladamente, concluir que houve '
        "adulteração. O relatório descreve o que foi comparado e o que não pôde ser verificado.</p>"
    )
    return "".join(blocks)


def _files(report: dict[str, Any]) -> str:
    integrity = report["integrity"]
    hash_status = {
        item["file"]: item for item in integrity.get("hash_checks", [])
    }
    rows = []
    for item in report["target"]["files"]:
        name = item["path"].split("/")[-1]
        status = hash_status.get(name)
        if status:
            badge = _badge(
                "VALIDADO"
                if status["match"]
                else ("NAO_FOI_POSSIVEL_VERIFICAR" if status["match"] is None else "INCONSISTENTE")
            )
        else:
            badge = '<span class="badge warn">NÃO LISTADO NA ASSINATURA</span>'
        rows.append(
            f"<tr><td class='mono'>{_e(item['path'])}</td>"
            f"<td class='num'>{item['size']:,}</td>"
            f"<td>{_e(item['detected_type'])}</td>"
            f"<td class='mono'>{_e(item['sha256'])}</td>"
            f"<td>{badge}</td></tr>"
        )
    return f"""
<table>
  <thead><tr><th>Arquivo</th><th class="num">Bytes</th><th>Tipo detectado</th><th>SHA-256</th><th>Hash assinado</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>"""


def _method(report: dict[str, Any]) -> str:
    provenance = report.get("provenance", {})
    documented = "".join(f"<li>{_e(item)}</li>" for item in provenance.get("format_documentation", []))
    inferred = "".join(f"<li>{_e(item)}</li>" for item in provenance.get("inferred", []))
    limitations = "".join(
        f"<li>{_e(item)}</li>" for item in report["conclusion"]["limitacoes"]
    )
    extracted = "".join(
        f"<li class='mono'>{_e(item['path'])} · SHA-256 {_e(item['sha256'])}</li>"
        for item in report.get("extracted", [])
    )
    return f"""
<h3>Formato documentado</h3>
<ul class="tight">{documented}</ul>
<h3>Formato inferido / observado</h3>
<ul class="tight">{inferred}</ul>
<h3>Limitações desta análise</h3>
<ul class="tight">{limitations or '<li>Nenhuma limitação registrada.</li>'}</ul>
<h3>Artefatos extraídos (em <span class="mono">analysis/</span>)</h3>
<ul class="tight">{extracted or '<li>Nenhum artefato extraído.</li>'}</ul>
<h3>Reprodução</h3>
<pre>python analyzer.py --input "&lt;pasta da urna&gt;" --output "&lt;pasta analysis&gt;" \
  --uf {_e(report['target']['uf'])} --municipio {report['target']['municipio_codigo_tse']} \
  --zona {report['target']['zona']} --secao {report['target']['secao']} \
  --turno {_e(report['timeline'].get('turn') or '1')} --data-eleicao {_e(report['timeline'].get('election_date') or '')}</pre>
"""


def render_html(report: dict[str, Any]) -> str:
    integrity = report["integrity"]
    conclusion = report["conclusion"]
    title = (
        f"Urna {report['target']['uf'].upper()} {report['target']['municipio_codigo_tse']} "
        f"Z{report['target']['zona']:04d} S{report['target']['secao']:04d}"
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(title)} · auditoria</title>
<style>{CSS}</style>
</head>
<body>
{_header(report)}
<main>
  {_premise(report)}
  <div class="callout {'info' if integrity['alteration'] == 'SEM_EVIDENCIA_DE_ALTERACAO' else 'err' if integrity['alteration'] in ('ALTERACAO_COMPROVAVEL','ALTERACAO_POSSIVEL') else ''}">
    <strong>Conclusão técnica</strong>
    <p>{_e(conclusion['resumo'])}</p>
    <p class="sub">Integridade: {_e(STATUS_LABEL.get(integrity['status'], integrity['status']))} ·
    Autenticidade: {_e(STATUS_LABEL.get(integrity['authenticity'], integrity['authenticity']))} ·
    Alteração: {_e(ALTERATION_LABEL.get(integrity['alteration'], integrity['alteration']))}</p>
  </div>

  <h2>Identificação</h2>
  <div class="grid">
    <div class="card"><div class="label">UF</div><div class="value">{_e(report['target']['uf'].upper())}</div></div>
    <div class="card"><div class="label">Município</div><div class="value" style="font-size:19px">{_e(report['target'].get('municipio_nome') or '—')}</div><div class="note">código TSE {report['target']['municipio_codigo_tse']}</div></div>
    <div class="card"><div class="label">Zona</div><div class="value">{report['target']['zona']:04d}</div></div>
    <div class="card"><div class="label">Seção</div><div class="value">{report['target']['secao']:04d}</div></div>
    <div class="card"><div class="label">Turno</div><div class="value">{_e(report['timeline'].get('turn') if report['timeline'].get('turn') is not None else '—')}</div><div class="note">deduzido do log e do BU impresso</div></div>
    <div class="card"><div class="label">Eleição</div><div class="value" style="font-size:19px">{_e(_time(report['timeline'].get('election_date'), '%d/%m/%Y'))}</div></div>
  </div>

  <h2>Resultado</h2>
  {_results(report)}

  <h2>Linha do tempo</h2>
  {_timeline(report)}

  <h2>Integridade</h2>
  {_integrity(report)}

  <h2>Coerência entre arquivos</h2>
  {_matrix(report)}

  <h2>Alertas</h2>
  {_findings(report)}

  <h2>Arquivos analisados</h2>
  {_files(report)}

  <h2>Método, formato e limites</h2>
  {_method(report)}

  <footer>
    Gerado por {_e(report['tool']['name'])} {_e(report['tool']['version'])} em
    {_e(_time(report['analysis']['finished_at']))} ·
    entrada <span class="mono">{_e(report['analysis']['input_root'])}</span> ·
    escopo de hash: {_e(report['analysis']['hash_scope'])} ·
    {report['analysis']['duration_seconds']} s.
    <br>Arquivos originais tratados em modo somente leitura; a verificação
    pós-execução {('confirmou' if report['post_run_verification']['ok'] else 'NÃO confirmou')}
    que os hashes da urna não mudaram durante a análise.
  </footer>
</main>
</body>
</html>
"""
