// Prepare Uzbek text (Latin, Cyrillic or mixed) for natural literary pronunciation by a TTS model.
// Rules (kept permanently, see CLAUDE.md and .claude/skills/uzbek-tts):
//  - TTS text is Uzbek Latin only (Cyrillic input is converted to Latin); no English/Russian respelling.
//  - x = х (deep x) and h = ҳ (soft h) are distinct letters: never swapped, never dropped, never respelled as "ks".
//  - oʻ = ў, gʻ = ғ, q = қ, sh = ш, ch = ч, ng = нг: handled by the script converter, one letter for one letter.
//  - Uzbek words are normalised to ONE chosen script; foreign words (Russian, English) are left as written.
//  - Numbers, percentages, dates, ranges and abbreviations become words; the lexicon overrides everything.
//  - The original text is always returned untouched next to the prepared one.
import { cyrToLat, latToCyr, normalizeLatin } from '../../src/lib/uzbek.ts';
import { expandNumbers, type Expansion } from './numbers.ts';
import { lexKey, loadLexiconSync, type Lexicon, type UzScript } from './lexicon.ts';

export type Lang = 'uz' | 'ru' | 'en' | 'num' | 'sym';
export interface Token { text: string; lang: Lang; out: string; via?: 'lexicon' | 'script' | 'keep' | 'abbr' }
export interface Prepared {
  original: string;
  script: UzScript;
  normalized: string; // Uzbek words in the chosen script, numbers still as digits (for display/checking)
  tts: string; // what is sent to the TTS model
  tokens: Token[];
  numbers: Expansion[];
  warnings: string[];
}

const UZ_CYR = /[ҳқғўҲҚҒЎ]/;
const RU_CYR = /[ыщЫЩ]/;
const UZ_LAT = /(oʻ|gʻ|o'|g'|o‘|g‘|sh|ch|ng|q|x)/i;
const EN_HINT = /(w|c(?!h)|th|ee|oo|tion|ph)/i;
const EN_WORDS = new Set(['of', 'the', 'and', 'for', 'head', 'engineer', 'manager', 'team', 'design', 'motion', 'video', 'online', 'standard']);
// Uzbek names of Latin letters, used to spell unknown abbreviations ("KSt" -> "ka es te")
// (x is "xa", never English "iks")
const LETTER: Record<string, string> = { a: 'a', b: 'be', c: 'se', d: 'de', e: 'e', f: 'ef', g: 'ge', h: 'ha', i: 'i', j: 'je', k: 'ka', l: 'el', m: 'em', n: 'en', o: 'o', p: 'pe', q: 'qa', r: 'er', s: 'es', t: 'te', u: 'u', v: 've', w: 've', x: 'xa', y: 'ye', z: 'ze' };

/** Spoken form of the Uzbek deep x for the TTS model: x -> kh, X -> Kh (KH in an all-caps word). */
export const xToKh = (w: string) => w.replace(/x/g, 'kh').replace(/X(?=[A-Z]|$)/g, 'KH').replace(/X/g, 'Kh');

/** Natural pauses come from punctuation: every line and the whole text end with a sentence mark. */
export function addPauses(text: string): string {
  return text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => (/[.!?…:;,]$/.test(l) ? l : l + '.'))
    .join(' ');
}

