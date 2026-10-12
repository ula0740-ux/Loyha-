export type Format = '9:16' | '16:9' | '1:1';

export interface SceneWord {
  text: string;
  start: number; // seconds from scene start
  end: number;
}

export interface Scene {
  text: string;
  audio: string | null; // URL of the narration clip
  audioOffset: number; // seconds after scene start when narration begins (leaves room for the wipe)
  duration: number; // seconds the scene stays on screen (narration + padding)
  words: SceneWord[];
}

export interface VideoProps {
  [key: string]: unknown;
  format: Format;
  fps: number;
  theme: { bg: string; fg: string; accent: string; muted: string };
  title: string;
  scenes: Scene[];
}

export const SIZES: Record<Format, { width: number; height: number }> = {
  '9:16': { width: 1080, height: 1920 },
  '16:9': { width: 1920, height: 1080 },
  '1:1': { width: 1080, height: 1080 },
};

export const totalFrames = (p: Pick<VideoProps, 'scenes' | 'fps'>) =>
  Math.max(1, p.scenes.reduce((a, s) => a + Math.round(s.duration * p.fps), 0));
