import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { Entrance, Stack, useExit, WordReveal } from "../components/layers";
import { DADOS, fmt } from "../data";

const { colors: K, fonts: F, size: S, safe } = theme;

const Wrap: React.FC<{ children: React.ReactNode; gap?: number }> = ({ children, gap = 24 }) => (
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

const Rotulo: React.FC<{
  children: React.ReactNode;
  color?: string;
  size?: number;
  max?: number;
  style?: React.CSSProperties;
}> = ({ children, color = K.textDim, size = S.mono, max, style }) => (
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
      ...style,
    }}
  >
    {children}
  </div>
);
export const Ato1Regra: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  // Animação da curva descendente de 37 anos
  const pathProg = interpolate(frame, [20, 140], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={20}>
          <Entrance delay={0} preset="snappy">
            <Rotulo color={K.accent}>série histórica oficial (1989 a 2018)</Rotulo>
          </Entrance>

          <Entrance delay={8} preset="smooth">
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 56,
                color: K.text,
                textAlign: "center",
                lineHeight: 1.15,
                maxWidth: 820,
                letterSpacing: "-0.02em",
              }}
            >
              A REGRA DE QUATRO DÉCADAS
            </div>
          </Entrance>

          <Entrance delay={18}>
            <Rotulo color={K.primary} size={27} max={840}>
              o comparecimento sempre cai no 2º turno
            </Rotulo>
          </Entrance>

          {/* Gráfico SVG de curva descendente suave */}
          <div style={{ marginTop: 40, width: 840, height: 260, position: "relative" }}>
            <svg viewBox="0 0 840 260" style={{ width: "100%", height: "100%", overflow: "visible" }}>
              <defs>
                <linearGradient id="curveGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor={K.ok} />
                  <stop offset="100%" stopColor={K.accent} />
                </linearGradient>
              </defs>
              <line x1="40" y1="220" x2="800" y2="220" stroke={K.line} strokeWidth="2" strokeDasharray="6 6" />
              <path
                d="M 60 50 Q 250 80, 450 140 T 780 210"
                fill="none"
                stroke="url(#curveGrad)"
                strokeWidth="6"
                strokeDasharray="1000"
                strokeDashoffset={1000 * (1 - pathProg)}
                strokeLinecap="round"
              />
              {/* Pontos históricos */}
              {[
                { x: 60, y: 50, l: "1989" },
                { x: 260, y: 85, l: "2002" },
                { x: 440, y: 135, l: "2010" },
                { x: 780, y: 210, l: "2018" },
              ].map((p, i) => (
                <g key={p.l} opacity={pathProg > i * 0.25 ? 1 : 0}>
                  <circle cx={p.x} cy={p.y} r="8" fill={K.ok} />
                  <circle cx={p.x} cy={p.y} r="14" fill={K.ok} opacity="0.3" />
                  <text x={p.x} y={p.y - 18} fill={K.textDim} fontSize="20" fontFamily={F.mono} textAnchor="middle" fontWeight="bold">
                    {p.l}
                  </text>
                </g>
              ))}
            </svg>
          </div>

          <Entrance delay={70} style={{ marginTop: 20 }}>
            <Rotulo size={26} max={740}>
              retração natural: de 1,4 milhão a 4,5 milhões de eleitores a menos
            </Rotulo>
          </Entrance>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── ATO 2: A RUPTURA DE 2026 ───────────────────────── */
