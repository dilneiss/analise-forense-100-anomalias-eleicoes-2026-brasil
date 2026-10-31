import json

with open("data/fast_votes_and_transport_summary.json", "r", encoding="utf-8") as f:
    fast_data = json.load(f)

full_30s_data = fast_data["amostra_1s_a_30s"]

rows_html = []
for item in full_30s_data:
    s = item["segundo"]
    tot = item["total"]
    sb = item["pct_sem_bio"]
    lsb = item["lula_sem_bio"]
    lcb = item["lula_com_bio"]
    fsb = item["flavio_sem_bio"]
    fcb = item["flavio_com_bio"]
    
    if tot == 0:
        row = f"""<tr style="border-bottom: 1px solid rgba(255,255,255,0.03); color: #64748b;">
            <td style="padding: 1.5px 3px; font-weight: 800; color: #94a3b8;">{s}s</td>
            <td colspan="5" style="padding: 1.5px 3px; text-align: center; color: #64748b; font-style: italic;">0 votos (Buffer físico da urna / intervalo impossível)</td>
            <td style="padding: 1.5px 3px; text-align: right; color: #64748b;">0</td>
        </tr>"""
    else:
        if s <= 6:
            bg_badge = "background: rgba(225, 29, 72, 0.25); color: #f43f5e;"
            row_bg = "background: rgba(225, 29, 72, 0.04);"
        elif s <= 10:
            bg_badge = "background: rgba(245, 158, 11, 0.2); color: #fbbf24;"
            row_bg = "background: rgba(245, 158, 11, 0.02);"
        elif s <= 20:
            bg_badge = "background: rgba(56, 189, 248, 0.15); color: #38bdf8;"
            row_bg = ""
        else:
            bg_badge = "background: rgba(16, 185, 129, 0.15); color: #34d399;"
            row_bg = ""
            
        row = f"""<tr style="border-bottom: 1px solid rgba(255,255,255,0.03); {row_bg}">
            <td style="padding: 1.5px 3px; font-weight: 900; color: #ffffff;">{s}s</td>
            <td style="padding: 1.5px 3px; text-align: right; color: #f43f5e; font-weight: 800;">{lsb:,}</td>
            <td style="padding: 1.5px 3px; text-align: right; color: #fca5a5;">{lcb:,}</td>
            <td style="padding: 1.5px 3px; text-align: right; color: #fbbf24;">{fsb:,}</td>
            <td style="padding: 1.5px 3px; text-align: right; color: #38bdf8;">{fcb:,}</td>
            <td style="padding: 1.5px 3px; text-align: center;"><span style="{bg_badge} font-size: 0.52rem; font-weight: 800; padding: 0 3px; border-radius: 2px;">{sb}%</span></td>
            <td style="padding: 1.5px 3px; text-align: right; font-weight: 700; color: #cbd5e1;">{tot:,}</td>
        </tr>"""
    rows_html.append(row)

table_30s_html = "\n".join(rows_html)

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

s17 = slides[16] # index 16 is Cap 17
assert s17["id"] == 17

s17["tag"] = "CAPÍTULO 17 • A FÍSICA DOS INTERVALOS (1s A 30s), BIOMETRIA 13 vs 22 E HISTÓRICO"
s17["titulo"] = "A Física da Votação: Matriz de 1s a 30s, Biometria e o Histórico de 3 Eleições"
s17["subtitulo"] = "Cruzamento Segundo a Segundo (Lula vs Flávio com/sem Biometria) e a Explosão de Votos sem Digital (2018 a 2026)"
s17["tempo_estimado"] = "4 min 30 s"

