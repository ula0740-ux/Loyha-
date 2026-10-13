import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile } from 'node:fs/promises';
import type { WordTiming } from './types.ts';

const run = promisify(execFile);

/** Any audio file -> 48 kHz mono 16-bit WAV (what Remotion and the timing code expect). */
export async function toWav(input: string, output: string) {
  await run('ffmpeg', ['-v', 'error', '-y', '-i', input, '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s16le', output]);
}

export async function durationOf(file: string): Promise<number> {
  const { stdout } = await run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', file]);
  return Number(stdout.trim());
}

/** Start/end of speech in a 16-bit mono WAV (skips leading/trailing silence). */
export async function speechBounds(wav: string): Promise<{ start: number; end: number }> {
  const buf = await readFile(wav);
  const dataIdx = buf.indexOf('data');
  const pcm = new Int16Array(buf.buffer, buf.byteOffset + dataIdx + 8, Math.floor((buf.length - dataIdx - 8) / 2));
  const sr = buf.readUInt32LE(24);
  const win = Math.round(sr * 0.01);
  const rms: number[] = [];
  for (let i = 0; i + win <= pcm.length; i += win) {
    let s = 0;
    for (let j = i; j < i + win; j++) s += pcm[j] * pcm[j];
    rms.push(Math.sqrt(s / win));
  }
  const peak = Math.max(1, ...rms);
  const on = rms.map((r) => r > peak * 0.04);
  const first = on.indexOf(true), last = on.lastIndexOf(true);
  if (first < 0) return { start: 0, end: pcm.length / sr };
  return { start: first * 0.01, end: (last + 1) * 0.01 };
}

/** Rough syllable count, works for Latin and Cyrillic (vowel groups). */
function weight(word: string): number {
  const v = (word.toLowerCase().match(/[aeiouyаеёиоуўэюяыі]+/g) || []).length;
  return Math.max(1, v) + (/[.,!?;:…]$/.test(word) ? 0.6 : 0);
}

/** Spread words over the spoken part of the clip, proportional to syllables. Labelled "estimated" in the UI. */
export function estimateWords(text: string, start: number, end: number): WordTiming[] {
  const words = text.split(/\s+/).filter(Boolean);
  const total = words.reduce((a, w) => a + weight(w), 0);
  let t = start;
  return words.map((w) => {
    const d = ((end - start) * weight(w)) / total;
    const wt = { text: w, start: t, end: t + d };
    t += d;
    return wt;
  });
}
