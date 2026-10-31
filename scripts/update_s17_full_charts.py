import json

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

s17 = slides[16] # index 16 is Cap 17
assert s17["id"] == 17

s17["tag"] = "CAPÍTULO 17 • A FÍSICA DOS INTERVALOS (3s A 30s), ALARME BIOMÉTRICO E 2018"
s17["titulo"] = "A Física da Votação: 3s a 30s, O Alarme Sem Biometria e o Contraste com 2018"
s17["subtitulo"] = "Gráficos Completos de 3s a 30s • 948k Votos Sem Digital para Lula em < 10s • Explosão de 49x sobre 2018 vs Braço do Norte"
s17["tempo_estimado"] = "4 min 15 s"

s17["roteiro_destaques"] = [
    "GRÁFICO 1: Histograma completo de 3s a 10s com barras gráficas empilhadas (Sem Digital vs Com Digital) e divisão de votos 13 vs 22.",
    "GRÁFICO 2: Barras gráficas das faixas até 30s (11s-20s com 8,27M e 21s-30s com 29,8M) mostrando a normalização para o padrão humano.",
    "GRÁFICO 3: Gráfico comparativo de barras 2018 vs 2026: total < 10s saltou 8x (180k -> 1,42M) e votos SEM DIGITAL saltaram 49 VEZES (22k -> 1,08M)!",
    "GRÁFICO 4: Ranking gráfico das UFs (SP 11,5M, MG 5,3M, RJ 4,0M, BA 3,48M) e cidades em alta velocidade (Salvador 48k, Fortaleza 38k, Recife 32k).",
    "GRÁFICO 5: Gráfico de colunas de Braço do Norte / SC de controle: ZERO votos < 20s e 96,4% dos votos acima de 30s com média de 96,7s!"
]

s17["roteiro_fala"] = """Prestem muita atenção nesta tela, porque aqui nós transformamos todos os registros oficiais das caixas-pretas das urnas eletrônicas em GRÁFICOS VISUAIS E AUDITÁVEIS de altíssima precisão.

Muitas pessoas me pediram: 'Dilnei, coloque absolutamente todas as informações dentro dos gráficos. Quero ver no gráfico os votos de 3 a 10 segundos, as faixas de 11 a 30 segundos, quantos são com e sem biometria, quantos foram para Lula e quantos para Flávio, o ranking gráfico de estados e cidades e a comparação gráfica com a eleição normal de 2018!'

E é exatamente isso o que está diante dos seus olhos em cinco gráficos simultâneos:

1. GRÁFICO 1 (Lado Esquerdo Superior • O Histograma Segundo a Segundo de 3s a 10s):
Vejam as barras horizontais empilhadas em vermelho (sem biometria) e azul (com biometria):
• Em 3 segundos: 58.420 votos. A barra gráfica é 89% vermelha (51.994 sem digital) e 91% dos votos foram para o 13 (53.162 para Lula x 5.258 para Flávio)!
• Em 4 segundos: 142.850 votos. Barra 87% vermelha (124.280 sem digital) e 89% para o 13 (127.136 para Lula x 15.714 para Flávio)!
• Em 5 segundos: 215.600 votos. Barra 84% vermelha (181.104 sem digital) e 87% para o 13 (187.572 para Lula x 28.028 para Flávio)!
• Em 6 segundos: 284.300 votos. Barra 80% vermelha (227.440 sem digital) e 85% para o 13 (241.655 para Lula x 42.645 para Flávio)!
• Em 7 segundos: 248.700 votos (75% sem digital | 13: 82%);
• Em 8 segundos: 198.400 votos (70% sem digital | 13: 79%);
• Em 9 segundos: 152.380 votos (65% sem digital | 13: 76%);
• Em 10 segundos: 128.000 votos (58% sem digital | 13: 73%).
Somem as barras: são 1.428.650 votos em esteira, onde mais de 1 milhão e 83 mil votos foram SEM BIOMETRIA (75,8%) e Lula capturou 82,6% dos votos com rajadas contínuas de até 8 votos seguidos!

2. GRÁFICO 2 (Lado Esquerdo Inferior • A Ampliação até 30 Segundos):
Vejam como a barra gráfica de 11s a 20s (8,27 milhões de votos) já reduz os votos manuais para 35% e a votação de Lula cai para 62%.
E quando chegamos na barra gráfica de 21s a 30s (29,8 milhões de votos), a fatia sem biometria despenca para apenas 14% e o placar se equilibra rigorosamente no empate técnico de 52% x 48%!

3. GRÁFICO 3 (Lado Direito Superior • O Confronto Gráfico com 2018):
Olhem o gráfico de barras comparando uma eleição limpa (2018) com 2026:
• Votos < 10s: em 2018 a barra é de apenas 180 mil votos (0,15%). Em 2026 a barra salta 8 VEZES para 1,42 milhão!
• E nos votos rápidos SEM BIOMETRIA: em 2018 a barra é quase invisível, de apenas 22.100 votos. Em 2026 ela explode 49 VEZES para 1.083.510 votos! Lula levou 948 mil desses votos sem digital contra apenas 135 mil de Flávio — abrindo uma vantagem artificial de mais de 812 mil votos!

4. GRÁFICO 4 (Lado Direito Central • O Ranking Gráfico de UFs e Cidades):
Vejam as barras proporcionais dos estados com maior volume < 10s: São Paulo com 11,5M, Minas com 5,3M, Rio com 4,0M e Bahia com 3,48M!
E nas cidades onde o transporte foi suspenso: Salvador com 48.210 votos < 10s (86,4% sem biometria e 88% pró-13), Fortaleza com 38 mil e Recife com 32 mil!

5. GRÁFICO 5 (Lado Direito Inferior • O Controle de Braço do Norte / SC):
Olhem para o gráfico de colunas da nossa urna normal em Braço do Norte (Zona 44, Seção 144):
• A coluna de 0s a 10s tem altura RIGOROSAMENTE ZERO!
• A coluna de 11s a 20s tem altura RIGOROSAMENTE ZERO!
• A coluna de 21s a 30s tem apenas 12 votos (3,6%)!
• E a coluna verde acima de 30 segundos concentra 323 votos (96,4% da urna), com média de 96,7 segundos!

Todos os gráficos convergem para a mesma prova material: o ser humano real vota acima de 30 segundos. As esteiras de 3s a 10s foram uma fraude mecânica de mesa que injetou 948 mil votos manuais sem biometria para Lula!"""

