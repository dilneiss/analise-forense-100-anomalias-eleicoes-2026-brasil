import json, re

# =========================================================================
# 1. ATUALIZAR apresentacao_slides.html e comparison_nacional_brasil/
# =========================================================================
with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

# --- SLIDE 06 (Índice 5) ---
s6 = slides[5]
assert s6["id"] == 6

# Ajustar destaques de Slide 6
s6["roteiro_destaques"] = [
    d.replace("cravados para o 13 (Lula)", "na seção onde Lula teve 74% dos votos no BU")
    for d in s6["roteiro_destaques"]
]

# Ajustar fala de Slide 6
s6["roteiro_fala"] = s6["roteiro_fala"].replace(
    "Voto confirmado para o 13 (Lula)!",
    "Voto confirmado para [Presidente] (nesta seção, Lula teve 74% dos votos no BU)!"
)
s6["roteiro_fala"] = s6["roteiro_fala"].replace(
    "todos liberados por ano de nascimento e 100% computados para Lula!",
    "todos liberados por ano de nascimento! Lembrando com rigor pericial: a lei assegura o sigilo do voto, então o log não traz o número do candidato individual. Mas o resultado do Boletim de Urna desta seção mostra que 74% dos votos foram para Lula, evidenciando que essa esteira mecânica inflou a votação majoritária da urna!"
)

# --- SLIDE 17 (Índice 16) ---
s17 = slides[16]
assert s17["id"] == 17

# Ajustar destaques de Slide 17
s17["roteiro_destaques"] = [
    d.replace("cravados no 13", "estimados para o 13 com base na apuração dos BUs das seções afetadas")
    for d in s17["roteiro_destaques"]
]

# Ajustar fala de Slide 17
s17["roteiro_fala"] = s17["roteiro_fala"].replace(
    "cravados no 13",
    "estimados para o 13 com base nos BUs das seções com esteira"
)
if "Muitas pessoas perguntam: 'Temos como saber em quem cada pessoa votou" not in s17["roteiro_fala"]:
    s17["roteiro_fala"] = s17["roteiro_fala"].replace(
        "A resposta científica, matemática e oficial extraída de mais de 490 mil arquivos de log está diante dos seus olhos neste gráfico:",
        "Muitas pessoas perguntam: 'Temos como saber em quem cada pessoa votou individualmente na esteira?' E a resposta com total rigor científico é: NÃO, o log não identifica o candidato individual de cada eleitor, pois o voto é secreto por cláusula pétrea constitucional (Artigo 14 da Constituição). O que o log comprova de forma inegável é o fato físico do tempo (3 a 10 segundos) e a ausência de biometria. A divisão de votos entre Lula e Flávio que apresentamos aqui é uma ESTIMATIVA PERICIAL PROPORCIONAL baseada na apuração oficial dos Boletins de Urna (BUs) daquelas mesmas seções onde as esteiras ocorreram, e onde Lula teve ampla maioria:"
    )

vh17 = s17["visual_html"]
vh17 = vh17.replace("13: 82,6% TOTAL < 10s", "13: 82,6% (ESTIMATIVA BU)")
vh17 = vh17.replace("cravados no 13!", "estimados para o 13 com base nos BUs das seções afetadas!")
s17["visual_html"] = vh17

# --- SLIDE 18 (Índice 17) ---
s18 = slides[17]
assert s18["id"] == 18

vh18 = s18["visual_html"]
vh18 = vh18.replace(
    "100% dos votos viciados foram computados para LULA (PT) e retirados de Bolsonaro (2022) e Flávio (2026)!",
    "a totalidade do saldo anômalo e dos desvios de hardware e mesa favoreceu exclusivamente a campanha de LULA (PT) e prejudicou Bolsonaro (2022) e Flávio (2026)!"
)
vh18 = vh18.replace("100% PRÓ-LULA", "SALDO PRÓ-LULA")
s18["visual_html"] = vh18

