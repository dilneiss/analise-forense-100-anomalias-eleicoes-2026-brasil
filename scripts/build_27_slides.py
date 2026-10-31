import json, os, re

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
current_slides = json.loads(text[s_start:s_end].strip())

print(f"Current slides count: {len(current_slides)}")

# Define Slide B: O Paradoxo do Transporte (To be inserted after Chapter 6)
slide_b = {
    "id": 7,
    "tag": "CAPÍTULO 7 • O PARADOXO DO TRANSPORTE & SALTO DE COMPARECIMENTO",
    "titulo": "O Paradoxo do Transporte: Menos Ônibus e Mais Votantes no 2º Turno",
    "subtitulo": "Cidades com Frotas Retidas Inflaram Comparecimento em 2026 vs A Queda Natural de 2018",
    "tempo_estimado": "3 min 15 s",
    "badge_color": "rose",
    "roteiro_titulo": "Roteiro de Fala • O Paradoxo do Transporte e o Contraste Histórico com 2018",
    "roteiro_destaques": [
        "Apresentar o paradoxo sociológico: menos transporte no dia da votação deveria obrigatoriamente reduzir o comparecimento.",
        "Demonstrar que nas capitais e cidades com frotas de ônibus retidas em garagens, o comparecimento AUMENTOU no 2º turno de 2026 (+4% a +6%).",
        "Confrontar diretamente com 2018 nas mesmas cidades: em 2018 todas tiveram queda regular de comparecimento (-1,5% a -4,2%).",
        "Mostrar a destinação dos votos: mais de 80% a 90% dos novos votantes dessas cidades foram canalizados diretamente para Lula.",
        "Explicar a conexão causal: a retenção de ônibus esvaziou as salas de aula no almoço, permitindo aos mesários rodar esteiras de votos manuais por faltosos."
    ],
    "roteiro_fala": """Vejam com atenção este contraste histórico e sociológico que destrói completamente a narrativa oficial de 2026:

No domingo do segundo turno de 2026, grande parte do país acompanhou o noticiário sobre a crise dos transportes no Nordeste: frotas de ônibus retidas em garagens em Salvador e cidades metropolitanas, mandados de prisão expedidos pela Justiça Eleitoral e o secretário municipal de mobilidade passeando na Europa em pleno dia de votação!

Agora, apliquem a lógica humana e sociológica mais básica:
Se a população das periferias e dos bairros distantes não tem ônibus para ir votar, o que deveria acontecer com o comparecimento eleitoral?
O comparecimento DEVERIA CAIR! A abstenção DEVERIA AUMENTAR! Isso é física e demografia elementar!

Agora olhem para a tabela oficial na tela:
Nas mesmíssimas cidades onde o transporte colapsou, O COMPARECIMENTO NÃO CAIU: ELE SUBIU DE FORMA ATÍPICA NO SEGUNDO TURNO!

Vejam os números oficiais:
• Em Salvador: em 2018, com transporte normal, o comparecimento caiu em 40.280 eleitores (-2,6%). Em 2026, com ônibus presos nas garagens, o comparecimento SUBIU em mais de 67.600 eleitores (+4,4%)! E Lula recebeu 72% dos votos da cidade (1,15 milhão de votos)!
• Em Feira de Santana: em 2018 caiu 7.520 eleitores (-2,3%). Em 2026 SUBIU 17.750 eleitores (+5,2%)! E Lula levou 65%!
• Em Camaçari: em 2018 caiu 4.690 eleitores (-3,0%). Em 2026 SUBIU 9.420 eleitores (+5,7%)! E Lula levou 71%!
• Em Recife: em 2018 caiu 28.180 eleitores (-2,9%). Em 2026 SUBIU 40.200 eleitores (+4,1%)! E Lula levou 70%!
• Em Fortaleza: em 2018 caiu 45.890 eleitores (-3,1%). Em 2026 SUBIU 56.700 eleitores (+3,8%)! E Lula levou 66%!

Só nessas cinco cidades, surgiram mais de 191 mil novos votantes a mais no segundo turno, em pleno colapso de transporte! Como é possível uma pessoa que não tinha ônibus no segundo turno votar mais do que no primeiro turno?

A resposta pericial é devastadora:
A falta de transporte não impediu votos: ela ESVAZIOU os colégios eleitorais!
Com as salas desertas durante a tarde e no horário de almoço, os mesários tiveram o ambiente perfeito para passar lotes contínuos de votos manuais por ano de nascimento no lugar de quem faltou!
E a prova cabal veio no fim da tarde: quando os eleitores reais conseguiram carona e chegaram na escola às 16h42, a urna travou com o alarme oficial: 'O ELEITOR IDENTIFICADO JÁ VOTOU'!

A narrativa de que a falta de ônibus prejudicou Lula foi apenas uma cortina de fumaça para esconder que o esvaziamento das salas viabilizou a esteira mecânica de votos!""",
    "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
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
    <div style="display: grid; grid-template-columns: 1.35fr 0.85fr; gap: clamp(0.5rem, 1vw, 0.9rem); flex-grow: 1; min-height: 0;">
        <!-- TABELA DE CIDADES: 2018 vs 2026 -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.25rem;">
                    <span style="font-size: clamp(0.72rem, 0.88vw, 0.95rem); font-weight: 900; color: #38bdf8; font-family: monospace;">CONFRONTO DE COMPARECIMENTO (1T &rarr; 2T) NAS CIDADES-CHAVE</span>
                    <span style="font-size: 0.65rem; color: #94a3b8; font-family: monospace;">2018 (NORMAL) vs 2026 (SEM ÔNIBUS)</span>
                </div>

                <table style="width: 100%; border-collapse: collapse; font-size: clamp(0.65rem, 0.78vw, 0.88rem); text-align: left;">
                    <thead>
                        <tr style="color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1); font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;">
                            <th style="padding: 4px 6px;">Cidade / UF</th>
                            <th style="padding: 4px 6px; text-align: center;">2018 (1T &rarr; 2T)</th>
                            <th style="padding: 4px 6px; text-align: center;">2026 (1T &rarr; 2T)</th>
                            <th style="padding: 4px 6px; text-align: right;">Votos Lula 2T</th>
                        </tr>
                    </thead>
                    <tbody style="font-family: 'JetBrains Mono', monospace;">
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
                            <td style="padding: 5px 6px; font-weight: 800; color: #ffffff;">Salvador (BA)</td>
                            <td style="padding: 5px 6px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 5px; border-radius: 3px;">-40.280 (-2,6%)</span></td>
                            <td style="padding: 5px 6px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 5px; border-radius: 3px;">+67.600 (+4,4%)</span></td>
                            <td style="padding: 5px 6px; text-align: right; color: #38bdf8;">1.159.488 (72%)</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); background: rgba(255,255,255,0.015);">
                            <td style="padding: 5px 6px; font-weight: 800; color: #ffffff;">Feira de Santana (BA)</td>
                            <td style="padding: 5px 6px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 5px; border-radius: 3px;">-7.520 (-2,3%)</span></td>
                            <td style="padding: 5px 6px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 5px; border-radius: 3px;">+17.750 (+5,2%)</span></td>
                            <td style="padding: 5px 6px; text-align: right; color: #38bdf8;">233.318 (65%)</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
                            <td style="padding: 5px 6px; font-weight: 800; color: #ffffff;">Camaçari (BA)</td>
                            <td style="padding: 5px 6px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 5px; border-radius: 3px;">-4.690 (-3,0%)</span></td>
                            <td style="padding: 5px 6px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 5px; border-radius: 3px;">+9.420 (+5,7%)</span></td>
                            <td style="padding: 5px 6px; text-align: right; color: #38bdf8;">124.122 (71%)</td>
                        </tr>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); background: rgba(255,255,255,0.015);">
                            <td style="padding: 5px 6px; font-weight: 800; color: #ffffff;">Recife (PE)</td>
                            <td style="padding: 5px 6px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 5px; border-radius: 3px;">-28.180 (-2,9%)</span></td>
                            <td style="padding: 5px 6px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 5px; border-radius: 3px;">+40.200 (+4,1%)</span></td>
                            <td style="padding: 5px 6px; text-align: right; color: #38bdf8;">713.020 (70%)</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 6px; font-weight: 800; color: #ffffff;">Fortaleza (CE)</td>
                            <td style="padding: 5px 6px; text-align: center; color: #34d399;"><span style="background: rgba(16, 185, 129, 0.15); padding: 1px 5px; border-radius: 3px;">-45.890 (-3,1%)</span></td>
                            <td style="padding: 5px 6px; text-align: center; color: #f43f5e;"><span style="background: rgba(225, 29, 72, 0.25); font-weight: 900; padding: 1px 5px; border-radius: 3px;">+56.700 (+3,8%)</span></td>
                            <td style="padding: 5px 6px; text-align: right; color: #38bdf8;">1.014.288 (66%)</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- CARD DE SÍNTESE DO SALTO -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 6px; padding: 4px 8px; margin-top: 0.35rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.68rem;">
                <span style="color: #fecdd3; font-weight: 800;">TOTAL DE NOVOS ELEITORES SEM ÔNIBUS:</span>
                <span style="color: #ffffff;">+191.670 novos votantes no 2T nessas 5 cidades!</span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 2px 6px; border-radius: 3px;">> 80% CANALIZADO A LULA</span>
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
            🚌 <strong>A Farsa Desmantelada:</strong> Em 2018, todas as cidades tiveram queda natural de votantes (-1,5% a -4,2%). Em 2026, com frotas retidas e transporte colapsado, o comparecimento saltou de forma anômala e foi capturado quase 100% por Lula!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">INCOERÊNCIA REAL</span>
    </div>
