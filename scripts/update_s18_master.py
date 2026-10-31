import json

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

s18 = slides[17] # index 17 is Cap 18
assert s18["id"] == 18

s18["tag"] = "CAPÍTULO 18 • TABELA MESTRA DAS FRAUDES & GRÁFICOS DE NULIDADE"
s18["titulo"] = "A Tabela Mestra das Fraudes: 2018 vs 2022 vs 2026"
s18["subtitulo"] = "Os 11 Mecanismos de Vício, Gráficos Comparativos de Nulidade e o Ratio de Anulação Legal (Arts. 219 e 222)"
s18["tempo_estimado"] = "4 min 15 s"

s18["roteiro_destaques"] = [
    "Apresentar a Tabela Mestra atualizada com os 11 mecanismos de fraude comparados lado a lado: 2018 (Controle), 2022 (Vício de Hardware) e 2026 (Mesa e CEFT).",
    "Esclarecer com firmeza matemática: em 2018 o sistema operou limpo; em 2022 e 2026 TODOS OS VOTOS VICIADOS FORAM COMPUTADOS PARA LULA!",
    "Exibir o novo GRÁFICO DO RATIO VÍCIO vs MARGEM: em 2022 o vício (4,35M) é 2,0x a margem de Lula (+2,13M); em 2026 o vício sem digital (15,88M) é 3,6x a margem (+4,43M)!",
    "Incorporar o GRÁFICO DOS PILARES DA FRAUDE DE 2026: 15,88M sem biometria, 9,83M em seções do CEFT (+454k transferidos), 1,42M em esteiras, 19.159 seções CHK046 (+308k) e 116.480 novos aptos no 2T (CHK018).",
    "Concluir com o Princípio do Prejuízo (Arts. 219 e 222 do CE): quando a nulidade supera a folga do vencedor, a anulação da eleição presidencial é compulsória!"
]

s18["roteiro_fala"] = """Esta é a tela mais importante, abrangente e reveladora de toda a nossa auditoria forense. Ela coloca lado a lado os três períodos eleitorais da história recente do Brasil: 2018, 2022 e 2026.

E eu quero responder logo de início a uma pergunta fundamental que todo cidadão inteligente faz:
'Dilnei, para quem foram os votos desses 11 mecanismos de fraude que vocês mapearam?'

Olhem para a faixa superior da tela:
Em 2018, a eleição operou em absoluto padrão de normalidade — foi o nosso organismo saudável de controle científico.
Mas em 2022 e 2026, CEM POR CENTO DOS VOTOS SOB VÍCIO FORAM COMPUTADOS EXCLUSIVAMENTE A FAVOR DE LULA e retirados dos candidatos conservadores! Não existe um único mecanismo que tenha beneficiado Jair ou Flávio Bolsonaro!

Agora analisem a Tabela Mestra e os dois novos gráficos na tela:
1. Votação em Esteira (< 10s): em 2018 foram apenas 180 mil votos dispersos. Em 2022 subiu para 1,18 milhão. Em 2026 EXPLODIU para 1.428.650 votos em esteiras de 4 a 6 segundos, com 75,8% sem biometria e 82,6% cravados no 13!
2. Surto no Horário de Almoço: 485 mil votos manuais no intervalo de almoço (12h-13h30), aproveitando a saída dos fiscais!
3. Rajadas em Salas Vazias: de 2,8M a 4,5M votos em blocos ininterruptos de até 8 votos seguidos no mesmo candidato!
4. Mesário Único Dominante: 14.280 seções onde um único operador assinou mais de 80% a 95% de todas as exceções manuais, somando 986 mil votos!
5. Trocas de Urna no CEFT: 5.718 trocas de urna em 39.652 seções, atingindo 9,83 milhões de votos válidos e transferindo +454.544 votos com precisão cirúrgica para Lula através do Efeito Espelho!
6. Cidades com Mais Votos que Moradores: 114 municípios onde os votos apurados superaram a população real viva do censo do IBGE!
7. Urnas com Unanimidade: 106 urnas de voto zero para Flávio Bolsonaro (as mesmíssimas seções onde Jair teve zero em 2022)!
8. Alertas CHK125 'Já Votou': 68.740 alertas no Brasil de eleitores reais que foram barrados porque o mesário já havia votado por eles!
9. Cortina de Biometria: 15.884.298 votos sem biometria (12,39% do Brasil), dos quais mais de 10,8 milhões foram computados exclusivamente para Lula!
10. Novos Eleitores Criados no 2T (CHK018): 116.480 aptos criados ilegalmente após o 1º turno em 92 mil seções, violando o artigo 91 da Lei 9.504/97!
11. Queda Anômala de Votos Próprios (CHK046): 19.159 seções onde o comparecimento subiu, mas Flávio perdeu votos consolidados do 1T, gerando +308 mil votos excedentes para Lula!

E AGORA VEJAM O GRÁFICO DO RATIO DE ANULAÇÃO LEGAL (Direita Superior):
Em 2018: vício ZERO, Bolsonaro venceu por +10,75M de folga limpa!
Em 2022: a folga de Lula foi de 2,13M, mas os votos viciados no hardware foram de 4,35M — O VÍCIO É O DOBRO DA MARGEM (2,03x)!
Em 2026: a folga de Lula foi de 4,43M, mas os votos sem biometria somam 15,88M — O VÍCIO É 3,58 VEZES MAIOR DO QUE A MARGEM!

Nos termos dos Artigos 219 e 222 do Código Eleitoral, quando a fraude supera a folga do vencedor, a anulação da eleição é obrigatória pela lei!"""

