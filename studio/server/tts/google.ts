import { writeFile } from 'node:fs/promises';
import type { Lang, Provider, Voice } from './types.ts';
import { durationOf, estimateWords, speechBounds, toWav } from './audio.ts';
import { fetchOk } from '../net.ts';

const LOCALES: Record<Lang, string> = { uz: 'uz-UZ', ru: 'ru-RU', en: 'en-US' };

// Google Cloud Text-to-Speech (paid, API key). Voices are read from the live voices.list call,
// so a language only appears if Google actually serves it for this key (Uzbek is not assumed).
export const google: Provider = {
  id: 'google',
  label: 'Google Cloud TTS (pullik API kalit)',
  kind: 'paid-api',
  env: ['GOOGLE_TTS_API_KEY'],
  hosts: ['texttospeech.googleapis.com'],
  async available() {
    return process.env.GOOGLE_TTS_API_KEY ? { ok: true } : { ok: false, reason: '.env da yoʻq: GOOGLE_TTS_API_KEY' };
  },
  async voices() {
    if (!(await this.available()).ok) return [];
    const out: Voice[] = [];
    for (const [lang, loc] of Object.entries(LOCALES) as [Lang, string][]) {
      const res = await fetchOk(`https://texttospeech.googleapis.com/v1/voices?languageCode=${loc}&key=${process.env.GOOGLE_TTS_API_KEY}`);
      const { voices = [] } = (await res.json()) as { voices?: { name: string; ssmlGender: string; languageCodes: string[] }[] };
      for (const g of ['FEMALE', 'MALE'] as const) {
        const v = voices.find((x) => x.ssmlGender === g && x.languageCodes.includes(loc));
        if (v) out.push({ key: 'google:' + v.name, provider: 'google', voiceId: v.name, lang, gender: g === 'FEMALE' ? 'female' : 'male', label: `Google ${v.name}` });
      }
    }
    return out;
  },
  async synth(text, voice, outBase) {
    const res = await fetchOk(`https://texttospeech.googleapis.com/v1/text:synthesize?key=${process.env.GOOGLE_TTS_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: { text },
        voice: { languageCode: voice.voiceId.slice(0, 5), name: voice.voiceId },
        audioConfig: { audioEncoding: 'LINEAR16', sampleRateHertz: 48000 },
      }),
    });
    const { audioContent } = (await res.json()) as { audioContent: string };
    const raw = outBase + '.google.wav', wav = outBase + '.wav';
    await writeFile(raw, Buffer.from(audioContent, 'base64'));
    await toWav(raw, wav);
    const b = await speechBounds(wav);
    return { wavPath: wav, duration: await durationOf(wav), words: estimateWords(text, b.start, b.end), timing: 'estimated' };
  },
};
