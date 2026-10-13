// Uzbek pronunciation toolkit for ElevenLabs.
//   npm run uz -- prepare "matn" [--script latin|cyrillic]
//   npm run uz -- test "matn" [--model eleven_v3] [--voice ID]          lotin va kirillni STT bilan solishtiradi
//   npm run uz -- say "matn" out/fayl.mp3 [--script auto|latin|cyrillic] [--attempts 3] [--min 0.9]
//   npm run uz -- word Jizzax [--extra "Жиззах,Jizzax"]                   bitta soʻzni qayta sinab, lugʻatga yozadi
//   npm run uz -- lexicon list | add <soʻz> --spoken <shakl> [--prefer cyrillic] | approve <soʻz> | remove <soʻz>
import '../server/net.ts';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { prepareUzbek } from '../server/uz/prepare.ts';
import { testVariants, fixWord, transcribe, score, DEFAULT_MODEL } from '../server/uz/eleven.ts';
import { lexKey, loadLexicon, saveLexicon, upsert, type UzScript } from '../server/uz/lexicon.ts';

const argv = process.argv.slice(2);
const flag = (k: string, d?: string) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const pos = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')));
const [cmd, a1, a2] = pos;
const opts = { model: flag('model', DEFAULT_MODEL), voice: flag('voice') };
const pct = (x: number) => (x * 100).toFixed(1) + '%';

async function main() {
  switch (cmd) {
    case 'prepare': {
      const p = prepareUzbek(a1, (flag('script', 'latin') as UzScript));
      console.log(JSON.stringify({ original: p.original, normalized: p.normalized, tts: p.tts, numbers: p.numbers, warnings: p.warnings }, null, 2));
      break;
    }
    case 'test': {
      const dir = flag('out', 'out/uz-test')!;
      await mkdir(dir, { recursive: true });
      const res = await testVariants(a1, opts);
      for (const r of res) {
        const f = `${dir}/${r.script}.mp3`;
        await writeFile(f, r.mp3);
        console.log(`\n[${r.script}] oʻxshashlik ${pct(r.score.similarity)}  -> ${f}`);
        console.log(`  yuborildi: ${r.tts}`);
        console.log(`  eshitildi: ${r.score.heard}`);
        for (const p of r.score.problems) console.log(`  ✗ "${p.expected}" -> "${p.heard}"`);
      }
      console.log(`\nEng yaxshisi: ${res[0].script} (${pct(res[0].score.similarity)}). Avtomatik baho taxminiy — quloq bilan tasdiqlang.`);
      break;
    }
    case 'say': {
      const out = a2 || 'out/uz-say.mp3';
      const mode = flag('script', 'auto')!;
      const attempts = Number(flag('attempts', '3')), min = Number(flag('min', '0.9'));
      const scripts: UzScript[] = mode === 'auto' ? ['latin', 'cyrillic'] : [mode as UzScript];
      let best: Awaited<ReturnType<typeof testVariants>>[0] | null = null;
      for (let k = 0; k < attempts; k++) {
        const res = await testVariants(a1, { ...opts, scripts });
        if (!best || res[0].score.similarity > best.score.similarity) best = res[0];
        console.log(`urinish ${k + 1}: ${res.map((r) => `${r.script} ${pct(r.score.similarity)}`).join(', ')}`);
        if (best.score.similarity >= min) break;
      }
      await mkdir(dirname(out), { recursive: true });
      await writeFile(out, best!.mp3);
      await writeFile(out.replace(/\.mp3$/, '.json'), JSON.stringify({ original: a1, script: best!.script, normalized: best!.prepared.normalized, tts: best!.tts, similarity: best!.score.similarity, problems: best!.score.problems, heard: best!.score.heard, words: best!.words, model: opts.model }, null, 1));
      console.log(`✓ ${out} — ${best!.script}, oʻxshashlik ${pct(best!.score.similarity)}`);
      for (const p of best!.score.problems) console.log(`  muammoli: "${p.expected}" -> "${p.heard}"  (npm run uz -- word "${p.expected}")`);
      break;
    }
    case 'word': {
      const extra = (flag('extra') || '').split(',').map((s) => s.trim()).filter(Boolean);
      const lex = await loadLexicon();
      const approved = lex.entries[lexKey(a1)]?.status === 'approved';
      const r = await fixWord(a1, { ...opts, extra, save: !approved });
      for (const x of r.results) console.log(`  ${x.form.padEnd(16)} ${pct(x.similarity)}  eshitildi: ${x.heard}`);
      console.log(approved ? 'Lugʻatda tasdiqlangan shakl bor — oʻzgartirilmadi.' : `Eng yaxshi shakl lugʻatga "candidate" sifatida yozildi: ${r.results[0].form}. Tinglab, tasdiqlang: npm run uz -- lexicon approve ${a1}`);
      break;
    }
    case 'lexicon': {
      const lex = await loadLexicon();
      const sub = a1, word = a2;
      if (sub === 'list') {
        for (const [k, e] of Object.entries(lex.entries)) console.log(`${e.status === 'approved' ? '✓' : '?'} ${k.padEnd(14)} ${e.latin} / ${e.cyrillic}  -> ${e.spoken[e.prefer]} (${e.prefer})${e.score ? ' ' + pct(e.score) : ''}`);
      } else if (sub === 'add') {
        const spoken = flag('spoken'); const prefer = (flag('prefer') as UzScript) || (spoken && /[Ѐ-ӿ]/.test(spoken) ? 'cyrillic' : 'latin');
        upsert(lex, word, { ...(spoken ? { spoken: { [prefer]: spoken } } : {}), prefer, status: 'candidate' });
        await saveLexicon(lex); console.log('qoʻshildi:', lexKey(word));
      } else if (sub === 'approve') {
        const e = lex.entries[lexKey(word)]; if (!e) throw new Error('lugʻatda yoʻq: ' + word);
        e.status = 'approved'; await saveLexicon(lex); console.log('tasdiqlandi:', lexKey(word));
      } else if (sub === 'remove') {
        delete lex.entries[lexKey(word)]; await saveLexicon(lex); console.log('oʻchirildi:', lexKey(word));
      } else console.log('lexicon list | add <soʻz> --spoken <shakl> [--prefer latin|cyrillic] | approve <soʻz> | remove <soʻz>');
      break;
    }
    case 'stt': { // transcribe an existing file: npm run uz -- stt file.mp3 "kutilgan matn"
      const { readFile } = await import('node:fs/promises');
      const heard = await transcribe(await readFile(a1));
      console.log('eshitildi:', heard);
      if (a2) { const s = score(prepareUzbek(a2, 'latin').tts, heard); console.log('oʻxshashlik', pct(s.similarity), s.problems); }
      break;
    }
    default:
      console.log('buyruqlar: prepare | test | say | word | lexicon | stt  (fayl boshidagi izohga qarang)');
  }
}
main().catch((e) => { console.error('✗', (e as Error).message); process.exit(1); });
