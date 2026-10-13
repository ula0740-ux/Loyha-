import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import type { Provider, Voice } from './types.ts';
import { durationOf, estimateWords, speechBounds, toWav } from './audio.ts';
import { toScript } from '../../src/lib/uzbek.ts';

const run = promisify(execFile);

// eSpeak NG: offline, open source (GPL-3). Formant synthesis, so it sounds robotic, but it has an Uzbek voice.
// Its Uzbek rules read Latin script correctly and mis-read Cyrillic (я, ш), so Uzbek text is always sent as Latin.
const VOICES: Voice[] = [
  { key: 'espeak:uz+f3', provider: 'espeak', voiceId: 'uz+f3', lang: 'uz', gender: 'female', label: 'eSpeak oʻzbekcha (ayol)', uzInput: 'latin' },
  { key: 'espeak:uz', provider: 'espeak', voiceId: 'uz', lang: 'uz', gender: 'male', label: 'eSpeak oʻzbekcha (erkak)', uzInput: 'latin' },
  { key: 'espeak:ru+f3', provider: 'espeak', voiceId: 'ru+f3', lang: 'ru', gender: 'female', label: 'eSpeak ruscha (ayol)' },
  { key: 'espeak:ru', provider: 'espeak', voiceId: 'ru', lang: 'ru', gender: 'male', label: 'eSpeak ruscha (erkak)' },
  { key: 'espeak:en-us+f3', provider: 'espeak', voiceId: 'en-us+f3', lang: 'en', gender: 'female', label: 'eSpeak inglizcha (ayol)' },
  { key: 'espeak:en-us', provider: 'espeak', voiceId: 'en-us', lang: 'en', gender: 'male', label: 'eSpeak inglizcha (erkak)' },
];

export const espeak: Provider = {
  id: 'espeak',
  label: 'eSpeak NG (bepul, ochiq manba, oflayn)',
  kind: 'offline-open-source',
  env: [],
  hosts: [],
  async available() {
    try {
      await run('espeak-ng', ['--version']);
      return { ok: true };
    } catch {
      return { ok: false, reason: 'espeak-ng oʻrnatilmagan (sudo apt-get install espeak-ng)' };
    }
  },
  async voices() {
    return (await this.available()).ok ? VOICES : [];
  },
  async synth(text, voice, outBase) {
    const spoken = voice.lang === 'uz' ? toScript(text, 'latin') : text;
    const raw = outBase + '.espeak.wav', wav = outBase + '.wav';
    await run('espeak-ng', ['-v', voice.voiceId, '-s', '145', '-g', '4', '-w', raw, spoken]);
    await toWav(raw, wav);
    const b = await speechBounds(wav);
    return { wavPath: wav, duration: await durationOf(wav), words: estimateWords(text, b.start, b.end), timing: 'estimated' };
  },
};
