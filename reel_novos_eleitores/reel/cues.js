// reel/cues.js: THE timeline. The page (reel.js) and the score (music/score.mjs) both read it, so every hit in the
// music lands on its frame. 120 BPM: a beat is 0.5 s, a bar 2 s. Cuts on beats, chapter changes on bars.
// Durações dos capítulos derivadas da narração real (1,2x): 6,98 / 6,12 / 6,10 / 8,88 s + respiro.
var KCUE = (() => {
  const B = n => +(n * 0.5).toFixed(4);                    // B(n) = time of beat n
  const S = { open: 0, lei: 7.5, flagrante: 15, controle: 22.5 };
  return {
    bpm: 120, fps: 30, dur: 32, B, S,
    CH: [['OPEN', 0, 7.5], ['01 LEI', 7.5, 15], ['02 FLAGRANTE', 15, 22.5], ['03 CONTROLE', 22.5, 32]],
    hits: {
      // open
      dot: 0.5, mark: 1.0, num: 1.4, dash: 2.6, claim: 3.6, chips: 4.6,
      // lei
      leiTitle: 7.7, lei150: 9.2, leiAxis: 10.9, leiQuote: 12.6,
      // flagrante
      flNum: 15.2, flGrid: 17.2, flLabel: 19.2,
      // controle
      ctBars: 22.75, ctVal: 24.6, ctPct: 25.9, ctSeal: 27.4, end: 30.8,
    },
  };
})();
if (typeof module !== 'undefined') module.exports = KCUE;
