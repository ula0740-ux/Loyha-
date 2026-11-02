// Pauzasiz yozuv tanlash: har jumla bir necha marta yoziladi, STT >= 97% va berilgan ikki so'z orasidagi pauza eng kichigi tanlanadi.
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { writeFile } from 'node:fs/promises';
const Q = '/home/user/Loyha-/audio/badantarbiya/qiz_ovozi/audio/', V = 'EXAVITQu4vr4xnSDxMaL';
// id, matn (TTS ga), STT tekshiruv matni, pauza o'lchanadigan so'zlar juftligi (TTS yozuvidagi so'z boshlari)
const J: [string, string, string, string, string][] = [
  ['f0', 'Assalomu alaykum, A-de-em Jizzakh khodimlari! Ertalabki badantarbiya mashqlarimizni boshlaymiz. Dastlab oraliq masofani saqlash maqsadida qoʻllarimizni ikki yonga yoygan holda oʻngga va chapga qarab olamiz.',
   'Assalomu alaykum, ADM Jizzax xodimlari! Ertalabki badantarbiya mashqlarimizni boshlaymiz. Dastlab oraliq masofani saqlash maqsadida qoʻllarimizni ikki yonga yoygan holda oʻngga va chapga qarab olamiz.', 'A-de-em', 'Jizzakh'],
  ['m0', 'Juda ham ajoyib!', 'Juda ham ajoyib!', 'ham', 'ajoyib'],
  ['m3', prepareUzbek('Juda ham ajoyib! Bizda keyingi mashqimiz: oyoqlarimiz yelka kengligida, qoʻllarimiz esa yelkada. Yelkalarimizni oldinga va orqaga toʻrt martadan aylantirib olamiz.', 'latin').tts,
   'Juda ham ajoyib! Bizda keyingi mashqimiz: oyoqlarimiz yelka kengligida, qoʻllarimiz esa yelkada. Yelkalarimizni oldinga va orqaga toʻrt martadan aylantirib olamiz.', 'ham', 'ajoyib'],
  ['m6', prepareUzbek('Juda ham ajoyib! Bizda navbatdagi mashqimiz: oyoqlar yelka kengligida, qoʻllarimiz esa tizzada. Tizzalarimizni ichkariga va tashqariga toʻrt martadan aylantirib olamiz.', 'latin').tts,
   'Juda ham ajoyib! Bizda navbatdagi mashqimiz: oyoqlar yelka kengligida, qoʻllarimiz esa tizzada. Tizzalarimizni ichkariga va tashqariga toʻrt martadan aylantirib olamiz.', 'ham', 'ajoyib'],
];
const prev = prepareUzbek('Ertalabki badantarbiya mashqlarimiz.', 'latin').tts;
for (const [id, tts, ref, w1, w2] of J) {
  let best: any = null;
  for (let k = 0; k < 6; k++) {
    const s = await synth(tts, { voice: V, model: 'eleven_v4', previousText: prev, nextText: prev });
    const sc = score(spokenReference(ref), await transcribe(s.mp3));
    const i = s.words.findIndex((w) => w.text.replace(/[^\p{L}-]/gu, '').startsWith(w1));
    const j = s.words.findIndex((w, n) => n > i && w.text.replace(/[^\p{L}-]/gu, '').startsWith(w2));
    const gap = i >= 0 && j > i ? s.words[j].start - s.words[i].end : 9;
    console.log(`${id} #${k + 1}: STT ${(sc.similarity * 100).toFixed(1)}%  pauza ${w1}→${w2} ${gap.toFixed(2)}s`);
    if (sc.similarity >= 0.95 && (!best || gap < best.gap)) best = { s, gap, sc };
    if (best && best.gap < 0.12 && best.sc.similarity >= 0.97) break;
  }
  await writeFile(Q + id + '.mp3', best.s.mp3);
  console.log(`✓ ${id} tanlandi: pauza ${best.gap.toFixed(2)}s, STT ${(best.sc.similarity * 100).toFixed(1)}%`);
}
