import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { DADOS, fmt } from "./data";
import { C, FONTS, FS, SAFE } from "./theme";
import { Caderno, Fundo } from "./svg";
import { BarraContraste, Contador, FaixaSplit, GridSecoes, Rotulo } from "./widgets";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const fadeIn = (f: number, start: number, dur = 22) =>
  interpolate(f, [start, start + dur], [0, 1], clamp);

const up = (f: number, start: number, dur = 22) =>
  interpolate(f, [start, start + dur], [26, 0], clamp);

const Wrap: React.FC<{ children: React.ReactNode; padTop?: number }> = ({
  children,
  padTop = 0,
}) => (
  <AbsoluteFill
    style={{
      paddingLeft: SAFE.x,
      paddingRight: SAFE.x,
      paddingTop: SAFE.top + padTop,
      paddingBottom: SAFE.bottom,
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    {children}
  </AbsoluteFill>
);

/* ─────────────────────────── CENA 1 · GANCHO ─────────────────────────── */
export const Gancho: React.FC = () => {
  const f = useCurrentFrame();
  const scan = interpolate(f, [8, 118], [0, 1], clamp);
  const out = interpolate(f, [138, 150], [1, 0], clamp);

  const lines = [
    { t: "ENTRE O 1º E O 2º TURNO", at: 14, color: C.muted, size: FS.mono },
    { t: "O CADERNO DE VOTAÇÃO", at: 32, color: C.white, size: FS.title },
    { t: "MUDOU.", at: 52, color: C.amber, size: FS.title },
  ];

  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Fundo>
        <Wrap>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
            {lines.map((l) => (
              <div
                key={l.t}
                style={{
                  opacity: fadeIn(f, l.at),
                  transform: `translateY(${up(f, l.at)}px)`,
                  fontFamily: l.size === FS.mono ? FONTS.mono : FONTS.sans,
                  fontWeight: 900,
                  fontSize: l.size,
                  letterSpacing: l.size === FS.mono ? "0.16em" : "-0.02em",
                  color: l.color,
                  textAlign: "center",
                  lineHeight: 1.2,
                }}
              >
                {l.t}
              </div>
            ))}

            <div style={{ marginTop: 90, opacity: 0.4 + scan * 0.6 }}>
              <Caderno progress={scan} scale={1} />
            </div>
          </div>
        </Wrap>
      </Fundo>
    </AbsoluteFill>
  );
};

/* ─────────────────────────── CENA 2 · A REGRA ─────────────────────────── */
export const Regra: React.FC = () => {
  const f = useCurrentFrame();

  const ruler = interpolate(f, [12, 104], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const dias = Math.round(interpolate(f, [12, 104], [0, DADOS.prazoLegalDias], clamp));
  const ticks = DADOS.prazoLegalDias;

  return (
    <AbsoluteFill>
      <Fundo>
        <Wrap>
          <div style={{ opacity: fadeIn(f, 0), transform: `translateY(${up(f, 0)}px)` }}>
            <Rotulo color={C.muted}>a lei congela o cadastro</Rotulo>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 22,
              marginTop: 54,
              opacity: fadeIn(f, 10),
            }}
          >
            <Contador value={String(dias)} size={250} glow={0.4} />
            <div
              style={{
                fontFamily: FONTS.mono,
                fontWeight: 700,
                fontSize: 42,
                letterSpacing: "0.18em",
                color: C.cyan,
                paddingBottom: 34,
              }}
            >
              DIAS
            </div>
          </div>

          <div style={{ opacity: fadeIn(f, 34), marginTop: 14 }}>
            <Rotulo color={C.white} size={38}>
              antes da eleição
            </Rotulo>
          </div>

          <div
            style={{
              display: "flex",
              gap: 3,
              width: 820,
              height: 30,
              alignItems: "flex-end",
              marginTop: 84,
              opacity: fadeIn(f, 6),
            }}
          >
            {Array.from({ length: ticks }).map((_, i) => {
              const lit = i / ticks < ruler;
              const alt = i % 10 === 0 ? 30 : 18;
              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    height: alt,
                    borderRadius: 1,
                    background: lit ? C.cyan : "rgba(148,163,184,0.16)",
                    opacity: lit ? 0.92 : 1,
                  }}
                />
              );
            })}
          </div>

          <div style={{ marginTop: 46, opacity: fadeIn(f, 62) }}>
            <Rotulo color={C.amber} size={30}>
              art. 91 · lei 9.504/1997
            </Rotulo>
          </div>
        </Wrap>
      </Fundo>
    </AbsoluteFill>
  );
};

