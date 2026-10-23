// "Endi chapga!" yolg'iz yozilganda STT uni ingliz/hind tili deb o'qidi; shu sababli sanoq bilan birga yoziladi
// ("... To'rt! Endi chapga!"), STT butun gapni tekshiradi, ishora o'sha yozuvdan kesib olinadi.
import '/home/user/Loyha-/studio/server/net.ts';
import { synth, transcribe, normForCompare } from '/home/user/Loyha-/studio/server/uz/eleven.ts';
import { readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
const O = '/home/user/Loyha-/audio/badantarbiya/murabbiy/', VS = { stability: .3, similarity_boost: .75, style: .6, use_speaker_boost: true };
const man = JSON.parse(await readFile(O + 'manifest.json', 'utf8'));
for (let k = 0; k < 6; k++) {
  const s = await synth('[excited] Uch! Toʻrt! Endi chapga!', { voice: 'EXAVITQu4vr4xnSDxMaL', model: 'eleven_v4', voiceSettings: VS });
  const w = s.words.filter((x) => !x.text.startsWith('[')), heard = normForCompare(await transcribe(s.mp3));
  console.log(`#${k + 1} ${heard} | ${w.map((x) => x.text + '@' + x.start.toFixed(2)).join(' ')}`);
  if (!/endi chapga/.test(heard) || w.length !== 4) continue;
  await writeFile('/tmp/cue_raw.mp3', s.mp3);
  const a = Math.max(0, w[2].start - .05), b = w[3].end + .2;
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', '/tmp/cue_raw.mp3', '-af', `atrim=${a.toFixed(3)}:${b.toFixed(3)},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=${(b - a - .05).toFixed(3)}:d=0.05`, '-b:a', '192k', O + 'cues/chapga.mp3']);
  man.cues.chapga = { file: 'cues/chapga.mp3', from: 'Uch! Toʻrt! Endi chapga!' }; await writeFile(O + 'manifest.json', JSON.stringify(man, null, 1));
  console.log('✓ chapga', (b - a).toFixed(2), 's'); break;
}
