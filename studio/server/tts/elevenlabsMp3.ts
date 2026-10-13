// ElevenLabs text-to-speech -> MP3 file.
// The API key is read only from the environment (ELEVENLABS_API_KEY, loaded from .env by server/net.ts);
// it is never written to disk, logged or included in error messages.
import { writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { normalizeLatin, detectScript } from '../../src/lib/uzbek.ts';

export const ELEVENLABS_API = 'https://api.elevenlabs.io';
export const DEFAULT_VOICE = 'JBFqnCBsd6RMkjVDRZzb';

export interface Mp3Options {
  /** ElevenLabs voice id. Defaults to ELEVENLABS_VOICE_FEMALE, then ELEVENLABS_VOICE_MALE. */
  voiceId?: string;
  /** Model id. Defaults to ELEVENLABS_MODEL or eleven_multilingual_v2. */
  modelId?: string;
  /** ISO 639-1 hint sent to models that accept it (e.g. "uz"). Defaults to ELEVENLABS_LANGUAGE_CODE if set. */
  languageCode?: string;
  /** MP3 quality, e.g. mp3_44100_128 (default). */
  outputFormat?: string;
  stability?: number;
  similarityBoost?: number;
  /** Injected for tests; defaults to global fetch. */
  fetchImpl?: typeof fetch;
}

export class ElevenLabsError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ElevenLabsError';
  }
}

export function getApiKey(): string {
  const key = process.env.ELEVENLABS_API_KEY?.trim();
  if (!key) throw new ElevenLabsError('ELEVENLABS_API_KEY topilmadi. Uni .env fayliga yoki muhit oʻzgaruvchisiga qoʻshing.');
  return key;
}

/** Turn an API failure into a short Uzbek message without leaking the key or the request. */
function explain(status: number, body: string): string {
  if (status === 401) return 'API kalit notoʻgʻri yoki bekor qilingan (401).';
  if (status === 402 || /quota|credits/i.test(body)) return 'ElevenLabs hisobida kredit/limit tugagan.';
  if (status === 404) return 'Ovoz (voice_id) topilmadi (404).';
  if (status === 422) return `Soʻrov notoʻgʻri (422): ${body.slice(0, 200)}`;
  if (status === 429) return 'Juda koʻp soʻrov (429). Birozdan keyin qayta urining.';
  return `ElevenLabs xatosi ${status}: ${body.slice(0, 200)}`;
}

/** Uzbek text is sent in Latin with proper oʻ/gʻ apostrophes (Cyrillic input is kept as typed). */
export function prepareText(text: string): string {
  const t = text.trim();
  return detectScript(t) === 'latin' ? normalizeLatin(t) : t;
}

/**
 * Synthesize `text` with ElevenLabs and save it as an MP3 file.
 * Returns the number of bytes written.
 */
export async function textToSpeechMp3(text: string, outFile: string, opts: Mp3Options = {}): Promise<number> {
  const key = getApiKey();
  // falls back to ElevenLabs' default premade voice (the one in their quickstart) when none is configured
  const voiceId = opts.voiceId || process.env.ELEVENLABS_VOICE_FEMALE || process.env.ELEVENLABS_VOICE_MALE || DEFAULT_VOICE;
  if (!text.trim()) throw new ElevenLabsError('Matn boʻsh.');

  const body: Record<string, unknown> = {
    text: prepareText(text),
    model_id: opts.modelId || process.env.ELEVENLABS_MODEL || 'eleven_multilingual_v2',
    voice_settings: { stability: opts.stability ?? 0.5, similarity_boost: opts.similarityBoost ?? 0.75 },
  };
  const lang = opts.languageCode ?? process.env.ELEVENLABS_LANGUAGE_CODE;
  if (lang) body.language_code = lang;

  const url = `${ELEVENLABS_API}/v1/text-to-speech/${encodeURIComponent(voiceId)}?output_format=${opts.outputFormat || 'mp3_44100_128'}`;
  let res: Response;
  try {
    res = await (opts.fetchImpl ?? fetch)(url, {
      method: 'POST',
      headers: { 'xi-api-key': key, 'Content-Type': 'application/json', Accept: 'audio/mpeg' },
      body: JSON.stringify(body),
    });
  } catch (e) {
    throw new ElevenLabsError(`api.elevenlabs.io ga ulanib boʻlmadi (internet yoki tarmoq ruxsati): ${(e as Error).message}`);
  }
  if (!res.ok) throw new ElevenLabsError(explain(res.status, await res.text()), res.status);

  const audio = Buffer.from(await res.arrayBuffer());
  const isMp3 = audio.subarray(0, 3).toString('latin1') === 'ID3' || (audio[0] === 0xff && (audio[1] & 0xe0) === 0xe0);
  if (!isMp3) throw new ElevenLabsError('Javob MP3 emas.');
  await mkdir(dirname(outFile), { recursive: true });
  await writeFile(outFile, audio);
  return audio.length;
}

/** Cheap authenticated call to check the key and network without spending characters. */
export async function checkConnection(fetchImpl: typeof fetch = fetch): Promise<{ voices: { voice_id: string; name: string; labels?: Record<string, string> }[]; restricted?: boolean }> {
  const key = getApiKey();
  let res: Response;
  try {
    res = await fetchImpl(`${ELEVENLABS_API}/v1/voices`, { headers: { 'xi-api-key': key } });
  } catch (e) {
    throw new ElevenLabsError(`api.elevenlabs.io ga ulanib boʻlmadi (internet yoki tarmoq ruxsati): ${(e as Error).message}`);
  }
  if (!res.ok) {
    const body = await res.text();
    // A restricted key (e.g. Text to Speech only) is still a valid, authenticated key.
    if (res.status === 401 && body.includes('missing_permissions')) return { voices: [], restricted: true };
    throw new ElevenLabsError(explain(res.status, body), res.status);
  }
  return (await res.json()) as { voices: { voice_id: string; name: string }[] };
}
