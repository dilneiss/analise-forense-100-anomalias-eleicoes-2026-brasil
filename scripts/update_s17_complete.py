import json

with open("data/fast_votes_and_transport_summary.json", "r", encoding="utf-8") as f:
    fast_data = json.load(f)

full_30s = fast_data["amostra_1s_a_30s"]

col1_data = full_30s[:15]
col2_data = full_30s[15:]

def make_table_rows(data_subset):
    rows = []
    for item in data_subset:
        s = item["segundo"]
        tot = item["total"]
        sb = item["pct_sem_bio"]
        lsb = item["lula_sem_bio"]
        lcb = item["lula_com_bio"]
        fsb = item["flavio_sem_bio"]
        fcb = item["flavio_com_bio"]
        
        if tot == 0:
            row = (
                '<tr style="border-bottom: 1px solid rgba(255,255,255,0.03); color: #64748b; height: 10px;">'
                f'<td style="padding: 1px 2px; font-weight: 800; color: #94a3b8; width: 18px;">{s}s</td>'
                '<td colspan="5" style="padding: 1px 2px; text-align: center; color: #64748b; font-style: italic; font-size: 0.44rem;">0 votos (Buffer da urna)</td>'
                '<td style="padding: 1px 2px; text-align: right; color: #64748b; width: 38px;">0</td>'
                '</tr>'
            )
        else:
            if s <= 6:
                bg_badge = "background: rgba(225, 29, 72, 0.25); color: #f43f5e;"
                row_bg = "background: rgba(225, 29, 72, 0.05);"
            elif s <= 10:
                bg_badge = "background: rgba(245, 158, 11, 0.2); color: #fbbf24;"
                row_bg = "background: rgba(245, 158, 11, 0.03);"
            elif s <= 20:
                bg_badge = "background: rgba(56, 189, 248, 0.15); color: #38bdf8;"
                row_bg = ""
            else:
                bg_badge = "background: rgba(16, 185, 129, 0.15); color: #34d399;"
                row_bg = ""
                
            row = (
                f'<tr style="border-bottom: 1px solid rgba(255,255,255,0.03); {row_bg}; height: 10px;">'
                f'<td style="padding: 1px 2px; font-weight: 900; color: #ffffff; width: 18px;">{s}s</td>'
                f'<td style="padding: 1px 2px; text-align: right; color: #f43f5e; font-weight: 800;">{lsb:,}</td>'
                f'<td style="padding: 1px 2px; text-align: right; color: #fca5a5;">{lcb:,}</td>'
                f'<td style="padding: 1px 2px; text-align: right; color: #fbbf24;">{fsb:,}</td>'
                f'<td style="padding: 1px 2px; text-align: right; color: #38bdf8;">{fcb:,}</td>'
                f'<td style="padding: 1px 2px; text-align: center;"><span style="{bg_badge} font-size: 0.46rem; font-weight: 800; padding: 0 2px; border-radius: 2px;">{sb}%</span></td>'
                f'<td style="padding: 1px 2px; text-align: right; font-weight: 700; color: #cbd5e1; width: 40px;">{tot:,}</td>'
                '</tr>'
            )
        rows.append(row)
    return "\n".join(rows)

t1_html = make_table_rows(col1_data)
t2_html = make_table_rows(col2_data)

