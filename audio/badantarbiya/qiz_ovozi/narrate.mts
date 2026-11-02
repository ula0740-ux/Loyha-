// ElevenLabs narration with character timestamps -> audio/<id>.mp3 + audio/timing.json (word start/end per line).
// run from studio/: npx tsx ../video/pptx-film/narrate.mts   (needs ELEVENLABS_API_KEY)
import '../../../studio/server/net.ts';
import { prepareUzbek, spokenReference } from '../../../studio/server/uz/prepare.ts';
import { synth, transcribe, score } from '../../../studio/server/uz/eleven.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

const run = promisify(execFile);
// {English} segments are read in English (the user's choice, 2026-10-14): they bypass prepareUzbek and keep their letters;
// everything else goes through prepareUzbek as usual. Captions and timing use the text without braces.
const plain = (t: string) => t.replace(/[{}]/g, '');
function prepMixed(t: string) {
  const parts = t.split(/(\{[^}]*\})/).filter(Boolean);
  const out = parts.map((p) => {
    if (p.startsWith('{')) return p.slice(1, -1);
    const lead = /^\s/.test(p) ? ' ' : '', tail = /\s$/.test(p) ? ' ' : '';
    let tts = prepareUzbek(p, 'latin').tts;
    if (/^\s*[a-zʻ]/.test(p)) tts = tts.charAt(0).toLowerCase() + tts.slice(1); // prepareUzbek capitalises each chunk; keep mid-sentence case
    if (!/[.!?…:;,]\s*$/.test(p)) tts = tts.replace(/[.]$/, ''); // addPauses appends a stop to every chunk; keep only real ones
    return lead + tts + tail;
  });
  return { tts: out.join('').replace(/\s+/g, ' ').trim() };
}
const HERE = fileURLToPath(new URL('.', import.meta.url));
const cfg = JSON.parse(await readFile(HERE + 'narration.json', 'utf8'));
const voice = process.env.VOICE || cfg.voice;
await mkdir(HERE + 'audio', { recursive: true });

// ONLY=id1,id2 re-records just those lines and keeps the rest of timing.json
const only = (process.env.ONLY || '').split(',').filter(Boolean);
let timing: Record<string, { duration: number; words: { text: string; start: number; end: number }[] }> = {};
if (only.length) timing = JSON.parse(await readFile(HERE + 'audio/timing.json', 'utf8'));
for (const line of cfg.lines) {
  if (only.length && !only.includes(line.id)) continue;
  // text stays in correct literary spelling; prepareUzbek (Uzbek Latin only) applies the tested lexicon and numbers
  const prep = prepMixed(line.text);
  const shown = plain(line.text).split(/\s+/).filter(Boolean);
  // automatic ear: each take is transcribed (STT) and compared; up to ATTEMPTS takes, the best one is kept (CHECK=0 skips)
  const attempts = process.env.CHECK === '0' ? 1 : Number(process.env.ATTEMPTS || 4);
  let best: { s: Awaited<ReturnType<typeof synth>>; sc?: ReturnType<typeof score> } | null = null;
  for (let k = 0; k < attempts; k++) {
    // neighbouring lines as context (previous_text/next_text; sent only to models that accept it, e.g. eleven_v4):
    // without it eleven_v4 sometimes gives a short line a Persian accent
    const idx = cfg.lines.indexOf(line);
    // context sentences go through prepareUzbek in full (English words included): English context pulled
    // "ADM" towards an English reading (heard by the user, 2026-10-15)
    const ctx = { previousText: cfg.lines[idx - 1] && prepareUzbek(plain(cfg.lines[idx - 1].text), 'latin').tts, nextText: cfg.lines[idx + 1] && prepareUzbek(plain(cfg.lines[idx + 1].text), 'latin').tts };
    const s = await synth(prep.tts, { voice, model: cfg.model, ...ctx });
    const sc = process.env.CHECK === '0' ? undefined : score(spokenReference(plain(line.text)), await transcribe(s.mp3));
    if (sc) console.log(`  ${line.id} #${k + 1}: STT ${(sc.similarity * 100).toFixed(1)}%${sc.problems.map((p) => `  ✗ ${p.expected}->${p.heard}`).join('')}`);
    if (!best || (sc && best.sc && sc.similarity > best.sc.similarity)) best = { s, sc };
    if (!sc || (sc.similarity >= 0.97 && !sc.problems.some((p) => /x/.test(p.expected)))) break;
  }
  const s = best!.s;
  const mp3 = `${HERE}audio/${line.id}.mp3`;
  await writeFile(mp3, s.mp3);
  // keep the written words in timing.json (film.html addresses words by index)
  const words = s.words.length === shown.length ? s.words.map((w, i) => ({ ...w, text: shown[i] })) : s.words;
  console.log(`  ${line.id}: ${prep.tts}`);
  const { stdout } = await run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]);
  timing[line.id] = { duration: Number(stdout), words };
  console.log(`✓ ${line.id} ${Number(stdout).toFixed(2)}s  ${words.length}/${shown.length} soʻz`);
}
await writeFile(HERE + 'audio/timing.json', JSON.stringify(timing, null, 1));
