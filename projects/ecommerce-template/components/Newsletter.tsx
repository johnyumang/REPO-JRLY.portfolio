'use client';
import { useState } from 'react';

/** Phase 1: validates and stores sign-ups locally. Phase 2 moves this into the offline sync queue. */
export default function Newsletter() {
  const [state, setState] = useState<'idle' | 'error' | 'done'>('idle');
  const submit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const email = String(new FormData(e.currentTarget).get('email') || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return setState('error');
    try {
      const list = JSON.parse(localStorage.getItem('tpl.newsletter') || '[]');
      localStorage.setItem('tpl.newsletter', JSON.stringify([...new Set([...list, email])]));
    } catch {}
    setState('done');
  };
  return (
    <section className="mx-auto mt-28 max-w-3xl px-4 text-center" aria-labelledby="nl">
      <h2 id="nl" className="display text-4xl md:text-6xl">Join the list</h2>
      <p className="mt-4 text-sm text-muted">New drops, early access, 10% off your first order.</p>
      {state === 'done' ? (
        <p role="status" className="label mt-10 text-primary-text">You&apos;re in. Check your inbox.</p>
      ) : (
        <form onSubmit={submit} noValidate className="mx-auto mt-10 flex max-w-xl flex-col gap-3 sm:flex-row">
          <label htmlFor="nl-email" className="sr-only">Email address</label>
          <input id="nl-email" name="email" type="email" autoComplete="email" placeholder="EMAIL ADDRESS" aria-invalid={state === 'error'} aria-describedby="nl-err"
            className="min-h-cta flex-1 border border-line bg-transparent px-4 text-[12px] uppercase tracking-label placeholder:text-muted focus:border-primary focus:outline-none" />
          <button className="btn-primary sm:w-auto">Subscribe</button>
        </form>
      )}
      <p id="nl-err" className="mt-3 min-h-5 text-[12px] text-danger" aria-live="polite">{state === 'error' ? 'Enter a valid email address.' : ''}</p>
    </section>
  );
}
