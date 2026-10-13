import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cyrToLat, latToCyr } from '../src/lib/uzbek.ts';
import { cardinal, ordinal, decimal, expandNumbers } from '../server/uz/numbers.ts';
import { prepareUzbek, wordLang } from '../server/uz/prepare.ts';
import type { Lexicon } from '../server/uz/lexicon.ts';

const LEX: Lexicon = { entries: {
  jizzax: { original: 'Jizzax', latin: 'Jizzax', cyrillic: 'Жиззах', spoken: { latin: 'Jiz-zax', cyrillic: 'Жиззах' }, prefer: 'latin', kind: 'word', status: 'candidate' },
  it: { original: 'IT', latin: 'IT', cyrillic: '', spoken: { latin: 'axborot texnologiyalari' }, prefer: 'latin', kind: 'term', status: 'candidate' },
  adm: { original: 'ADM', latin: 'ADM', cyrillic: 'АДМ', spoken: { latin: 'ADM', cyrillic: 'АДМ' }, prefer: 'latin', status: 'approved' },
} };

test('letter pairs map one to one: x=х, h=ҳ, oʻ=ў, gʻ=ғ, q=қ, sh=ш, ch=ч, ng=нг', () => {
  assert.equal(latToCyr('xodim hisobot oʻqish gʻoya qabul shahar choy yangi'), 'ходим ҳисобот ўқиш ғоя қабул шаҳар чой янги');
  assert.equal(cyrToLat('ходим ҳисобот ўқиш ғоя қабул шаҳар чой янги'), 'xodim hisobot oʻqish gʻoya qabul shahar choy yangi');
});

test('x and h are never swapped or dropped (round trip)', () => {
  for (const w of ['Jizzax', 'xodim', 'Zaxira', 'hisobot', 'xohish', 'Xorazm', 'mahalla', 'baxt']) {
    const back = cyrToLat(latToCyr(w));
    assert.equal(back, w);
    assert.equal((back.match(/x/gi) || []).length, (w.match(/x/gi) || []).length);
    assert.equal((back.match(/h/gi) || []).length, (w.match(/h/gi) || []).length);
  }
});

test('sʼh is two sounds, not the digraph sh', () => {
  assert.equal(latToCyr('Isʼhoq'), 'Исҳоқ');
  assert.equal(cyrToLat('Исҳоқ'), 'Isʼhoq');
});

test('numbers in Uzbek words', () => {
  assert.equal(cardinal(855), 'sakkiz yuz ellik besh');
  assert.equal(cardinal(2026), 'ikki ming yigirma olti');
  assert.equal(cardinal(172), 'bir yuz yetmish ikki');
  assert.equal(ordinal(2026), 'ikki ming yigirma oltinchi');
  assert.equal(ordinal(1), 'birinchi');
  assert.equal(ordinal(9), 'toʻqqizinchi');
  assert.equal(ordinal(20), 'yigirmanchi');
  assert.equal(decimal('80,1'), 'sakson butun oʻndan bir');
});

test('numeric expressions: years, percents, ranges, dates', () => {
  assert.equal(expandNumbers('2026-yil').text, 'ikki ming yigirma oltinchi yil');
  assert.equal(expandNumbers('80,1%').text, 'sakson butun oʻndan bir foiz');
  assert.equal(expandNumbers('5–7').text, 'beshdan yettigacha');
  assert.equal(expandNumbers('03.09.2026').text, 'ikki ming yigirma oltinchi yil uchinchi sentabr');
  assert.equal(expandNumbers('1-hafta').text, 'birinchi hafta');
});

test('word language detection', () => {
  assert.equal(wordLang('ҳисобот'), 'uz');
  assert.equal(wordLang('выполнено'), 'ru');
  assert.equal(wordLang('xodim'), 'uz');
  assert.equal(wordLang('Head'), 'en');
});

test('Latin text: lexicon word uses its tested Latin form (same letters), numbers spoken', () => {
  const p = prepareUzbek('ADM Jizzax: 685 nafar xodim, 80,1%.', 'latin', LEX);
  assert.equal(p.original, 'ADM Jizzax: 685 nafar xodim, 80,1%.');
  assert.equal(p.tts, 'ADM Jiz-zakh: olti yuz sakson besh nafar khodim, sakson butun oʻndan bir foiz.');
  assert.ok(!/[Ѐ-ӿ]/.test(p.tts), 'Latin only');
  assert.ok(p.tts.includes('khodim'), 'x is spoken as kh, never h');
});

