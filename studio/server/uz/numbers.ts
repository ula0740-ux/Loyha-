// Numbers, percentages, ordinals, ranges and dates -> natural Uzbek words (Latin script; the caller converts
// to Cyrillic when that script is chosen). Written so a TTS model never sees raw digits.

const ONES = ['nol', 'bir', 'ikki', 'uch', 'toʻrt', 'besh', 'olti', 'yetti', 'sakkiz', 'toʻqqiz'];
const TENS = ['', 'oʻn', 'yigirma', 'oʻttiz', 'qirq', 'ellik', 'oltmish', 'yetmish', 'sakson', 'toʻqson'];
const SCALES: [number, string][] = [[1e9, 'milliard'], [1e6, 'million'], [1e3, 'ming']];
export const MONTHS = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr'];

function under1000(n: number): string {
  const out: string[] = [];
  const h = Math.floor(n / 100), t = Math.floor((n % 100) / 10), o = n % 10;
  // 100-199: plain "yuz" ("yuz yetmish ikki"), not "bir yuz" — the user's choice by ear (2026-10-15)
  if (h) out.push(...(h === 1 ? ['yuz'] : [ONES[h], 'yuz']));
  if (t) out.push(TENS[t]);
  if (o) out.push(ONES[o]);
  return out.join(' ');
}

/** 855 -> "sakkiz yuz ellik besh", 2026 -> "ikki ming yigirma olti" */
export function cardinal(n: number): string {
  if (!Number.isFinite(n)) return String(n);
  if (n < 0) return 'minus ' + cardinal(-n);
  n = Math.floor(n);
  if (n === 0) return ONES[0];
  const parts: string[] = [];
  for (const [v, name] of SCALES) {
    if (n >= v) { parts.push(under1000(Math.floor(n / v)), name); n %= v; }
  }
  if (n) parts.push(under1000(n));
  return parts.join(' ');
}

/** ordinal suffix: after a vowel -nchi, after a consonant -inchi (ikki -> ikkinchi, besh -> beshinchi) */
export function ordinal(n: number): string {
  const w = cardinal(n);
  return /[aeiouʻ]$/i.test(w) && !/ʻ$/.test(w) ? w + 'nchi' : w + 'inchi';
}

/** "80,1" / "80.1" -> "sakson butun oʻndan bir" */
export function decimal(s: string): string {
  const [i, f] = s.split(/[.,]/);
  if (!f) return cardinal(Number(i));
  const den = ['', 'oʻndan', 'yuzdan', 'mingdan', 'oʻn mingdan', 'yuz mingdan'][f.length] ?? 'mingdan';
  return `${cardinal(Number(i))} butun ${den} ${cardinal(Number(f))}`;
}

/** "-dan" / "-gacha" ablative/terminative after a number word (vowel harmony does not apply in Uzbek). */
const dan = (w: string) => w + 'dan';
const gacha = (w: string) => w + 'gacha';

export interface Expansion { from: string; to: string; kind: string }

/**
 * Expand every numeric expression in `text`. Returns the new text and a log of what changed.
 * Handled: dd.mm.yyyy dates, N-suffix ordinals (2026-yil, 1-hafta), ranges 5–7, percentages 80,1%,
 * thousands with spaces (1 200), decimals, plain integers.
 */
export function expandNumbers(text: string): { text: string; changes: Expansion[] } {
  const changes: Expansion[] = [];
  const rep = (re: RegExp, kind: string, fn: (...m: string[]) => string) => {
    text = text.replace(re, (...m: string[]) => { const to = fn(...m); changes.push({ from: m[0], to, kind }); return to; });
  };
  rep(/\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b/g, 'sana', (_, d, m, y) => `${ordinal(+y)} yil ${ordinal(+d)} ${MONTHS[+m - 1] ?? cardinal(+m)}`);
  rep(/\b(\d+)\s*[-–—]\s*(\d+)\s*%/g, 'oraliq-foiz', (_, a, b) => `${dan(cardinal(+a))} ${gacha(cardinal(+b))} foiz`);
  rep(/\b(\d+)\s*[–—]\s*(\d+)\b/g, 'oraliq', (_, a, b) => `${dan(cardinal(+a))} ${gacha(cardinal(+b))}`);
  const SUF = 'yil|yilgi|hafta|oy|kun|son|sinf|bosqich|chorak|qism|sahna|oʻrin|daraja|toifa';
  const SUF_CYR = 'йил|йилги|ҳафта|ой|кун|сон|синф|босқич|чорак|қисм|саҳна|ўрин|даража|тоифа';
  // the word may carry a case ending: 2026-yilda -> ikki ming yigirma oltinchi yilda
  rep(new RegExp(`(\\d+)-((?:${SUF}|${SUF_CYR})[\\p{L}ʻʼ']*)`, 'giu'), 'tartib', (_, n, w) => `${ordinal(+n)} ${w}`);
  rep(/\b(\d+(?:[.,]\d+)?)\s*%/g, 'foiz', (_, n) => `${decimal(n)} foiz`);
  rep(/\b(\d{1,3}(?: \d{3})+)\b/g, 'son', (n) => cardinal(Number(n.replace(/ /g, ''))));
  rep(/\b(\d+[.,]\d+)\b/g, 'kasr', (n) => decimal(n));
  rep(/\b(\d+)\b/g, 'son', (n) => cardinal(Number(n)));
  return { text, changes };
}
