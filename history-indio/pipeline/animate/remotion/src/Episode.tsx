import React from 'react';
import {
  AbsoluteFill, Audio, Freeze, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';

// The manifest written by motion.py / i2v.py or exported from the studio. Times are seconds on the voice track.
export type Line = {i: number; text: string; speaker: string; style: string; start: number; end: number};
export type Shot = {
  id: string; clip: string | null; clip_duration?: number | null; start: number; end: number;
  shout?: boolean; trans_in?: 'cut' | 'fade'; caption?: 'bottom' | 'top';
};
export type Manifest = {fps: number; width: number; height: number; audio: string | null; lines: Line[]; shots: Shot[]};

const NARRATOR = new Set(['TAGAPAGSALAYSAY', 'NARRATOR']);
const t0 = (m: Manifest) => (m.shots.length ? m.shots[0].start : 0);
const fr = (m: Manifest, s: number) => Math.round((s - t0(m)) * (m.fps || 30));
export const totalFrames = (m: Manifest) => (m.shots.length ? fr(m, m.shots[m.shots.length - 1].end) : 30);
const isUrl = (s: string) => /^https?:\/\//.test(s);
const src = (s: string) => (isUrl(s) ? s : staticFile(s));

const fontFace = `
@font-face{font-family:Anton;src:url(${staticFile('fonts/Anton-Regular.ttf')})}
@font-face{font-family:Bebas;src:url(${staticFile('fonts/BebasNeue-Regular.ttf')})}`;

// Kinetic caption: yellow uppercase words with a black outline, speaker label above. Shouts slam in, others pop.
const Caption: React.FC<{line: Line; durFrames: number; place: 'bottom' | 'top'}> = ({line, durFrames, place}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const shout = line.style === 'shout';
  const words = line.text.toUpperCase().split(/\s+/);
  const per = shout ? durFrames / words.length : Math.min(durFrames / words.length, 6);
  const out = interpolate(frame, [durFrames + 6, durFrames + 12], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lab = spring({frame, fps, config: {damping: 200}, durationInFrames: 8});
  const label = NARRATOR.has(line.speaker) ? '' : line.speaker;
  return (
    <AbsoluteFill style={{
      justifyContent: place === 'top' ? 'flex-start' : 'flex-end', alignItems: 'center', opacity: out,
      paddingBottom: place === 'top' ? 0 : 60, paddingTop: place === 'top' ? 120 : 0,
    }}>
      {label ? (
        <div style={{fontFamily: 'Bebas', fontSize: 40, letterSpacing: 4, color: '#fff', background: 'rgba(0,0,0,0.6)',
          padding: '2px 16px', borderRadius: 4, marginBottom: 8, opacity: lab, transform: `translateY(${(1 - lab) * 10}px)`}}>
          {label}
        </div>
      ) : null}
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', maxWidth: 1500, gap: '0 22px'}}>
        {words.map((w, i) => {
          const s = spring({frame: frame - i * per, fps,
            config: shout ? {damping: 8, stiffness: 260, mass: 0.6} : {damping: 14, stiffness: 180}});
          const scale = shout ? interpolate(s, [0, 1], [2.2, 1]) : interpolate(s, [0, 1], [0.6, 1]);
          return (
            <span key={i} style={{fontFamily: 'Anton', fontSize: shout ? 100 : 76, lineHeight: 1.12, color: '#FFD400',
              WebkitTextStroke: shout ? '7px #000' : '6px #000', paintOrder: 'stroke fill',
              textShadow: '0 6px 0 #000, 0 0 18px rgba(0,0,0,0.6)', display: 'inline-block',
              opacity: Math.min(1, s * 1.5), transform: `scale(${scale}) rotate(${shout ? (i % 2 ? 2 : -2) * (1 - s) : 0}deg)`}}>
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// One shot = one clip, hard cut in and out. A clip shorter than its shot is slowed (to half speed at most), then
// holds its last frame. Shake only for the first frames of a shout.
const ShotView: React.FC<{shot: Shot; len: number; shakeAt: number[]}> = ({shot, len, shakeAt}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!shot.clip) return <AbsoluteFill style={{background: '#111'}} />;
  const clipFrames = Math.max(1, Math.floor((shot.clip_duration || len / fps) * fps));
  const rate = Math.min(1, Math.max(0.5, clipFrames / len));
  const playable = Math.max(1, Math.floor(clipFrames / rate) - 2);
  let tx = 0, ty = 0, sc = 1.0;
  for (const s of shakeAt) {
    const k = interpolate(frame - s, [0, 14], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    if (frame >= s && k > 0) {
      tx += Math.sin(frame * 2.7) * 16 * k; ty += Math.cos(frame * 3.3) * 12 * k; sc = 1.04;
    }
  }
  const video = <OffthreadVideo src={src(shot.clip)} muted playbackRate={rate} style={{width: '100%', height: '100%', objectFit: 'cover'}} />;
  return (
    <AbsoluteFill style={{transform: `translate(${tx}px,${ty}px) scale(${sc})`}}>
      {frame < playable ? video : <Freeze frame={playable - 1}>{video}</Freeze>}
    </AbsoluteFill>
  );
};

const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 5], [0.9, 0], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: '#fff4d6', opacity: o}} />;
};

// Dip to black for a change of time or place (never a cross-dissolve between pictures of people).
const Dip: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 8, 16], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: '#000', opacity: o}} />;
};

