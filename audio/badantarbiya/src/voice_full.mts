// Butun badantarbiya audiosi uchun barcha yozuvlar tanlangan ovozda (2026-10-27: foydalanuvchi 8-namuna — Freya).
// Matn Laura variantidagi bilan so'zma-so'z bir xil. Har yozuv STT bilan tekshiriladi; eng yaxshisi olinadi.
//   VDIR=freya VOICE=jsCqWAovK2LkecY7zXl4 npx tsx ../audio/badantarbiya/src/voice_full.mts   (ONLY=f0,f3a,... ixtiyoriy)
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score, normForCompare } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { readFile, writeFile } from 'node:fs/promises';
/* server band (429/5xx) bo'lsa kutib qayta urinish */
async function retry<T>(f: () => Promise<T>): Promise<T> {
  for (let i = 0; ; i++) { try { return await f(); } catch (e: any) { if (i >= 6 || !/ (429|5\d\d)/.test(String(e.message))) throw e; console.log('  server band, kutilmoqda', 10 * (i + 1), 's'); await new Promise((r) => setTimeout(r, 10000 * (i + 1))); } }
}
const B = '/home/user/Loyha-/audio/badantarbiya/', O = B + (process.env.VDIR || 'freya') + '/', V = process.env.VOICE || 'jsCqWAovK2LkecY7zXl4';
const VS = { stability: .3, similarity_boost: .75, style: .7, use_speaker_boost: true }, TAG = '[excited] ';
const L: { id: string; text: string }[] = JSON.parse(await readFile(B + 'qiz_ovozi/narration.json', 'utf8')).lines;
const T: Record<string, string> = Object.fromEntries(L.map((l) => [l.id, l.text]));
T.f0 = T.f0.replace('xodimlari! ', 'xodimlari! Xayrli tong! ');
// f3 ikki qism: ko'rsatma + "Bo'shashmaymiz, ADM Jizzax xodimlari!" (oxiridagi ADM keyin f0 bo'lagi bilan almashtiriladi)
T.f3a = 'Bizda keyingi mashqimiz: oyoqlarimiz yelka kengligida, qoʻllarimiz esa ikki yonga yoygan holatda. Oʻng va chap tomonga qayrilib olamiz.';
T.f3b = 'Boʻshashmaymiz, ADM Jizzax xodimlari!';
delete T.f3;
const ORDER = ['f0', 'm0', 'm1', 'f1', 'm2', 'm3', 'f2', 'm4', 'm5', 'f3a', 'f3b', 'm6', 'm7', 'f4', 'f5'];
const tts = (t: string) => prepareUzbek(t, 'latin').tts.replace(/A-de-em,? ?(?=Jizzakh)/g, 'A di em ').replace(/A-de-em/g, 'A di em')
  .replace('Hammaga', 'Ham-maga').replace('Khavfsizlik qoidalariga rioya', 'Khavf-sizlik qoi-dalariga ri-oya');
const hasADM = (h: string) => /\bADM\b|АДМ|\bA,? ?D,? ?M\b/i.test(h);
const only = process.env.ONLY?.split(',');
const man: any = JSON.parse(await readFile(O + 'manifest.json', 'utf8').catch(() => '{"lines":{}}'));
for (let n = 0; n < ORDER.length; n++) {
  const id = ORDER[n]; if (only && !only.includes(id)) continue;
  const ctx = { previousText: n ? prepareUzbek(T[ORDER[n - 1]], 'latin').tts : undefined, nextText: ORDER[n + 1] ? prepareUzbek(T[ORDER[n + 1]], 'latin').tts : undefined };
  let best: any = null;
  for (let k = 0; k < +(process.env.TRIES || 6); k++) {
    const s = await retry(() => synth(TAG + tts(T[id]), { voice: V, model: 'eleven_v4', voiceSettings: VS, ...ctx }));
    const h = await retry(() => transcribe(s.mp3)), sc = score(spokenReference(T[id]), h), adm = !/ADM/.test(T[id]) || hasADM(h);
    console.log(`${id} #${k + 1}: ${(sc.similarity * 100).toFixed(1)}% ADM:${adm ? 'ok' : "yo'q"} | ${h}`);
    const rank = sc.similarity + (adm ? 1 : 0); if (!best || rank > best.rank) best = { s, rank, sim: sc.similarity, adm, h };
    if (adm && sc.similarity >= +(process.env.MIN || .985)) break;
  }
  await writeFile(O + `lines/${id}.mp3`, best.s.mp3); man.lines[id] = { sim: +best.sim.toFixed(3), adm: best.adm, heard: best.h };
  console.log(`✓ ${id} ${(best.sim * 100).toFixed(1)}%${best.adm ? '' : ' ⚠ ADM'}`);
  await writeFile(O + 'manifest.json', JSON.stringify(man, null, 1));
}
/* sanoqlar: yugurish — tabiiy ("Bir, ikki, ..."), bel — sekin ("Bir. Ikki. ...") */
const CNT: [string, string][] = [['tabiiy', 'Bir, ikki, uch, toʻrt! Bir, ikki, uch, toʻrt! Qani-qani, boʻshashmaymiz!'], ['sekin', 'Bir. Ikki. Uch. Toʻrt. Bir. Ikki. Uch. Toʻrt. Qani-qani, boʻshashmaymiz!']];
for (const [k, t] of CNT) {
  if (only && !only.includes(k)) continue;
  let best: any = null;
  for (let r = 0; r < 6; r++) {
    const s = await retry(() => synth(TAG + t, { voice: V, model: 'eleven_v4', voiceSettings: VS }));
    const w = s.words.filter((x) => !x.text.startsWith('[')), h = normForCompare(await retry(() => transcribe(s.mp3)));
    const ok = w.length === 10 && /bir ikki uch to.?rt bir ikki uch to.?rt qan/.test(h) && /bo.?shashmaymiz/.test(h);
    const st = w.slice(0, 8).map((x) => x.start), d = st.slice(1).map((x, i) => x - st[i]), m = d.reduce((a, b) => a + b, 0) / d.length;
    const sd = Math.sqrt(d.reduce((a, b) => a + (b - m) ** 2, 0) / d.length);
    console.log(`${k} #${r + 1}: ${ok ? 'ok' : 'rad'} oraliq ${m.toFixed(2)}±${sd.toFixed(2)} | ${h}`);
    if (ok && (!best || sd < best.sd)) best = { s, w, sd, m };
    if (best && r >= 2) break;
  }
  if (!best) { console.log(`⚠ ${k} topilmadi`); continue; }
  await writeFile(O + `counts/${k}.mp3`, best.s.mp3); await writeFile(O + `counts/${k}.json`, JSON.stringify(best.w));
  man[k] = { mean: +best.m.toFixed(2), sd: +best.sd.toFixed(2) }; console.log(`✓ ${k} oraliq ${best.m.toFixed(2)}±${best.sd.toFixed(2)}`);
  await writeFile(O + 'manifest.json', JSON.stringify(man, null, 1));
}
console.log('tayyor');
