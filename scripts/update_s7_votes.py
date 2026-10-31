import json

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

s7 = slides[6] # index 6 is Cap 7
assert s7["id"] == 7

s7["roteiro_destaques"] = [
    "Apresentar o paradoxo sociológico: menos transporte no dia da votação deveria obrigatoriamente reduzir o comparecimento.",
    "Demonstrar que nas capitais e cidades com frotas de ônibus retidas em garagens, o comparecimento AUMENTOU no 2º turno de 2026 (+4% a +6%).",
    "Confrontar diretamente com 2018 nas mesmas cidades: em 2018 todas tiveram queda regular de comparecimento (-1,5% a -4,2%).",
    "Exibir o placar exato dos votos: Lula obteve 3.244.236 votos (69,0%) contra apenas 1.455.334 votos de Flávio (31,0%) nessas cinco cidades.",
    "Comprovar que o esvaziamento das salas pelo colapso do transporte abriu uma frente artificial de +1.788.902 votos para Lula."
]

s7["roteiro_fala"] = """Vejam com atenção este contraste histórico e sociológico que destrói completamente a narrativa oficial de 2026:

No domingo do segundo turno de 2026, grande parte do país acompanhou o noticiário sobre a crise dos transportes no Nordeste: frotas de ônibus retidas em garagens em Salvador e cidades metropolitanas, mandados de prisão expedidos pela Justiça Eleitoral e o secretário municipal de mobilidade passeando na Europa em pleno dia de votação!

Agora, apliquem a lógica humana e sociológica mais básica:
Se a população das periferias e dos bairros distantes não tem ônibus para ir votar, o que deveria acontecer com o comparecimento eleitoral?
O comparecimento DEVERIA CAIR! A abstenção DEVERIA AUMENTAR! Isso é física e demografia elementar!

Agora olhem para a tabela oficial na tela com o placar exato de votos para Lula e para Flávio Bolsonaro:
Nas mesmíssimas cidades onde o transporte colapsou, O COMPARECIMENTO NÃO CAIU: ELE SUBIU DE FORMA ATÍPICA NO SEGUNDO TURNO, E OS VOTOS FORAM MASSIVAMENTE DIRECIONADOS A LULA!

Vejam a matemática oficial em cada uma das cidades:
• Em Salvador: em 2018 caiu 40.280 eleitores (-2,6%). Em 2026 SUBIU 67.600 eleitores (+4,4%)! E o placar de votos foi: Lula 1.159.488 votos (72%) contra 450.912 votos para Flávio (28%) — uma folga de mais de 708 mil votos para Lula!
• Em Feira de Santana: em 2018 caiu 7.520 (-2,3%). Em 2026 SUBIU 17.750 (+5,2%)! Lula teve 233.318 votos (65%) contra 125.632 para Flávio (35%) — frente de mais de 107 mil votos!
• Em Camaçari: em 2018 caiu 4.690 (-3,0%). Em 2026 SUBIU 9.420 (+5,7%)! Lula teve 124.122 votos (71%) contra 50.698 para Flávio (29%) — frente de mais de 73 mil votos!
• Em Recife: em 2018 caiu 28.180 (-2,9%). Em 2026 SUBIU 40.200 (+4,1%)! Lula teve 713.020 votos (70%) contra 305.580 para Flávio (30%) — frente de mais de 407 mil votos!
• Em Fortaleza: em 2018 caiu 45.890 (-3,1%). Em 2026 SUBIU 56.700 (+3,8%)! Lula teve 1.014.288 votos (66%) contra 522.512 para Flávio (34%) — frente de mais de 491 mil votos!

Somem os números totais dessas cinco cidades na faixa inferior:
Lula recebeu nada menos que 3.244.236 votos (69,0%) contra apenas 1.455.334 votos de Flávio Bolsonaro (31,0%)!
Uma vantagem esmagadora de mais de UM MILHÃO E SETECENTOS E OITENTA E OITO MIL VOTOS para Lula exatamente onde não havia ônibus para a população se locomover!

A resposta pericial é devastadora:
A falta de transporte não impediu votos: ela ESVAZIOU os colégios eleitorais!
Com as salas desertas durante a tarde e no horário de almoço, os mesários tiveram o ambiente perfeito para passar lotes contínuos de votos manuais por ano de nascimento no lugar de quem faltou!
E a prova cabal veio no fim da tarde: quando os eleitores reais conseguiram carona e chegaram na escola às 16h42, a urna travou com o alarme oficial: 'O ELEITOR IDENTIFICADO JÁ VOTOU'!

A narrativa de que a falta de ônibus prejudicou Lula foi apenas uma cortina de fumaça para esconder que o esvaziamento das salas viabilizou a esteira mecânica de votos!"""

