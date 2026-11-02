// ElevenLabs for Uzbek: model capabilities, synthesis with timestamps, Speech-to-Text check,
// Latin vs Cyrillic A/B testing and re-generation of mis-read words.
import { cyrToLat, normalizeLatin } from '../../src/lib/uzbek.ts';
import { prepareUzbek, spokenReference, xToKh, type Prepared } from './prepare.ts';
import { expandNumbers } from './numbers.ts';
import { lexKey, loadLexicon, saveLexicon, sameLetters, upsert, type Lexicon, type UzScript } from './lexicon.ts';

export const API = 'https://api.elevenlabs.io';
// eleven_v4 + language_code uz + x spoken as "kh": chosen by ear by the user (2026-10-13)
export const DEFAULT_MODEL = process.env.ELEVENLABS_MODEL || 'eleven_v4';
export const DEFAULT_VOICE = process.env.ELEVENLABS_VOICE_FEMALE || 'EXAVITQu4vr4xnSDxMaL';
export const STT_MODEL = 'scribe_v1';

/**
 * Only parameters the model accepted in a live test are sent (2026-10-13, this account):
 * - language_code "uz": accepted by eleven_v4; 400 unsupported_language on eleven_v3, eleven_multilingual_v2,
 *   eleven_flash_v2_5, eleven_turbo_v2_5.
 * - previous_text/next_text (context between sentences): eleven_v4, eleven_multilingual_v2; 400 on eleven_v3.
 * - seed: accepted by eleven_v3, eleven_v4, eleven_multilingual_v2.
 * Unknown models get none of these.
 */
export interface ModelCaps { uzLanguageCode: boolean; contextText: boolean; seed: boolean }
export const MODEL_CAPS: Record<string, ModelCaps> = {
  eleven_v4: { uzLanguageCode: true, contextText: true, seed: true },
  eleven_v3: { uzLanguageCode: false, contextText: false, seed: true },
  eleven_multilingual_v2: { uzLanguageCode: false, contextText: true, seed: true },
  eleven_flash_v2_5: { uzLanguageCode: false, contextText: false, seed: false },
  eleven_turbo_v2_5: { uzLanguageCode: false, contextText: false, seed: false },
};

/** Request body with only the parameters `model` supports. */
/** ElevenLabs voice_settings (stability, similarity_boost, style, use_speaker_boost) — sent only when given. */
export interface VoiceSettings { stability?: number; similarity_boost?: number; style?: number; use_speaker_boost?: boolean }

export function ttsBody(text: string, model: string, o: { seed?: number; previousText?: string; nextText?: string; voiceSettings?: VoiceSettings } = {}) {
  const caps = MODEL_CAPS[model];
  const body: Record<string, unknown> = { text, model_id: model };
  if (caps?.uzLanguageCode) body.language_code = 'uz';
  if (caps?.seed && o.seed !== undefined) body.seed = o.seed;
  if (caps?.contextText && o.previousText) body.previous_text = o.previousText;
  if (caps?.contextText && o.nextText) body.next_text = o.nextText;
  if (o.voiceSettings) body.voice_settings = o.voiceSettings;   // eleven_v4 accepted it in a live test (2026-10-23)
  return body;
}

const key = () => {
  const k = process.env.ELEVENLABS_API_KEY?.trim();
  if (!k) throw new Error('ELEVENLABS_API_KEY topilmadi (.env yoki muhit oʻzgaruvchisi).');
  return k;
};

export interface Synth { mp3: Buffer; words: { text: string; start: number; end: number }[] }

export interface SynthOpts { voice?: string; model?: string; seed?: number; previousText?: string; nextText?: string; voiceSettings?: VoiceSettings }

