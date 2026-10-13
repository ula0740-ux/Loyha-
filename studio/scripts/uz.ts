// Uzbek pronunciation toolkit for ElevenLabs (Uzbek Latin only, see .claude/skills/uzbek-tts).
//   npm run uz -- prepare "matn"                                  TTS ga nima ketishini koʻrsatadi (internetsiz)
//   npm run uz -- test "matn" [--model eleven_v3] [--takes 2]     ovozlab, STT bilan tekshiradi
//   npm run uz -- make "matn" out/a.mp3 [--file matn.txt] [--min 0.97] [--attempts 3]
//                                                                 gapma-gap yaratadi, har gapni tekshiradi, .json hisobot
//   npm run uz -- redo out/a.json 2,4                              faqat 2- va 4-gaplarni qayta yaratadi
//   npm run uz -- word Jizzax [--extra "Jiz-zax"]                  bitta soʻzni sinab, eng yaxshi shaklni lugʻatga yozadi
//   npm run uz -- lexicon list | add <soʻz> --spoken <shakl> [--kind word|term|abbr] | approve <soʻz> | remove <soʻz>
//   npm run uz -- stt fayl.mp3 ["kutilgan matn"]                   tayyor faylni tekshiradi
import '../server/net.ts';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { prepareUzbek } from '../server/uz/prepare.ts';
import { testVariants, fixWord, transcribe, score, DEFAULT_MODEL } from '../server/uz/eleven.ts';
import { makeNarration, redoNarration, type NarrationReport } from '../server/uz/segments.ts';
import { lexKey, loadLexicon, saveLexicon, sameLetters, upsert, type LexEntry, type UzScript } from '../server/uz/lexicon.ts';

const argv = process.argv.slice(2);
const flag = (k: string, d?: string) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const pos = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')));
const [cmd, a1, a2] = pos;
const opts = { model: flag('model', DEFAULT_MODEL), voice: flag('voice') };
const pct = (x?: number) => (x === undefined ? '—' : (x * 100).toFixed(1) + '%');
const summary = (r: NarrationReport) => {
  const bad = r.segments.filter((s) => (s.similarity ?? 1) < 0.97);
  console.log(`✓ ${r.out}  (${r.segments.length} gap, hisobot: ${r.out.replace(/\.mp3$/, '')}.json)`);
  if (bad.length) console.log(`Tekshirish kerak: ${bad.map((s) => s.i).join(', ')} — soʻzni tuzating (npm run uz -- word ...) va: npm run uz -- redo ${r.out.replace(/\.mp3$/, '')}.json ${bad.map((s) => s.i).join(',')}`);
};

