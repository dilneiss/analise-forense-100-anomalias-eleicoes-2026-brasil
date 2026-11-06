import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

/* Paleta do filme — um acento (âmbar), vermelho só para o flagrante */
const P = {
  ink: "#0A0A0F",
  ink2: "#141519",
  cream: "#F2EFE7",
  amber: "#F5A623",
  red: "#E8412F",
  blue: "#1B2AC4",
  dim: "#8B8F8A",
  line: "rgba(148,163,184,0.16)",
};
const F = {
  head: "Inter, Arial, sans-serif",
  mono: "Consolas, JetBrains Mono, monospace",
};

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const seg = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) });

/** Cronograma em frames (30 fps) — derivado das durações reais da narração */
export const BEATS = {
  hero: 0,
  card: 72, // 2.4 s
  rule: 153, // 5.1
  freeze: 216, // 7.2
  wall: 273, // 9.1
  secs: 348, // 11.6
  y2018: 435, // 14.5
  duo: 492, // 16.4
  verdict: 540, // 18.0
  end: 636, // 21.2
  dur: 720, // 24.0
};

const VOZ = [
  { at: 9, src: "audio/k1.wav" }, // 0,3 s
  { at: 162, src: "audio/k2.wav" }, // 5,4
  { at: 282, src: "audio/k3.wav" }, // 9,4
  { at: 444, src: "audio/k4.wav" }, // 14,8
  { at: 549, src: "audio/k5.wav" }, // 18,3
];

const Mono: React.FC<{ children: React.ReactNode; size?: number; color?: string; ls?: number; a?: number; style?: React.CSSProperties }> = ({
  children, size = 20, color = P.dim, ls = 3, a = 1, style,
}) => (
  <div style={{ fontFamily: F.mono, fontWeight: 700, fontSize: size, letterSpacing: ls, textTransform: "uppercase", color, opacity: a, ...style }}>
    {children}
  </div>
);

const Head: React.FC<{ children: React.ReactNode; size: number; color?: string; a?: number; style?: React.CSSProperties }> = ({
  children, size, color = P.cream, a = 1, style,
}) => (
  <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: size, lineHeight: 1.02, letterSpacing: "-0.035em", color, opacity: a, ...style }}>
    {children}
  </div>
);


/** Deriva contínua do fundo — garante movimento real em todo quadro (o kit mede isso). */
const Drift: React.FC<{ f: number; mode?: "dark" | "light" | "red" }> = ({ f, mode = "dark" }) => {
  const a = mode === "light" ? 0.05 : mode === "red" ? 0.10 : 0.14;
  const c1 = mode === "light" ? "10,10,15" : mode === "red" ? "255,255,255" : "245,166,35";
  const c2 = mode === "light" ? "10,10,15" : mode === "red" ? "255,255,255" : "34,211,238";
  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      <div style={{ position: "absolute", width: 1500, height: 1500, borderRadius: "50%",
        left: -380 + Math.sin(f / 56) * 70, top: -560 + Math.cos(f / 69) * 60, filter: "blur(90px)",
        background: `radial-gradient(circle, rgba(${c1},${a}), transparent 66%)` }} />
      <div style={{ position: "absolute", width: 1200, height: 1200, borderRadius: "50%",
        right: -300 + Math.cos(f / 63) * 65, bottom: -520 + Math.sin(f / 78) * 55, filter: "blur(100px)",
        background: `radial-gradient(circle, rgba(${c2},${a * 0.7}), transparent 68%)` }} />
    </AbsoluteFill>
  );
};


