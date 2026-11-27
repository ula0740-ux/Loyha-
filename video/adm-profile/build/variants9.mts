// v7 prep (2026-11-27): the user rejected every spelling trick for Jizzax's final x (variants8) and wants Renault in
// fully Uzbek pronunciation. Jizzakh now follows the pattern of the approved film video/pptx-film (ADM_HR_2026_v5:
// "A-de-em, Jizzakh!" — Jizzakh at a sentence end with "!", eleven_v4 + uz, Sarah, prepareUzbek context, no seed).
// Several takes per pattern -> OUT/<id>_<k>.mp3 + .json (TTS word times); build/jz_pick.py ranks them against the
// approved "Jizzakh" (MFCC-DTW) + ru STT of the cut word. Renault: three Uzbek spoken forms in the h2021 sentence.
// run from studio/: ELEVENLABS_API_KEY=proxy-injected OUT=dir K=6 npx tsx ../video/adm-profile/build/variants9.mts [ids]
import '../../../studio/server/net.ts';
import { prepareUzbek } from '../../../studio/server/uz/prepare.ts';
import { synth } from '../../../studio/server/uz/eleven.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const HERE = fileURLToPath(new URL('../', import.meta.url));
const OUT = (process.env.OUT || '/tmp/variants9') + '/'; await mkdir(OUT, { recursive: true });
const cfg = JSON.parse(await readFile(HERE + 'narration.json', 'utf8'));
const L = (id: string) => cfg.lines.findIndex((l: { id: string }) => l.id === id);
const tsekh = (t: string) => t.replace(/(^|[^\p{L}ʻʼ'])([Ss])ekh/gu, (_m, pre, s) => pre + (s === 'S' ? 'Tsekh' : 'tsekh'));
const base = (t: string) => tsekh(prepareUzbek(t.replace(/[{}]/g, ''), 'latin').tts).replace(/A-de-em,?\s*/g, 'A-De-Em ').replace(/Renault/g, 'Reno');
const K = Number(process.env.K || 6);
// [id, line, text override (written, goes through base) or null, extra spoken substitution, takes]
const JOBS: [string, string, string | null, (t: string) => string, number][] = [
  // title, same words, Jizzakh closes its own sentence with "!" (variant F of the approved film)
  ['B', 'title', 'ADM Jizzax. Koʻp brendli avtomobil ishlab chiqaruvchi kompaniya.', (t) => t.replace(/Jizzakh\./, 'Jizzakh!'), K],
  // h2020 as it is (mid-sentence Jizzakh): more takes, picked by closeness to the approved sound
  ['I', 'h2020', null, (t) => t, K],
  // restructured title (TEXT CHANGE, needs the user's consent): Jizzakh! then a word that does not start with k
  ['T', 'title', 'ADM Jizzax. Avtomobil ishlab chiqaruvchi koʻp brendli kompaniya.', (t) => t.replace(/Jizzakh\./, 'Jizzakh!'), 3],
  // Renault, Uzbek spoken forms (on-screen text stays "Renault")
  ['R1', 'h2021', null, (t) => t.replace(/Reno/, 'Renoʻ'), 1],
  ['R2', 'h2021', null, (t) => t.replace(/Reno/, 'Renolt'), 1],
  ['R3', 'h2021', null, (t) => t.replace(/Reno/, 'Re-na-ult'), 1],
];
const want = process.argv.slice(2);
for (const [id, lid, over, sub, n] of JOBS) {
  if (want.length && !want.includes(id)) continue;
  const i = L(lid), text = sub(base(over ?? cfg.lines[i].text));
  const ctx = { previousText: cfg.lines[i - 1] && base(cfg.lines[i - 1].text), nextText: cfg.lines[i + 1] && base(cfg.lines[i + 1].text) };
  for (let k = 0; k < n; k++) {
    const s = await synth(text, { voice: cfg.voice, model: cfg.model, seed: 31 + k, ...ctx });
    await writeFile(`${OUT}${id}_${k}.mp3`, s.mp3); await writeFile(`${OUT}${id}_${k}.json`, JSON.stringify({ text, words: s.words }));
    console.log(id, k, text.slice(0, 70));
  }
}
