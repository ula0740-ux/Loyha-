// End-to-end check without the UI: narrate a few scenes and render an MP4.
// usage: npm run render-demo -- [voiceKey] [format]
import type { AddressInfo } from 'node:net';
import { createApp } from '../server/app.ts';
import { narrate, renderVideo } from '../server/pipeline.ts';
import type { Format } from '../src/types.ts';

const voice = process.argv[2] || 'espeak:uz+f3';
const format = (process.argv[3] || '9:16') as Format;
const scenes = ['Har bir gʻoya bitta nuqtadan boshlanadi.', 'Kod bilan harakat.', 'Gʻoyadan videogacha.'];

let port = 0;
const server = createApp(() => port).listen(0);
port = (server.address() as AddressInfo).port;
const log = (stage: string, p: number) => process.stdout.write(`\r${stage} ${(p * 100).toFixed(0)}%      `);
try {
  const id = `demo-${voice.replace(/[^a-z0-9]/gi, '_')}-${format.replace(':', 'x')}`;
  const { props, timing } = await narrate(id, { scenes, voice, format, title: 'Loyha' }, `http://localhost:${port}/media`, log);
  console.log('\nsahnalar:', props.scenes.map((s) => s.duration.toFixed(2) + 's').join(', '), '| vaqt:', timing.join(','));
  const file = await renderVideo(id, props, log);
  console.log('\nMP4 ->', file);
} finally {
  server.close();
}
