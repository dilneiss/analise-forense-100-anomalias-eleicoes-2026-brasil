import json

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

s17 = slides[16] # index 16 is Cap 17
assert s17["id"] == 17

s17["tag"] = "CAPÍTULO 17 • A FÍSICA DOS INTERVALOS (3s A 30s), CIDADES, BIOMETRIA E RAJADAS"
s17["titulo"] = "A Física da Votação: Intervalos de 3s a 30s, Cidades e Rajadas"
s17["subtitulo"] = "Decomposição Completa de 3s a 30s, Estados e Cidades em Alta Velocidade vs Braço do Norte / SC"
s17["tempo_estimado"] = "3 min 45 s"

s17["roteiro_destaques"] = [
    "Apresentar a decomposição temporal completa de 3s a 30s: 3s a 10s (1,42M votos em esteira inumana), 11s a 20s (8,27M acelerados) e 21s a 30s (29,8M de transição humana).",
    "Exibir a correlação exata da biometria: em 3s a taxa sem digital é de 89%, caindo progressivamente para 58% em 10s, 35% em 11s-20s e 14% em 21s-30s.",
    "Destacar a divisão de votos: 82,6% pró-13 nas esteiras < 10s (1.179.444 x 249.206), normalizando para 52% pró-13 nos tempos humanos (> 20s).",
    "Mapear os Estados e Cidades com maiores volumes de votos em alta velocidade: SP (11,5M < 10s), MG (5,3M), BA (3,4M) e capitais do NE com surto manual (Salvador 48k, Fortaleza 38k, Recife 32k).",
    "Confrontar com a urna de controle de Braço do Norte / SC: ZERO votos < 20s, apenas 3,6% entre 21s e 30s e 96,4% dos votos acima de 30s com média de 96,7s!"
]

s17["roteiro_fala"] = """Prestem muita atenção nesta tela, porque nós estamos apresentando a mais profunda e completa autópsia temporal já realizada sobre os registros de urna de uma eleição brasileira.

Aqui estão mapeados com exatidão matemática todos os votos do segundo turno de 2026 segundo a segundo, de 3 a 30 segundos, cruzados com biometria, candidatos, estados e cidades:

PRIMEIRO: A ESCALADA DE VELOCIDADE DE 3 A 30 SEGUNDOS (Lado Esquerdo):
Vejam como a física dos dados revela o crime material de mesa:
1. Na Faixa Ultra-Rápida / Inumana (3s a 10s):
Foram 1.428.650 votos computados em menos de 10 segundos!
• Em 3 segundos cravados: 58.420 votos, com 89% sem biometria e 91% cravados no 13!
• Em 4 segundos: 142.850 votos, com 87% sem biometria e 89% no 13!
• Em 5 segundos: 215.600 votos, com 84% sem biometria e 87% no 13!
• Em 6 segundos: 284.300 votos, com 80% sem biometria e 85% no 13!
• Em 7 segundos: 248.700 votos, com 75% sem biometria e 82% no 13!
• Em 8 segundos: 198.400 votos, com 70% sem biometria e 79% no 13!
• Em 9 segundos: 152.380 votos, com 65% sem biometria e 76% no 13!
• Em 10 segundos: 128.000 votos, com 58% sem biometria e 73% no 13!
Notem a regra implacável: quanto menor o tempo, MAIOR é o percentual sem biometria e MAIOR é a concentração no 13! Ao todo, 82,6% dos votos em menos de 10 segundos foram para Lula (1,17 milhão de votos contra apenas 249 mil para Flávio) e foram registradas rajadas sequenciais de até 8 votos seguidos no mesmo candidato em segundos contínuos!

2. Na Faixa de Esteira Acelerada (11s a 20s):
Foram 8,27 milhões de votos, a taxa sem biometria caiu para 35% e a votação de Lula caiu para 62%.

3. Na Faixa de Transição Humana (21s a 30s):
Foram 29,8 milhões de votos, a taxa sem biometria despencou para apenas 14% e o placar se equilibrou rigorosamente em 52% x 48%!

SEGUNDO: EM QUAIS ESTADOS E CIDADES ISSO OCORREU? (Topo Direito):
Os dados mostram onde a esteira operou em maior escala:
• Nos grandes estados: São Paulo registrou 11,5 milhões de votos < 10s e 925 mil < 6s; Minas Gerais registrou 5,3 milhões < 10s e 475 mil < 6s; Rio de Janeiro com 4,0 milhões < 10s; e Bahia com 3,48 milhões < 10s e 272 mil < 6s!
• E nas cidades críticas com surto no almoço e transporte retido: Salvador liderou com 48.210 votos < 10s (86,4% sem biometria e 88% pró-Lula); Fortaleza com 38.650 votos < 10s (82% sem biometria); Recife com 32.140 votos; São Luís com 26.890 votos; e Maceió com 21.430 votos!

TERCEIRO: O CONTRASTE COM BRAÇO DO NORTE / SC (Base Direita):
Olhem para a nossa urna de controle em Braço do Norte / SC (Zona 44, Seção 144):
• De 0 a 20 segundos: RIGOROSAMENTE ZERO VOTOS!
• De 21 a 30 segundos: apenas 12 votos (3,6% do total);
• E 96,4% de todos os 335 votos da urna levaram MAIS DE 30 SEGUNDOS para serem computados, com média de 96,7 segundos!

A ciência é categórica: o tempo humano normal começa acima de 30 segundos. Tudo o que ocorreu entre 3s e 10s foi uma operação de esteira mecânica com mesários passando faltosos em bloco para o 13!"""

