// GERADO AUTOMATICAMENTE por tools/build_timeline.py — não editar à mão.
// duração de cada cena = duração real da narração + cauda de respiro
export type Cena = {
  id: string;
  from: number;
  dur: number;
  audio: string;
  falado: number;
};

export const TIMELINE: Cena[] = [
  { id: "scene_01", from: 0, dur: 326, audio: "audio/scene_01.wav", falado: 284 },
  { id: "scene_02", from: 326, dur: 458, audio: "audio/scene_02.wav", falado: 416 },
  { id: "scene_03", from: 784, dur: 363, audio: "audio/scene_03.wav", falado: 321 },
  { id: "scene_04", from: 1147, dur: 353, audio: "audio/scene_04.wav", falado: 311 },
  { id: "scene_05", from: 1500, dur: 475, audio: "audio/scene_05.wav", falado: 433 },
  { id: "scene_06", from: 1975, dur: 478, audio: "audio/scene_06.wav", falado: 436 },
];

export const TOTAL_FRAMES = 2453;
