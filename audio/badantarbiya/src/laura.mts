// Laura ovozi (foydalanuvchi tanlagan 3-shablon, 2026-10-23): barcha gaplar + ravon sanoq yozuvlari.
// ADM — "A di em" (foydalanuvchi: "A-di-em Jizzax xodimlari" deb eshitilsin), STT da ADM/a di em tekshiriladi.
//   cd studio && npx tsx ../audio/badantarbiya/src/laura.mts   (ONLY=f0,m1,... yoki ONLY=counts)
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score, normForCompare } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
const B = '/home/user/Loyha-/audio/badantarbiya/', O = B + 'laura/', V = 'FGY2WhTYpPnrIDTdsKH5';
const VS = { stability: .3, similarity_boost: .75, style: .7, use_speaker_boost: true }, TAG = '[excited] ';
const L: { id: string; text: string }[] = JSON.parse(await readFile(B + 'qiz_ovozi/narration.json', 'utf8')).lines;
const TEXT: Record<string, string> = Object.fromEntries(L.map((l) => [l.id, l.text]));
TEXT.f0 = TEXT.f0.replace('xodimlari! ', 'xodimlari! Xayrli tong! ');
const tts = (t: string) => prepareUzbek(t, 'latin').tts.replace(/A-de-em,? ?(?=Jizzakh)/g, 'A di em ').replace(/A-de-em/g, 'A di em')
  .replace('Hammaga', 'Ham-maga').replace('Khavfsizlik qoidalariga rioya', 'Khavf-sizlik qoi-dalariga ri-oya');
const hasADM = (h: string) => /\bADM\b|АДМ|\bA,? ?D,? ?M\b|a\s*di\s*em/i.test(h);
await mkdir(O + 'lines', { recursive: true }); await mkdir(O + 'counts', { recursive: true });
const only = process.env.ONLY?.split(',');
const man: any = JSON.parse(await readFile(O + 'manifest.json', 'utf8').catch(() => '{"lines":{},"counts":[]}'));
for (let n = 0; n < L.length; n++) {
  const id = L[n].id; if (only && !only.includes(id)) continue;
  const text = TAG + tts(TEXT[id]), ctx = { previousText: L[n - 1] && prepareUzbek(TEXT[L[n - 1].id], 'latin').tts, nextText: L[n + 1] && prepareUzbek(TEXT[L[n + 1].id], 'latin').tts };
  let best: any = null;
  for (let k = 0; k < 5; k++) {
    const s = await synth(text, { voice: V, model: 'eleven_v4', voiceSettings: VS, ...ctx });
    const h = await transcribe(s.mp3), sc = score(spokenReference(TEXT[id]), h), adm = !/ADM/.test(TEXT[id]) || hasADM(h);
    console.log(`${id} #${k + 1}: STT ${(sc.similarity * 100).toFixed(1)}% ADM:${adm ? 'ok' : "yo'q"} | ${h}`);
    const rank = sc.similarity + (adm ? 1 : 0);
    if (!best || rank > best.rank) best = { s, rank, sim: sc.similarity, adm };
    if (adm && sc.similarity >= .97) break;
  }
  await writeFile(O + `lines/${id}.mp3`, best.s.mp3); man.lines[id] = { sim: +best.sim.toFixed(3), adm: best.adm };
  console.log(`✓ ${id} (${(best.sim * 100).toFixed(1)}%${best.adm ? '' : ', ADM tekshiruvdan o\'tmadi'})`);
}
/* sanoq: bitta ravon gap ("Bir, ikki, uch, to'rt, bir, ikki, uch, to'rt! Qani-qani bo'shashmaymiz!") —
   so'z oraliqlari eng tekis va 0.6 s ga eng yaqin yozuvlar olinadi (foydalanuvchi namunasi ritmi) */
if (!only || only.includes('counts')) {
  const cands: any[] = [];
  for (let k = 0; k < 8; k++) {
    const s = await synth(TAG + 'Bir, ikki, uch, toʻrt, bir, ikki, uch, toʻrt! Qani-qani boʻshashmaymiz!', { voice: V, model: 'eleven_v4', voiceSettings: VS });
    const w = s.words.filter((x) => !x.text.startsWith('[')), h = normForCompare(await transcribe(s.mp3));
    if (w.length !== 10 || !/bir ikki uch to.?rt bir ikki uch to.?rt qani/.test(h)) { console.log(`sanoq #${k + 1}: rad | ${h}`); continue; }
    const d = w.slice(0, 8).map((x, i, a) => i ? x.start - a[i - 1].start : 0).slice(1), mean = d.reduce((a, b) => a + b) / d.length;
    const sd = Math.sqrt(d.reduce((a, b) => a + (b - mean) ** 2, 0) / d.length), cost = sd + Math.abs(mean - .6) * .5;
    console.log(`sanoq #${k + 1}: oraliq ${mean.toFixed(2)}±${sd.toFixed(2)} | ${h}`);
    cands.push({ s, w, cost, mean, sd });
  }
  cands.sort((a, b) => a.cost - b.cost); man.counts = [];
  for (const [i, c] of cands.slice(0, 3).entries()) { const f = `counts/c${i + 1}.mp3`; await writeFile(O + f, c.s.mp3); man.counts.push({ file: f, words: c.w, mean: c.mean, sd: c.sd }); }
}
await writeFile(O + 'manifest.json', JSON.stringify(man, null, 1)); console.log('tayyor');
