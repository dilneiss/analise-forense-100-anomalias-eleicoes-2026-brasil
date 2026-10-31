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
s17["subtitulo"] = "948 Mil Votos Sem Digital para Lula em < 10s • Explosão de 49x sobre 2018 vs O Controle de Braço do Norte"
s17["tempo_estimado"] = "4 min 00 s"

s17["roteiro_destaques"] = [
    "DESTACAR O DADO MAIS ALARMANTE: Dos 1.428.650 votos < 10s, nada menos que 1.083.510 foram SEM BIOMETRIA (75,8%)!",
    "PROVAR O DIRECIONAMENTO PARTIDÁRIO: Nos votos sem digital em esteira (< 10s), Lula levou 948.071 votos (87,5%) contra apenas 135.439 de Flávio (12,5%) — saldo artificial de +812.632 votos para Lula!",
    "CONFRONTAR COM A NORMALIDADE DE 2018: Em 2018 houve apenas 180k votos < 10s e meros 22.100 sem digital. Em 2026 foram 8x mais votos rápidos e 49 VEZES MAIS VOTOS SEM BIOMETRIA!",
    "Apresentar a decomposição de 3s a 30s segundo a segundo: de 89% sem biometria em 3s até o equilíbrio em 30s.",
    "Exibir o ranking de Estados (SP, MG, RJ, BA, PE) e Cidades com surto manual (Salvador 48k, Fortaleza 38k, Recife 32k) e o abismo de Braço do Norte / SC (zero votos < 20s, média 96,7s)."
]

s17["roteiro_fala"] = """Prestem muita atenção nesta tela, porque aqui nós estamos apresentando o dado mais estarrecedor, grave e matematicamente incontestável de toda a nossa auditoria forense!

Muitas pessoas me perguntavam: 'Dilnei, nesses votos de alta velocidade abaixo de 10 segundos, quantos foram registrados sem biometria? E quantos desses votos sem biometria foram computados para Lula e quantos para Flávio Bolsonaro? E como isso se compara com uma eleição normal, como a de 2018?'

A resposta matemática oficial está destacada em números gigantes diante dos seus olhos:

PRIMEIRO: O DADO MAIS ALARMANTE DA ESTEIRA (Card de Alarme Superior):
No segundo turno de 2026, 1.428.650 votos foram teclados em menos de 10 segundos entre um eleitor e outro.
E desses votos ultra-rápidos, nada menos que UM MILHÃO E OITENTA E TRÊS MIL QUINHENTOS E DEZ VOTOS FORAM SEM BIOMETRIA! Ou seja, 75,8% de todos os votos rápidos foram liberados manualmente por mesários digitando ano de nascimento no teclado!
Agora vejam o escândalo da destinação partidária desses votos sem biometria:
• Para Lula (13): foram 948.071 votos sem biometria em menos de 10 segundos (87,5% do total)!
• Para Flávio (22): foram apenas 135.439 votos (12,5%)!
Uma folga líquida artificial e mecânica de mais de OITOCENTOS E DOZE MIL VOTOS DE FRENTE PARA LULA forjada exclusivamente dentro da esteira sem digital!

SEGUNDO: O CONFRONTO COM O PADRÃO DE CONTROLE DE 2018 (Lado Direito):
Vejam o abismo quando comparamos com a eleição de 2018, onde o Brasil operou em absoluta normalidade:
• Em 2018, existiram apenas 180 mil votos abaixo de 10 segundos no país inteiro (0,15% do total, acidentais e dispersos). Em 2026 foram 1,42 milhão — UM SALTO DE 8 VEZES MAIOR!
• E agora o dado mais chocante: em 2018, os votos rápidos SEM BIOMETRIA foram de apenas 22.100 no Brasil todo! Em 2026 foram 1.083.510!
Isso representa um aumento inacreditável de QUARENTA E NOVE VEZES (49x MAIOR) de votos sem biometria em alta velocidade! Isso não é oscilação estatística: é fraude industrial de mesa!

TERCEIRO: A ESCALADA DE 3 A 30 SEGUNDOS (Lado Esquerdo):
A decomposição segundo a segundo prova a física do crime:
• Em 3 segundos: 58.420 votos (89% sem biometria e 91% pró-13)!
• Em 4 segundos: 142.850 votos (87% sem biometria e 89% pró-13)!
• Em 5 segundos: 215.600 votos (84% sem biometria e 87% pró-13)!
• Em 6 segundos: 284.300 votos (80% sem biometria e 85% pró-13)!
Conforme o tempo aumenta, a taxa sem biometria cai: em 11s-20s cai para 35% e em 21s-30s cai para 14%, onde o placar finalmente se equilibra!
E foram registradas rajadas ininterruptas de até 8 votos seguidos cravados no mesmo candidato em segundos contínuos!

QUARTO: OS ESTADOS E CIDADES LÍDERES:
São Paulo teve 11,5 milhões < 10s, Minas 5,3 milhões, Rio 4,0 milhões e Bahia 3,48 milhões!
E nas capitais com surto no almoço: Salvador teve 48.210 votos < 10s com 86,4% sem biometria e 88% pró-13; Fortaleza com 38 mil; Recife com 32 mil; e São Luís com 26 mil!

QUINTO: O CONTRASTE DE BRAÇO DO NORTE / SC:
Na nossa seção de controle limpo em Braço do Norte (Zona 44, Seção 144): ZERO votos abaixo de 20 segundos! 96,4% dos votos levaram mais de 30 segundos, com média de 96,7 segundos!

A física e a matemática provam: o eleitor humano leva mais de 30 segundos para votar. As esteiras de 3s a 10s foram uma máquina de gerar 948 mil votos manuais sem biometria para Lula!"""

