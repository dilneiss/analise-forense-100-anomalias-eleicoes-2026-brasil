// Timeline da História dos Novos Eleitores (Gerada a partir dos áudios reais)
export type Ato = {
  id: string;
  from: number;
  dur: number;
  audio: string;
  falado: number;
};

export const TIMELINE_HISTORIA: Ato[] = [
  { id: "ato_01", from: 0, dur: 525, audio: "historia/ato_01.wav", falado: 489 },
  { id: "ato_02", from: 525, dur: 518, audio: "historia/ato_02.wav", falado: 482 },
  { id: "ato_03", from: 1043, dur: 514, audio: "historia/ato_03.wav", falado: 478 },
  { id: "ato_04", from: 1557, dur: 476, audio: "historia/ato_04.wav", falado: 440 },
  { id: "ato_05", from: 2033, dur: 552, audio: "historia/ato_05.wav", falado: 516 },
];

export const TOTAL_FRAMES_HISTORIA = 2585;
