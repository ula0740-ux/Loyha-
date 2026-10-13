// End-to-end: Uzbek text -> TTS -> Remotion MP4, then measure that speech in the MP4 starts where
// the first word appears on screen (A/V sync). Run with: npm run test:e2e [voiceKey]
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import type { AddressInfo } from 'node:net';
import { createApp } from '../server/app.ts';
import { narrate, renderVideo } from '../server/pipeline.ts';

const run = promisify(execFile);
const voice = process.argv[2] || 'espeak:uz+f3';
let port = 0;
const server = createApp(() => port).listen(0);
port = (server.address() as AddressInfo).port;
try {
  const { props } = await narrate('e2e', { scenes: ['Ҳар бир ғоя битта нуқтадан бошланади.', 'Kod bilan harakat.'], voice, format: '1:1' }, `http://localhost:${port}/media`, () => {});
  const file = await renderVideo('e2e', props, () => {});
  const { stdout } = await run('ffprobe', ['-v', 'error', '-show_entries', 'stream=codec_type:format=duration', '-of', 'csv=p=0', file]);
  assert.match(stdout, /video/);
  assert.match(stdout, /audio/);
  const expected = props.scenes.reduce((a, s) => a + Math.round(s.duration * 30), 0) / 30;
  const dur = Number(stdout.trim().split('\n').pop());
  assert.ok(Math.abs(dur - expected) < 0.15, `duration ${dur} vs ${expected}`);

  // speech onsets in the MP4 vs the first word time of each scene
  const { stderr } = await run('ffmpeg', ['-hide_banner', '-i', file, '-af', 'silencedetect=noise=-35dB:d=0.25', '-f', 'null', '-']);
  const onsets = [...stderr.matchAll(/silence_end: ([\d.]+)/g)].map((m) => Number(m[1]));
  let sceneStart = 0;
  for (const [i, s] of props.scenes.entries()) {
    const firstWord = sceneStart + s.words[0].start;
    const onset = onsets.find((o) => o > sceneStart - 0.05 && o < sceneStart + s.duration);
    assert.ok(onset !== undefined, `scene ${i + 1}: no speech found`);
    assert.ok(Math.abs(onset! - firstWord) < 0.2, `scene ${i + 1}: speech at ${onset}s, first word at ${firstWord.toFixed(2)}s`);
    console.log(`sahna ${i + 1}: nutq ${onset!.toFixed(2)}s, birinchi soʻz ${firstWord.toFixed(2)}s ✓`);
    sceneStart += Math.round(s.duration * 30) / 30;
  }
  console.log('E2E OK:', file, dur.toFixed(2) + 's');
} finally {
  server.close();
}
