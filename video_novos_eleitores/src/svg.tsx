import React from "react";
import { interpolate } from "remotion";
import { C } from "./theme";

/** Fundo grafite com gradiente radial + grão fino determinístico */
export const Fundo: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: `radial-gradient(120% 80% at 50% 35%, ${C.bg1} 0%, ${C.bg0} 62%, #060A0E 100%)`,
    }}
  >
    <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.035 }}>
      <filter id="grao">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7" />
      </filter>
      <rect width="100%" height="100%" filter="url(#grao)" />
    </svg>
    {children}
  </div>
);

/** Caderno de votação em isometria, com linha de varredura ciano */
export const Caderno: React.FC<{ progress: number; scale?: number }> = ({ progress, scale = 1 }) => {
  const scanX = interpolate(progress, [0, 1], [-260, 300]);
  return (
    <svg
      viewBox="0 0 900 620"
      style={{ width: 900 * scale, height: 620 * scale, overflow: "visible" }}
    >
      <defs>
        <linearGradient id="capa" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#1E293B" />
          <stop offset="100%" stopColor="#0F172A" />
        </linearGradient>
        <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={C.cyan} stopOpacity="0" />
          <stop offset="50%" stopColor={C.cyan} stopOpacity="0.85" />
          <stop offset="100%" stopColor={C.cyan} stopOpacity="0" />
        </linearGradient>
        <linearGradient id="lombo" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#334155" />
          <stop offset="100%" stopColor="#1E293B" />
        </linearGradient>
        <clipPath id="capaClip">
          <polygon points="150,180 600,90 760,240 310,330" />
        </clipPath>
      </defs>

      {/* espessura da lombada */}
      <polygon points="150,180 310,330 310,392 150,242" fill="url(#lombo)" />
      {/* corte das páginas */}
      <polygon points="760,240 760,302 310,392 310,330" fill="#0B1220" />
      <polygon points="310,330 760,240 760,252 310,342" fill="#1F2937" opacity="0.6" />
      {/* capa */}
      <polygon points="150,180 600,90 760,240 310,330" fill="url(#capa)" />
      <polygon
        points="150,180 600,90 760,240 310,330"
        fill="none"
        stroke={C.line}
        strokeWidth="2"
      />

      {/* linhas de registro na capa */}
      <g clipPath="url(#capaClip)" opacity="0.22">
        {Array.from({ length: 9 }).map((_, i) => (
          <line
            key={i}
            x1={180 + i * 26}
            y1={168 + i * 14}
            x2={470 + i * 26}
            y2={78 + i * 14}
            stroke={C.muted}
            strokeWidth="1.5"
          />
        ))}
      </g>

      {/* varredura ciano */}
      <g clipPath="url(#capaClip)">
        <rect x={scanX} y={70} width="26" height="300" fill="url(#scan)" />
      </g>

    </svg>
  );
};
