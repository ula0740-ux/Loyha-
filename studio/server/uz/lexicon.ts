// Persistent pronunciation dictionary (studio/lexicon/uz-lexicon.json).
// Every entry keeps the original spelling, the Latin and Cyrillic forms and the spoken form that was tested.
import { readFile, writeFile } from 'node:fs/promises';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { cyrToLat, latToCyr, detectScript, normalizeLatin } from '../../src/lib/uzbek.ts';

export type UzScript = 'latin' | 'cyrillic';
export interface LexEntry {
  original: string;
  latin: string;
  cyrillic: string;
  spoken: { latin?: string; cyrillic?: string };
  prefer: UzScript;
  status: 'approved' | 'candidate';
  score?: number; // best STT similarity 0..1 when tested
  testedAt?: string;
  notes?: string;
}
export interface Lexicon { _about?: string; entries: Record<string, LexEntry> }

export const LEXICON_FILE = process.env.UZ_LEXICON || fileURLToPath(new URL('../../lexicon/uz-lexicon.json', import.meta.url));

/** Lookup key: Latin, lower case, apostrophes unified, surrounding punctuation removed. */
export function lexKey(word: string): string {
  const w = word.replace(/^[^\p{L}\p{N}&]+|[^\p{L}\p{N}&ʻʼ']+$/gu, '');
  const lat = detectScript(w) === 'cyrillic' ? cyrToLat(w) : normalizeLatin(w);
  return lat.toLowerCase().replace(/['‘’`ʼ]/g, 'ʻ');
}

export function loadLexiconSync(file = LEXICON_FILE): Lexicon {
  try { return JSON.parse(readFileSync(file, 'utf8')); } catch { return { entries: {} }; }
}
export async function loadLexicon(file = LEXICON_FILE): Promise<Lexicon> {
  try { return JSON.parse(await readFile(file, 'utf8')); } catch { return { entries: {} }; }
}
export async function saveLexicon(lex: Lexicon, file = LEXICON_FILE) {
  const sorted = Object.fromEntries(Object.entries(lex.entries).sort(([a], [b]) => a.localeCompare(b)));
  await writeFile(file, JSON.stringify({ ...lex, entries: sorted }, null, 2) + '\n', 'utf8');
}

/** Create or update an entry. Latin/Cyrillic forms are derived when not given. */
export function upsert(lex: Lexicon, word: string, patch: Partial<LexEntry> = {}): LexEntry {
  const key = lexKey(word);
  const latin = detectScript(word) === 'cyrillic' ? cyrToLat(word) : normalizeLatin(word);
  const cyrillic = detectScript(word) === 'cyrillic' ? word : latToCyr(word);
  const prev = lex.entries[key];
  const e: LexEntry = {
    original: prev?.original ?? word,
    latin: prev?.latin ?? latin,
    cyrillic: prev?.cyrillic ?? cyrillic,
    spoken: { ...(prev?.spoken ?? { latin, cyrillic }), ...(patch.spoken ?? {}) },
    prefer: patch.prefer ?? prev?.prefer ?? 'latin',
    status: patch.status ?? prev?.status ?? 'candidate',
    ...(prev?.score !== undefined ? { score: prev.score } : {}),
    ...(prev?.notes ? { notes: prev.notes } : {}),
    ...patch,
  } as LexEntry;
  e.spoken = { ...(prev?.spoken ?? { latin, cyrillic }), ...(patch.spoken ?? {}) };
  lex.entries[key] = e;
  return e;
}