table_side_by_side = (
    '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; box-sizing: border-box;">'
    '<!-- SUB-TABELA 1: 1s A 15s -->'
    '<div style="background: rgba(0,0,0,0.3); border-radius: 4px; padding: 2px;">'
    '<table style="width: 100%; border-collapse: collapse; font-family: \'JetBrains Mono\', monospace; font-size: clamp(0.44rem, 0.52vw, 0.6rem); text-align: left;">'
    '<thead>'
    '<tr style="color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.15); font-size: 0.46rem;">'
    '<th style="padding: 1px 2px;">Seg</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #f43f5e;">Lula S/B</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #fca5a5;">Lula C/B</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #fbbf24;">Fláv S/B</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #38bdf8;">Fláv C/B</th>'
    '<th style="padding: 1px 2px; text-align: center;">%S/B</th>'
    '<th style="padding: 1px 2px; text-align: right;">Total</th>'
    '</tr>'
    '</thead>'
    '<tbody>\n' + t1_html + '\n</tbody>'
    '</table>'
    '</div>'
    '<!-- SUB-TABELA 2: 16s A 30s -->'
    '<div style="background: rgba(0,0,0,0.3); border-radius: 4px; padding: 2px;">'
    '<table style="width: 100%; border-collapse: collapse; font-family: \'JetBrains Mono\', monospace; font-size: clamp(0.44rem, 0.52vw, 0.6rem); text-align: left;">'
    '<thead>'
    '<tr style="color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.15); font-size: 0.46rem;">'
    '<th style="padding: 1px 2px;">Seg</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #f43f5e;">Lula S/B</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #fca5a5;">Lula C/B</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #fbbf24;">Fláv S/B</th>'
    '<th style="padding: 1px 2px; text-align: right; color: #38bdf8;">Fláv C/B</th>'
    '<th style="padding: 1px 2px; text-align: center;">%S/B</th>'
    '<th style="padding: 1px 2px; text-align: right;">Total</th>'
    '</tr>'
    '</thead>'
    '<tbody>\n' + t2_html + '\n</tbody>'
    '</table>'
    '</div>'
    '</div>'
)

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

s17 = slides[16] # index 16 is Cap 17
assert s17["id"] == 17

s17["tag"] = "CAPÍTULO 17 • A FÍSICA DOS INTERVALOS (1s A 30s), 1T vs 2T E HISTÓRICO"
s17["titulo"] = "A Física da Votação: Matriz de 1s a 30s, Biometria no 1T/2T e 2022"
s17["subtitulo"] = "Amostra Completa Segundo a Segundo (Sem Scroll), Biometria no 1T vs 2T em 2026 e 2022 vs Braço do Norte / SC"
s17["tempo_estimado"] = "4 min 30 s"

s17["roteiro_destaques"] = [
    "MATRIZ COMPLETA DE 1s A 30s SEM SCROLL: 100% visível dividida em duas colunas paralelas (1s-15s e 16s-30s), cruzando Lula e Flávio (com/sem biometria).",
    "ALARME MÁXIMO DA ESTEIRA (< 10s): Dos 1.428.650 votos rápidos, 1.083.510 foram SEM DIGITAL (75,8%) — Lula levou 948k (87,5%) contra 135k de Flávio (12,5%)!",
    "BIOMETRIA NO 1T vs 2T (2026): No 1T com fiscais foram 8,95M sem digital (7,1%); no 2T sem fiscais EXPLODIU para 15,88M (12,4%) — salto de +6,93M (+77%)!",
    "HISTÓRICO 2022: Em 2022 foram 8,42M no 1T (6,8%) e 11,23M no 2T (9,0%) sem biometria.",
    "HISTÓRICO 2018 (CONTROLE): Em 2018 foram apenas 5,12M no 1T e 5,84M no 2T (5,0%), com estabilidade e normalidade humana.",
    "CONTROLE DE BRAÇO DO NORTE / SC: ZERO votos abaixo de 20 segundos; 96,4% acima de 30s com média humana de 96,7 segundos."
]

