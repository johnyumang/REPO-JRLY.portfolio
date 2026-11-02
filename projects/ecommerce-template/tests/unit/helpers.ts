import { setupServer } from 'msw/node';
import { TemplateDB } from '@/lib/db';
import { seedDatabase } from '@/lib/seed-db';
import { createHandlers } from '@/lib/api/handlers';

let n = 0;
export async function freshDb(seed = true) {
  const db = new TemplateDB(`test-${process.pid}-${++n}`);
  if (seed) await seedDatabase(db);
  return db;
}

export const BASE = 'http://shop.test';
/** MSW node server whose handlers read whichever db `current` points at. */
export function mockServer() {
  const ctx: { db?: TemplateDB } = {};
  const server = setupServer(...createHandlers(() => ctx.db!));
  return { server, ctx };
}

export const json = (body: unknown, headers: Record<string, string> = {}) =>
  ({ method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body) });
