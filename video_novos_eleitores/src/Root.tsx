import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import { Narrado } from "./narrado/Comp";
import { TOTAL_FRAMES } from "./timeline";

/**
 * NovosEleitores       — versão muda, 38s, 1080x1920
 * NovosEleitoresWide   — versão muda, 16:9
 * EleitoresEntreTurnos — versão NARRADA, duração derivada do áudio real
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
  </>
);
