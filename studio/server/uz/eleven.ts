// ElevenLabs for Uzbek: model capabilities, synthesis with timestamps, Speech-to-Text check,
// Latin vs Cyrillic A/B testing and re-generation of mis-read words.
import { cyrToLat, normalizeLatin } from '../../src/lib/uzbek.ts';
import { prepareUzbek, type Prepared } from './prepare.ts';
import { expandNumbers } from './numbers.ts';
import { lexKey, loadLexicon, saveLexicon, upsert, type Lexicon, type UzScript } from './lexicon.ts';

export const API = 'https://api.elevenlabs.io';
export const DEFAULT_MODEL = process.env.ELEVENLABS_MODEL || 'eleven_v3';
export const DEFAULT_VOICE = process.env.ELEVENLABS_VOICE_FEMALE || 'EXAVITQu4vr4xnSDxMaL';
export const STT_MODEL = 'scribe_v1';

/**
 * Only parameters the model accepted in a live test are sent (2026-10-13, this account):
 * language_code "uz" -> accepted by eleven_v4; rejected (400 unsupported_language) by eleven_v3,
 * eleven_multilingual_v2, eleven_flash_v2_5, eleven_turbo_v2_5. Unknown models get no language_code.
 */
export const MODEL_CAPS: Record<string, { uzLanguageCode: boolean }> = {
  eleven_v4: { uzLanguageCode: true },
  eleven_v3: { uzLanguageCode: false },
  eleven_multilingual_v2: { uzLanguageCode: false },
  eleven_flash_v2_5: { uzLanguageCode: false },
  eleven_turbo_v2_5: { uzLanguageCode: false },
};

const key = () => {
  const k = process.env.ELEVENLABS_API_KEY?.trim();
  if (!k) throw new Error('ELEVENLABS_API_KEY topilmadi (.env yoki muhit oʻzgaruvchisi).');
  return k;
};

export interface Synth { mp3: Buffer; words: { text: string; start: number; end: number }[] }

