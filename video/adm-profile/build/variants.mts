// Pronunciation samples for the user's ear (uzbek-tts rule: the user decides). 4 variants per word, each in its own
// natural carrier sentence; the spoken form is swapped in after prepareUzbek. The lexicon is NOT changed here.
// run from studio/: ELEVENLABS_API_KEY=... npx tsx ../video/adm-profile/build/variants.mts
import '../../../studio/server/net.ts';
import { prepareUzbek } from '../../../studio/server/uz/prepare.ts';
import { synth, transcribe } from '../../../studio/server/uz/eleven.ts';
import { writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const OUT = fileURLToPath(new URL('../audio/variants/', import.meta.url));
const SETS = [
  { word: 'CKD', text: 'Bu CKD sexida avtomobillar yigʻiladi.', from: /se ka de/i, forms: ['Si-Ka-De', 'Si-Ke-Di', 'Se-Ka-De', 'Si-Kay-Di'] },
  { word: 'SKD', text: 'Zavod faoliyatini dastlab SKD sexida boshlagan.', from: /es ka de/i, forms: ['Es-Ka-De', 'Es-Ke-Di', 'Se-Ka-De', 'Es-Kay-Di'] },
  { word: 'ADM', text: 'ADM Jizzax zavodiga xush kelibsiz.', from: /A-de-em,?/, forms: ['A-de-em,', 'A. De. Em.', 'A-De-Em,', 'Ey-Di-Em,'] },
];
const CTX_PREV = prepareUzbek('Kompaniyaga 2014-yilda asos solingan.', 'latin').tts;
const CTX_NEXT = prepareUzbek('Guruh tarkibida 33 ta kompaniya va 5 900 nafar xodim bor.', 'latin').tts;
const LABELS = ['Birinchi variant.', 'Ikkinchi variant.', 'Uchinchi variant.', 'Toʻrtinchi variant.'];
const sil = OUT + '_sil.mp3';
execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '0.6', '-b:a', '128k', sil]);
const labels: string[] = [];
for (let i = 0; i < 4; i++) { const l = await synth(LABELS[i], { model: 'eleven_v4', seed: 7 }); labels[i] = OUT + `_label${i}.mp3`; await writeFile(labels[i], l.mp3); }
for (const S of SETS) {
  const base = prepareUzbek(S.text, 'latin').tts;
  const list: string[] = [];
  for (let i = 0; i < 4; i++) {
    const tts = base.replace(S.from, S.forms[i]);
    // neighbouring film sentences as context (without it v4 gave a Persian accent to short lines)
    const s = await synth(tts, { model: 'eleven_v4', seed: 7, previousText: CTX_PREV, nextText: CTX_NEXT });
    const f = OUT + `${S.word}_${i + 1}.mp3`; await writeFile(f, s.mp3);
    console.log(`${S.word}_${i + 1}  [${S.forms[i]}]  yuborildi: ${tts}  |  STT: ${await transcribe(s.mp3)}`);
    list.push(labels[i], sil, f, sil, sil);
  }
  const args = ['-v', 'error', '-y']; list.forEach((f) => args.push('-i', f));
  args.push('-filter_complex', list.map((_, i) => `[${i}:a]aresample=44100,aformat=channel_layouts=mono[a${i}]`).join(';') + ';' + list.map((_, i) => `[a${i}]`).join('') + `concat=n=${list.length}:v=0:a=1[o]`, '-map', '[o]', '-b:a', '160k', OUT + `${S.word}_variantlar.mp3`);
  execFileSync('ffmpeg', args);
}
execFileSync('sh', ['-c', `rm -f "${OUT}"_label* "${sil}"`]);
