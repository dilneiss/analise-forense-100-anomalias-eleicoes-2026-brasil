import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, interpolate, useCurrentFrame } from "remotion";
import { TIMELINE_HISTORIA } from "../story_timeline";
import { Ato1Regra, Ato2Ruptura, Ato3Onibus, Ato4CaixaPreta, Ato5Desfecho } from "./scenes";
import { theme } from "../theme";

const { colors: K, safe } = theme;

const ATOS = {
  ato_01: Ato1Regra,
  ato_02: Ato2Ruptura,
  ato_03: Ato3Onibus,
  ato_04: Ato4CaixaPreta,
  ato_05: Ato5Desfecho,
} as const;

const atrasoVoz = 8; // a voz entra 8 frames após o corte visual

/** Trilha de progresso: 5 segmentos, um para cada Ato */
const TrilhaHistoria: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        position: "absolute",
        top: 96,
        left: safe.x,
        right: safe.x,
        display: "flex",
        gap: 12,
        zIndex: 50,
      }}
    >
      {TIMELINE_HISTORIA.map((ato, i) => {
        const w = interpolate(f, [ato.from, ato.from + ato.dur], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={ato.id}
            style={{
              flex: 1,
              height: 4,
              background: "rgba(148,163,184,0.18)",
              borderRadius: 2,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${w * 100}%`,
                height: "100%",
                background: i === 4 ? K.ok : i === 1 ? K.alert : K.primary,
                opacity: 0.9,
              }}
            />
          </div>
        );
      })}
    </div>
  );
};

export const HistoriaVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#0A0A0F" }}>
    <TrilhaHistoria />
    {/* Trilha de fundo sutil (pad contínuo) */}
    <Audio src={staticFile("sfx/pad.wav")} volume={0.08} loop />

    {/* Os 5 Atos com suas cenas visuais e narrações sincronizadas */}
    {TIMELINE_HISTORIA.map((ato) => {
      const AtoComponente = ATOS[ato.id as keyof typeof ATOS];
      return (
        <Sequence key={ato.id} from={ato.from} durationInFrames={ato.dur}>
          <AtoComponente />
          {/* Narração masterizada em estúdio */}
          <Sequence from={atrasoVoz} durationInFrames={ato.falado + 12}>
            <Audio src={staticFile(ato.audio)} volume={1.0} />
          </Sequence>
        </Sequence>
      );
    })}

    {/* SFX: Whoosh de transição 4 frames antes de cada corte */}
    {TIMELINE_HISTORIA.map((ato) => (
      <Sequence
        key={`w-${ato.id}`}
        from={Math.max(0, ato.from - 4)}
        durationInFrames={20}
      >
        <Audio src={staticFile("sfx/whoosh.wav")} volume={0.28} />
      </Sequence>
    ))}

    {/* SFX: Impacto no Ato 2 quando os +2,96M aterrissam */}
    <Sequence from={TIMELINE_HISTORIA[1].from + 18} durationInFrames={30}>
      <Audio src={staticFile("sfx/impacto.wav")} volume={0.45} />
    </Sequence>

    {/* SFX: Impacto no Ato 4 quando o cronômetro de 4s aterrissa */}
    <Sequence from={TIMELINE_HISTORIA[3].from + 16} durationInFrames={30}>
      <Audio src={staticFile("sfx/impacto.wav")} volume={0.45} />
    </Sequence>

    {/* SFX: Riser na entrada do Ato 5 (fecho decisivo) */}
    <Sequence from={Math.max(0, TIMELINE_HISTORIA[4].from - 40)} durationInFrames={46}>
      <Audio src={staticFile("sfx/riser.wav")} volume={0.25} />
    </Sequence>
  </AbsoluteFill>
);
