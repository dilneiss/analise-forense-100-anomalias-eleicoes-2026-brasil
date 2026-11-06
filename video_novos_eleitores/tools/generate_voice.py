"""Gera a narração do vídeo com Kokoro-82M (local, ONNX).

Uso:
    ~/.tts-venv/Scripts/python.exe tools/generate_voice.py [--voice pm_alex]

Saída: public/audio/scene_NN.wav (24 kHz mono) + relatório de duração.
"""
import argparse
import json
import wave
from pathlib import Path

import numpy as np
from kokoro_onnx import Kokoro

MODELS = Path.home() / ".tts-venv" / "models"
OUT = Path(__file__).resolve().parent.parent / "public" / "audio"

# Roteiro: uma entrada por cena. O texto é o que será falado, sem marcações.
ROTEIRO = [
    (
        "scene_01",
        "Dois mil e dezoito: zero eleitores inseridos no caderno entre o primeiro "
        "e o segundo turno. Dois mil e vinte e seis: cento e dezesseis mil, "
        "quatrocentos e oitenta.",
    ),
    (
        "scene_02",
        "A lei é explícita. O Artigo noventa e um da Lei nove mil quinhentos e "
        "quatro congela o cadastro eleitoral cento e cinquenta dias antes da "
        "eleição. Não é burocracia: o caderno é a régua do comparecimento. "
        "Se ele muda entre turnos, a régua muda.",
    ),
    (
        "scene_03",
        "Foram cento e dezesseis mil, quatrocentos e oitenta novos eleitores, "
        "espalhados por noventa e duas mil seções. Não em uma cidade. Não em um "
        "estado. Em noventa e duas mil seções.",
    ),
    (
        "scene_04",
        "Agora o controle. Dois mil e dezoito, o mesmo cálculo, o mesmo sistema, "
        "o mesmo país: zero. Nenhum eleitor inserido entre o primeiro e o segundo "
        "turno, em nenhuma seção do Brasil.",
    ),
    (
        "scene_05",
        "Dos que efetivamente compareceram, a estimativa por boletim de urna "
        "aponta oitenta por cento para um lado e vinte para o outro. E aqui é "
        "preciso ser rigoroso: essa divisão é estimativa. O log da urna não "
        "registra candidato, por sigilo do voto.",
    ),
    (
        "scene_06",
        "E o contexto fecha a conta. No mesmo período, o comparecimento nacional "
        "subiu dois milhões, novecentos e sessenta mil. Um cadastro que deveria "
        "estar congelado cresceu. Um eleitorado que deveria encolher, cresceu. "
        "A pergunta não é política. É aritmética.",
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="pm_alex")
    ap.add_argument("--speed", type=float, default=1.0)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    kokoro = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))

    relatorio = {}
    for nome, texto in ROTEIRO:
        samples, sr = kokoro.create(
            texto, voice=args.voice, speed=args.speed, lang="pt-br"
        )
        audio = (np.asarray(samples) * 32767).astype(np.int16)
        destino = OUT / f"{nome}.wav"
        with wave.open(str(destino), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(audio.tobytes())

        dur = len(audio) / sr
        relatorio[nome] = {
            "arquivo": str(destino),
            "amostras": int(len(audio)),
            "sample_rate": sr,
            "duracao_s": round(dur, 3),
            "frames_30fps": int(round(dur * 30)),
            "texto": texto,
        }
        print(f"{nome}: {dur:6.2f}s  ({len(audio)} amostras @ {sr} Hz)")

    meta = Path(__file__).resolve().parent.parent / "public" / "audio"
    (meta / "narracao.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(v["duracao_s"] for v in relatorio.values())
    print(f"\nTOTAL falado: {total:.2f}s em {len(relatorio)} cenas")


if __name__ == "__main__":
    main()
