import React from 'react';
import { AbsoluteFill, Audio, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from 'remotion';
import type { Scene, VideoProps } from './types';

const FONT = '"Inter Display", Inter, "Noto Sans", system-ui, sans-serif';

/** One narrated scene: a colour wipe opens it, each word rises in exactly when it is spoken. */
const SceneView: React.FC<{ scene: Scene; index: number; props: VideoProps }> = ({ scene, index, props }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const t = frame / fps;
  const { theme } = props;
  const portrait = height > width;
  const base = Math.min(width, height);
  const fontSize = Math.round(base * (scene.text.length > 90 ? 0.075 : scene.text.length > 45 ? 0.095 : 0.125));

  // wipe: a solid accent panel crosses the frame in ~0.5 s
  const wipe = spring({ frame, fps, config: { damping: 200, stiffness: 120 }, durationInFrames: Math.round(fps * 0.55) });
    const exit = interpolate(frame, [durationInFrames - fps * 0.35, durationInFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic) });

  // which word is being spoken right now (for the highlight)
  const current = scene.words.findIndex((w) => t >= w.start && t < w.end + 0.05);

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg, fontFamily: FONT }}>
      {/* solid accent panel sweeps across and leaves: reveals the new scene */}
      <div
        style={{
          position: 'absolute', top: 0, height, width: width * 1.2, background: theme.accent,
          left: interpolate(wipe, [0, 1], [index % 2 ? -width * 1.2 : 0, index % 2 ? width : -width * 1.2]),
          transform: `skewX(${index % 2 ? -8 : 8}deg)`,
          display: frame < fps * 0.6 ? 'block' : 'none',
        }}
      />
      <div style={{ position: 'absolute', left: base * 0.08, top: base * 0.08, display: 'flex', gap: base * 0.012, alignItems: 'center' }}>
        {props.scenes.map((_, i) => (
          <div key={i} style={{ width: i === index ? base * 0.05 : base * 0.014, height: base * 0.014, borderRadius: base, background: i <= index ? theme.accent : theme.muted }} />
        ))}
      </div>
      <AbsoluteFill
        style={{
          justifyContent: 'center', alignItems: portrait ? 'flex-start' : 'center', flexDirection: 'column',
          padding: `0 ${base * 0.08}px`, transform: `translateY(${-exit * base * 0.06}px)`, opacity: 1 - exit,
        }}
      >
        <div style={{ display: 'flex', flexWrap: 'wrap', columnGap: fontSize * 0.28, rowGap: fontSize * 0.1, maxWidth: width - base * 0.16, justifyContent: portrait ? 'flex-start' : 'center' }}>
          {scene.words.map((w, i) => {
            const f = Math.round(w.start * fps);
            const p = spring({ frame: frame - f + 2, fps, config: { damping: 18, stiffness: 170, mass: 0.8 } });
            const spoken = t >= w.start;
            return (
              <span key={i} style={{ display: 'inline-block', overflow: 'hidden', paddingBottom: fontSize * 0.08, lineHeight: 1.08 }}>
                <span
                  style={{
                    display: 'inline-block', fontSize, fontWeight: 700, letterSpacing: '-0.03em',
                    color: i === current ? theme.accent : spoken ? theme.fg : theme.muted,
                    opacity: spoken ? 1 : 0.0,
                    transform: `translateY(${(1 - p) * 105}%) rotate(${(1 - p) * 4}deg)`,
                  }}
                >
                  {w.text}
                </span>
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
      {scene.audio ? (
        <Sequence from={Math.round(scene.audioOffset * fps)} layout="none">
          <Audio src={scene.audio} />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};

export const MotionVideo: React.FC<VideoProps> = (props) => {
  const { fps, width, height } = useVideoConfig();
  const frame = useCurrentFrame();
  const base = Math.min(width, height);
  let from = 0;
  const total = props.scenes.reduce((a, s) => a + Math.round(s.duration * fps), 0);
  return (
    <AbsoluteFill style={{ backgroundColor: props.theme.bg }}>
      {props.scenes.map((s, i) => {
        const dur = Math.max(1, Math.round(s.duration * fps));
        const el = (
          <Sequence key={i} from={from} durationInFrames={dur} name={`Sahna ${i + 1}`}>
            <SceneView scene={s} index={i} props={props} />
          </Sequence>
        );
        from += dur;
        return el;
      })}
      {props.title ? (
        <div style={{ position: 'absolute', right: base * 0.08, top: base * 0.07, fontFamily: FONT, fontSize: base * 0.032, fontWeight: 600, color: props.theme.muted }}>
          {props.title}
        </div>
      ) : null}
      <div style={{ position: 'absolute', left: 0, bottom: 0, height: base * 0.008, width: `${(frame / Math.max(1, total)) * 100}%`, background: props.theme.accent }} />
    </AbsoluteFill>
  );
};
