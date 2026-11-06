import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

const inter = loadInter("normal", {
  weights: ["400", "700", "900"],
  subsets: ["latin"],
});

const mono = loadMono("normal", {
  weights: ["500", "700"],
  subsets: ["latin"],
});

export const FONTS = {
  sans: inter.fontFamily,
  mono: mono.fontFamily,
};

export const C = {
  bg0: "#0B0F14",
  bg1: "#111827",
  white: "#F8FAFC",
  muted: "#94A3B8",
  dim: "#64748B",
  cyan: "#22D3EE",
  amber: "#F59E0B",
  red: "#EF4444",
  green: "#10B981",
  line: "rgba(148,163,184,0.18)",
};

export const SAFE = {
  x: 100,
  top: 170,
  bottom: 190,
};

export const FS = {
  hero: 176,
  big: 120,
  title: 62,
  body: 44,
  mono: 30,
  micro: 26,
};
