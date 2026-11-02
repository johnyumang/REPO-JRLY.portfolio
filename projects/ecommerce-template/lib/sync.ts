// Background sync queue: actions taken offline are stored in the outbox and replayed in order when
// a connection is available. Each item's id is sent as the Idempotency-Key, so a replay whose
// response was lost can be retried safely without creating duplicates on the server.
import { nowIso, type AuditEntry, type OutboxItem, type TemplateDB } from './db';
import { uuid } from './crypto';

export type Send = (item: OutboxItem) => Promise<Response>;
export type ReplaySummary = { sent: number; failed: number; retried: number; skipped: number };

const BASE_DELAY = 2_000;
const MAX_DELAY = 5 * 60_000;
export const MAX_ATTEMPTS = 8;
export const backoff = (attempts: number) => Math.min(MAX_DELAY, BASE_DELAY * 2 ** Math.max(0, attempts - 1));

const audit = (db: TemplateDB, e: Omit<AuditEntry, 'at'>) => db.audit.add({ at: nowIso(), ...e });

export async function enqueue(db: TemplateDB, item: Pick<OutboxItem, 'type' | 'method' | 'path' | 'body'> & { id?: string }) {
  const row: OutboxItem = { id: item.id ?? uuid(), type: item.type, method: item.method, path: item.path, body: item.body, status: 'pending', attempts: 0, nextAttemptAt: 0, createdAt: nowIso() };
  // Same id enqueued twice (e.g. double-tap while offline) is a no-op.
  await db.transaction('rw', db.outbox, async () => { if (!(await db.outbox.get(row.id))) await db.outbox.add(row); });
  return (await db.outbox.get(row.id))!;
}

const retryable = (status: number) => status >= 500 || status === 408 || status === 429;

const running = new WeakMap<TemplateDB, Promise<ReplaySummary>>();

/** Replays due outbox items oldest-first. Concurrent calls share one run. */
export function replay(db: TemplateDB, send: Send, now = () => Date.now()): Promise<ReplaySummary> {
  const inflight = running.get(db);
  if (inflight) return inflight;
  const run = (async () => {
    const summary: ReplaySummary = { sent: 0, failed: 0, retried: 0, skipped: 0 };
    const items = await db.outbox.where('status').equals('pending').sortBy('createdAt');
    for (const item of items) {
      // Strict FIFO: if the oldest item isn't due yet, everything behind it waits too.
      if (item.nextAttemptAt > now()) { summary.skipped += items.length - items.indexOf(item); break; }
      let res: Response | undefined;
      let error: string | undefined;
      try { res = await send(item); } catch (e) { error = e instanceof Error ? e.message : String(e); }

      if (res && res.ok) {
        await db.outbox.delete(item.id);
        await audit(db, { entity: item.type, entityId: item.id, action: 'sync:sent', detail: { status: res.status } });
        summary.sent++;
      } else if (res && !retryable(res.status)) {
        await db.outbox.update(item.id, { status: 'failed', attempts: item.attempts + 1, lastError: `HTTP ${res.status}` });
        await audit(db, { entity: item.type, entityId: item.id, action: 'sync:failed', detail: { status: res.status } });
        summary.failed++;
      } else {
        const attempts = item.attempts + 1;
        const lastError = error ?? `HTTP ${res!.status}`;
        if (attempts >= MAX_ATTEMPTS) {
          await db.outbox.update(item.id, { status: 'failed', attempts, lastError });
          await audit(db, { entity: item.type, entityId: item.id, action: 'sync:gave-up', detail: { lastError } });
          summary.failed++;
        } else {
          await db.outbox.update(item.id, { attempts, lastError, nextAttemptAt: now() + backoff(attempts) });
          summary.retried++;
          // Keep order: later items wait until this one goes through.
          summary.skipped += items.length - items.indexOf(item) - 1;
          break;
        }
      }
    }
    return summary;
  })().finally(() => running.delete(db));
  running.set(db, run);
  return run;
}

/** Sends an outbox item to a live API at baseUrl with its Idempotency-Key. */
export const httpSender = (baseUrl: string, fetchImpl?: typeof fetch): Send => (item) =>
  (fetchImpl ?? globalThis.fetch)(new URL(item.path, baseUrl), {
    method: item.method,
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': item.id },
    body: item.body === undefined ? undefined : JSON.stringify(item.body),
  });

type Versioned = { updatedAt: string };
/** Last-write-wins merge. Ties keep the server copy. Every conflict is written to the audit log. */
export async function resolveConflict<T extends Versioned>(db: TemplateDB, entity: string, entityId: string, local: T, remote: T): Promise<T> {
  if (local.updatedAt === remote.updatedAt && JSON.stringify(local) === JSON.stringify(remote)) return remote;
  const winner = local.updatedAt > remote.updatedAt ? local : remote;
  await audit(db, { entity, entityId, action: 'sync:conflict', detail: { winner: winner === local ? 'local' : 'remote', local, remote } });
  return winner;
}

/** Browser wiring: replay on reconnect and on a timer while online. Returns a stop function. */
export function startAutoSync(db: TemplateDB, send: Send, intervalMs = 30_000) {
  const tick = () => { if (navigator.onLine) void replay(db, send).catch(() => {}); };
  window.addEventListener('online', tick);
  const timer = window.setInterval(tick, intervalMs);
  tick();
  return () => { window.removeEventListener('online', tick); window.clearInterval(timer); };
}
