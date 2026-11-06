"""Animação Manim: 116.480 novos eleitores entre turnos (9:16, 30fps, 48s).

O áudio é mixado depois com ffmpeg — esta cena é silenciosa.

Render:
    python -m manim render manim_novos_eleitores/scene.py AuditoriaEleitores -qh --format=mp4
"""
from manim import *  # noqa: F401,F403

# ── Saída vertical 1080x1920 ──────────────────────────────────────────────
config.background_color = "#0B0C0E"
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30

# ── Paleta ────────────────────────────────────────────────────────────────
INK = "#F8FAFC"
DIM = "#94A3B8"
FAINT = "#4A4F57"
AMBER = "#F59E0B"
RED = "#FF4A2E"
CYAN = "#22D3EE"
GREEN = "#10B981"
FRAME = "#2E3238"

F_MONO = "Consolas"
F_HEAD = "Arial"

# ── Zonas verticais do quadro (y vai de -8 a +8) ──────────────────────────
Y_CHIP = 7.0
Y_RETRANCA = 1.0  # margem horizontal segura (~100 px)


def num(v: int) -> str:
    """1234567 -> '1.234.567' (separador pt-BR)."""
    return f"{v:,}".replace(",", ".")


class AuditoriaEleitores(Scene):
    # ── utilidades ────────────────────────────────────────────────────────
    def hold_until(self, t: float) -> None:
        restante = t - self.renderer.time
        if restante > 0:
            self.wait(restante)

    def rotulo(self, txt: str, size=22, color=DIM) -> Text:
        return Text(txt.upper(), font=F_MONO, font_size=size, color=color)

    def chip(self, tipo: str, tag: str, cor=CYAN) -> VGroup:
        barra = Rectangle(width=0.09, height=0.26, fill_color=cor, fill_opacity=1,
                          stroke_width=0)
        texto = Text(f"{tipo} · {tag}", font=F_MONO, font_size=17, color=DIM)
        grupo = VGroup(barra, texto).arrange(RIGHT, buff=0.16, aligned_edge=UP)
        grupo.move_to([-4.5 + Y_RETRANCA + grupo.width / 2, Y_CHIP, 0])
        return grupo

    def grade(self, rows: int, cols: int, cell: float, gap: float,
              cor: str, opacidade: float, centro) -> VGroup:
        """Grade determinística posicionada por cálculo explícito (sem arrange)."""
        passo = cell + gap
        largura = cols * passo - gap
        altura = rows * passo - gap
        x0 = -largura / 2 + cell / 2
        y0 = altura / 2 - cell / 2
        grupo = VGroup()
        for r in range(rows):
            for c in range(cols):
                grupo.add(
                    Square(side_length=cell, stroke_width=0, fill_color=cor,
                           fill_opacity=opacidade).move_to(
                        [x0 + c * passo, y0 - r * passo, 0]
                    )
                )
        grupo.move_to(centro)
        return grupo

    # ── cena ──────────────────────────────────────────────────────────────
    def construct(self) -> None:
        # ═══════════ ATO 1 · AUDITORIA COM IA · 0 → 11,33 s ═══════════
        chip1 = self.chip("MOTOR", "AUDITORIA COM INTELIGÊNCIA ARTIFICIAL")

        t1 = Text("499.178", font=F_HEAD, weight=BOLD, font_size=96, color=INK)
        t1.move_to([-4.5 + Y_RETRANCA + t1.width / 2, 4.9, 0])
        s1 = self.rotulo("seções eleitorais processadas", 20)
        s1.next_to(t1, DOWN, buff=0.16).align_to(t1, LEFT)

        self.play(FadeIn(chip1, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(t1, shift=UP * 0.3), FadeIn(s1, shift=UP * 0.15), run_time=1.1)

        malha1 = self.grade(30, 14, 0.2, 0.11, CYAN, 0.55, [0, -1.5, 0])
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.6) for d in malha1], lag_ratio=0.002),
            run_time=1.5,
        )
        self.hold_until(5.1)

        varredura = Line(
            [-4.2, malha1.get_top()[1], 0], [4.2, malha1.get_top()[1], 0],
            color=CYAN, stroke_width=3,
        )
        self.play(varredura.animate.set_y(malha1.get_bottom()[1]), run_time=1.7)
        self.play(FadeOut(varredura), run_time=0.25)
        self.hold_until(7.4)

        alerta = Text("ANOMALIA CADASTRAL\nDETECTADA", font=F_MONO, font_size=25,
                      color=RED, line_spacing=1.2)
        alerta.move_to([-4.5 + Y_RETRANCA + alerta.width / 2, -4.9, 0])
        caixa = SurroundingRectangle(alerta, color=RED, stroke_width=1.6, buff=0.3,
                                     corner_radius=0.05)
        detalhe = self.rotulo("o cadastro não deveria mudar entre turnos", 16)
        detalhe.next_to(caixa, DOWN, buff=0.28).align_to(caixa, LEFT)

        self.play(Create(caixa), FadeIn(alerta, shift=UP * 0.15), run_time=0.8)
        self.play(FadeIn(detalhe, shift=UP * 0.1), run_time=0.6)
        self.hold_until(11.33 - 0.42)
        self.play(FadeOut(VGroup(chip1, t1, s1, malha1, caixa, alerta, detalhe)),
                  run_time=0.4)

        # ═══════════ ATO 2 · A LEI DOS 150 DIAS · 11,33 → 21,82 s ═══════════
        chip2 = self.chip("LEGISLAÇÃO", "LEI 9.504/1997 · ART. 91", RED)

        t2 = Text("CADASTRO CONGELADO", font=F_HEAD, weight=BOLD, font_size=44,
                  color=INK)
        t2.move_to([-4.5 + Y_RETRANCA + t2.width / 2, 5.6, 0])

        n150 = Text("150", font=F_MONO, weight=BOLD, font_size=132, color=RED)
        n150.move_to([-4.5 + Y_RETRANCA + n150.width / 2, 3.3, 0])
        dias = self.rotulo("dias antes do pleito", 22, INK)
        dias.next_to(n150, DOWN, buff=0.1).align_to(n150, LEFT)

        self.play(FadeIn(chip2, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(t2, shift=UP * 0.25), run_time=0.8)
        self.play(Write(n150, run_time=1.1), FadeIn(dias, shift=UP * 0.1), run_time=1.1)
        self.hold_until(15.4)

        eixo = NumberLine(x_range=[0, 150, 25], length=7.8, color=FAINT,
                          include_numbers=False, include_tip=False)
        eixo.move_to([0, 0.5, 0])
        marcas = VGroup(*[
            Text(str(v), font=F_MONO, font_size=16, color=FAINT).next_to(
                eixo.n2p(v), DOWN, buff=0.16)
            for v in (0, 50, 100, 150)
        ])
        trava = Line(ORIGIN, UP * 0.8, color=RED, stroke_width=4)
        trava.move_to(eixo.n2p(0), aligned_edge=DOWN)

        self.play(Create(eixo), FadeIn(marcas), run_time=1.1)
        self.play(GrowFromCenter(trava), run_time=0.5)
        self.hold_until(18.2)

        citacao = Text(
            "“nenhuma alteração no cadastro\npode ser feita nesse prazo”",
            font=F_MONO, font_size=18, color=DIM, line_spacing=1.5,
        )
        citacao.move_to([-4.5 + Y_RETRANCA + citacao.width / 2, -2.6, 0])
        self.play(FadeIn(citacao, shift=UP * 0.2), run_time=0.8)
        self.hold_until(21.82 - 0.42)
        self.play(FadeOut(VGroup(chip2, t2, n150, dias, eixo, marcas, trava, citacao)),
                  run_time=0.4)

        # ═══════════ ATO 3 · O FLAGRANTE · 21,82 → 32,69 s ═══════════
        chip3 = self.chip("FLAGRANTE", "REGRA CHK018 · DISCREPÂNCIA", RED)

        rot3 = self.rotulo("novos nomes inseridos no caderno", 20)
        rot3.move_to([-4.5 + Y_RETRANCA + rot3.width / 2, 5.7, 0])

        contador = Text("0", font=F_MONO, weight=BOLD, font_size=124, color=RED)
        contador.move_to([-4.5 + Y_RETRANCA + contador.width / 2, 4.0, 0])

        self.play(FadeIn(chip3, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(rot3, shift=UP * 0.15), run_time=0.5)
        self.play(FadeIn(contador, shift=UP * 0.2), run_time=0.5)

        alvo = Text(num(116480), font=F_MONO, weight=BOLD, font_size=124, color=RED)
        alvo.move_to([-4.5 + Y_RETRANCA + alvo.width / 2, 4.0, 0])
        # Troca por fade: interpolar dois Text de larguras diferentes borra os glifos
        self.play(FadeOut(contador, shift=UP * 0.22), run_time=0.32)
        self.play(FadeIn(alvo, shift=UP * 0.22), run_time=0.45)
        self.hold_until(24.6)

        malha3 = self.grade(14, 30, 0.19, 0.07, RED, 0.8, [0, -1.4, 0])
        legenda = self.rotulo("92.000 seções afetadas no país", 20, CYAN)
        legenda.move_to([-4.5 + Y_RETRANCA + legenda.width / 2, -5.5, 0])

        self.play(
            LaggedStart(*[FadeIn(r, scale=1.7) for r in malha3], lag_ratio=0.002),
            run_time=2.2,
        )
        self.play(FadeIn(legenda, shift=UP * 0.15), run_time=0.6)
        self.hold_until(32.69 - 0.42)
        self.play(FadeOut(VGroup(chip3, rot3, alvo, malha3, legenda)),
                  run_time=0.4)

        # ═══════════ ATO 4 · CONTROLE 2018 vs 2026 · 32,69 → 48,00 s ═══════════
        chip4 = self.chip("PROVA", "GRUPO DE CONTROLE · 2018", GREEN)

        t4 = Text("2018   vs   2026", font=F_HEAD, weight=BOLD, font_size=48,
                  color=INK)
        t4.move_to([-4.5 + Y_RETRANCA + t4.width / 2, 5.7, 0])

        self.play(FadeIn(chip4, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(t4, shift=UP * 0.25), run_time=0.7)
        self.hold_until(34.3)

        base = -4.4
        barra18 = Rectangle(width=1.6, height=0.08, fill_color=GREEN,
                            fill_opacity=1, stroke_width=0)
        barra18.move_to([-2.1, base, 0], aligned_edge=DOWN)

        barra26 = Rectangle(width=1.6, height=5.4, fill_color=RED,
                            fill_opacity=1, stroke_width=0)
        barra26.move_to([2.1, base, 0], aligned_edge=DOWN)

        v18 = Text("0", font=F_MONO, weight=BOLD, font_size=52, color=GREEN)
        v18.next_to(barra18, UP, buff=0.25)
        v26 = Text(num(116480), font=F_MONO, weight=BOLD, font_size=52, color=RED)
        v26.next_to(barra26, UP, buff=0.25)

        l18 = self.rotulo("2018", 21, GREEN).next_to(barra18, DOWN, buff=0.22)
        l26 = self.rotulo("2026", 21, RED).next_to(barra26, DOWN, buff=0.22)

        self.play(GrowFromEdge(barra18, DOWN), FadeIn(v18, shift=UP * 0.2),
                  FadeIn(l18, shift=UP * 0.1), run_time=0.7)
        self.play(GrowFromEdge(barra26, DOWN), FadeIn(v26, shift=UP * 0.2),
                  FadeIn(l26, shift=UP * 0.1), run_time=1.8)
        self.hold_until(40.4)

        veredito = Text("80% PARA O MESMO LADO", font=F_MONO, font_size=23,
                        color=AMBER)
        veredito.move_to([0, 4.3, 0])

        selo_txt = Text("ART. 219 · PREJUÍZO", font=F_MONO, weight=BOLD,
                        font_size=22, color=INK)
        selo = VGroup(
            SurroundingRectangle(selo_txt, color=RED, stroke_width=2, buff=0.26,
                                 corner_radius=0.04),
            selo_txt,
        ).move_to([0, -6.5, 0])

        self.play(FadeIn(veredito, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(selo, scale=1.12), run_time=0.8)
        self.hold_until(47.6)
        self.play(FadeOut(VGroup(chip4, t4, barra18, barra26, v18, v26, l18, l26,
                                 veredito, selo)), run_time=0.4)
