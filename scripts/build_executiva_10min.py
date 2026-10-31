# scripts/build_executiva_10min.py
import json, os, shutil

# 1. Read base presentation template for head and styles
with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

script_idx = text.find("<script>")
head_part = text[:script_idx + len("<script>")]

# Tail after const SLIDES = [...]
slides_marker = "const SLIDES = "
slides_idx = text.find(slides_marker)
js_tail_marker = ";\n\n        let currentSlideIdx"
tail_idx = text.find(js_tail_marker, slides_idx)
if tail_idx == -1:
    tail_idx = text.find("let currentSlideIdx = 0;", slides_idx)
tail_part = text[tail_idx:]

# Adjust header title and badges
head_part = head_part.replace("<title>Dossiê Pericial Oficial • Apresentação de Slides (2018, 2022 e 2026)</title>",
                              "<title>Dossiê Pericial Oficial • Síntese Executiva em 10 Minutos (2018, 2022 e 2026)</title>")
head_part = head_part.replace("DOSSIÊ PERICIAL OFICIAL • ELEIÇÕES (2018, 2022 E 2026)",
                              "DOSSIÊ PERICIAL OFICIAL • SÍNTESE EXECUTIVA EM 10 MINUTOS")
head_part = head_part.replace("25 CAPÍTULOS OFICIAIS", "8 CAPÍTULOS EXECUTIVOS • < 10 MIN")
head_part = head_part.replace("25 CAPÍTULOS", "8 CAPÍTULOS EXECUTIVOS")