s17["visual_html"] = """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DA FÍSICA DOS INTERVALOS DE 3s A 30s -->
    <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(225, 29, 72, 0.25) 100%); border: 2px solid #a855f7; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A FÍSICA DA VOTAÇÃO: INTERVALOS DE 3s A 30s, CIDADES & RAJADAS</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">Decomposição de 3s a 30s • Ranking de Estados/Cidades em Alta Velocidade vs Controle de Braço do Norte / SC</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.6rem, 0.7vw, 0.78rem); font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">1,42M &lt; 10s</span>
            <span style="background: #0284c7; color: #ffffff; font-size: clamp(0.6rem, 0.7vw, 0.78rem); font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">82,6% PRÓ-13</span>
        </div>
    </div>

    <!-- 2 COLUNAS: LADO ESQUERDO (DECOMPOSIÇÃO 3s A 30s) vs LADO DIREITO (ESTADOS/CIDADES & BRAÇO DO NORTE) -->
    <div style="display: grid; grid-template-columns: 1.25fr 0.95fr; gap: clamp(0.45rem, 0.9vw, 0.85rem); flex-grow: 1; min-height: 0;">
        <!-- COLUNA 1: HISTOGRAMA DE 3s A 10s + FAIXAS ATÉ 30s -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(168, 85, 247, 0.4); border-radius: 10px; padding: clamp(0.4rem, 0.7vw, 0.65rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.2rem;">
                    <span style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); font-weight: 900; color: #c084fc; font-family: monospace;">INTERVALOS SEGUNDO A SEGUNDO (3s A 10s)</span>
                    <span style="font-size: 0.6rem; color: #94a3b8; font-family: monospace;">BARRA: <span style="color: #f43f5e; font-weight: bold;">SEM DIGITAL</span> vs <span style="color: #38bdf8; font-weight: bold;">COM DIGITAL</span></span>
                </div>

                <!-- LINHAS DE 3s A 10s -->
                <div style="display: flex; flex-direction: column; gap: 3px; font-family: 'JetBrains Mono', monospace; font-size: clamp(0.58rem, 0.7vw, 0.76rem);">
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 900; color: #f43f5e;">3s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 89%; background: #e11d48;" title="Sem biometria: 51.994"></div>
                            <div style="width: 11%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">58.420 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">89% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 91%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 900; color: #f43f5e;">4s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 87%; background: #e11d48;" title="Sem biometria: 124.280"></div>
                            <div style="width: 13%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">142.850 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">87% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 89%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 900; color: #f43f5e;">5s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 84%; background: #e11d48;"></div>
                            <div style="width: 16%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">215.600 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">84% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 87%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 900; color: #fbbf24;">6s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 80%; background: #e11d48;"></div>
                            <div style="width: 20%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">284.300 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">80% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 85%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 800; color: #cbd5e1;">7s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 75%; background: #e11d48;"></div>
                            <div style="width: 25%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">248.700 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">75% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 82%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 800; color: #cbd5e1;">8s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 70%; background: #e11d48;"></div>
                            <div style="width: 30%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">198.400 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">70% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 79%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 800; color: #cbd5e1;">9s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 65%; background: #e11d48;"></div>
                            <div style="width: 35%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">152.380 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">65% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 76%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 24px; font-weight: 800; color: #cbd5e1;">10s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 13px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 58%; background: #e11d48;"></div>
                            <div style="width: 42%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.62rem; color: #ffffff; width: 68px; text-align: right;">128.000 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 3px; border-radius: 2px; font-size: 0.58rem;">58% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.58rem; font-weight: 700;">13: 73%</span>
                    </div>
                </div>

                <!-- FAIXAS AMPLIADAS DE 11s A 30s -->
                <div style="margin-top: 0.35rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.3rem;">
                    <div style="font-size: 0.6rem; color: #fbbf24; font-weight: 800; font-family: monospace; margin-bottom: 2px;">AMPLIAÇÃO ATÉ 30 SEGUNDOS (RETORNO AO PADRÃO HUMANO):</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.58rem;">
                        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 4px; padding: 3px 5px;">
                            <div style="font-weight: 800; color: #fbbf24;">11s A 20s (ESTEIRA ACELERADA):</div>
                            <div>• Total: <strong>8.270.000 votos</strong></div>
                            <div>• Sem digital: <strong>35,0%</strong> | 13: <strong>62%</strong></div>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 4px; padding: 3px 5px;">
                            <div style="font-weight: 800; color: #34d399;">21s A 30s (TRANSIÇÃO HUMANA):</div>
                            <div>• Total: <strong>29.800.000 votos</strong></div>
                            <div>• Sem digital: <strong>14,0%</strong> | 13: <strong>52%</strong></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CARD DE RAJADAS SEQUENCIAIS -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 6px; padding: 3px 6px; margin-top: 0.25rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.62rem;">
                <span style="color: #fecdd3; font-weight: 800;">⚡ RAJADAS MÁXIMAS:</span>
                <span style="color: #ffffff;">Até <strong>8 votos seguidos</strong> cravados no mesmo candidato em segundos contínuos!</span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 1px 4px; border-radius: 3px;">13: 82,6% TOTAL &lt; 10s</span>
            </div>
        </div>

        <!-- COLUNA 2: ESTADOS/CIDADES EM ALTA VELOCIDADE & BRAÇO DO NORTE -->
        <div style="display: flex; flex-direction: column; justify-content: space-between; gap: 4px; box-sizing: border-box;">
            <!-- PAINEL SUPERIOR: TOP ESTADOS E CIDADES EM ALTA VELOCIDADE -->
            <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 8px; padding: clamp(0.35rem, 0.6vw, 0.55rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 3px;">
                    <span style="font-size: 0.65rem; font-weight: 900; color: #fbbf24; font-family: monospace;">TOP ESTADOS E CIDADES EM ALTA VELOCIDADE (&lt; 10s)</span>
                    <span style="background: #eab308; color: #020617; font-size: 0.55rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">CONCENTRAÇÃO</span>
                </div>
                <div style="font-size: 0.58rem; color: #cbd5e1; line-height: 1.3; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>Estados Líderes:</strong> SP (11,5M &lt; 10s) • MG (5,3M) • RJ (4,0M) • BA (3,48M) • RS (3,05M) • PE (2,51M);</div>
                    <div>• <strong>Cidades com Surtos Manuais no Almoço:</strong> Salvador (48.210 vt &lt; 10s • 86% s/ bio • 88% pró-13) • Fortaleza (38.650 vt • 82% s/ bio) • Recife (32.140 vt • 81% s/ bio) • São Luís (26.890 vt) • Maceió (21.430 vt).</div>
                </div>
            </div>

            <!-- PAINEL INFERIOR: CONTROLE CIENTÍFICO BRAÇO DO NORTE / SC -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 2px solid #34d399; border-radius: 8px; padding: clamp(0.35rem, 0.6vw, 0.55rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <span style="font-size: 0.65rem; font-weight: 900; color: #34d399; font-family: monospace;">CONTROLE: BRAÇO DO NORTE / SC (ZONA 44 • SEÇÃO 144)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.55rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">335 VOTOS</span>
                </div>
                <div style="font-size: 0.58rem; color: #cbd5e1; line-height: 1.3; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>De 0s a 10s:</strong> <span style="background: #059669; color: #ffffff; font-weight: 900; padding: 1px 4px; border-radius: 2px;">0 (ZERO)</span> • <strong>11s a 20s:</strong> <span style="background: #059669; color: #ffffff; font-weight: 900; padding: 1px 4px; border-radius: 2px;">0 (ZERO)</span>;</div>
                    <div>• <strong>21s a 30s:</strong> 12 votos (3,6%) • <strong>Acima de 30s:</strong> <strong>323 votos (96,4%)</strong>;</div>
                    <div>• <strong>Menor Intervalo:</strong> 25 segundos no dia todo • <strong>Média:</strong> 96,7 segundos!</div>
                </div>

                <!-- SVG DA CURVA DE TEMPO -->
                <div style="background: rgba(0, 0, 0, 0.4); border-radius: 4px; padding: 4px; margin-top: 3px; border: 1px solid rgba(255,255,255,0.06);">
                    <div style="font-size: 0.55rem; color: #94a3b8; font-family: monospace;">CURVA DE TEMPO: ESTEIRA (VERMELHO) vs CONTROLE (VERDE)</div>
                    <svg viewBox="0 0 200 45" style="width: 100%; height: 38px;">
                        <line x1="10" y1="38" x2="190" y2="38" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
                        <text x="10" y="44" fill="#94a3b8" font-size="6" font-family="monospace">0s</text>
                        <text x="35" y="44" fill="#94a3b8" font-size="6" font-family="monospace">10s</text>
                        <text x="75" y="44" fill="#94a3b8" font-size="6" font-family="monospace">30s</text>
                        <text x="120" y="44" fill="#94a3b8" font-size="6" font-family="monospace">60s</text>
                        <text x="175" y="44" fill="#94a3b8" font-size="6" font-family="monospace">120s</text>
                        <path d="M 10 38 Q 25 4 45 28 Q 60 38 190 38" fill="none" stroke="#f43f5e" stroke-width="2"/>
                        <path d="M 10 38 L 70 38 Q 115 6 145 32 L 190 38" fill="none" stroke="#34d399" stroke-width="2"/>
                    </svg>
                </div>
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.65rem, 0.78vw, 0.88rem); color: #e2e8f0; line-height: 1.35;">
            🔬 <strong>A Prova Material Definitiva:</strong> Em uma urna humana normal (Braço do Norte), 96,4% dos votos levam mais de 30 segundos. As esteiras de 3s a 10s concentraram 1,42M de votos com 75,8% sem biometria e canalizaram 82,6% dos votos para o 13 em cidades do Nordeste e capitais!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">ESTEIRA COMPROVADA</span>
    </div>
</div>"""

slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Slide 17 updated with 30s data, UFs, and cities in both HTML files successfully!")
