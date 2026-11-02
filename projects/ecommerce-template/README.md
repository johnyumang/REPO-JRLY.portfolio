# [BRAND] — Offline-First E-Commerce Template

Zara-style editorial storefront. Dark + Royal Blue + White. Static Next.js export + service worker, so the whole site works offline after the first visit.

**Status: Phase 1 of 10 (design gate)** — see `MASTER-PROMPT.md` for the full build plan and `PROGRESS.md` for what's done.

## Run it (under 5 minutes)
```bash
npm install
npm run build        # static export to /out + generates offline service worker
npm start            # serves /out on http://localhost:3000
npm run dev          # dev mode (service worker disabled)
```

## Checks
```bash
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

## Swap in your brand
- Copy, products, prices: `content/catalog.ts`
- Colours: `app/globals.css` (`:root` tokens)
- Images: drop photos in `public/stock/`, map them in `content/stock-map.json`, run `node scripts/optimize-images.mjs`
