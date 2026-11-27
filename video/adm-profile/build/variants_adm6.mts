// v4: the opening "ADM Jizzax" modelled on the user's reference video (src/user_ref_adm.mp4), whose narrator says
// "ADM" as English letter names ("Ey-di-em", STT hears "EDM"/"80M"/"ADHD") straight into "Jizzakh" with no pause.
// Labelled candidates of the title line -> audio/variants6/; each take: STT (uz, en) + the "ADM Jizzakh" span cut by
// the TTS alignment (for the acoustic comparison in build/adm_match.py).
// run from studio/: ELEVENLABS_API_KEY=proxy-injected npx tsx ../video/adm-profile/build/variants_adm6.mts
import '../../../studio/server/net.ts';
import { prepareUzbek } from '../../../studio/server/uz/prepare.ts';
import { synth } from '../../../studio/server/uz/eleven.ts';
import { writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const OUT = fileURLToPath(new URL('../audio/variants6/', import.meta.url));
const API = 'https://api.elevenlabs.io', KEY = process.env.ELEVENLABS_API_KEY || 'proxy-injected', VOICE = 'EXAVITQu4vr4xnSDxMaL';
const full = prepareUzbek('ADM Jizzax, koʻp brendli avtomobil ishlab chiqaruvchi kompaniya.', 'latin').tts;
console.log('prepareUzbek:', full);
const REST = full.replace(/^.*?Jizzakh[,!.]?\s*/, '');
const NEXT = prepareUzbek('Kompaniyaga 2014-yilda asos solingan.', 'latin').tts;
async function stt(mp3: Buffer, lang: string) {
  const fd = new FormData(); fd.append('model_id', 'scribe_v1'); fd.append('language_code', lang);
  fd.append('file', new Blob([new Uint8Array(mp3)], { type: 'audio/mpeg' }), 'a.mp3');
  const r = await fetch(`${API}/v1/speech-to-text`, { method: 'POST', headers: { 'xi-api-key': KEY }, body: fd });
  return ((await r.json()) as { text: string }).text;
}
const V = [
  ['ADM6_A', 'Ey-di-em Jizzakh', 'namunadagidek: inglizcha harf nomlari, pauzasiz'],
  ['ADM6_B', 'Ey-Di-Em, Jizzakh', 'inglizcha harf nomlari, ADM dan keyin qisqa pauza (F uslubi)'],
  ['ADM6_C', 'Eydiem Jizzakh', 'inglizcha harf nomlari bitta soʻz boʻlib'],
  ['ADM6_D', 'A. De. Em. Jizzakh', 'oʻzbekcha harf nomlari alohida (lugʻat izohidagi muqobil)'],
];
const notes: string[] = [];
for (const [name, adm, how] of V) {
  for (const k of [1, 2]) {
    const text = `${adm}, ${REST}`;
    const s = await synth(text, { voice: VOICE, model: 'eleven_v4', nextText: NEXT });
    const f = `${OUT}${name}_${k}.mp3`; await writeFile(f, s.mp3);
    const ji = s.words.findIndex((w) => /Jizz/i.test(w.text));
    const a = Math.max(0, s.words[0].start - .03), b = s.words[ji].end + .03;
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(a), '-to', String(b), '-i', f, '-ac', '1', '-ar', '44100', `${OUT}${name}_${k}_span.wav`]);
    const line = `${name}_${k} [${how}] tts="${text}"  span ${a.toFixed(2)}-${b.toFixed(2)}s\n  STT uz: ${await stt(s.mp3, 'uzb')}\n  STT en: ${await stt(s.mp3, 'eng')}`;
    console.log(line); notes.push(line);
  }
}
await writeFile(OUT + 'stt.txt', notes.join('\n') + '\n');