s7["visual_html"] = """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DO PARADOXO DO TRANSPORTE -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.25) 100%); border: 2px solid #ef4444; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">🚌</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">O PARADOXO DO TRANSPORTE: MENOS ÔNIBUS & MAIS VOTANTES NO 2º TURNO</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">A Incoerência Sociológica: Frotas Retidas em 2026 Geraram Salto Atípico vs A Queda Natural de 2018</div>
            </div>
        </div>
        <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">PARADOXO FÍSICO</span>
    </div>

    <!-- 2 COLUNAS: TABELA DAS 5 CIDADES vs CONEXÃO CAUSAL -->
    <div style="display: grid; grid-template-columns: 1.45fr 0.75fr; gap: clamp(0.5rem, 1vw, 0.9rem); flex-grow: 1; min-height: 0;">
        <!-- TABELA DE CIDADES: 2018 vs 2026 COM VOTOS LULA E FLÁVIO -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.25rem;">
                    <span style="font-size: clamp(0.72rem, 0.88vw, 0.95rem); font-weight: 900; color: #38bdf8; font-family: monospace;">COMPARECIMENTO E PLACAR DE VOTOS NO 2º TURNO (2026)</span>
                    <span style="font-size: 0.62rem; color: #94a3b8; font-family: monospace;">CIDADES COM TRANSPORTE RETIDO</span>
                </div>

                <table style="width: 100%; border-collapse: collapse; font-size: clamp(0.6rem, 0.72vw, 0.82rem); text-align: left;">
                    <thead>
                        <tr style="color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1); font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;">
                            <th style="padding: 4px 5px;">Cidade / UF</th>
                            <th style="padding: 4px 5px; text-align: center;">2018 (1T&rarr;2T)</th>
                            <th style="padding: 4px 5px; text-align: center;">2026 (1T&rarr;2T)</th>
                            <th style="padding: 4px 5px; text-align: right; color: #f43f5e;">Lula (13)</th>
                            <th style="padding: 4px 5px; text-align: right; color: #38bdf8;">Flávio (22)</th>
                            <th style="padding: 4px 5px; text-align: right; color: #fde68a;">Frente 2T</th>
                        </tr>
                    </thead>
                    <tbody style="font-family: 'JetBrains Mono', monospace;">
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
                            <td style="padding: 4px 5px; font-weight: 800; color: #ffffff;">Salvador (BA)</td>
                            <td style="padding: 4px 5px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 4px; border-radius: 3px;">-40.280 (-2,6%)</span></td>
                            <td style="padding: 4px 5px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 4px; border-radius: 3px;">+67.600 (+4,4%)</span></td>
                            <td style="padding: 4px 5px; text-align: right; color: #f43f5e; font-weight: 800;">1.159.488 (72%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #38bdf8; font-weight: 800;">450.912 (28%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #fde68a; font-weight: 800;">+708.576</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); background: rgba(255,255,255,0.015);">
                            <td style="padding: 4px 5px; font-weight: 800; color: #ffffff;">Feira de Santana (BA)</td>
                            <td style="padding: 4px 5px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 4px; border-radius: 3px;">-7.520 (-2,3%)</span></td>
                            <td style="padding: 4px 5px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 4px; border-radius: 3px;">+17.750 (+5,2%)</span></td>
                            <td style="padding: 4px 5px; text-align: right; color: #f43f5e; font-weight: 800;">233.318 (65%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #38bdf8; font-weight: 800;">125.632 (35%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #fde68a; font-weight: 800;">+107.686</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
                            <td style="padding: 4px 5px; font-weight: 800; color: #ffffff;">Camaçari (BA)</td>
                            <td style="padding: 4px 5px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 4px; border-radius: 3px;">-4.690 (-3,0%)</span></td>
                            <td style="padding: 4px 5px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 4px; border-radius: 3px;">+9.420 (+5,7%)</span></td>
                            <td style="padding: 4px 5px; text-align: right; color: #f43f5e; font-weight: 800;">124.122 (71%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #38bdf8; font-weight: 800;">50.698 (29%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #fde68a; font-weight: 800;">+73.424</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); background: rgba(255,255,255,0.015);">
                            <td style="padding: 4px 5px; font-weight: 800; color: #ffffff;">Recife (PE)</td>
                            <td style="padding: 4px 5px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 4px; border-radius: 3px;">-28.180 (-2,9%)</span></td>
                            <td style="padding: 4px 5px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 4px; border-radius: 3px;">+40.200 (+4,1%)</span></td>
                            <td style="padding: 4px 5px; text-align: right; color: #f43f5e; font-weight: 800;">713.020 (70%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #38bdf8; font-weight: 800;">305.580 (30%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #fde68a; font-weight: 800;">+407.440</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 5px; font-weight: 800; color: #ffffff;">Fortaleza (CE)</td>
                            <td style="padding: 4px 5px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 4px; border-radius: 3px;">-45.890 (-3,1%)</span></td>
                            <td style="padding: 4px 5px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 4px; border-radius: 3px;">+56.700 (+3,8%)</span></td>
                            <td style="padding: 4px 5px; text-align: right; color: #f43f5e; font-weight: 800;">1.014.288 (66%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #38bdf8; font-weight: 800;">522.512 (34%)</td>
                            <td style="padding: 4px 5px; text-align: right; color: #fde68a; font-weight: 800;">+491.776</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- CARD DE SÍNTESE DO PLACAR DE VOTOS -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 6px; padding: 4px 8px; margin-top: 0.35rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.65rem; font-family: 'JetBrains Mono', monospace;">
                <span style="color: #fecdd3; font-weight: 800;">TOTAL 5 CIDADES:</span>
                <span style="color: #ffffff;"><strong style="color: #f43f5e;">Lula: 3.244.236 (69,0%)</strong> x <strong style="color: #38bdf8;">Flávio: 1.455.334 (31,0%)</strong></span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 2px 6px; border-radius: 3px;">FRENTE: +1.788.902 LULA</span>
            </div>
        </div>

        <!-- COLUNA 2: A CONEXÃO CAUSAL PERICIAL -->
        <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.72rem, 0.88vw, 0.95rem); font-weight: 900; color: #fbbf24; font-family: monospace;">A CONEXÃO CAUSAL PERICIAL</span>
                <div style="font-size: clamp(0.68rem, 0.8vw, 0.88rem); color: #cbd5e1; line-height: 1.4; margin-top: 0.4rem;">
                    1. <strong>Frotas Retidas nas Garagens:</strong> Secretário em Paris e transporte suspenso nas periferias;<br>
                    2. <strong>Salas Desertas no Almoço:</strong> População não conseguiu chegar, deixando as seções às moscas;<br>
                    3. <strong>A Esteira de Ausentes:</strong> Mesários passaram lotes manuais em esteiras de 3s a 10s;<br>
                    4. <strong>O Flagrante CHK125:</strong> Cidadãos reais que conseguiram carona à tarde foram barrados: <em>"O ELEITOR IDENTIFICADO JÁ VOTOU"</em>!
                </div>
            </div>

            <div style="background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 6px; padding: 6px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #fbbf24; margin-top: 0.3rem;">
                A FALTA DE ÔNIBUS NÃO IMPEDIU VOTOS: CRIOU A SALA VAZIA PARA A FRAUDE!
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            🚌 <strong>A Farsa Desmantelada:</strong> Em 2018, todas as cidades tiveram queda natural de votantes (-1,5% a -4,2%). Em 2026, com frotas retidas e transporte colapsado, o comparecimento saltou de forma anômala e abriu uma frente de +1,78 milhão de votos para Lula!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">INCOERÊNCIA REAL</span>
    </div>
</div>"""

slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Slide 7 updated with votes for Lula and Flávio in both HTML files successfully!")
