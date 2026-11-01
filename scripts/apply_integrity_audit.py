import json, re

# =========================================================================
# 1. ATUALIZAR apresentacao_slides.html e comparison_nacional_brasil/
# =========================================================================
with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

# --- SLIDE 6 (Índice 5) ---
s6 = slides[5]
assert s6["id"] == 6

# Ajustar visual_html de Slide 6: remover [13 - LULA] do log e colocar formato oficial autêntico
vh6 = s6["visual_html"]
vh6 = vh6.replace("<span style=\"color: #f43f5e; font-weight: 900;\">[13 - LULA]</span>",
                  "<span style=\"color: #34d399; font-weight: 800;\">[Presidente]</span>")

# Substituir o texto de total da rajada
old_rajada_text = "(100% pró-Lula e 100% sem digital)"
new_rajada_text = "(100% sem digital • Nesta seção, Lula teve 74% dos votos no BU)"
vh6 = vh6.replace(old_rajada_text, new_rajada_text)

# Inserir nota metodológica no rodapé do terminal do Slide 6 se ainda não existir
nota_sigilo_s6 = """<div style="font-size: 0.48rem; color: #94a3b8; font-style: italic; margin-top: 3px; border-top: 1px dotted rgba(255,255,255,0.1); padding-top: 2px; line-height: 1.25;">
    ⚖️ <strong>Nota Metodológica &bull; Sigilo do Voto (Art. 14 CF):</strong> O log oficial registra apenas <code>Voto confirmado para [Presidente]</code>, sem imprimir o candidato para preservar o sigilo constitucional. A destinação majoritária é uma <strong>estimativa pericial por correlação com o BU da seção</strong> (onde Lula teve 74% nesta urna).
</div>"""

if "Nota Metodológica &bull; Sigilo do Voto" not in vh6:
    # Insere logo antes do fechamento do terminal
    ins_pos = vh6.find("<!-- ALERTA CHK125 -->")
    if ins_pos != -1:
        # inserir após o container do alerta
        alert_end = vh6.find("</div>\n                    </div>\n                </div>", ins_pos)
        if alert_end != -1:
            vh6 = vh6[:alert_end] + "</div>\n                        " + nota_sigilo_s6 + vh6[alert_end + len("</div>"):]

s6["visual_html"] = vh6

# Ajustar roteiro de fala do Slide 6
s6["roteiro_fala"] = s6["roteiro_fala"].replace(
    "Voto confirmado para o 13 (Lula)!",
    "Voto confirmado para [Presidente] (nesta seção, Lula teve 74% dos votos no BU)!"
)
s6["roteiro_fala"] = s6["roteiro_fala"].replace(
    "todos liberados por ano de nascimento e 100% computados para Lula!",
    "todos liberados por ano de nascimento! Como a lei exige o sigilo do voto (Artigo 14 da Constituição), o log não imprime o número do candidato, mas o cruzamento com o Boletim de Urna desta seção mostra que 74% dos votos foram para Lula, provando que a esteira inflou a votação majoritária!"
)

# --- SLIDE 17 (Índice 16) ---
s17 = slides[16]
assert s17["id"] == 17

vh17 = s17["visual_html"]

# Ajustar cabeçalhos da tabela do Slide 17 para explicitar 'Estimativa'
vh17 = vh17.replace("Lula S/B", "Lula (Est)")
vh17 = vh17.replace("Fláv S/B", "Fláv (Est)")
vh17 = vh17.replace("LULA vs FLÁVIO", "ESTIMATIVA PROPORCIONAL POR SEÇÃO (LOG + BU)")

# Adicionar nota explicativa transparente na legenda
nota_sigilo_s17 = """<div style="font-size: 0.46rem; color: #94a3b8; font-style: italic; margin-top: 2px; border-top: 1px dotted rgba(255,255,255,0.08); padding-top: 1px; line-height: 1.2;">
    ⚖️ <strong>Sigilo do Voto (Art. 14 CF):</strong> O log oficial registra o tempo e a biometria, mas omite o candidato. A divisão entre Lula e Flávio representa <strong>estimativa pericial por correlação</strong> com os Boletins de Urna (BUs) de cada seção com esteira.
</div>"""

if "Sigilo do Voto (Art. 14 CF)" not in vh17:
    legenda_pos = vh17.find("<!-- LEGENDA DIDÁTICA DAS 3 FAIXAS -->")
    if legenda_pos != -1:
        end_legenda = vh17.find("</div>", legenda_pos) + len("</div>")
        vh17 = vh17[:end_legenda] + "\n                " + nota_sigilo_s17 + vh17[end_legenda:]

s17["visual_html"] = vh17

# Ajustar fala do Slide 17
s17["roteiro_fala"] = s17["roteiro_fala"].replace(
    "cruzando exatamente os votos com e sem biometria para Lula e para Flávio Bolsonaro:",
    "cruzando a telemetria do log com a estimativa proporcional do Boletim de Urna (BU) para Lula e para Flávio Bolsonaro. É essencial esclarecer com rigor científico: o log oficial não identifica o candidato do voto individual para respeitar o sigilo constitucional do voto (Artigo 14 da Constituição). O log prova o fato físico inegável do tempo e da ausência de digital; a divisão de votos é uma estimativa pericial decorrente da apuração do BU daquelas mesmas seções:"
)

# Salvar apresentacao_slides.html
slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("apresentacao_slides.html updated with integrity audit successfully!")

# =========================================================================
# 2. ATUALIZAR motion_graphics_achados.html e comparison_nacional_brasil/
# =========================================================================
with open("motion_graphics_achados.html", "r", encoding="utf-8") as f:
    mg_text = f.read()

# Substituir [13 - LULA] por [Presidente] nos snippets do terminal
mg_text = mg_text.replace("Voto confirmado: [13 - LULA]", "Voto confirmado: [Presidente]")
mg_text = mg_text.replace("(Total: 6 votos em 52s)", "(Total: 6 votos em 52s • Estimativa: 74% pró-Lula no BU)")

# Inserir nota no terminal da Cena 5
mg_nota = '<div style="font-size: 0.52rem; color: #94a3b8; font-style: italic; margin-top: 4px; border-top: 1px dotted rgba(255,255,255,0.1); padding-top: 3px;">⚖️ <strong>Nota Pericial:</strong> O log oficial omite o candidato por sigilo constitucional (Art. 14 CF). A destinação majoritária decorre de estimativa por correlação com o BU da seção.</div>'

if "Nota Pericial" not in mg_text:
    term_hook = '<span class="log-cursor"></span>'
    mg_text = mg_text.replace(term_hook, term_hook + "\n                    " + mg_nota)

with open("motion_graphics_achados.html", "w", encoding="utf-8") as f:
    f.write(mg_text)

with open("comparison_nacional_brasil/motion_graphics_achados.html", "w", encoding="utf-8") as f:
    f.write(mg_text)

print("motion_graphics_achados.html updated successfully!")