export const Ato2Ruptura: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  const valor = interpolate(
    spring({ frame: frame - 14, fps, config: { damping: 28, stiffness: 50 } }),
    [0, 1],
    [0, 2960756]
  );
  const pulse = Math.sin(frame / 18) * 0.015;

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={20}>
          <Entrance delay={0}>
            <Rotulo color={K.alert}>outubro de 2026 • a quebra do padrão</Rotulo>
          </Entrance>

          <Entrance delay={8} preset="smooth">
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 52,
                color: K.text,
                textAlign: "center",
                lineHeight: 1.15,
                maxWidth: 800,
              }}
            >
              A RUPTURA DEMOGRÁFICA
            </div>
          </Entrance>

          <div style={{ transform: `scale(${1 + pulse})`, marginTop: 30 }}>
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 160,
                color: K.primary,
                lineHeight: 0.95,
                letterSpacing: "-0.04em",
                fontVariantNumeric: "tabular-nums",
                textShadow: `0 0 90px ${K.glow}`,
                textAlign: "center",
              }}
            >
              +{fmt(valor)}
            </div>
          </div>

          <Entrance delay={30}>
            <Rotulo color={K.primary} size={28} max={840}>
              novos votantes que surgiram no 2º turno
            </Rotulo>
          </Entrance>

          <Entrance delay={65} style={{ marginTop: 40 }}>
            <div style={{ background: "rgba(245,158,11,0.1)", border: `1.5px solid ${K.primary}`, borderRadius: 8, padding: "16px 24px" }}>
              <Rotulo color={K.text} size={26} max={700}>
                eleitores que não votaram no 1º turno compareceram atipicamente
              </Rotulo>
            </div>
          </Entrance>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── ATO 3: O PARADOXO DAS GARAGENS ───────────────────────── */
export const Ato3Onibus: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  const barraSalto = interpolate(
    spring({ frame: frame - 24, fps, config: theme.spring.smooth }),
    [0, 1],
    [0, 1]
  );

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={26}>
          <Entrance delay={0}>
            <Rotulo color={K.accent}>capitais metropolitanas • salvador, recife e fortaleza</Rotulo>
          </Entrance>

          <Entrance delay={8} preset="smooth">
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 50,
                color: K.text,
                textAlign: "center",
                lineHeight: 1.2,
                maxWidth: 820,
              }}
            >
              O PARADOXO DAS GARAGENS
            </div>
          </Entrance>

          {/* Cards Lado a Lado: Ônibus Retidos vs Comparecimento Subindo */}
          <div style={{ display: "flex", gap: 32, width: 840, marginTop: 20 }}>
            {/* Card 1: Ônibus (SVG limpo, zero emoji) */}
            <Entrance delay={16} style={{ flex: 1 }}>
              <div style={{ background: "rgba(239,68,68,0.1)", border: `2px solid ${K.alert}`, borderRadius: 10, padding: 20, textAlign: "center", height: 260, display: "flex", flexDirection: "column", justifyContent: "space-between", alignItems: "center" }}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={K.alert} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="15" rx="2" />
                  <circle cx="7" cy="18" r="2" />
                  <circle cx="17" cy="18" r="2" />
                  <line x1="3" y1="9" x2="21" y2="9" />
                  <line x1="1" y1="1" x2="23" y2="23" stroke="#ef4444" strokeWidth="2.5" />
                </svg>
                <Rotulo color={K.alert} size={25}>frotas retidas em garagens</Rotulo>
                <div style={{ fontSize: 18, color: K.textDim, fontFamily: F.mono }}>população da periferia sem transporte</div>
              </div>
            </Entrance>

            {/* Card 2: Comparecimento */}
            <Entrance delay={24} style={{ flex: 1 }}>
              <div style={{ background: "rgba(34,211,238,0.1)", border: `2px solid ${K.accent}`, borderRadius: 10, padding: 20, textAlign: "center", height: 260, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 54, color: K.accent, fontVariantNumeric: "tabular-nums" }}>
                  +{Math.round(barraSalto * 11)}%
                </div>
                <Rotulo color={K.accent} size={26}>salto no comparecimento</Rotulo>
                <div style={{ fontSize: 18, color: K.textDim, fontFamily: F.mono }}>+275.000 votos na manhã</div>
              </div>
            </Entrance>
          </div>

          <Entrance delay={60} style={{ marginTop: 24 }}>
            <Rotulo color={K.text} size={26} max={740}>
              menos condução nas ruas gerou um aumento inexplicável de votantes
            </Rotulo>
          </Entrance>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── ATO 4: A CAIXA-PRETA REVELA ───────────────────────── */
