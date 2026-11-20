// MiniMax image-to-video, server side only. The key comes only from env MINIMAX_API_KEY.
//
// UNVERIFIED: the official docs host could not be reached when this was written. The request and response shapes
// below follow the documented three-step flow as seen in search results and in a third-party client:
//   1. POST {host}/v1/video_generation   body {model, prompt, first_frame_image, duration, resolution, prompt_optimizer}
//        -> {task_id, base_resp: {status_code, status_msg}}        (first_frame_image: public URL or data: URL)
//   2. GET  {host}/v1/query/video_generation?task_id=ID
//        -> {task_id, status: 'Preparing'|'Queueing'|'Processing'|'Success'|'Fail', file_id, base_resp}
//   3. GET  {host}/v1/files/retrieve?file_id=ID
//        -> {file: {file_id, download_url, ...}, base_resp}           (download_url expires; save the clip soon)
// All of it is in this one file: if MiniMax changes a field, change it here only.

const HOST = () => (process.env.MINIMAX_API_HOST || 'https://api.minimax.io').replace(/\/+$/, '');
const MODEL = () => process.env.MINIMAX_MODEL || 'MiniMax-Hailuo-02';
const RESOLUTION = () => process.env.MINIMAX_RESOLUTION || '768P';

export const minimaxConfigured = () => Boolean(process.env.MINIMAX_API_KEY);

type BaseResp = {status_code?: number; status_msg?: string};

async function call<T extends {base_resp?: BaseResp}>(path: string, body?: unknown): Promise<T> {
  const key = process.env.MINIMAX_API_KEY;
  if (!key) throw new Error('MINIMAX_API_KEY is not set for this deployment.');
  const res = await fetch(HOST() + path, {
    method: body ? 'POST' : 'GET',
    headers: {Authorization: `Bearer ${key}`, 'Content-Type': 'application/json'},
    body: body ? JSON.stringify(body) : undefined,
    cache: 'no-store',
    signal: AbortSignal.timeout(20000),
  });
  const text = await res.text();
  let json: T;
  try {
    json = JSON.parse(text) as T;
  } catch {
    throw new Error(`MiniMax HTTP ${res.status}: ${text.slice(0, 200)}`);
  }
  if (!res.ok) throw new Error(`MiniMax HTTP ${res.status}: ${json.base_resp?.status_msg || text.slice(0, 200)}`);
  if (json.base_resp && json.base_resp.status_code && json.base_resp.status_code !== 0) {
    throw new Error(`MiniMax error ${json.base_resp.status_code}: ${json.base_resp.status_msg || ''}`);
  }
  return json;
}

export type CreateInput = {image: string; prompt: string; duration: number};

/** Starts a task and returns its id at once (no waiting inside the function). */
export async function createTask(input: CreateInput): Promise<string> {
  const r = await call<{task_id?: string; base_resp?: BaseResp}>('/v1/video_generation', {
    model: MODEL(),
    prompt: input.prompt.slice(0, 2000),
    first_frame_image: input.image,
    duration: input.duration > 6 ? 10 : 6,
    resolution: RESOLUTION(),
    prompt_optimizer: false,
  });
  if (!r.task_id) throw new Error('MiniMax returned no task id.');
  return String(r.task_id);
}

export type TaskState = {status: 'queued' | 'running' | 'done' | 'failed'; videoUrl?: string; error?: string; raw?: string};

/** One status check (plus the file lookup once it is done). Fast; the browser calls it every few seconds. */
export async function queryTask(taskId: string): Promise<TaskState> {
  const q = await call<{status?: string; file_id?: string | number; base_resp?: BaseResp}>(
    `/v1/query/video_generation?task_id=${encodeURIComponent(taskId)}`);
  const s = q.status || '';
  if (s === 'Success') {
    if (!q.file_id) return {status: 'failed', error: 'finished without a file id', raw: s};
    const f = await call<{file?: {download_url?: string}; base_resp?: BaseResp}>(
      `/v1/files/retrieve?file_id=${encodeURIComponent(String(q.file_id))}`);
    const url = f.file?.download_url;
    return url ? {status: 'done', videoUrl: url, raw: s} : {status: 'failed', error: 'no download url', raw: s};
  }
  if (s === 'Fail') return {status: 'failed', error: 'MiniMax reported the task failed', raw: s};
  if (s === 'Processing') return {status: 'running', raw: s};
  return {status: 'queued', raw: s};
}
