'use client';
import Link from 'next/link';
import { useEffect, useMemo, useRef, useState } from 'react';
import { usePathname } from 'next/navigation';
import { BagIcon, CloseIcon, MenuIcon, SearchIcon, UserIcon } from './Icons';
import ThemeToggle from './ThemeToggle';
import { useBag } from './Bag';
import Img from './Img';
import { BRAND, collections, products, money } from '@/content/catalog';

export default function Header() {
  const [menu, setMenu] = useState(false);
  const [search, setSearch] = useState(false);
  const { count, setOpen } = useBag();
  const path = usePathname();
  useEffect(() => { setMenu(false); setSearch(false); }, [path]);
  useEffect(() => {
    document.body.style.overflow = menu || search ? 'hidden' : '';
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') { setMenu(false); setSearch(false); } };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [menu, search]);

  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:bg-primary focus:px-4 focus:py-3 focus:text-white">Skip to content</a>
      <header className="sticky top-0 z-40 border-b border-line bg-bg backdrop-blur-md">
        <div className="mx-auto grid h-16 grid-cols-[1fr_auto_1fr] items-center px-2 md:px-6">
          <div className="flex items-center">
            <button className="icon-btn" onClick={() => setMenu(true)} aria-label="Open menu" aria-expanded={menu}><MenuIcon /></button>
            <button className="icon-btn sm:hidden" onClick={() => setSearch(true)} aria-label="Search"><SearchIcon /></button>
            <nav className="ml-4 hidden gap-6 lg:flex" aria-label="Primary">
              {collections.slice(0, 3).map((c) => (
                <Link key={c.slug} href={`/collections/${c.slug}/`} className={`label hover:text-primary-text ${path?.startsWith(`/collections/${c.slug}`) ? 'text-primary-text' : ''}`}>{c.title}</Link>
              ))}
            </nav>
          </div>
          <Link href="/" className="justify-self-center font-logo text-xl tracking-[0.12em] md:text-3xl md:tracking-[0.18em]" aria-label={`${BRAND} home`}>{BRAND}</Link>
          <div className="flex items-center justify-self-end">
            <span className="hidden sm:inline-flex"><button className="icon-btn" onClick={() => setSearch(true)} aria-label="Search"><SearchIcon /></button></span>
            <span className="hidden sm:inline-flex"><Link href="/account/" className="icon-btn" aria-label="Account (Phase 3)"><UserIcon /></Link></span>
            <ThemeToggle />
            <button className="icon-btn relative" onClick={() => setOpen(true)} aria-label={`Open bag, ${count} items`}>
              <BagIcon />
              {count > 0 && <span className="absolute right-1.5 top-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[9px] font-semibold text-white">{count}</span>}
            </button>
          </div>
        </div>
      </header>
      <MenuOverlay open={menu} onClose={() => setMenu(false)} />
      <SearchOverlay open={search} onClose={() => setSearch(false)} />
    </>
  );
}

function MenuOverlay({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <div role="dialog" aria-modal="true" aria-label="Menu" aria-hidden={!open}
      className={`fixed inset-0 z-50 bg-bg transition-[opacity,visibility] duration-500 ${open ? 'visible opacity-100' : 'invisible opacity-0'}`}>
      <div className="flex h-16 items-center px-2 md:px-6">
        <button className="icon-btn" onClick={onClose} aria-label="Close menu"><CloseIcon /></button>
      </div>
      <div className="grid h-[calc(100%-4rem)] md:grid-cols-[1fr_1fr]">
        <nav className="flex flex-col justify-center gap-1 px-8 md:px-20" aria-label="All categories">
          {collections.map((c, i) => (
            <Link key={c.slug} href={`/collections/${c.slug}/`} onClick={onClose}
              className={`display text-5xl transition-all duration-700 hover:text-primary-text md:text-7xl ${open ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'}`}
              style={{ transitionDelay: open ? `${80 + i * 50}ms` : '0ms' }}>{c.title}</Link>
          ))}
          <div className="mt-10 flex gap-6 text-[12px] text-muted">
            <span>Help · Phase 8</span><span>Journal · Phase 7</span><span>Stores · Phase 8</span>
          </div>
        </nav>
        <div className="relative hidden overflow-hidden md:block">
          <Img name="blue-coat" alt="" sizes="50vw" className="h-full w-full object-cover" />
        </div>
      </div>
    </div>
  );
}

function SearchOverlay({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [q, setQ] = useState('');
  const ref = useRef<HTMLInputElement>(null);
  useEffect(() => { if (open) setTimeout(() => ref.current?.focus(), 50); else setQ(''); }, [open]);
  const results = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (!t) return products.slice(0, 4);
    return products.filter((p) => [p.name, ...p.collections, ...p.colors.map((c) => c.name)].join(' ').toLowerCase().includes(t));
  }, [q]);
  return (
    <div role="dialog" aria-modal="true" aria-label="Search" aria-hidden={!open}
      className={`fixed inset-0 z-50 overflow-y-auto bg-bg transition-[opacity,visibility] duration-300 ${open ? 'visible opacity-100' : 'invisible opacity-0'}`}>
      <div className="flex h-16 items-center justify-end px-2 md:px-6">
        <button className="icon-btn" onClick={onClose} aria-label="Close search"><CloseIcon /></button>
      </div>
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <label htmlFor="q" className="label text-muted">Search — works offline</label>
        <input id="q" ref={ref} value={q} onChange={(e) => setQ(e.target.value)} placeholder="WHAT ARE YOU LOOKING FOR?"
          className="mt-3 w-full border-b border-ink bg-transparent pb-3 text-2xl font-extralight uppercase tracking-wide placeholder:text-muted focus:outline-none md:text-4xl" />
        <p className="label mt-8 text-muted" aria-live="polite">{q ? `${results.length} results` : 'Trending'}</p>
        <ul className="mt-4 grid grid-cols-2 gap-x-3 gap-y-8 pb-16 md:grid-cols-4">
          {results.map((p) => (
            <li key={p.slug}>
              <Link href={`/products/${p.slug}/`} onClick={onClose} className="group block" tabIndex={open ? 0 : -1}>
                <Img name={p.images[0]} alt={p.name} className="aspect-[3/4] w-full object-cover" />
                <p className="label mt-3 group-hover:text-primary-text">{p.name}</p>
                <p className="mt-1 text-[12px] text-muted">{money(p.price)}</p>
              </Link>
            </li>
          ))}
          {q && results.length === 0 && <li className="col-span-full py-10 text-sm text-muted">No results for “{q}”. Try “jacket”, “tee” or “knit”.</li>}
        </ul>
      </div>
    </div>
  );
}
