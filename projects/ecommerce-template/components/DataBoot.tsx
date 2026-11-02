'use client';
import { useEffect } from 'react';
/** Seeds IndexedDB on first visit and, in live mode, replays the offline outbox. Lazy-loaded so it never blocks first paint. */
export default function DataBoot() {
  useEffect(() => {
    let stop: (() => void) | undefined;
    let cancelled = false;
    (async () => {
      const [{ getDB }, { seedDatabase }, sync] = await Promise.all([import('@/lib/db'), import('@/lib/seed-db'), import('@/lib/sync')]);
      const db = getDB();
      await seedDatabase(db);
      const api = process.env.NEXT_PUBLIC_API_URL;
      if (!cancelled && process.env.NEXT_PUBLIC_DATA_MODE === 'live' && api) stop = sync.startAutoSync(db, sync.httpSender(api));
    })().catch((e) => console.warn('[data] boot failed', e));
    return () => { cancelled = true; stop?.(); };
  }, []);
  return null;
}