async function main() {
  switch (cmd) {
    case 'prepare': {
      const p = prepareUzbek(a1, (flag('script', 'latin') as UzScript));
      console.log(JSON.stringify({ original: p.original, tts: p.tts, numbers: p.numbers, warnings: p.warnings }, null, 2));
      break;
    }
    case 'test': {
      const dir = flag('out', 'out/uz-test')!;
      await mkdir(dir, { recursive: true });
      const scripts = (flag('script', 'latin')!.split(',') as UzScript[]);
      const res = await testVariants(a1, { ...opts, scripts, takes: Number(flag('takes', '1')) });
      for (const [k, r] of res.entries()) {
        const f = `${dir}/${r.script}-${k + 1}.mp3`;
        await writeFile(f, r.mp3);
        console.log(`\n[${r.script} #${k + 1}] oʻxshashlik ${pct(r.score.similarity)}  -> ${f}`);
        console.log(`  yuborildi: ${r.tts}`);
        console.log(`  eshitildi: ${r.score.heard}`);
        for (const p of r.score.problems) console.log(`  ✗ "${p.expected}" -> "${p.heard}"   (npm run uz -- word "${p.expected}")`);
      }
      console.log('\nAvtomatik baho taxminiy — quloq bilan tasdiqlang.');
      break;
    }
    case 'make':
    case 'say': {
      const text = flag('file') ? await readFile(flag('file')!, 'utf8') : a1;
      const out = (flag('file') ? a1 : a2) || 'out/uz-say.mp3';
      const r = await makeNarration(text, out, { ...opts, min: Number(flag('min', '0.97')), attempts: Number(flag('attempts', '3')), check: flag('check') !== 'no' });
      summary(r);
      break;
    }
    case 'redo': {
      const which = (a2 || '').split(',').map(Number).filter(Boolean);
      if (!which.length) throw new Error('qaysi gaplar? masalan: npm run uz -- redo out/a.json 2,4');
      summary(await redoNarration(a1, which, { min: Number(flag('min', '0.97')), attempts: Number(flag('attempts', '3')) }));
      break;
    }
    case 'word': {
      const extra = (flag('extra') || '').split(',').map((s) => s.trim()).filter(Boolean);
      const lex = await loadLexicon();
      const approved = lex.entries[lexKey(a1)]?.status === 'approved';
      const r = await fixWord(a1, { ...opts, extra, save: !approved, takes: Number(flag('takes', '2')) });
      for (const x of r.results) console.log(`  ${x.form.padEnd(16)} ${pct(x.similarity)}  eshitildi: ${x.heard.join(' | ')}`);
      if (r.rejected.length) console.log(`  rad etildi (harflar oʻzgargan): ${r.rejected.join(', ')}`);
      console.log(approved ? 'Lugʻatda tasdiqlangan shakl bor — oʻzgartirilmadi.' : `Eng yaxshi shakl lugʻatga "candidate" sifatida yozildi: ${r.results[0]?.form}. Tinglab, tasdiqlang: npm run uz -- lexicon approve ${a1}`);
      break;
    }
    case 'lexicon': {
      const lex = await loadLexicon();
      const sub = a1, word = a2;
      if (sub === 'list') {
        for (const [k, e] of Object.entries(lex.entries)) console.log(`${e.status === 'approved' ? '✓' : '?'} ${k.padEnd(14)} ${(e.kind ?? 'word').padEnd(5)} ${e.latin.padEnd(12)} -> ${e.spoken.latin}${e.score ? '  ' + pct(e.score) : ''}`);
      } else if (sub === 'add') {
        const spoken = flag('spoken'), kind = (flag('kind') || 'word') as LexEntry['kind'];
        if (spoken && /[Ѐ-ӿ]/.test(spoken)) throw new Error('faqat lotin yozuvi: ' + spoken);
        if (spoken && kind === 'word' && !sameLetters(spoken, word)) throw new Error(`"${spoken}" harflari "${word}" dan farq qiladi. Soʻz harflari oʻzgarmaydi; atama boʻlsa --kind term qoʻshing.`);
        upsert(lex, word, { ...(spoken ? { spoken: { latin: spoken } } : {}), prefer: 'latin', kind, status: 'candidate' });
        await saveLexicon(lex); console.log('qoʻshildi:', lexKey(word));
      } else if (sub === 'approve') {
        const e = lex.entries[lexKey(word)]; if (!e) throw new Error('lugʻatda yoʻq: ' + word);
        e.status = 'approved'; await saveLexicon(lex); console.log('tasdiqlandi:', lexKey(word));
      } else if (sub === 'remove') {
        delete lex.entries[lexKey(word)]; await saveLexicon(lex); console.log('oʻchirildi:', lexKey(word));
      } else console.log('lexicon list | add <soʻz> --spoken <shakl> [--kind word|term|abbr] | approve <soʻz> | remove <soʻz>');
      break;
    }
    case 'stt': {
      const heard = await transcribe(await readFile(a1));
      console.log('eshitildi:', heard);
      if (a2) { const s = score(prepareUzbek(a2).tts, heard); console.log('oʻxshashlik', pct(s.similarity), s.problems); }
      break;
    }
    default:
      console.log('buyruqlar: prepare | test | make | redo | word | lexicon | stt  (fayl boshidagi izohga qarang)');
  }
}
main().catch((e) => { console.error('✗', (e as Error).message); process.exit(1); });