/* ─────────────────────────── CENA 3 · O NÚMERO ─────────────────────────── */
export const Numero: React.FC = () => {
  const f = useCurrentFrame();

  const cont = interpolate(f, [18, 138], [0, DADOS.novosEleitores], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });
  const p = interpolate(f, [18, 138], [0, 1], clamp);
  // pulso a cada dezena de milhar (11 pulsos na contagem)
  const pulse = Math.pow(Math.max(0, Math.cos(p * Math.PI * 11)), 6);

  const valorCor = pulse > 0.35 ? C.amber : C.white;

  return (
    <AbsoluteFill>
      <Fundo>
        <Wrap>
          <div style={{ opacity: fadeIn(f, 2), marginBottom: 26 }}>
            <Rotulo color={C.amber} size={27} maxWidth={780}>
              novos eleitores inseridos entre turnos
            </Rotulo>
          </div>

          <div style={{ transform: `scale(${1 + pulse * 0.012})` }}>
            <Contador value={fmt(cont)} color={valorCor} glow={0.4 + pulse * 0.6} />
          </div>

          <div style={{ marginTop: 34, opacity: fadeIn(f, 96) }}>
            <Rotulo color={C.muted} size={30}>
              em {fmt(DADOS.secoesAfetadas)} seções
            </Rotulo>
          </div>

          <div
            style={{
              marginTop: 120,
              height: 2,
              width: interpolate(f, [110, 170], [0, 620], clamp),
              background: `linear-gradient(90deg, transparent, ${C.cyan}, transparent)`,
              opacity: 0.6,
            }}
          />
        </Wrap>
      </Fundo>
    </AbsoluteFill>
  );
};

/* ─────────────────────────── CENA 4 · ONDE ─────────────────────────── */
export const Onde: React.FC = () => {
  const f = useCurrentFrame();
  const g = interpolate(f, [14, 128], [0, 1], { ...clamp, easing: Easing.inOut(Easing.quad) });

  return (
    <AbsoluteFill>
      <Fundo>
        <Wrap>
          <div style={{ opacity: fadeIn(f, 0), marginBottom: 30 }}>
            <Rotulo color={C.white} size={FS.title}>
              {fmt(DADOS.secoesAfetadas)} SEÇÕES
            </Rotulo>
          </div>

          <div style={{ opacity: fadeIn(f, 10), marginBottom: 60 }}>
            <Rotulo color={C.dim} size={26}>
              cada ponto é uma seção · em âmbar, as que receberam novos aptos
            </Rotulo>
          </div>

          <div style={{ opacity: fadeIn(f, 6) }}>
            <GridSecoes progress={g} />
          </div>
        </Wrap>
      </Fundo>
    </AbsoluteFill>
  );
};

/* ─────────────────────────── CENA 5 · CONTRASTE ─────────────────────────── */
export const Contraste: React.FC = () => {
  const f = useCurrentFrame();

  const h2018 = interpolate(f, [6, 30], [0, 0.012], clamp);
  const h2026 = interpolate(f, [62, 130], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });

  return (
    <AbsoluteFill>
      <Fundo>
        <Wrap>
          <div style={{ opacity: fadeIn(f, 0), marginBottom: 20 }}>
            <Rotulo color={C.muted} size={30}>
              mesmo cálculo · mesmo sistema
            </Rotulo>
          </div>

          <div style={{ opacity: fadeIn(f, 8), marginBottom: 60 }}>
            <Rotulo color={C.white} size={40}>
              novos aptos entre turnos
            </Rotulo>
          </div>

          <BarraContraste
            h2018={h2018}
            h2026={h2026}
            v2018={fmt(DADOS.controle2018)}
            v2026={fmt(DADOS.novosEleitores)}
          />
        </Wrap>
      </Fundo>
    </AbsoluteFill>
  );
};

/* ─────────────────────────── CENA 6 · DIVISÃO ─────────────────────────── */
export const Divisao: React.FC = () => {
  const f = useCurrentFrame();
  const p = interpolate(f, [12, 122], [0, 1], clamp);

  return (
    <AbsoluteFill>
      <Fundo>
        <Wrap>
          <div style={{ opacity: fadeIn(f, 0), marginBottom: 26 }}>
            <Rotulo color={C.muted} size={28}>
              divisão estimada dos que compareceram
            </Rotulo>
          </div>

          <FaixaSplit
            progress={p}
            labelA="LULA (13)"
            labelB="FLÁVIO (22)"
            pctA={DADOS.pctLula}
          />

          <div
            style={{
              marginTop: 62,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 14,
              opacity: fadeIn(f, 40),
            }}
          >
            <div style={{ width: 28, height: 2, background: C.amber }} />
            <Rotulo color={C.amber} size={23} maxWidth={700}>
              estimativa por boletim de urna — o log não registra candidato
            </Rotulo>
          </div>
        </Wrap>
      </Fundo>
    </AbsoluteFill>
  );
};

/* ─────────────────────────── CENA 7 · FECHO ─────────────────────────── */
export const Fecho: React.FC = () => {
  const f = useCurrentFrame();
  const out = interpolate(f, [70, 90], [1, 0], clamp);
  const linhas = [
    "FONTE: ARQUIVOS PÚBLICOS DO TSE",
    "CADERNO DE VOTAÇÃO · BOLETINS DE URNA",
    "DADOS ABERTOS · CÓDIGO AUDITÁVEL",
  ];

  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Fundo>
        <Wrap>
          <div style={{ display: "flex", flexDirection: "column", gap: 30, alignItems: "center" }}>
            <div
              style={{
                width: 90,
                height: 2,
                background: C.cyan,
                opacity: fadeIn(f, 0, 18),
                marginBottom: 10,
              }}
            />
            {linhas.map((l, i) => (
              <div key={l} style={{ opacity: fadeIn(f, 8 + i * 12) }}>
                <Rotulo color={i === 0 ? C.white : C.dim} size={26}>
                  {l}
                </Rotulo>
              </div>
            ))}
          </div>
        </Wrap>
      </Fundo>
    </AbsoluteFill>
  );
};
