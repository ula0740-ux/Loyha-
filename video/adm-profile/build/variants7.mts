// v5 phase 1 (2026-11-27): the user rejected both "Ey-di-em" (v4) and "A-de-em" for ADM, and says "investitsiya" is
// mispronounced. Labelled candidates, one take each (seed 7), in the film's own sentences:
//   T*  title line  "ADM Jizzax, koʻp brendli …"        (ADM at the very start)
//   M*  h2020 line  "2020-yilda ADM Jizzax avtozavodi …" (ADM mid-sentence)
//   I*  c_kia line  "Kia CKD loyihasi: investitsiya …"
// Each take: STT (scribe_v1) of the whole take (uz) + of the cut word span (uz, ru, en) by the TTS alignment.
// Writes <OUT>/<id>.mp3 and <OUT>/stt.json. Pick the distinct ones afterwards (audio/variants7/izoh.txt).
// run from studio/: ELEVENLABS_API_KEY=proxy-injected OUT=/some/dir npx tsx ../video/adm-profile/build/variants7.mts [ids…]
import '../../../studio/server/net.ts';
import { prepareUzbek, spokenReference } from '../../../studio/server/uz/prepare.ts';
import { synth, score } from '../../../studio/server/uz/eleven.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = fileURLToPath(new URL('../', import.meta.url));
const OUT = (process.env.OUT || HERE + 'audio/variants7/pool') + '/';
await mkdir(OUT, { recursive: true });
const API = 'https://api.elevenlabs.io', KEY = process.env.ELEVENLABS_API_KEY || 'proxy-injected', VOICE = 'EXAVITQu4vr4xnSDxMaL';
const cfg = JSON.parse(await readFile(HERE + 'narration.json', 'utf8'));
const L = (id: string) => cfg.lines.findIndex((l: { id: string }) => l.id === id);
const tsekh = (t: string) => t.replace(/(^|[^\p{L}ʻʼ'])([Ss])ekh/gu, (_m, pre, s) => pre + (s === 'S' ? 'Tsekh' : 'tsekh'));
const prep = (t: string) => tsekh(prepareUzbek(t.replace(/[{}]/g, ''), 'latin').tts);
async function stt(mp3: Buffer, lang: string) {
  const fd = new FormData(); fd.append('model_id', 'scribe_v1'); fd.append('language_code', lang);
  fd.append('file', new Blob([new Uint8Array(mp3)], { type: 'audio/mpeg' }), 'a.mp3');
  const r = await fetch(`${API}/v1/speech-to-text`, { method: 'POST', headers: { 'xi-api-key': KEY }, body: fd });
  return ((await r.json()) as { text: string }).text;
}
// ADM spoken forms (replace prepareUzbek's "A-de-em," also in the context sentences, so context and line agree)
const ADM: Record<string, [string, string]> = {
  A: ['A. De. Em. ', 'oʻzbekcha harf nomlari, har biri nuqta bilan (badantarbiya audiosida foydalanuvchi tanlagan shakl)'],
  B: ['A, De, Em, ', 'oʻzbekcha harf nomlari, vergul bilan (sekinroq, har harf aniq)'],
  C: ['A-De-Em ', 'oʻzbekcha harf nomlari, chiziqcha, pauzasiz Jizzakh ga ulanadi'],
  D: ['Adm ', 'bitta soʻz qilib, oʻzbekcha oʻqilishi'],
  E: ['Ey. Di. Em. ', 'inglizcha harf nomlari, har biri alohida nuqta bilan'],
  F: ['Ei-Di-Em, ', 'inglizcha harf nomlari, boshqa imlo (Ei), keyin qisqa pauza'],
};
const INV: Record<string, [string, string]> = {
  A: ['investitsiya', 'oddiy yozuv (v4 dagi kabi), nazorat uchun yangi take'],
  B: ['in-ves-ti-tsi-ya', 'boʻgʻinlarga ajratilgan, ts bir boʻgʻinda (tsi)'],
  C: ['in-ves-tit-si-ya', 'boʻgʻinlarga ajratilgan, oʻzbek imlo boʻgʻini (tit-si)'],
  D: ['investitsi-ya', 'oxirgi "ya" boʻgʻini ajratilgan (oxirgi boʻgʻin urgʻusi uchun)'],
  E: ['investi-tsiya', 'ikki boʻlak: investi + tsiya ("ts" aniq chiqishi uchun)'],
  F: ['investitsiya,', 'oddiy yozuv + vergul (soʻz oxiri yutilmasligi uchun qisqa pauza)'],
};
type Job = { id: string; line: string; how: string; form: string; sub: (t: string) => string; span: RegExp; spanLen: number };
const jobs: Job[] = [];
for (const [k, [form, how]] of Object.entries(ADM)) {
  const sub = (t: string) => t.replace(/A-de-em,?\s*/g, form);
  jobs.push({ id: `T${k}`, line: 'title', how, form, sub, span: /Jizz/i, spanLen: form.trim().split(/\s+/).length });
  jobs.push({ id: `M${k}`, line: 'h2020', how, form, sub, span: /Jizz/i, spanLen: form.trim().split(/\s+/).length });
}
for (const [k, [form, how]] of Object.entries(INV)) {
  const sub = (t: string) => t.replace(/investitsiya,?/g, form).replace(/Investitsiya,?/g, form.charAt(0).toUpperCase() + form.slice(1));
  jobs.push({ id: `I${k}`, line: 'c_kia', how, form, sub, span: /^in/i, spanLen: 0 });
}
const want = process.argv.slice(2);
const res: Record<string, unknown> = {};
try { Object.assign(res, JSON.parse(await readFile(OUT + 'stt.json', 'utf8'))); } catch { /* first run */ }
for (const j of jobs) {
  if (want.length && !want.includes(j.id)) continue;
  const i = L(j.line);
  const text = j.sub(prep(cfg.lines[i].text));
  const ctx = { previousText: cfg.lines[i - 1] && j.sub(prep(cfg.lines[i - 1].text)), nextText: cfg.lines[i + 1] && j.sub(prep(cfg.lines[i + 1].text)) };
  const s = await synth(text, { voice: VOICE, model: 'eleven_v4', seed: 7, ...ctx });
  const f = `${OUT}${j.id}.mp3`; await writeFile(f, s.mp3);
  const w = s.words;
  let a: number, b: number;
  if (j.spanLen) { const ji = w.findIndex((x) => j.span.test(x.text)); a = w[Math.max(0, ji - j.spanLen)].start; b = w[ji].end; }
  else { const ii = w.findIndex((x) => j.span.test(x.text)); a = w[ii].start; b = w[ii].end; }
  a = Math.max(0, a - .04); b = b + .06;
  const sp = `${OUT}${j.id}_span.mp3`;
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(a), '-to', String(b), '-i', f, '-c:a', 'libmp3lame', '-q:a', '2', sp]);
  const spb = await readFile(sp);
  const [full, su, sr, se] = await Promise.all([stt(s.mp3, 'uzb'), stt(spb, 'uzb'), stt(spb, 'rus'), stt(spb, 'eng')]);
  const sc = score(spokenReference(cfg.lines[i].text.replace(/[{}]/g, '')), full);
  res[j.id] = { line: j.line, form: j.form, how: j.how, tts: text, span: [+a.toFixed(2), +b.toFixed(2)], spanDur: +(b - a).toFixed(2), stt_full: full, similarity: +(sc.similarity * 100).toFixed(1), stt_span: { uz: su, ru: sr, en: se } };
  console.log(`${j.id} [${j.form.trim()}] ${(b - a).toFixed(2)}s | full ${(sc.similarity * 100).toFixed(1)}%: ${full}\n    span uz: ${su} | ru: ${sr} | en: ${se}`);
  await writeFile(OUT + 'stt.json', JSON.stringify(res, null, 1));
}
