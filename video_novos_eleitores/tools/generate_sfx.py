"""Sintetiza o kit de SFX e a base musical (zero downloads, determinístico).

Uso:
    ~/.tts-venv/Scripts/python.exe tools/generate_sfx.py

Saída: public/sfx/*.wav (24 kHz mono 16-bit)
"""
import wave
from pathlib import Path

import numpy as np

SR = 24000
OUT = Path(__file__).resolve().parent.parent / "public" / "sfx"
RNG = np.random.default_rng(2026)


def salvar(nome: str, sinal: np.ndarray) -> None:
    sinal = np.clip(sinal, -1.0, 1.0)
    pcm = (sinal * 32767).astype(np.int16)
    with wave.open(str(OUT / f"{nome}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"{nome}.wav  {len(sinal) / SR:5.2f}s")


def envelope(n: int, ataque: int, decaimento: int) -> np.ndarray:
    env = np.ones(n)
    env[:ataque] = np.linspace(0, 1, ataque)
    env[-decaimento:] = np.linspace(1, 0, decaimento) ** 2
    return env


def passa_faixa(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Filtro simples no domínio da frequência (suficiente para 0,5-2s)."""
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    mascara = (freqs >= lo) & (freqs <= hi)
    spec = spec * mascara
    return np.fft.irfft(spec, n=len(x))


def whoosh(dur: float = 0.55) -> np.ndarray:
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    ruido = passa_faixa(RNG.normal(0, 1, n), 400, 5000)
    ruido /= np.max(np.abs(ruido)) + 1e-9
    # varredura de faixa: abre e fecha
    varredura = np.sin(np.pi * t) ** 2
    return ruido * varredura * envelope(n, int(n * 0.15), int(n * 0.45)) * 0.55


def impacto(dur: float = 0.9) -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    corpo = np.sin(2 * np.pi * (58 * np.exp(-t * 3.2) + 34) * t) * np.exp(-t * 4.4)
    clique = RNG.normal(0, 1, n) * np.exp(-t * 120) * 0.35
    return (corpo * 0.85 + clique) * 0.8


def tick(dur: float = 0.06) -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 95) * 0.35


def riser(dur: float = 1.6) -> np.ndarray:
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    ruido = passa_faixa(RNG.normal(0, 1, n), 900, 9000)
    ruido /= np.max(np.abs(ruido)) + 1e-9
    crescendo = t ** 2.2
    return ruido * crescendo * 0.45


def pad(dur: float = 14.0) -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    notas = [110.0, 164.81, 220.0, 329.63]
    sinal = np.zeros(n)
    for i, f in enumerate(notas):
        sinal += np.sin(2 * np.pi * f * t + i) * 0.16
        sinal += np.sin(2 * np.pi * f * 1.003 * t) * 0.10
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * t)
    fade = envelope(n, int(SR * 1.2), int(SR * 2.0))
    return sinal * lfo * fade * 0.5


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    salvar("whoosh", whoosh())
    salvar("impacto", impacto())
    salvar("tick", tick())
    salvar("riser", riser())
    salvar("pad", pad())


if __name__ == "__main__":
    main()