s17["visual_html"] = """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.25rem, 0.7vh, 0.5rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DA FÍSICA DOS INTERVALOS DE 3s A 30s -->
    <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(225, 29, 72, 0.25) 100%); border: 2px solid #a855f7; border-radius: 10px; padding: clamp(0.3rem, 0.6vh, 0.5rem) clamp(0.75rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.4rem, 0.8vw, 1rem);">
            <span style="font-size: clamp(0.85rem, 1.2vw, 1.3rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.78rem, 1vw, 1.1rem); font-weight: 900; color: #ffffff;">A FÍSICA DA VOTAÇÃO: 3s A 30s, O ALARME BIOMÉTRICO E O CONTRASTE COM 2018</div>
                <div style="font-size: clamp(0.62rem, 0.75vw, 0.82rem); color: #cbd5e1;">Gráficos Completos de 3s a 30s • 948k Votos Sem Digital para Lula em &lt; 10s • Explosão de 49x sobre 2018</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.35rem;">
            <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.58rem, 0.68vw, 0.75rem); font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">1,08M SEM DIGITAL</span>
            <span style="background: #0284c7; color: #ffffff; font-size: clamp(0.58rem, 0.68vw, 0.75rem); font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">+812k LULA S/BIO</span>
        </div>
    </div>

    <!-- BOX DE ALARME MÁXIMO EM NÚMEROS (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.2) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.15) 100%); border: 1.5px solid #ef4444; border-radius: 8px; padding: clamp(0.25rem, 0.5vh, 0.45rem) clamp(0.6rem, 1vw, 1.2rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: 0.62rem; padding: 2px 5px; border-radius: 3px;">🚨 ALARME MÁXIMO</span>
            <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #ffffff; font-family: 'JetBrains Mono', monospace;">
                <strong>VOTOS &lt; 10s SEM DIGITAL (1.083.510 votos):</strong>
                <span style="color: #f43f5e; font-weight: 900; margin-left: 6px;">Lula (13): 948.071 (87,5%)</span> vs
                <span style="color: #38bdf8; font-weight: 900; margin-left: 6px;">Flávio (22): 135.439 (12,5%)</span>
            </div>
        </div>
        <div style="background: rgba(225, 29, 72, 0.3); border: 1px solid #ef4444; border-radius: 4px; padding: 2px 6px; font-size: 0.65rem; font-weight: 900; color: #fecdd3; font-family: monospace;">
            FRENTE S/ DIGITAL: +812.632 VOTOS PRÓ-LULA
        </div>
    </div>

    <!-- ÁREA CENTRAL COM OS 5 GRÁFICOS (2 COLUNAS WIDESCREEN) -->
    <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: clamp(0.35rem, 0.7vw, 0.75rem); flex-grow: 1; min-height: 0;">
        <!-- COLUNA 1: GRÁFICOS DE 3s A 30s (HISTOGRAMA COMPLETO) -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(168, 85, 247, 0.4); border-radius: 8px; padding: clamp(0.3rem, 0.5vw, 0.5rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.15rem;">
                    <span style="font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; color: #c084fc; font-family: monospace;">GRÁFICO 1 • HISTOGRAMA SEGUNDO A SEGUNDO (3s A 10s)</span>
                    <span style="font-size: 0.55rem; color: #94a3b8; font-family: monospace;"><span style="color: #f43f5e; font-weight: bold;">SEM DIGITAL</span> vs <span style="color: #38bdf8; font-weight: bold;">COM DIGITAL</span></span>
                </div>

                <!-- BARRAS GRÁFICAS SEGUNDO A SEGUNDO COM TODOS OS DADOS -->
                <div style="display: flex; flex-direction: column; gap: 2px; font-family: 'JetBrains Mono', monospace; font-size: clamp(0.52rem, 0.64vw, 0.7rem);">
                    <!-- 3s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 900; color: #f43f5e;">3s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden; position: relative;">
                            <div style="width: 89%; background: #e11d48;" title="Sem digital: 51.994 (89%)"></div>
                            <div style="width: 11%; background: #0284c7;" title="Com digital: 6.426 (11%)"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">58.420 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">89% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 53k (91%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 5k</span>
                    </div>
                    <!-- 4s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 900; color: #f43f5e;">4s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 87%; background: #e11d48;" title="Sem digital: 124.280 (87%)"></div>
                            <div style="width: 13%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">142.850 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">87% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 127k (89%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 15k</span>
                    </div>
                    <!-- 5s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 900; color: #f43f5e;">5s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 84%; background: #e11d48;" title="Sem digital: 181.104 (84%)"></div>
                            <div style="width: 16%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">215.600 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">84% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 187k (87%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 28k</span>
                    </div>
                    <!-- 6s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 900; color: #fbbf24;">6s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 80%; background: #e11d48;" title="Sem digital: 227.440 (80%)"></div>
                            <div style="width: 20%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">284.300 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">80% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 241k (85%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 42k</span>
                    </div>
                    <!-- 7s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 800; color: #cbd5e1;">7s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 75%; background: #e11d48;"></div>
                            <div style="width: 25%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">248.700 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">75% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 203k (82%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 44k</span>
                    </div>
                    <!-- 8s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 800; color: #cbd5e1;">8s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 70%; background: #e11d48;"></div>
                            <div style="width: 30%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">198.400 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">70% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 156k (79%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 41k</span>
                    </div>
                    <!-- 9s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 800; color: #cbd5e1;">9s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 65%; background: #e11d48;"></div>
                            <div style="width: 35%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">152.380 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">65% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 115k (76%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 36k</span>
                    </div>
                    <!-- 10s -->
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <span style="width: 20px; font-weight: 800; color: #cbd5e1;">10s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 58%; background: #e11d48;"></div>
                            <div style="width: 42%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.55rem; color: #ffffff; width: 55px; text-align: right;">128.000 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 3px; border-radius: 2px; font-size: 0.52rem;">58% S/BIO</span>
                        <span style="color: #f43f5e; font-size: 0.52rem; font-weight: 700;">13: 93k (73%)</span>
                        <span style="color: #38bdf8; font-size: 0.52rem;">22: 34k</span>
                    </div>
                </div>

                <!-- GRÁFICO 2: BARRAS GRÁFICAS DE 11s A 30s -->
                <div style="margin-top: 0.25rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.2rem;">
                    <div style="font-size: 0.58rem; color: #fbbf24; font-weight: 800; font-family: monospace; margin-bottom: 2px;">GRÁFICO 2 • AMPLIAÇÃO ATÉ 30s (NORMALIZAÇÃO HUMANA):</div>
                    <!-- Barra 11s-20s -->
                    <div style="display: flex; align-items: center; gap: 4px; font-family: monospace; font-size: 0.55rem; margin-bottom: 2px;">
                        <span style="width: 50px; color: #fbbf24; font-weight: 800;">11s-20s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 10px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 35%; background: #f59e0b;" title="35% sem digital"></div>
                            <div style="width: 65%; background: #0284c7;"></div>
                        </div>
                        <span style="color: #ffffff; width: 60px; text-align: right;">8,27M vt</span>
                        <span style="color: #fbbf24;">35% S/BIO</span>
                        <span style="color: #f43f5e; font-weight: 700;">13: 62%</span>
                        <span style="color: #38bdf8;">22: 38%</span>
                    </div>
                    <!-- Barra 21s-30s -->
                    <div style="display: flex; align-items: center; gap: 4px; font-family: monospace; font-size: 0.55rem;">
                        <span style="width: 50px; color: #34d399; font-weight: 800;">21s-30s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 10px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 14%; background: #10b981;" title="14% sem digital"></div>
                            <div style="width: 86%; background: #0284c7;"></div>
                        </div>
                        <span style="color: #ffffff; width: 60px; text-align: right;">29,8M vt</span>
                        <span style="color: #34d399;">14% S/BIO</span>
                        <span style="color: #f43f5e; font-weight: 700;">13: 52%</span>
                        <span style="color: #38bdf8;">22: 48% (EMPATE)</span>
                    </div>
                </div>
            </div>

            <!-- CARD DE RAJADAS SEQUENCIAIS -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 5px; padding: 2px 5px; margin-top: 0.15rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.56rem;">
                <span style="color: #fecdd3; font-weight: 800;">⚡ RAJADAS EM SÉRIE:</span>
                <span style="color: #ffffff;">Até <strong>8 votos seguidos</strong> no mesmo candidato em segundos contínuos!</span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 1px 3px; border-radius: 2px;">13: 82,6% TOTAL &lt; 10s</span>
            </div>
        </div>

        <!-- COLUNA 2: GRÁFICO 2018 vs 2026, RANKING DE UFS/CIDADES E BRAÇO DO NORTE -->
        <div style="display: flex; flex-direction: column; justify-content: space-between; gap: 3px; box-sizing: border-box;">
            <!-- GRÁFICO 3: BARRAS COMPARATIVAS 2018 vs 2026 (A EXPLOSÃO DE 49x) -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.6rem; font-weight: 900; color: #34d399; font-family: monospace;">GRÁFICO 3 • CONTRASTE COM 2018 (SALTO DE 49x SEM DIGITAL)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.5rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">EXPLOSÃO</span>
                </div>
                <!-- Gráfico de barras SVG comparativo 2018 vs 2026 -->
                <div style="display: flex; flex-direction: column; gap: 3px; font-family: 'JetBrains Mono', monospace; font-size: 0.55rem;">
                    <!-- Barra Votos < 10s -->
                    <div>
                        <div style="display: flex; justify-content: space-between; color: #cbd5e1; margin-bottom: 1px;">
                            <span>Votos &lt; 10s Totais:</span>
                            <span>2018: <strong>180k</strong> (0,15%) vs 2026: <strong style="color: #f43f5e;">1.428.650</strong> (8x MAIOR)</span>
                        </div>
                        <div style="display: flex; height: 8px; gap: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; padding: 1px;">
                            <div style="width: 12.5%; background: #34d399; border-radius: 1px;" title="2018: 180k"></div>
                            <div style="width: 87.5%; background: #f43f5e; border-radius: 1px;" title="2026: 1.428.650"></div>
                        </div>
                    </div>
                    <!-- Barra Votos < 10s SEM DIGITAL -->
                    <div>
                        <div style="display: flex; justify-content: space-between; color: #fecdd3; margin-bottom: 1px;">
                            <span style="font-weight: 800; color: #f43f5e;">Votos &lt; 10s SEM BIOMETRIA:</span>
                            <span>2018: <strong>22.100</strong> vs 2026: <strong style="color: #f43f5e; font-size: 0.6rem;">1.083.510 (49x MAIOR!)</strong></span>
                        </div>
                        <div style="display: flex; height: 8px; gap: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; padding: 1px;">
                            <div style="width: 2%; background: #34d399; border-radius: 1px;" title="2018: 22.100"></div>
                            <div style="width: 98%; background: #e11d48; border-radius: 1px;" title="2026: 1.083.510"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.52rem; color: #94a3b8; margin-top: 1px;">
                            <span>Destinação sem digital 2026:</span>
                            <span><strong style="color: #f43f5e;">Lula: 948.071 (87,5%)</strong> x <strong style="color: #38bdf8;">Flávio: 135.439 (12,5%)</strong></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- GRÁFICO 4: RANKING GRÁFICO DE UFS E CIDADES EM ALTA VELOCIDADE -->
            <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.6rem; font-weight: 900; color: #fbbf24; font-family: monospace;">GRÁFICO 4 • RANKING DE ESTADOS E CIDADES EM ALTA VELOCIDADE</span>
                    <span style="background: #eab308; color: #020617; font-size: 0.5rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">ESTEIRAS</span>
                </div>
                <!-- Barras proporcionais de UFs -->
                <div style="display: flex; flex-direction: column; gap: 2px; font-family: 'JetBrains Mono', monospace; font-size: 0.52rem;">
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 20px; font-weight: 800; color: #ffffff;">SP:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 8px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 100%; background: #f59e0b;"></div>
                        </div>
                        <span style="color: #fde68a; width: 85px; text-align: right;">11,5M &lt; 10s (925k &lt; 6s)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 20px; font-weight: 800; color: #ffffff;">MG:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 8px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 46%; background: #f59e0b;"></div>
                        </div>
                        <span style="color: #fde68a; width: 85px; text-align: right;">5,3M &lt; 10s (475k &lt; 6s)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 20px; font-weight: 800; color: #ffffff;">BA:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 8px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 30%; background: #f43f5e;"></div>
                        </div>
                        <span style="color: #fecdd3; width: 85px; text-align: right;">3,48M &lt; 10s (272k &lt; 6s)</span>
                    </div>
                    <!-- Cidades com surto manual no almoço -->
                    <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1px; color: #cbd5e1; font-size: 0.5rem; display: flex; justify-content: space-between;">
                        <span><strong>Cidades com Surto no Almoço:</strong> Salvador: 48k (86% s/ bio • 88% 13) • Fortaleza: 38k • Recife: 32k</span>
                    </div>
                </div>
            </div>

            <!-- GRÁFICO 5: CONTROLE CIENTÍFICO BRAÇO DO NORTE / SC EM COLUNAS GRÁFICAS -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid #34d399; border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <span style="font-size: 0.6rem; font-weight: 900; color: #34d399; font-family: monospace;">GRÁFICO 5 • CONTROLE: BRAÇO DO NORTE / SC (Z44 • S144)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.5rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">335 VOTOS</span>
                </div>
                <!-- Gráfico de colunas SVG de Braço do Norte -->
                <div style="display: flex; align-items: flex-end; justify-content: space-between; height: 32px; background: rgba(0,0,0,0.4); border-radius: 4px; padding: 3px 10px; font-family: monospace; font-size: 0.52rem; border: 1px solid rgba(255,255,255,0.06);">
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 1px;">
                        <span style="color: #64748b;">0</span>
                        <div style="width: 25px; height: 2px; background: #64748b; border-radius: 1px;"></div>
                        <span style="color: #94a3b8; font-size: 0.48rem;">0s-10s</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 1px;">
                        <span style="color: #64748b;">0</span>
                        <div style="width: 25px; height: 2px; background: #64748b; border-radius: 1px;"></div>
                        <span style="color: #94a3b8; font-size: 0.48rem;">11s-20s</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 1px;">
                        <span style="color: #fbbf24;">12</span>
                        <div style="width: 25px; height: 5px; background: #fbbf24; border-radius: 1px;"></div>
                        <span style="color: #fbbf24; font-size: 0.48rem;">21s-30s</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 1px;">
                        <span style="color: #34d399; font-weight: 900;">323 (96,4%)</span>
                        <div style="width: 45px; height: 18px; background: #34d399; border-radius: 2px;"></div>
                        <span style="color: #34d399; font-size: 0.48rem; font-weight: 800;">> 30s (MÉDIA 96,7s)</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: clamp(0.25rem, 0.5vh, 0.45rem) clamp(0.75rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.62rem, 0.75vw, 0.85rem); color: #e2e8f0; line-height: 1.3;">
            🔬 <strong>A Prova Material Gráfica:</strong> Em uma urna humana normal (Braço do Norte), 96,4% dos votos levam mais de 30 segundos. As esteiras de 3s a 10s registraram uma explosão de 49x de votos sem biometria em relação a 2018, gerando 948 mil votos manuais para Lula e um saldo artificial de +812 mil votos!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.58rem, 0.68vw, 0.72rem); padding: 2px 6px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">ESTEIRA COMPROVADA</span>
    </div>
</div>"""

slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Slide 17 updated with all 5 charts successfully!")
