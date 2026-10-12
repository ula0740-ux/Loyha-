import { writeFile } from 'node:fs/promises';
import type { Lang, Provider, Voice, WordTiming } from './types.ts';
import { durationOf, toWav } from './audio.ts';
import { fetchOk } from '../net.ts';

// ElevenLabs (paid, API key). Multilingual model with character timestamps -> exact word timings.
// The user picks the female/male voice ids in .env. Uzbek quality must be checked with `npm run verify-tts`.
export const elevenlabs: Provider = {
  id: 'elevenlabs',
  label: 'ElevenLabs (pullik API kalit)',
  kind: 'paid-api',
  env: ['ELEVENLABS_API_KEY', 'ELEVENLABS_VOICE_FEMALE', 'ELEVENLABS_VOICE_MALE'],
  hosts: ['api.elevenlabs.io'],
  async available() {
    const miss = this.env.filter((k) => !process.env[k]);
    return miss.length ? { ok: false, reason: `.env da yoʻq: ${miss.join(', ')}` } : { ok: true };
  },
  async voices() {
    if (!(await this.available()).ok) return [];
    const out: Voice[] = [];
    for (const lang of ['uz', 'ru', 'en'] as Lang[])
      for (const gender of ['female', 'male'] as const) {
        const id = gender === 'female' ? process.env.ELEVENLABS_VOICE_FEMALE! : process.env.ELEVENLABS_VOICE_MALE!;
        out.push({ key: `elevenlabs:${id}:${lang}`, provider: 'elevenlabs', voiceId: id, lang, gender, label: `ElevenLabs ${lang} (${gender === 'female' ? 'ayol' : 'erkak'})` });
      }
    return out;
  },
  async synth(text, voice, outBase) {
    const model = process.env.ELEVENLABS_MODEL || 'eleven_multilingual_v2';
    const res = await fetchOk(`https://api.elevenlabs.io/v1/text-to-speech/${voice.voiceId}/with-timestamps?output_format=mp3_44100_128`, {
      method: 'POST',
      headers: { 'xi-api-key': process.env.ELEVENLABS_API_KEY!, 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, model_id: model }),
    });
    const j = (await res.json()) as {
      audio_base64: string;
      alignment?: { characters: string[]; character_start_times_seconds: number[]; character_end_times_seconds: number[] };
    };
    const mp3 = outBase + '.mp3', wav = outBase + '.wav';
    await writeFile(mp3, Buffer.from(j.audio_base64, 'base64'));
    await toWav(mp3, wav);
    const words: WordTiming[] = [];
    const a = j.alignment;
    if (a) {
      let cur: WordTiming | null = null;
      a.characters.forEach((c, i) => {
        if (/\s/.test(c)) { if (cur) words.push(cur); cur = null; return; }
        if (!cur) cur = { text: '', start: a.character_start_times_seconds[i], end: 0 };
        cur.text += c;
        cur.end = a.character_end_times_seconds[i];
      });
      if (cur) words.push(cur);
    }
    return { wavPath: wav, duration: await durationOf(wav), words, timing: 'exact' };
  },
};