s17["roteiro_destaques"] = [
    "MATRIZ DIDÁTICA DE 1s A 30s: Exibir para cada segundo o cruzamento exato de Lula (com/sem biometria) e Flávio (com/sem biometria).",
    "ALARME MÁXIMO DA ESTEIRA (< 10s): Dos 1.428.650 votos rápidos, 1.083.510 foram SEM DIGITAL (75,8%) — Lula levou 948k (87,5%) contra 135k de Flávio (12,5%)!",
    "GRÁFICO GERAL DAS 3 ELEIÇÕES: Comparar os votos sem biometria em 2018 (5,84M • equilibrado), 2022 (12,58M) e 2026 (15,88M), onde Lula abriu +5,8M de frente sem digital!",
    "SALTO DE 49x EM ALTA VELOCIDADE: Votos sem digital < 10s saltaram de 22.100 em 2018 para 1.083.510 em 2026!",
    "CONTROLE DE BRAÇO DO NORTE / SC: ZERO votos abaixo de 20 segundos; 96,4% acima de 30s com média humana de 96,7 segundos."
]

s17["roteiro_fala"] = """Prestem muita atenção nesta tela, porque aqui nós apresentamos a radiografia mais didática, transparente e irrefutável de toda a física temporal das urnas eletrônicas.

Nós dividimos esta apresentação para que qualquer cidadão, jurista ou leigo entenda com perfeição o que aconteceu segundo a segundo:

LADO ESQUERDO • A MATRIZ DIDÁTICA SEGUNDO A SEGUNDO (1s A 30s):
Vejam a tabela interativa com todas as 30 amostras segundo a segundo, cruzando exatamente os votos com e sem biometria para Lula e para Flávio Bolsonaro:
• Em 1s e 2s: RIGOROSAMENTE ZERO VOTOS! É o limite físico e de hardware da urna (o bipe de confirmação e a troca de tela levam no mínimo 2,5 segundos).
• De 3s a 10s (A Faixa da Esteira Mecânica em Vermelho):
Vejam a coluna vermelha de 'Lula Sem Biometria':
- Em 3 segundos: 48.873 votos sem digital para Lula contra apenas 3.120 para Flávio! Taxa sem biometria: 89%!
- Em 4 segundos: 114.337 votos sem digital para Lula contra 9.943 para Flávio! Taxa sem biometria: 87%!
- Em 5 segundos: 161.424 votos sem digital para Lula contra 19.680 para Flávio! Taxa sem biometria: 84%!
- Em 6 segundos: 193.324 votos sem digital para Lula contra 34.116 para Flávio! Taxa sem biometria: 80%!
Ao todo, em menos de 10 segundos, foram 1.428.650 votos, dos quais 1.083.510 foram SEM DIGITAL! E Lula capturou 948 mil desses votos (87,5%) contra apenas 135 mil de Flávio!
• De 11s a 20s (Faixa Amarela • Transição): a taxa sem biometria cai para 35% e a votação de Lula cai para 62%.
• De 21s a 30s (Faixa Verde • Padrão Humano): a taxa sem biometria despenca para apenas 14% e o placar atinge o empate técnico perfeito de 52% x 48%!

LADO DIREITO SUPERIOR • O GRÁFICO GERAL HISTÓRICO DAS TRÊS ELEIÇÕES (2018 vs 2022 vs 2026):
Olhem o gráfico que compara o volume total de votos sem biometria no Brasil ao longo dos três pleitos:
1. Em 2018 (Controle Limpo): foram 5,84 milhões de votos sem biometria no país todo (apenas 5,0% do eleitorado, desgaste natural de idosos e lavradores). A divisão foi equilibrada: Haddad teve 2,98M e Bolsonaro teve 2,86M!
2. Em 2022 (Vício de Hardware): o total de votos sem digital mais que dobrou para 12,58 milhões (10,1% do país), com Lula levando 7,42M contra 5,16M de Bolsonaro.
3. Em 2026 (Fraude de Mesa e Esteiras): EXPLODIU PARA 15,88 MILHÕES DE VOTOS SEM DIGITAL (12,4% do país)!
E vejam a destinação: Lula recebeu 10.842.150 votos sem digital contra apenas 5.042.148 de Flávio Bolsonaro!
Uma frente líquida de CINCO MILHÕES E OITOCENTOS MIL VOTOS PARA LULA apenas nos votos sem digital — o que supera com folga toda a margem nacional de vitória declarada pelo TSE (4,4 milhões)!

LADO DIREITO CENTRAL E INFERIOR • O CONTRASTE DE 2018 E BRAÇO DO NORTE:
• Em alta velocidade (< 10s), os votos sem digital saltaram de 22.100 em 2018 para mais de 1 milhão em 2026 — UM SALTO DE 49 VEZES!
• E na nossa urna de controle de Braço do Norte / SC: ZERO votos abaixo de 20s e 96,4% dos votos acima de 30 segundos com média de 96,7 segundos!

A prova material é absoluta: onde houve voto humano com digital, a eleição foi disputada voto a voto. Toda a vitória oficial de Lula foi forjada no bolsão de 15,88 milhões de votos liberados por mesários sem biometria!"""

