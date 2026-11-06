import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import * as theatrePkg from "@theatre/core";
import { THEATRE_STATE, FILM_SECONDS } from "./state";

/* Superfície mínima do @theatre/core que este filme usa (o pacote não expõe tipos CJS). */
type TheatreObject<T extends Record<string, number>> = { value: T };
type TheatreSheet = {
  sequence: { position: number };
  object: <T extends Record<string, number>>(name: string, props: T) => TheatreObject<T>;
};
type TheatreProject = { sheet: (name: string) => TheatreSheet };
type TheatreModule = { getProject: (id: string, config?: { state?: unknown }) => TheatreProject };
/* O pacote é CJS: no node vem como namespace, no bundle como { default }. Aceita os dois. */
const mod = theatrePkg as unknown as TheatreModule & { default?: TheatreModule };
const getProject = (mod.getProject ?? mod.default?.getProject) as TheatreModule["getProject"];
if (!getProject) throw new Error("@theatre/core: getProject não encontrado no módulo");

/* Uma única sequência do Theatre dita todo o movimento do filme. */
const project = getProject("ReelNovosEleitores", { state: THEATRE_STATE });
const sheet = project.sheet("Film");
const g = sheet.object("g", { push: 1, tick: 0, sweep: -700 });
const hero = sheet.object("hero", { cardX: -640, numS: 0.9 });
const rule = sheet.object("rule", { barH: 0, lockY: 0 });
const wall = sheet.object("wall", { reveal: 0 });
const secoes = sheet.object("secoes", { gridH: 1, zeroO: 0 });
const verdict = sheet.object("verdict", { fill: 0 });

const P = {
  ink: "#0A0A0F", panel: "#141519", cream: "#F5F2EA", amber: "#F5A623",
  red: "#E8412F", dim: "#8B8F8A", green: "#5FCB7E",
  mono: "Consolas, monospace", head: "Inter, Arial, sans-serif",
};

const W = 1080, H = 1920;

const Mono: React.FC<{ children: React.ReactNode; size?: number; color?: string; ls?: number; style?: React.CSSProperties }> = ({
  children, size = 26, color = P.dim, ls = 4, style,
}) => (
  <div style={{ fontFamily: P.mono, fontWeight: 700, fontSize: size, letterSpacing: ls, textTransform: "uppercase", color, ...style }}>
    {children}
  </div>
);

/** marca d'água de movimento: ticks em scroll, dirigidos por `g.tick` */
const Ticks: React.FC<{ tick: number; dark?: boolean }> = ({ tick, dark = true }) => (
  <div style={{ position: "absolute", left: 60, right: 60, bottom: 90, height: 16, overflow: "hidden" }}>
    <div style={{ display: "flex", gap: 10, transform: `translateX(${-(tick % 18)}px)` }}>
      {Array.from({ length: 90 }).map((_, i) => (
        <div key={i} style={{ width: 3, height: i % 6 === 0 ? 16 : 8, flex: "0 0 auto", background: dark ? "rgba(245,242,234,0.22)" : "rgba(10,10,15,0.25)" }} />
      ))}
    </div>
  </div>
);

