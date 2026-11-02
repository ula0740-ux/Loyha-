// ADM talaffuzi: "A. De. Em." — foydalanuvchi quloq bilan tanlagan 4-namuna (2026-10-22). f0, f3, f5 qayta yoziladi.
// Har jumla 6 martagacha yoziladi; STT >= 95% va STT da "ADM" chiqqan, f0 da "ADM Jizzax" orasidagi pauza eng kichik yozuv tanlanadi.
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { readFile, writeFile } from 'node:fs/promises';
const B = '/home/user/Loyha-/audio/badantarbiya/qiz_ovozi/', V = 'EXAVITQu4vr4xnSDxMaL';
const L: { id: string; text: string }[] = JSON.parse(await readFile(B + 'narration.json', 'utf8')).lines;
const tts = (t: string) => prepareUzbek(t, 'latin').tts.replace(/A-de-em,? ?(?=Jizzakh)/g, 'A. De. Em. ').replace(/A-de-em!/g, 'A. De. Em.!').replace(/A-de-em/g, 'A. De. Em.')
  .replace('Hammaga', 'Ham-maga').replace('Khavfsizlik qoidalariga rioya', 'Khavf-sizlik qoi-dalariga ri-oya');
const only = (process.env.ONLY ?? 'f0,f3,f5').split(',');
for (const id of only) {
  const n = L.findIndex((l) => l.id === id), text = tts(L[n].text);
  const ctx = { previousText: L[n - 1] && prepareUzbek(L[n - 1].text, 'latin').tts, nextText: L[n + 1] && prepareUzbek(L[n + 1].text, 'latin').tts };
  console.log(id, '→', text);
  let best: any = null;
  for (let k = 0; k < 6; k++) {
    const s = await synth(text, { voice: V, model: 'eleven_v4', ...ctx });
    const tr = await transcribe(s.mp3), sc = score(spokenReference(L[n].text), tr);
    const heard = typeof tr === 'string' ? tr : (tr as any).text, adm = /\bADM\b|АДМ|\bA,? ?D,? ?M\b/i.test(heard);
    const i = s.words.findIndex((w) => w.text.startsWith('Em')), j = s.words.findIndex((w, m) => m > i && w.text.startsWith('Jizzakh'));
    const gap = i >= 0 && j > i ? s.words[j].start - s.words[i].end : 0;
    console.log(`  #${k + 1}: STT ${(sc.similarity * 100).toFixed(1)}%  ADM:${adm ? 'ha' : "yo'q"}  pauza ${gap.toFixed(2)}s  | ${heard}`);
    const ok = sc.similarity >= 0.95 && adm, rank = (ok ? 0 : 10) + gap - sc.similarity;
    if (!best || rank < best.rank) best = { s, rank, ok };
    if (ok && gap < 0.12) break;
  }
  await writeFile(B + 'audio/' + id + '.mp3', best.s.mp3);
  console.log(`✓ ${id} saqlandi${best.ok ? '' : " (ogohlantirish: talab to'liq bajarilmadi)"}`);
}
