import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import { Narrado } from "./narrado/Comp";
import { TOTAL_FRAMES } from "./timeline";
import { HistoriaVideo } from "./historia/Comp";
import { TOTAL_FRAMES_HISTORIA } from "./story_timeline";
import { OpuscarVideo } from "./opuscar/Comp";
import { TOTAL_FRAMES_OPUSCAR } from "./opuscar_timeline";

/**
 * NovosEleitores        — versão muda original (38s)
 * NovosEleitoresWide    — versão muda 16:9
 * EleitoresEntreTurnos  — versão narrada com voz Kokoro (81,8s)
 * HistoriaEleitores     — a história em 5 atos sobre o salto demográfico (86,2s)
 * OpuscarNovosEleitores — MODELO OPUSCAR (Visual Investigation): rápido 1.5x, pausas de 200ms, início com IA (38,5s)
 */
export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="NovosEleitores"
      component={Video}
      durationInFrames={1140}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="NovosEleitoresWide"
      component={Video}
      durationInFrames={1140}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="EleitoresEntreTurnos"
      component={Narrado}
      durationInFrames={TOTAL_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="HistoriaEleitores"
      component={HistoriaVideo}
      durationInFrames={TOTAL_FRAMES_HISTORIA}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="OpuscarNovosEleitores"
      component={OpuscarVideo}
      durationInFrames={TOTAL_FRAMES_OPUSCAR}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);
