import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import type { Provider, Voice, WordTiming } from './types.ts';
import { durationOf, toWav } from './audio.ts';

const run = promisify(execFile);
const HELPER = fileURLToPath(new URL('./edge_tts_helper.py', import.meta.url));

// Microsoft neural voices through the Edge read-aloud endpoint. Free, no key, but needs speech.platform.bing.com.
// The same voice names exist in Azure AI Speech (see azure.ts) for a paid, keyed route.
export const NEURAL_VOICES: Omit<Voice, 'key' | 'provider'>[] = [
  { voiceId: 'uz-UZ-MadinaNeural', lang: 'uz', gender: 'female', label: 'Madina (oʻzbekcha, ayol)', uzInput: 'latin' },
  { voiceId: 'uz-UZ-SardorNeural', lang: 'uz', gender: 'male', label: 'Sardor (oʻzbekcha, erkak)', uzInput: 'latin' },
  { voiceId: 'ru-RU-SvetlanaNeural', lang: 'ru', gender: 'female', label: 'Svetlana (ruscha, ayol)' },
  { voiceId: 'ru-RU-DmitryNeural', lang: 'ru', gender: 'male', label: 'Dmitry (ruscha, erkak)' },
  { voiceId: 'en-US-AriaNeural', lang: 'en', gender: 'female', label: 'Aria (inglizcha, ayol)' },
  { voiceId: 'en-US-GuyNeural', lang: 'en', gender: 'male', label: 'Guy (inglizcha, erkak)' },
];

export const edge: Provider = {
  id: 'edge',
  label: 'Microsoft Edge ovozlari (bepul, kalitsiz, onlayn)',
  kind: 'free-online',
  env: [],
  hosts: ['speech.platform.bing.com'],
  async available() {
    try {
      await run('python3', ['-c', 'import edge_tts']);
      return { ok: true };
    } catch {
      return { ok: false, reason: 'edge-tts Python paketi yoʻq (pip install edge-tts)' };
    }
  },
  async voices() {
    return NEURAL_VOICES.map((v) => ({ ...v, provider: 'edge', key: 'edge:' + v.voiceId }));
  },
  async synth(text, voice, outBase) {
    const txt = outBase + '.txt', mp3 = outBase + '.mp3', js = outBase + '.words.json', wav = outBase + '.wav';
    await writeFile(txt, text, 'utf8');
    try {
      await run('python3', [HELPER, voice.voiceId, txt, mp3, js], { timeout: 90_000 });
    } catch (e) {
      const tail = String((e as { stderr?: string }).stderr || (e as Error).message).trim().split('\n').pop();
      throw new Error(`speech.platform.bing.com ga ulanib boʻlmadi yoki rad etildi: ${tail}`);
    }
    await toWav(mp3, wav);
    const words: WordTiming[] = JSON.parse(await readFile(js, 'utf8'));
    return { wavPath: wav, duration: await durationOf(wav), words, timing: 'exact' };
  },
};
