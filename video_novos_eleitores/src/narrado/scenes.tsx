import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { DADOS, fmt } from "../data";
import { theme } from "../theme";
import { Entrance, Stack, useExit, WordReveal } from "../components/layers";
import { BarraContraste, FaixaSplit, GridSecoes } from "../widgets";

const { colors: K, fonts: F, size: S, safe } = theme;

const Wrap: React.FC<{ children: React.ReactNode; gap?: number }> = ({ children, gap = 26 }) => (
  <AbsoluteFill
    style={{
      paddingLeft: safe.x,
      paddingRight: safe.x,
      paddingTop: safe.top,
      paddingBottom: safe.bottom,
      alignItems: "center",
      justifyContent: "center",
      gap,
    }}
  >
    {children}
  </AbsoluteFill>
);

const Rotulo: React.FC<{ children: React.ReactNode; color?: string; size?: number; max?: number }> = ({
  children,
  color = K.textDim,
  size = S.mono,
  max,
}) => (
  <div
    style={{
      fontFamily: F.mono,
      fontWeight: 700,
      fontSize: size,
      letterSpacing: "0.16em",
      textTransform: "uppercase",
      color,
      textAlign: "center",
      lineHeight: 1.4,
      maxWidth: max,
    }}
  >
    {children}
  </div>
);

/* ───────────────────────── 01 · GANCHO ───────────────────────── */
export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  // respiração do bloco maior
  const breathe = 1 + Math.sin(frame / 26) * 0.012;

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={8}>
          <Entrance delay={2} preset="snappy">
            <Rotulo>o caderno de votação entre turnos</Rotulo>
          </Entrance>

          <div style={{ display: "flex", alignItems: "flex-end", gap: 56, marginTop: 40 }}>
            <Entrance delay={10} preset="smooth" rise={30}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
                <div
                  style={{
                    fontFamily: F.display,
                    fontWeight: 900,
                    fontSize: 96,
                    color: K.ok,
                    lineHeight: 1,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {fmt(DADOS.controle2018)}
                </div>
                <Rotulo color={K.ok} size={26}>
                  2018
                </Rotulo>
              </div>
            </Entrance>

            <div
              style={{
                width: 2,
                height: 150,
                background: K.line,
                opacity: spring({ frame: frame - 18, fps, config: theme.spring.snappy }),
              }}
            />

            <Entrance delay={22} preset="smooth" style={{ transformOrigin: "bottom" }}>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 10,
                  transform: `scale(${breathe})`,
                }}
              >
                <div
                  style={{
                    fontFamily: F.display,
                    fontWeight: 900,
                    fontSize: 132,
                    color: K.primary,
                    lineHeight: 1,
                    letterSpacing: "-0.03em",
                    fontVariantNumeric: "tabular-nums",
                    textShadow: `0 0 70px ${K.glow}`,
                  }}
                >
                  {fmt(DADOS.novosEleitores)}
                </div>
                <Rotulo color={K.primary} size={26}>
                  2026
                </Rotulo>
              </div>
            </Entrance>
          </div>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── 02 · A LEI ───────────────────────── */
