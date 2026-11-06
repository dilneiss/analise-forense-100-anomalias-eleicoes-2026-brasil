// Timeline Opuscar Visual Investigation (Pausas ultra-curtas de 200ms, voz 1.5x)
export type BeatOpuscar = {
  id: string;
  from: number;
  dur: number;
  audio: string;
  falado: number;
};

export const TIMELINE_OPUSCAR: BeatOpuscar[] = [
  { id: "beat_01_ia_open", from: 0, dur: 282, audio: "opuscar/beat_01_ia_open.wav", falado: 276 },
  { id: "beat_02_lei_150d", from: 282, dur: 252, audio: "opuscar/beat_02_lei_150d.wav", falado: 246 },
  { id: "beat_03_flagrante_116k", from: 534, dur: 261, audio: "opuscar/beat_03_flagrante_116k.wav", falado: 255 },
  { id: "beat_04_controle_2018", from: 795, dur: 359, audio: "opuscar/beat_04_controle_2018.wav", falado: 353 },
];

export const TOTAL_FRAMES_OPUSCAR = 1154;
