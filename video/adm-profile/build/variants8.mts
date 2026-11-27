// v6 feedback (2026-11-27): "JIZZAKH is pronounced JIZZAQ". Labelled spoken forms of Jizzax's final throat x in the
// title (T*) and in h2020 (M*); ADM stays "A-De-Em" (approved variant 2). One take each (seed 7); STT of the whole take
// (uz) and of the cut word (uz, ru, en: ru "Джиззах" = x heard, "Джизак" = k heard).
// run from studio/: ELEVENLABS_API_KEY=proxy-injected OUT=dir npx tsx ../video/adm-profile/build/variants8.mts [ids…]
import '../../../studio/server/net.ts';
import { prepareUzbek, spokenReference } from '../../../studio/server/uz/prepare.ts';
import { synth, score } from '../../../studio/server/uz/eleven.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = fileURLToPath(new URL('../', import.meta.url));
const OUT = (process.env.OUT || HERE + 'audio/variants8/pool') + '/';
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
const adeem = (t: string) => t.replace(/A-de-em,?\s*/g, 'A-De-Em ');
// [form for "Jizzakh<punct>", how]; the title form A turns the comma after Jizzax into a sentence end ("!", variant F)
const JZ: Record<string, [string, string, string]> = {
  A: ['Jizzakh!', 'Jizzakh,', 'kh + undov belgisi (F varianti): sarlavhada jumla "Jizzakh!" bilan tugaydi, gap ichida vergul (pauza)'],
  B: ['Jizzax,', 'Jizzax', 'oddiy oʻzbekcha x (kh ga aylantirilmagan), language_code uz'],
  C: ['Jizzakhh,', 'Jizzakhh', 'uzaytirilgan kh (khh) — faqat shu film uchun ogʻzaki shakl'],
  D: ['Jiz-zakh,', 'Jiz-zakh', 'boʻgʻin chizigʻi bilan (lugʻatda sinalgan "Jiz-zax" shakli), kh'],
  E: ['Jizzakh —', 'Jizzakh —', 'kh + tire (soʻzdan keyin uzunroq pauza, oxirgi tovush yutilmasligi uchun)'],
  F: ['Jizzaakh,', 'Jizzaakh', 'choʻzilgan a + kh (urgʻu oxirgi boʻgʻinda) — faqat shu film uchun ogʻzaki shakl'],
  G: ['Jizzach,', 'Jizzach', 'nemischa ch (Bach) imlosi — faqat shu film uchun ogʻzaki shakl'],
  H: ['Jizzah,', 'Jizzah', 'h bilan — FAQAT taqqoslash uchun (x va h almashtirilmaydi qoidasi)'],
  I: ['Jizzakhkh,', 'Jizzakhkh', 'ikki marta kh (kuchaytirilgan boʻgʻiz tovushi) — faqat shu film uchun'],
  J: ['Jizzax!', 'Jizzax,', 'oddiy x + undov belgisi'],
  K: ['Djizzakh,', 'Djizzakh', 'Dj + kh (ruscha "Джиззах" yozilishiga yaqin) — faqat shu film uchun'],
};
type Job = { id: string; line: string; how: string; form: string; sub: (t: string) => string };
const jobs: Job[] = [];
for (const [k, [ft, fm, how]] of Object.entries(JZ)) {
  jobs.push({ id: `T${k}`, line: 'title', how, form: ft, sub: (t) => { let x = adeem(t).replace(/Jizzakh,/, ft); if (ft.endsWith('!')) x = x.replace(/! koʻp/, '! Koʻp'); return x; } });
  jobs.push({ id: `M${k}`, line: 'h2020', how, form: fm, sub: (t) => adeem(t).replace(/Jizzakh(?= avtozavodi)/, fm) });
}
// Renault (the user's correction of "Ravon", 2026-11-27): spoken "Reno" — h2021 sentence; R* jobs keep Jizzakh as is
for (const [k, form, how] of [['1', 'Reno', 'fransuzcha talaffuz: Reno'], ['2', 'Re-no', 'boʻgʻinli: Re-no (urgʻu aniqroq)']] as const)
  jobs.push({ id: `R${k}`, line: 'h2021', how, form, sub: (t) => adeem(t).replace(/Renault/g, form) });
const want = process.argv.slice(2);
const res: Record<string, unknown> = {};
try { Object.assign(res, JSON.parse(await readFile(OUT + 'stt.json', 'utf8'))); } catch { /* first run */ }
for (const j of jobs) {
  if (want.length && !want.includes(j.id)) continue;
  const i = L(j.line);
  const text = j.sub(prep(cfg.lines[i].text));
  const ctx = { previousText: cfg.lines[i - 1] && j.sub(prep(cfg.lines[i - 1].text)), nextText: cfg.lines[i + 1] && j.sub(prep(cfg.lines[i + 1].text)) };
  const s = await synth(text, { voice: VOICE, model: 'eleven_v4', seed: Number(process.env.SEED || 7), ...ctx });
  const f = `${OUT}${j.id}.mp3`; await writeFile(f, s.mp3);
  const w = s.words;
  let a: number, b: number;
  const ii = w.findIndex((x) => (j.id[0] === 'R' ? /^re-?no/i : /^d?jiz/i).test(x.text)); a = Math.max(0, w[ii].start - .04); b = w[ii].end + .12;
  const sp = `${OUT}${j.id}_span.mp3`;
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(a), '-to', String(b), '-i', f, '-c:a', 'libmp3lame', '-q:a', '2', sp]);
  const spb = await readFile(sp);
  const [full, su, sr, se] = await Promise.all([stt(s.mp3, 'uzb'), stt(spb, 'uzb'), stt(spb, 'rus'), stt(spb, 'eng')]);
  const sc = score(spokenReference(cfg.lines[i].text.replace(/[{}]/g, '')), full);
  res[j.id] = { line: j.line, form: j.form, how: j.how, tts: text, span: [+a.toFixed(2), +b.toFixed(2)], spanDur: +(b - a).toFixed(2), stt_full: full, similarity: +(sc.similarity * 100).toFixed(1), stt_span: { uz: su, ru: sr, en: se } };
  console.log(`${j.id} [${j.form.trim()}] ${(b - a).toFixed(2)}s | full ${(sc.similarity * 100).toFixed(1)}%: ${full}\n    span uz: ${su} | ru: ${sr} | en: ${se}`);
  await writeFile(OUT + 'stt.json', JSON.stringify(res, null, 1));
}