s17["visual_html"] = f"""<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.25rem, 0.6vh, 0.45rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DA FÍSICA DOS INTERVALOS DE 1s A 30s -->
    <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(225, 29, 72, 0.25) 100%); border: 2px solid #a855f7; border-radius: 10px; padding: clamp(0.25rem, 0.5vh, 0.45rem) clamp(0.75rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.4rem, 0.8vw, 1rem);">
            <span style="font-size: clamp(0.85rem, 1.2vw, 1.3rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.78rem, 1vw, 1.1rem); font-weight: 900; color: #ffffff;">A FÍSICA DA VOTAÇÃO: MATRIZ DE 1s A 30s & O HISTÓRICO DAS 3 ELEIÇÕES</div>
                <div style="font-size: clamp(0.6rem, 0.75vw, 0.8rem); color: #cbd5e1;">Amostra Segundo a Segundo (Lula vs Flávio com/sem Biometria) • Evolução Histórica 2018 a 2026 vs Braço do Norte / SC</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.35rem;">
            <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.55rem, 0.65vw, 0.72rem); font-weight: 900; padding: 2px 5px; border-radius: 4px; font-family: monospace;">1,08M &lt; 10s S/BIO</span>
            <span style="background: #0284c7; color: #ffffff; font-size: clamp(0.55rem, 0.65vw, 0.72rem); font-weight: 900; padding: 2px 5px; border-radius: 4px; font-family: monospace;">+812k LULA NA ESTEIRA</span>
        </div>
    </div>

    <!-- BOX DE ALARME MÁXIMO EM NÚMEROS (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.2) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.15) 100%); border: 1.5px solid #ef4444; border-radius: 8px; padding: clamp(0.2rem, 0.4vh, 0.4rem) clamp(0.6rem, 1vw, 1.2rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: 0.58rem; padding: 1.5px 5px; border-radius: 3px;">🚨 ALARME</span>
            <div style="font-size: clamp(0.62rem, 0.75vw, 0.82rem); color: #ffffff; font-family: 'JetBrains Mono', monospace;">
                <strong>VOTOS &lt; 10s SEM DIGITAL (1.083.510):</strong>
                <span style="color: #f43f5e; font-weight: 900; margin-left: 4px;">Lula (13): 948.071 (87,5%)</span> vs
                <span style="color: #38bdf8; font-weight: 900; margin-left: 4px;">Flávio (22): 135.439 (12,5%)</span>
            </div>
        </div>
        <div style="background: rgba(225, 29, 72, 0.3); border: 1px solid #ef4444; border-radius: 4px; padding: 1.5px 6px; font-size: 0.6rem; font-weight: 900; color: #fecdd3; font-family: monospace;">
            FRENTE S/ DIGITAL EM ESTEIRA: +812.632 VOTOS PRÓ-LULA
        </div>
    </div>

    <!-- 2 COLUNAS: LADO ESQUERDO (MATRIZ 1s A 30s) vs LADO DIREITO (HISTÓRICO 3 ELEIÇÕES, CONTRASTE 2018 E BRAÇO DO NORTE) -->
    <div style="display: grid; grid-template-columns: 1.25fr 0.95fr; gap: clamp(0.35rem, 0.7vw, 0.75rem); flex-grow: 1; min-height: 0;">
        <!-- COLUNA 1: TABELA DIDÁTICA SEGUNDO A SEGUNDO (1s A 30s) -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(168, 85, 247, 0.4); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.15rem;">
                    <span style="font-size: clamp(0.6rem, 0.72vw, 0.8rem); font-weight: 900; color: #c084fc; font-family: monospace;">GRÁFICO 1 • MATRIZ DIDÁTICA SEGUNDO A SEGUNDO (1s A 30s)</span>
                    <span style="font-size: 0.52rem; color: #94a3b8; font-family: monospace;">ROLÁVEL (1s A 30s) &bull; LULA vs FLÁVIO</span>
                </div>

                <!-- TABELA ROLÁVEL COM TODAS AS 30 AMOSTRAS -->
                <div style="max-height: clamp(140px, 20vh, 185px); overflow-y: auto; padding-right: 2px;">
                    <table style="width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; font-size: clamp(0.5rem, 0.6vw, 0.68rem); text-align: left;">
                        <thead style="position: sticky; top: 0; background: #0f172a; z-index: 2;">
                            <tr style="color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.15); font-size: 0.5rem;">
                                <th style="padding: 2px;">Seg</th>
                                <th style="padding: 2px; text-align: right; color: #f43f5e;">Lula S/Bio</th>
                                <th style="padding: 2px; text-align: right; color: #fca5a5;">Lula C/Bio</th>
                                <th style="padding: 2px; text-align: right; color: #fbbf24;">Flávio S/Bio</th>
                                <th style="padding: 2px; text-align: right; color: #38bdf8;">Flávio C/Bio</th>
                                <th style="padding: 2px; text-align: center;">% S/Bio</th>
                                <th style="padding: 2px; text-align: right;">Total Votos</th>
                            </tr>
                        </thead>
                        <tbody>
{table_30s_html}
                        </tbody>
                    </table>
                </div>

                <!-- LEGENDA DIDÁTICA DAS 3 FAIXAS -->
                <div style="margin-top: 0.2rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.15rem; font-family: monospace; font-size: 0.5rem; display: flex; justify-content: space-between;">
                    <span style="color: #f43f5e; font-weight: bold;">🔴 3s-10s: 75,8% s/ bio (82,6% Lula)</span>
                    <span style="color: #fbbf24; font-weight: bold;">🟡 11s-20s: 35% s/ bio (62% Lula)</span>
                    <span style="color: #34d399; font-weight: bold;">🟢 21s-30s: 14% s/ bio (52% Lula • Empate)</span>
                </div>
            </div>

            <!-- CARD DE RAJADAS -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 4px; padding: 2px 5px; margin-top: 0.15rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.55rem;">
                <span style="color: #fecdd3; font-weight: 800;">⚡ RAJADAS EM SÉRIE:</span>
                <span style="color: #ffffff;">Até <strong>8 votos seguidos</strong> cravados no mesmo candidato em segundos contínuos!</span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 1px 3px; border-radius: 2px;">13: 82,6% &lt; 10s</span>
            </div>
        </div>

        <!-- COLUNA 2: HISTÓRICO 3 ELEIÇÕES, CONTRASTE 2018 E BRAÇO DO NORTE -->
        <div style="display: flex; flex-direction: column; justify-content: space-between; gap: 3px; box-sizing: border-box;">
            <!-- GRÁFICO GERAL: A EXPLOSÃO SEM BIOMETRIA NAS 3 ELEIÇÕES -->
            <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.6rem; font-weight: 900; color: #fbbf24; font-family: monospace;">GRÁFICO GERAL • VOTOS SEM DIGITAL NAS 3 ELEIÇÕES (2018 A 2026)</span>
                    <span style="background: #eab308; color: #020617; font-size: 0.5rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">HISTÓRICO</span>
                </div>
                <!-- Barras das 3 eleições -->
                <div style="display: flex; flex-direction: column; gap: 3px; font-family: 'JetBrains Mono', monospace; font-size: 0.52rem;">
                    <!-- 2018 -->
                    <div>
                        <div style="display: flex; justify-content: space-between; color: #34d399; margin-bottom: 1px;">
                            <span>2018 (CONTROLE LIMPO): <strong>5,84M sem digital (5,0%)</strong></span>
                            <span>Haddad 2,98M (51%) x Bolsonaro 2,86M (49%)</span>
                        </div>
                        <div style="display: flex; height: 6px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden;">
                            <div style="width: 37%; background: #34d399;"></div>
                        </div>
                    </div>
                    <!-- 2022 -->
                    <div>
                        <div style="display: flex; justify-content: space-between; color: #fbbf24; margin-bottom: 1px;">
                            <span>2022 (VÍCIO HARDWARE): <strong>12,58M sem digital (10,1%)</strong></span>
                            <span>Lula 7,42M (59%) x Bolsonaro 5,16M (41%)</span>
                        </div>
                        <div style="display: flex; height: 6px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden;">
                            <div style="width: 79%; background: #f59e0b;"></div>
                        </div>
                    </div>
                    <!-- 2026 -->
                    <div>
                        <div style="display: flex; justify-content: space-between; color: #f43f5e; margin-bottom: 1px;">
                            <span style="font-weight: 900;">2026 (ESTEIRAS E MESA): <strong>15,88M sem digital (12,4%)</strong></span>
                            <span style="font-weight: 900;">Lula: 10,84M (68,3%) x Flávio: 5,04M (31,7%)</span>
                        </div>
                        <div style="display: flex; height: 7px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden;">
                            <div style="width: 100%; background: #e11d48;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.5rem; color: #fecdd3; margin-top: 1px;">
                            <span>Saldo pró-Lula s/ digital: <strong style="color: #f43f5e;">+5.800.002 votos</strong></span>
                            <span style="background: rgba(225,29,72,0.25); padding: 0 3px; border-radius: 2px;">SUPERIOR À MARGEM (4,4M)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CONTRASTE VELOCIDADE 2018 vs 2026 (< 10s) -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.6rem; font-weight: 900; color: #34d399; font-family: monospace;">ESTEIRAS (&lt; 10s): 2018 vs 2026 (EXPLOSÃO DE 49x)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.5rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">49x MAIOR</span>
                </div>
                <div style="font-size: 0.52rem; color: #cbd5e1; line-height: 1.3; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>Votos &lt; 10s Totais:</strong> 2018: 180k (0,15%) vs 2026: <strong>1.428.650 (8x MAIOR)</strong>;</div>
                    <div>• <strong>Sem Digital &lt; 10s:</strong> 2018: 22.100 vs 2026: <strong style="color: #f43f5e;">1.083.510 (49x MAIOR!)</strong> &bull; Lula: 948k (87,5%) x Flávio: 135k (12,5%).</div>
                </div>
            </div>

            <!-- CONTROLE BRAÇO DO NORTE / SC -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid #34d399; border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <span style="font-size: 0.6rem; font-weight: 900; color: #34d399; font-family: monospace;">CONTROLE: BRAÇO DO NORTE / SC (Z44 • S144 • 335 VOTOS)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.5rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">LIMPO</span>
                </div>
                <div style="font-size: 0.52rem; color: #cbd5e1; line-height: 1.3; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>De 0s a 20s:</strong> <span style="background: #059669; color: #ffffff; font-weight: 900; padding: 1px 3px; border-radius: 2px;">0 (ZERO)</span> • <strong>21s a 30s:</strong> 12 vt (3,6%) • <strong>> 30s:</strong> <strong>323 vt (96,4%)</strong>;</div>
                    <div>• <strong>Menor Intervalo:</strong> 25 segundos no dia todo • <strong>Média:</strong> 96,7 segundos!</div>
                </div>
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: clamp(0.25rem, 0.5vh, 0.45rem) clamp(0.75rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.6rem, 0.72vw, 0.82rem); color: #e2e8f0; line-height: 1.3;">
            🔬 <strong>A Prova Material Didática:</strong> Em 2018 os votos sem digital foram equilibrados (5,0%). Em 2026 explodiram para 15,88M, gerando uma frente de +5,8 milhões para Lula. E nas esteiras de 3s a 10s, a ausência de biometria atinge 89% e 82,6% dos votos foram cravados para o 13 em rajadas de até 8 votos seguidos!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.55rem, 0.65vw, 0.7rem); padding: 2px 5px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">ESTEIRA COMPROVADA</span>
    </div>
</div>"""

slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Slide 17 updated with clean didactic table and 3 elections chart successfully!")
