import type { VideoProps } from './types';

// Silent preview for `npm run studio` (no narration; real renders get audio and word timings from the server).
const scene = (text: string, duration: number) => {
  const words = text.split(/\s+/);
  const step = (duration - 0.8) / words.length;
  return { text, audio: null, audioOffset: 0, duration, words: words.map((w, i) => ({ text: w, start: 0.3 + i * step, end: 0.3 + (i + 1) * step })) };
};

export const demoProps: VideoProps = {
  format: '9:16',
  fps: 30,
  title: 'Loyha',
  theme: { bg: '#0b0b0c', fg: '#f5f5f2', accent: '#cdf24f', muted: '#3a3a3f' },
  scenes: [
    scene('Har bir gʻoya bitta nuqtadan boshlanadi.', 3.2),
    scene('Kod bilan harakat.', 2.4),
    scene('Gʻoyadan videogacha.', 2.6),
  ],
};
