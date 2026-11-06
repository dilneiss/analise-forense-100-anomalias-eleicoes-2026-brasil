import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import { BEATS, SCENE_LIST, VOZ } from "./scenes";

/**
 * Montagem: uma timeline só, cada composição é uma cena.
 * O "ator persistente" é o cartão do caderno; as composições se sucedem em cortes secos
 * com o foreground carregando a transição (regra 1 da gramática do kit).
 */
export const KitFilm: React.FC = () => {
  const f = useCurrentFrame();
  let idx = 0;
  for (let i = 0; i < SCENE_LIST.length; i++) if (f >= SCENE_LIST[i].at) idx = i;
  const Cena = SCENE_LIST[idx].C;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0A0F" }}>
      <Cena f={f} />

      {/* narração: entra 0,3 s depois de cada corte */}
      {VOZ.map((v) => (
        <Sequence key={v.src} from={v.at} durationInFrames={220}>
          <Audio src={staticFile(v.src)} volume={1} />
        </Sequence>
      ))}

      {/* um whoosh curto por transição real */}
      {SCENE_LIST.slice(1).map((s) => (
        <Sequence key={`w-${s.key}`} from={Math.max(0, s.at - 3)} durationInFrames={16}>
          <Audio src={staticFile("sfx/whoosh.wav")} volume={0.3} />
        </Sequence>
      ))}

      {/* leito musical contínuo, bem abaixo da voz */}
      <Audio src={staticFile("sfx/pad.wav")} volume={0.08} loop />
    </AbsoluteFill>
  );
};

export { BEATS };
