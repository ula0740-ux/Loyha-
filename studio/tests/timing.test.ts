import { test } from 'node:test';
import assert from 'node:assert/strict';
import { estimateWords } from '../server/tts/audio.ts';
import { totalFrames } from '../src/types.ts';

test('estimated words cover the spoken span in order', () => {
  const w = estimateWords('Har bir gʻoya bitta nuqtadan boshlanadi.', 0.5, 3.5);
  assert.equal(w.length, 6);
  assert.equal(w[0].start, 0.5);
  assert.ok(Math.abs(w[w.length - 1].end - 3.5) < 1e-9);
  for (let i = 1; i < w.length; i++) assert.ok(Math.abs(w[i].start - w[i - 1].end) < 1e-9);
  // longer words get more time
  assert.ok(w[5].end - w[5].start > w[1].end - w[1].start);
});

test('Cyrillic words are weighted too', () => {
  const w = estimateWords('Код билан ҳаракат.', 0, 2);
  assert.ok(w[2].end - w[2].start > w[0].end - w[0].start);
});

test('video length is the sum of scene lengths', () => {
  const scene = (duration: number) => ({ text: 'x', audio: null, audioOffset: 0, duration, words: [] });
  assert.equal(totalFrames({ fps: 30, scenes: [scene(2), scene(1.5)] }), 105);
});