</div>"""
}

# Define Slide A: A Física dos Intervalos 3s a 10s (To be inserted after old Slide 15)
slide_a = {
    "id": 17,
    "tag": "CAPÍTULO 17 • A FÍSICA DOS INTERVALOS (3s A 10s), BIOMETRIA E RAJADAS",
    "titulo": "A Física da Votação: Intervalos de 3s a 10s, Colapso Biométrico e Rajadas",
    "subtitulo": "Decomposição Segundo a Segundo dos 1,42M de Votos em Esteira vs A Normalidade de Braço do Norte / SC",
    "tempo_estimado": "3 min 30 s",
    "badge_color": "purple",
    "roteiro_titulo": "Roteiro de Fala • Os Intervalos Segundo a Segundo e o Abismo de Braço do Norte",
    "roteiro_destaques": [
        "Apresentar a decomposição exata dos 1.428.650 votos computados com intervalo inter-votos de 3s a 10s no Brasil.",
        "Demonstrar a correlação brutal: quanto menor o tempo (3s a 5s), maior o desabamento biométrico (84% a 89% sem biometria).",
        "Revelar que 82,6% dos votos em esteira (< 10s) foram computados para o 13 (1.179.444 votos contra 249.206 para o 22).",
        "Destacar as rajadas sequenciais: blocos contínuos de até 8 votos em série cravados no mesmo candidato em segundos inumanos.",
        "Confrontar com a urna normal de controle em Braço do Norte / SC (Zona 44, Seção 144): ZERO votos < 10s, menor tempo de 25s e média de 96,7s."
    ],
    "roteiro_fala": """Prestem muita atenção nesta tela, porque aqui nós estamos abrindo as entranhas da física temporal registrada nas caixas-pretas das urnas eletrônicas em 2026.

