# Vídeo · Novos Eleitores entre Turnos (Remotion)

Duas peças sobre os **116.480 novos eleitores inseridos no caderno de votação entre o 1º e o 2º turno** de 2026.

| Composição | Duração | Áudio | Descrição |
|---|:---:|:---:|---|
| `NovosEleitores` | 38 s | mudo | versão original, 7 cenas |
| `NovosEleitoresWide` | 38 s | mudo | a mesma, 16:9 |
| `EleitoresEntreTurnos` | 81,8 s | **narrado** | versão com voz PT-BR + sound design, construída com a skill `remotion-motion-graphics` |

Todo número vem de `src/data.ts` — a fonte única de verdade. Nenhum componente calcula dado.

## Rodar

```bash
npm install
npm run dev             # Remotion Studio
npm run render          # versão muda vertical
npm run render:narrado  # versão narrada (1080x1920, com áudio)
npm run render:wide     # versão muda 16:9
```

## Pipeline de voz (local, sem nuvem)

TTS: **Kokoro-82M** (ONNX, vozes PT-BR nativas) em venv isolado fora do repo.

```bash
# 1. ambiente (uma vez)
python -m venv ~/.tts-venv
~/.tts-venv/Scripts/python.exe -m pip install kokoro-onnx soundfile
# modelos (~338 MB) em ~/.tts-venv/models/

# 2. narração  -> public/audio/scene_NN.wav + narracao.json
~/.tts-venv/Scripts/python.exe tools/generate_voice.py --voice pm_alex

# 3. SFX sintetizado -> public/sfx/*.wav (zero downloads)
~/.tts-venv/Scripts/python.exe tools/generate_sfx.py

# 4. timeline: frames derivados da duração real do áudio -> src/timeline.ts
~/.tts-venv/Scripts/python.exe tools/build_timeline.py
```

Vozes PT-BR disponíveis: `pm_alex` (masculina), `pf_dora`, `pm_santa`. Trocar a voz é um
argumento — depois rode os passos 2 e 4 outra vez.

## Estrutura

| Arquivo | Papel |
|---|---|
| `src/data.ts` | Dados + classificação CONTAGEM DIRETA / ESTIMATIVA |
| `src/theme.ts` | Objeto único de tema: cores, fontes, easings, springs, áreas seguras |
| `src/timeline.ts` | **Gerado** a partir do áudio. Não editar à mão |
| `src/components/layers.tsx` | Pilha de 5 camadas: mesh, grade, grain, vinheta, entradas |
| `src/narrado/scenes.tsx` | 6 cenas da versão narrada |
| `src/narrado/Comp.tsx` | Timeline + trilha de voz + SFX |
| `src/scenes.tsx` | 7 cenas da versão muda |
| `tools/*.py` | Voz (Kokoro), SFX sintetizado, construtor de timeline |

## Regras de motion aplicadas (skill `remotion-motion-graphics`)

- Zero interpolação linear: entradas por `spring`, saídas por bezier `ease.in` e mais rápidas que as entradas.
- Entradas animam opacidade + subida + escala ao mesmo tempo.
- Stagger de 3–6 frames entre palavras e blocos.
- Pilha de 5 camadas em toda cena: mesh de fundo → conteúdo → grade → grão → vinheta.
- Uma cor-herói (âmbar `#F59E0B`) por frame; ciano `#22D3EE` só como acento.
- Timing derivado de `fps`, nunca de número mágico de frame.
- Render → extrair frames → inspecionar → corrigir → re-renderizar, sempre.

## Honestidade do dado

- **Contagem direta:** 116.480 novos eleitores, 92.000 seções, zero em 2018, 150 dias, +2.960.756 de comparecimento.
- **Estimativa:** a divisão por candidato (80/20). O log da urna não registra candidato — sigilo do voto, Art. 14 da CF/88. A cena 5 exibe esse aviso de forma permanente.
