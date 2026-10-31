# [BRAND] — Offline-First E-Commerce Template

Zara-style editorial storefront. Dark + Royal Blue + White. Static Next.js export + service worker, so the whole site works offline after the first visit.

**Status: Phase 2 of 10 (data layer) complete** — see `MASTER-PROMPT.md` for the full build plan and `PROGRESS.md` for what's done.

## Run it (under 5 minutes)
```bash
npm install
npm run build        # static export to /out + generates offline service worker
npm start            # serves /out on http://localhost:3000
npm run dev          # dev mode (service worker disabled)
```

## Checks
```bash
npm test                 # unit tests: seed data, mock API, sync queue (Vitest)
npm run typecheck
npm run check:contrast   # WCAG AA on every colour token pair, both themes
npm run test:visual      # needs `npm start` running: screenshots (dark/light × 390/1440),
                         # button-size spec, offline navigation + offline add-to-bag
```

## What's in Phase 1
| Area | Detail |
|---|---|
| Pages | Home, 6 collection pages, 12 product pages, account placeholder, 404 |
| Design | Zara-style: full-bleed hero, thin uppercase display type, centred Didone wordmark, 1/2/4 grid toggle, hover second image, full-screen menu |
| Themes | Dark default, light option, header toggle, remembers choice, follows OS setting on first visit |
| Motion | Subtle GSAP (from the design skills pack): hero line reveals, scroll reveals, light parallax. Off under `prefers-reduced-motion` |
| Commerce | Variant + size picker, sold-out sizes, size guide, add-to-bag with loading/added states, sticky mobile CTA, bag drawer with free-shipping bar |
| Trust | Trust badge set (home strip, PDP, bag), payment icons |
| Offline | PWA manifest + service worker precaching all 111 files; offline search; offline bag |
| SEO | Per-page titles/descriptions, Product JSON-LD |

## Data layer (Phase 2)
| Piece | Where |
|---|---|
| IndexedDB schema (Dexie) | `lib/db.ts` |
| Seed data: 8 collections, 48 products with variants, 6 posts, 30 FAQs, 20 reviews, 5 orders, 3 users | `content/catalog.ts`, `content/seed.ts` |
| REST contract + Zod validation | `lib/api/contract.ts` |
| Mock API (MSW handlers over IndexedDB) | `lib/api/handlers.ts` |
| App fetch client, `DATA_MODE=offline\|live` | `lib/api/client.ts`, `.env.example` |
| Background sync queue | `lib/sync.ts` |

Demo accounts (placeholder, dev only; login UI arrives in Phase 3):
| Role | Email | Password |
|---|---|---|
| customer | customer@example.com | `Customer-Demo-2026!` |
| support | support@example.com | `Support-Demo-2026!` |
| admin | admin@example.com | `Admin-Demo-2026!` |

## Swap in your brand
- Copy, products, prices: `content/catalog.ts`
- Colours: `app/globals.css` (`:root` tokens)
- Images: drop photos in `public/stock/`, map them in `content/stock-map.json`, run `node scripts/optimize-images.mjs`
