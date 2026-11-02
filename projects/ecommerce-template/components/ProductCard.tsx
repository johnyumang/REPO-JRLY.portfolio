import Link from 'next/link';
import Img from './Img';
import { money, type Product } from '@/content/catalog';

export default function ProductCard({ p, sizes, priority }: { p: Product; sizes?: string; priority?: boolean }) {
  return (
    <Link href={`/products/${p.slug}/`} className="reveal group block" aria-label={`${p.name}, ${money(p.price)}`}>
      <div className="img-swap relative aspect-[3/4] overflow-hidden bg-surface">
        <Img name={p.images[0]} alt={p.name} sizes={sizes} priority={priority} className="absolute inset-0 h-full w-full object-cover transition-transform duration-[1.2s] ease-out group-hover:scale-[1.03]" />
        <Img name={p.images[1]} alt="" sizes={sizes} className="img-b absolute inset-0 h-full w-full object-cover" />
        {p.badge && <span className="absolute left-2 top-2 bg-bg px-2 py-1 text-[9px] font-semibold tracking-label text-primary-text">{p.badge}</span>}
      </div>
      <div className="mt-3 flex items-start justify-between gap-2 px-1">
        <p className="label leading-snug group-hover:text-primary-text">{p.name}</p>
        <p className="shrink-0 text-[12px]">
          {p.compareAt && <s className="mr-2 text-muted">{money(p.compareAt)}</s>}
          <span className={p.compareAt ? 'text-danger' : ''}>{money(p.price)}</span>
        </p>
      </div>
      {p.colors.length > 1 && (
        <div className="mt-2 flex gap-1.5 px-1" aria-label={`${p.colors.length} colours`}>
          {p.colors.map((c) => <span key={c.name} className="h-2.5 w-2.5 border border-line" style={{ background: c.hex }} />)}
        </div>
      )}
    </Link>
  );
}
