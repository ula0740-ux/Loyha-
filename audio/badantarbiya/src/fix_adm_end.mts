// Gap oxiridagi ADM ("Boʻshashmaymiz, ADM!", "Olgʻa, ADM!"): oxirida v4 "Adam/Adem" deydi.
// Shu sababli jumla ortidan qisqa davom ("Juda ham ajoyib!") bilan yoziladi va o'sha yozuvning o'zi ADM so'zidan keyin kesiladi
// (so'zlar boshqa yozuvlardan ulanmaydi). Kesilgan yozuv STT da "ADM" chiqqani va >= 95% bo'lgani tanlanadi.
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
const B = '/home/user/Loyha-/audio/badantarbiya/qiz_ovozi/', V = 'EXAVITQu4vr4xnSDxMaL', T = '/tmp/adm_end_';
const L: { id: string; text: string }[] = JSON.parse(await readFile(B + 'narration.json', 'utf8')).lines;
const tts = (t: string) => prepareUzbek(t, 'latin').tts.replace(/A-de-em/g, 'Aa-de-em')
  .replace('Hammaga', 'Ham-maga').replace('Khavfsizlik qoidalariga rioya', 'Khavf-sizlik qoi-dalariga ri-oya');
for (const id of (process.env.ONLY ?? 'f3,f5').split(',')) {
  const n = L.findIndex((l) => l.id === id), text = tts(L[n].text) + ' Juda ham ajoyib!';
  const prev = L[n - 1] && prepareUzbek(L[n - 1].text, 'latin').tts;
  let best: any = null;
  for (let k = 0; k < 8; k++) {
    const s = await synth(text, { voice: V, model: 'eleven_v4', previousText: prev });
    const i = s.words.findLastIndex((w) => w.text.startsWith('Aa-de-em'));
    if (i < 0 || !s.words[i + 1]) continue;
    const end = Math.min(s.words[i].end + 0.14, s.words[i + 1].start - 0.02);
    await writeFile(T + 'raw.mp3', s.mp3);
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', T + 'raw.mp3', '-af', `atrim=0:${end.toFixed(3)},afade=t=out:st=${(end - 0.06).toFixed(3)}:d=0.06`, '-b:a', '192k', T + 'cut.mp3']);
    const mp3 = await readFile(T + 'cut.mp3'), tr: any = await transcribe(mp3), heard = typeof tr === 'string' ? tr : tr.text;
    const sc = score(spokenReference(L[n].text), tr), adm = /(\bADM|\bA,? D,? M)[.!]?$/i.test(heard.trim());
    console.log(`${id} #${k + 1}: STT ${(sc.similarity * 100).toFixed(1)}% ADM:${adm ? 'ha' : "yo'q"} | ${heard}`);
    if (sc.similarity >= 0.95 && adm) { best = mp3; break; }
  }
  if (best) { await writeFile(B + 'audio/' + id + '.mp3', best); console.log('✓', id); } else console.log('✗', id, 'topilmadi');
}
