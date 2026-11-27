// "CKD NEV" -> "Si-Ke-Di New energy vehicle" (English, the user's explicit choice). 4 labelled variants of the c_nev line.
// run from studio/: ELEVENLABS_API_KEY=... npx tsx ../video/adm-profile/build/variants_nev.mts
import '../../../studio/server/net.ts';
import { prepareUzbek } from '../../../studio/server/uz/prepare.ts';
import { synth } from '../../../studio/server/uz/eleven.ts';
import { writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const OUT = fileURLToPath(new URL('../audio/variants5/', import.meta.url));
const API = 'https://api.elevenlabs.io', KEY = process.env.ELEVENLABS_API_KEY || 'proxy-injected', VOICE = 'EXAVITQu4vr4xnSDxMaL';
const PREV = prepareUzbek('Shtamplash sexi: investitsiya 55 million dollar, 150 ish oʻrni.', 'latin').tts.replace(/sekh/g, 'tsekh');
const NEXT = prepareUzbek('Ilmiy-tadqiqot markazi: investitsiya 100 million dollar, 500 muhandis.', 'latin').tts;
const TAIL = prepareUzbek('investitsiya 100 million dollar, 1 200 ish oʻrni.', 'latin').tts.replace(/^I/, 'i');
async function tts(text: string, lang: string | null) {   // raw call so the language can be English for one chunk
  const body: Record<string, unknown> = { text, model_id: 'eleven_v4', seed: 7, previous_text: PREV, next_text: NEXT };
  if (lang) body.language_code = lang;
  const r = await fetch(`${API}/v1/text-to-speech/${VOICE}?output_format=mp3_44100_128`, { method: 'POST', headers: { 'xi-api-key': KEY, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`TTS ${r.status} ${(await r.text()).slice(0, 150)}`);
  return Buffer.from(await r.arrayBuffer());
}
async function stt(mp3: Buffer, lang: string) {
  const fd = new FormData(); fd.append('model_id', 'scribe_v1'); fd.append('language_code', lang);
  fd.append('file', new Blob([new Uint8Array(mp3)], { type: 'audio/mpeg' }), 'a.mp3');
  const r = await fetch(`${API}/v1/speech-to-text`, { method: 'POST', headers: { 'xi-api-key': KEY }, body: fd });
  return ((await r.json()) as { text: string }).text;
}
const trim = (inF: string, outF: string) => execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', inF, '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse', '-ar', '44100', '-ac', '1', outF]);
const sil = (d: number, f: string) => execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', String(d), f]);
const cat = (files: string[], out: string) => { const a = ['-v', 'error', '-y']; files.forEach((f) => a.push('-i', f));
  a.push('-filter_complex', files.map((_, i) => `[${i}:a]aresample=44100,aformat=channel_layouts=mono[a${i}]`).join(';') + ';' + files.map((_, i) => `[a${i}]`).join('') + `concat=n=${files.length}:v=0:a=1[o]`, '-map', '[o]', '-b:a', '160k', out); execFileSync('ffmpeg', a); };

const V: { name: string; make: () => Promise<Buffer>; how: string }[] = [
  { name: 'NEV_1', how: 'butun jumla uz, inglizcha soʻzlar oddiy matn', make: () => tts(`Yangi loyihalar. Si-Ke-Di New energy vehicle: ${TAIL}`, 'uz') },
  { name: 'NEV_2', how: 'butun jumla uz, inglizcha qism qoʻshtirnoq va vergullar ichida', make: () => tts(`Yangi loyihalar. Si-Ke-Di, "New energy vehicle", ${TAIL}`, 'uz') },
  { name: 'NEV_3', how: 'uch boʻlak: uz + inglizcha boʻlak (language_code en) + uz, pauzada ulangan', make: async () => {
      const a = await tts('Yangi loyihalar. Si-Ke-Di,', 'uz'), b = await tts('New energy vehicle.', 'en'), c = await tts(prepareUzbek('Investitsiya 100 million dollar, 1 200 ish oʻrni.', 'latin').tts, 'uz');
      const fs = ['a', 'b', 'c'].map((k) => OUT + `_${k}.mp3`); await writeFile(fs[0], a); await writeFile(fs[1], b); await writeFile(fs[2], c);
      const ts = fs.map((f) => f.replace('.mp3', '_t.wav')); fs.forEach((f, i) => trim(f, ts[i])); sil(.12, OUT + '_s1.wav'); sil(.28, OUT + '_s2.wav');
      cat([ts[0], OUT + '_s1.wav', ts[1], OUT + '_s2.wav', ts[2]], OUT + '_v3.mp3'); return (await import('node:fs/promises')).readFile(OUT + '_v3.mp3'); } },
  { name: 'NEV_4', how: 'oʻzbekcha talaffuz yozuvi "Nyu enerji vikl" (oxirgi chora)', make: () => tts(`Yangi loyihalar. Si-Ke-Di Nyu enerji vikl: ${TAIL}`, 'uz') },
];
const LABELS = ['Birinchi variant.', 'Ikkinchi variant.', 'Uchinchi variant.', 'Toʻrtinchi variant.'];
sil(.6, OUT + '_sil.wav'); const list: string[] = [];
for (let i = 0; i < V.length; i++) {
  const mp3 = await V[i].make(); const f = OUT + V[i].name + '.mp3'; await writeFile(f, mp3);
  const lab = await synth(LABELS[i], { model: 'eleven_v4', seed: 7 }); await writeFile(OUT + `_l${i}.mp3`, lab.mp3);
  console.log(`${V[i].name} (${V[i].how})\n  STT uz: ${await stt(mp3, 'uzb')}\n  STT en: ${await stt(mp3, 'eng')}`);
  list.push(OUT + `_l${i}.mp3`, OUT + '_sil.wav', f, OUT + '_sil.wav', OUT + '_sil.wav');
}
cat(list, OUT + 'CKD_NEV_variantlar.mp3');
execFileSync('sh', ['-c', `rm -f "${OUT}"_*`]);
console.log('->', OUT + 'CKD_NEV_variantlar.mp3');
