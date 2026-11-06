import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Paleta oficial do estilo Visual Investigation do Opuscar
const OPUS = {
  ground: "#0B0C0E",
  panel: "#141619",
  frame: "#2E3238",
  text: "#ECEAE4",
  secondary: "#8B9097",
  muted: "#4A4F57",
  red: "#FF4A2E", // O acento único de flagrante / alerta do Opuscar
  cyan: "#22D3EE",
  green: "#10B981",
  mono: "JetBrains Mono, monospace",
  sans: "Inter, sans-serif",
};

// Componente de Chip de Fonte oficial do Opuscar (6x12 chip + texto mono)
const SourceTag: React.FC<{ tag: string; type?: string; color?: string }> = ({
  tag,
  type = "FONTE",
  color = OPUS.cyan,
}) => (
  <div style={{ display: "inline-flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
    <div style={{ width: 6, height: 12, background: color, borderRadius: 1 }} />
    <span
      style={{
        fontFamily: OPUS.mono,
        fontSize: 20,
        fontWeight: 700,
        letterSpacing: "0.14em",
        textTransform: "uppercase",
        color: OPUS.secondary,
      }}
    >
      {type} · {tag}
    </span>
  </div>
);

// Painel com moldura técnica de 1px
const EvidencePanel: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({
  children,
  style,
}) => (
  <div
    style={{
      background: OPUS.panel,
      border: `1px solid ${OPUS.frame}`,
      borderRadius: 4,
      padding: "24px 32px",
      boxSizing: "border-box",
      ...style,
    }}
  >
    {children}
  </div>
);

// Flash branco de 3 frames nos cortes (assinatura visual do Opuscar)
const CutFlash: React.FC = () => {
  const frame = useCurrentFrame();
  const flash = interpolate(frame, [0, 3], [0.35, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return <AbsoluteFill style={{ background: "#ffffff", opacity: flash, pointerEvents: "none" }} />;
};

/* ───────────────────────── BEAT 1: COLD OPEN COM IA ───────────────────────── */
export const Beat1IAOpen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scan = interpolate(frame, [8, 120], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pulse = Math.sin(frame / 8) * 0.02;

  return (
    <AbsoluteFill style={{ background: OPUS.ground, padding: "80px 70px" }}>
      <CutFlash />

      {/* Header técnico */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `1px solid ${OPUS.frame}`, paddingBottom: 16 }}>
        <SourceTag type="MOTOR" tag="AUDITORIA COM INTELIGÊNCIA ARTIFICIAL" color={OPUS.cyan} />
        <span style={{ fontFamily: OPUS.mono, color: OPUS.red, fontSize: 20, fontWeight: 700 }}>
          [MODO INVESTIGAÇÃO]
        </span>
      </div>

      {/* Título principal do Cold Open */}
      <div style={{ marginTop: 60 }}>
        <div style={{ fontFamily: OPUS.mono, color: OPUS.secondary, fontSize: 24, letterSpacing: "0.16em", textTransform: "uppercase" }}>
          varredura nacional automatizada
        </div>
        <div style={{ fontFamily: OPUS.sans, fontWeight: 900, fontSize: 68, color: OPUS.text, letterSpacing: "-0.03em", marginTop: 8, lineHeight: 1.1 }}>
          499.178 SEÇÕES AUDITADAS
        </div>
      </div>

      {/* Painel Central com Mira / Retículo de Radar */}
      <EvidencePanel style={{ marginTop: 60, position: "relative", overflow: "hidden" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 20 }}>
          <span style={{ fontFamily: OPUS.mono, color: OPUS.cyan, fontSize: 22, fontWeight: 700 }}>
            OBJETO: CADERNO DE VOTAÇÃO 1T vs 2T
          </span>
          <span style={{ fontFamily: OPUS.mono, color: OPUS.text, fontSize: 22, fontWeight: 700 }}>
            PROGRESSO: {Math.min(100, Math.round(scan))}%
          </span>
        </div>

        {/* Linha de varredura laser */}
        <div style={{ width: "100%", height: 6, background: "rgba(255,255,255,0.08)", borderRadius: 3, overflow: "hidden", position: "relative" }}>
          <div style={{ width: `${scan}%`, height: "100%", background: OPUS.cyan, borderRadius: 3, boxShadow: `0 0 15px ${OPUS.cyan}` }} />
        </div>

        <div style={{ marginTop: 36, padding: "20px 24px", background: "rgba(255,74,46,0.08)", border: `1px solid ${OPUS.red}`, borderRadius: 3 }}>
          <div style={{ fontFamily: OPUS.mono, fontSize: 22, color: OPUS.red, fontWeight: 700, letterSpacing: "0.08em" }}>
            ALERTA CRÍTICO DETECTADO:
          </div>
          <div style={{ fontFamily: OPUS.sans, fontSize: 32, fontWeight: 800, color: OPUS.text, marginTop: 6 }}>
            Discrepância no cadastro congelado de eleitores aptos
          </div>
        </div>
      </EvidencePanel>
    </AbsoluteFill>
  );
};

/* ───────────────────────── BEAT 2: A REGRA DOS 150 DIAS ───────────────────────── */
export const Beat2Lei150d: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const count = Math.min(
    150,
    Math.round(interpolate(frame, [10, 80], [0, 150], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }))
  );

  return (
    <AbsoluteFill style={{ background: OPUS.ground, padding: "80px 70px" }}>
      <CutFlash />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `1px solid ${OPUS.frame}`, paddingBottom: 16 }}>
        <SourceTag type="LEGISLAÇÃO" tag="LEI Nº 9.504/1997 · ART. 91" color={OPUS.red} />
        <span style={{ fontFamily: OPUS.mono, color: OPUS.secondary, fontSize: 20 }}>
          NORMA VINCULANTE
        </span>
      </div>

      <div style={{ marginTop: 60 }}>
        <div style={{ fontFamily: OPUS.mono, color: OPUS.secondary, fontSize: 24, letterSpacing: "0.16em" }}>
          REGRA LEGAL INEGOCIÁVEL
        </div>
        <div style={{ fontFamily: OPUS.sans, fontWeight: 900, fontSize: 64, color: OPUS.text, letterSpacing: "-0.03em", marginTop: 8, lineHeight: 1.1 }}>
          CADASTRO CONGELADO
        </div>
      </div>

      <EvidencePanel style={{ marginTop: 50 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 20 }}>
          <div style={{ fontFamily: OPUS.mono, fontWeight: 900, fontSize: 140, color: OPUS.red, lineHeight: 1, letterSpacing: "-0.04em" }}>
            {count}
          </div>
          <div style={{ fontFamily: OPUS.mono, fontWeight: 800, fontSize: 40, color: OPUS.text, letterSpacing: "0.1em" }}>
            DIAS ANTES DO PLEITO
          </div>
        </div>

        <div style={{ marginTop: 30, borderTop: `1px solid ${OPUS.frame}`, paddingTop: 20, fontFamily: OPUS.mono, fontSize: 22, color: OPUS.secondary, lineHeight: 1.5 }}>
          "Nenhuma alteração na situação do eleitor nem transferência de domicílio poderá ser efetuada nos 150 dias anteriores à eleição."
        </div>

        <div style={{ marginTop: 24, background: "rgba(255,255,255,0.03)", padding: "12px 16px", borderLeft: `3px solid ${OPUS.red}`, fontFamily: OPUS.mono, fontSize: 20, color: OPUS.text }}>
          PROIBIÇÃO EXPRESSA: ZERO novos eleitores podem entrar no 2º turno.
        </div>
      </EvidencePanel>
    </AbsoluteFill>
  );
};

