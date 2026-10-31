import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import type { OutboxItem, TemplateDB } from '@/lib/db';
import { backoff, enqueue, httpSender, MAX_ATTEMPTS, replay, resolveConflict } from '@/lib/sync';
import { BASE, freshDb, mockServer } from './helpers';

const order = { email: 'offline@example.com', lines: [{ slug: 'essential-white-tee', color: 'White', size: 'M', qty: 1 }] };
const ticket = { email: 'offline@example.com', subject: 'Offline ticket', message: 'Sent while the network was down.' };

let local: TemplateDB;
beforeEach(async () => { local = await freshDb(false); });

describe('enqueue', () => {
  it('stores pending items and ignores a duplicate id', async () => {
    await enqueue(local, { id: 'a', type: 'order', method: 'POST', path: '/api/orders', body: order });
    await enqueue(local, { id: 'a', type: 'order', method: 'POST', path: '/api/orders', body: order });
    const items = await local.outbox.toArray();
    expect(items.length).toBe(1);
    expect(items[0]).toMatchObject({ status: 'pending', attempts: 0 });
  });
});

describe('replay against the mock live API', () => {
  const { server, ctx } = mockServer();
  let remote: TemplateDB;
  beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
  afterAll(() => server.close());
  beforeEach(async () => { remote = ctx.db = await freshDb(); });
  const send = httpSender(BASE);

  it('sends queued order, ticket and newsletter, then empties the outbox', async () => {
    await enqueue(local, { type: 'order', method: 'POST', path: '/api/orders', body: order });
    await enqueue(local, { type: 'ticket', method: 'POST', path: '/api/tickets', body: ticket });
    await enqueue(local, { type: 'newsletter', method: 'POST', path: '/api/newsletter', body: { email: 'offline@example.com' } });
    expect(await replay(local, send)).toEqual({ sent: 3, failed: 0, retried: 0, skipped: 0 });
    expect(await local.outbox.count()).toBe(0);
    expect((await remote.orders.toArray()).filter((o) => o.email === 'offline@example.com').length).toBe(1);
    expect(await remote.tickets.count()).toBe(1);
    expect(await remote.newsletter.count()).toBe(1);
    expect(await local.audit.where('action').equals('sync:sent').count()).toBe(3);
  });

  it('does not duplicate when the response is lost and the item is replayed again', async () => {
    const item = await enqueue(local, { type: 'order', method: 'POST', path: '/api/orders', body: order });
    // Server processes the request but the client never sees the response.
    let first = true;
    const lossy = async (i: OutboxItem) => { const res = await send(i); if (first) { first = false; throw new Error('connection reset'); } return res; };
    expect((await replay(local, lossy)).retried).toBe(1);
    expect(await local.outbox.count()).toBe(1);
    expect(await replay(local, lossy, () => Date.now() + backoff(1) + 1)).toMatchObject({ sent: 1 });
    expect(await remote.orders.where('idempotencyKey').equals(item.id).count()).toBe(1);
  });

  it('replaying the same outbox concurrently sends each item once', async () => {
    await enqueue(local, { type: 'order', method: 'POST', path: '/api/orders', body: order });
    let calls = 0;
    const counting = (i: OutboxItem) => { calls++; return send(i); };
    const [a, b] = await Promise.all([replay(local, counting), replay(local, counting)]);
    expect(a).toBe(b);
    expect(calls).toBe(1);
  });
});