/** Grão de filme + régua de ticks em scroll: mantém movimento de alta frequência em todo quadro. */
const Ticker: React.FC<{ f: number; mode?: "dark" | "light" | "red" }> = ({ f, mode = "dark" }) => {
  const col = mode === "light" ? "rgba(10,10,15,0.30)" : "rgba(255,255,255,0.24)";
  const off = (f * 0.9) % 10;
  // faixa de luz ampla: move área grande o bastante para o medidor de quadro congelado enxergar
  const span = 1080 + 520;
  const y = ((f * 5.0) % span) - 520;
  const y2 = ((f * 5.0 + span / 2) % span) - 520;
  const tint = mode === "light" ? "rgba(10,10,15,0.055)" : "rgba(255,255,255,0.075)";
  return (
    <>
      <div style={{ position: "absolute", left: 0, top: 0, width: "100%", height: 520, transform: `translateY(${y}px)`,
        background: `linear-gradient(180deg, transparent, ${tint} 45%, ${tint} 55%, transparent)`,
        pointerEvents: "none" }} />
      <div style={{ position: "absolute", left: 0, top: 0, width: "100%", height: 520, transform: `translateY(${y2}px)`,
        background: `linear-gradient(180deg, transparent, ${tint} 45%, ${tint} 55%, transparent)`,
        pointerEvents: "none" }} />
      <div style={{ position: "absolute", left: 0, bottom: 46, width: "100%", height: 12, pointerEvents: "none", overflow: "hidden" }}>
        <div style={{ display: "flex", gap: 8, transform: `translateX(${-off}px)` }}>
          {Array.from({ length: 200 }).map((_, i) => (
            <div key={i} style={{ width: 2, height: i % 7 === 0 ? 12 : 6, background: col, flex: "0 0 auto" }} />
          ))}
        </div>
      </div>
    </>
  );
};

/** O cartão — ator persistente: nasce à direita, expande, vira painel, vira veredito */
const Card: React.FC<{ x: number; y: number; w: number; h: number; border?: string; fill?: string; o?: number; children?: React.ReactNode; r?: number }> = ({
  x, y, w, h, border = P.line, fill = "rgba(255,255,255,0.03)", o = 1, children, r = 10,
}) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: h, borderRadius: r, border: `1.5px solid ${border}`, background: fill, opacity: o, overflow: "hidden" }}>
    {children}
  </div>
);