export const Lei: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  const dias = Math.round(
    interpolate(spring({ frame: frame - 14, fps, config: theme.spring.smooth }), [0, 1], [0, 150]),
  );
  const preenchido = interpolate(frame, [26, 110], [0, 1], {
    easing: theme.ease.out,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={30}>
          <Entrance delay={0}>
            <Rotulo>art. 91 · lei 9.504/1997</Rotulo>
          </Entrance>

          <Entrance delay={8} preset="smooth">
            <div style={{ display: "flex", alignItems: "baseline", gap: 20 }}>
              <div
                style={{
                  fontFamily: F.display,
                  fontWeight: 900,
                  fontSize: 210,
                  color: K.text,
                  lineHeight: 0.95,
                  letterSpacing: "-0.04em",
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {dias}
              </div>
              <div
                style={{
                  fontFamily: F.mono,
                  fontWeight: 700,
                  fontSize: 38,
                  letterSpacing: "0.2em",
                  color: K.primary,
                  paddingBottom: 40,
                }}
              >
                DIAS
              </div>
            </div>
          </Entrance>

          <Entrance delay={20}>
            <Rotulo color={K.text} size={34}>
              o cadastro está congelado
            </Rotulo>
          </Entrance>

          <div style={{ width: 820, marginTop: 46 }}>
            <div
              style={{
                display: "flex",
                gap: 3,
                height: 44,
                alignItems: "flex-end",
                opacity: 0.9,
              }}
            >
              {Array.from({ length: 150 }).map((_, i) => {
                const lit = i / 150 < preenchido;
                return (
                  <div
                    key={i}
                    style={{
                      flex: 1,
                      height: i % 10 === 0 ? 44 : 24,
                      borderRadius: 1,
                      background: lit ? K.accent : "rgba(148,163,184,0.16)",
                    }}
                  />
                );
              })}
            </div>
          </div>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── 03 · O NÚMERO ───────────────────────── */
export const Numero: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  const valor = interpolate(
    spring({ frame: frame - 12, fps, config: { damping: 30, stiffness: 52 } }),
    [0, 1],
    [0, DADOS.novosEleitores],
  );
  const grade = interpolate(frame, [50, 150], [0, 1], {
    easing: theme.ease.inOut,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const breathe = 1 + Math.sin(frame / 24) * 0.01;

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={24}>
          <Entrance delay={0}>
            <Rotulo max={900}>novos eleitores no caderno</Rotulo>
          </Entrance>

          <div style={{ transform: `scale(${breathe})` }}>
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: S.hero,
                color: K.primary,
                lineHeight: 1,
                letterSpacing: "-0.035em",
                fontVariantNumeric: "tabular-nums",
                textShadow: `0 0 80px ${K.glow}`,
              }}
            >
              {fmt(valor)}
            </div>
          </div>

          <Entrance delay={34}>
            <Rotulo color={K.text} size={30}>
              em {fmt(DADOS.secoesAfetadas)} seções eleitorais
            </Rotulo>
          </Entrance>

          <div style={{ opacity: 0.9, marginTop: 26 }}>
            <GridSecoes progress={grade} />
          </div>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── 04 · O CONTROLE ───────────────────────── */
export const Controle: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  const h2018 = interpolate(frame, [8, 34], [0, 0.012], {
    easing: theme.ease.out,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const h2026 = interpolate(
    spring({ frame: frame - 58, fps, config: theme.spring.smooth }),
    [0, 1],
    [0, 1],
  );

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={18}>
          <Entrance delay={0}>
            <Rotulo>mesmo cálculo · mesmo sistema · mesmo país</Rotulo>
          </Entrance>

          <Entrance delay={8}>
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 54,
                color: K.text,
                letterSpacing: "-0.02em",
                textAlign: "center",
              }}
            >
              novos aptos entre turnos
            </div>
          </Entrance>

          <div style={{ marginTop: 40 }}>
            <BarraContraste
              h2018={h2018}
              h2026={h2026}
              v2018={fmt(DADOS.controle2018)}
              v2026={fmt(DADOS.novosEleitores)}
            />
          </div>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── 05 · DIVISÃO ───────────────────────── */
export const Divisao: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  const p = interpolate(frame, [18, 120], [0, 1], {
    easing: theme.ease.out,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={30}>
          <Entrance delay={0}>
            <Rotulo max={720}>dos que compareceram</Rotulo>
          </Entrance>

          <FaixaSplit
            progress={p}
            labelA="LULA (13)"
            labelB="FLÁVIO (22)"
            pctA={DADOS.pctLula}
          />

          <Entrance delay={44} style={{ marginTop: 32 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
              <div style={{ width: 30, height: 2, background: K.primary }} />
              <Rotulo color={K.primary} size={21} max={620}>
                estimativa por boletim de urna — o log não registra candidato
              </Rotulo>
            </div>
          </Entrance>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── 06 · FECHO ───────────────────────── */
export const Fecho: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames, 14);

  const salto = interpolate(
    spring({ frame: frame - 8, fps: 30, config: theme.spring.smooth }),
    [0, 1],
    [0, DADOS.saltoComparecimento],
  );

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={26}>
          <Entrance delay={0}>
            <Rotulo>comparecimento nacional no pleito</Rotulo>
          </Entrance>

          <Entrance delay={6} preset="smooth">
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 128,
                color: K.primary,
                lineHeight: 1,
                letterSpacing: "-0.03em",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              +{fmt(salto)}
            </div>
          </Entrance>

          <Entrance delay={26}>
            <WordReveal
              text="cadastro congelado que cresceu. eleitorado que deveria encolher, cresceu."
              per={3}
              style={{
                fontFamily: F.display,
                fontWeight: 700,
                fontSize: 46,
                color: K.text,
                lineHeight: 1.25,
                maxWidth: 800,
              }}
            />
          </Entrance>

          <Entrance delay={72} style={{ marginTop: 60 }}>
            <Rotulo size={23} max={700}>
              fonte: arquivos públicos do TSE · dados abertos auditáveis
            </Rotulo>
          </Entrance>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};
