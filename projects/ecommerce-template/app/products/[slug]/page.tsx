import { notFound } from 'next/navigation';
import Link from 'next/link';
import Img from '@/components/Img';
import ProductCard from '@/components/ProductCard';
import BuyBox from './BuyBox';
import { BRAND, CURRENCY, getProduct, products } from '@/content/catalog';

export const dynamicParams = false;
export function generateStaticParams() { return products.map((p) => ({ slug: p.slug })); }
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const p = getProduct(slug);
  return { title: p?.name ?? 'Product', description: p?.description };
}

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const p = getProduct(slug);
  if (!p) notFound();
  const related = products.filter((x) => x.slug !== p.slug && x.collections.some((c) => p.collections.includes(c))).slice(0, 4);
  const jsonLd = {
    '@context': 'https://schema.org', '@type': 'Product', name: p.name, description: p.description, brand: { '@type': 'Brand', name: BRAND },
    image: p.images.map((i) => `/stock/${i}-1400.webp`),
    offers: { '@type': 'Offer', price: p.price, priceCurrency: CURRENCY === '€' ? 'EUR' : CURRENCY, availability: 'https://schema.org/InStock' },
  };
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <div className="mx-auto grid max-w-[1600px] gap-8 md:grid-cols-[1.4fr_1fr] md:gap-12 md:px-6 md:pt-6">
        {/* Gallery: horizontal swipe on mobile, stacked editorial column on desktop */}
        <section aria-label="Product images" className="scrollbar-none flex snap-x snap-mandatory overflow-x-auto md:grid md:grid-cols-2 md:gap-2 md:overflow-visible">
          {p.images.map((img, i) => (
            <div key={img} className={`relative w-full shrink-0 snap-center overflow-hidden bg-surface ${i === 0 ? 'md:col-span-2' : ''}`}>
              <Img name={img} alt={`${p.name} — view ${i + 1}`} priority={i === 0} sizes={i === 0 ? '(min-width:768px) 58vw, 100vw' : '(min-width:768px) 29vw, 100vw'}
                className={`w-full object-cover ${i === 0 ? 'aspect-[3/4] md:aspect-[4/5]' : 'aspect-[3/4]'}`} />
              <span className="absolute bottom-3 right-3 bg-bg px-2 py-1 text-[10px] tracking-label md:hidden">{i + 1} / {p.images.length}</span>
            </div>
          ))}
        </section>

        <div className="px-4 md:px-0">
          <div className="md:sticky md:top-24">
            <nav aria-label="Breadcrumb" className="label text-muted">
              <Link href="/" className="hover:text-ink">Home</Link> / <Link href={`/collections/${p.collections[0]}/`} className="hover:text-ink">{p.collections[0].replace('-', ' ')}</Link>
            </nav>
            <BuyBox p={p} />
          </div>
        </div>
      </div>

      {/* A+ content teaser — full module library ships in Phase 4 */}
      <section className="mx-auto mt-28 grid max-w-[1600px] items-center gap-10 px-4 md:grid-cols-2 md:px-6" aria-label="Product story">
        <div className="reveal md:order-2 md:px-16">
          <p className="label text-primary-text">Crafted to last</p>
          <h2 className="display mt-4 text-4xl md:text-6xl">Details that matter</h2>
          <ul className="mt-8 grid grid-cols-3 gap-6 border-t border-line pt-6 text-[12px] text-muted">
            <li><span className="display block text-3xl text-ink">01</span>Premium materials</li>
            <li><span className="display block text-3xl text-ink">02</span>Reinforced seams</li>
            <li><span className="display block text-3xl text-ink">03</span>Considered fit</li>
          </ul>
        </div>
        <div className="reveal relative aspect-[4/3] overflow-hidden"><Img name={p.images[2] ?? p.images[0]} alt="" sizes="(min-width:768px) 50vw, 100vw" className="parallax h-[112%] w-full object-cover" /></div>
      </section>

      {related.length > 0 && (
        <section className="mx-auto mt-28 max-w-[1600px] px-2 md:px-6" aria-labelledby="rel">
          <h2 id="rel" className="label mb-6 px-2 md:px-0">You may also like</h2>
          <div className="grid grid-cols-2 gap-x-2 gap-y-10 md:grid-cols-4 md:gap-x-3">{related.map((r) => <ProductCard key={r.slug} p={r} />)}</div>
        </section>
      )}
    </>
  );
}