export async function synth(text: string, opts: SynthOpts = {}): Promise<Synth> {
  const model = opts.model || DEFAULT_MODEL;
  const body = ttsBody(text, model, opts);
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
  // a syllable break from the lexicon ("Jiz-zax") is the same word as "Jizzax"
  return normalizeLatin(lat).toLowerCase().replace(/kh/g, 'x').replace(/(\p{L})-(?=\p{L})/gu, '$1').replace(/[ʻʼ'‘’`]/g, "'").replace(/[^\p{L}\p{N}' ]+/gu, ' ').replace(/\s+/g, ' ').trim();
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
 * Synthesize the prepared text (Latin; several takes if asked), transcribe each take and rank them against the
 * spoken reference. The automatic ear is approximate: a human listen confirms.
 */
export async function testVariants(text: string, opts: { voice?: string; model?: string; scripts?: UzScript[]; lex?: Lexicon; takes?: number } = {}): Promise<VariantResult[]> {
  const lex = opts.lex ?? (await loadLexicon());
  const reference = spokenReference(text);
  const out: VariantResult[] = [];
  // project rule: Latin only. Cyrillic can still be compared on request (--script cyrillic).
  for (const script of opts.scripts ?? (['latin'] as UzScript[]))
    for (let k = 0; k < (opts.takes ?? 1); k++) {
      const prepared = prepareUzbek(text, script, lex);
      const s = await synth(prepared.tts, opts);
      const heard = await transcribe(s.mp3);
      out.push({ script, prepared, tts: prepared.tts, score: score(reference, heard), mp3: s.mp3, words: s.words });
    }
  return out.sort((a, b) => b.score.similarity - a.score.similarity || (a.script === 'latin' ? -1 : 1));
}

/** Latin spellings with the same letters and one syllable break: "Jizzax" -> "Jiz-zax", "Ji-zzax", ... */
export function syllableForms(word: string): string[] {
  const out: string[] = [];
  const V = /[aeiouAEIOU]/;
  for (let i = 1; i < word.length - 1; i++) {
    const a = word[i - 1], b = word[i];
    if (/[ʻʼ']/.test(b) || /[ʻʼ']/.test(a)) continue;
    if (/^(sh|ch|ng)$/i.test(a + b)) continue; // never split a digraph
    // break between two consonants, or before a consonant that follows a vowel
    if ((!V.test(a) && !V.test(b) && /\p{L}/u.test(a) && /\p{L}/u.test(b)) || (V.test(a) && !V.test(b) && V.test(word[i + 1] ?? ''))) out.push(word.slice(0, i) + '-' + word.slice(i));
  }
  return out;
}

/**
 * Re-test a single mis-read word. Candidates are Latin only and keep every letter (the plain word, syllable
 * breaks, the current lexicon form and extra forms you pass); each is spoken `takes` times in a carrier sentence
 * and scored by the STT ear. The best one is saved as a lexicon candidate.
 */
export async function fixWord(word: string, opts: { voice?: string; model?: string; extra?: string[]; save?: boolean; takes?: number } = {}) {
  const lex = await loadLexicon();
  const k = lexKey(word);
  const prev = lex.entries[k];
  const latin = /[Ѐ-ӿ]/.test(word) ? cyrToLat(word) : normalizeLatin(word);
  const cands = [...new Set([latin, prev?.spoken?.latin, ...syllableForms(latin), ...(opts.extra ?? [])].filter(Boolean) as string[])]
    .filter((f) => !/[Ѐ-ӿ]/.test(f));
  const rejected = cands.filter((f) => !sameLetters(f, latin) && prev?.kind !== 'term' && prev?.kind !== 'abbr');
  const results: { form: string; similarity: number; heard: string[] }[] = [];
  const target = normForCompare(latin);
  for (const form of cands.filter((f) => !rejected.includes(f))) {
    let sum = 0;
    const heard: string[] = [];
    for (let t = 0; t < (opts.takes ?? 2); t++) {
      const say = xToKh(form);
      const s = await synth(`${say}. Bu soʻz ${say} deb oʻqiladi.`, opts);
      const sc = score(`${latin}. Bu soʻz ${latin} deb oʻqiladi.`, await transcribe(s.mp3));
      const hits = sc.problems.filter((p) => p.expected === target).length;
      sum += sc.similarity * 0.4 + (1 - hits / 2) * 0.6;
      heard.push(sc.heard);
    }
    results.push({ form, similarity: sum / (opts.takes ?? 2), heard });
  }
  results.sort((a, b) => b.similarity - a.similarity || a.form.length - b.form.length);
  const best = results[0];
  if (opts.save !== false && best) {
    upsert(lex, word, {
      spoken: { ...(prev?.spoken ?? {}), latin: best.form },
      prefer: 'latin',
      kind: prev?.kind ?? 'word',
      status: prev?.status === 'approved' ? 'approved' : 'candidate',
      score: +best.similarity.toFixed(3),
      testedAt: new Date().toISOString(),
    });
    await saveLexicon(lex);
  }
  return { word, results, rejected };
}
