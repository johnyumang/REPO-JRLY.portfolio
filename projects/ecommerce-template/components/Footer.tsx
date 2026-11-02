import Link from 'next/link';
import { BRAND, collections } from '@/content/catalog';
import { PaymentIcons } from './TrustBadges';

const cols = [
  { title: 'Shop', links: collections.map((c) => ({ label: c.title, href: `/collections/${c.slug}/` })) },
  { title: 'Help', soon: 'Phase 8', links: ['Shipping', 'Returns', 'Order tracking', 'Contact', 'FAQ'].map((label) => ({ label })) },
  { title: 'Company', soon: 'Phase 7', links: ['About', 'Journal', 'Careers', 'Sustainability'].map((label) => ({ label })) },
  { title: 'Legal', soon: 'Phase 8', links: ['Privacy', 'Terms', 'Cookies', 'Accessibility'].map((label) => ({ label })) },
];

export default function Footer() {
  return (
    <footer className="mt-24 border-t border-line">
      <div className="mx-auto grid max-w-[1600px] grid-cols-2 gap-10 px-4 py-14 md:grid-cols-5 md:px-6">
        <div className="col-span-2 md:col-span-1">
          <p className="font-logo text-3xl tracking-[0.18em]">{BRAND}</p>
          <p className="mt-4 max-w-xs text-[12px] text-muted">[BRAND TAGLINE] Template storefront — offline-first PWA.</p>
        </div>
        {cols.map((c) => (
          <div key={c.title}>
            <h3 className="label">{c.title}</h3>
            <ul className="mt-4 space-y-2 text-[12px] text-muted">
              {c.links.map((l) => (
                <li key={l.label}>
                  {'href' in l && l.href ? <Link href={l.href} className="inline-block py-1 hover:text-ink">{l.label}</Link>
                    : <span className="inline-block py-1" title={`Ships in ${c.soon}`}>{l.label}</span>}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="mx-auto flex max-w-[1600px] flex-col gap-4 border-t border-line px-4 py-6 md:flex-row md:items-center md:justify-between md:px-6">
        <PaymentIcons />
        <p className="text-[11px] text-muted">© {new Date().getFullYear()} {BRAND}. Template — stock imagery from Unsplash.</p>
      </div>
    </footer>
  );
}