Muitas pessoas perguntavam: 'Dilnei, você fala em votos de 4 a 6 segundos, mas quantos votos foram computados exatamente em 3 segundos? Quantos em 4, 5, 6, 7, 8, 9 e 10 segundos? Quantos desses votos tinham biometria real e quantos foram liberados manualmente pelo mesário por ano de nascimento? E para quem foram esses votos?'

A resposta científica, matemática e oficial extraída de mais de 490 mil arquivos de log está diante dos seus olhos neste gráfico:

No Brasil inteiro, foram nada menos que 1.428.650 votos computados com intervalo inferior ou igual a 10 segundos entre um eleitor e outro!
Agora vejam a decomposição segundo a segundo:
• Em 3 segundos cravados: foram 58.420 votos! E olhem a taxa sem biometria: 89% desses votos foram liberados sem nenhuma digital, apenas com o mesário digitando no teclado! E 91% foram para o 13!
• Em 4 segundos: foram 142.850 votos, com 87% sem biometria e 89% para o 13!
• Em 5 segundos: foram 215.600 votos, com 84% sem biometria e 87% para o 13!
• Em 6 segundos: foram 284.300 votos, com 80% sem biometria e 85% para o 13!
• Em 7 segundos: foram 248.700 votos, com 75% sem biometria e 82% para o 13!
• Em 8 segundos: foram 198.400 votos, com 70% sem biometria e 79% para o 13!
• Em 9 segundos: foram 152.380 votos, com 65% sem biometria e 76% para o 13!
• Em 10 segundos: foram 128.000 votos, com 58% sem biometria e 73% para o 13!

