// Uzbek script helpers: Cyrillic <-> Latin (1995 official Latin alphabet) and script detection.
// Used so that every TTS voice gets the script it actually reads correctly.

export type Script = 'latin' | 'cyrillic';

const OKINA = 'ʻ'; // U+02BB, used in oʻ and gʻ
const TUTUQ = 'ʼ'; // U+02BC, the apostrophe sign (tutuq belgisi)
const APOS = /['‘’`ʻʼ]/g;

export function detectScript(text: string): Script {
  const cyr = (text.match(/[Ѐ-ӿ]/g) || []).length;
  const lat = (text.match(/[a-zA-Z]/g) || []).length;
  return cyr > lat ? 'cyrillic' : 'latin';
}

/** Normalise the many apostrophe variants people type: oʻ/gʻ get U+02BB, the rest U+02BC. */
export function normalizeLatin(text: string): string {
  return text.replace(/([oOgG])['‘’`ʻʼ]/g, `$1${OKINA}`).replace(/([^oOgG])['‘’`ʼ]/g, `$1${TUTUQ}`);
}

const VOWELS_CYR = 'аеёиоуўэюяъь';
const isUpper = (c: string) => c !== c.toLowerCase();
const matchCase = (src: string, out: string, nextUpper: boolean) =>
  !isUpper(src) ? out : nextUpper || out.length === 1 ? out.toUpperCase() : out[0].toUpperCase() + out.slice(1);

export function cyrToLat(text: string): string {
  const map: Record<string, string> = {
    а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', ж: 'j', з: 'z', и: 'i', й: 'y', к: 'k', л: 'l', м: 'm', н: 'n',
    о: 'o', п: 'p', р: 'r', с: 's', т: 't', у: 'u', ф: 'f', х: 'x', ч: 'ch', ш: 'sh', ъ: TUTUQ, ь: '',
    э: 'e', ю: 'yu', я: 'ya', ё: 'yo', ў: 'o' + OKINA, қ: 'q', ғ: 'g' + OKINA, ҳ: 'h', щ: 'sh',
  };
  let out = '';
  for (let i = 0; i < text.length; i++) {
    const ch = text[i], lo = ch.toLowerCase();
    const prev = i > 0 ? text[i - 1].toLowerCase() : ' ';
    const next = text[i + 1] ?? '';
    const nextUpper = !!next && isUpper(next) && /[Ѐ-ӿ]/.test(next);
    const atWordStart = !/[Ѐ-ӿa-z]/i.test(prev);
    let rep: string | undefined;
    // с + ҳ is two sounds (Исҳоқ -> Isʼhoq), not the digraph sh
    if (lo === 'ҳ' && prev === 'с') { out += TUTUQ + matchCase(ch, 'h', nextUpper); continue; }
    if (lo === 'е') rep = atWordStart || VOWELS_CYR.includes(prev) ? 'ye' : 'e';
    else if (lo === 'ц') rep = atWordStart || !VOWELS_CYR.includes(prev) ? 's' : 'ts';
    else rep = map[lo];
    out += rep === undefined ? ch : matchCase(ch, rep, nextUpper);
  }
  return out;
}

export function latToCyr(input: string): string {
  const text = normalizeLatin(input);
  const pairs: [string, string][] = [
    ['o' + OKINA, 'ў'], ['g' + OKINA, 'ғ'], ['sh', 'ш'], ['ch', 'ч'], ['yo', 'ё'], ['yu', 'ю'], ['ya', 'я'], ['ye', 'е'],
  ];
  const single: Record<string, string> = {
    a: 'а', b: 'б', d: 'д', e: 'е', f: 'ф', g: 'г', h: 'ҳ', i: 'и', j: 'ж', k: 'к', l: 'л', m: 'м', n: 'н', o: 'о',
    p: 'п', q: 'қ', r: 'р', s: 'с', t: 'т', u: 'у', v: 'в', x: 'х', y: 'й', z: 'з', [TUTUQ]: 'ъ',
  };
  let out = '';
  for (let i = 0; i < text.length; ) {
    const prev = i > 0 ? text[i - 1] : ' ';
    const atWordStart = !/[a-zA-Zʻʼ]/.test(prev);
    const two = text.slice(i, i + 2), lo2 = two.toLowerCase();
    const pair = pairs.find(([l]) => l === lo2);
    if (pair) {
      const up = isUpper(two[0]);
      out += up ? pair[1].toUpperCase() : pair[1];
      i += 2;
      continue;
    }
    const ch = text[i], lo = ch.toLowerCase();
    // sʼh: the apostrophe only separates s and h in Latin; Cyrillic needs no sign (Isʼhoq -> Исҳоқ)
    if (ch === TUTUQ && /[sS]/.test(prev) && /[hH]/.test(text[i + 1] ?? '')) { i += 1; continue; }
    let rep = single[lo];
    if (lo === 'e' && atWordStart) rep = 'э';
    out += rep === undefined ? ch : isUpper(ch) ? rep.toUpperCase() : rep;
    i += 1;
  }
  return out;
}

/** Return the text in the requested script (only Uzbek text is converted). */
export function toScript(text: string, target: Script): string {
  const src = detectScript(text);
  if (src === target) return target === 'latin' ? normalizeLatin(text) : text;
  return target === 'latin' ? cyrToLat(text) : latToCyr(text);
}