const Logo: React.FC = () => (
  <div style={{position: 'absolute', left: 48, top: 40, fontFamily: 'Bebas', fontSize: 44, letterSpacing: 5, color: '#fff',
    textShadow: '0 2px 6px rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', gap: 12, opacity: 0.92}}>
    <span style={{width: 10, height: 36, background: '#d62828', display: 'inline-block'}} />
    HISTORY <span style={{color: '#FFD400'}}>INDIO</span>
  </div>
);

export const Episode: React.FC<{manifest: Manifest}> = ({manifest: m}) => {
  const fps = m.fps || 30;
  const shotAt = (t: number) => m.shots.find((s) => t >= s.start && t < s.end) || m.shots[m.shots.length - 1];
  const shouts = m.lines.filter((l) => l.style === 'shout');
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <style>{fontFace}</style>
      {m.shots.map((s) => {
        const from = fr(m, s.start), len = fr(m, s.end) - from;
        const shakeAt = shouts.filter((l) => l.start >= s.start && l.start < s.end).map((l) => fr(m, l.start) - from);
        return (
          <Sequence key={s.id} from={from} durationInFrames={len}>
            <ShotView shot={s} len={len} shakeAt={shakeAt} />
          </Sequence>
        );
      })}
      {m.shots.map((s, i) => (i > 0 && s.trans_in === 'fade' ? (
        <Sequence key={'dip' + s.id} from={fr(m, s.start) - 8} durationInFrames={16}><Dip /></Sequence>
      ) : null))}
      {shouts.map((l) => (
        <Sequence key={'fl' + l.i} from={fr(m, l.start)} durationInFrames={6}><Flash /></Sequence>
      ))}
      <AbsoluteFill style={{background: 'linear-gradient(to top, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 30%)'}} />
      {m.lines.map((l) => {
        const from = Math.max(0, fr(m, l.start)), dur = fr(m, l.end) - from;
        return (
          <Sequence key={'c' + l.i} from={from} durationInFrames={dur + 12}>
            <Caption line={l} durFrames={dur} place={shotAt(l.start)?.caption === 'top' ? 'top' : 'bottom'} />
          </Sequence>
        );
      })}
      <Logo />
      {m.audio ? <Audio src={src(m.audio)} startFrom={Math.round(t0(m) * fps)} /> : null}
    </AbsoluteFill>
  );
};