export async function synth(text: string, opts: { voice?: string; model?: string; seed?: number } = {}): Promise<Synth> {
  const model = opts.model || DEFAULT_MODEL;
  const body: Record<string, unknown> = { text, model_id: model };
  if (MODEL_CAPS[model]?.uzLanguageCode) body.language_code = 'uz';
  if (opts.seed !== undefined) body.seed = opts.seed;
  const res = await fetch(`${API}/v1/text-to-speech/${opts.voice || DEFAULT_VOICE}/with-timestamps?output_format=mp3_44100_128`, {
    method: 'POST', headers: { 'xi-api-key': key(), 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`TTS ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const j = (await res.json()) as { audio_base64: string; alignment?: { characters: string[]; character_start_times_seconds: number[]; character_end_times_seconds: number[] } };
  const words: Synth['words'] = [];
  const a = j.alignment;
  if (a) {
    let cur: Synth['words'][0] | null = null;
    a.characters.forEach((c, i) => {
      if (/\s/.test(c)) { if (cur) words.push(cur); cur = null; return; }
      if (!cur) cur = { text: '', start: a.character_start_times_seconds[i], end: 0 };
      cur.text += c; cur.end = a.character_end_times_seconds[i];
    });
    if (cur) words.push(cur);
  }
  return { mp3: Buffer.from(j.audio_base64, 'base64'), words };
}

/** ElevenLabs Speech-to-Text (Uzbek). Used as an automatic "ear" for the A/B test. */
export async function transcribe(mp3: Buffer): Promise<string> {
  const fd = new FormData();
  fd.append('model_id', STT_MODEL);
  fd.append('language_code', 'uzb');
  fd.append('file', new Blob([new Uint8Array(mp3)], { type: 'audio/mpeg' }), 'a.mp3');
  const res = await fetch(`${API}/v1/speech-to-text`, { method: 'POST', headers: { 'xi-api-key': key() }, body: fd });
  if (!res.ok) throw new Error(`STT ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return ((await res.json()) as { text: string }).text;
}

/** Comparable form: Latin, lower case, one apostrophe, no punctuation. */
export function normForCompare(s: string): string {
  const lat = expandNumbers(/[Ѐ-ӿ]/.test(s) ? cyrToLat(s) : s).text; // STT writes "2026", the reference has words
  // "kh" is how STT romanises х; Uzbek Latin writes x (k+h never meet inside a native Uzbek word)
  return normalizeLatin(lat).toLowerCase().replace(/kh/g, 'x').replace(/[ʻʼ'‘’`]/g, "'").replace(/[^\p{L}\p{N}' ]+/gu, ' ').replace(/\s+/g, ' ').trim();
}

function lev<T>(a: T[], b: T[], eq: (x: T, y: T) => boolean = (x, y) => x === y) {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++)
    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (eq(a[i - 1], b[j - 1]) ? 0 : 1));
  return d;
}

export interface Score { similarity: number; cer: number; problems: { expected: string; heard: string }[]; heard: string }

/** Character error rate and the expected words the "ear" heard differently. */
export function score(expected: string, heardRaw: string): Score {
  const e = normForCompare(expected), h = normForCompare(heardRaw);
  const cer = lev([...e], [...h])[e.length][h.length] / Math.max(1, e.length);
  const ew = e.split(' '), hw = h.split(' ');
  const d = lev(ew, hw);
  const problems: Score['problems'] = [];
  let i = ew.length, j = hw.length;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && d[i][j] === d[i - 1][j - 1] + (ew[i - 1] === hw[j - 1] ? 0 : 1)) {
      if (ew[i - 1] !== hw[j - 1]) problems.unshift({ expected: ew[i - 1], heard: hw[j - 1] });
      i--; j--;
    } else if (i > 0 && d[i][j] === d[i - 1][j] + 1) { problems.unshift({ expected: ew[i - 1], heard: '∅' }); i--; }
    else { j--; }
  }
  return { similarity: Math.max(0, 1 - cer), cer, problems, heard: h };
}

export interface VariantResult { script: UzScript; prepared: Prepared; tts: string; score: Score; mp3: Buffer; words: Synth['words'] }

/**
 * Synthesize the text in Latin and in Cyrillic, transcribe both, and rank them against the spoken
 * reference (the Latin-prepared text). The automatic ear is approximate: a human listen confirms.
 */
export async function testVariants(text: string, opts: { voice?: string; model?: string; scripts?: UzScript[]; lex?: Lexicon } = {}): Promise<VariantResult[]> {
  const lex = opts.lex ?? (await loadLexicon());
  const reference = prepareUzbek(text, 'latin', lex).tts;
  const out: VariantResult[] = [];
  for (const script of opts.scripts ?? (['latin', 'cyrillic'] as UzScript[])) {
    const prepared = prepareUzbek(text, script, lex);
    const s = await synth(prepared.tts, opts);
    const heard = await transcribe(s.mp3);
    out.push({ script, prepared, tts: prepared.tts, score: score(reference, heard), mp3: s.mp3, words: s.words });
  }
  return out.sort((a, b) => b.score.similarity - a.score.similarity || (a.script === 'latin' ? -1 : 1));
}

/**
 * Re-test a single mis-read word: every candidate spelling (Latin, Cyrillic, current lexicon form, extra
 * forms you pass) is spoken in a carrier sentence and scored. The best one is saved as a lexicon candidate.
 */
export async function fixWord(word: string, opts: { voice?: string; model?: string; extra?: string[]; save?: boolean } = {}) {
  const lex = await loadLexicon();
  const k = lexKey(word);
  const prev = lex.entries[k];
  const latin = /[Ѐ-ӿ]/.test(word) ? cyrToLat(word) : normalizeLatin(word);
  const base = upsert(structuredClone(lex), word);
  const cands = [...new Set([base.latin, base.cyrillic, prev?.spoken?.latin, prev?.spoken?.cyrillic, ...(opts.extra ?? [])].filter(Boolean) as string[])];
  const results: { form: string; similarity: number; heard: string }[] = [];
  for (const form of cands) {
    const carrierLat = `Bu soʻz ${latin} deb oʻqiladi.`;
    const sent = /[Ѐ-ӿ]/.test(form) ? `Бу сўз ${form} деб ўқилади.` : `Bu soʻz ${form} deb oʻqiladi.`;
    const s = await synth(sent, opts);
    const heard = await transcribe(s.mp3);
    const sc = score(carrierLat, heard);
    const target = normForCompare(latin);
    const wordHit = sc.problems.every((p) => p.expected !== target) ? 1 : 0;
    results.push({ form, similarity: sc.similarity * 0.5 + wordHit * 0.5, heard: sc.heard });
  }
  results.sort((a, b) => b.similarity - a.similarity);
  const best = results[0];
  if (opts.save !== false && best) {
    const isCyr = /[Ѐ-ӿ]/.test(best.form);
    upsert(lex, word, {
      spoken: { ...(prev?.spoken ?? {}), [isCyr ? 'cyrillic' : 'latin']: best.form },
      prefer: isCyr ? 'cyrillic' : 'latin',
      status: prev?.status === 'approved' ? 'approved' : 'candidate',
      score: +best.similarity.toFixed(3),
      testedAt: new Date().toISOString(),
    });
    await saveLexicon(lex);
  }
  return { word, results };
}