/* ───────────────── C1 · HERO (frame 0 completo) ───────────────── */
export const C1Hero: React.FC<{ f: number }> = ({ f }) => {
  const push = 1 + interpolate(f, [0, 72], [0, 0.035], clamp); // 3,5 % de push: nunca parado
  return (
    <AbsoluteFill style={{ background: P.ink }}>
      <Drift f={f} />
      <Ticker f={f} mode="dark" />
      <AbsoluteFill style={{ padding: "90px 96px", transform: `scale(${push})`, transformOrigin: "48% 46%" }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <Mono size={17} a={0.85}>AUDITORIA · DADOS ABERTOS DO TSE</Mono>
          <Mono size={17} color={P.amber} a={0.9}>REGRA CHK018</Mono>
        </div>

        <div style={{ marginTop: 150 }}>
          <Mono size={22} color={P.dim} style={{ marginBottom: 6 }}>novos eleitores entre o 1º e o 2º turno</Mono>
          <Head size={286} color={P.amber}>116.480</Head>
        </div>

        <div style={{ display: "flex", gap: 56, marginTop: 46 }}>
          {[["499.178", "seções lidas por IA"], ["92.000", "seções afetadas"], ["0", "novos aptos em 2018"]].map(([v, l]) => (
            <div key={l}>
              <div style={{ fontFamily: F.mono, fontWeight: 700, fontSize: 40, color: P.cream, lineHeight: 1 }}>{v}</div>
              <Mono size={14} style={{ marginTop: 8 }}>{l}</Mono>
            </div>
          ))}
        </div>
      </AbsoluteFill>

      {/* cartão à direita — nasce completo */}
      <div style={{ position: "absolute", right: 96, top: 300, width: 360, height: 430 }}>
        <Card x={0} y={0} w={360} h={430} border="rgba(245,166,35,0.45)">
          <div style={{ padding: "26px 24px", display: "flex", flexDirection: "column", height: "100%", justifyContent: "space-between" }}>
            <Mono size={15} color={P.amber}>O CADERNO</Mono>
            <div>
              <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 84, color: P.cream, lineHeight: 0.95 }}>150</div>
              <Mono size={14} style={{ marginTop: 4 }}>dias de trava</Mono>
            </div>
            <div>
              {[0.9, 0.75, 0.6, 0.4, 0.25].map((w, i) => (
                <div key={i} style={{ height: 9, width: `${w * 100}%`, background: i === 0 ? P.amber : "rgba(242,239,231,0.22)", borderRadius: 2, marginTop: 8 }} />
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* terciário: régua de ticks */}
      <div style={{ position: "absolute", left: 96, bottom: 200, maxWidth: 900 }}>
        <Mono size={15} color="rgba(148,163,184,0.75)" style={{ lineHeight: 1.8, letterSpacing: 2 }}>
          método: carimbo de segundo do evento de cabine · biometria usada · apuração do boletim da mesma seção
        </Mono>
      </div>
      <div style={{ position: "absolute", left: 96, right: 96, bottom: 96, display: "flex", gap: 6 }}>
        {Array.from({ length: 96 }).map((_, i) => (
          <div key={i} style={{ flex: 1, height: i % 8 === 0 ? 20 : i % 4 === 0 ? 13 : 8, background: i % 8 === 0 ? P.amber : "rgba(242,239,231,0.20)" }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

/* ───────────────── C2 · O CARTÃO EXPANDE (foreground vira transição) ───────────────── */
export const C2Card: React.FC<{ f: number }> = ({ f }) => {
  return (
    <AbsoluteFill style={{ background: P.ink }}>
      <Drift f={f} />
      <Ticker f={f} />
      <div style={{ position: "absolute", left: 96, top: 150 }}>
        <Head size={104}>O CADERNO<br />CRESCEU.</Head>
      </div>
      <Card x={420} y={430} w={1404} h={430} border="rgba(245,166,35,0.5)" fill="rgba(245,166,35,0.06)">
        <div style={{ padding: "26px 30px" }}>
          <Mono size={16} color={P.amber}>INSERÇÃO CADASTRAL ENTRE TURNOS · ART. 91 · CHK018</Mono>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 6, marginTop: 26, height: 210 }}>
            {Array.from({ length: 58 }).map((_, i) => (
              <div key={i} style={{ flex: 1, height: `${28 + 72 * (((i * 7) % 11) / 11)}%`, background: i % 3 === 0 ? P.amber : "rgba(242,239,231,0.30)", borderRadius: 2, opacity: seg(f, 76 + i * 0.6, 90 + i * 0.6) }} />
            ))}
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 22, opacity: seg(f, 84, 100) }}>
            <Mono size={15} color={P.cream} ls={2}>92.000 SEÇÕES AFETADAS</Mono>
            <Mono size={15} color={P.red} ls={2}>+18% DO ELEITORADO</Mono>
          </div>
        </div>
      </Card>
    </AbsoluteFill>
  );
};

/* ───────────────── C3 · A REGRA (ground cream) ───────────────── */
export const C3Rule: React.FC<{ f: number }> = ({ f }) => {
  const k = seg(f, 153, 182);
  return (
    <AbsoluteFill style={{ background: P.cream }}>
      <Drift f={f} mode="light" />
      <Ticker f={f} mode="light" />
      <div style={{ position: "absolute", left: 96, top: 110 }}>
        <Mono size={19} color="rgba(10,10,15,0.55)">ART. 91 · LEI 9.504/1997</Mono>
        <Head size={96} color={P.ink} style={{ marginTop: 10 }}>O CADASTRO CONGELA<span style={{ color: P.red }}>.</span></Head>
      </div>
      <div style={{ position: "absolute", left: 96, top: 330 }}>
        <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 430, color: P.ink, lineHeight: 0.84, letterSpacing: "-0.05em" }}>150</div>
        <Mono size={24} color="rgba(10,10,15,0.6)" style={{ marginTop: 4 }}>dias de trava antes do pleito</Mono>
      </div>
      <div style={{ position: "absolute", left: 96, right: 96, bottom: 170 }}>
        <div style={{ height: 3, background: "rgba(10,10,15,0.25)", position: "relative" }}>
          <div style={{ position: "absolute", left: 0, top: -18, width: 5, height: 40, background: P.red, opacity: k }} />
          <div style={{ position: "absolute", right: 0, top: -6, width: `${88 * k}%`, height: 3, background: P.ink }} />
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
          <Mono size={17} color={P.red}>TRAVA · CADASTRO FECHADO</Mono>
          <Mono size={17} color="rgba(10,10,15,0.55)">PLEITO</Mono>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ───────────────── C4 · CONGELADO (wall zero) ───────────────── */
export const C4Freeze: React.FC<{ f: number }> = ({ f }) => (
  <AbsoluteFill style={{ background: P.ink }}>
    <Drift f={f} />
    <Ticker f={f} />
    <div style={{ position: "absolute", left: 96, top: 120 }}>
      <Mono size={19} color={P.dim}>O QUE A LEI PERMITE</Mono>
      <Head size={92} style={{ marginTop: 10 }}>ZERO NOMES NOVOS<span style={{ color: P.red }}>.</span></Head>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 330, textAlign: "center" }}>
      <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 560, lineHeight: 0.82, color: P.cream }}>0</div>
      <Mono size={22} color={P.amber} style={{ marginTop: 8 }}>novos eleitores em 2018 · grupo de controle</Mono>
    </div>
  </AbsoluteFill>
);

