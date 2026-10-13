// Sentence-by-sentence narration with a cache, an STT check per sentence and partial re-generation.
// Every sentence is synthesized on its own and cached by hash(prepared text + voice + model): after a lexicon fix or
// a text edit, only the sentences whose prepared text changed are generated again; `redo` forces chosen ones.
import { createHash } from 'node:crypto';
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { dirname, join, resolve } from 'node:path';
import { prepareUzbek, addPauses } from './prepare.ts';
import { synth, transcribe, score, DEFAULT_MODEL, DEFAULT_VOICE, MODEL_CAPS, type Score } from './eleven.ts';
import { loadLexicon } from './lexicon.ts';

const run = promisify(execFile);

/** Split into sentences, keeping the closing punctuation (it gives the pause). */
export function splitSentences(text: string): string[] {
  return (addPauses(text).match(/[^.!?…]+(?:[.!?…]+|$)/g) ?? []).map((s) => s.trim()).filter(Boolean);
}

export interface Segment {
  i: number;
  text: string; // as written
  tts: string; // sent to the model
  hash: string;
  file: string;
  duration: number;
  similarity?: number;
  problems?: Score['problems'];
  heard?: string;
  takes: number;
}
export interface NarrationReport { out: string; voice: string; model: string; createdAt: string; segments: Segment[] }

export interface MakeOpts { voice?: string; model?: string; check?: boolean; min?: number; attempts?: number; cacheDir?: string; redo?: number[]; log?: (s: string) => void }

async function duration(f: string) {
  const { stdout } = await run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]);
  return Number(stdout);
}

/** Build `out` (.mp3) from `text`. Writes `out` with .json next to it (the report used by `redo`). */
export async function makeNarration(text: string, out: string, o: MakeOpts = {}): Promise<NarrationReport> {
  const voice = o.voice || DEFAULT_VOICE, model = o.model || DEFAULT_MODEL;
  const cache = resolve(o.cacheDir || join(dirname(out), 'uz-cache'));
  const log = o.log ?? ((s: string) => console.log(s));
  await mkdir(cache, { recursive: true });
  const lex = await loadLexicon();
  const sentences = splitSentences(text);
  const segs: Segment[] = [];
  for (const [i, sentence] of sentences.entries()) {
    const tts = prepareUzbek(sentence, 'latin', lex).tts;
    const hash = createHash('sha1').update(`${model}|${voice}|${tts}`).digest('hex').slice(0, 16);
    const file = join(cache, `${hash}.mp3`), meta = join(cache, `${hash}.json`);
    if (o.redo?.includes(i + 1)) await rm(file, { force: true });
    if (existsSync(file) && existsSync(meta)) {
      segs.push({ ...(JSON.parse(await readFile(meta, 'utf8')) as Segment), i: i + 1, text: sentence, file });
      log(`  ${i + 1}. (keshdan) ${sentence}`);
      continue;
    }
    // context between sentences only where the model accepts it (not eleven_v3)
    const ctx = MODEL_CAPS[model]?.contextText
      ? { previousText: sentences[i - 1] && prepareUzbek(sentences[i - 1], 'latin', lex).tts, nextText: sentences[i + 1] && prepareUzbek(sentences[i + 1], 'latin', lex).tts }
      : {};
    let best: { mp3: Buffer; sc?: Score } | null = null;
    let takes = 0;
    for (let k = 0; k < (o.check === false ? 1 : o.attempts ?? 3); k++) {
      takes++;
      const s = await synth(tts, { voice, model, ...ctx });
      const sc = o.check === false ? undefined : score(tts, await transcribe(s.mp3));
      if (!best || (sc && best.sc && sc.similarity > best.sc.similarity)) best = { mp3: s.mp3, sc };
      if (!sc || sc.similarity >= (o.min ?? 0.97)) break;
    }
    await writeFile(file, best!.mp3);
    const seg: Segment = { i: i + 1, text: sentence, tts, hash, file, duration: await duration(file), takes, similarity: best!.sc?.similarity, problems: best!.sc?.problems, heard: best!.sc?.heard };
    await writeFile(meta, JSON.stringify(seg, null, 1));
    segs.push(seg);
    log(`  ${i + 1}. ${seg.similarity !== undefined ? (seg.similarity * 100).toFixed(1) + '%' : ''} ${tts}${(seg.problems ?? []).map((p) => `  ✗ ${p.expected}->${p.heard}`).join('')}`);
  }
  await mkdir(dirname(out), { recursive: true });
  const list = join(cache, `list-${process.pid}.txt`);
  await writeFile(list, segs.map((s) => `file '${s.file.replace(/'/g, "'\\''")}'`).join('\n'));
  await run('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c:a', 'libmp3lame', '-b:a', '128k', out]);
  await rm(list, { force: true });
  const report: NarrationReport = { out, voice, model, createdAt: new Date().toISOString(), segments: segs };
  await writeFile(out.replace(/\.mp3$/, '') + '.json', JSON.stringify(report, null, 1));
  return report;
}

/** Re-generate only the given sentence numbers (1-based) of an existing narration, keeping the rest. */
export async function redoNarration(reportFile: string, which: number[], o: MakeOpts = {}) {
  const r = JSON.parse(await readFile(reportFile, 'utf8')) as NarrationReport;
  const text = r.segments.map((s) => s.text).join(' ');
  return makeNarration(text, r.out, { voice: r.voice, model: r.model, ...o, redo: which, cacheDir: dirname(r.segments[0].file) });
}
