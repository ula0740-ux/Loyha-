import React from 'react';
import { Composition } from 'remotion';
import { MotionVideo } from './Video';
import { SIZES, totalFrames, type VideoProps } from './types';
import { demoProps } from './demo';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="MotionVideo"
    component={MotionVideo}
    defaultProps={demoProps}
    fps={30}
    width={1080}
    height={1920}
    durationInFrames={totalFrames(demoProps)}
    calculateMetadata={({ props }: { props: VideoProps }) => ({
      durationInFrames: totalFrames(props),
      fps: props.fps,
      ...SIZES[props.format],
    })}
  />
);
