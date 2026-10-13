// Prepare Uzbek text (Latin, Cyrillic or mixed) for natural literary pronunciation by a TTS model.
// Rules (kept permanently, see CLAUDE.md):
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
const LETTER: Record<string, string> = { a: 'a', b: 'be', c: 'se', d: 'de', e: 'e', f: 'ef', g: 'ge', h: 'ha', i: 'i', j: 'je', k: 'ka', l: 'el', m: 'em', n: 'en', o: 'o', p: 'pe', q: 'qu', r: 'er', s: 'es', t: 'te', u: 'u', v: 've', w: 'dabl-yu', x: 'iks', y: 'ye', z: 'ze' };

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
 * Prepare `text` for TTS in `script`. Lexicon entries win; their `prefer` script is used for that word even
 * inside a sentence of the other script (e.g. "Жиззах" inside Latin text), because that form was tested.
 */
export function prepareUzbek(text: string, script: UzScript, lex: Lexicon = loadLexiconSync()): Prepared {
  const warnings: string[] = [];
  const parts = text.split(/(\s+)/);
  const tokens: Token[] = [];
  const outNorm: string[] = [];
  const outTts: string[] = [];

  for (const part of parts) {
    if (/^\s*$/.test(part)) { outNorm.push(part); outTts.push(part); continue; }
    const m = part.match(/^([^\p{L}\p{N}&]*)(.*?)([^\p{L}\p{N}&ʻʼ'‘’`]*)$/u)!;
    const [, lead, core, trail] = m;
    const key = lexKey(core);
    const entry = key ? lex.entries[key] : undefined;
    const lang = wordLang(core);
    let norm = core, spoken = core, via: Token['via'] = 'keep';

    if (entry) {
      norm = script === 'cyrillic' ? entry.cyrillic : entry.latin;
      spoken = entry.spoken[entry.prefer] ?? entry.spoken[script] ?? norm;
      via = 'lexicon';
    } else if (isAbbr(core)) {
      spoken = core.toLowerCase().split('').map((c) => LETTER[c] ?? c).join(' ');
      via = 'abbr';
      warnings.push(`Lugʻatda yoʻq qisqartma harflab oʻqiladi: ${core} → ${spoken} (npm run uz -- lexicon add ${core} ...)`);
    } else if (lang === 'uz') {
      norm = spoken = toScript(core, script);
      via = 'script';
    } else if (lang === 'ru' || lang === 'en') {
      warnings.push(`Oʻzbekcha boʻlmagan soʻz oʻzgarishsiz qoldi (${lang}): ${core}`);
    }
    // a word with Latin x read in Latin script is the classic "eks" risk: flag it unless the lexicon decided
    if (!entry && via === 'script' && script === 'latin' && /x/i.test(spoken)) {
      warnings.push(`"${core}": lotincha x — kirill varianti bilan solishtirib tekshiring (npm run uz -- test).`);
    }
    tokens.push({ text: core, lang, out: spoken, via });
    outNorm.push(lead + norm + trail);
    outTts.push(lead + spoken + trail);
  }

  const normalized = outNorm.join('');
  const num = expandNumbers(outTts.join(''));
  let tts = num.text;
  if (script === 'cyrillic') tts = tts.replace(/[A-Za-zʻʼ]+/g, (w) => (wordLang(w) === 'uz' && !Object.values(lex.entries).some((e) => e.spoken.latin === w && e.prefer === 'latin') ? latToCyr(w) : w));
  return { original: text, script, normalized, tts: tts.replace(/\s+/g, ' ').trim(), tokens, numbers: num.changes, warnings };
}
