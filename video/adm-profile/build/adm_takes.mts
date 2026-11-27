// v6: several takes of the ADM lines (same text/context as narrate.mts) -> OUT/<id>_<k>.mp3 + .json (TTS word times);
// build/adm_pick.py then keeps the take whose "ADM" is closest (MFCC-DTW) to the approved samples
// audio/variants7/ADM_JIZZAKH_2.mp3 / ADM_ICHIDA_2.mp3.
// run from studio/: ELEVENLABS_API_KEY=proxy-injected OUT=dir K=4 npx tsx ../video/adm-profile/build/adm_takes.mts cl0 eco outro
import '../../../studio/server/net.ts';
import { prepareUzbek } from '../../../studio/server/uz/prepare.ts';
import { synth } from '../../../studio/server/uz/eleven.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const HERE = fileURLToPath(new URL('../', import.meta.url));
const OUT = (process.env.OUT || '/tmp/adm_takes') + '/'; await mkdir(OUT, { recursive: true });
const cfg = JSON.parse(await readFile(HERE + 'narration.json', 'utf8'));
const plain = (t: string) => t.replace(/[{}]/g, '');
const tsekh = (t: string) => t.replace(/(^|[^\p{L}ʻʼ'])([Ss])ekh/gu, (_m, pre, s) => pre + (s === 'S' ? 'Tsekh' : 'tsekh'));
const spoken = (t: string) => tsekh(prepareUzbek(plain(t), 'latin').tts).replace(/A-de-em,?\s*/g, 'A-De-Em ');
const K = Number(process.env.K || 4);
for (const id of process.argv.slice(2)) {
  const i = cfg.lines.findIndex((l: { id: string }) => l.id === id);
  const ctx = { previousText: cfg.lines[i - 1] && spoken(cfg.lines[i - 1].text), nextText: cfg.lines[i + 1] && spoken(cfg.lines[i + 1].text) };
  for (let k = 0; k < K; k++) {
    const s = await synth(spoken(cfg.lines[i].text), { voice: cfg.voice, model: cfg.model, seed: 7 + k, ...ctx });
    await writeFile(`${OUT}${id}_${k}.mp3`, s.mp3); await writeFile(`${OUT}${id}_${k}.json`, JSON.stringify(s.words));
    console.log(id, k, s.words.slice(0, 3).map((w) => `${w.text} ${w.start.toFixed(2)}-${w.end.toFixed(2)}`).join(' | '));
  }
}
