import Link from 'next/link';
import Img from '@/components/Img';
import ProductCard from '@/components/ProductCard';
import { TrustBadges } from '@/components/TrustBadges';
import Newsletter from '@/components/Newsletter';
import { collections, inCollection } from '@/content/catalog';

export default function Home() {
  const newIn = inCollection('new-in').slice(0, 8);
  return (
    <>
      {/* HERO — full bleed, thin display type */}
      <section className="relative h-[calc(100svh-4rem)] min-h-[520px] overflow-hidden">
        <div className="absolute inset-0 scale-110"><Img name="hero" alt="Clothing rail in a softly lit studio" sizes="100vw" priority className="parallax h-full w-full object-cover" /></div>
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-black/10" />
        <div className="absolute inset-x-0 bottom-0 px-4 pb-10 text-white md:px-10 md:pb-16">
          <p className="label mb-4 overflow-hidden"><span className="hero-line inline-block">Autumn / Winter [YEAR]</span></p>
          <h1 className="display text-[12.5vw] md:text-[11vw]">
            <span className="block overflow-hidden"><span className="hero-line block">New</span></span>
            <span className="block overflow-hidden"><span className="hero-line block">Collection</span></span>
          </h1>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/collections/new-in/" className="btn-primary sm:w-auto">Shop new in</Link>
            <Link href="/collections/outerwear/" className="inline-flex min-h-cta items-center justify-center border border-white px-8 text-[12px] font-medium uppercase tracking-label text-white transition-colors hover:bg-white hover:text-black">Outerwear</Link>
          </div>
        </div>
      </section>

      {/* COLLECTION TILES */}
      <section className="mx-auto max-w-[1600px] px-2 pt-20 md:px-6" aria-labelledby="cats">
        <h2 id="cats" className="label mb-6 px-2 md:px-0">Shop by category</h2>
        <ul className="grid grid-cols-2 gap-2 md:grid-cols-3 md:gap-3">
          {collections.map((c) => (
            <li key={c.slug} className="reveal">
              <Link href={`/collections/${c.slug}/`} className="group relative block h-full overflow-hidden">
                <Img name={c.image} alt="" sizes="(min-width:768px) 33vw, 50vw" className="aspect-[3/4] w-full object-cover transition-transform duration-[1.4s] ease-out group-hover:scale-105" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/55 to-transparent" />
                <span className="display absolute bottom-4 left-4 text-3xl text-white md:text-5xl">{c.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      {/* NEW ARRIVALS */}
      <section className="mx-auto max-w-[1600px] px-2 pt-24 md:px-6" aria-labelledby="new">
        <div className="mb-8 flex items-end justify-between px-2 md:px-0">
          <h2 id="new" className="display text-4xl md:text-6xl">New in</h2>
          <Link href="/collections/new-in/" className="label link-u">View all</Link>
        </div>
        <div className="grid grid-cols-2 gap-x-2 gap-y-10 md:grid-cols-4 md:gap-x-3">
          {newIn.map((p) => <ProductCard key={p.slug} p={p} />)}
        </div>
      </section>

      {/* EDITORIAL SPLIT */}
      <section className="mx-auto mt-28 grid max-w-[1600px] items-center gap-10 px-4 md:grid-cols-2 md:px-6">
        <div className="reveal relative aspect-[4/5] overflow-hidden"><Img name="biker-model" alt="Model in a black leather jacket" sizes="(min-width:768px) 50vw, 100vw" className="parallax h-[112%] w-full object-cover" /></div>
        <div className="reveal md:px-16">
          <p className="label text-primary-text">Editorial</p>
          <h2 className="display mt-4 text-5xl md:text-7xl">The leather edit</h2>
          <p className="mt-6 max-w-md text-sm leading-relaxed text-muted">[EDITORIAL COPY] Sharp tailoring meets weathered texture. Pieces built to be worn for a decade, styled for tonight.</p>
          <Link href="/products/leather-biker-jacket/" className="btn-secondary mt-10">Discover</Link>
        </div>
      </section>

      {/* TRUST */}
      <section className="mx-auto mt-28 max-w-[1600px] px-4 md:px-6"><TrustBadges /></section>

      <Newsletter />
    </>
  );
}
