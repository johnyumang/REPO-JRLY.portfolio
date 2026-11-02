// One fetch function for the whole app. DATA_MODE=offline (default) routes requests through the MSW
// handlers in-page against IndexedDB, with no network and no extra service worker. DATA_MODE=live
// sends them to NEXT_PUBLIC_API_URL; queueable writes that fail on the network go to the outbox.
import { getResponse } from 'msw';
import { getDB } from '../db';
import { enqueue } from '../sync';
import { uuid } from '../crypto';
import { createHandlers } from './handlers';

export const DATA_MODE = (process.env.NEXT_PUBLIC_DATA_MODE ?? 'offline') as 'offline' | 'live';
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

let handlers: ReturnType<typeof createHandlers> | undefined;
const origin = () => (typeof location !== 'undefined' ? location.origin : 'http://localhost');

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  if (DATA_MODE === 'offline') {
    const req = new Request(new URL(path, origin()), init);
    return (await getResponse((handlers ??= createHandlers(getDB)), req)) ?? Response.json({ error: 'Not found' }, { status: 404 });
  }
  return fetch(new URL(path, API_URL || origin()), init);
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, { ...init, headers: { 'Content-Type': 'application/json', ...init.headers } });
  if (!res.ok) throw Object.assign(new Error((await res.json().catch(() => ({})))?.error ?? `HTTP ${res.status}`), { status: res.status });
  return res.status === 204 ? (undefined as T) : res.json();
}

type Queueable = { type: 'order' | 'ticket' | 'newsletter'; path: string; body: unknown };
/** POST a write that must survive being offline. Returns the response, or { queued: true }. */
export async function submit<T>({ type, path, body }: Queueable): Promise<T | { queued: true; id: string }> {
  const id = uuid();
  try {
    return await api<T>(path, { method: 'POST', body: JSON.stringify(body), headers: { 'Idempotency-Key': id } });
  } catch (e) {
    const status = (e as { status?: number }).status;
    if (DATA_MODE === 'live' && (status === undefined || status >= 500)) {
      await enqueue(getDB(), { id, type, method: 'POST', path, body });
      return { queued: true, id };
    }
    throw e;
  }
}
