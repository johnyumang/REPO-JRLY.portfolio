// The episode manifest: the same JSON the local pipeline (pipeline/animate) reads and writes.
export type ProviderId = 'wan-free' | 'minimax';

export type Take = {
  id: string;
  provider: ProviderId;
  status: 'queued' | 'running' | 'done' | 'failed' | 'interrupted';
  taskId?: string;
  url?: string;
  duration?: number;
  error?: string;
  note?: string;
  startedAt: number;
  errors?: number;
};

export type Shot = {
  id: string;
  still?: string;
  image: string;
  prompt: string;
  negative?: string;
  duration: number;
  start?: number;
  end?: number;
  lines?: number[];
  shout?: boolean;
  trans_in?: 'cut' | 'fade';
  caption?: 'bottom' | 'top';
  provider: ProviderId;
  takes: Take[];
  chosen?: string | null;
  clip?: string | null;
  clip_duration?: number | null;
  warning?: string;
  [k: string]: unknown;
};

export type Line = {i: number; text: string; speaker: string; style: string; start: number; end: number};

export type Manifest = {
  version: 1;
  episode: string;
  fps: number;
  width: number;
  height: number;
  audio: string | null;
  lines: Line[];
  shots: Shot[];
  [k: string]: unknown;
};

export const emptyManifest = (): Manifest => ({
  version: 1, episode: 'untitled', fps: 30, width: 1920, height: 1080, audio: 'voice.wav', lines: [], shots: [],
});

export const newShot = (n: number): Shot => ({
  id: 's' + String(n).padStart(2, '0'), image: '', prompt: '', duration: 3.5, provider: 'wan-free', takes: [], chosen: null,
});

/** Accepts a manifest from motion.py / an earlier export, or a bare list of shots. Throws with a plain message. */
export function parseManifest(text: string): Manifest {
  const raw = JSON.parse(text);
  const base = emptyManifest();
  const src = Array.isArray(raw) ? {shots: raw} : raw;
  if (!src || !Array.isArray(src.shots)) throw new Error('No "shots" list found.');
  const shots: Shot[] = src.shots.map((s: Record<string, unknown>, i: number) => {
    const shot: Shot = {
      ...newShot(i),
      ...s,
      id: String(s.id ?? 's' + String(i).padStart(2, '0')),
      image: String(s.image ?? s.image_url ?? ''),
      prompt: String(s.prompt ?? s.motion ?? ''),
      duration: Number(s.duration ?? 3.5),
      provider: s.provider === 'minimax' ? 'minimax' : 'wan-free',
      takes: Array.isArray(s.takes) ? (s.takes as Take[]).filter((t) => t && typeof t === 'object' && 'status' in t) : [],
    };
    // a take that was running when the page closed cannot be resumed for the browser provider
    shot.takes = shot.takes.map((t) => (t.provider === 'wan-free' && (t.status === 'running' || t.status === 'queued')
      ? {...t, status: 'interrupted' as const} : t));
    if (s.clip && typeof s.clip === 'string' && /^https?:/.test(s.clip) && !shot.takes.some((t) => t.url === s.clip)) {
      const t: Take = {id: 'imported', provider: shot.provider, status: 'done', url: s.clip, startedAt: Date.now(),
        duration: typeof s.clip_duration === 'number' ? s.clip_duration : undefined};
      shot.takes.push(t);
      shot.chosen = t.id;
    }
    return shot;
  });
  return {...base, ...src, version: 1, shots, lines: Array.isArray(src.lines) ? src.lines : []};
}

/** The final manifest: each shot's picked take becomes its clip. Takes stay listed for the record. */
export function exportManifest(m: Manifest): Manifest {
  return {
    ...m,
    exported_at: new Date().toISOString(),
    shots: m.shots.map((s) => {
      const t = s.takes.find((x) => x.id === s.chosen && x.status === 'done');
      const image = s.image.startsWith('data:') ? '(uploaded in the studio)' : s.image;
      return {...s, image, clip: t?.url ?? null, clip_duration: t?.duration ?? null, provider: t?.provider ?? s.provider};
    }),
  };
}
