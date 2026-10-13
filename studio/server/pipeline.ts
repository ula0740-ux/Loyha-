import { copyFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { speak } from './tts/index.ts';
import type { Format, Scene, VideoProps } from '../src/types.ts';

export const ROOT = fileURLToPath(new URL('..', import.meta.url));
export const MEDIA_DIR = join(ROOT, 'media');
export const OUT_DIR = join(ROOT, 'out');

const LEAD = 0.45; // narration starts after the opening wipe
const TAIL = 0.65; // breathing room after the last word

export interface JobInput {
  scenes: string[];
  voice: string;
  format: Format;
  title?: string;
  theme?: Partial<VideoProps['theme']>;
}
export type Progress = (stage: string, value: number) => void;

let bundled: Promise<string> | null = null;
export const getBundle = () =>
  (bundled ??= bundle({ entryPoint: join(ROOT, 'src/index.ts'), onProgress: () => undefined }));

/** A headless Chromium we can use without downloading one (Remotion's own download host may be blocked). */
export function browserExecutable(): string | null {
  if (process.env.REMOTION_BROWSER && existsSync(process.env.REMOTION_BROWSER)) return process.env.REMOTION_BROWSER;
  const candidates = ['/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'];
  return candidates.find((c) => existsSync(c)) ?? null;
}

/** Text -> narration clips -> scene timings. Each scene lasts exactly as long as its narration (+ lead/tail). */
export async function narrate(jobId: string, input: JobInput, mediaBaseUrl: string, progress: Progress): Promise<{ props: VideoProps; timing: string[] }> {
  const dir = join(MEDIA_DIR, jobId);
  await mkdir(dir, { recursive: true });
  const scenes: Scene[] = [];
  const timing: string[] = [];
  for (const [i, text] of input.scenes.entries()) {
    progress(`Ovoz: sahna ${i + 1}/${input.scenes.length}`, i / input.scenes.length);
    const r = await speak(text, input.voice, join(dir, `scene${i}`));
    await copyFile(r.wavPath, join(dir, `scene${i}.final.wav`));
    timing.push(r.timing);
    scenes.push({
      text,
      audio: `${mediaBaseUrl}/${jobId}/scene${i}.final.wav`,
      audioOffset: LEAD,
      duration: Math.max(2, LEAD + r.duration + TAIL),
      words: r.words.map((w) => ({ text: w.text, start: w.start + LEAD, end: w.end + LEAD })),
    });
  }
  const props: VideoProps = {
    format: input.format,
    fps: 30,
    title: input.title ?? '',
    theme: { bg: '#0b0b0c', fg: '#f5f5f2', accent: '#cdf24f', muted: '#3a3a3f', ...input.theme },
    scenes,
  };
  return { props, timing };
}

export async function renderVideo(jobId: string, props: VideoProps, progress: Progress): Promise<string> {
  progress('Remotion: tayyorlanmoqda', 0);
  const serveUrl = await getBundle();
  const exe = browserExecutable();
  const composition = await selectComposition({ serveUrl, id: 'MotionVideo', inputProps: props, logLevel: 'error', ...(exe ? { browserExecutable: exe } : {}) });
  await mkdir(OUT_DIR, { recursive: true });
  const outputLocation = join(OUT_DIR, `${jobId}.mp4`);
  await renderMedia({
    serveUrl,
    composition,
    inputProps: props,
    codec: 'h264',
    logLevel: 'error',
    outputLocation,
    ...(exe ? { browserExecutable: exe } : {}),
    onProgress: ({ progress: p }) => progress('Remotion: render', p),
  });
  return outputLocation;
}
