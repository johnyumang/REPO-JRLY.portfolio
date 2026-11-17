import React from 'react';
import {Composition} from 'remotion';
import {Episode, Manifest, totalFrames} from './Episode';

const EMPTY: Manifest = {fps: 30, width: 1920, height: 1080, audio: null, lines: [], shots: []};

export const Root: React.FC = () => (
  <Composition
    id="Episode"
    component={Episode}
    defaultProps={{manifest: EMPTY}}
    durationInFrames={30}
    fps={30}
    width={1920}
    height={1080}
    calculateMetadata={({props}) => {
      const m = props.manifest;
      return {durationInFrames: Math.max(1, totalFrames(m)), fps: m.fps || 30, width: m.width || 1920, height: m.height || 1080};
    }}
  />
);