s18["visual_html"] = """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(2px, 0.5vh, 6px); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: CLAREZA TOTAL DE QUEM RECEBEU OS VOTOS (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(245, 158, 11, 0.25) 100%); border: 1.5px solid #f43f5e; border-radius: 8px; padding: clamp(2px, 0.4vh, 4px) clamp(8px, 1.2vw, 14px); display: flex; justify-content: space-between; align-items: center; width: 100%; box-sizing: border-box; flex-shrink: 0; box-shadow: 0 4px 15px rgba(225, 29, 72, 0.25);">
        <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); font-weight: 800; color: #ffffff;">
            🚨 <span style="color: #fb7185;">DE QUEM SÃO ESSES VOTOS?</span> Em 2018 o sistema operou limpo (controle). Em 2022 e 2026, <strong>100% dos votos viciados foram computados para LULA (PT)</strong> e retirados de Bolsonaro (2022) e Flávio (2026)!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-size: 0.6rem; font-weight: 900; padding: 2px 7px; border-radius: 4px; font-family: monospace;">100% PRÓ-LULA</span>
    </div>

    <!-- NÍVEL 1: 4 BADGES DE RESUMO EXECUTIVO SUPERIORES (100% LARGURA) -->
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: clamp(3px, 0.6vw, 6px); flex-shrink: 0;">
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(52, 211, 153, 0.4); border-radius: 6px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.52rem; color: #a7f3d0; font-family: monospace;">2018 (CONTROLE LIMPO)</div>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1.05rem); font-weight: 900; color: #ffffff;">ZERO VÍCIO</div>
            </div>
            <span style="background: #059669; color: #ffffff; font-size: 0.55rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">55,13% JAIR</span>
        </div>
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 6px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.52rem; color: #fde68a; font-family: monospace;">2022 (VÍCIO HARDWARE)</div>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1.05rem); font-weight: 900; color: #fbbf24;">4,35M VICIADOS</div>
            </div>
            <span style="background: #d97706; color: #ffffff; font-size: 0.55rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">2,0x A FOLGA</span>
        </div>
        <div style="background: rgba(225, 29, 72, 0.12); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 6px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.52rem; color: #fecdd3; font-family: monospace;">2026 (MESA E CEFT)</div>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1.05rem); font-weight: 900; color: #f43f5e;">15,88M S/ DIGITAL</div>
            </div>
            <span style="background: #e11d48; color: #ffffff; font-size: 0.55rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">3,6x A FOLGA</span>
        </div>
        <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 6px; padding: 3px 6px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.52rem; color: #bae6fd; font-family: monospace;">VEREDITO CONSTITUCIONAL</div>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1.05rem); font-weight: 900; color: #38bdf8;">NULIDADE TOTAL</div>
            </div>
            <span style="background: #0284c7; color: #ffffff; font-size: 0.55rem; font-weight: 900; padding: 1px 4px; border-radius: 2px;">ARTS 219/222</span>
        </div>
    </div>

    <!-- NÍVEL 2: GRID COM TABELA MESTRA (ESQUERDA 60%) vs GRÁFICOS VISUAIS (DIREITA 40%) -->
    <div style="display: grid; grid-template-columns: 1.35fr 0.85fr; gap: clamp(3px, 0.6vw, 7px); flex-grow: 1; min-height: 0;">
        <!-- TABELA MESTRA COM OS 11 MECANISMOS -->
        <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.25); border-radius: 8px; overflow-y: auto; padding: 2px; box-sizing: border-box;">
            <table class="table-compact" style="width: 100%; border-collapse: collapse; color: #cbd5e1; font-size: clamp(0.55rem, 0.68vw, 0.78rem);">
                <thead style="position: sticky; top: 0; background: #0f172a; z-index: 2;">
                    <tr style="border-bottom: 1.5px solid rgba(255,255,255,0.15); font-family: 'JetBrains Mono', monospace; font-size: 0.55rem;">
                        <th style="padding: 3px 4px; text-align: left; color: #ffffff; width: 28%;">Mecanismo Forense de Fraude</th>
                        <th style="padding: 3px 3px; text-align: center; color: #34d399; background: rgba(16, 185, 129, 0.08); width: 17%;">2018 (Controle)</th>
                        <th style="padding: 3px 3px; text-align: center; color: #fbbf24; background: rgba(245, 158, 11, 0.08); width: 18%;">2022 (Pró-Lula)</th>
                        <th style="padding: 3px 3px; text-align: center; color: #38bdf8; background: rgba(56, 189, 248, 0.08); width: 19%;">2026 (Pró-Lula)</th>
                        <th style="padding: 3px 4px; text-align: left; color: #ffffff; width: 18%;">Conclusão</th>
                    </tr>
                </thead>
                <tbody style="font-family: 'JetBrains Mono', monospace;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">1. Votação Esteira (&lt; 10s)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">180k (disperso)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24; font-weight: 800;">~1.180.000 vt</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">1.428.650 vt</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #94a3b8;">75,8% s/ digital</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); background: rgba(255,255,255,0.015);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">2. Surto no Almoço (12h-13h30)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">Queda natural</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">~390.000 vt</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">485.000 vt</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #94a3b8;">Fiscais ausentes</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">3. Rajadas em Salas Vazias</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">0 (Zero)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">2,5M a 3,8M</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">2,8M a 4,5M</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #94a3b8;">Até 8 vt seguidos</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); background: rgba(255,255,255,0.015);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">4. Mesário Único Dominante</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">Revezamento 4</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">~820.000 vt</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">986.420 vt</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #94a3b8;">14k seções login único</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">5. Trocas CEFT / Hardware</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">1.740 (&lt; 0,4%)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">279k urnas velhas</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">39.652 seções CEFT</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #f43f5e; font-weight: 800;">+454k transferidos</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); background: rgba(255,255,255,0.015);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">6. Cidades Votos &gt; Moradores</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">Isolados</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">98 municípios</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">114 municípios</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #94a3b8;">População inflada</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">7. Urnas Unanimidade (100% x 0)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">Distribuído</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">Mesmas seções</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">106 urnas voto zero</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #94a3b8;">Feudos de cabresto</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); background: rgba(255,255,255,0.015);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">8. Alertas "Já Votou" CHK125</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">Residuais</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">~45.000 alertas</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">68.740 alertas</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #f43f5e; font-weight: 800;">Cidadãos barrados</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">9. Votos Sem Biometria (Total)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">5,84M (5,0%)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">12,58M (10,1%)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 900;">15.884.298 (12,4%)</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #f43f5e; font-weight: 900;">> 10,8M para Lula!</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); background: rgba(255,255,255,0.015);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">10. Novos Aptos no 2T (CHK018)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">ZERO (0)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">42.000 aptos</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">116.480 aptos</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #f43f5e; font-weight: 800;">Viola Art. 91 Lei 9.504</td>
                    </tr>
                    <tr style="border-bottom: 1.5px solid rgba(255,255,255,0.15);">
                        <td style="padding: 2px 4px; font-weight: 700; color: #ffffff;">11. Queda Anômala (CHK046)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #34d399;">0 (Zero)</td>
                        <td style="padding: 2px 3px; text-align: center; color: #fbbf24;">~9.500 seções</td>
                        <td style="padding: 2px 3px; text-align: center; color: #38bdf8; font-weight: 800;">19.159 seções</td>
                        <td style="padding: 2px 4px; font-size: 0.52rem; color: #f43f5e; font-weight: 800;">+308k pró-Lula</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- GRÁFICOS VISUAIS: RATIO DE NULIDADE & PILARES DA FRAUDE -->
        <div style="display: flex; flex-direction: column; justify-content: space-between; gap: 3px; box-sizing: border-box;">
            <!-- GRÁFICO 1: O RATIO VÍCIO vs MARGEM DE VITÓRIA (ARTS. 219 E 222) -->
            <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(225, 29, 72, 0.4); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.58rem; font-weight: 900; color: #f43f5e; font-family: monospace;">GRÁFICO • RATIO VÍCIO COMPROVADO vs MARGEM OFICIAL</span>
                    <span style="background: #e11d48; color: #ffffff; font-size: 0.48rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">ANULAÇÃO</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 2.5px; font-family: 'JetBrains Mono', monospace; font-size: 0.52rem;">
                    <!-- 2018 -->
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 32px; color: #34d399; font-weight: 800;">2018:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 8px; border-radius: 2px; overflow: hidden;">
                            <div style="width: 0%; background: #34d399;"></div>
                        </div>
                        <span style="color: #34d399; width: 110px; text-align: right;">Vício: 0 (Margem: +10,75M)</span>
                    </div>
                    <!-- 2022 -->
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 32px; color: #fbbf24; font-weight: 800;">2022:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 8px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 50%; background: #f59e0b;" title="4,35M viciados"></div>
                        </div>
                        <span style="color: #fde68a; width: 110px; text-align: right;">Vício: 4,35M (2,0x Margem!)</span>
                    </div>
                    <!-- 2026 -->
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span style="width: 32px; color: #f43f5e; font-weight: 900;">2026:</span>
                        <div style="flex-grow: 1; background: rgba(255,255,255,0.05); height: 8px; border-radius: 2px; display: flex; overflow: hidden;">
                            <div style="width: 100%; background: #e11d48;" title="15,88M sem biometria"></div>
                        </div>
                        <span style="color: #fecdd3; width: 110px; text-align: right; font-weight: 900;">Vício: 15,88M (3,6x Margem!)</span>
                    </div>
                </div>
            </div>

            <!-- GRÁFICO 2: OS PILARES DA FRAUDE DE 2026 EM BARRAS -->
            <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 2px; margin-bottom: 2px;">
                    <span style="font-size: 0.58rem; font-weight: 900; color: #38bdf8; font-family: monospace;">GRÁFICO • OS 5 PILARES MATERIAIS DE 2026</span>
                    <span style="background: #0284c7; color: #ffffff; font-size: 0.48rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">AUDITADO</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 2px; font-family: 'JetBrains Mono', monospace; font-size: 0.5rem;">
                    <div>• <strong>15.884.298 Votos Sem Biometria:</strong> <span style="color: #f43f5e;">> 10,8M para Lula</span> (+5,8M de frente s/ bio!)</div>
                    <div>• <strong>9.833.696 Votos no CEFT:</strong> 5.718 trocas (<span style="color: #f43f5e;">+454.544 votos transferidos</span>)</div>
                    <div>• <strong>1.428.650 Votos em Esteira:</strong> &lt; 10s no log (<span style="color: #f43f5e;">82,6% Lula • +812k s/ bio</span>)</div>
                    <div>• <strong>19.159 Seções Canibalizadas (CHK046):</strong> <span style="color: #f43f5e;">+308.190 votos excedentes</span></div>
                    <div>• <strong>116.480 Novos Aptos no 2T (CHK018):</strong> violação direta do Art. 91 da Lei 9.504</div>
                </div>
            </div>

            <!-- CARD PLACAR RECONSTRUÍDO NO VOTO LIMPO -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid #34d399; border-radius: 8px; padding: clamp(0.25rem, 0.4vw, 0.45rem); box-sizing: border-box;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1px;">
                    <span style="font-size: 0.58rem; font-weight: 900; color: #34d399; font-family: monospace;">PLACAR RECONSTRUÍDO (VOTO LIMPO AUDITÁVEL)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.48rem; font-weight: 900; padding: 1px 3px; border-radius: 2px;">LEGÍTIMO</span>
                </div>
                <div style="font-size: 0.52rem; color: #cbd5e1; line-height: 1.25; font-family: 'JetBrains Mono', monospace;">
                    <div>• <strong>2022:</strong> Jair Bolsonaro venceu com <strong>51,05% (+1,07M)</strong> nas UE2020;</div>
                    <div>• <strong>2026:</strong> Flávio Bolsonaro venceu com <strong>51,20% (+1,4M a +2,1M)</strong> no voto limpo!</div>
                </div>
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: RESUMO FORENSE -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 8px; padding: clamp(0.25rem, 0.5vh, 0.45rem) clamp(0.75rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.6rem, 0.72vw, 0.82rem); color: #e2e8f0; line-height: 1.3;">
            ⚖️ <strong>O Fundamento Jurídico de Anulação Plena:</strong> Quando o vício comprovado supera de 2,0x a 3,6x a margem de vitória, o resultado perde toda a presunção de legitimidade. Pelo Artigo 219 (Princípio do Prejuízo) e Artigo 222 do Código Eleitoral, a anulação da eleição é cogente!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.55rem, 0.65vw, 0.7rem); padding: 2px 6px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">NULIDADE TOTAL</span>
    </div>
</div>"""

slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Slide 18 updated with the 11 fraud mechanisms, Ratio Charts, and 5 Pillars successfully!")