/* ───────────────────────── BEAT 3: O FLAGRANTE DE 116.480 ───────────────────────── */
export const Beat3Flagrante116k: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const valor = Math.round(
    interpolate(
      spring({ frame: frame - 10, fps, config: { damping: 24, stiffness: 60 } }),
      [0, 1],
      [0, 116480]
    )
  );

  return (
    <AbsoluteFill style={{ background: OPUS.ground, padding: "80px 70px" }}>
      <CutFlash />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `1px solid ${OPUS.frame}`, paddingBottom: 16 }}>
        <SourceTag type="FLAGRANTE" tag="REGRA CHK018 · DISCREPÂNCIA CADASTRAL" color={OPUS.red} />
        <span style={{ fontFamily: OPUS.mono, color: OPUS.red, fontSize: 20, fontWeight: 700 }}>
          EVIDÊNCIA MATERIAL
        </span>
      </div>

      <div style={{ marginTop: 50 }}>
        <div style={{ fontFamily: OPUS.mono, color: OPUS.secondary, fontSize: 24, letterSpacing: "0.14em" }}>
          NOVOS NOMES INSERIDOS NO CADERNO
        </div>
        <div style={{ fontFamily: OPUS.mono, fontWeight: 900, fontSize: 130, color: OPUS.red, letterSpacing: "-0.04em", lineHeight: 1, marginTop: 12, textShadow: `0 0 50px rgba(255,74,46,0.3)` }}>
          {valor.toLocaleString("pt-BR")}
        </div>
      </div>

      {/* Painel com as 92.000 seções */}
      <EvidencePanel style={{ marginTop: 40 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <span style={{ fontFamily: OPUS.mono, fontSize: 24, fontWeight: 800, color: OPUS.text }}>
            AMPLITUDE NACIONAL DO FLAGRANTE
          </span>
          <span style={{ fontFamily: OPUS.mono, fontSize: 22, color: OPUS.cyan, fontWeight: 700 }}>
            92.000 SEÇÕES ELEITORAIS
          </span>
        </div>

        {/* Dot matrix simplificado estilo Opuscar */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(30, 1fr)", gap: 6, margin: "20px 0" }}>
          {Array.from({ length: 180 }).map((_, i) => (
            <div
              key={i}
              style={{
                height: 8,
                borderRadius: 1,
                background: (i * 7) % 10 < 6 ? OPUS.red : "rgba(255,255,255,0.06)",
                opacity: (i * 7) % 10 < 6 ? 0.9 : 0.3,
              }}
            />
          ))}
        </div>

        <div style={{ fontFamily: OPUS.mono, fontSize: 20, color: OPUS.secondary }}>
          Não foi um caso isolado: a inserção ocorreu de forma capilarizada em 92 mil urnas.
        </div>
      </EvidencePanel>
    </AbsoluteFill>
  );
};

/* ───────────────────────── BEAT 4: O CONTROLE DE 2018 E A CONTA QUE NÃO FECHA ───────────────────────── */
export const Beat4Controle2018: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const barH2026 = interpolate(
    spring({ frame: frame - 20, fps, config: { damping: 20, stiffness: 80 } }),
    [0, 1],
    [0, 1]
  );

  return (
    <AbsoluteFill style={{ background: OPUS.ground, padding: "80px 70px" }}>
      <CutFlash />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `1px solid ${OPUS.frame}`, paddingBottom: 16 }}>
        <SourceTag type="PROVA" tag="GRUPO DE CONTROLE CIENTÍFICO (2018)" color={OPUS.green} />
        <span style={{ fontFamily: OPUS.mono, color: OPUS.text, fontSize: 20, fontWeight: 700 }}>
          CONFRONTO HISTÓRICO
        </span>
      </div>

      <div style={{ marginTop: 40 }}>
        <div style={{ fontFamily: OPUS.mono, color: OPUS.secondary, fontSize: 22, letterSpacing: "0.14em" }}>
          MESMO ALGORITMO DE IA · MESMO CÓDIGO
        </div>
        <div style={{ fontFamily: OPUS.sans, fontWeight: 900, fontSize: 52, color: OPUS.text, letterSpacing: "-0.03em", marginTop: 6 }}>
          2018 (CONTROLE) vs 2026
        </div>
      </div>

      {/* Grid Comparativo de Duas Colunas */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 30 }}>
        {/* Coluna 2018 */}
        <EvidencePanel style={{ borderLeft: `3px solid ${OPUS.green}`, textAlign: "center" }}>
          <div style={{ fontFamily: OPUS.mono, fontSize: 20, color: OPUS.green, fontWeight: 700 }}>
            ELEIÇÕES 2018
          </div>
          <div style={{ fontFamily: OPUS.mono, fontSize: 90, fontWeight: 900, color: OPUS.green, margin: "16px 0" }}>
            0
          </div>
          <div style={{ fontFamily: OPUS.mono, fontSize: 18, color: OPUS.secondary }}>
            Zero novos aptos no 2º turno. Sistema operou 100% limpo.
          </div>
        </EvidencePanel>

        {/* Coluna 2026 */}
        <EvidencePanel style={{ borderLeft: `3px solid ${OPUS.red}`, textAlign: "center" }}>
          <div style={{ fontFamily: OPUS.mono, fontSize: 20, color: OPUS.red, fontWeight: 700 }}>
            ELEIÇÕES 2026
          </div>
          <div style={{ fontFamily: OPUS.mono, fontSize: 64, fontWeight: 900, color: OPUS.red, margin: "26px 0", lineHeight: 1 }}>
            116.480
          </div>
          <div style={{ fontFamily: OPUS.mono, fontSize: 18, color: OPUS.secondary }}>
            80% canalizados para o mesmo lado (estimativa por BU).
          </div>
        </EvidencePanel>
      </div>

      {/* Veredito Pericial Final */}
      <div style={{ marginTop: 32, padding: "18px 24px", background: "rgba(255,255,255,0.03)", border: `1px solid ${OPUS.frame}`, borderRadius: 4, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontFamily: OPUS.mono, fontSize: 20, color: OPUS.text, fontWeight: 700 }}>
            ARTIGO 219 DO CÓDIGO ELEITORAL (PRINCÍPIO DO PREJUÍZO)
          </div>
          <div style={{ fontFamily: OPUS.mono, fontSize: 16, color: OPUS.secondary, marginTop: 2 }}>
            A conta não fecha: inserção atípica com repercussão no resultado final
          </div>
        </div>
        <div style={{ background: OPUS.red, color: "#fff", padding: "6px 14px", fontFamily: OPUS.mono, fontSize: 18, fontWeight: 900, borderRadius: 2 }}>
          NULO
        </div>
      </div>
    </AbsoluteFill>
  );
};