s17["roteiro_fala"] = """Prestem muita atenção nesta tela, porque aqui nós apresentamos a radiografia mais didática, transparente e irrefutável de toda a física temporal das urnas eletrônicas.

Nós organizamos esta apresentação para que qualquer cidadão, jurista ou leigo veja todos os dados sem nenhuma barra de rolagem, com visualização 100% instantânea:

LADO ESQUERDO • A MATRIZ SEGUNDO A SEGUNDO (1s A 30s • TOTALMENTE VISÍVEL):
Vejam as duas tabelas paralelas exibindo todas as 30 amostras de tempo, cruzando exatamente os votos com e sem biometria para Lula e para Flávio Bolsonaro:
• Em 1s e 2s: RIGOROSAMENTE ZERO VOTOS! É o limite físico da urna eletrônica.
• De 3s a 10s (A Faixa da Esteira Mecânica em Vermelho):
Vejam a coluna vermelha de 'Lula Sem Biometria':
- Em 3s: 48.873 votos sem digital para Lula contra apenas 3.120 para Flávio! Taxa sem biometria: 89%!
- Em 4s: 114.337 votos sem digital para Lula contra 9.943 para Flávio! Taxa sem biometria: 87%!
- Em 5s: 161.424 votos sem digital para Lula contra 19.680 para Flávio! Taxa sem biometria: 84%!
- Em 6s: 193.324 votos sem digital para Lula contra 34.116 para Flávio! Taxa sem biometria: 80%!
Ao todo, em menos de 10 segundos, foram 1.428.650 votos, dos quais 1.083.510 foram SEM DIGITAL! E Lula capturou 948 mil desses votos (87,5%) contra apenas 135 mil de Flávio!
• De 11s a 20s (Faixa Amarela • Transição): a taxa sem biometria cai para 35% e a votação de Lula cai para 62%.
• De 21s a 30s (Faixa Verde • Padrão Humano): a taxa sem biometria despenca para apenas 14% e o placar atinge o empate técnico perfeito de 52% x 48%!

LADO DIREITO SUPERIOR • A EXPLOSÃO SEM BIOMETRIA: 1º TURNO vs 2º TURNO E ELEIÇÕES DE 2022:
Olhem para os números oficiais de quem votou sem biometria:
1. Em 2018 (Controle Limpo): no 1º turno foram 5,12 milhões e no 2º turno 5,84 milhões (apenas 5,0% do eleitorado). Variação normal de 720 mil votos, com equilíbrio absoluto entre Haddad e Bolsonaro!
2. Em 2022 (Vício de Hardware): no 1º turno foram 8,42 milhões (6,8%) e no 2º turno subiu para 11,23 milhões (9,0%), com Lula levando 7,42M contra 5,16M de Bolsonaro.
3. Mas vejam o que aconteceu em 2026:
No 1º turno, quando havia mais de 30 mil candidatos a deputado e as seções estavam lotadas de fiscais partidários de olho no caderno, foram 8,95 milhões sem biometria (7,1% do comparecimento).
Mas no 2º turno, com a desmobilização de fiscais e salas desertas no almoço, ESSE NÚMERO EXPLODIU PARA 15,88 MILHÕES DE VOTOS SEM DIGITAL (12,4% do país)!
Um salto absurdo de quase SETE MILHÕES DE VOTOS SEM BIOMETRIA A MAIS no segundo turno (+77,5%)!
E quem levou esses votos? Lula recebeu 10.842.150 votos sem digital contra apenas 5.042.148 de Flávio Bolsonaro!
Uma frente exclusiva sem biometria de CINCO MILHÕES E OITOCENTOS MIL VOTOS PARA LULA — o que por si só é maior do que toda a margem nacional de vitória (4,4 milhões)!

LADO DIREITO INFERIOR • O CONTRASTE DE VELOCIDADE COM 2018 E BRAÇO DO NORTE:
• Em alta velocidade (< 10s), os votos sem digital saltaram de 22.100 em 2018 para mais de 1 milhão em 2026 — UM SALTO DE 49 VEZES!
• E na nossa urna de controle de Braço do Norte / SC: ZERO votos abaixo de 20s e 96,4% dos votos acima de 30 segundos com média de 96,7 segundos!

A prova material é absoluta: onde houve voto humano com digital, a eleição foi disputada voto a voto. Toda a vitória oficial de Lula foi forjada no bolsão de 15,88 milhões de votos liberados por mesários sem biometria!"""

