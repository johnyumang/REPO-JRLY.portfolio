'use client';
import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import Link from 'next/link';
import Img from './Img';
import { CloseIcon } from './Icons';
import { getProduct, money, FREE_SHIPPING_OVER, CURRENCY } from '@/content/catalog';
import { TrustBadges } from './TrustBadges';

export type Line = { slug: string; size: string; color: string; qty: number };
type Ctx = { lines: Line[]; add: (l: Omit<Line, 'qty'>) => void; remove: (i: number) => void; open: boolean; setOpen: (o: boolean) => void; count: number };
const BagCtx = createContext<Ctx | null>(null);
const KEY = 'tpl.bag.v1';

export function BagProvider({ children }: { children: React.ReactNode }) {
  const [lines, setLines] = useState<Line[]>([]);
  const [open, setOpen] = useState(false);
  useEffect(() => { try { setLines(JSON.parse(localStorage.getItem(KEY) || '[]')); } catch {} }, []);
  const persist = (next: Line[]) => { setLines(next); try { localStorage.setItem(KEY, JSON.stringify(next)); } catch {} };
  const add = useCallback((l: Omit<Line, 'qty'>) => {
    setLines((cur) => {
      const i = cur.findIndex((x) => x.slug === l.slug && x.size === l.size && x.color === l.color);
      const next = i >= 0 ? cur.map((x, j) => (j === i ? { ...x, qty: x.qty + 1 } : x)) : [...cur, { ...l, qty: 1 }];
      try { localStorage.setItem(KEY, JSON.stringify(next)); } catch {}
      return next;
    });
    setOpen(true);
  }, []);
  const remove = (i: number) => persist(lines.filter((_, j) => j !== i));
  const count = lines.reduce((n, l) => n + l.qty, 0);
  return <BagCtx.Provider value={{ lines, add, remove, open, setOpen, count }}>{children}<BagDrawer /></BagCtx.Provider>;
}

export const useBag = () => {
  const c = useContext(BagCtx);
  if (!c) throw new Error('useBag outside provider');
  return c;
};

function BagDrawer() {
  const { lines, remove, open, setOpen } = useBag();
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false);
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [setOpen]);
  const subtotal = lines.reduce((s, l) => s + (getProduct(l.slug)?.price ?? 0) * l.qty, 0);
  const left = Math.max(0, FREE_SHIPPING_OVER - subtotal);
  const pct = Math.min(100, (subtotal / FREE_SHIPPING_OVER) * 100);
  return (
    <div className={`fixed inset-0 z-50 ${open ? '' : 'pointer-events-none'}`} aria-hidden={!open}>
      <div className={`absolute inset-0 bg-[var(--overlay)] transition-opacity duration-300 ${open ? 'opacity-100' : 'opacity-0'}`} onClick={() => setOpen(false)} />
      <aside role="dialog" aria-modal="true" aria-label="Shopping bag"
        className={`absolute right-0 top-0 flex h-full w-full max-w-md flex-col bg-bg transition-transform duration-500 ease-[cubic-bezier(.2,.7,.2,1)] ${open ? 'translate-x-0' : 'translate-x-full'}`}>
        <header className="flex items-center justify-between border-b border-line px-5 py-2">
          <h2 className="label">Bag ({lines.reduce((n, l) => n + l.qty, 0)})</h2>
          <button className="icon-btn" onClick={() => setOpen(false)} aria-label="Close bag" tabIndex={open ? 0 : -1}><CloseIcon /></button>
        </header>
        <div className="border-b border-line px-5 py-4">
          <p className="text-[12px]">{left > 0 ? <>Add <strong>{money(left)}</strong> for free shipping</> : <>You&apos;ve unlocked <strong>free shipping</strong></>}</p>
          <div className="mt-2 h-[3px] bg-line" role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100} aria-label="Progress to free shipping">
            <div className="h-full bg-primary transition-all duration-500" style={{ width: `${pct}%` }} />
          </div>
        </div>
        <ul className="flex-1 overflow-y-auto">
          {lines.length === 0 && <li className="px-5 py-16 text-center text-sm text-muted">Your bag is empty.</li>}
          {lines.map((l, i) => {
            const p = getProduct(l.slug);
            if (!p) return null;
            return (
              <li key={i} className="flex gap-4 border-b border-line px-5 py-4">
                <Img name={p.images[0]} alt={p.name} sizes="96px" className="aspect-[3/4] w-24 object-cover" />
                <div className="flex flex-1 flex-col text-[12px]">
                  <Link href={`/products/${p.slug}/`} className="label hover:text-primary-text" onClick={() => setOpen(false)} tabIndex={open ? 0 : -1}>{p.name}</Link>
                  <span className="mt-1 text-muted">{l.color} · {l.size} · Qty {l.qty}</span>
                  <span className="mt-auto">{money(p.price * l.qty)}</span>
                </div>
                <button className="icon-btn self-start text-muted" onClick={() => remove(i)} aria-label={`Remove ${p.name}`} tabIndex={open ? 0 : -1}><CloseIcon /></button>
              </li>
            );
          })}
        </ul>
        <footer className="space-y-4 border-t border-line px-5 py-5">
          <div className="flex justify-between label"><span>Subtotal</span><span>{money(subtotal)}</span></div>
          <button className="btn-primary !w-full" disabled title="Checkout ships in Phase 5" tabIndex={open ? 0 : -1}>Checkout · Phase 5</button>
          <TrustBadges compact only={['secure', 'returns', 'guarantee']} />
          <p className="text-center text-[10px] text-muted">Prices in {CURRENCY}. Template data.</p>
        </footer>
      </aside>
    </div>
  );
}
