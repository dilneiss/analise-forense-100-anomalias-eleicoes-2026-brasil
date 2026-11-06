import React from "react";
import { C, FONTS, FS } from "./theme";

/** Rótulo mono, uppercase, com tracking largo */
export const Rotulo: React.FC<{
  children: React.ReactNode;
  color?: string;
  size?: number;
  opacity?: number;
  align?: "center" | "left";
  maxWidth?: number;
}> = ({ children, color = C.muted, size = FS.mono, opacity = 1, align = "center", maxWidth }) => (
  <div
    style={{
      fontFamily: FONTS.mono,
      fontWeight: 700,
      fontSize: size,
      letterSpacing: "0.16em",
      textTransform: "uppercase",
      color,
      opacity,
      textAlign: align,
      lineHeight: 1.35,
      maxWidth,
      marginLeft: align === "center" ? "auto" : undefined,
      marginRight: align === "center" ? "auto" : undefined,
    }}
  >
    {children}
  </div>
);

/** Número-herói com formatação pt-BR */
export const Contador: React.FC<{
  value: string;
  size?: number;
  color?: string;
  glow?: number;
}> = ({ value, size = FS.hero, color = C.white, glow = 0.55 }) => (
  <div
    style={{
      fontFamily: FONTS.sans,
      fontWeight: 900,
      fontSize: size,
      letterSpacing: "-0.03em",
      color,
      lineHeight: 1,
      textShadow: `0 0 ${80 * glow}px rgba(34,211,238,${0.32 * glow})`,
      fontVariantNumeric: "tabular-nums",
    }}
  >
    {value}
  </div>
);

/** Grade de pontos representando as seções, acendendo em onda diagonal */
export const GridSecoes: React.FC<{ progress: number }> = ({ progress }) => {
  const cols = 40;
  const rows = 22;
  const size = 11;
  const gap = 9;
  const maxDiag = cols + rows - 2;
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${cols}, ${size}px)`,
        gap,
        justifyContent: "center",
      }}
    >
      {Array.from({ length: cols * rows }).map((_, i) => {
        const x = i % cols;
        const y = Math.floor(i / cols);
        const diag = (x + y) / maxDiag;
        // 60% dos pontos acendem
        const acesa = (x * 7 + y * 13) % 10 < 6;
        const local = Math.min(1, Math.max(0, (progress - diag * 0.55) / 0.28));
        return (
          <div
            key={i}
            style={{
              width: size,
              height: size,
              borderRadius: 3,
              background: acesa ? C.amber : "rgba(148,163,184,0.10)",
              opacity: acesa ? 0.15 + local * 0.85 : 0.5,
              transform: `scale(${acesa ? 0.7 + local * 0.3 : 1})`,
            }}
          />
        );
      })}
    </div>
  );
};

/** Duas barras verticais alinhadas pela base, para o contraste 2018 x 2026 */
export const BarraContraste: React.FC<{
  h2018: number;
  h2026: number;
  v2018: string;
  v2026: string;
}> = ({ h2018, h2026, v2018, v2026 }) => (
  <div style={{ display: "flex", alignItems: "flex-end", gap: 90, height: 780 }}>
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
      <div
        style={{
          fontFamily: FONTS.sans,
          fontWeight: 900,
          fontSize: 74,
          color: C.green,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {v2018}
      </div>
      <div
        style={{
          width: 190,
          height: Math.max(6, 620 * h2018),
          background: C.green,
          borderRadius: 6,
          opacity: 0.85,
        }}
      />
      <Rotulo color={C.green}>2018 · controle</Rotulo>
    </div>

    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
      <div
        style={{
          fontFamily: FONTS.sans,
          fontWeight: 900,
          fontSize: 74,
          color: C.white,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {v2026}
      </div>
      <div
        style={{
          width: 190,
          height: Math.max(6, 620 * h2026),
          background: C.red,
          borderRadius: 6,
        }}
      />
      <Rotulo color={C.red}>2026</Rotulo>
    </div>
  </div>
);

/** Duas faixas horizontais proporcionais (divisão estimada) */
export const FaixaSplit: React.FC<{
  progress: number;
  labelA: string;
  labelB: string;
  pctA?: number;
}> = ({ progress, labelA, labelB, pctA = 80 }) => {
  const p1 = Math.min(1, Math.max(0, progress / 0.55));
  const p2 = Math.min(1, Math.max(0, (progress - 0.45) / 0.55));
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 34, width: 820 }}>
      {[
        { label: labelA, pct: pctA, color: C.cyan, p: p1 },
        { label: labelB, pct: 100 - pctA, color: C.dim, p: p2 },
      ].map((b) => (
        <div key={b.label} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <Rotulo color={C.muted} size={26}>{b.label}</Rotulo>
            <Rotulo color={b.color} size={26}>{b.pct}%</Rotulo>
          </div>
          <div
            style={{
              height: 26,
              background: "rgba(148,163,184,0.10)",
              borderRadius: 4,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${b.pct * b.p}%`,
                height: "100%",
                background: b.color,
                borderRadius: 4,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};
