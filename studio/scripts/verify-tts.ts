// Synthesizes a test sentence with every configured voice and records which ones really work.
// The UI only labels a voice "tekshirildi" (verified) when this test produced real speech.
import '../server/net.ts';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { allVoices, readStatus, speak, writeStatus } from '../server/tts/index.ts';
import { speechBounds } from '../server/tts/audio.ts';

const SAMPLES = {
  uz: 'Har bir gʻoya bitta nuqtadan boshlanadi. Oʻzbekiston, shahar, choy.',
  'uz-cyr': 'Ҳар бир ғоя битта нуқтадан бошланади.',
  ru: 'Каждая идея начинается с одной точки.',
  en: 'Every idea starts from a single point.',
};

const outDir = fileURLToPath(new URL('../public/verify/', import.meta.url));
await mkdir(outDir, { recursive: true });
const status = await readStatus();
const only = process.argv[2]; // optional provider id filter

for (const g of await allVoices()) {
  if (only && g.provider.id !== only) continue;
  if (!g.ok) {
    console.log(`- ${g.provider.label}: oʻtkazib yuborildi (${g.reason})`);
    continue;
  }
  for (const v of g.voices) {
    const texts = v.lang === 'uz' ? [SAMPLES.uz, SAMPLES['uz-cyr']] : [SAMPLES[v.lang]];
    const base = outDir + v.key.replace(/[^a-zA-Z0-9_-]/g, '_');
    try {
      let secs = 0;
      for (const [i, t] of texts.entries()) {
        const r = await speak(t, v.key, base + (i ? '_cyr' : ''));
        const b = await speechBounds(r.wavPath);
        if (b.end - b.start < 0.8) throw new Error('nutq aniqlanmadi (audio boʻsh yoki juda qisqa)');
        secs += r.duration;
      }
      status[v.key] = { ok: true, testedAt: new Date().toISOString(), sample: 'verify/' + base.split('/').pop() + '.wav', seconds: +secs.toFixed(2) };
      console.log(`✓ ${v.label} [${v.key}] ${secs.toFixed(1)} s`);
    } catch (e) {
      const msg = String((e as Error).message).split('\n')[0].slice(0, 200);
      status[v.key] = { ok: false, testedAt: new Date().toISOString(), error: msg };
      console.log(`✗ ${v.label} [${v.key}] ${msg}`);
    }
  }
}
await writeStatus(status);
console.log('natija -> data/tts-status.json');
