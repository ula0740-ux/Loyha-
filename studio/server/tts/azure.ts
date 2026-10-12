import { writeFile } from 'node:fs/promises';
import type { Provider } from './types.ts';
import { durationOf, estimateWords, speechBounds, toWav } from './audio.ts';
import { fetchOk } from '../net.ts';
import { NEURAL_VOICES } from './edge.ts';

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Azure AI Speech (paid, key). Same neural voice names as the Edge route, including uz-UZ Madina/Sardor.
export const azure: Provider = {
  id: 'azure',
  label: 'Azure AI Speech (pullik API kalit)',
  kind: 'paid-api',
  env: ['AZURE_SPEECH_KEY', 'AZURE_SPEECH_REGION'],
  hosts: ['<region>.tts.speech.microsoft.com'],
  async available() {
    const miss = this.env.filter((k) => !process.env[k]);
    return miss.length ? { ok: false, reason: `.env da yoʻq: ${miss.join(', ')}` } : { ok: true };
  },
  async voices() {
    if (!(await this.available()).ok) return [];
    return NEURAL_VOICES.map((v) => ({ ...v, provider: 'azure', key: 'azure:' + v.voiceId }));
  },
  async synth(text, voice, outBase) {
    const region = process.env.AZURE_SPEECH_REGION!;
    const locale = voice.voiceId.slice(0, 5);
    const ssml = `<speak version="1.0" xml:lang="${locale}"><voice name="${voice.voiceId}">${esc(text)}</voice></speak>`;
    const res = await fetchOk(`https://${region}.tts.speech.microsoft.com/cognitiveservices/v1`, {
      method: 'POST',
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.AZURE_SPEECH_KEY!,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'riff-48khz-16bit-mono-pcm',
        'User-Agent': 'uz-motion-studio',
      },
      body: ssml,
    });
    const raw = outBase + '.azure.wav', wav = outBase + '.wav';
    await writeFile(raw, Buffer.from(await res.arrayBuffer()));
    await toWav(raw, wav);
    const b = await speechBounds(wav);
    return { wavPath: wav, duration: await durationOf(wav), words: estimateWords(text, b.start, b.end), timing: 'estimated' };
  },
};
