# Vídeos de teste — organizados por repositório

Cada subpasta é nomeada pelo repositório (ou skill local) que produziu o vídeo.

| pasta | arquivo | descrição | dur | resolução | áudio |
|---|---|---|---|---|---|
| `3b1b-manim` | `manim_novos_eleitores_apresentacao.mp4` | apresentação em 4 atos | 47.97s | 1080x1920 | sim |
| `cth9191-animate` | `animate-math-caderno-1080x1920.mp4` | estilo math · cópia do export multi-formato | 12.00s | 1080x1920 | sim |
| `cth9191-animate` | `animate-math-caderno-1080x1920-narrado.mp4` | mesma peça · **sem trilha, com locução** (idêntica ao `9x16-narrado`: SSIM 1,0 nos 288 quadros) | 12.00s | 1080x1920 | sim (voz) |
| `cth9191-animate` | `animate-math-caderno-9x16.mp4` | estilo math · 9:16 | 12.00s | 1080x1920 | sim |
| `cth9191-animate` | `animate-math-caderno-9x16-narrado.mp4` | mesma peça · **sem trilha, com locução em 2 cenas** | 12.00s | 1080x1920 | sim (voz) |
| `heygen-com-hyperframes` | `hyperframes-registry-16s.mp4` | blocks mk-progress-stat + split-flap | 16.00s | 1920x1080 | sim |
| `heygen-com-hyperframes` | `hyperframes-registry-16s-narrado.mp4` | mesma peça · **sem trilha, com locução** | 16.00s | 1920x1080 | sim (voz) |
| `heygen-com-hyperframes-launches` | `hyperframes-launches-caderno-24s.mp4` | 6 cenas no padrão dos launches | 24.00s | 1920x1080 | sim |
| `howseen-ai-claude-motion-design` | `motion-design-caderno-4x5.mp4` | film 4:5 · seek(t) | 16.00s | 1080x1350 | sim |
| `howseen-ai-claude-motion-design` | `motion-design-caderno-4x5-narrado.mp4` | mesma peça · **sem trilha, com locução em 4 atos** | 16.00s | 1080x1350 | sim (voz) |
| `iart-ai-motion-skills` | `motion-skills-chart-15s.mp4` | skill chart-animation | 15.00s | 1920x1080 | sim |
| `motion-video-kit` | `kit_launch_film_novos_eleitores.mp4` | launch film (.motion-video-kit) · **re-cortado na voz** | 23.70s | 1920x1080 | sim |
| `nateherkai-hyperframes-student-kit` | `herk-edit-kit-auditoria-18s-mudo.mp4` | auditoria 18 s · sem áudio | 18.00s | 1920x1080 | não |
| `nateherkai-hyperframes-student-kit` | `herk-edit-kit-auditoria-18s.mp4` | auditoria 18 s · narrada | 18.00s | 1920x1080 | sim |
| `nateherkai-hyperframes-student-kit` | `herk-edit-kit-auditoria-18s-v2.mp4` | **locução aprimorada**: 5 frases, sem trilha, sem aceleração | 18.00s | 1920x1080 | sim (voz) |
| `opus-video-skills` | `reel_novos_eleitores_kinetic.mp4` | skill kinetic-reel (.opus-video-skills) | 31.81s | 1920x1080 | sim |
| `opus-video-skills` | `reel_novos_eleitores_kinetic_narracao.mp4` | mesma peça · **só narração, sem trilha** | 31.80s | 1920x1080 | sim (voz) |
| `remotion-dev-remotion` | `eleitores_entre_turnos_narrado.mp4` | EleitoresEntreTurnos · narrada (Kokoro) | 81.80s | 1080x1920 | sim |
| `remotion-dev-remotion` | `historia_novos_eleitores.mp4` | HistoriaEleitores · 5 atos | 86.20s | 1080x1920 | sim |
| `remotion-dev-remotion` | `novos_eleitores_entre_turnos.mp4` | NovosEleitores · 38 s · muda | 38.00s | 1080x1920 | não |
| `remotion-dev-remotion` | `opuscar_novos_eleitores.mp4` | OpuscarNovosEleitores · modelo Opuscar | 38.50s | 1080x1920 | sim |
| `remotion-dev-remotion` | `remotion-transitions-15s.mp4` | TransitionsFilm · @remotion/transitions + shapes | 15.60s | 1920x1080 | sim |
| `theatre-js` | `theatre_novos_eleitores.mp4` | peça Theatre.js (@theatre/core) | 22.60s | 1080x1920 | sim |

## Onde cada peça foi construída

| pasta | código-fonte do build |
|---|---|
| `remotion-dev-remotion` | `video_novos_eleitores/src/` (composições `NovosEleitores`, `EleitoresEntreTurnos`, `HistoriaEleitores`, `OpuscarNovosEleitores`, `TransitionsFilm`) |
| `heygen-com-hyperframes` | `herk/video-projects/registry-film/` (blocks instalados via `hyperframes add`) |
| `heygen-com-hyperframes-launches` | `herk/video-projects/caderno-launch/` (6 cenas no padrão dos launches) |
| `nateherkai-hyperframes-student-kit` | `herk/video-projects/auditoria-caderno/` |
| `cth9191-animate` | `ani/pieces/caderno/` (estilo `math`) |
| `howseen-ai-claude-motion-design` | `cmd/films/caderno/` (`film.html` + `render.py`) |
| `iart-ai-motion-skills` | `video_novos_eleitores/src/chart/Comp.tsx` (composição `ChartFilm`) |
| `3b1b-manim` | `manim_novos_eleitores/` (saída em `media/videos/scene/1920p30/`) |
| `opus-video-skills` | `.opus-video-skills/skills/kinetic-reel/` |
| `motion-video-kit` | `.motion-video-kit/business-motion-film/` |
| `theatre-js` | `video_novos_eleitores/src/theatre/` |

## Observações

- **Duplicatas intencionais:** `cth9191-animate` tem dois arquivos de 12 s e mesma resolução, mas encodes diferentes — são o `final.mp4` e o `final-1080x1920.mp4` que o export multi-formato gerou.
- **Arquivos não movidos:** as pastas de build (`herk/video-projects/*/renders/`, `video_novos_eleitores/out/`, `cmd/films/caderno/out/`, `ani/pieces/caderno/renders/`) mantêm suas cópias de trabalho. Elas ficam nos clones/ferramentas (todos no `.gitignore`) e não são entregas.
- **`media/videos/.../partial_movie_files/`:** centenas de clipes parciais do Manim; são cache do renderizador, não vídeos finais.