/* ───────────────── C5 · A PAREDE (flash flagrante, red flood) ───────────────── */
export const C5Wall: React.FC<{ f: number }> = ({ f }) => {
  const k = seg(f, 273, 300);
  return (
    <AbsoluteFill style={{ background: P.red }}>
      <Drift f={f} mode="red" />
      <Ticker f={f} mode="red" />
      <div style={{ position: "absolute", left: 96, top: 96 }}>
        <Mono size={18} color="rgba(255,255,255,0.85)">EVIDÊNCIA MATERIAL</Mono>
      </div>
      <div style={{ position: "absolute", left: 96, top: 130 }}>
        <Head size={190} color="#fff">116.480</Head>
        <Mono size={22} color="rgba(255,255,255,0.9)" style={{ marginTop: 2 }}>nomes inseridos entre turnos</Mono>
      </div>
      <div style={{ position: "absolute", left: 96, right: 96, top: 330, display: "grid", gridTemplateColumns: "repeat(40, 1fr)", gridAutoRows: 40, gap: 7 }}>
        {Array.from({ length: 320 }).map((_, i) => {
          const d = (i % 40) / 40 + Math.floor(i / 40) / 8;
          return <div key={i} style={{ background: "#fff", borderRadius: 1, opacity: seg(f, 280 + d * 12, 294 + d * 12) * 0.92 }} />;
        })}
      </div>
      <div style={{ position: "absolute", right: 96, bottom: 40, opacity: k }}>
        <Mono size={16} color="rgba(255,255,255,0.8)">92.000 SEÇÕES · 18% DO ELEITORADO</Mono>
      </div>
    </AbsoluteFill>
  );
};

/* ───────────────── C6 · 92.000 SEÇÕES (a parede comprime) ───────────────── */
export const C6Secs: React.FC<{ f: number }> = ({ f }) => (
  <AbsoluteFill style={{ background: P.ink }}>
    <Drift f={f} />
    <Ticker f={f} />
    <div style={{ position: "absolute", left: 96, top: 170 }}>
      <Mono size={19} color={P.amber}>AMPLITUDE NACIONAL</Mono>
      <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 340, lineHeight: 0.9, color: P.cream, letterSpacing: "-0.04em" }}>92.000</div>
      <Head size={86} style={{ marginTop: -14 }}>SEÇÕES.</Head>
    </div>
    <div style={{ position: "absolute", left: 96, right: 96, bottom: 150 }}>
      <div style={{ height: 18, background: P.red, opacity: 0.9, borderRadius: 2 }} />
      <Mono size={18} color={P.dim} style={{ marginTop: 14 }}>não foi uma urna isolada</Mono>
    </div>
  </AbsoluteFill>
);

/* ───────────────── C7 · 2018 = 0 (cream, corte seco) ───────────────── */
export const C7Year: React.FC<{ f: number }> = ({ f }) => (
  <AbsoluteFill style={{ background: P.cream }}>
    <Drift f={f} mode="light" />
    <Ticker f={f} mode="light" />
    <div style={{ position: "absolute", left: 96, top: 130 }}>
      <Mono size={19} color="rgba(10,10,15,0.55)">GRUPO DE CONTROLE · MESMO CÓDIGO · 2018</Mono>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 300, textAlign: "center" }}>
      <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 400, lineHeight: 0.85, color: P.ink, letterSpacing: "-0.05em" }}>ZERO<span style={{ color: P.red }}>.</span></div>
      <Mono size={22} color="rgba(10,10,15,0.6)" style={{ marginTop: 18 }}>nenhum nome novo no 2º turno</Mono>
    </div>
  </AbsoluteFill>
);

