/**
 * Estado do Theatre.js — toda a animação do filme vive em keyframes.
 * O componente apenas faz `sheet.sequence.position = frame / 30` e lê as props.
 *
 * Formato do estado: schema do @theatre/core 0.4.0 (sequence + BasicKeyframedTrack).
 */

export type KF = { position: number; value: number; ease?: "expo" | "in" | "linear" };

const HANDLES: Record<string, number[]> = {
  expo: [0.16, 1, 0.3, 1],      // easeOutExpo: entra rápido, pousa devagar
  in: [0.7, 0, 0.84, 0],        // easeIn: acelera na saída
  linear: [0.33, 0, 0.67, 1],
};

const track = (frames: KF[]) => ({
  type: "BasicKeyframedTrack" as const,
  keyframes: frames.map((k, i) => ({
    id: `k${i}_${k.position}`,
    position: k.position,
    connectedRight: true,
    handles: HANDLES[k.ease ?? "expo"],
    value: k.value,
    type: "bezier" as const,
  })),
});

type Obj = { props: Record<string, number>; tracks: Record<string, KF[]> };

const OBJS: Record<string, Obj> = {
  // global: push de câmera e scroll dos ticks (nunca deixa o quadro parado)
  g: {
    props: { push: 1, tick: 0, sweep: -700 },
    tracks: {
      push: [{ position: 0, value: 1 }, { position: 22.5, value: 1.045, ease: "linear" }],
      tick: [{ position: 0, value: 0 }, { position: 22.5, value: 900, ease: "linear" }],
      sweep: [{ position: 0, value: -700 }, { position: 22.5, value: 2620, ease: "linear" }],
    },
  },
  hero: {
    props: { cardX: -640, numS: 0.9 },
    tracks: {
      cardX: [{ position: 0.35, value: -640 }, { position: 1.5, value: 0 }],
      numS: [{ position: 0, value: 0.9 }, { position: 1.4, value: 1 }],
    },
  },
  rule: {
    props: { barH: 0, lockY: 0 },
    tracks: {
      barH: [{ position: 5.6, value: 0 }, { position: 8.3, value: 1 }],
      lockY: [{ position: 6.2, value: 0 }, { position: 8.0, value: 1 }],
    },
  },
  wall: {
    props: { reveal: 0 },
    tracks: {
      reveal: [{ position: 9.1, value: 0 }, { position: 12.8, value: 1, ease: "linear" }],
    },
  },
  secoes: {
    props: { gridH: 1, zeroO: 0 },
    tracks: {
      gridH: [{ position: 14.1, value: 1 }, { position: 16.2, value: 0.055 }],
      zeroO: [{ position: 15.4, value: 0 }, { position: 16.6, value: 1 }],
    },
  },
  verdict: {
    props: { fill: 0 },
    tracks: {
      fill: [{ position: 18.0, value: 0 }, { position: 20.4, value: 1 }],
    },
  },
};

export const FILM_SECONDS = 22.5;

export const THEATRE_STATE = {
  sheetsById: {
    Film: {
      staticOverrides: {
        byObject: Object.fromEntries(
          Object.entries(OBJS).map(([name, o]) => [name, o.props]),
        ),
      },
      sequence: {
        type: "PositionalSequence" as const,
        length: FILM_SECONDS,
        subUnitsPerUnit: 30,
        tracksByObject: Object.fromEntries(
          Object.entries(OBJS).map(([name, o]) => [
            name,
            {
              trackIdByPropPath: Object.fromEntries(
                Object.keys(o.props).map((p) => [`["${p}"]`, `t_${name}_${p}`]),
              ),
              trackData: Object.fromEntries(
                Object.entries(o.tracks).map(([p, frames]) => [`t_${name}_${p}`, track(frames)]),
              ),
            },
          ]),
        ),
      },
    },
  },
  definitionVersion: "0.4.0" as const,
  revisionHistory: [] as string[],
};
