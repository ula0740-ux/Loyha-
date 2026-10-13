// ElevenLabs narration with character timestamps -> audio/<id>.mp3 + audio/timing.json (word start/end per line).
// run from studio/: npx tsx ../video/pptx-film/narrate.mts   (needs ELEVENLABS_API_KEY)
import '../../studio/server/net.ts';
import { prepareUzbek } from '../../studio/server/uz/prepare.ts';
import { synth, transcribe, score } from '../../studio/server/uz/eleven.ts';
import type { UzScript } from '../../studio/server/uz/lexicon.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

const run = promisify(execFile);
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
  // text stays in correct literary spelling; prepareUzbek applies the tested lexicon (Jizzax -> Жиззах) and numbers
  const prep = prepareUzbek(line.text, (process.env.UZ_SCRIPT as UzScript) || cfg.script || 'latin');
  const s = await synth(prep.tts, { voice, model: cfg.model });
  const mp3 = `${HERE}audio/${line.id}.mp3`;
  await writeFile(mp3, s.mp3);
  const shown = line.text.split(/\s+/).filter(Boolean);
  // keep the written words in timing.json (film.html addresses words by index)
  const words = s.words.length === shown.length ? s.words.map((w, i) => ({ ...w, text: shown[i] })) : s.words;
  // automatic ear: Speech-to-Text of the take, compared with the intended text (CHECK=0 skips it)
  if (process.env.CHECK !== '0') {
    const sc = score(prepareUzbek(line.text, 'latin').tts, await transcribe(s.mp3));
    console.log(`  ${line.id}: ${prep.tts}\n  STT ${(sc.similarity * 100).toFixed(1)}%${sc.problems.map((p) => `  ✗ ${p.expected}->${p.heard}`).join('')}`);
  }
  const { stdout } = await run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]);
  timing[line.id] = { duration: Number(stdout), words };
  console.log(`✓ ${line.id} ${Number(stdout).toFixed(2)}s  ${words.length}/${shown.length} soʻz`);
}
await writeFile(HERE + 'audio/timing.json', JSON.stringify(timing, null, 1));