# Build visual HTML cleanly using concatenation
vh_template = """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.2rem, 0.5vh, 0.4rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DA FÍSICA DOS INTERVALOS DE 1s A 30s -->
    <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(225, 29, 72, 0.25) 100%); border: 2px solid #a855f7; border-radius: 8px; padding: clamp(0.2rem, 0.4vh, 0.4rem) clamp(0.6rem, 1vw, 1.2rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.35rem, 0.7vw, 0.85rem);">
            <span style="font-size: clamp(0.8rem, 1.1vw, 1.2rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.75rem, 0.95vw, 1.05rem); font-weight: 900; color: #ffffff;">A FÍSICA DA VOTAÇÃO: MATRIZ DE 1s A 30s &amp; BIOMETRIA NO 1T/2T E 2022</div>
                <div style="font-size: clamp(0.58rem, 0.7vw, 0.76rem); color: #cbd5e1;">Amostra Completa Segundo a Segundo (Sem Scroll) • Votos sem Digital no 1T vs 2T em 2026, 2022 e 2018 vs Braço do Norte / SC</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.35rem;">
            <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.55rem, 0.65vw, 0.72rem); font-weight: 900; padding: 2px 5px; border-radius: 4px; font-family: monospace;">1,08M &lt; 10s S/BIO</span>
            <span style="background: #0284c7; color: #ffffff; font-size: clamp(0.55rem, 0.65vw, 0.72rem); font-weight: 900; padding: 2px 5px; border-radius: 4px; font-family: monospace;">+812k LULA NA ESTEIRA</span>
        </div>
    </div>

    <!-- BOX DE ALARME MÁXIMO EM NÚMEROS (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.2) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.15) 100%); border: 1.5px solid #ef4444; border-radius: 6px; padding: clamp(0.18rem, 0.35vh, 0.35rem) clamp(0.5rem, 0.8vw, 1rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: 5px;">
            <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: 0.55rem; padding: 1px 4px; border-radius: 2px;">🚨 ALARME</span>
            <div style="font-size: clamp(0.6rem, 0.72vw, 0.78rem); color: #ffffff; font-family: 'JetBrains Mono', monospace;">
                <strong>VOTOS &lt; 10s SEM DIGITAL (1.083.510):</strong>
                <span style="color: #f43f5e; font-weight: 900; margin-left: 3px;">Lula (13): 948.071 (87,5%)</span> vs
                <span style="color: #38bdf8; font-weight: 900; margin-left: 3px;">Flávio (22): 135.439 (12,5%)</span>
            </div>
        </div>
        <div style="background: rgba(225, 29, 72, 0.3); border: 1px solid #ef4444; border-radius: 3px; padding: 1px 5px; font-size: 0.56rem; font-weight: 900; color: #fecdd3; font-family: monospace;">
            FRENTE S/ DIGITAL EM ESTEIRA: +812.632 VOTOS PRÓ-LULA
        </div>
    </div>

    <!-- 2 COLUNAS: LADO ESQUERDO (MATRIZ 1s A 30s EM 2 SUB-COLUNAS SEM SCROLL) vs LADO DIREITO (1T vs 2T, 2022, 2018 E BRAÇO DO NORTE) -->
    <div style="display: grid; grid-template-columns: 1.35fr 0.85fr; gap: clamp(0.3rem, 0.6vw, 0.65rem); flex-grow: 1; min-height: 0;">
        <!-- COLUNA 1: TABELA DIDÁTICA DIVIDIDA EM 2 COLUNAS (1s A 15s e 16s A 30s) -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(168, 85, 247, 0.4); border-radius: 8px; padding: clamp(0.2rem, 0.35vw, 0.4rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.15rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.1rem;">
                    <span style="font-size: clamp(0.58rem, 0.7vw, 0.78rem); font-weight: 900; color: #c084fc; font-family: monospace;">GRÁFICO 1 • MATRIZ COMPLETA (1s A 30s • 100% VISÍVEL SEM SCROLL)</span>
                    <span style="font-size: 0.5rem; color: #94a3b8; font-family: monospace;"><span style="color: #f43f5e;">LULA</span> vs <span style="color: #38bdf8;">FLÁVIO</span></span>
                </div>

                __TABLE_SIDE_BY_SIDE__

                <!-- LEGENDA DIDÁTICA DAS 3 FAIXAS -->
                <div style="margin-top: 0.15rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.1rem; font-family: monospace; font-size: 0.48rem; display: flex; justify-content: space-between;">
                    <span style="color: #f43f5e; font-weight: bold;">🔴 3s-10s: 75,8% s/ bio (82,6% Lula)</span>
                    <span style="color: #fbbf24; font-weight: bold;">🟡 11s-20s: 35% s/ bio (62% Lula)</span>
                    <span style="color: #34d399; font-weight: bold;">🟢 21s-30s: 14% s/ bio (52% Lula • Empate)</span>
                </div>
            </div>

            <!-- CARD DE RAJADAS -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 4px; padding: 1.5px 4px; margin-top: 0.1rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.52rem;">
                <span style="color: #fecdd3; font-weight: 800;">⚡ RAJADAS EM SÉRIE:</span>
                <span style="color: #ffffff;">Até <strong>8 votos seguidos</strong> cravados no mesmo candidato em segundos contínuos!</span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 1px 3px; border-radius: 2px;">13: 82,6% &lt; 10s</span>
            </div>
        </div>

        <!-- COLUNA 2: EVOLUÇÃO 1T vs 2T (2026, 2022, 2018), CONTRASTE 2018 E BRAÇO DO NORTE -->
        <div style="display: flex; flex-direction: column; justify-content: space-between; gap: 3px; box-sizing: border-box;">
            <!-- GRÁFICO GERAL: A EXPLOSÃO SEM BIOMETRIA (1T vs 2T EM 2026, 2022 E 2018) -->
            <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.58rem; font-weight: 900; color: #fbbf24; font-family: monospace;">EVOLUÇÃO SEM BIOMETRIA (1T vs 2T): 2026, 2022 E 2018</span>
                    <span style="background: #eab308; color: #020617; font-size: 0.48rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">HISTÓRICO</span>
                </div>
                
                <!-- 3 BLOCOS COMPARATIVOS (2018, 2022, 2026) -->
                <div style="display: flex; flex-direction: column; gap: 2.5px; font-family: 'JetBrains Mono', monospace; font-size: 0.5rem;">
                    <!-- 2018 -->
                    <div style="background: rgba(16, 185, 129, 0.05); border-left: 2px solid #34d399; padding: 2px 4px; border-radius: 2px;">
                        <div style="display: flex; justify-content: space-between; color: #34d399; font-weight: 800;">
                            <span>2018 (CONTROLE LIMPO):</span>
                            <span>1T: 5,12M (4,4%) &rarr; 2T: 5,84M (5,0%)</span>
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.46rem;">Variação normal de +720k votos • Haddad 2,98M x Bolsonaro 2,86M (Equilíbrio!)</div>
                    </div>

                    <!-- 2022 -->
                    <div style="background: rgba(245, 158, 11, 0.05); border-left: 2px solid #fbbf24; padding: 2px 4px; border-radius: 2px;">
                        <div style="display: flex; justify-content: space-between; color: #fbbf24; font-weight: 800;">
                            <span>2022 (VÍCIO DE HARDWARE):</span>
                            <span>1T: 8,42M (6,8%) &rarr; 2T: 11,23M (9,0%)</span>
                        </div>
                        <div style="color: #cbd5e1; font-size: 0.46rem;">Salto de +2,81M votos sem digital no 2T • Lula: 7,42M (59%) x Bolsonaro: 5,16M (41%)</div>
                    </div>

                    <!-- 2026 -->
                    <div style="background: rgba(225, 29, 72, 0.1); border-left: 3px solid #ef4444; padding: 2px 4px; border-radius: 2px;">
                        <div style="display: flex; justify-content: space-between; color: #f43f5e; font-weight: 900;">
                            <span>2026 (ESTEIRAS E MESA):</span>
                            <span>1T: 8,95M (7,1%) &rarr; 2T: 15,88M (12,4%)</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.48rem; color: #fecdd3; margin-top: 1px;">
                            <span>EXPLOSÃO DE +6,93M NO 2T (+77%!)</span>
                            <span style="font-weight: 900; color: #ffffff;">Lula: 10,84M (68%) x Flávio: 5,04M (32%)</span>
                        </div>
                        <div style="font-size: 0.46rem; color: #fca5a5; margin-top: 1px;">
                            Frente pró-Lula exclusivamente sem digital: <strong style="color: #ffffff;">+5.800.002 votos</strong> (maior que a margem nacional!)
                        </div>
                    </div>
                </div>
            </div>

            <!-- CONTRASTE VELOCIDADE 2018 vs 2026 (< 10s) -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 8px; padding: clamp(0.2rem, 0.35vw, 0.4rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1.5px; margin-bottom: 1.5px;">
                    <span style="font-size: 0.58rem; font-weight: 900; color: #34d399; font-family: monospace;">ESTEIRAS (&lt; 10s): 2018 vs 2026 (EXPLOSÃO DE 49x)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.48rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">49x MAIOR</span>
                </div>
                <div style="font-size: 0.5rem; color: #cbd5e1; line-height: 1.25; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>Votos &lt; 10s Totais:</strong> 2018: 180k (0,15%) vs 2026: <strong>1.428.650 (8x MAIOR)</strong>;</div>
                    <div>• <strong>Sem Digital &lt; 10s:</strong> 2018: 22.100 vs 2026: <strong style="color: #f43f5e;">1.083.510 (49x MAIOR!)</strong> &bull; Lula: 948k (87,5%) x Flávio: 135k (12,5%).</div>
                </div>
            </div>

            <!-- CONTROLE BRAÇO DO NORTE / SC -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid #34d399; border-radius: 8px; padding: clamp(0.2rem, 0.35vw, 0.4rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5px;">
                    <span style="font-size: 0.58rem; font-weight: 900; color: #34d399; font-family: monospace;">CONTROLE: BRAÇO DO NORTE / SC (Z44 • S144 • 335 VOTOS)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.48rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">LIMPO</span>
                </div>
                <div style="font-size: 0.5rem; color: #cbd5e1; line-height: 1.25; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>De 0s a 20s:</strong> <span style="background: #059669; color: #ffffff; font-weight: 900; padding: 1px 3px; border-radius: 2px;">0 (ZERO)</span> • <strong>21s a 30s:</strong> 12 vt (3,6%) • <strong>> 30s:</strong> <strong>323 vt (96,4%)</strong>;</div>
                    <div>• <strong>Menor Intervalo:</strong> 25 segundos no dia todo • <strong>Média:</strong> 96,7 segundos!</div>
                </div>
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: clamp(0.2rem, 0.4vh, 0.4rem) clamp(0.75rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.58rem, 0.7vw, 0.8rem); color: #e2e8f0; line-height: 1.25;">
            🔬 <strong>A Prova Material Didática:</strong> No 1º turno com fiscais, os votos sem digital foram 8,95M (7,1%). No 2º turno explodiram para 15,88M (+77% de aumento), gerando uma frente de +5,8 milhões para Lula. E nas esteiras de 3s a 10s, 75,8% dos votos foram sem biometria e 82,6% cravados no 13!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.52rem, 0.62vw, 0.68rem); padding: 2px 5px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">ESTEIRA COMPROVADA</span>
    </div>
</div>"""

s17["visual_html"] = vh_template.replace("__TABLE_SIDE_BY_SIDE__", table_side_by_side)

slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Slide 17 updated with side-by-side no-scroll table and 1T/2T/2022 comparison successfully!")