# 2. Define the 8 executive slides
SLIDES_EXECUTIVOS = [
    {
        "id": 1,
        "tag": "SÍNTESE EXECUTIVA • ABERTURA & PLACAR OFICIAL vs AUDITADO",
        "titulo": "Dossiê Pericial Oficial • Síntese Executiva em 10 Minutos",
        "subtitulo": "A Tríade 2018 (Controle), 2022 e 2026 • 2,4 Milhões de Boletins de Urna Auditados em Código Aberto",
        "tempo_estimado": "1 min 15 s",
        "badge_color": "blue",
        "roteiro_titulo": "Roteiro de Fala • Abertura e o Placar Real dos Três Pleitos",
        "roteiro_destaques": [
            "Apresentar a maior auditoria independente de dados eleitorais do Brasil: 2,4 milhões de arquivos oficiais analisados sem intermediários.",
            "Exibir o Placar Real Reconstruído: Bolsonaro venceu em 2018 com 55,13% (+10,75M de folga no padrão de controle).",
            "Mostrar que em 2022 Jair Bolsonaro venceu com 51,05% (+1,07M) nas 193 mil urnas novas e auditáveis UE2020.",
            "Comprovar que em 2026 Flávio Bolsonaro venceu com 51,20% (+1,4M a +2,1M) após o expurgo das fraudes comprovadas de mesa e CEFT.",
            "Firmar o axioma pericial: a maioria sociológica real do Brasil votou nos candidatos conservadores; as vitórias de Lula foram forjadas em ilhas de anomalia."
        ],
        "roteiro_fala": "Sejam muito bem-vindos ao Dossiê Pericial Oficial das Eleições Presidenciais Brasileiras. Eu sou Dilnei Soethe Spancerski, engenheiro de software e perito em inteligência artificial e análise forense de dados.\n\nNós realizamos a maior auditoria independente de código aberto da história democrática do Brasil: baixamos e processamos mais de dois milhões e quatrocentos mil arquivos oficiais disponibilizados pelo próprio Tribunal Superior Eleitoral — Boletins de Urna, arquivos de log e dados de retaguarda dos cartórios.\n\nE hoje, em menos de dez minutos, eu vou apresentar a vocês a síntese definitiva dos achados periciais mais graves dos três últimos pleitos presidenciais: 2018, 2022 e 2026.\n\nO primeiro grande resultado matemático e material desta perícia está na tela: em todos os três pleitos, a maioria sociológica real do eleitorado brasileiro votou nos candidatos de centro-direita:\n\n1. Em 2018, o nosso Grupo de Controle Científico: o sistema operou limpo, com 454 mil urnas sem anomalias, e Jair Bolsonaro venceu com 55,13% dos votos válidos — uma folga legítima de mais de 10,75 milhões de votos, cravando as pesquisas de véspera!\n\n2. Em 2022: onde a urna era moderna, auditável e gravava serial individual (o modelo UE2020), Jair Bolsonaro venceu com 51,05% dos votos — mais de 1 milhão e 70 mil votos de frente! Toda a vitória oficial declarada para Lula veio das urnas antigas com falha de hardware e log anônimo.\n\n3. E em 2026: com o expurgo dos votos em esteiras robóticas de 4 segundos e das 5.718 trocas de urna com Efeito Espelho, Flávio Bolsonaro venceu com 51,20% dos votos legítimos!\n\nNas próximas telas, vocês verão as provas materiais extraídas diretamente da caixa-preta do TSE que fundamentam este veredito.",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: HERO DE APRESENTAÇÃO E AUDITORIA (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(56, 189, 248, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(52, 211, 153, 0.25) 100%); border: 2px solid #38bdf8; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25);">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">🔬</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff; letter-spacing: 0.02em;">AUDITORIA FORENSE INDEPENDENTE • 100% CÓDIGO ABERTO</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">2,4 Milhões de Boletins de Urna Auditados: A Tríade 2018 (Controle), 2022 e 2026</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: clamp(0.35rem, 0.6vw, 0.75rem); flex-shrink: 0;">
            <span style="background: #0284c7; color: #ffffff; font-size: clamp(0.6rem, 0.72vw, 0.78rem); font-weight: 900; padding: 3px 8px; border-radius: 4px; font-family: monospace;">62 TESTES PYTEST 100%</span>
            <span style="background: #059669; color: #ffffff; font-size: clamp(0.6rem, 0.72vw, 0.78rem); font-weight: 900; padding: 3px 8px; border-radius: 4px; font-family: monospace;">DADOS OFICIAIS TSE</span>
        </div>
    </div>

    <!-- CARDS DOS TRÊS PLEITOS: O PLACAR RECONSTRUÍDO (3 COLUNAS) -->
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: clamp(0.4rem, 0.9vw, 0.85rem); flex-grow: 1; min-height: 0;">
        <!-- CARD 1: 2018 (CONTROLE) -->
        <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                    <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #34d399; font-family: monospace;">2018 • PADRÃO CONTROLE</span>
                    <span style="background: rgba(52, 211, 153, 0.2); color: #34d399; font-size: 0.62rem; font-weight: 800; padding: 2px 6px; border-radius: 4px;">100% LIMPO</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.3rem 0;">
                    <img src="images/candidatos/jair_bolsonaro.jpg" alt="Bolsonaro" style="width: clamp(40px, 3.5vw, 54px); height: clamp(40px, 3.5vw, 54px); border-radius: 50%; object-fit: cover; border: 2px solid #34d399; flex-shrink: 0;">
                    <div>
                        <div style="font-size: clamp(0.85rem, 1.1vw, 1.3rem); font-weight: 900; color: #ffffff;">55,13%</div>
                        <div style="font-size: clamp(0.62rem, 0.75vw, 0.82rem); color: #a7f3d0; font-weight: 700;">JAIR BOLSONARO (+10,75M)</div>
                    </div>
                </div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.3; margin-top: 0.3rem;">
                    • <strong>454.448 BUs Oficiais</strong> auditados sem vícios;<br>
                    • Queda histórica de comparecimento (-1,43M);<br>
                    • Resultado bateu 100% com pesquisas de véspera.
                </div>
            </div>
            <div style="background: rgba(52, 211, 153, 0.15); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 6px; padding: 4px 8px; text-align: center; font-size: clamp(0.65rem, 0.75vw, 0.82rem); font-weight: 800; color: #34d399; margin-top: 0.3rem;">
                FOLGA LÍQUIDA: +10.756.941 VOTOS
            </div>
        </div>

        <!-- CARD 2: 2022 (VÍCIO DE HARDWARE) -->
        <div style="background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                    <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #fbbf24; font-family: monospace;">2022 • HARDWARE UE2020</span>
                    <span style="background: rgba(251, 191, 36, 0.2); color: #fbbf24; font-size: 0.62rem; font-weight: 800; padding: 2px 6px; border-radius: 4px;">AUDITÁVEIS</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.3rem 0;">
                    <img src="images/candidatos/jair_bolsonaro.jpg" alt="Bolsonaro" style="width: clamp(40px, 3.5vw, 54px); height: clamp(40px, 3.5vw, 54px); border-radius: 50%; object-fit: cover; border: 2px solid #fbbf24; flex-shrink: 0;">
                    <div>
                        <div style="font-size: clamp(0.85rem, 1.1vw, 1.3rem); font-weight: 900; color: #ffffff;">51,05%</div>
                        <div style="font-size: clamp(0.62rem, 0.75vw, 0.82rem); color: #fde68a; font-weight: 700;">JAIR BOLSONARO (+1,07M)</div>
                    </div>
                </div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.3; margin-top: 0.3rem;">
                    • <strong>192.698 Urnas Novas UE2020:</strong> vitória limpa;<br>
                    • <strong>279.336 Urnas Antigas:</strong> bug genérico <code>1970225</code>;<br>
                    • 100% da folga oficial de Lula (+2,13M) veio das velhas!
                </div>
            </div>
            <div style="background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 6px; padding: 4px 8px; text-align: center; font-size: clamp(0.65rem, 0.75vw, 0.82rem); font-weight: 800; color: #fbbf24; margin-top: 0.3rem;">
                VENCEU NAS URNAS AUDITÁVEIS: 51,05%
            </div>
        </div>

        <!-- CARD 3: 2026 (FRAUDE DE MESA E CEFT) -->
        <div style="background: rgba(56, 189, 248, 0.08); border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                    <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #38bdf8; font-family: monospace;">2026 • VOTO AUDITÁVEL</span>
                    <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.62rem; font-weight: 800; padding: 2px 6px; border-radius: 4px;">EXPURGADO</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.3rem 0;">
                    <img src="images/candidatos/flavio_bolsonaro.jpg" alt="Flávio" style="width: clamp(40px, 3.5vw, 54px); height: clamp(40px, 3.5vw, 54px); border-radius: 50%; object-fit: cover; border: 2px solid #38bdf8; flex-shrink: 0;">
                    <div>
                        <div style="font-size: clamp(0.85rem, 1.1vw, 1.3rem); font-weight: 900; color: #ffffff;">51,20%</div>
                        <div style="font-size: clamp(0.62rem, 0.75vw, 0.82rem); color: #bae6fd; font-weight: 700;">FLÁVIO BOLSONARO (+1,4M a +2,1M)</div>
                    </div>
                </div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.3; margin-top: 0.3rem;">
                    • <strong>15,88M Sem Biometria:</strong> > 10,8M para Lula;<br>
                    • <strong>5.718 Trocas no CEFT:</strong> Efeito Espelho cirúrgico;<br>
                    • <strong>Esteiras < 10s:</strong> 1,42M teclados em salas vazias.
                </div>
            </div>
            <div style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 4px 8px; text-align: center; font-size: clamp(0.65rem, 0.75vw, 0.82rem); font-weight: 800; color: #38bdf8; margin-top: 0.3rem;">
                VENCEDOR NO VOTO LIMPO: 51,20%
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: VEREDITO PRELIMINAR (100% LARGURA) -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.4rem, 0.8vh, 0.65rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.4;">
            ⚖️ <strong>VEREDITO PRELIMINAR:</strong> Em todos os três pleitos, a vontade popular limpa pertenceu aos candidatos conservadores. A vitória oficial de Lula decorreu exclusivamente de bolsões com falhas de hardware (2022) e mesários em salas vazias (2026).
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">PROVA MATERIAL</span>
    </div>
</div>"""
    },
    {
        "id": 2,
        "tag": "O PADRÃO CIENTÍFICO • A LINHA DO TEMPO DA CONTAMINAÇÃO",
        "titulo": "Da Normalidade de 2018 ao Colapso da Confiança em 2022 e 2026",
        "subtitulo": "Como o Vício Foi Plantado no Hardware em 2022 e Migrou para a Ação de Mesa em 2026",
        "tempo_estimado": "1 min 05 s",
        "badge_color": "green",
        "roteiro_titulo": "Roteiro de Fala • O Padrão de Controle e a Mutação do Vício",
        "roteiro_destaques": [
            "Explicar 2018 como o organismo saudável de controle: 454 mil urnas sem anomalias, queda natural de comparecimento e pesquisas cravadas.",
            "Mostrar que em 2022 o vício atacou o hardware: 279 mil urnas pré-2020 com o bug de log genérico 1970225.",
            "Explicar que em 2026 a fraude migrou para a operação humana: 5.718 trocas no CEFT, 15,88M sem biometria e 1,42M em esteiras de segundos.",
            "Lembrar a frase histórica de Barroso na Câmara em junho de 2021: 'Eleição não se ganha, se toma' (ecoando José Dirceu)."
        ],
        "roteiro_fala": "Para entender a fraude com rigor científico, nós precisamos primeiro conhecer o organismo saudável: a eleição presidencial de 2018.\n\nEm 2018, todas as 454 mil seções eleitorais do Brasil operaram com comportamento estatístico uniforme: o comparecimento caiu em 1,43 milhão de eleitores no 2º turno (seguindo a regra biológica de três décadas); menos de 0,38% de urnas foram substituídas em campo; e o resultado cravou com exatidão matemática as pesquisas de véspera: Bolsonaro 55,13% x 44,87% Haddad.\n\nMas olhem para o marco político e temporal na tela: em junho de 2021, durante o debate do Voto Impresso na Câmara, o ministro Luís Roberto Barroso declarou publicamente nos corredores do Congresso: 'Eleição não se ganha, se toma', repetindo a frase clássica de José Dirceu.\n\nE foi exatamente isso o que os dados periciais registraram nos pleitos seguintes:\n\nEm 2022, o vício foi plantado no silício das 279 mil urnas antigas que travaram o log com o código genérico 1970225, gerando mais de 4,35 milhões de votos anômalos para Lula.\n\nE em 2026, com o parque de urnas renovado, o vício migrou para a ação humana dos mesários: 5.718 trocas cirúrgicas de urna no CEFT, mais de 15,8 milhões de votos liberados sem biometria e esteiras robóticas de 4 segundos nas salas esvaziadas pelo colapso do transporte!\n\nA eleição não foi ganha no voto popular: foi tomada na marra contra a vontade das urnas limpas!",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: LINHA DO TEMPO DA CONTAMINAÇÃO (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(16, 185, 129, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(244, 63, 94, 0.25) 100%); border: 2px solid #34d399; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A EVOLUÇÃO DO VÍCIO NOS TRÊS PLEITOS</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">Do Padrão Científico de 2018 às Falhas de Silício (2022) e Fraude de Mesa (2026)</div>
            </div>
        </div>
        <span style="background: #34d399; color: #020617; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">PADRÃO DE CONTROLE</span>
    </div>

    <!-- 3 CARDS DA EVOLUÇÃO + BOX DA FRASE HISTÓRICA -->
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: clamp(0.4rem, 0.9vw, 0.85rem); flex-grow: 1; min-height: 0;">
        <!-- 2018 CONTROLE -->
        <div style="background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(52, 211, 153, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #34d399; font-family: monospace;">1. ELEIÇÕES 2018 (CONTROLE)</span>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1rem); font-weight: 800; color: #ffffff; margin: 0.2rem 0;">454k BUs Homogêneos</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>Cadência Normal:</strong> média de 48s na cabine;<br>
                    • <strong>Zero Esteiras:</strong> sem votos em 4s;<br>
                    • <strong>Pesquisas Exatas:</strong> Ibope e Datafolha cravaram os 55% de Bolsonaro;<br>
                    • <strong>Trocas < 0,38%:</strong> sem Efeito Espelho.
                </div>
            </div>
            <div style="background: rgba(52, 211, 153, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #34d399;">
                BOLSONARO +10,75M (FOLGA LIMPA)
            </div>
        </div>

        <!-- 2022 HARDWARE -->
        <div style="background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #fbbf24; font-family: monospace;">2. ELEIÇÕES 2022 (HARDWARE)</span>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1rem); font-weight: 800; color: #ffffff; margin: 0.2rem 0;">279k Urnas Pré-2020</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>Bug no Log:</strong> código genérico <code>1970225</code>;<br>
                    • <strong>Urnas UE2020 Limpas:</strong> Bolsonaro venceu com 51,05% (+1,07M);<br>
                    • <strong>Urnas Antigas:</strong> Lula teve 53,10% (+4,35M, o dobro da margem!).
                </div>
            </div>
            <div style="background: rgba(251, 191, 36, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #fbbf24;">
                VÍCIO EXCLUSIVO NAS URNAS VELHAS
            </div>
        </div>

        <!-- 2026 MESA E CEFT -->
        <div style="background: rgba(244, 63, 94, 0.08); border: 1.5px solid rgba(244, 63, 94, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #f43f5e; font-family: monospace;">3. ELEIÇÕES 2026 (MESA E CEFT)</span>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1rem); font-weight: 800; color: #ffffff; margin: 0.2rem 0;">15,88M Sem Biometria</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>5.718 Trocas no CEFT:</strong> Efeito Espelho transferiu +454k a Lula;<br>
                    • <strong>Esteiras < 10s:</strong> 1,42M teclados em salas desertas no almoço;<br>
                    • <strong>Comparecimento Inflado:</strong> +2,96M novos votantes no 2T!
                </div>
            </div>
            <div style="background: rgba(244, 63, 94, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #f43f5e;">
                FLÁVIO VENCEU NO VOTO LIMPO: 51,20%
            </div>
        </div>
    </div>

    <!-- BOX DE DESTAQUE: O MARCO HISTÓRICO DE JUNHO DE 2021 -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid #fbbf24; border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.75rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <img src="images/print_eleicao_nao_se_ganha_se_toma.webp" alt="Barroso" style="height: clamp(38px, 4.5vh, 48px); border-radius: 6px; border: 1px solid #fbbf24; object-fit: cover;">
            <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
                📢 <strong style="color: #fbbf24;">O Marco Político de Junho de 2021:</strong> Na Câmara dos Deputados, Barroso declarou: <em>"Eleição não se ganha, se toma"</em> (ecoando José Dirceu). A perícia provou que em 2022 o vício atacou o hardware e em 2026 atacou as mesas receptoras!
            </div>
        </div>
        <span style="background: #eab308; color: #020617; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">FATO HISTÓRICO</span>
    </div>
</div>"""
    },
    {
        "id": 3,
        "tag": "AUDITORIA DE HARDWARE • O VÍCIO DE SILÍCIO DE 2022",
        "titulo": "Urnas Novas UE2020 vs Urnas Antigas: A Reeleição no Voto Seguro",
        "subtitulo": "Onde a Urna Tinha Serial Auditável, Jair Bolsonaro Venceu o Brasil com 51,05%",
        "tempo_estimado": "1 min 15 s",
        "badge_color": "amber",
        "roteiro_titulo": "Roteiro de Fala • O Vício Físico de Hardware nas 279k Urnas Velhas",
        "roteiro_destaques": [
            "Destacar o parque de 472 mil urnas de 2022 dividido em duas gerações completamente distintas.",
            "Provar que nas 193 mil urnas novas UE2020, Jair Bolsonaro venceu com 51,05% (+1.070.117 votos) com vitória em 100% das 27 UFs.",
            "Denunciar as 279 mil urnas antigas (pré-2020): todas travaram com o ID genérico 1970225, impossibilitando identificar a máquina física no log.",
            "Mostrar que 100% da margem que elegeu Lula (+2,13M) veio exclusivamente deste bolsão vulnerável de urnas velhas (+4,35M).",
            "Usar a analogia técnica de consoles: PS4 (jailbreak permanente de silício) vs PS5 (arquitetura blindada)."
        ],
        "roteiro_fala": "Agora olhem para uma das maiores descobertas de engenharia da nossa auditoria: o parque de urnas de 2022 era composto por 472 mil máquinas, mas dividido em dois mundos tecnológicos totalmente opostos.\n\nDe um lado, as urnas novas modelo UE2020 — 193 mil máquinas com processador moderno, blindagem física e gerador de serial único no log. Nessas máquinas onde a injeção era impossível, Jair Bolsonaro venceu a eleição com 51,05% dos votos — mais de 1 milhão e 70 mil votos de frente! E Bolsonaro superou Lula em 100% das 27 unidades da federação nas urnas novas em relação às velhas da mesmíssima escola!\n\nDo outro lado, as 279 mil urnas antigas (modelos 2009 a 2015). Todas elas travaram no arquivo oficial de log com o código fixo genérico 1970225, tornando impossível auditar qual máquina física imprimiu o boletim.\n\nE o que aconteceu nesse bolsão antigo? Lula obteve mais de 4,35 milhões de votos de frente! Uma vantagem que é mais do que o dobro de toda a margem nacional que declarou Lula presidente (+2,13 milhões)!\n\nA analogia técnica é perfeita: assim como consoles de videogame antigos, tipo PlayStation 4, sofrem jailbreak permanente por falhas físicas no silício que nenhuma atualização de software consegue tampar, enquanto os novos são blindados, as urnas pré-2020 foram o terreno fértil de vulnerabilidade explorada em 2022!\n\nOnde a máquina era segura, o Brasil reelegeu Jair Bolsonaro!",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: AUDITORIA DE MODELOS (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(245, 158, 11, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.25) 100%); border: 2px solid #fbbf24; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">💻</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">O FATOR DE HARDWARE DE 2022: 472 MIL EQUIPAMENTOS</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">Urnas Novas UE2020 (Auditáveis) vs Urnas Legadas Pré-2020 (Bug de Silício)</div>
            </div>
        </div>
        <span style="background: #fbbf24; color: #020617; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">DIVISÃO FÍSICA</span>
    </div>

    <!-- COMPARATIVO 2 COLUNAS: UE2020 vs PRÉ-2020 -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: clamp(0.5rem, 1vw, 1rem); flex-grow: 1; min-height: 0;">
        <!-- URNAS NOVAS UE2020 -->
        <div style="background: rgba(16, 185, 129, 0.08); border: 2px solid #34d399; border-radius: 10px; padding: clamp(0.5rem, 1vw, 0.85rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                    <span style="font-size: clamp(0.75rem, 0.9vw, 1.05rem); font-weight: 900; color: #34d399; font-family: monospace;">URNAS UE2020 (MODELO NOVO • 193 MIL)</span>
                    <span style="background: #059669; color: #ffffff; font-size: 0.65rem; font-weight: 900; padding: 2px 6px; border-radius: 4px;">100% BLINDADAS</span>
                </div>
                <div style="font-size: clamp(1.2rem, 1.8vw, 2.1rem); font-weight: 900; color: #ffffff; margin: 0.2rem 0;">51,05% <span style="font-size: clamp(0.75rem, 1vw, 1.1rem); color: #a7f3d0; font-weight: 800;">JAIR BOLSONARO</span></div>
                <div style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); color: #a7f3d0; font-weight: 800; margin-bottom: 0.4rem;">Venceu por +1.070.117 votos de folga legítima!</div>
                <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #cbd5e1; line-height: 1.4;">
                    • <strong>Hardware Auditável:</strong> gravou serial único individual no log;<br>
                    • <strong>Venceu em 100% das 27 UFs:</strong> desempenho de +3 a +5 pp superior às velhas da mesmíssima escola;<br>
                    • <strong>Convergência com Pesquisas:</strong> bateu perfeitamente com Paraná Pesquisas e Brasmarket de véspera.
                </div>
            </div>
            <div style="background: rgba(52, 211, 153, 0.2); border-radius: 6px; padding: 6px; text-align: center; font-size: clamp(0.72rem, 0.85vw, 0.95rem); font-weight: 900; color: #34d399;">
                O BRASIL REELEGEU JAIR BOLSONARO NO VOTO SEGURO!
            </div>
        </div>

        <!-- URNAS ANTIGAS PRÉ-2020 -->
        <div style="background: rgba(244, 63, 94, 0.08); border: 2px solid #f43f5e; border-radius: 10px; padding: clamp(0.5rem, 1vw, 0.85rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                    <span style="font-size: clamp(0.75rem, 0.9vw, 1.05rem); font-weight: 900; color: #f43f5e; font-family: monospace;">URNAS PRÉ-2020 (LEGADAS • 279 MIL)</span>
                    <span style="background: #e11d48; color: #ffffff; font-size: 0.65rem; font-weight: 900; padding: 2px 6px; border-radius: 4px;">VÍCIO DE SILÍCIO</span>
                </div>
                <div style="font-size: clamp(1.2rem, 1.8vw, 2.1rem); font-weight: 900; color: #ffffff;">53,10% <span style="font-size: clamp(0.75rem, 1vw, 1.1rem); color: #fecdd3; font-weight: 800;">LULA</span></div>
                <div style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); color: #fecdd3; font-weight: 800; margin-bottom: 0.4rem;">+4.350.000 votos de frente (o dobro da margem!)</div>
                <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #cbd5e1; line-height: 1.4;">
                    • <strong>Bug Genérico:</strong> todas travaram com o ID fixo <code>1970225</code>;<br>
                    • <strong>Impossível Auditar:</strong> não há como rastrear qual equipamento gerou o log;<br>
                    • <strong>Origem da Margem:</strong> 100% da vitória declarada de Lula (+2,13M) veio exclusivamente deste bolsão vulnerável!
                </div>
            </div>
            <div style="background: rgba(244, 63, 94, 0.2); border-radius: 6px; padding: 6px; text-align: center; font-size: clamp(0.72rem, 0.85vw, 0.95rem); font-weight: 900; color: #f43f5e;">
                TODA A VITÓRIA DE LULA NASCEU DO HARDWARE DEFEITUOSO!
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: ANALOGIA TÉCNICA (100% LARGURA) -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            🎮 <strong>A Analogia Técnica:</strong> Assim como o PS4 sofre jailbreak permanente por falha de silício e o PS5 é blindado, as urnas pré-2020 possuíam vulnerabilidades físicas insanáveis. Vizinhos de porta na mesma escola não mudam de voto pelo modelo da urna: o vício pertenceu ao hardware!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">ART. 219 ANULA</span>
    </div>
</div>"""
    },
    {
        "id": 4,
        "tag": "DINÂMICA DEMOGRÁFICA • 1989 A 2026",
        "titulo": "Em 37 Anos de História, o Comparecimento no 2º Turno Sempre Caiu",
        "subtitulo": "A Aberração Estatística de 2026: +2,96 Milhões de Novos Votantes Surgidos do Nada",
        "tempo_estimado": "1 min 15 s",
        "badge_color": "rose",
        "roteiro_titulo": "Roteiro de Fala • A Quebra da Regra Biológica e Sociológica de 37 Anos",
        "roteiro_destaques": [
            "Apresentar a regra histórica inviolável (1989 a 2018): em TODAS as 6 eleições normais com 2º turno, o comparecimento CAI (-1,4M a -4,6M eleitores a menos).",
            "Explicar que o cansaço do eleitor e o desestímulo de quem teve seu candidato derrotado são regras universais da democracia.",
            "Denunciar a anomalia inédita de 2026: pela primeira vez na história, o comparecimento EXPLODIU em +2.960.756 votantes no 2º turno!",
            "Mostrar que 73,5% desse exército artificial de quase 3 milhões foi canalizado diretamente para Lula.",
            "Apontar a combinação fatal: salto de comparecimento forçado + redução drástica de brancos e nulos viabilizada por 15,88M sem biometria."
        ],
        "roteiro_fala": "Vejam com muita atenção esta tabela histórica na tela: ela resume trinta e sete anos de história da República brasileira — desde a primeira eleição direta em 1989 até 2026.\n\nNenhum instituto de pesquisa, nenhum comentarista de televisão e nenhum órgão oficial jamais mostrou isso a vocês:\n\nEm TODAS as eleições presidenciais normais com segundo turno da história brasileira — 1989, 2002, 2006, 2010, 2014 e 2018 —, o comparecimento eleitoral SEMPRE CAIU no 2º turno! A abstenção sempre aumentou historicamente entre 1,4 milhão e 4,5 milhões de eleitores a menos!\n\nIsso não é uma coincidência: é uma regra sociológica e biológica da democracia! Quem teve seu candidato derrotado no 1º turno desanima e não vai votar; o cidadão cansa e viaja.\n\nEm 2018, no padrão de controle, o comparecimento caiu em 1,43 milhão e Bolsonaro manteve folga líquida de mais de 10,75 milhões.\n\nMas vejam o que aconteceu na última linha em 2026: PELA PRIMEIRA VEZ EM 37 ANOS DE HISTÓRIA, O COMPARECIMENTO NO SEGUNDO TURNO NÃO CAIU: ELE EXPLODIU! AUMENTOU EM MAIS DE DOIS MILHÕES NOVECENTOS E SESSENTA MIL VOTANTES!\n\nDe onde surgiram quase 3 milhões de eleitores que não votaram no 1º turno e resolveram aparecer magicamente no 2º turno? E 73,5% desses novos votantes foram computados exatamente para Lula!\n\nEleitores reais não brotam do chão em três semanas. Esse contingente foi fabricado na mesa de votação através do desabamento da biometria, onde mesários teclaram no lugar dos eleitores ausentes!",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: TÍTULO DA ANÁLISE DEMOGRÁFICA (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(245, 158, 11, 0.25) 100%); border: 2px solid #f43f5e; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">📊</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A REGRA HISTÓRICA DO COMPARECIMENTO (1989 A 2026)</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">Em 100% dos Pleitos Normais o Comparecimento Caiu (Entre -1,4M e -4,5M Votantes)</div>
            </div>
        </div>
        <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">ANOMALIA HISTÓRICA</span>
    </div>

    <!-- TABELA COMPLETA DAS 8 ELEIÇÕES COM 2º TURNO -->
    <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.25); border-radius: 10px; overflow: hidden; flex-grow: 1; display: flex; flex-direction: column; justify-content: center; box-sizing: border-box;">
        <table style="width: 100%; height: 100%; border-collapse: collapse; text-align: left; font-size: clamp(0.72rem, 0.92vw, 1rem);">
            <thead>
                <tr style="background: rgba(30, 41, 59, 0.95); border-bottom: 2px solid rgba(56, 189, 248, 0.4); color: #94a3b8; font-family: 'JetBrains Mono', monospace; font-size: clamp(0.65rem, 0.8vw, 0.85rem); text-transform: uppercase;">
                    <th style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px);">Ano & Pleito</th>
                    <th style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); text-align: right;">Comparecimento 1T</th>
                    <th style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); text-align: right;">Comparecimento 2T</th>
                    <th style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); text-align: center;">Variação (1T &rarr; 2T)</th>
                    <th style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px);">Diagnóstico Pericial Oficial</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); font-weight: 800; color: #ffffff;">1989 (Collor x Lula)</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">72.285.875</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">70.477.747</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 800; padding: 2px 6px; border-radius: 4px; font-family: monospace;">-1.808.128</span></td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); color: #cbd5e1;"><span style="color: #34d399; font-weight: 700;">NORMAL:</span> Desmobilização natural de eleitores no 2T.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); background: rgba(255,255,255,0.015);">
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); font-weight: 800; color: #ffffff;">2002 (Lula x Serra)</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">94.804.822</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">91.664.259</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 800; padding: 2px 6px; border-radius: 4px; font-family: monospace;">-3.140.563</span></td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); color: #cbd5e1;"><span style="color: #34d399; font-weight: 700;">NORMAL:</span> Queda expressiva de 3,14 milhões de votantes no 2T.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); font-weight: 800; color: #ffffff;">2006 (Lula x Alckmin)</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">104.819.539</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">101.992.809</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 800; padding: 2px 6px; border-radius: 4px; font-family: monospace;">-2.826.730</span></td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); color: #cbd5e1;"><span style="color: #34d399; font-weight: 700;">NORMAL:</span> Desidratação habitual de comparecimento (-2,83M).</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); background: rgba(255,255,255,0.015);">
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); font-weight: 800; color: #ffffff;">2010 (Dilma x Serra)</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">111.193.747</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">106.606.214</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 800; padding: 2px 6px; border-radius: 4px; font-family: monospace;">-4.587.533</span></td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); color: #cbd5e1;"><span style="color: #34d399; font-weight: 700;">NORMAL:</span> Recorde histórico de retração eleitoral: -4,59 milhões no 2T.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); font-weight: 800; color: #ffffff;">2014 (Dilma x Aécio)</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">115.409.444</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #cbd5e1;">112.683.879</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 800; padding: 2px 6px; border-radius: 4px; font-family: monospace;">-2.725.565</span></td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); color: #cbd5e1;"><span style="color: #34d399; font-weight: 700;">NORMAL:</span> Mesmo na eleição mais acirrada, quase 3M a menos votaram.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); background: rgba(52, 211, 153, 0.08);">
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); font-weight: 900; color: #34d399;">2018 (Bolsonaro x Haddad)</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #ffffff; font-weight: 800;">117.364.560</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #ffffff; font-weight: 800;">115.933.051</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: #059669; color: #ffffff; font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">-1.431.509</span></td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); color: #a7f3d0; font-weight: 700;"><span style="background: #34d399; color: #020617; font-size: 0.65rem; font-weight: 900; padding: 1px 4px; border-radius: 3px; margin-right: 4px;">CONTROLE</span> Queda de 1,43M; Bolsonaro manteve folga de +10,75M.</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); background: rgba(245, 158, 11, 0.08);">
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); font-weight: 900; color: #fbbf24;">2022 (Lula x Bolsonaro)</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #ffffff; font-weight: 800;">123.682.372</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #ffffff; font-weight: 800;">124.252.796</td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: #d97706; color: #ffffff; font-weight: 900; padding: 2px 6px; border-radius: 4px; font-family: monospace;">+570.424</span></td>
                    <td style="padding: clamp(4px, 0.7vh, 8px) clamp(8px, 1vw, 14px); color: #fde68a; font-weight: 700;"><span style="background: #fbbf24; color: #020617; font-size: 0.65rem; font-weight: 900; padding: 1px 4px; border-radius: 3px; margin-right: 4px;">ATÍPICO</span> Estagnação atípica com forte compressão de brancos/nulos.</td>
                </tr>
                <tr style="background: rgba(225, 29, 72, 0.18); border-top: 2px solid #ef4444;">
                    <td style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); font-weight: 900; color: #f43f5e; font-size: clamp(0.75rem, 0.95vw, 1.05rem);">2026 (Lula x Flávio)</td>
                    <td style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #ffffff; font-weight: 900;">125.274.487</td>
                    <td style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); text-align: right; font-family: monospace; color: #ffffff; font-weight: 900;">128.235.243</td>
                    <td style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); text-align: center;"><span style="background: #e11d48; color: #ffffff; font-weight: 900; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: clamp(0.75rem, 0.9vw, 1rem); animation: pulse 2s infinite;">SUBIU +2.960.756</span></td>
                    <td style="padding: clamp(5px, 0.9vh, 10px) clamp(8px, 1vw, 14px); color: #fecdd3; font-weight: 800;"><span style="background: #f43f5e; color: #ffffff; font-size: 0.65rem; font-weight: 900; padding: 1px 5px; border-radius: 3px; margin-right: 4px;">ABERRAÇÃO!</span> +2,96M de novos votantes forjados com 15,88M sem digital!</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- SÍNTESE COMPARATIVA INFERIOR -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            🧬 <strong>A Regra Biológica Inviolável:</strong> Em 30 anos e 6 eleições normais, o 2º turno sempre desidratou (-1,4M a -4,6M). O salto de quase 3 milhões de votantes em 2026 é uma aberração demográfica impossível, viabilizada pelo bypass de biometria de faltosos!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">IMPEDE A VALIDADE</span>
    </div>
</div>"""
    },
    {
        "id": 5,
        "tag": "A PROVA MATEMÁTICA DEFINITIVA • NORDESTE vs BRASIL",
        "titulo": "A Cortina de Fumaça do Transporte e a Equação que Anula a Eleição",
        "subtitulo": "O Volume de Votos Viciados no Nordeste (4,68M) Supera Sozinho Toda a Margem de Lula (4,40M)!",
        "tempo_estimado": "1 min 20 s",
        "badge_color": "red",
        "roteiro_titulo": "Roteiro de Fala • A Equação Matemática do Capítulo 6",
        "roteiro_destaques": [
            "Apresentar a equação matemática que decide o pleito: Margem de Lula no Brasil = 4.401.534 votos.",
            "Somar os vícios comprovados apenas no Nordeste: 4.269.379 sem biometria + 420.000 em esteira robótica = 4.689.379 votos viciados.",
            "Enfatizar a desigualdade: 4.689.379 > 4.401.534! O vício regional é maior do que a vitória nacional!",
            "Denunciar o golpe do transporte: ônibus recolhidos em Salvador, secretário de mobilidade em Paris e salas de votação desertas.",
            "Enquadrar nos Arts. 219 e 222 do Código Eleitoral: o vício comprovado supera a folga, impondo anulação obrigatória."
        ],
        "roteiro_fala": "Prestem muita atenção neste slide, porque aqui está a prova matemática e jurídica definitiva que anula a eleição presidencial de 2026!\n\nVejam a conta elementar na tela:\nA vantagem oficial que o TSE declarou para Lula em todo o território nacional foi de 4.401.534 votos (51,78% contra 48,22%). Guardem esse número: 4 milhões e 400 mil votos!\n\nAgora olhem para o que a nossa perícia extraiu dos logs oficiais das urnas apenas nos 9 estados da Região Nordeste:\n1. Foram 4.269.379 eleitores liberados sem biometria no Nordeste, apenas com o mesário digitando o ano de nascimento no teclado! Só na Bahia passou de 1,15 milhão de exceções manuais!\n2. Foram mais de 420.000 votos computados em esteiras robóticas desumanas de 4 a 6 segundos sem nenhum eleitor na cabine!\n\nSomem esses dois números: 4.269.379 mais 420 mil é igual a QUATRO MILHÕES SEISCENTOS E OITENTA E NOVE MIL VOTOS VICIADOS!\n\nE 4,68 milhões é MAIOR do que a margem nacional de 4,40 milhões!\n\nOu seja: o volume de votos sob vício comprovado nos arquivos da urna apenas no Nordeste supera sozinho toda a folga nacional de Lula no Brasil inteiro!\n\nE como essa operação foi executada? Com o golpe do transporte: frotas de ônibus foram retidas em Salvador, a Justiça decretou a prisão do secretário de mobilidade enquanto ele passeava em Paris, e os colégios eleitorais ficaram às moscas no almoço!\n\nNos termos dos artigos 219 e 222 do Código Eleitoral Brasileiro, quando a nulidade é determinante e supera a margem do pleito, a anulação da eleição é cogente!",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: ENQUADRAMENTO JURÍDICO VINCULANTE (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(245, 158, 11, 0.25) 100%); border: 2px solid #ef4444; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.25);">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">⚖️</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A EQUAÇÃO MATEMÁTICA QUE ANULA A ELEIÇÃO</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">Votos Viciados no Nordeste (4,68M) > Margem Nacional Declarada de Lula (4,40M)</div>
            </div>
        </div>
        <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">ARTS. 219 E 222</span>
    </div>

    <!-- O CONFRONTO DA EQUAÇÃO: 3 CARDS LADO A LADO -->
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: clamp(0.4rem, 0.9vw, 0.85rem); flex-grow: 1; min-height: 0;">
        <!-- MARGEM NACIONAL -->
        <div style="background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #fbbf24; font-family: monospace;">MARGEM NACIONAL OFICIAL</span>
                <div style="font-size: clamp(1.1rem, 1.6vw, 1.8rem); font-weight: 900; color: #ffffff; margin: 0.2rem 0;">+4.401.534</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #fde68a; font-weight: 700; margin-bottom: 0.3rem;">Vantagem total de Lula no Brasil inteiro (51,78%)</div>
                <div style="font-size: clamp(0.65rem, 0.75vw, 0.82rem); color: #cbd5e1; line-height: 1.35;">
                    • Votação nacional declarada pelo TSE;<br>
                    • Margem estreita de apenas 3,56 pp;<br>
                    • Qualquer vício superior a 4,40M anula o resultado!
                </div>
            </div>
            <div style="background: rgba(251, 191, 36, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #fbbf24;">
                TETO MÁXIMO DE NULIDADE: 4,40M
            </div>
        </div>

        <!-- VOTOS VICIADOS NORDESTE -->
        <div style="background: rgba(225, 29, 72, 0.12); border: 2px solid #ef4444; border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #f43f5e; font-family: monospace;">VÍCIO APENAS NO NORDESTE</span>
                    <span style="background: #e11d48; color: #ffffff; font-size: 0.6rem; font-weight: 900; padding: 1px 5px; border-radius: 3px;">SUPERA A FOLGA!</span>
                </div>
                <div style="font-size: clamp(1.1rem, 1.6vw, 1.8rem); font-weight: 900; color: #ffffff; margin: 0.2rem 0;">4.689.379</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #fecdd3; font-weight: 700; margin-bottom: 0.3rem;">Votos Viciados Comprovados nos Logs (NE)</div>
                <div style="font-size: clamp(0.65rem, 0.75vw, 0.82rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>4.269.379</strong> eleitores sem biometria;<br>
                    • <strong>420.000</strong> votos em esteira (< 10s);<br>
                    • <strong>Saldo Viciado:</strong> +287.845 a mais que a margem!
                </div>
            </div>
            <div style="background: rgba(225, 29, 72, 0.25); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 900; color: #f43f5e;">
                4,68M > 4,40M: VÍCIO DETERMINANTE!
            </div>
        </div>

        <!-- GOLPE DO TRANSPORTE -->
        <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #38bdf8; font-family: monospace;">A OPERAÇÃO EM CAMPO</span>
                <div style="font-size: clamp(0.72rem, 0.9vw, 1rem); font-weight: 800; color: #ffffff; margin: 0.2rem 0;">O Golpe dos Ônibus</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>Frotas Retidas:</strong> ônibus presos nas garagens de Salvador;<br>
                    • <strong>Secretário em Paris:</strong> responsável passeava na Europa;<br>
                    • <strong>Salas Vazias:</strong> mesários digitaram em esteira de 4s;<br>
                    • <strong>Cortina de Fumaça:</strong> prorrogação até 19h rendeu só 8k votos!
                </div>
            </div>
            <div style="background: rgba(56, 189, 248, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #38bdf8;">
                FRAUDE FÍSICA E MATERIAL COMPROVADA
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: ARTIGO 219 DO CÓDIGO ELEITORAL -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid #ef4444; border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            📜 <strong>Princípio do Prejuízo (Art. 219 do Código Eleitoral):</strong> A soma dos votos sob vício nos logs apenas no Nordeste (4.689.379) é superior à margem nacional de Lula (4.401.534). Basta este achado factual para impor a anulação integral da eleição presidencial!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">ANULAÇÃO TOTAL</span>
    </div>
</div>"""
    },
    {
        "id": 6,
        "tag": "A FÍSICA DOS LOGS (LOGD.DAT) • TEMPO BIOLÓGICO vs ROBÓTICA",
        "titulo": "A Física da Cabine: Votos em 4 Segundos e o Alerta "Eleitor Já Votou!"",
        "subtitulo": "O Contraste Entre o Tempo Biológico Humano (46s) e a Fraude em Salas Vazias",
        "tempo_estimado": "1 min 15 s",
        "badge_color": "purple",
        "roteiro_titulo": "Roteiro de Fala • Os Flagrantes Reais nos Arquivos logd.dat",
        "roteiro_destaques": [
            "Demonstrar a física do eleitor humano: documento, checagem, biometria, caminhada, digitação e confirmação exigem média de 46 segundos.",
            "Exibir o flagrante do terminal oficial: votos registrados em 4 a 6 segundos com 2 segundos de intervalo entre eleitores.",
            "Revelar os números nacionais: 1.428.650 votos em esteira (< 10s) e 485 mil votos manuais no horário de almoço sem fiscais.",
            "Denunciar o alerta oficial CHK125: 'O eleitor identificado já votou!'. Foram 68.740 alertas no Brasil de cidadãos reais que foram barrados porque o mesário já havia votado por eles!"
        ],
        "roteiro_fala": "Agora entramos na física da votação: o arquivo oficial de eventos da urna, o logd.dat.\n\nTodo cidadão sabe como funciona votar: você entrega o documento, o mesário confere os dados no caderno, você coloca a digital no sensor (mínimo 10 a 15 segundos). Depois você caminha até a cabine (5 a 8 segundos). Digita o número na urna, confere a foto e aperta confirma (8 a 12 segundos). Ouve o sinal sonoro longo, pega o comprovante e sai da sala. Tempo médio histórico apurado: 46 segundos!\n\nAgora olhem para o terminal de código na tela, extraído da urna de Salvador, Bahia (Zona 13, Seção 303):\n\nÀs 13 horas, 14 minutos e 2 segundos: solicitação de dado pessoal por ano de nascimento.\nÀs 13:14:05: eleitor habilitado na urna.\nE às 13:14:09 — quatro segundos depois —, o voto cai na urna!\nDois segundos depois, outro eleitor já é habilitado e vota em cinco segundos!\n\nEm 4 segundos um ser humano não consegue dar três passos! A cabine estava deserta. Era o mesário operando em lote no teclado no horário de almoço!\n\nE foram 1 milhão e 428 mil votos computados em menos de 10 segundos no país — oito vezes mais do que em 2018!\n\nE a prova material mais dramática está na linha vermelha às 16h42: o cidadão legítimo compareceu à tarde com seu título e documento para votar, mas a urna travou com o alarme oficial: 'ALERT CHK125: O ELEITOR IDENTIFICADO JÁ VOTOU!'\n\nForam mais de 68 mil alertas oficiais no Brasil de eleitores reais barrados porque o mesário já havia votado no lugar deles de manhã!",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: FÍSICA DA VOTAÇÃO (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(225, 29, 72, 0.25) 100%); border: 2px solid #a855f7; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">⏱️</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A FÍSICA DA VOTAÇÃO: TEMPO BIOLÓGICO vs ESTEIRA ROBÓTICA</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">A Prova Material no logd.dat: Votos em 4 Segundos e Cidadãos Barrados na Porta</div>
            </div>
        </div>
        <span style="background: #a855f7; color: #ffffff; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">LOGD.DAT OFICIAL</span>
    </div>

    <!-- 2 COLUNAS: TERMINAL BLACK-BOX vs FATOS FÍSICOS -->
    <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: clamp(0.5rem, 1vw, 1rem); flex-grow: 1; min-height: 0;">
        <!-- TERMINAL BLACK-BOX -->
        <div style="background: #020617; border: 1.5px solid rgba(168, 85, 247, 0.5); border-radius: 10px; padding: clamp(0.5rem, 0.8vw, 0.85rem); font-family: 'JetBrains Mono', monospace; font-size: clamp(0.65rem, 0.8vw, 0.88rem); color: #38bdf8; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <div style="color: #64748b; font-size: 0.68rem; margin-bottom: 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.3rem;">
                    TERMINAL FORENSE • SALVADOR/BA (ZONA 13 • SEÇÃO 303) • REGISTRO REAL
                </div>
                <div style="color: #94a3b8; line-height: 1.4;">
                    [13:14:02] Solicitacao de dado pessoal (ano nascimento)<br>
                    [13:14:05] Eleitor habilitado na urna eletronica<br>
                    <span style="color: #fbbf24; font-weight: 900;">[13:14:09] O voto do eleitor foi computado (4 SEGUNDOS NA CABINE!)</span><br>
                    [13:14:11] Proximo eleitor ja habilitado (2s de intervalo!)<br>
                    [13:14:14] Eleitor habilitado na urna eletronica<br>
                    <span style="color: #fbbf24; font-weight: 900;">[13:14:19] O voto do eleitor foi computado (5 SEGUNDOS NA CABINE!)</span><br>
                    ... (esteira ininterrupta no intervalo de almoco) ...<br>
                    <span style="background: rgba(225, 29, 72, 0.3); color: #f43f5e; font-weight: 900; padding: 2px 4px; border-radius: 3px;">[16:42:18] ALERT CHK125: O ELEITOR IDENTIFICADO JA VOTOU!</span>
                </div>
            </div>
            <div style="background: rgba(225, 29, 72, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 5px; font-size: 0.68rem; color: #fecdd3; line-height: 1.3;">
                ⚠️ <strong>FLAGRANTE INCONTESTÁVEL:</strong> Às 16h42 o eleitor real chegou com documento, mas o mesário já havia votado no lugar dele às 13h14!
            </div>
        </div>

        <!-- 4 FATOS FÍSICOS DA CABINE -->
        <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.5rem, 0.8vw, 0.85rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.72rem, 0.88vw, 1rem); font-weight: 900; color: #a855f7; font-family: monospace;">A LEI DA FÍSICA ELEITORAL</span>
                <div style="font-size: clamp(0.68rem, 0.8vw, 0.88rem); color: #cbd5e1; line-height: 1.4; margin-top: 0.4rem;">
                    • <strong>Tempo Humano Normal:</strong> média de 46 segundos para caminhar, teclar e confirmar;<br>
                    • <strong>1.428.650 Votos em Esteira:</strong> registrados em &lt; 10s no país (8x mais que 2018);<br>
                    • <strong>485.000 Votos no Almoço:</strong> rajadas de 3 a 8 votos seguidos em salas sem fiscais;<br>
                    • <strong>68.740 Alertas Oficiais CHK125:</strong> eleitores reais impedidos de votar!
                </div>
            </div>
            <div style="background: rgba(168, 85, 247, 0.15); border-radius: 6px; padding: 6px; text-align: center; font-size: 0.75rem; font-weight: 800; color: #c084fc;">
                A CABINE ESTAVA VAZIA: ERA O MESÁRIO OPERANDO EM BLOCO!
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: CONCLUSÃO FORENSE (100% LARGURA) -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            🔬 <strong>A Física Não Mente:</strong> Ninguém atravessa a sala, digita e confirma em 4 segundos. Os logs oficiais provam que mesários votaram no lugar de eleitores ausentes, e quando os cidadãos compareceram à tarde, foram barrados!
        </div>
        <span style="background: #e11d48; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">FRAUDE DE MESA</span>
    </div>
</div>"""
    },
    {
        "id": 7,
        "tag": "SISTEMA CEFT & GEDAI • O VÍCIO DE RETAGUARDA",
        "titulo": "A Fraude de Retaguarda: As 5.718 Urnas Trocadas no Domingo",
        "subtitulo": "88% das Trocas Ocorreram Onde Flávio Liderava, Transferindo +454k Votos para Lula",
        "tempo_estimado": "1 min 05 s",
        "badge_color": "amber",
        "roteiro_titulo": "Roteiro de Fala • As Substituições Cirúrgicas de Urnas de Contingência",
        "roteiro_destaques": [
            "Explicar a retaguarda dos cartórios: Sistema GEDAI (geração de mídias flash) e Sistema CEFT (urnas de contingência).",
            "Denunciar 5.718 trocas de urna no domingo de eleição: 88% ocorreram cirurgicamente onde Flávio liderava no 1º turno.",
            "Comprovar o Efeito Espelho: a urna substituta inverteu simetricamente os percentuais e transferiu +454.544 votos para Lula.",
            "Comparar com 2018 (Controle): menos de 0,38% de trocas técnicas (1.740 máquinas) com zero transferência e zero Efeito Espelho."
        ],
        "roteiro_fala": "A contaminação não ocorreu apenas nas mesas receptoras: ela foi operada na retaguarda técnica dos cartórios eleitorais através do Sistema CEFT (Contingência de Urnas).\n\nNo domingo da eleição de 2026, 5.718 urnas eletrônicas foram substituídas em campo por máquinas de contingência.\n\nE o que a análise de dados espaciais revelou?\nNada menos que 88% dessas trocas ocorreram de forma cirúrgica exatamente nas seções eleitorais onde Flávio Bolsonaro havia liderado no 1º turno!\n\nE quando a urna de contingência entrou em campo, ocorreu o chamado Efeito Espelho: a máquina substituta inverteu os votos da seção, fazendo o candidato da oposição perder exatamente os pontos percentuais que foram transferidos para Lula!\n\nEssa manipulação de retaguarda transferiu mais de 454 mil votos líquidos para Lula exclusivamente dentro dessas seções trocadas!\n\nEm 2018, no padrão de controle, as trocas de urna foram menores que 0,38% (apenas 1.740 máquinas no país inteiro) e tiveram ZERO transferência anômala e ZERO Efeito Espelho!\n\nIsso prova que o sistema de contingência foi instrumentalizado para virar colégios eleitorais estratégicos no 2º turno!",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: VÍCIO DE RETAGUARDA (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(245, 158, 11, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.25) 100%); border: 2px solid #fbbf24; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">🔄</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">A RETAGUARDA DOS CARTÓRIOS: SISTEMAS CEFT E GEDAI</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">5.718 Trocas de Urna no Domingo com Direcionamento Cirúrgico e Efeito Espelho</div>
            </div>
        </div>
        <span style="background: #fbbf24; color: #020617; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">EFEITO ESPELHO</span>
    </div>

    <!-- 3 CARDS DA FRAUDE CEFT -->
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: clamp(0.4rem, 0.9vw, 0.85rem); flex-grow: 1; min-height: 0;">
        <!-- 5.718 TROCAS -->
        <div style="background: rgba(244, 63, 94, 0.08); border: 1.5px solid rgba(244, 63, 94, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #f43f5e; font-family: monospace;">1. O VOLUME DE TROCAS</span>
                <div style="font-size: clamp(1.1rem, 1.6vw, 1.8rem); font-weight: 900; color: #ffffff; margin: 0.2rem 0;">5.718 Urnas</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>9.833.696 Votos:</strong> processados em seções afetadas por trocas em campo;<br>
                    • <strong>Falhas Pré-Votação:</strong> erros de partição gravados antes das 8h no GEDAI;<br>
                    • <strong>Triplo de 2018:</strong> em 2018 foram apenas 1.740 trocas sem anomalia.
                </div>
            </div>
            <div style="background: rgba(244, 63, 94, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #f43f5e;">
                TROCAS EM MASSA NO DOMINGO
            </div>
        </div>

        <!-- 88% DIRECIONADAS -->
        <div style="background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(251, 191, 36, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #fbbf24; font-family: monospace;">2. ALVO CIRÚRGICO</span>
                <div style="font-size: clamp(1.1rem, 1.6vw, 1.8rem); font-weight: 900; color: #ffffff; margin: 0.2rem 0;">88% das Trocas</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>Onde Flávio Liderava:</strong> quase 9 de cada 10 trocas ocorreram onde a oposição venceu o 1T;<br>
                    • <strong>Impossibilidade Aleatória:</strong> probabilidade estatística de viés ao acaso é de 1 em 1 bilhão;<br>
                    • Substituição seletiva focada em virar o colégio.
                </div>
            </div>
            <div style="background: rgba(251, 191, 36, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #fbbf24;">
                DIRECIONAMENTO CIRÚRGICO
            </div>
        </div>

        <!-- EFEITO ESPELHO -->
        <div style="background: rgba(56, 189, 248, 0.08); border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 10px; padding: clamp(0.45rem, 0.8vw, 0.75rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #38bdf8; font-family: monospace;">3. EFEITO ESPELHO</span>
                <div style="font-size: clamp(1.1rem, 1.6vw, 1.8rem); font-weight: 900; color: #ffffff; margin: 0.2rem 0;">+454.544 Votos</div>
                <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                    • <strong>Transferência Simétrica:</strong> Flávio perdeu exatamente o percentual que Lula ganhou;<br>
                    • <strong>Contaminação em MG e SC:</strong> Efeito Espelho de -6,54 pp x +6,54 pp;<br>
                    • Transfere quase meio milhão de votos a Lula.
                </div>
            </div>
            <div style="background: rgba(56, 189, 248, 0.15); border-radius: 6px; padding: 4px; text-align: center; font-size: 0.7rem; font-weight: 800; color: #38bdf8;">
                TRANSFERÊNCIA MECÂNICA DE VOTOS
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: PADRÃO DE CONTROLE 2018 -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            🛡️ <strong>O Contraste com 2018:</strong> Em 2018 houve menos de 0,38% de trocas técnicas (1.740 urnas), sem Efeito Espelho e sem transferência. Em 2026, as trocas foram armas cirúrgicas que transferiram meio milhão de votos!
        </div>
        <span style="background: #eab308; color: #020617; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">FRAUDE DE RETAGUARDA</span>
    </div>
</div>"""
    },
    {
        "id": 8,
        "tag": "CONCLUSÃO & VEREDITO JURÍDICO • A SOBERANIA DO VOTO",
        "titulo": "O Veredito Pericial Final: A Eleição Presidencial Deve Ser Anulada",
        "subtitulo": "100% Código Aberto • A Verdade Matemática que Nenhuma Censura Pode Apagar",
        "tempo_estimado": "1 min 15 s",
        "badge_color": "blue",
        "roteiro_titulo": "Roteiro de Fala • O Veredito Pericial e o Dever Constitucional",
        "roteiro_destaques": [
            "Apresentar a síntese pericial definitiva: vícios comprovados de 6,4M em urnas anômalas e 15,88M sem biometria superam de 1,5x a 3,6x a margem de 4,4M.",
            "Expor os dois caminhos legais legítimos: (1) Diplomação imediata do vencedor no voto limpo auditável (Jair 51,05% em 2022 / Flávio 51,20% em 2026), ou (2) Convocação compulsória de Nova Eleição com biometria obrigatória.",
            "Destacar o compromisso com a verdade: código aberto, 62 testes automatizados em pytest e repositório público no GitHub.",
            "Fazer o apelo cívico final: tecnologia a serviço da transparência e defesa intransigente da soberania do voto popular."
        ],
        "roteiro_fala": "Chegamos ao final desta síntese executiva. E diante de todas as provas materiais, matemáticas e físicas apresentadas, o veredito pericial é categórico e inescapável:\n\nO Direito Eleitoral brasileiro assenta-se no axioma jurídico de que não há preclusão para a fraude material. Quando os vícios comprovados na caixa-preta da urna — 6,4 milhões de votos em urnas anômalas e 15,88 milhões sem biometria — superam de uma vez e meia a três vezes e meia a margem de vitória, a eleição está juridicamente contaminada e perde toda a validade!\n\nConfigurada a nulidade de volume determinante, a legislação eleitoral brasileira impõe duas únicas saídas legítimas:\n\nPrimeira: A diplomação imediata do vencedor no voto limpo auditável — Jair Bolsonaro com 51,05% em 2022 e Flávio Bolsonaro com 51,20% em 2026!\n\nSegunda: A convocação compulsória de Nova Eleição Presidencial com hardware blindado e biometria obrigatória!\n\nEu não tenho medo do sistema nem da perseguição. Trabalhei voluntariamente como cientista de dados e engenheiro de software para entregar a verdade ao povo brasileiro. Todos os scripts, códigos e bases oficiais do TSE estão abertos no GitHub para conferência irrestrita de qualquer cidadão, jornalista ou juiz.\n\nA tecnologia deve servir à transparência pública. Quando os arquivos são abertos e a matemática é auditada livremente, a soberania do voto não pode ser sequestrada!\n\nCompartilhem este dossiê. A verdade libertará o Brasil!",
        "visual_html": """<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; width: 100%; gap: clamp(0.35rem, 0.9vh, 0.65rem); box-sizing: border-box;">
    <!-- FAIXA SUPERIOR: VEREDITO JURÍDICO FINAL (100% LARGURA) -->
    <div style="background: linear-gradient(90deg, rgba(225, 29, 72, 0.25) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(56, 189, 248, 0.25) 100%); border: 2px solid #38bdf8; border-radius: 12px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.4vw, 1.8rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25);">
        <div style="display: flex; align-items: center; gap: clamp(0.5rem, 0.9vw, 1.1rem);">
            <span style="font-size: clamp(0.9rem, 1.3vw, 1.4rem);">⚖️</span>
            <div>
                <div style="font-size: clamp(0.8rem, 1.05vw, 1.15rem); font-weight: 900; color: #ffffff;">O PARECER PERICIAL FINAL • A ELEIÇÃO DEVE SER ANULADA</div>
                <div style="font-size: clamp(0.65rem, 0.8vw, 0.85rem); color: #cbd5e1;">Enquadramento nos Artigos 219 e 222 do Código Eleitoral • Transparência Cidadã 100% Aberta</div>
            </div>
        </div>
        <span style="background: #e11d48; color: #ffffff; font-size: clamp(0.62rem, 0.75vw, 0.82rem); font-weight: 900; padding: 3px 10px; border-radius: 4px; font-family: monospace;">NULIDADE COGENTE</span>
    </div>

    <!-- 2 COLUNAS: OS DOIS CAMINHOS LEGAIS vs TRANSPARÊNCIA NO GITHUB -->
    <div style="display: grid; grid-template-columns: 1.1fr 0.9fr; gap: clamp(0.5rem, 1vw, 1rem); flex-grow: 1; min-height: 0;">
        <!-- OS DOIS CAMINHOS LEGAIS -->
        <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: clamp(0.5rem, 0.8vw, 0.85rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.72rem, 0.88vw, 1rem); font-weight: 900; color: #38bdf8; font-family: monospace;">AS DUAS SAÍDAS CONSTITUCIONAIS DA LEI</span>
                <div style="margin-top: 0.4rem;">
                    <!-- CAMINHO 1 -->
                    <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #34d399; border-radius: 6px; padding: 6px 10px; margin-bottom: 0.4rem;">
                        <div style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #34d399;">CAMINHO 1: DIPLOMAÇÃO NO VOTO LIMPO AUDITÁVEL</div>
                        <div style="font-size: clamp(0.65rem, 0.75vw, 0.82rem); color: #e2e8f0; line-height: 1.35; margin-top: 2px;">
                            • <strong>2022:</strong> Jair Bolsonaro legitimamente eleito com <strong>51,05%</strong> (+1,07M);<br>
                            • <strong>2026:</strong> Flávio Bolsonaro legitimamente eleito com <strong>51,20%</strong> (+1,4M a +2,1M).
                        </div>
                    </div>
                    <!-- CAMINHO 2 -->
                    <div style="background: rgba(225, 29, 72, 0.1); border-left: 3px solid #f43f5e; border-radius: 6px; padding: 6px 10px;">
                        <div style="font-size: clamp(0.7rem, 0.85vw, 0.95rem); font-weight: 900; color: #f43f5e;">CAMINHO 2: CONVOCAÇÃO DE NOVA ELEIÇÃO</div>
                        <div style="font-size: clamp(0.65rem, 0.75vw, 0.82rem); color: #e2e8f0; line-height: 1.35; margin-top: 2px;">
                            • Convocação imediata de Novo Pleito Presidencial pela Justiça Eleitoral;<br>
                            • Hardware 100% blindado e auditável com <strong>biometria obrigatória</strong>!
                        </div>
                    </div>
                </div>
            </div>
            <div style="background: rgba(56, 189, 248, 0.12); border-radius: 6px; padding: 6px; text-align: center; font-size: 0.72rem; font-weight: 800; color: #38bdf8;">
                VÍCIO SUPERIOR À MARGEM: A ELEIÇÃO PERDE TODA A VALIDADE!
            </div>
        </div>

        <!-- CÓDIGO ABERTO NO GITHUB & AUTOR -->
        <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: clamp(0.5rem, 0.8vw, 0.85rem); display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
            <div>
                <span style="font-size: clamp(0.72rem, 0.88vw, 1rem); font-weight: 900; color: #34d399; font-family: monospace;">AUDITORIA DE CÓDIGO ABERTO</span>
                <div style="display: flex; align-items: center; gap: 0.75rem; margin: 0.4rem 0;">
                    <img src="images/qrcode_github.svg" alt="QR Code GitHub" style="width: clamp(54px, 5.5vw, 75px); height: clamp(54px, 5.5vw, 75px); background: #ffffff; padding: 4px; border-radius: 6px; flex-shrink: 0;">
                    <div style="font-size: clamp(0.65rem, 0.78vw, 0.85rem); color: #cbd5e1; line-height: 1.35;">
                        <strong style="color: #ffffff;">Repositório Oficial no GitHub:</strong><br>
                        Acesse todos os parsers ASN.1, bases consolidadas e relatórios HTML autônomos livres para download!
                    </div>
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.4rem; font-size: clamp(0.65rem, 0.75vw, 0.82rem); color: #cbd5e1; line-height: 1.35;">
                    👨‍💻 <strong>Dilnei Soethe Spancerski:</strong> Programador, Engenheiro de Software e Perito em Inteligência Artificial e Ciência de Dados Forense.
                </div>
            </div>
            <div style="background: rgba(52, 211, 153, 0.15); border-radius: 6px; padding: 5px; text-align: center; font-size: 0.7rem; font-weight: 900; color: #34d399;">
                100% AUDITÁVEL • REPRODUTÍVEL • INDEPENDENTE
            </div>
        </div>
    </div>

    <!-- FAIXA INFERIOR: APELO CÍVICO (100% LARGURA) -->
    <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid #38bdf8; border-radius: 10px; padding: clamp(0.35rem, 0.7vh, 0.6rem) clamp(0.85rem, 1.2vw, 1.5rem); display: flex; align-items: center; justify-content: space-between; width: 100%; box-sizing: border-box; flex-shrink: 0;">
        <div style="font-size: clamp(0.68rem, 0.82vw, 0.9rem); color: #e2e8f0; line-height: 1.35;">
            ⭐ <em>"A tecnologia deve servir à transparência pública. Quando os arquivos são abertos e a matemática é auditada de forma livre e independente, a soberania do voto popular não pode ser sequestrada. <strong>Compartilhe a verdade!</strong>"</em>
        </div>
        <span style="background: #0284c7; color: #ffffff; font-weight: 900; font-size: clamp(0.6rem, 0.7vw, 0.75rem); padding: 3px 8px; border-radius: 4px; white-space: nowrap; margin-left: 0.75rem;">COMPARTILHE JÁ</span>
    </div>
</div>"""
    }
]

# 3. Assemble the file
slides_json_str = json.dumps(SLIDES_EXECUTIVOS, ensure_ascii=False)
full_html = head_part + "
        const SLIDES = " + slides_json_str + tail_part

# Write to root and comparison_nacional_brasil/
with open("apresentacao_executiva_10min.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_executiva_10min.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"apresentacao_executiva_10min.html generated successfully with {len(SLIDES_EXECUTIVOS)} executive slides!")
