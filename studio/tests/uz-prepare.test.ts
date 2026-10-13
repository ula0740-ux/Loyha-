import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cyrToLat, latToCyr } from '../src/lib/uzbek.ts';
import { cardinal, ordinal, decimal, expandNumbers } from '../server/uz/numbers.ts';
import { prepareUzbek, wordLang } from '../server/uz/prepare.ts';
import type { Lexicon } from '../server/uz/lexicon.ts';

const LEX: Lexicon = { entries: {
  jizzax: { original: 'Jizzax', latin: 'Jizzax', cyrillic: 'Жиззах', spoken: { latin: 'Jizzax', cyrillic: 'Жиззах' }, prefer: 'cyrillic', status: 'candidate' },
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

test('Latin text: Uzbek words kept Latin, lexicon word uses its tested Cyrillic form, numbers spoken', () => {
  const p = prepareUzbek('ADM Jizzax: 685 nafar xodim, 80,1%.', 'latin', LEX);
  assert.equal(p.original, 'ADM Jizzax: 685 nafar xodim, 80,1%.');
  assert.equal(p.tts, 'ADM Жиззах: olti yuz sakson besh nafar xodim, sakson butun oʻndan bir foiz.');
  assert.ok(p.tts.includes('xodim'), 'x must stay x');
});

test('Cyrillic target: mixed input is normalised to one script, original kept', () => {
  const p = prepareUzbek('2026-йил hisoboti: Жиззах xodimlari', 'cyrillic', LEX);
  assert.equal(p.original, '2026-йил hisoboti: Жиззах xodimlari');
  assert.equal(p.normalized, '2026-йил ҳисоботи: Жиззах ходимлари');
  assert.equal(p.tts, 'икки минг йигирма олтинчи йил ҳисоботи: Жиззах ходимлари');
});

test('Russian words are kept as written and reported', () => {
  const p = prepareUzbek('Режа выполнено', 'latin', LEX);
  assert.ok(p.tts.includes('выполнено'));
  assert.ok(p.warnings.some((w) => w.includes('выполнено')));
});

test('abbreviations vs capitalised words', () => {
  const p = prepareUzbek('KST XODIM', 'latin', { version: 1, entries: {} } as never);
  assert.equal(p.tts, 'ka es te XODIM');
});

test('score finds mis-heard words', async () => {
  const { score, normForCompare } = await import('../server/uz/eleven.ts');
  assert.equal(normForCompare('Oʻzbekiston, Жиззах!'), "o'zbekiston jizzax");
  const s = score('ADM Jizzax xodim', 'adm jizzaks xodim');
  assert.deepEqual(s.problems, [{ expected: 'jizzax', heard: 'jizzaks' }]);
  assert.ok(s.similarity > 0.8 && s.similarity < 1);
  assert.equal(score('bir ikki', 'bir ikki').similarity, 1);
});
