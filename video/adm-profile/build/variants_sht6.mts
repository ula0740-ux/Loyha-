// v4: "Shtamplash sexi" (the user heard it wrong in v3). Labelled candidates of the c_sht opening -> audio/variants6/SHT6_*.
// "sex" stays spoken "tsekh…" (the user's approved choice); only the take and the syllable break of "Shtamplash" vary.
// run from studio/: ELEVENLABS_API_KEY=proxy-injected npx tsx ../video/adm-profile/build/variants_sht6.mts
import '../../../studio/server/net.ts';
import { prepareUzbek } from '../../../studio/server/uz/prepare.ts';
import { synth } from '../../../studio/server/uz/eleven.ts';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const OUT = fileURLToPath(new URL('../audio/variants6/', import.meta.url));
const API = 'https://api.elevenlabs.io', KEY = process.env.ELEVENLABS_API_KEY || 'proxy-injected';
const ts = (s: string) => prepareUzbek(s, 'latin').tts.replace(/(^|[^\p{L}])([Ss])ekh/gu, (_m, p, s) => p + (s === 'S' ? 'Tsekh' : 'tsekh'));
const PREV = ts('Lokalizatsiya klasteri: investitsiya 150 million dollar, 350 ish oʻrni.');
const NEXT = ts('Yangi loyihalar. CKD, investitsiya 100 million dollar, 1 200 ish oʻrni.');
const RAW = (x: string) => prepareUzbek(x, 'latin').tts;
const BODY = ts('Shtamplash sexi: investitsiya 55 million dollar, 150 ish oʻrni. Bu sex kuzov panellarini ishlab chiqaradi.');
async function stt(mp3: Buffer, lang: string) {
  const fd = new FormData(); fd.append('model_id', 'scribe_v1'); fd.append('language_code', lang);
  fd.append('file', new Blob([new Uint8Array(mp3)], { type: 'audio/mpeg' }), 'a.mp3');
  const r = await fetch(`${API}/v1/speech-to-text`, { method: 'POST', headers: { 'xi-api-key': KEY }, body: fd });
  return ((await r.json()) as { text: string }).text;
}
const ALL = [['SHT6_A', BODY, 'tasdiqlangan shakl, yangi take'], ['SHT6_B', BODY.replace('Shtamplash', 'Shtamp-lash'), 'boʻgʻin chizigʻi: Shtamp-lash'],
  ['SHT6_C', RAW('Shtamplash sexi: investitsiya 55 million dollar, 150 ish oʻrni. Bu sex kuzov panellarini ishlab chiqaradi.'), 'oʻzbekcha sex -> sekh (tsekh emas)']];
const V = ALL.filter(([n]) => !process.env.ONLY || process.env.ONLY.split(',').includes(n));
const notes: string[] = [];
for (const [name, text, how] of V) for (const k of [1, 2]) {
  const s = await synth(text, { model: 'eleven_v4', previousText: PREV, nextText: NEXT });
  await writeFile(`${OUT}${name}_${k}.mp3`, s.mp3);
  const line = `${name}_${k} [${how}] tts="${text}"\n  STT uz: ${await stt(s.mp3, 'uzb')}\n  STT ru: ${await stt(s.mp3, 'rus')}`;
  console.log(line); notes.push(line);
}
await writeFile(OUT + 'stt_sht.txt', notes.join('\n') + '\n', { flag: 'a' });
