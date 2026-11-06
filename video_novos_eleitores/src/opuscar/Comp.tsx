import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { TIMELINE_OPUSCAR } from "../opuscar_timeline";
import { Beat1IAOpen, Beat2Lei150d, Beat3Flagrante116k, Beat4Controle2018 } from "./scenes";

const BEATS = {
  beat_01_ia_open: Beat1IAOpen,
  beat_02_lei_150d: Beat2Lei150d,
  beat_03_flagrante_116k: Beat3Flagrante116k,
  beat_04_controle_2018: Beat4Controle2018,
} as const;

// Pausa de no máximo 200ms: a voz entra quase imediatamente (4 frames = 133ms)
const atrasoVozOpuscar = 4;

export const OpuscarVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#0B0C0E" }}>
    {/* Trilha de fundo investigativa (low drone / pad contínuo) */}
    <Audio src={staticFile("sfx/pad.wav")} volume={0.07} loop />

    {/* Os 4 Beats da Investigação Visual */}
    {TIMELINE_OPUSCAR.map((beat) => {
      const BeatComponente = BEATS[beat.id as keyof typeof BEATS];
      return (
        <Sequence key={beat.id} from={beat.from} durationInFrames={beat.dur}>
          <BeatComponente />
          {/* Narração rápida em 1.5x do Antonio */}
          <Sequence from={atrasoVozOpuscar} durationInFrames={beat.falado + 4}>
            <Audio src={staticFile(beat.audio)} volume={1.0} />
          </Sequence>
        </Sequence>
      );
    })}

    {/* SFX: Transição rápida / Whoosh cortando com precisão */}
    {TIMELINE_OPUSCAR.map((beat) => (
      <Sequence
        key={`sfx-${beat.id}`}
        from={Math.max(0, beat.from - 2)}
        durationInFrames={16}
      >
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.22} />
      </Sequence>
    ))}

    {/* SFX: Impacto no Beat 3 quando os 116.480 batem na tela */}
    <Sequence from={TIMELINE_OPUSCAR[2].from + 10} durationInFrames={25}>
      <Audio src={staticFile("sfx/impacto.wav")} volume={0.4} />
    </Sequence>

    {/* SFX: Riser antes da revelação do controle de 2018 */}
    <Sequence from={Math.max(0, TIMELINE_OPUSCAR[3].from - 30)} durationInFrames={36}>
      <Audio src={staticFile("sfx/riser.wav")} volume={0.22} />
    </Sequence>
  </AbsoluteFill>
);
