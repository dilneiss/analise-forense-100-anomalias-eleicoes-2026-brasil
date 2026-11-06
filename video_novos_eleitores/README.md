# Vídeo · Novos Eleitores entre Turnos (Remotion)

Vídeo de 38 segundos (1080×1920, 30 fps) sobre os **116.480 novos eleitores inseridos no caderno de votação entre o 1º e o 2º turno** de 2026.

Todo o dado vem de `src/data.ts`, que é a **fonte única de verdade**. Nenhum componente calcula número — apenas anima o que está lá.

## Rodar

```bash
npm install
npm run dev            # Remotion Studio (preview com scrubber)
npm run render         # out/video.mp4 (vertical 1080x1920)
npm run render:wide    # out/video_wide.mp4 (16:9 1920x1080)
npm run still          # out/frame.png (frame único para conferência)
```

Requer Node 18+ (testado em Node 24) e baixa o Chrome Headless Shell na primeira renderização.

## Estrutura

| Arquivo | Papel |
|---|---|
| `src/data.ts` | Dados + classificação CONTAGEM DIRETA / ESTIMATIVA |
| `src/theme.ts` | Cores, fontes, tipografia, áreas seguras |
| `src/svg.tsx` | Caderno isométrico, selo de cera, fundo com grão |
| `src/widgets.tsx` | Contador, grade de seções, barras, faixas |
| `src/scenes.tsx` | As 7 cenas animadas |
| `src/Video.tsx` | Timeline (`Sequence`) |
| `src/Root.tsx` | Composições registradas |

## Timeline (1140 frames)

| Cena | Frames | Duração | Conteúdo |
|---|:---:|:---:|---|
| 1 · Gancho | 0–150 | 5 s | "O caderno de votação mudou" |
| 2 · A regra | 150–330 | 6 s | Art. 91 / 150 dias de congelamento |
| 3 · O número | 330–540 | 7 s | Contador 0 → 116.480 |
| 4 · Onde | 540–720 | 6 s | 92 mil seções em grade |
| 5 · Contraste | 720–900 | 6 s | 2018 (zero) × 2026 |
| 6 · Divisão | 900–1050 | 5 s | 80% / 20% — **estimativa** |
| 7 · Fecho | 1050–1140 | 3 s | Fontes |

## Honestidade do dado

- **Contagem direta:** novos eleitores, seções afetadas, zero em 2018, 150 dias, aptos, comparecimentos.
- **Estimativa:** a divisão por candidato (80/20). O log da urna não registra candidato — sigilo do voto, Art. 14 da CF/88. A cena 6 exibe esse aviso de forma permanente e o vídeo não pode ser publicado sem ele.

Qualquer alteração de número deve ser feita **apenas** em `src/data.ts`.
