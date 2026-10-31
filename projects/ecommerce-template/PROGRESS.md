# Progress

## Phase 1 — Design system + Zara-style preview ✅ (approved 2026-10-31)
**Shipped:** design tokens (dark/light), Home, Collection (×6), Product (×12), header/menu/search overlays, bag drawer, trust badges, newsletter, footer, PWA + service worker.

**Test results (2026-10-31)**
| Check | Result |
|---|---|
| WCAG AA contrast, 23 token pairs | 23/23 pass |
| Primary CTA ≥ 56px, all controls ≥ 48px — 12 page/theme/viewport combos | 0 violations |
| Offline navigation (6 routes, network cut) | 6/6 load, 0 broken images |
| Offline add-to-bag | Pass |
| Screenshots | `screenshots/` — 3 pages × 2 themes × 2 widths |



## Phase 2 — Data layer ✅
**Shipped:** IndexedDB schema (Dexie, 15 tables), seed data, MSW mock REST API over IndexedDB, background sync queue, `DATA_MODE=offline|live` client, browser seeding on first visit.

**Test results (2026-10-31)**
| Check | Result |
|---|---|
| Unit tests (`npm test`, Vitest 5) | 45/45 pass — seed 13, API 21, sync 11 |
| Typecheck (`npm run typecheck`) | 0 errors |
| Seed counts in a real browser (Chromium, IndexedDB) | 48 products · 8 collections · 6 posts · 30 FAQs · 20 reviews · 5 orders · 3 users |
| Phase 1 regression (`npm run test:visual`) | 0 button violations · 6/6 offline routes · 0 broken images · offline add-to-bag pass |
| Contrast | 23/23 pass |
| Build | 61 static pages (was 23); `sw.js` precaches 153 files |

**Covered by tests:** filter/search/sort/pagination, 404s, query validation, cart merge + stock limits, wishlist, server-side pricing, idempotent + concurrent orders, all-or-nothing stock checks, tickets, newsletter, outbox dedupe, lost-response replay with no duplicate order, strict FIFO, exponential backoff (2 s → 5 min cap), 4xx fail-fast, give-up after 8 attempts, last-write-wins with audit log.

**Not yet wired to the UI:** the bag still uses localStorage and pages still read `content/catalog.ts` at build time. Both move onto the API in Phase 4 (catalog + cart), as planned.

**Next:** Phase 3 — auth, security headers, roles (upgrade to Next 16 first).
