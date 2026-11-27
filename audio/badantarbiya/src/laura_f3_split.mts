// f3: ko'rsatma qismi va "Bo'shashmaymiz, ADM Jizzax!" alohida yoziladi (gap ichida ADM noto'g'ri chiqavergani uchun),
// so'ng ikki butun gap 0.35 s pauza bilan ulanadi. ADM yozilishining bir nechta shakli sinaladi, STT "ADM Jizzax" eshitgani olinadi.
import '/home/user/Loyha-/studio/server/net.ts';
import { prepareUzbek, spokenReference } from '/home/user/Loyha-/studio/server/uz/prepare.ts';
import { synth, transcribe, score } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { writeFile } from 'node:fs/promises';
const O = '/home/user/Loyha-/audio/badantarbiya/laura/', V = 'FGY2WhTYpPnrIDTdsKH5', VS = { stability: .3, similarity_boost: .75, style: .7, use_speaker_boost: true };
const A = 'Bizda keyingi mashqimiz: oyoqlarimiz yelka kengligida, qoʻllarimiz esa ikki yonga yoygan holatda. Oʻng va chap tomonga qayrilib olamiz.';
let best: any = null;
for (let k = 0; k < 4; k++) {
  const s = await synth('[excited] ' + prepareUzbek(A, 'latin').tts, { voice: V, model: 'eleven_v4', voiceSettings: VS, nextText: 'Boʻshashmaymiz!' });
  const sc = score(spokenReference(A), await transcribe(s.mp3)); console.log(`f3a #${k + 1}: ${(sc.similarity * 100).toFixed(1)}%`);
  if (!best || sc.similarity > best.sim) best = { s, sim: sc.similarity }; if (sc.similarity >= .98) break;
}
await writeFile(O + 'lines/f3a.mp3', best.s.mp3);
let got = false;
for (const f of ['A di em Jizzakh', 'A di em, Jizzakh', 'A di em Jizzakh khodimlari', 'A-di-em Jizzakh']) {
  for (let k = 0; k < 3 && !got; k++) {
    const s = await synth(`[excited] Boʻshashmaymiz, ${f}!`, { voice: V, model: 'eleven_v4', voiceSettings: VS, previousText: prepareUzbek(A, 'latin').tts });
    const h = await transcribe(s.mp3), ok = /bo.?shashmaymiz.*\bADM\b,? ?jizza/i.test(h) && !/xodim/i.test(h) === !f.includes('khodimlari');
    console.log(`f3b "${f}" #${k + 1}: ${ok ? 'ok' : '--'} | ${h}`);
    if (ok) { await writeFile(O + 'lines/f3b.mp3', s.mp3); console.log('✓ f3b:', f); got = true; }
  }
  if (got) break;
}
