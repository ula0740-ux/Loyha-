// v7: K takes of the Jizzakh lines exactly as narrate.mts would speak them (same text, context and overrides)
// -> OUT/<id>_<k>.mp3 + .json; build/jz_pick.py picks by closeness to the approved "A-de-em, Jizzakh!".
// run from studio/: ELEVENLABS_API_KEY=proxy-injected OUT=dir K=6 npx tsx ../video/adm-profile/build/jz_takes.mts title h2020 cl0 dost1
import '../../../studio/server/net.ts';
import { prepareUzbek } from '../../../studio/server/uz/prepare.ts';
import { synth } from '../../../studio/server/uz/eleven.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const HERE = fileURLToPath(new URL('../', import.meta.url));
const OUT = (process.env.OUT || '/tmp/jz_takes') + '/'; await mkdir(OUT, { recursive: true });
const cfg = JSON.parse(await readFile(HERE + 'narration.json', 'utf8'));
const plain = (t: string) => t.replace(/[{}]/g, '');
const tsekh = (t: string) => t.replace(/(^|[^\p{L}ʻʼ'])([Ss])ekh/gu, (_m, pre, s) => pre + (s === 'S' ? 'Tsekh' : 'tsekh'));
const adeem = (t: string) => t.replace(/A-de-em,?\s*/g, 'A-De-Em ');
const reno = (t: string) => t.replace(/Renault/g, 'Renolt');
const spokenFor = (id: string) => (t: string) => reno(id === 'title' ? tsekh(t) : adeem(tsekh(t)));
const K = Number(process.env.K || 6);
for (const id of process.argv.slice(2)) {
  const i = cfg.lines.findIndex((l: { id: string }) => l.id === id), sp = spokenFor(id), sc = spokenFor('');
  const text = sp(prepareUzbek(plain(cfg.lines[i].text), 'latin').tts);
  const ctx = { previousText: cfg.lines[i - 1] && sc(prepareUzbek(plain(cfg.lines[i - 1].text), 'latin').tts), nextText: cfg.lines[i + 1] && sc(prepareUzbek(plain(cfg.lines[i + 1].text), 'latin').tts) };
  console.log(id, text);
  for (let k = 0; k < K; k++) {
    const s = await synth(text, { voice: cfg.voice, model: cfg.model, seed: 41 + k, ...ctx });
    await writeFile(`${OUT}${id}_${k}.mp3`, s.mp3); await writeFile(`${OUT}${id}_${k}.json`, JSON.stringify({ text, words: s.words }));
  }
}
