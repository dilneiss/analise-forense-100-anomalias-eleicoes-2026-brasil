import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { TIMELINE } from "../timeline";
import { Controle, Divisao, Fecho, Hook, Lei, Numero } from "./scenes";

const CENAS = {
  scene_01: Hook,
  scene_02: Lei,
  scene_03: Numero,
  scene_04: Controle,
  scene_05: Divisao,
  scene_06: Fecho,
} as const;

const atrasoVoz = 8; // a voz entra depois do corte, nunca junto

export const Narrado: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#0A0A0F" }}>
    <Audio src={staticFile("sfx/pad.wav")} volume={0.09} loop />

    {TIMELINE.map((cena) => {
      const Cena = CENAS[cena.id as keyof typeof CENAS];
      return (
        <Sequence key={cena.id} from={cena.from} durationInFrames={cena.dur}>
          <Cena />
          <Sequence from={atrasoVoz} durationInFrames={cena.falado + 12}>
            <Audio src={staticFile(cena.audio)} volume={1} />
          </Sequence>
        </Sequence>
      );
    })}

    {/* SFX: whoosh 4 frames antes de cada corte */}
    {TIMELINE.map((cena) => (
      <Sequence
        key={`w-${cena.id}`}
        from={Math.max(0, cena.from - 4)}
        durationInFrames={20}
      >
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.32} />
      </Sequence>
    ))}

    {/* impacto quando o número grande aterrissa */}
    <Sequence from={TIMELINE[2].from + 14} durationInFrames={30}>
      <Audio src={staticFile("sfx/impacto.wav")} volume={0.5} />
    </Sequence>

    {/* riser entrando no fecho */}
    <Sequence from={Math.max(0, TIMELINE[5].from - 42)} durationInFrames={48}>
      <Audio src={staticFile("sfx/riser.wav")} volume={0.28} />
    </Sequence>
  </AbsoluteFill>
);
