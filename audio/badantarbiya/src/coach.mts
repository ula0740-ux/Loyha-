// Murabbiy uslubidagi ovoz (2026-10-23): barcha gaplar quvnoq, energiyali ohangda qayta yoziladi ([excited] + voice_settings),
// mashqlar uchun "Bir! Ikki! Uch! To'rt!" sanoq yozuvlari va yo'nalish almashish ishoralari tayyorlanadi.
// Har yozuv STT bilan tekshiriladi; ADM — foydalanuvchi tanlagan "A. De. Em." shaklida.
//   cd studio && npx tsx ../audio/badantarbiya/src/coach.mts
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score, normForCompare } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
const B = '/home/user/Loyha-/audio/badantarbiya/', O = B + 'murabbiy/', V = 'EXAVITQu4vr4xnSDxMaL';
const VS = { stability: .3, similarity_boost: .75, style: .6, use_speaker_boost: true };
const TAG = '[excited] ';
const L: { id: string; text: string }[] = JSON.parse(await readFile(B + 'qiz_ovozi/narration.json', 'utf8')).lines;
const TEXT: Record<string, string> = Object.fromEntries(L.map((l) => [l.id, l.text]));
TEXT.f0 = TEXT.f0.replace('xodimlari! ', 'xodimlari! Xayrli tong! ');
const tts = (t: string) => prepareUzbek(t, 'latin').tts.replace(/A-de-em,? ?(?=Jizzakh)/g, 'A. De. Em. ').replace(/A-de-em!/g, 'A. De. Em.!').replace(/A-de-em/g, 'A. De. Em.')
  .replace('Hammaga', 'Ham-maga').replace('Khavfsizlik qoidalariga rioya', 'Khavf-sizlik qoi-dalariga ri-oya');
const hasADM = (h: string) => /\bADM\b|АДМ|\bA,? ?D,? ?M\b/i.test(h);
await mkdir(O + 'lines', { recursive: true }); await mkdir(O + 'counts', { recursive: true }); await mkdir(O + 'cues', { recursive: true });
const only = process.env.ONLY?.split(',');
const man: any = JSON.parse(await readFile(O + 'manifest.json', 'utf8').catch(() => '{"lines":{},"counts":[],"cues":{}}'));
/* 1) gaplar */
for (let n = 0; n < L.length; n++) {
  const id = L[n].id; if (only && !only.includes(id)) continue;
  const text = TAG + tts(TEXT[id]), ctx = { previousText: L[n - 1] && prepareUzbek(TEXT[L[n - 1].id], 'latin').tts, nextText: L[n + 1] && prepareUzbek(TEXT[L[n + 1].id], 'latin').tts };
  let best: any = null;
  for (let k = 0; k < 5; k++) {
    const s = await synth(text, { voice: V, model: 'eleven_v4', voiceSettings: VS, ...ctx });
    const heard = await transcribe(s.mp3), sc = score(spokenReference(TEXT[id]), heard), adm = !/ADM/.test(TEXT[id]) || hasADM(heard);
    console.log(`${id} #${k + 1}: STT ${(sc.similarity * 100).toFixed(1)}% ADM:${adm ? 'ok' : "yo'q"} | ${heard}`);
    const rank = sc.similarity + (adm ? 1 : 0);
    if (!best || rank > best.rank) best = { s, rank, sim: sc.similarity, adm };
    if (adm && sc.similarity >= .97) break;
  }
  await writeFile(O + `lines/${id}.mp3`, best.s.mp3);
  man.lines[id] = { sim: +best.sim.toFixed(3), adm: best.adm };
  console.log(`✓ ${id} (${(best.sim * 100).toFixed(1)}%)`);
}
/* 2) sanoq: bir nechta yozuv — har to'plam boshqa yozuvdan, ohang bir xil bo'lib qolmasin */
if (!only || only.includes('counts')) {
  man.counts = [];
  for (let k = 0; k < 7 && man.counts.length < 5; k++) {
    const s = await synth(TAG + 'Bir! Ikki! Uch! Toʻrt!', { voice: V, model: 'eleven_v4', voiceSettings: VS });
    s.words = s.words.filter((w) => !w.text.startsWith('['));   // [excited] ishorasi so'z emas
    const heard = normForCompare(await transcribe(s.mp3)), ok = /bir ikki uch to.?rt/.test(heard) && s.words.length === 4;
    console.log(`count #${k + 1}: ${ok ? 'ok' : 'rad'} | ${heard} | ${s.words.map((w) => w.text + '@' + w.start.toFixed(2)).join(' ')}`);
    if (!ok) continue;
    const f = `counts/c${man.counts.length + 1}.mp3`; await writeFile(O + f, s.mp3); man.counts.push({ file: f, words: s.words });
  }
}
/* 3) yo'nalish almashish ishoralari */
if (!only || only.includes('cues')) {
  const CUES: [string, string, string][] = [['chapga', 'Endi chapga!', 'chap'], ['orqaga', 'Endi orqaga!', 'endi orqaga'], ['tashqariga', 'Endi tashqariga!', 'endi tashqariga']];
  for (const [key, text, ref] of CUES) {
    if (process.env.CUE && process.env.CUE !== key) continue;
    for (let k = 0; k < 5; k++) {
      const s = await synth(TAG + text, { voice: V, model: 'eleven_v4', voiceSettings: VS, previousText: 'Bir! Ikki! Uch! Toʻrt!' });
      s.words = s.words.filter((w) => !w.text.startsWith('['));
      const heard = normForCompare(await transcribe(s.mp3)), ok = heard.includes(ref);
      console.log(`cue ${key} #${k + 1}: ${ok ? 'ok' : 'rad'} | ${heard}`);
      if (ok) { await writeFile(O + `cues/${key}.mp3`, s.mp3); man.cues[key] = { file: `cues/${key}.mp3`, words: s.words }; break; }
    }
  }
}
await writeFile(O + 'manifest.json', JSON.stringify(man, null, 1));
console.log('tayyor');