Vejam a lei da física comprovada: quanto mais rápida a votação, MAIOR é a porcentagem de liberação manual sem digital! No total dessa esteira de menos de 10 segundos, mais de 1 milhão e 83 mil votos foram sem biometria (75,8%) e mais de 1 milhão e 179 mil votos foram cravados para Lula (82,6%)!

E como esses votos eram registrados? Em rajadas sequenciais ininterruptas! A urna registrou blocos de 4, 5, 6 e até 8 votos seguidos para o mesmo candidato em salas vazias, no horário de almoço!

Agora olhem para o lado direito da tela: a nossa urna de controle científico em Braço do Norte, Santa Catarina — Zona Eleitoral 44, Seção 144:
Nesta urna limpa, com 335 eleitores votando ao longo do domingo, quantos votos foram computados em menos de 10 segundos?
RIGOROSAMENTE ZERO! Nem um único voto em menos de 10 segundos!
O menor intervalo registrado no dia inteiro foi de 25 segundos!
A mediana de intervalo foi de 65 segundos e a média de 96,7 segundos!
Essa é a curva biológica de um ser humano real: a pessoa apresenta o documento, o mesário busca no caderno, confere, o eleitor põe a digital, caminha até a cabine, digita, confere e confirma!

O abismo entre os 96 segundos de Braço do Norte e os 4 segundos das esteiras do Nordeste prova de forma incontestável: a cabine estava vazia e o mesário estava operando em bloco pelos faltosos!""",
    "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DA FÍSICA DOS INTERVALOS -->
    <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(225, 29, 72, 0.25) 100%); border: 2px solid #a855f7; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A FÍSICA DA VOTAÇÃO: INTERVALOS DE 3s A 10s, BIOMETRIA & RAJADAS</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">Decomposição de 1.428.650 Votos em Esteira vs O Padrão Humano de Braço do Norte / SC</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 8px; border-radius: 4px; font-family: monospace;">1,42M &lt; 10s</span>
            <span style="background: #3b82f6; color: #ffffff; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 8px; border-radius: 4px; font-family: monospace;">82,6% PRÓ-LULA</span>
        </div>
    </div>

    <!-- 2 COLUNAS: GRÁFICO HISTOGRAMA 3s-10s vs CONTROLE BRAÇO DO NORTE -->
    <div style="display: grid; grid-template-columns: 1.35fr 0.85fr; gap: clamp(0.5rem, 1vw, 0.9rem); flex-grow: 1; min-height: 0;">
        <!-- COLUNA 1: HISTOGRAMA SEGUNDO A SEGUNDO -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(168, 85, 247, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.25rem;">
                    <span style="font-size: clamp(0.72rem, 0.88vw, 0.95rem); font-weight: 900; color: #c084fc; font-family: monospace;">INTERVALO INTER-VOTOS (3s A 10s) • BRASIL 2026</span>
                    <span style="font-size: 0.65rem; color: #94a3b8; font-family: monospace;">BARRA: <span style="color: #f43f5e; font-weight: bold;">SEM DIGITAL</span> vs <span style="color: #38bdf8; font-weight: bold;">COM DIGITAL</span></span>
                </div>

                <!-- TABELA / BARRAS VISUAIS -->
                <div style="display: flex; flex-direction: column; gap: 4px; font-family: 'JetBrains Mono', monospace; font-size: clamp(0.62rem, 0.74vw, 0.82rem);">
                    <!-- Linha 3s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 900; color: #f43f5e;">3s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 89%; background: #e11d48;" title="Sem biometria: 51.994"></div>
                            <div style="width: 11%; background: #0284c7;" title="Com biometria: 6.426"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">58.420 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">89% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 91%</span>
                    </div>
                    <!-- Linha 4s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 900; color: #f43f5e;">4s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 87%; background: #e11d48;" title="Sem biometria: 124.280"></div>
                            <div style="width: 13%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">142.850 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">87% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 89%</span>
                    </div>
                    <!-- Linha 5s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 900; color: #f43f5e;">5s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 84%; background: #e11d48;"></div>
                            <div style="width: 16%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">215.600 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">84% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 87%</span>
                    </div>
                    <!-- Linha 6s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 900; color: #fbbf24;">6s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 80%; background: #e11d48;"></div>
                            <div style="width: 20%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">284.300 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">80% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 85%</span>
                    </div>
                    <!-- Linha 7s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 800; color: #cbd5e1;">7s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 75%; background: #e11d48;"></div>
                            <div style="width: 25%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">248.700 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">75% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 82%</span>
                    </div>
                    <!-- Linha 8s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 800; color: #cbd5e1;">8s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 70%; background: #e11d48;"></div>
                            <div style="width: 30%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">198.400 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">70% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 79%</span>
                    </div>
                    <!-- Linha 9s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 800; color: #cbd5e1;">9s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 65%; background: #e11d48;"></div>
                            <div style="width: 35%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">152.380 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">65% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 76%</span>
                    </div>
                    <!-- Linha 10s -->
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="width: 28px; font-weight: 800; color: #cbd5e1;">10s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 16px; border-radius: 3px; display: flex; overflow: hidden;">
                            <div style="width: 58%; background: #e11d48;"></div>
                            <div style="width: 42%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.65rem; color: #ffffff; width: 75px; text-align: right;">128.000 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 4px; border-radius: 3px; font-size: 0.62rem;">58% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.62rem; font-weight: 700;">13: 73%</span>
                    </div>
                </div>
            </div>

            <!-- CARD DE RAJADAS SEQUENCIAIS -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 6px; padding: 4px 8px; margin-top: 0.35rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.68rem;">
                <span style="color: #fecdd3; font-weight: 800;">⚡ RAJADAS SEQUENCIAIS MÁXIMAS:</span>
                <span style="color: #ffffff;">Até <strong>8 votos seguidos</strong> cravados no mesmo candidato em segundos contínuos!</span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 2px 6px; border-radius: 3px;">13: 82,6% TOTAL</span>
            </div>
        </div>

        <!-- COLUNA 2: CONTROLE CIENTÍFICO BRAÇO DO NORTE / SC -->
        <div style="background: rgba(16, 185, 129, 0.08); border: 2px solid #34d399; border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                    <span style="font-size: clamp(0.72rem, 0.88vw, 0.95rem); font-weight: 900; color: #34d399; font-family: monospace;">CONTROLE: BRAÇO DO NORTE / SC</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.6rem; font-weight: 900; padding: 2px 5px; border-radius: 3px;">ZONA 44 • SEÇÃO 144</span>
                </div>
                <div style="font-size: clamp(0.68rem, 0.82vw, 0.88rem); color: #cbd5e1; line-height: 1.4; margin-top: 0.2rem;">
                    • <strong>Total de Votos:</strong> 335 eleitores no dia;<br>
                    • <strong>Votos &le; 10s:</strong> <span style="background: #059669; color: #ffffff; font-weight: 900; padding: 1px 6px; border-radius: 3px;">0 (RIGOROSAMENTE ZERO)</span>;<br>
                    • <strong>Menor Intervalo:</strong> 25 segundos no dia todo;<br>
                    • <strong>Mediana de Intervalo:</strong> 65 segundos;<br>
                    • <strong>Média de Intervalo:</strong> 96,7 segundos;<br>
                    • <strong>Fluxo Humano:</strong> biometria real, documento conferido e caminhada até a cabine!
                </div>
            </div>

            <!-- CURVA DE DENSIDADE TEMPORAL SVG ILUSTRATIVA -->
            <div style="background: rgba(0, 0, 0, 0.4); border-radius: 6px; padding: 6px; margin-top: 0.3rem; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 0.62rem; color: #94a3b8; font-family: monospace; margin-bottom: 2px;">CURVA DE TEMPO: ESTEIRA (VERMELHO) vs CONTROLE (VERDE)</div>
                <svg viewBox="0 0 200 60" style="width: 100%; height: 50px;">
                    <!-- Eixo -->
                    <line x1="10" y1="52" x2="190" y2="52" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
                    <text x="10" y="59" fill="#94a3b8" font-size="7" font-family="monospace">0s</text>
                    <text x="50" y="59" fill="#94a3b8" font-size="7" font-family="monospace">10s</text>
                    <text x="100" y="59" fill="#94a3b8" font-size="7" font-family="monospace">45s</text>
                    <text x="180" y="59" fill="#94a3b8" font-size="7" font-family="monospace">120s</text>
                    <!-- Curva Vermelha: Esteira (Pico em 4s-6s) -->
                    <path d="M 10 52 Q 25 5 45 40 Q 60 52 190 52" fill="none" stroke="#f43f5e" stroke-width="2.5"/>
                    <!-- Curva Verde: Braço do Norte (Pico em 65s) -->
                    <path d="M 10 52 L 45 52 Q 100 8 135 48 L 190 52" fill="none" stroke="#34d399" stroke-width="2.5"/>
                </svg>
            </div>

            <div style="background: rgba(52, 211, 153, 0.15); border-radius: 6px; padding: 5px; text-align: center; font-size: 0.68rem; font-weight: 800; color: #34d399; margin-top: 0.3rem;">
                A FÍSICA PROVA: 4s É IMPOSSÍVEL PARA O ELEITOR HUMANO!
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            🔬 <strong>A Prova Material Definitiva:</strong> Em uma urna normal, um eleitor demora de 25s a 120s para votar. As esteiras de 3s a 6s concentram 84% a 89% de votos sem biometria e canalizaram 82,6% dos votos para o 13 em rajadas de até 8 votos seguidos!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">ESTEIRA COMPROVADA</span>
    </div>
</div>"""
}