/** Classify one word: Uzbek, Russian or English (heuristic, documented in README). */
export function wordLang(w: string): Lang {
  const core = w.replace(/[^\p{L}ʻʼ'‘’`]/gu, '');
  if (!core) return /\d/.test(w) ? 'num' : 'sym';
  if (/[Ѐ-ӿ]/.test(core)) {
    if (UZ_CYR.test(core)) return 'uz';
    if (RU_CYR.test(core)) return 'ru';
    return 'uz';
  }
  const lc = core.toLowerCase();
  if (EN_WORDS.has(lc)) return 'en';
  if (UZ_LAT.test(core)) return 'uz';
  if (EN_HINT.test(core)) return 'en';
  return 'uz';
}

// ALL-CAPS word that is not a capitalised Uzbek word: up to 3 letters, or no vowel at all ("KST", "HR"; not "XODIM")
const isAbbr = (w: string) => /^[A-Z&]{2,6}$/.test(w) && (w.length <= 3 || !/[AEIOU]/.test(w));

const toScript = (w: string, script: UzScript) => {
  const isCyr = /[Ѐ-ӿ]/.test(w);
  if (script === 'cyrillic') return isCyr ? w : latToCyr(w);
  return isCyr ? cyrToLat(w) : normalizeLatin(w);
};

/**
 * Prepare `text` for TTS (Latin by default; the project rule is Latin only). Lexicon entries win: their tested
 * spoken form is used (e.g. "Jizzax" -> "Jiz-zax": same letters, a syllable break the model reads correctly).
 */
export function prepareUzbek(text: string, script: UzScript = 'latin', lex: Lexicon = loadLexiconSync(), opts: { xAsKh?: boolean; keepAbbr?: boolean } = {}): Prepared {
  const xAsKh = opts.xAsKh ?? process.env.UZ_X_KH !== '0';
  const warnings: string[] = [];
  const parts = addPauses(text).split(/(\s+)/);
  const tokens: Token[] = [];
  const outNorm: string[] = [];
  const outTts: string[] = [];

  for (const part of parts) {
    if (/^\s*$/.test(part)) { outNorm.push(part); outTts.push(part); continue; }
    const m = part.match(/^([^\p{L}\p{N}&]*)(.*?)([^\p{L}\p{N}&ʻʼ'‘’`]*)$/u)!;
    const [, lead, core, trail] = m;
    const key = lexKey(core);
    const hit = key ? lex.entries[key] : undefined;
    // an ALL-CAPS lexicon entry (IT, HR) only matches ALL-CAPS text: Uzbek "it" (dog) is not "IT"
    const entry = hit && /^[^a-zʻ]*[A-Z][^a-z]*$/.test(hit.original) && core !== core.toUpperCase() ? undefined : hit;
    const lang = wordLang(core);
    let norm = core, spoken = core, via: Token['via'] = 'keep';

    if (entry) {
      norm = script === 'cyrillic' ? entry.cyrillic : entry.latin;
      spoken = entry.spoken[script] ?? norm;
      via = 'lexicon';
      if ((entry.kind === 'term' || entry.kind === 'abbr') && spoken !== core) warnings.push(`ℹ ${core} → ${spoken} (lugʻatdagi oʻzbekcha shakl)`);
    } else if (isAbbr(core) && !opts.keepAbbr) {
      spoken = core.toLowerCase().split('').map((c) => LETTER[c] ?? c).join(' ');
      via = 'abbr';
      warnings.push(`Lugʻatda yoʻq qisqartma harflab oʻqiladi: ${core} → ${spoken} (npm run uz -- lexicon add ${core} ...)`);
    } else if (lang === 'uz') {
      norm = spoken = toScript(core, script);
      via = 'script';
    } else if (lang === 'ru' || lang === 'en') {
      warnings.push(`Oʻzbekcha boʻlmagan soʻz oʻzgarishsiz qoldi (${lang}): ${core}`);
    }
    // deep x: the model reads Latin "x" as "eks"; "kh" gives the throat sound (chosen by ear by the user, 2026-10-13,
    // eleven_v4 + language_code uz). Spoken form only; the written text keeps x. x is never turned into h.
    if (script === 'latin' && xAsKh && via !== 'keep') spoken = xToKh(spoken);
    tokens.push({ text: core, lang, out: spoken, via });
    outNorm.push(lead + norm + trail);
    outTts.push(lead + spoken + trail);
  }

  const normalized = outNorm.join('');
  const num = expandNumbers(outTts.join(''));
  let tts = num.text;
  if (script === 'cyrillic') tts = tts.replace(/[A-Za-zʻʼ]+/g, (w) => (wordLang(w) === 'uz' ? latToCyr(w) : w));
  // a sentence starts with a capital letter, also when it starts with a spelled-out number
  tts = tts.replace(/\s+/g, ' ').trim().replace(/(^|[.!?…]\s+)(\p{Ll})/gu, (_, a: string, b: string) => a + b.toUpperCase());
  return { original: text, script, normalized, tts, tokens, numbers: num.changes, warnings };
}

/** What a listener should hear, written plainly: Latin, numbers in words, abbreviations as written, x as x.
 *  Used as the STT reference so lexicon spellings ("A-de-em", "Jizzakh") are not counted as errors. */
export function spokenReference(text: string): string {
  return prepareUzbek(text, 'latin', { entries: {} }, { xAsKh: false, keepAbbr: true }).tts;
}
