// Yakuniy audiodan so'zma-so'z vaqtlar (ElevenLabs STT) → words.json: mashq pozalari aytilgan so'zga bog'lanadi.
import '/home/user/Loyha-/studio/server/net.ts';
import { readFile, writeFile } from 'node:fs/promises';
const fd = new FormData();
fd.append('model_id', 'scribe_v1'); fd.append('language_code', 'uzb'); fd.append('timestamps_granularity', 'word');
fd.append('file', new Blob([new Uint8Array(await readFile('/home/user/Loyha-/audio/badantarbiya/Badantarbiya_mashqi_AI_ovoz.mp3'))], { type: 'audio/mpeg' }), 'a.mp3');
const res = await fetch('https://api.elevenlabs.io/v1/speech-to-text', { method: 'POST', headers: { 'xi-api-key': process.env.ELEVENLABS_API_KEY!.trim() }, body: fd });
if (!res.ok) throw new Error(`STT ${res.status}`);
const j: any = await res.json();
const w = j.words.filter((x: any) => x.type === 'word').map((x: any) => [x.text, +x.start.toFixed(2), +x.end.toFixed(2)]);
await writeFile('/home/user/Loyha-/video/badantarbiya-2d/words.json', JSON.stringify(w));
console.log(w.map((x: any) => `${x[1]} ${x[0]}`).join(' | '));
