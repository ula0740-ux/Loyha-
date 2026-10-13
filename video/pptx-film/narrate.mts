// ElevenLabs narration with character timestamps -> audio/<id>.mp3 + audio/timing.json (word start/end per line).
// run from studio/: npx tsx ../video/pptx-film/narrate.mts   (needs ELEVENLABS_API_KEY)
import '../../studio/server/net.ts';
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
  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}/with-timestamps?output_format=mp3_44100_128`, {
    method: 'POST',
    headers: { 'xi-api-key': process.env.ELEVENLABS_API_KEY!, 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: line.text, model_id: cfg.model }),
  });
  if (!res.ok) throw new Error(`${line.id}: HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
  const j = (await res.json()) as { audio_base64: string; alignment: { characters: string[]; character_start_times_seconds: number[]; character_end_times_seconds: number[] } };
  const mp3 = `${HERE}audio/${line.id}.mp3`;
  await writeFile(mp3, Buffer.from(j.audio_base64, 'base64'));
  const words: { text: string; start: number; end: number }[] = [];
  let cur: { text: string; start: number; end: number } | null = null;
  const a = j.alignment;
  a.characters.forEach((c, i) => {
    if (/\s/.test(c)) { if (cur) words.push(cur); cur = null; return; }
    if (!cur) cur = { text: '', start: a.character_start_times_seconds[i], end: 0 };
    cur.text += c;
    cur.end = a.character_end_times_seconds[i];
  });
  if (cur) words.push(cur);
  const { stdout } = await run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]);
  timing[line.id] = { duration: Number(stdout), words };
  console.log(`✓ ${line.id} ${Number(stdout).toFixed(2)}s  ${words.length} soʻz`);
}
await writeFile(HERE + 'audio/timing.json', JSON.stringify(timing, null, 1));
