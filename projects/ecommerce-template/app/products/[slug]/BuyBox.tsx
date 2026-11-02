'use client';
import { useEffect, useRef, useState } from 'react';
import { useBag } from '@/components/Bag';
import { TrustBadges } from '@/components/TrustBadges';
import { CloseIcon } from '@/components/Icons';
import { money, type Product } from '@/content/catalog';

export default function BuyBox({ p }: { p: Product }) {
  const { add } = useBag();
  const [color, setColor] = useState(p.colors[0].name);
  const [size, setSize] = useState<string | null>(p.sizes.length === 1 ? p.sizes[0] : null);
  const [err, setErr] = useState(false);
  const [state, setState] = useState<'idle' | 'loading' | 'done'>('idle');
  const [guide, setGuide] = useState(false);
  const [stickyVisible, setStickyVisible] = useState(false);
  const ctaRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const el = ctaRef.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setStickyVisible(!e.isIntersecting && e.boundingClientRect.top < 0));
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const onAdd = () => {
    if (state === 'loading') return; // prevent double-submit
    if (!size) { setErr(true); document.getElementById('sizes')?.scrollIntoView({ block: 'center', behavior: 'smooth' }); return; }
    setState('loading');
    setTimeout(() => { add({ slug: p.slug, size, color }); setState('done'); setTimeout(() => setState('idle'), 1600); }, 350);
  };
  const label = state === 'loading' ? 'Adding…' : state === 'done' ? 'Added ✓' : size ? 'Add to bag' : 'Select a size';

  return (
    <div className="pb-6">
      {p.badge && <p className="label mt-6 text-primary-text">{p.badge}</p>}
      <h1 className="mt-3 text-2xl font-light uppercase tracking-wide md:text-3xl">{p.name}</h1>
      <p className="mt-3 text-sm">
        {p.compareAt && <s className="mr-2 text-muted">{money(p.compareAt)}</s>}
        <span className={p.compareAt ? 'text-danger' : ''}>{money(p.price)}</span>
        <span className="ml-2 text-[11px] text-muted">VAT included</span>
      </p>
      <p className="mt-6 max-w-md text-[13px] leading-relaxed text-muted">{p.description}</p>

      <fieldset className="mt-8">
        <legend className="label">Colour — <span className="text-muted">{color}</span></legend>
        <div className="mt-3 flex gap-2">
          {p.colors.map((c) => (
            <button key={c.name} onClick={() => setColor(c.name)} aria-pressed={color === c.name} aria-label={c.name}
              className={`icon-btn border ${color === c.name ? 'border-ink' : 'border-transparent'}`}>
              <span className="h-7 w-7 border border-line" style={{ background: c.hex }} />
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset id="sizes" className="mt-6" aria-describedby="size-err">
        <div className="flex items-center justify-between">
          <legend className="label">Size</legend>
          <button className="min-h-tap text-[11px] uppercase tracking-label link-u" onClick={() => setGuide(true)}>Size guide</button>
        </div>
        <div className="mt-2 grid grid-cols-5 gap-1">
          {p.sizes.map((s) => {
            const out = p.soldOut?.includes(s);
            return (
              <button key={s} disabled={out} onClick={() => { setSize(s); setErr(false); }} aria-pressed={size === s}
                className={`min-h-tap border text-[12px] uppercase transition-colors ${p.sizes.length === 1 ? 'col-span-5' : ''} ${size === s ? 'border-ink bg-ink text-bg' : 'border-line hover:border-ink'} ${out ? 'cursor-not-allowed text-muted line-through opacity-60' : ''}`}>
                {s}{out && <span className="sr-only"> sold out</span>}
              </button>
            );
          })}
        </div>
        <p id="size-err" className="mt-2 min-h-5 text-[12px] text-danger" aria-live="polite">{err ? 'Please select a size.' : ''}</p>
      </fieldset>

      <button ref={ctaRef} onClick={onAdd} aria-busy={state === 'loading'} className="btn-primary mt-2 !w-full" data-testid="add-to-bag">{label}</button>
      <p className="mt-3 text-[12px] text-success">● In stock — ships in 24–48h</p>

      <div className="mt-6"><TrustBadges compact only={['secure', 'shipping', 'returns']} /></div>

      <div className="mt-8 divide-y divide-line border-y border-line">
        {[
          ['Composition & care', p.composition + ' Machine wash at 30°C. Do not tumble dry.'],
          ['Shipping & returns', 'Free standard shipping over the threshold. Free returns within 30 days. [POLICY PLACEHOLDER]'],
        ].map(([t, body]) => (
          <details key={t} className="group">
            <summary className="flex min-h-tap cursor-pointer list-none items-center justify-between label">{t}<span className="text-lg font-light transition-transform group-open:rotate-45">+</span></summary>
            <p className="pb-4 text-[13px] leading-relaxed text-muted">{body}</p>
          </details>
        ))}
      </div>

      {/* Sticky add-to-bag (mobile) */}
      <div className={`fixed inset-x-0 bottom-0 z-30 border-t border-line bg-bg p-3 backdrop-blur transition-transform duration-300 md:hidden ${stickyVisible ? 'translate-y-0' : 'translate-y-full'}`} aria-hidden={!stickyVisible}>
        <div className="flex items-center gap-3">
          <div className="min-w-0 flex-1"><p className="label truncate">{p.name}</p><p className="text-[12px] text-muted">{money(p.price)}{size ? ` · ${size}` : ''}</p></div>
          <button onClick={onAdd} className="btn-primary !w-auto shrink-0" tabIndex={stickyVisible ? 0 : -1}>{label}</button>
        </div>
      </div>

      {guide && (
        <div role="dialog" aria-modal="true" aria-label="Size guide" className="fixed inset-0 z-50 flex items-end justify-center bg-[var(--overlay)] md:items-center" onClick={() => setGuide(false)}>
          <div className="w-full max-w-lg bg-bg p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between"><h2 className="label">Size guide (cm)</h2><button className="icon-btn" autoFocus onClick={() => setGuide(false)} aria-label="Close size guide"><CloseIcon /></button></div>
            <table className="mt-4 w-full text-left text-[12px]">
              <thead className="text-muted"><tr><th className="py-2 font-normal">Size</th><th className="font-normal">Chest</th><th className="font-normal">Waist</th><th className="font-normal">Hip</th></tr></thead>
              <tbody>{[['XS', 82, 66, 90], ['S', 88, 72, 96], ['M', 94, 78, 102], ['L', 100, 84, 108], ['XL', 106, 90, 114]].map((r) => (
                <tr key={r[0]} className="border-t border-line">{r.map((c, i) => <td key={i} className="py-2">{c}</td>)}</tr>))}</tbody>
            </table>
            <p className="mt-4 text-[11px] text-muted">[PLACEHOLDER] Replace with brand measurements.</p>
          </div>
        </div>
      )}
    </div>
  );
}
