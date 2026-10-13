// Offline unit tests: fetch is mocked, no key or network needed.
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { textToSpeechMp3, prepareText, checkConnection, ElevenLabsError } from '../server/tts/elevenlabsMp3.ts';

const FAKE_KEY = 'test-key-not-real';
const MP3 = Buffer.concat([Buffer.from('ID3'), Buffer.alloc(64, 1)]);

beforeEach(() => {
  process.env.ELEVENLABS_API_KEY = FAKE_KEY;
  process.env.ELEVENLABS_VOICE_FEMALE = 'voice-f';
  delete process.env.ELEVENLABS_MODEL;
  delete process.env.ELEVENLABS_LANGUAGE_CODE;
});

const mockFetch = (status: number, body: Buffer | string, seen: { url?: string; init?: RequestInit }) =>
  (async (url: string, init?: RequestInit) => {
    seen.url = url;
    seen.init = init;
    return new Response(typeof body === 'string' ? body : new Uint8Array(body), { status });
  }) as unknown as typeof fetch;

test('writes MP3 and sends key only in the header', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'el-'));
  const seen: { url?: string; init?: RequestInit } = {};
  const n = await textToSpeechMp3("Har bir g'oya bitta nuqtadan boshlanadi.", join(dir, 'a.mp3'), { fetchImpl: mockFetch(200, MP3, seen), languageCode: 'uz' });
  assert.equal(n, MP3.length);
  assert.deepEqual(await readFile(join(dir, 'a.mp3')), MP3);
  assert.match(seen.url!, /\/v1\/text-to-speech\/voice-f\?output_format=mp3_44100_128$/);
  assert.equal((seen.init!.headers as Record<string, string>)['xi-api-key'], FAKE_KEY);
  assert.ok(!seen.url!.includes(FAKE_KEY));
  const body = JSON.parse(String(seen.init!.body));
  assert.equal(body.text, 'Har bir gʻoya bitta nuqtadan boshlanadi.');
  assert.equal(body.model_id, 'eleven_multilingual_v2');
  assert.equal(body.language_code, 'uz');
});

test('missing key gives a clear error and makes no request', async () => {
  delete process.env.ELEVENLABS_API_KEY;
  let called = false;
  const f = (async () => { called = true; return new Response(''); }) as unknown as typeof fetch;
  await assert.rejects(textToSpeechMp3('Salom', '/tmp/x.mp3', { fetchImpl: f }), /ELEVENLABS_API_KEY topilmadi/);
  assert.equal(called, false);
});

test('401 is explained and the key never appears in the error', async () => {
  const seen = {};
  await assert.rejects(
    textToSpeechMp3('Salom', '/tmp/x.mp3', { fetchImpl: mockFetch(401, `{"detail":"invalid key ${FAKE_KEY}"}`, seen) }),
    (e: Error) => e instanceof ElevenLabsError && /notoʻgʻri/.test(e.message) && !e.message.includes(FAKE_KEY),
  );
});

test('non-MP3 response is rejected', async () => {
  await assert.rejects(textToSpeechMp3('Salom', '/tmp/x.mp3', { fetchImpl: mockFetch(200, Buffer.from('{"oops":1}'), {}) }), /MP3 emas/);
});

test('network failure is reported as a connection problem', async () => {
  const f = (async () => { throw new TypeError('fetch failed'); }) as unknown as typeof fetch;
  await assert.rejects(checkConnection(f), /ulanib boʻlmadi/);
});

test('Uzbek apostrophes are normalised, Cyrillic kept', () => {
  assert.equal(prepareText("  O'zbekiston  "), 'Oʻzbekiston');
  assert.equal(prepareText('Ўзбекистон'), 'Ўзбекистон');
});
