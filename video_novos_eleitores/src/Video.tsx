import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from "remotion";
import { C, SAFE } from "./theme";
import { Gancho, Regra, Numero, Onde, Contraste, Divisao, Fecho } from "./scenes";

/** Offsets em frames (30fps). Total: 1140 frames = 38s */
const CENAS = [
  { Comp: Gancho, from: 0, dur: 150 },
  { Comp: Regra, from: 150, dur: 180 },
  { Comp: Numero, from: 330, dur: 210 },
  { Comp: Onde, from: 540, dur: 180 },
  { Comp: Contraste, from: 720, dur: 180 },
  { Comp: Divisao, from: 900, dur: 150 },
  { Comp: Fecho, from: 1050, dur: 90 },
] as const;

/** Trilha de progresso: 7 segmentos, um por cena */
const Trilha: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        position: "absolute",
        top: 96,
        left: SAFE.x,
        right: SAFE.x,
        display: "flex",
        gap: 10,
      }}
    >
      {CENAS.map(({ from, dur }, i) => {
        const w = interpolate(f, [from, from + dur], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={from}
            style={{
              flex: 1,
              height: 3,
              background: "rgba(148,163,184,0.14)",
              borderRadius: 2,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${w * 100}%`,
                height: "100%",
                background: i === CENAS.length - 1 ? C.amber : C.cyan,
                opacity: 0.85,
              }}
            />
          </div>
        );
      })}
    </div>
  );
};

export const Video: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#060A0E" }}>
    {CENAS.map(({ Comp, from, dur }) => (
      <Sequence key={from} from={from} durationInFrames={dur}>
        <Comp />
      </Sequence>
    ))}
    <Trilha />
  </AbsoluteFill>
);
