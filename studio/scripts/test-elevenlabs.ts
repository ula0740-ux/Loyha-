// Live check of the real ElevenLabs API: key -> voices list -> Uzbek MP3.
// usage: npm run test:elevenlabs ["matn"]   (needs ELEVENLABS_API_KEY in .env and access to api.elevenlabs.io)
import '../server/net.ts';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { checkConnection, textToSpeechMp3, ElevenLabsError } from '../server/tts/elevenlabsMp3.ts';

const run = promisify(execFile);
const text = process.argv[2] || 'Assalomu alaykum! Har bir gʻoya bitta nuqtadan boshlanadi. Oʻzbekiston — mening Vatanim.';
const out = 'out/elevenlabs-test.mp3';

try {
  console.log('1) Kalit va tarmoq tekshirilmoqda…');
  const { voices, restricted } = await checkConnection();
  console.log(restricted
    ? '   ✓ Ulanish bor. Kalit cheklangan (ovozlar roʻyxatini oʻqish ruxsati yoʻq) — TTS uchun bu yetarli.'
    : `   ✓ Ulanish bor. Hisobingizda ${voices.length} ta ovoz.`);
  console.log('2) Oʻzbekcha MP3 yaratilmoqda…');
  const bytes = await textToSpeechMp3(text, out);
  const { stdout } = await run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=codec_name', '-of', 'csv=p=0', out]);
  const [codec, dur] = stdout.trim().split('\n');
  if (codec.trim() !== 'mp3' || !(Number(dur) > 0.5)) throw new Error(`Fayl yaroqsiz: ${stdout}`);
  console.log(`   ✓ ${out} (${(bytes / 1024).toFixed(0)} KB, ${Number(dur).toFixed(1)} s)`);
  console.log('Natija: API ishlayapti. Talaffuz sifatini faylni tinglab baholang.');
} catch (e) {
  const msg = e instanceof ElevenLabsError ? e.message : String((e as Error).message);
  console.error('✗', msg);
  if (/ELEVENLABS_API_KEY|Ovoz ID/.test(msg)) console.error('  -> studio/.env faylini toʻldiring (README: ElevenLabs boʻlimi).');
  if (/ulanib boʻlmadi/.test(msg)) console.error('  -> Tarmoqda api.elevenlabs.io ga ruxsat bering (bulut muhitida: Network access → Allowed domains).');
  process.exit(1);
}
