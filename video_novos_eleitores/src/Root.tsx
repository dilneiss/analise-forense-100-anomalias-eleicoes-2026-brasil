import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";

/**
 * Composição padrão: 1080x1920 (vertical, TikTok / Reels / Shorts).
 * Para 16:9, renderize NovosEleitoresWide.
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
  </>
);
