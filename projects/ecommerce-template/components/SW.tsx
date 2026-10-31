'use client';
import { useEffect, useState } from 'react';
/** Registers the offline service worker and shows a quiet offline indicator. */
export default function SW() {
  const [offline, setOffline] = useState(false);
  useEffect(() => {
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') navigator.serviceWorker.register('/sw.js').catch(() => {});
    const set = () => setOffline(!navigator.onLine);
    set(); window.addEventListener('online', set); window.addEventListener('offline', set);
    return () => { window.removeEventListener('online', set); window.removeEventListener('offline', set); };
  }, []);
  if (!offline) return null;
  return <div role="status" className="fixed bottom-4 left-1/2 z-50 -translate-x-1/2 bg-surface px-4 py-2 text-[11px] uppercase tracking-label text-muted shadow">Offline — browsing from cache</div>;
}