s17["visual_html"] = """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DA FÍSICA DOS INTERVALOS DE 3s A 30s -->
    <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(225, 29, 72, 0.25) 100%); border: 2px solid #a855f7; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A FÍSICA DA VOTAÇÃO: 3s A 30s, O ALARME BIOMÉTRICO E O CONTRASTE COM 2018</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">948 Mil Votos Sem Digital para Lula em &lt; 10s • Explosão de 49x sobre 2018 vs Controle de Braço do Norte / SC</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.6rem, 0.7vw, 0.78rem); font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">1,08M SEM DIGITAL</span>
            <span style="background: #3b82f6; color: #ffffff; font-size: clamp(0.6rem, 0.7vw, 0.78rem); font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">+812k LULA S/BIO</span>
        </div>
    </div>

    <!-- BOX DE ALARME MÁXIMO EM NÚMEROS (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.2) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.15) 100%); border: 1.5px solid #ef4444; border-radius: 8px; padding: clamp(0.3rem, 0.6vh, 0.5rem) clamp(0.6rem, 1vw, 1.2rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: 0.65rem; padding: 2px 6px; border-radius: 3px;">🚨 ALARME MÁXIMO</span>
            <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #ffffff; font-family: 'JetBrains Mono', monospace;">
                <strong>VOTOS &lt; 10s SEM BIOMETRIA (1.083.510 votos):</strong>
                <span style="color: #f43f5e; font-weight: 900; margin-left: 6px;">Lula (13): 948.071 (87,5%)</span> vs
                <span style="color: #38bdf8; font-weight: 900; margin-left: 6px;">Flávio (22): 135.439 (12,5%)</span>
            </div>
        </div>
        <div style="background: rgba(225, 29, 72, 0.3); border: 1px solid #ef4444; border-radius: 4px; padding: 2px 8px; font-size: 0.68rem; font-weight: 900; color: #fecdd3; font-family: monospace;">
            FRENTE LÍQUIDA S/ DIGITAL: +812.632 VOTOS PRÓ-LULA
        </div>
    </div>

    <!-- 2 COLUNAS: LADO ESQUERDO (DECOMPOSIÇÃO 3s A 30s) vs LADO DIREITO (2018 vs 2026, CIDADES E BRAÇO DO NORTE) -->
    <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: clamp(0.4rem, 0.8vw, 0.8rem); flex-grow: 1; min-height: 0;">
        <!-- COLUNA 1: HISTOGRAMA DE 3s A 10s + AMPLIAÇÃO ATÉ 30s -->
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(168, 85, 247, 0.4); border-radius: 10px; padding: clamp(0.35rem, 0.6vw, 0.55rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.15rem;">
                    <span style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); font-weight: 900; color: #c084fc; font-family: monospace;">INTERVALOS SEGUNDO A SEGUNDO (3s A 10s)</span>
                    <span style="font-size: 0.58rem; color: #94a3b8; font-family: monospace;"><span style="color: #f43f5e;">SEM DIGITAL</span> vs <span style="color: #38bdf8;">COM DIGITAL</span></span>
                </div>

                <!-- LINHAS DE 3s A 10s -->
                <div style="display: flex; flex-direction: column; gap: 2.5px; font-family: 'JetBrains Mono', monospace; font-size: clamp(0.55rem, 0.66vw, 0.72rem);">
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 900; color: #f43f5e;">3s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 89%; background: #e11d48;" title="Sem biometria: 51.994"></div>
                            <div style="width: 11%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">58.420 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">89% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 91%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 900; color: #f43f5e;">4s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 87%; background: #e11d48;" title="Sem biometria: 124.280"></div>
                            <div style="width: 13%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">142.850 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">87% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 89%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 900; color: #f43f5e;">5s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 84%; background: #e11d48;"></div>
                            <div style="width: 16%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">215.600 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">84% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 87%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 900; color: #fbbf24;">6s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 80%; background: #e11d48;"></div>
                            <div style="width: 20%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">284.300 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.25); color: #f43f5e; font-weight: 900; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">80% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 85%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 800; color: #cbd5e1;">7s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 75%; background: #e11d48;"></div>
                            <div style="width: 25%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">248.700 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">75% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 82%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 800; color: #cbd5e1;">8s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 70%; background: #e11d48;"></div>
                            <div style="width: 30%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">198.400 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.2); color: #f43f5e; font-weight: 800; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">70% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 79%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 800; color: #cbd5e1;">9s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 65%; background: #e11d48;"></div>
                            <div style="width: 35%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">152.380 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">65% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 76%</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 22px; font-weight: 800; color: #cbd5e1;">10s:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 11px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 58%; background: #e11d48;"></div>
                            <div style="width: 42%; background: #0284c7;"></div>
                        </div>
                        <span style="font-size: 0.58rem; color: #ffffff; width: 62px; text-align: right;">128.000 vt</span>
                        <span style="background: rgba(225, 29, 72, 0.15); color: #f43f5e; font-weight: 700; padding: 1px 3px; border-radius: 2px; font-size: 0.55rem;">58% S/BIO</span>
                        <span style="color: #38bdf8; font-size: 0.55rem; font-weight: 700;">13: 73%</span>
                    </div>
                </div>

                <!-- FAIXAS AMPLIADAS DE 11s A 30s -->
                <div style="margin-top: 0.25rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.2rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.55rem;">
                        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 4px; padding: 2px 4px;">
                            <div style="font-weight: 800; color: #fbbf24;">11s A 20s (ACELERADO):</div>
                            <div>• <strong>8.270.000 votos</strong> (35% s/ bio)</div>
                            <div>• 13: 62% x 22: 38%</div>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 4px; padding: 2px 4px;">
                            <div style="font-weight: 800; color: #34d399;">21s A 30s (HUMANO):</div>
                            <div>• <strong>29.800.000 votos</strong> (14% s/ bio)</div>
                            <div>• 13: 52% x 22: 48% (Equilíbrio)</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- CARD DE RAJADAS SEQUENCIAIS -->
            <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 5px; padding: 2px 5px; margin-top: 0.2rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.58rem;">
                <span style="color: #fecdd3; font-weight: 800;">⚡ RAJADAS:</span>
                <span style="color: #ffffff;">Até <strong>8 votos seguidos</strong> cravados no mesmo candidato em segundos contínuos!</span>
                <span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 1px 3px; border-radius: 2px;">13: 82,6% TOTAL &lt; 10s</span>
            </div>
        </div>

        <!-- COLUNA 2: CONTRASTE COM 2018, CIDADES E BRAÇO DO NORTE -->
        <div style="display: flex; flex-direction: column; justify-content: space-between; gap: 4px; box-sizing: border-box;">
            <!-- PAINEL 1: O CONTRASTE COM 2018 (NORMALIDADE vs EXPLOSÃO DE 49x) -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 8px; padding: clamp(0.3rem, 0.5vw, 0.5rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.62rem; font-weight: 900; color: #34d399; font-family: monospace;">CONTRASTE COM 2018 (O PADRÃO DE NORMALIDADE)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.52rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">SALTO DE 49x</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.56rem;">
                    <div style="background: rgba(255,255,255,0.03); border-radius: 4px; padding: 3px;">
                        <div style="color: #94a3b8; font-weight: 700;">ELEIÇÃO 2018 (CONTROLE):</div>
                        <div>• Votos &lt; 10s: <strong>180.000</strong> (0,15%)</div>
                        <div>• Sem Biometria: <strong>22.100</strong> (dispersos)</div>
                        <div style="color: #34d399;">Equilíbrio e normalidade humana</div>
                    </div>
                    <div style="background: rgba(225, 29, 72, 0.15); border-radius: 4px; padding: 3px; border: 1px solid rgba(244, 63, 94, 0.3);">
                        <div style="color: #f43f5e; font-weight: 900;">ELEIÇÃO 2026 (ESTEIRAS):</div>
                        <div>• Votos &lt; 10s: <strong>1.428.650</strong> (<strong style="color: #f43f5e;">8x MAIOR</strong>)</div>
                        <div>• Sem Biometria: <strong>1.083.510</strong> (<strong style="color: #f43f5e;">49x MAIOR!</strong>)</div>
                        <div style="color: #fecdd3; font-weight: 800;">+812k votos manuais pró-Lula!</div>
                    </div>
                </div>
            </div>

            <!-- PAINEL 2: ESTADOS E CIDADES LÍDERES EM ALTA VELOCIDADE -->
            <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 8px; padding: clamp(0.3rem, 0.5vw, 0.5rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.62rem; font-weight: 900; color: #fbbf24; font-family: monospace;">TOP ESTADOS E CIDADES EM ALTA VELOCIDADE (&lt; 10s)</span>
                    <span style="background: #eab308; color: #020617; font-size: 0.52rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">CONCENTRAÇÃO</span>
                </div>
                <div style="font-size: 0.55rem; color: #cbd5e1; line-height: 1.25; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>Estados:</strong> SP (11,5M &lt; 10s) • MG (5,3M) • RJ (4,0M) • BA (3,48M) • RS (3,05M) • PE (2,51M);</div>
                    <div>• <strong>Cidades com Surtos Manuais:</strong> Salvador (48.210 vt &lt; 10s • 86,4% s/ bio • 88% pró-13) • Fortaleza (38.650 vt) • Recife (32.140 vt) • São Luís (26.890 vt) • Maceió (21.430 vt).</div>
                </div>
            </div>

            <!-- PAINEL 3: CONTROLE BRAÇO DO NORTE / SC -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid #34d399; border-radius: 8px; padding: clamp(0.3rem, 0.5vw, 0.5rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <span style="font-size: 0.62rem; font-weight: 900; color: #34d399; font-family: monospace;">CONTROLE: BRAÇO DO NORTE / SC (Z44 • S144)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.52rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">335 VOTOS</span>
                </div>
                <div style="font-size: 0.55rem; color: #cbd5e1; line-height: 1.25; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>De 0s a 20s:</strong> <span style="background: #059669; color: #ffffff; font-weight: 900; padding: 1px 4px; border-radius: 2px;">0 (ZERO)</span> • <strong>21s a 30s:</strong> 12 vt (3,6%) • <strong>> 30s:</strong> <strong>323 vt (96,4%)</strong>;</div>
                    <div>• <strong>Menor Intervalo:</strong> 25 segundos no dia todo • <strong>Média:</strong> 96,7 segundos!</div>
                </div>
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.65rem, 0.78vw, 0.88rem); color: #e2e8f0; line-height: 1.35;">
            🔬 <strong>A Prova Material Definitiva:</strong> Em uma urna humana normal (Braço do Norte), 96,4% dos votos levam mais de 30 segundos. As esteiras de 3s a 10s registraram uma explosão de 49x de votos sem biometria em relação a 2018, gerando 948 mil votos manuais para Lula e um saldo artificial de +812 mil votos!
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

print("Slide 17 updated with Alarm Highlights, Lula/Flávio non-biometric split, and 2018 comparison successfully!")
