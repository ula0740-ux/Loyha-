// f3, f5 dagi gap oxiridagi ADM noto'g'ri chiqdi (foydalanuvchi, 2026-10-23). Audio boshidagi kabi bir xil bo'lishi uchun
// ADM bu yerda ham "A di em Jizzakh" shaklida (Jizzax so'zidan oldin) yoziladi: "Bo'shashmaymiz, ADM Jizzax!", "Olg'a, ADM Jizzax!".
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { readFile, writeFile } from 'node:fs/promises';
const B = '/home/user/Loyha-/audio/badantarbiya/', O = B + 'laura/', V = 'FGY2WhTYpPnrIDTdsKH5';
const VS = { stability: .3, similarity_boost: .75, style: .7, use_speaker_boost: true };
const L: { id: string; text: string }[] = JSON.parse(await readFile(B + 'qiz_ovozi/narration.json', 'utf8')).lines;
const man = JSON.parse(await readFile(O + 'manifest.json', 'utf8'));
for (const id of ['f3', 'f5']) {
  const n = L.findIndex((l) => l.id === id), text = L[n].text.replace(/ADM!$/, 'ADM Jizzax!');
  const t = '[excited] ' + prepareUzbek(text, 'latin').tts.replace(/A-de-em,? ?(?=Jizzakh)/g, 'A di em ').replace(/A-de-em/g, 'A di em')
    .replace('Hammaga', 'Ham-maga').replace('Khavfsizlik qoidalariga rioya', 'Khavf-sizlik qoi-dalariga ri-oya');
  const ctx = { previousText: prepareUzbek(L[n - 1].text, 'latin').tts, nextText: L[n + 1] && prepareUzbek(L[n + 1].text, 'latin').tts };
  console.log(id, '→', t);
  let best: any = null;
  for (let k = 0; k < 6; k++) {
    const s = await synth(t, { voice: V, model: 'eleven_v4', voiceSettings: VS, ...ctx });
    const h = await transcribe(s.mp3), sc = score(spokenReference(text), h), ok = /\bADM\b,? ?jizza/i.test(h);
    console.log(`  #${k + 1}: STT ${(sc.similarity * 100).toFixed(1)}% "ADM Jizzax":${ok ? 'ok' : "yo'q"} | ${h}`);
    const rank = sc.similarity + (ok ? 1 : 0); if (!best || rank > best.rank) best = { s, rank, sim: sc.similarity, ok };
    if (ok && sc.similarity >= .97) break;
  }
  await writeFile(O + `lines/${id}.mp3`, best.s.mp3); man.lines[id] = { sim: +best.sim.toFixed(3), adm: best.ok, text };
  console.log(`✓ ${id}`);
}
await writeFile(O + 'manifest.json', JSON.stringify(man, null, 1));
