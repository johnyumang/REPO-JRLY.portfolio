'use client';
import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import ProductCard from '@/components/ProductCard';
import { collections, type Product } from '@/content/catalog';

type Sort = 'featured' | 'price-asc' | 'price-desc';
const VIEWS = [1, 2, 4] as const;

export default function CollectionView({ title, slug, items }: { title: string; slug: string; items: Product[] }) {
  const [view, setView] = useState<(typeof VIEWS)[number]>(4);
  const [sort, setSort] = useState<Sort>('featured');
  const [size, setSize] = useState<string | null>(null);
  useEffect(() => { try { const v = Number(localStorage.getItem('tpl.view')); if (VIEWS.includes(v as 1)) setView(v as 1); } catch {} }, []);
  const pick = (v: (typeof VIEWS)[number]) => { setView(v); try { localStorage.setItem('tpl.view', String(v)); } catch {} };

  const sizes = useMemo(() => [...new Set(items.flatMap((p) => p.sizes))], [items]);
  const list = useMemo(() => {
    let l = size ? items.filter((p) => p.sizes.includes(size) && !p.soldOut?.includes(size)) : items;
    if (sort === 'price-asc') l = [...l].sort((a, b) => a.price - b.price);
    if (sort === 'price-desc') l = [...l].sort((a, b) => b.price - a.price);
    return l;
  }, [items, size, sort]);

  // 1 = single column (editorial), 2 = two-up, 4 = dense. Mobile caps at 2.
  const grid = view === 1 ? 'grid-cols-1 md:grid-cols-2 md:px-[16%]' : view === 2 ? 'grid-cols-2 md:grid-cols-3' : 'grid-cols-2 md:grid-cols-4';

  return (
    <div className="mx-auto max-w-[1600px] px-2 md:px-6">
      <div className="px-2 pb-8 pt-16 md:px-0 md:pt-24">
        <nav aria-label="Breadcrumb" className="label text-muted"><Link href="/" className="hover:text-ink">Home</Link> / <span aria-current="page">{title}</span></nav>
        <h1 className="display mt-4 text-6xl md:text-9xl">{title}</h1>
      </div>

      <nav className="scrollbar-none -mx-2 flex gap-2 overflow-x-auto px-2 pb-6 md:mx-0 md:px-0" aria-label="Collections">
        {collections.map((c) => (
          <Link key={c.slug} href={`/collections/${c.slug}/`} aria-current={c.slug === slug ? 'page' : undefined}
            className={`inline-flex min-h-tap shrink-0 items-center border px-4 text-[11px] uppercase tracking-label ${c.slug === slug ? 'border-ink' : 'border-line text-muted hover:text-ink'}`}>{c.title}</Link>
        ))}
      </nav>

      <div className="sticky top-16 z-30 -mx-2 flex flex-wrap items-center justify-between gap-2 border-y border-line bg-bg px-2 py-1 backdrop-blur md:mx-0 md:px-0">
        <div className="flex items-center gap-1">
          <label htmlFor="size" className="sr-only">Filter by size</label>
          <select id="size" value={size ?? ''} onChange={(e) => setSize(e.target.value || null)} className="min-h-tap bg-transparent pr-2 text-[11px] uppercase tracking-label">
            <option value="" className="bg-bg">All sizes</option>
            {sizes.map((s) => <option key={s} value={s} className="bg-bg">{s}</option>)}
          </select>
          <label htmlFor="sort" className="sr-only">Sort</label>
          <select id="sort" value={sort} onChange={(e) => setSort(e.target.value as Sort)} className="min-h-tap bg-transparent pr-2 text-[11px] uppercase tracking-label">
            <option value="featured" className="bg-bg">Featured</option>
            <option value="price-asc" className="bg-bg">Price: low to high</option>
            <option value="price-desc" className="bg-bg">Price: high to low</option>
          </select>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px] uppercase tracking-label text-muted" aria-live="polite">{list.length} items</span>
          <div className="flex" role="group" aria-label="Grid view">
            {VIEWS.map((v) => (
              <button key={v} onClick={() => pick(v)} aria-pressed={view === v} aria-label={`${v} per row`}
                className={`icon-btn text-[12px] ${view === v ? 'text-ink underline underline-offset-4' : 'text-muted'} ${v === 4 ? 'hidden md:inline-flex' : ''}`}>{v}</button>
            ))}
          </div>
        </div>
      </div>

      {list.length === 0 ? (
        <div className="py-24 text-center">
          <p className="text-sm text-muted">No items in size {size}.</p>
          <button className="btn-secondary mt-6" onClick={() => setSize(null)}>Clear filter</button>
        </div>
      ) : (
        <div className={`mt-6 grid gap-x-2 gap-y-12 md:gap-x-3 ${grid}`}>
          {list.map((p, i) => <ProductCard key={p.slug} p={p} priority={i < 4} sizes={view === 1 ? '(min-width:768px) 34vw, 100vw' : '(min-width:768px) 25vw, 50vw'} />)}
        </div>
      )}
    </div>
  );
}
