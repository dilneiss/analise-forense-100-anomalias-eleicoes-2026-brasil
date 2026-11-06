import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";
import { Easing } from "remotion";

const inter = loadInter("normal", { weights: ["400", "700", "900"], subsets: ["latin"] });
const mono = loadMono("normal", { weights: ["500", "700"], subsets: ["latin"] });

/**
 * Fonte única de verdade visual do projeto.
 * Regra da skill: nunca inline hex ou easing em componente.
 */
export const theme = {
  colors: {
    bg: "#0A0A0F",
    bgAlt: "#12121A",
    primary: "#F59E0B", // hero color — no máximo 1 elemento por frame
    accent: "#22D3EE",
    text: "#F8FAFC",
    textDim: "#94A3B8",
    textFaint: "#64748B",
    alert: "#EF4444",
    ok: "#10B981",
    line: "rgba(148,163,184,0.18)",
    glow: "rgba(245,158,11,0.40)",
  },
  fonts: {
    display: inter.fontFamily,
    body: inter.fontFamily,
    sans: inter.fontFamily,
    mono: mono.fontFamily,
  },
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1),
    inOut: Easing.bezier(0.83, 0, 0.17, 1),
    in: Easing.bezier(0.7, 0, 0.84, 0),
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 },
  },
  safe: { x: 96, top: 150, bottom: 210 },
  size: { hero: 168, big: 104, title: 62, body: 42, mono: 28, micro: 24 },
} as const;

/* Aliases mantidos para as composições anteriores não quebrarem. */
export const FONTS = theme.fonts;
export const SAFE = theme.safe;
export const FS = theme.size;
export const C = {
  ...theme.colors,
  bg0: theme.colors.bg,
  bg1: theme.colors.bgAlt,
  white: theme.colors.text,
  muted: theme.colors.textDim,
  dim: theme.colors.textFaint,
  cyan: theme.colors.accent,
  amber: theme.colors.primary,
  red: theme.colors.alert,
  green: theme.colors.ok,
};