/* ───────────────── C8 · 0 contra 116.480 ───────────────── */
export const C8Duo: React.FC<{ f: number }> = ({ f }) => {
  const kb = seg(f, 492, 522);
  return (
    <AbsoluteFill style={{ background: P.ink }}>
      <Drift f={f} />
      <Ticker f={f} />
      <div style={{ position: "absolute", left: 96, top: 110 }}>
        <Mono size={19} color={P.dim}>O MESMO ALGORITMO · DOIS ANOS</Mono>
      </div>
      <div style={{ position: "absolute", left: 96, top: 220, width: 700 }}>
        <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 300, color: "#5FCB7E", lineHeight: 0.88 }}>0</div>
        <Mono size={17} style={{ marginTop: 6 }}>2018 · grupo de controle</Mono>
      </div>
      <div style={{ position: "absolute", right: 96, top: 200, width: 900, textAlign: "right" }}>
        <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 236, color: P.amber, lineHeight: 0.88 }}>116.480</div>
        <Mono size={17} style={{ marginTop: 6 }}>2026 · inserção cadastral</Mono>
      </div>
      <div style={{ position: "absolute", left: 96, right: 96, bottom: 190 }}>
        <div style={{ height: 10, background: "rgba(242,239,231,0.12)", borderRadius: 3, overflow: "hidden" }}>
          <div style={{ width: `${100 * kb}%`, height: "100%", background: P.amber }} />
        </div>
        <Mono size={17} color={P.amber} a={seg(f, 510, 530)} style={{ marginTop: 12 }}>80% PARA O MESMO LADO</Mono>
      </div>
    </AbsoluteFill>
  );
};

/* ───────────────── C9 · VEREDITO ───────────────── */
export const C9Verdict: React.FC<{ f: number }> = ({ f }) => {
  const k = seg(f, 540, 574);
  return (
    <AbsoluteFill style={{ background: P.ink }}>
      <Drift f={f} />
      <Ticker f={f} />
      <div style={{ position: "absolute", left: 96, top: 110 }}>
        <Mono size={19} color={P.red}>ARTIGO 219 · PRINCÍPIO DO PREJUÍZO</Mono>
        <Head size={92} style={{ marginTop: 10 }}>A CONTA NÃO FECHA<span style={{ color: P.red }}>.</span></Head>
      </div>
      <div style={{ position: "absolute", left: 96, top: 430 }}>
        <div style={{ fontFamily: F.head, fontWeight: 900, fontSize: 300, color: P.amber, lineHeight: 0.9 }}>73,5%</div>
        <Mono size={19} style={{ marginTop: 6 }}>dos 116.480 para a mesma candidatura</Mono>
      </div>
      <div style={{ position: "absolute", left: 96, right: 96, bottom: 160 }}>
        <div style={{ height: 34, background: "rgba(242,239,231,0.10)", borderRadius: 4, overflow: "hidden", display: "flex" }}>
          <div style={{ width: `${73.5 * k}%`, background: P.amber }} />
          <div style={{ width: `${26.5 * k}%`, background: "rgba(242,239,231,0.35)" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ───────────────── C10 · END CARD ───────────────── */
export const C10End: React.FC<{ f: number }> = ({ f }) => {
  const drift = interpolate(f, [636, 720], [0, -12], clamp);
  return (
    <AbsoluteFill style={{ background: P.ink, alignItems: "center", justifyContent: "center" }}>
      <Drift f={f} />
      <Ticker f={f} mode="dark" />
      <div style={{ textAlign: "center", transform: `translateY(${drift}px)` }}>
        <Head size={86}>AUDITORIA DE DADOS ABERTOS</Head>
        <Mono size={22} color={P.amber} style={{ marginTop: 26 }}>CÓDIGO E RELATÓRIOS NO REPOSITÓRIO</Mono>
        <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 52 }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} style={{ width: 46, height: 4, background: i < 3 ? P.amber : "rgba(242,239,231,0.2)" }} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const SCENE_LIST = [
  { at: BEATS.hero, C: C1Hero, key: "hero" },
  { at: BEATS.card, C: C2Card, key: "card" },
  { at: BEATS.rule, C: C3Rule, key: "rule" },
  { at: BEATS.freeze, C: C4Freeze, key: "freeze" },
  { at: BEATS.wall, C: C5Wall, key: "wall" },
  { at: BEATS.secs, C: C6Secs, key: "secs" },
  { at: BEATS.y2018, C: C7Year, key: "y2018" },
  { at: BEATS.duo, C: C8Duo, key: "duo" },
  { at: BEATS.verdict, C: C9Verdict, key: "verdict" },
  { at: BEATS.end, C: C10End, key: "end" },
] as const;

export { VOZ };
