// Install chosen takes as audio/<id>.mp3 + timing.json (written words when the token count matches, as narrate.mts),
// after an STT check of the whole take. usage (from studio/): npx tsx ../video/adm-profile/build/install_takes.mts id=/path/take.mp3 …
// (each take has a sibling .json with {words} from the TTS alignment)
import '../../../studio/server/net.ts';
import { spokenReference } from '../../../studio/server/uz/prepare.ts';
import { transcribe, score } from '../../../studio/server/uz/eleven.ts';
import { readFile, writeFile, copyFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const HERE = fileURLToPath(new URL('../', import.meta.url));
const cfg = JSON.parse(await readFile(HERE + 'narration.json', 'utf8'));
const timing = JSON.parse(await readFile(HERE + 'audio/timing.json', 'utf8'));
for (const a of process.argv.slice(2)) {
  const [id, f] = a.split('='); const line = cfg.lines.find((l: { id: string }) => l.id === id);
  const plain = line.text.replace(/[{}]/g, ''), shown = plain.split(/\s+/).filter(Boolean);
  const mp3 = await readFile(f), j = JSON.parse(await readFile(f.replace(/\.mp3$/, '.json'), 'utf8'));
  const sc = score(spokenReference(plain), await transcribe(mp3));
  console.log(`${id}: STT ${(sc.similarity * 100).toFixed(1)}%${sc.problems.map((p) => `  ✗ ${p.expected}->${p.heard}`).join('')}  | ${sc.heard}`);
  await copyFile(f, `${HERE}audio/${id}.mp3`);
  const words = j.words.length === shown.length ? j.words.map((w: object, i: number) => ({ ...w, text: shown[i] })) : j.words;
  const duration = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', `${HERE}audio/${id}.mp3`]).toString());
  timing[id] = { duration, words };
}
await writeFile(HERE + 'audio/timing.json', JSON.stringify(timing, null, 1));
