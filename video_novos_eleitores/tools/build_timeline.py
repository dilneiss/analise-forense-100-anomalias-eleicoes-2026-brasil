"""Converte as durações reais da narração em timeline de frames para o Remotion.

Uso:
    ~/.tts-venv/Scripts/python.exe tools/build_timeline.py

Lê  public/audio/narracao.json
Gera src/timeline.ts
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FPS = 30
CAUDA = 42  # 1,4s de respiro após a fala terminar
MINIMO = 105  # nenhuma cena abaixo de 3,5s

ORDEM = ["scene_01", "scene_02", "scene_03", "scene_04", "scene_05", "scene_06"]


def main() -> None:
    dados = json.loads((RAIZ / "public" / "audio" / "narracao.json").read_text(encoding="utf-8"))

    linhas = []
    from_frame = 0
    for nome in ORDEM:
        info = dados[nome]
        falado = int(round(info["duracao_s"] * FPS))
        dur = max(MINIMO, falado + CAUDA)
        linhas.append(
            f'  {{ id: "{nome}", from: {from_frame}, dur: {dur}, '
            f'audio: "audio/{nome}.wav", falado: {falado} }},'
        )
        from_frame += dur

    ts = (
        "// GERADO AUTOMATICAMENTE por tools/build_timeline.py — não editar à mão.\n"
        "// duração de cada cena = duração real da narração + cauda de respiro\n"
        "export type Cena = {\n"
        "  id: string;\n  from: number;\n  dur: number;\n  audio: string;\n  falado: number;\n};\n\n"
        "export const TIMELINE: Cena[] = [\n" + "\n".join(linhas) + "\n];\n\n"
        f"export const TOTAL_FRAMES = {from_frame};\n"
    )

    destino = RAIZ / "src" / "timeline.ts"
    destino.write_text(ts, encoding="utf-8")
    print(destino)
    print(f"total: {from_frame} frames = {from_frame / FPS:.1f}s")
    for linha in linhas:
        print(linha)


if __name__ == "__main__":
    main()