describe('replay failure handling', () => {
  const respond = (status: number) => async () => new Response(null, { status });

  it('retries 5xx with exponential backoff and keeps later items in order', async () => {
    await enqueue(local, { id: 'first', type: 'order', method: 'POST', path: '/x', body: {} });
    await new Promise((r) => setTimeout(r, 2));
    await enqueue(local, { id: 'second', type: 'ticket', method: 'POST', path: '/y', body: {} });
    const sent: string[] = [];
    const flaky = async (i: OutboxItem) => { sent.push(i.id); return new Response(null, { status: 503 }); };
    const t0 = 1_000_000;
    expect(await replay(local, flaky, () => t0)).toEqual({ sent: 0, failed: 0, retried: 1, skipped: 1 });
    expect(sent).toEqual(['first']);
    const first = (await local.outbox.get('first'))!;
    expect(first).toMatchObject({ attempts: 1, lastError: 'HTTP 503', nextAttemptAt: t0 + backoff(1) });
    // Not due yet: nothing is sent.
    expect((await replay(local, flaky, () => t0 + 1)).skipped).toBe(2);
    expect(sent.length).toBe(1);
  });

  it('backoff doubles and caps at 5 minutes', () => {
    expect([1, 2, 3, 4].map(backoff)).toEqual([2000, 4000, 8000, 16000]);
    expect(backoff(30)).toBe(300_000);
  });

  it('marks 4xx as failed without retrying, and moves on to the next item', async () => {
    await enqueue(local, { id: 'bad', type: 'order', method: 'POST', path: '/x', body: {} });
    await new Promise((r) => setTimeout(r, 2));
    await enqueue(local, { id: 'good', type: 'ticket', method: 'POST', path: '/y', body: {} });
    const send = async (i: OutboxItem) => new Response(null, { status: i.id === 'bad' ? 400 : 201 });
    expect(await replay(local, send)).toEqual({ sent: 1, failed: 1, retried: 0, skipped: 0 });
    expect(await local.outbox.get('bad')).toMatchObject({ status: 'failed', lastError: 'HTTP 400' });
    expect(await local.outbox.get('good')).toBeUndefined();
    expect((await replay(local, send)).sent).toBe(0); // failed items are not retried
  });

  it('treats 408 and 429 as retryable', async () => {
    for (const status of [408, 429]) {
      const db = await freshDb(false);
      await enqueue(db, { type: 'order', method: 'POST', path: '/x', body: {} });
      expect((await replay(db, respond(status))).retried).toBe(1);
    }
  });

  it(`gives up after ${MAX_ATTEMPTS} attempts`, async () => {
    await enqueue(local, { id: 'doomed', type: 'order', method: 'POST', path: '/x', body: {} });
    const down = async () => { throw new Error('offline'); };
    for (let i = 0; i < MAX_ATTEMPTS; i++) await replay(local, down, () => (i + 1) * 3_600_000); // always past the backoff
    expect(await local.outbox.get('doomed')).toMatchObject({ status: 'failed', attempts: MAX_ATTEMPTS, lastError: 'offline' });
    expect(await local.audit.where('action').equals('sync:gave-up').count()).toBe(1);
  });
});

describe('conflict resolution (last-write-wins + audit)', () => {
  it('keeps the newer copy and logs the conflict', async () => {
    const localCopy = { id: 'x', qty: 3, updatedAt: '2026-10-31T10:00:00.000Z' };
    const remoteCopy = { id: 'x', qty: 1, updatedAt: '2026-10-31T09:00:00.000Z' };
    expect(await resolveConflict(local, 'cart', 'x', localCopy, remoteCopy)).toBe(localCopy);
    expect(await resolveConflict(local, 'cart', 'x', remoteCopy, localCopy)).toBe(localCopy);
    const log = await local.audit.where('action').equals('sync:conflict').toArray();
    expect(log.length).toBe(2);
    expect(log[0].detail).toMatchObject({ winner: 'local' });
  });

  it('prefers the server on a tie and skips the log when identical', async () => {
    const a = { id: 'x', qty: 1, updatedAt: 't' };
    const b = { id: 'x', qty: 2, updatedAt: 't' };
    expect(await resolveConflict(local, 'cart', 'x', a, b)).toBe(b);
    expect(await resolveConflict(local, 'cart', 'x', b, { ...b })).toEqual(b);
    expect(await local.audit.count()).toBe(1);
  });
});
