import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cyrToLat, latToCyr, detectScript, normalizeLatin, toScript } from '../src/lib/uzbek.ts';

test('Cyrillic to Latin: special letters', () => {
  assert.equal(cyrToLat('Ҳар бир ғоя битта нуқтадан бошланади.'), 'Har bir gʻoya bitta nuqtadan boshlanadi.');
  assert.equal(cyrToLat('ўқитувчи'), 'oʻqituvchi');
  assert.equal(cyrToLat('Шаҳар, чой, янги'), 'Shahar, choy, yangi');
});

test('Cyrillic е and ц follow position rules', () => {
  assert.equal(cyrToLat('ер'), 'yer');
  assert.equal(cyrToLat('келди'), 'keldi');
  assert.equal(cyrToLat('цирк'), 'sirk');
  assert.equal(cyrToLat('станция'), 'stansiya');
});

test('Latin to Cyrillic round trip on common words', () => {
  assert.equal(latToCyr("Har bir g'oya bitta nuqtadan boshlanadi."), 'Ҳар бир ғоя битта нуқтадан бошланади.');
  assert.equal(latToCyr('Oʻzbekiston'), 'Ўзбекистон');
  assert.equal(latToCyr('ekran'), 'экран');
});

test('apostrophe variants are normalised', () => {
  assert.equal(normalizeLatin("o'qish g`oya ma'no"), 'oʻqish gʻoya maʼno');
});

test('script detection and toScript', () => {
  assert.equal(detectScript('Салом дунё'), 'cyrillic');
  assert.equal(detectScript('Salom dunyo'), 'latin');
  assert.equal(toScript('Салом дунё', 'latin'), 'Salom dunyo');
  assert.equal(toScript('Salom dunyo', 'cyrillic'), 'Салом дунё');
});
