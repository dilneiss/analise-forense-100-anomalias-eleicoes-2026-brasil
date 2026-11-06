import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

/** Camada 1 — mesh de gradiente em deriva (nunca fundo chapado) */
export const BgMesh: React.FC<{ intensity?: number }> = ({ intensity = 1 }) => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 55) * 46;
  const d2 = Math.cos(frame / 72) * 38;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <div
        style={{
          position: "absolute",
          width: 1180,
          height: 1180,
          borderRadius: "50%",
          top: -520 + d1 * 0.4,
          left: -280 + d1,
          filter: "blur(60px)",
          opacity: intensity,
          background: `radial-gradient(circle, ${theme.colors.primary}22, transparent 62%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 900,
          borderRadius: "50%",
          bottom: -430 - d2 * 0.3,
          right: -240 - d2,
          filter: "blur(72px)",
          opacity: intensity,
          background: `radial-gradient(circle, ${theme.colors.accent}1F, transparent 65%)`,
        }}
      />
    </AbsoluteFill>
  );
};

/** Camada 4 — grade de cor (unifica tudo num look só) */
export const Grade: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill
      style={{
        backgroundColor: theme.colors.primary,
        mixBlendMode: "soft-light",
        opacity: 0.14,
      }}
    />
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(180deg, rgba(0,0,0,0.12), transparent 26%, transparent 70%, rgba(0,0,0,0.28))",
      }}
    />
  </AbsoluteFill>
);

/** Camada 5a — grão procedural com cintilação de filme */
export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const noise =
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E\")";
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        backgroundImage: noise,
        backgroundSize: "220px",
        backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
        opacity: 0.05,
        mixBlendMode: "overlay",
      }}
    />
  );
};

/** Camada 5b — vinheta (topo absoluto) */
export const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: "radial-gradient(ellipse at center, transparent 54%, rgba(0,0,0,0.28) 100%)",
    }}
  />
);

/** Pilha completa de 5 camadas para envolver qualquer cena */
export const Stack: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill>
    <BgMesh />
    {children}
    <Grade />
    <Grain />
    <Vignette />
  </AbsoluteFill>
);

/** Entrada premium: opacidade + subida + escala, via spring */
export const Entrance: React.FC<{
  delay?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
  preset?: keyof typeof theme.spring;
  rise?: number;
  scaleFrom?: number;
}> = ({ delay = 0, children, style, preset = "smooth", rise = 44, scaleFrom = 0.94 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring[preset] });
  return (
    <div
      style={{
        opacity: p,
        transform: `translateY(${interpolate(p, [0, 1], [rise, 0])}px) scale(${interpolate(
          p,
          [0, 1],
          [scaleFrom, 1],
        )})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Revelação palavra por palavra com stagger */
export const WordReveal: React.FC<{
  text: string;
  delay?: number;
  per?: number;
  hero?: string;
  style?: React.CSSProperties;
}> = ({ text, delay = 0, per = 3, hero, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 18, ...style }}>
      {text.split(" ").map((word, i) => {
        const p = spring({ frame: frame - delay - i * per, fps, config: theme.spring.snappy });
        const isHero = hero !== undefined && word.replace(/[.,:;]/g, "") === hero;
        return (
          <span
            key={`${word}-${i}`}
            style={{
              display: "inline-block",
              opacity: p,
              transform: `translateY(${interpolate(p, [0, 1], [34, 0])}px)`,
              color: isHero ? theme.colors.primary : undefined,
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

/** Saída: mais rápida que a entrada (10 frames) */
export const useExit = (durationInFrames: number, frames = 10) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [durationInFrames - frames, durationInFrames - 2], [1, 0], {
    easing: theme.ease.in,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [durationInFrames - frames, durationInFrames - 2], [0, -40], {
    easing: theme.ease.in,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return { opacity, transform: `translateY(${y}px)` };
};