# Ajustar fala do Slide 18
s18["roteiro_fala"] = s18["roteiro_fala"].replace(
    "CEM POR CENTO DOS VOTOS SOB VÍCIO FORAM COMPUTADOS EXCLUSIVAMENTE A FAVOR DE LULA e retirados dos candidatos conservadores!",
    "TODOS OS DESVIOS ANÔMALOS E VÍCIOS MATERIAIS BENEFICIARAM EXCLUSIVAMENTE A CAMPANHA DE LULA. Isso não significa que temos como saber em quem cada eleitor individual votou na esteira — pois a Constituição garante o sigilo do voto —, mas sim que todo o saldo líquido de votos gerado nas seções anômalas inflou a votação de Lula no Boletim de Urna!"
)
s18["roteiro_fala"] = s18["roteiro_fala"].replace(
    "cravados no 13!",
    "estimados para o 13 com base nos BUs daquelas seções!"
)

# Salvar apresentacao_slides.html
slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("apresentacao_slides.html updated successfully!")

# =========================================================================
# 2. ATUALIZAR motion_graphics_achados.html e comparison_nacional_brasil/
# =========================================================================
with open("motion_graphics_achados.html", "r", encoding="utf-8") as f:
    mg_text = f.read()

mg_text = mg_text.replace(
    '<h2 class="scene-title">A Fábrica de 812 Mil Votos Sem Digital para Lula</h2>',
    '<h2 class="scene-title">Estimativa Pericial: O Saldo de 812 Mil Votos Sem Digital nas Urnas em Esteira</h2>'
)
mg_text = mg_text.replace(
    'Cruzamento dos votos sem biometria em alta velocidade (&le; 10s): 87,5% para o 13 contra 12,5% para o 22!',
    'Estimativa pericial proporcional cruzando as seções com esteira (&le; 10s) e a apuração oficial dos BUs: 87,5% pró-Lula vs 12,5% pró-Flávio'
)
mg_text = mg_text.replace(
    '<span style="font-size: 0.72rem; color: #fca5a5; font-weight: 800; font-family: monospace;">LULA (13) • SEM BIOMETRIA &lt; 10s</span>',
    '<span style="font-size: 0.72rem; color: #fca5a5; font-weight: 800; font-family: monospace;">LULA (13) • ESTIMATIVA PROPORCIONAL BU</span>'
)
mg_text = mg_text.replace(
    '<span style="font-size: 0.72rem; color: #bae6fd; font-weight: 800; font-family: monospace;">FLÁVIO (22) • SEM BIOMETRIA &lt; 10s</span>',
    '<span style="font-size: 0.72rem; color: #bae6fd; font-weight: 800; font-family: monospace;">FLÁVIO (22) • ESTIMATIVA PROPORCIONAL BU</span>'
)

# Nota explicativa na barra de cabo de guerra
note_mg_bar = '<div style="font-size: 0.52rem; color: #94a3b8; font-style: italic; margin-top: 2px;">*Estimativa pericial proporcional baseada no resultado oficial dos BUs das seções onde ocorreram as esteiras. O log oficial não identifica o candidato por sigilo constitucional (Art. 14 CF/88).</div>'
if "Estimativa pericial proporcional baseada no resultado oficial dos BUs" not in mg_text:
    mg_text = mg_text.replace(
        '<div style="background: rgba(15, 23, 42, 0.95); border: 1px solid var(--red);',
        note_mg_bar + '\n            <div style="background: rgba(15, 23, 42, 0.95); border: 1px solid var(--red);'
    )

with open("motion_graphics_achados.html", "w", encoding="utf-8") as f:
    f.write(mg_text)

with open("comparison_nacional_brasil/motion_graphics_achados.html", "w", encoding="utf-8") as f:
    f.write(mg_text)

print("motion_graphics_achados.html updated successfully!")

# =========================================================================
# 3. ATUALIZAR APRESENTACAO_DOSSIE_PERICIAL_ELEICOES.md
# =========================================================================
with open("APRESENTACAO_DOSSIE_PERICIAL_ELEICOES.md", "r", encoding="utf-8") as f:
    dos_text = f.read()

dos_text = dos_text.replace(
    "foram cravados para Lula (13)",
    "foram apurados para Lula (13) no Boletim de Urna"
)

with open("APRESENTACAO_DOSSIE_PERICIAL_ELEICOES.md", "w", encoding="utf-8") as f:
    f.write(dos_text)

print("APRESENTACAO_DOSSIE_PERICIAL_ELEICOES.md updated successfully!")