export const Ato4CaixaPreta: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames);

  const pulse = Math.sin(frame / 12) * 0.02;

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={24}>
          <Entrance delay={0}>
            <Rotulo color={K.primary}>telemetria oficial do arquivo logd.dat</Rotulo>
          </Entrance>

          <Entrance delay={8} preset="smooth">
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 50,
                color: K.text,
                textAlign: "center",
                lineHeight: 1.2,
                maxWidth: 820,
              }}
            >
              A FÍSICA DA CAIXA-PRETA
            </div>
          </Entrance>

          {/* Cronômetro de 4 segundos */}
          <div style={{ transform: `scale(${1 + pulse})`, marginTop: 20 }}>
            <div style={{ background: "rgba(0,0,0,0.6)", border: `2.5px solid ${K.alert}`, borderRadius: 16, padding: "24px 44px", textAlign: "center", boxShadow: `0 0 60px ${K.alert}33` }}>
              <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 120, color: K.alert, fontVariantNumeric: "tabular-nums", lineHeight: 1 }}>
                00:04s
              </div>
              <Rotulo color={K.text} size={24} style={{ marginTop: 10 }}>
                votos em esteira no horário de almoço
              </Rotulo>
            </div>
          </div>

          {/* O dado da biometria */}
          <Entrance delay={30} style={{ marginTop: 30 }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 72, color: K.text, fontVariantNumeric: "tabular-nums" }}>
                15.884.298
              </div>
              <Rotulo color={K.primary} size={26} max={720}>
                votos liberados por ano de nascimento (sem biometria)
              </Rotulo>
            </div>
          </Entrance>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};

/* ───────────────────────── ATO 5: O DESFECHO ARITMÉTICO ───────────────────────── */
export const Ato5Desfecho: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const exit = useExit(durationInFrames, 16);

  const barP = interpolate(frame, [14, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={exit}>
      <Stack>
        <Wrap gap={26}>
          <Entrance delay={0}>
            <Rotulo color={K.ok}>conclusão pericial de dados abertos</Rotulo>
          </Entrance>

          <Entrance delay={8} preset="smooth">
            <div
              style={{
                fontFamily: F.display,
                fontWeight: 900,
                fontSize: 50,
                color: K.text,
                textAlign: "center",
                lineHeight: 1.2,
                maxWidth: 820,
              }}
            >
              A CONTA NÃO FECHA
            </div>
          </Entrance>

          {/* Barra de Divisão dos 2,96M: 73,5% x 26,5% */}
          <div style={{ width: 820, marginTop: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
              <Rotulo color={K.primary} size={26}>candidatura A: 73,5%</Rotulo>
              <Rotulo color={K.textDim} size={26}>candidatura B: 26,5%</Rotulo>
            </div>
            <div style={{ width: "100%", height: 32, background: "rgba(255,255,255,0.08)", borderRadius: 6, overflow: "hidden", display: "flex" }}>
              <div style={{ width: `${73.5 * barP}%`, height: "100%", background: K.primary }} />
              <div style={{ width: `${26.5 * barP}%`, height: "100%", background: "rgba(148,163,184,0.3)" }} />
            </div>
          </div>

          {/* Card do Veredito no Voto Limpo */}
          <Entrance delay={40} style={{ marginTop: 30 }}>
            <div style={{ background: "rgba(16,185,129,0.12)", border: `2px solid ${K.ok}`, borderRadius: 12, padding: "20px 28px", textAlign: "center", boxShadow: `0 0 50px ${K.ok}33` }}>
              <div style={{ fontFamily: F.mono, fontWeight: 700, fontSize: 24, color: K.ok, letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 6 }}>
                placar no voto limpo auditável
              </div>
              <div style={{ fontFamily: F.display, fontWeight: 900, fontSize: 52, color: K.text }}>
                FLÁVIO BOLSONARO: 51,20%
              </div>
              <div style={{ fontSize: 22, color: K.textDim, fontFamily: F.mono, marginTop: 4 }}>
                folga legítima de +1,4M a +2,8M de votos
              </div>
            </div>
          </Entrance>

          <Entrance delay={80} style={{ marginTop: 20 }}>
            <Rotulo color={K.textDim} size={22} max={720}>
              artigo 219 do código eleitoral • princípio do prejuízo
            </Rotulo>
          </Entrance>
        </Wrap>
      </Stack>
    </AbsoluteFill>
  );
};
