// Official ElevenLabs SDK: Uzbek text -> MP3 file.
// usage: npm run say -- "Matn" [chiqish.mp3] [voice_id]
// The key comes from ELEVENLABS_API_KEY (.env or environment); it is never written in code.
import '../server/net.ts'; // loads .env and routes fetch through the proxy when one is set
import { createWriteStream } from 'node:fs';
import { mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';
import { prepareText } from '../server/tts/elevenlabsMp3.ts';

const text = process.argv[2] || 'Har bir gʻoya bitta nuqtadan boshlanadi. Kod bilan harakat. Gʻoyadan videogacha.';
const out = process.argv[3] || 'out/say-uz.mp3';
const voiceId = process.argv[4] || process.env.ELEVENLABS_VOICE_FEMALE || process.env.ELEVENLABS_VOICE_MALE || 'JBFqnCBsd6RMkjVDRZzb';

if (!process.env.ELEVENLABS_API_KEY) {
  console.error('✗ ELEVENLABS_API_KEY topilmadi: studio/.env ga yoki muhit oʻzgaruvchisiga qoʻshing.');
  process.exit(1);
}

const elevenlabs = new ElevenLabsClient(); // reads process.env.ELEVENLABS_API_KEY

try {
  const audio = await elevenlabs.textToSpeech.convert(voiceId, {
    text: prepareText(text),
    modelId: process.env.ELEVENLABS_MODEL || 'eleven_multilingual_v2',
    outputFormat: 'mp3_44100_128',
  });
  await mkdir(dirname(out), { recursive: true });
  await pipeline(Readable.fromWeb(audio as import('node:stream/web').ReadableStream), createWriteStream(out));
  console.log(`✓ MP3 saqlandi: ${out}`);
} catch (e) {
  const err = e as { statusCode?: number; message?: string };
  if (err.statusCode === 401) console.error('✗ API kalit notoʻgʻri (401).');
  else if (!err.statusCode) console.error('✗ api.elevenlabs.io ga ulanib boʻlmadi (internet yoki tarmoq ruxsati).');
  else console.error(`✗ ElevenLabs xatosi ${err.statusCode}: ${String(err.message).slice(0, 200)}`);
  process.exit(1);
}
