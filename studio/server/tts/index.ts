import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Provider, SynthResult, Voice, WordTiming } from './types.ts';
import { espeak } from './espeak.ts';
import { edge } from './edge.ts';
import { azure } from './azure.ts';
import { google } from './google.ts';
import { elevenlabs } from './elevenlabs.ts';
import { toScript } from '../../src/lib/uzbek.ts';
import { prepareUzbek } from '../uz/prepare.ts';
import type { UzScript } from '../uz/lexicon.ts';
import { estimateWords, speechBounds } from './audio.ts';

export const PROVIDERS: Provider[] = [espeak, edge, azure, google, elevenlabs];
export const STATUS_FILE = fileURLToPath(new URL('../../data/tts-status.json', import.meta.url));

export interface VoiceStatus {
  ok: boolean;
  testedAt: string;
  error?: string;
  sample?: string; // path under public/ to listen to the test clip
  seconds?: number;
}
export type StatusMap = Record<string, VoiceStatus>;

export async function readStatus(): Promise<StatusMap> {
  try {
    return JSON.parse(await readFile(STATUS_FILE, 'utf8'));
  } catch {
    return {};
  }
}

export async function writeStatus(s: StatusMap) {
  await mkdir(dirname(STATUS_FILE), { recursive: true });
  await writeFile(STATUS_FILE, JSON.stringify(s, null, 1));
}

export async function allVoices(): Promise<{ provider: Provider; ok: boolean; reason?: string; voices: Voice[] }[]> {
  return Promise.all(
    PROVIDERS.map(async (p) => {
      const a = await p.available();
      let voices: Voice[] = [];
      let reason = a.reason;
      if (a.ok) {
        try {
          voices = await p.voices();
        } catch (e) {
          reason = String((e as Error).message);
        }
      }
      return { provider: p, ok: a.ok && !reason, reason, voices };
    }),
  );
}

export async function findVoice(key: string): Promise<{ provider: Provider; voice: Voice }> {
  for (const g of await allVoices()) {
    const v = g.voices.find((x) => x.key === key);
    if (v) return { provider: g.provider, voice: v };
  }
  throw new Error(`Ovoz topilmadi yoki ulanmagan: ${key}`);
}

/**
 * Synthesize one scene. Uzbek text is sent in the script the voice reads correctly; the returned word
 * timings are mapped back onto the words as the user wrote them (transliteration keeps word count).
 */
const uzScript = () => (process.env.UZ_SCRIPT === 'cyrillic' ? 'cyrillic' : 'latin') as UzScript;

export async function speak(text: string, voiceKey: string, outBase: string): Promise<SynthResult> {
  const { provider, voice } = await findVoice(voiceKey);
  let spoken = text;
  // ElevenLabs + Uzbek: full preparation (one script, lexicon, numbers -> words; x/h never touched)
  const uzPrep = voice.lang === 'uz' && provider.id === 'elevenlabs';
  if (uzPrep) spoken = prepareUzbek(text, uzScript()).tts;
  else if (voice.lang === 'uz' && voice.uzInput && voice.uzInput !== 'any') spoken = toScript(text, voice.uzInput);
  const r = await provider.synth(spoken, voice, outBase);
  const shown = text.split(/\s+/).filter(Boolean);
  let words: WordTiming[];
  const groups = uzPrep ? shown.map((w) => prepareUzbek(w, uzScript()).tts.split(/\s+/).filter(Boolean).length) : [];
  if (r.words.length === shown.length) words = r.words.map((w, i) => ({ ...w, text: shown[i] }));
  else if (uzPrep && groups.reduce((a, b) => a + b, 0) === r.words.length) {
    // "2026-yil" was spoken as 4 words: its timing spans all of them
    let k = 0;
    words = shown.map((text, i) => { const g = r.words.slice(k, (k += groups[i])); return { text, start: g[0]?.start ?? 0, end: g[g.length - 1]?.end ?? 0 }; });
  }
  else {
    const b = await speechBounds(r.wavPath);
    words = estimateWords(text, b.start, b.end);
    return { ...r, words, timing: 'estimated' };
  }
  return { ...r, words };
}