test('Cyrillic target: mixed input is normalised to one script, original kept', () => {
  const p = prepareUzbek('2026-йил hisoboti: Жиззах xodimlari', 'cyrillic', LEX);
  assert.equal(p.original, '2026-йил hisoboti: Жиззах xodimlari');
  assert.equal(p.normalized, '2026-йил ҳисоботи: Жиззах ходимлари.');
  assert.equal(p.tts, 'Икки минг йигирма олтинчи йил ҳисоботи: Жиззах ходимлари.');
});

test('Russian words are kept as written and reported', () => {
  const p = prepareUzbek('Режа выполнено', 'latin', LEX);
  assert.ok(p.tts.includes('выполнено'));
  assert.ok(p.warnings.some((w) => w.includes('выполнено')));
});

test('abbreviations vs capitalised words', () => {
  const p = prepareUzbek('KST XODIM', 'latin', { entries: {} });
  assert.equal(p.tts, 'Ka es te KHODIM.');
  assert.equal(prepareUzbek('UX', 'latin', { entries: {} }).tts, 'U kha.', 'x is "xa" (spoken kha), never "iks"');
});

test('ALL-CAPS terms only replace ALL-CAPS text (Uzbek "it" stays)', () => {
  assert.equal(prepareUzbek('IT boʻlimi va it', 'latin', LEX).tts, 'Akhborot tekhnologiyalari boʻlimi va it.');
});

test('Cyrillic input becomes Latin; punctuation gives pauses', () => {
  assert.equal(prepareUzbek('Жиззах ходимлари\nҲисобот тайёр', undefined, LEX).tts, 'Jiz-zakh khodimlari. Hisobot tayyor.');
});

test('lexicon spoken forms keep the letters; syllable forms never split digraphs', async () => {
  const { sameLetters } = await import('../server/uz/lexicon.ts');
  const { syllableForms } = await import('../server/uz/eleven.ts');
  assert.ok(sameLetters('Jiz-zax', 'Jizzax'));
  assert.ok(!sameLetters('Jizzah', 'Jizzax'), 'x -> h is a different word');
  assert.ok(!sameLetters('Jizax', 'Jizzax'), 'a dropped letter is rejected');
  assert.deepEqual(syllableForms('Jizzax'), ['Jiz-zax']);
  for (const f of syllableForms('oshxona choynak')) assert.ok(!/s-h|c-h|n-g/.test(f), f);
});

test('sentences split for partial re-generation', async () => {
  const { splitSentences } = await import('../server/uz/segments.ts');
  assert.deepEqual(splitSentences('Birinchi gap. Ikkinchi gap!\nUchinchi'), ['Birinchi gap.', 'Ikkinchi gap!', 'Uchinchi.']);
});

test('score finds mis-heard words', async () => {
  const { score, normForCompare } = await import('../server/uz/eleven.ts');
  assert.equal(normForCompare('Oʻzbekiston, Жиззах!'), "o'zbekiston jizzax");
  assert.equal(normForCompare('Jiz-zax'), 'jizzax');
  const s = score('ADM Jizzax xodim', 'adm jizzaks xodim');
  assert.deepEqual(s.problems, [{ expected: 'jizzax', heard: 'jizzaks' }]);
  assert.ok(s.similarity > 0.8 && s.similarity < 1);
  assert.equal(score('bir ikki', 'bir ikki').similarity, 1);
});

test('deep x is spoken as kh (written text unchanged); h is never touched', () => {
  const p = prepareUzbek('Jizzax xodimlariga xayr, mahalla, Xorazm', 'latin', { entries: {} });
  assert.equal(p.original, 'Jizzax xodimlariga xayr, mahalla, Xorazm');
  assert.equal(p.tts, 'Jizzakh khodimlariga khayr, mahalla, Khorazm.');
  assert.equal(prepareUzbek('xayr', 'latin', { entries: {} }, { xAsKh: false }).tts, 'Xayr.');
  // foreign words are left as written
  assert.equal(prepareUzbek('Head of xodimlar', 'latin', { entries: {} }).tts, 'Head of khodimlar.');
});