export const TheatreFilm: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ── o seek: toda a animação vem daqui ────────────────────────────────
  sheet.sequence.position = Math.min(frame / fps, FILM_SECONDS);

  const G = g.value, HE = hero.value, RU = rule.value, WA = wall.value, SE = secoes.value, VE = verdict.value;
  const t = frame / fps;

  const push = G.push;
  const show = {
    hero: t < 5.1,
    rule: t >= 5.1 && t < 8.9,
    wall: t >= 8.9 && t < 14.0,
    secoes: t >= 14.0 && t < 17.5,
    verdict: t >= 17.5 && t < 21.0,
    end: t >= 21.0,
  };

  return (
    <AbsoluteFill style={{ background: show.rule || show.secoes ? P.cream : P.ink, transform: `scale(${push})`, transformOrigin: "50% 46%" }}>
      {/* ───────── HERO ───────── */}
      {show.hero && (
        <>
          <div style={{ position: "absolute", left: 60, top: 120 }}>
            <Mono color={P.amber}>AUDITORIA · DADOS ABERTOS</Mono>
          </div>
          <div style={{ position: "absolute", left: 60, top: 620, transform: `scale(${HE.numS})`, transformOrigin: "left center" }}>
            <Mono size={30} color={P.dim} style={{ marginBottom: 10 }}>novos eleitores entre turnos</Mono>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 206, lineHeight: 0.9, letterSpacing: "-0.05em", color: P.amber }}>116.480</div>
          </div>
          <div style={{ position: "absolute", left: 60, top: 1020, display: "flex", gap: 60 }}>
            {[["499.178", "seções lidas"], ["92.000", "seções afetadas"], ["0", "em 2018"]].map(([v, l]) => (
              <div key={l}>
                <div style={{ fontFamily: P.mono, fontWeight: 700, fontSize: 44, color: P.cream }}>{v}</div>
                <Mono size={18} style={{ marginTop: 8 }}>{l}</Mono>
              </div>
            ))}
          </div>
          {/* cartão: desliza de fora da tela — animado por keyframe */}
          <div style={{ position: "absolute", left: 60 + HE.cardX, top: 1200, width: 960, height: 300, borderRadius: 14, border: `2px solid rgba(245,166,35,0.5)`, background: "rgba(245,166,35,0.06)", padding: 30, boxSizing: "border-box" }}>
            <Mono size={24} color={P.amber}>o caderno de votação</Mono>
            <div style={{ display: "flex", alignItems: "flex-end", gap: 8, marginTop: 26, height: 170 }}>
              {Array.from({ length: 42 }).map((_, i) => (
                <div key={i} style={{ flex: 1, height: `${30 + 70 * (((i * 7) % 11) / 11)}%`, background: i % 3 === 0 ? P.amber : "rgba(245,242,234,0.28)", borderRadius: 3 }} />
              ))}
            </div>
          </div>
          <Ticks tick={G.tick} />
        </>
      )}

      {/* ───────── A LEI · 150 DIAS ───────── */}
      {show.rule && (
        <>
          <div style={{ position: "absolute", left: 60, top: 130 }}>
            <Mono color="rgba(10,10,15,0.6)">ART. 91 · LEI 9.504/1997</Mono>
          </div>
          <div style={{ position: "absolute", left: 60, top: 210 }}>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 150, lineHeight: 0.95, letterSpacing: "-0.04em", color: P.ink }}>O CADASTRO<br />CONGELA<span style={{ color: P.red }}>.</span></div>
          </div>
          {/* régua vertical: altura vem do keyframe barH */}
          <div style={{ position: "absolute", left: 150, top: 760, width: 12, height: 700, background: "rgba(10,10,15,0.12)", borderRadius: 6 }}>
            <div style={{ position: "absolute", bottom: 0, width: "100%", height: `${RU.barH * 100}%`, background: P.red, borderRadius: 6 }} />
          </div>
          <div style={{ position: "absolute", left: 210, top: 1200 + (1 - RU.lockY) * 40, opacity: RU.lockY }}>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 260, lineHeight: 0.9, color: P.ink }}>150</div>
            <Mono size={26} color="rgba(10,10,15,0.6)">dias de trava</Mono>
          </div>
          <Ticks tick={G.tick} dark={false} />
        </>
      )}

      {/* ───────── A PAREDE · 116.480 ───────── */}
      {show.wall && (
        <>
          <div style={{ position: "absolute", left: 60, top: 120 }}>
            <Mono color="rgba(255,255,255,0.9)">EVIDÊNCIA MATERIAL · CHK018</Mono>
          </div>
          <div style={{ position: "absolute", left: 60, top: 200 }}>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 230, lineHeight: 0.88, letterSpacing: "-0.05em", color: "#fff" }}>116.480</div>
            <Mono size={26} color="rgba(255,255,255,0.92)">nomes inseridos entre turnos</Mono>
          </div>
          <div style={{ position: "absolute", left: 60, right: 60, top: 620, display: "grid", gridTemplateColumns: "repeat(10, 1fr)", gap: 12 }}>
            {Array.from({ length: 80 }).map((_, i) => {
              const d = ((i % 10) / 10 + Math.floor(i / 10) / 8) / 2;
              const on = Math.max(0, Math.min(1, (WA.reveal - d) / 0.22));
              return <div key={i} style={{ height: 116, background: "#fff", borderRadius: 3, opacity: on * 0.94 }} />;
            })}
          </div>
          <div style={{ position: "absolute", left: 60, bottom: 200, opacity: WA.reveal }}>
            <Mono size={24} color="rgba(255,255,255,0.85)">92.000 SEÇÕES · 18% DO ELEITORADO</Mono>
          </div>
        </>
      )}

      {/* ───────── 2018 · ZERO ───────── */}
      {show.secoes && (
        <>
          <div style={{ position: "absolute", left: 60, top: 130 }}>
            <Mono color="rgba(10,10,15,0.6)">GRUPO DE CONTROLE · MESMO CÓDIGO</Mono>
          </div>
          {/* a parede comprime para uma faixa fina */}
          <div style={{ position: "absolute", left: 60, right: 60, top: 260, height: `${SE.gridH * 620}px`, background: P.red, borderRadius: 4, opacity: 0.9 }} />
          <div style={{ position: "absolute", left: 60, top: 900, opacity: SE.zeroO }}>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 292, lineHeight: 0.88, letterSpacing: "-0.05em", color: P.ink }}>ZERO<span style={{ color: P.red }}>.</span></div>
            <Mono size={28} color="rgba(10,10,15,0.62)">nenhum nome novo em 2018</Mono>
          </div>
          <Ticks tick={G.tick} dark={false} />
        </>
      )}

      {/* ───────── VEREDITO ───────── */}
      {show.verdict && (
        <>
          <div style={{ position: "absolute", left: 60, top: 130 }}>
            <Mono color={P.red}>ARTIGO 219 · PREJUÍZO</Mono>
          </div>
          <div style={{ position: "absolute", left: 60, top: 210 }}>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 150, lineHeight: 0.95, letterSpacing: "-0.04em", color: P.cream }}>A CONTA<br />NÃO FECHA<span style={{ color: P.red }}>.</span></div>
          </div>
          <div style={{ position: "absolute", left: 60, top: 780 }}>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 240, lineHeight: 0.9, color: P.amber }}>73,5%</div>
            <div style={{ position: "absolute", left: 0, top: 300 }}>
              <Mono size={26}>dos 116.480 para o mesmo lado</Mono>
            </div>
          </div>
          <div style={{ position: "absolute", left: 60, right: 60, bottom: 380, height: 40, background: "rgba(245,242,234,0.12)", borderRadius: 6, overflow: "hidden", display: "flex" }}>
            <div style={{ width: `${73.5 * VE.fill}%`, background: P.amber }} />
            <div style={{ width: `${26.5 * VE.fill}%`, background: "rgba(245,242,234,0.34)" }} />
          </div>
          <Ticks tick={G.tick} />
        </>
      )}

      {/* ───────── END CARD ───────── */}
      {show.end && (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontFamily: P.head, fontWeight: 900, fontSize: 92, lineHeight: 1.05, color: P.cream, letterSpacing: "-0.03em" }}>AUDITORIA DE<br />DADOS ABERTOS</div>
            <Mono size={24} color={P.amber} style={{ marginTop: 40 }}>código e relatórios no repositório</Mono>
          </div>
          <Ticks tick={G.tick} />
        </AbsoluteFill>
      )}

      {/* faixas de luz em varredura: movimento de área grande, sem quadro parado */}
      {[0, 960].map((off) => {
        const y = ((G.sweep + off) % 2740) - 760;
        return (
          <div key={off} style={{ position: "absolute", left: 0, top: 0, width: "100%", height: 760, transform: `translateY(${y}px)`, pointerEvents: "none",
            background: "linear-gradient(180deg, transparent, rgba(255,255,255,0.085) 42%, rgba(255,255,255,0.085) 58%, transparent)" }} />
        );
      })}

      {/* narração e leito */}
      {[
        [0.3, "audio/k1.wav"], [5.2, "audio/k2.wav"], [9.0, "audio/k3.wav"],
        [14.2, "audio/k4.wav"], [17.6, "audio/k5.wav"],
      ].map(([at, src]) => (
        <Sequence key={String(src)} from={Math.round(Number(at) * 30)} durationInFrames={220}>
          <Audio src={staticFile(String(src))} volume={1} />
        </Sequence>
      ))}
      <Audio src={staticFile("sfx/pad.wav")} volume={0.08} loop />
      {[0, 5.1, 8.9, 14.0, 17.5, 21.0].map((at) => (
        <Sequence key={`w${at}`} from={Math.max(0, Math.round(at * 30) - 3)} durationInFrames={16}>
          <Audio src={staticFile("sfx/whoosh.wav")} volume={0.3} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const THEATRE_W = W;
export const THEATRE_H = H;
export const THEATRE_FRAMES = Math.round(FILM_SECONDS * 30);