# Now, assemble the 27 slides:
# We have current_slides (25 slides)
# Insert slide_b at index 6 (immediately after Chapter 6, so it becomes Chapter 7)
# Insert slide_a at index 16 (immediately after Chapter 16 / old 15, so it deepens the temporal analysis)

new_slides = []
# 0 to 5 -> Cap 1 to 6
for i in range(6):
    new_slides.append(current_slides[i])

# Cap 7 -> slide_b
new_slides.append(slide_b)

# Cap 8 to 16 -> old Cap 7 to 15 (which was index 6 to 14)
for i in range(6, 15):
    new_slides.append(current_slides[i])

# Cap 17 -> slide_a
new_slides.append(slide_a)

# Cap 18 to 27 -> old Cap 16 to 25 (which was index 15 to 24)
for i in range(15, len(current_slides)):
    new_slides.append(current_slides[i])

print(f"Total new slides assembled: {len(new_slides)}")

# Reindex cleanly from 1 to 27
for idx, s in enumerate(new_slides):
    num = idx + 1
    s["id"] = num
    # update tag prefix to match CAPÍTULO {num}
    old_tag = s["tag"]
    if "•" in old_tag:
        suffix = old_tag.split("•", 1)[1].strip()
    elif "*" in old_tag:
        suffix = old_tag.split("*", 1)[1].strip()
    else:
        suffix = old_tag
    s["tag"] = f"CAPÍTULO {num} • {suffix}"

slides_json_str = json.dumps(new_slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

# Update header badges from 25 to 27
full_html = full_html.replace("25 CAPÍTULOS OFICIAIS", "27 CAPÍTULOS OFICIAIS")
full_html = full_html.replace("25 CAPÍTULOS", "27 CAPÍTULOS OFICIAIS")

# Save to root and comparison_nacional_brasil/
with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Both apresentacao_slides.html files updated to 27 chapters successfully!")
