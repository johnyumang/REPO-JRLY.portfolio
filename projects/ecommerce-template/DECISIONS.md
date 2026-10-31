# Decisions

1. **Static export + hand-written service worker** instead of Workbox for Phase 1: zero extra deps, every exported file precached (111 files, ~4 MB). Revisit with Workbox when dynamic data arrives in Phase 2.
2. **Contrast fixes to the brief's palette** (all needed to pass WCAG AA):
   - Dark `--primary-hover` `#5B7FF0` → `#2F54C9` (white label on lighter blue was 3.66:1, now 6.5:1).
   - Added `--primary-text`: `#8AA4FF` dark / `#2F54C9` light. Royal Blue `#4169E1` itself is kept for fills and CTAs.
   - Dark danger `#F06363`, dark success `#3CC47A`; light danger `#C42B2B`, light success `#157A41`.
3. **Motion kept subtle** (approved option): GSAP ScrollTrigger only, lazy-loaded, disabled for reduced-motion users. No WebGL, to protect the Lighthouse ≥ 90 target.
4. **Fonts self-hosted** (Inter Tight variable + Bodoni Moda) so typography works offline.
5. **Unbuilt routes never dead-end**: footer items for later phases render as plain text tagged with their phase; `/account/` exists as a placeholder; Checkout button is disabled and labelled "Phase 5".
6. **Stock photo with a visible third-party brand label removed** from the catalogue.
7. **MSW without its service worker.** One origin can only have one service worker per scope, and ours already precaches the site. In offline mode `lib/api/client.ts` passes each `Request` to MSW's `getResponse()` in-page, so the same handlers serve the browser and the Node tests (`msw/node`), with no second worker.
8. **Catalog stays the single source of truth.** `content/catalog.ts` grew to 48 products / 8 collections (adds Dresses and Trousers) and seeds IndexedDB, so the statically built pages and the database never disagree. Images reuse the 24 existing stock photos; no new downloads.
9. **Deterministic variant stock** (hash of the SKU, 3–40 units; listed sold-out sizes = 0), so seed data and tests are reproducible.
10. **Demo passwords are pre-hashed** in `content/seed.ts`; `scripts/hash-password.mjs` makes new ones. Nothing in the client bundle can recover them.
11. **Sync queue is strict FIFO.** If the oldest item is waiting on backoff, later ones wait too, so a ticket about an order can never arrive before the order. 4xx = permanent failure (kept, marked `failed`); 5xx/408/429/network = retry with backoff, give up after 8.
12. **Idempotency-Key = outbox item id**, sent on every replay, so a request whose response was lost can be retried without duplicates.
13. **UI wiring deferred to Phase 4.** Phase 2's gate is unit tests; moving the bag and pages onto the API is part of Phase 4 (catalog + cart), keeping each PR reviewable.
14. **Upgraded to vitest 5 and zod 4** because the 3.x lines had critical/high audit advisories.
15. **Medusa v2 (2.22.2) is the live backend**, replacing the custom Hono/Express + SQLite server in §2 (owner decision, 2026-10-31). It brings customer auth, cart, checkout, orders and an admin dashboard, so Phases 3, 5 and 9 configure Medusa instead of hand-building those parts. The Phase 2 offline layer (IndexedDB + MSW) stays as the offline cache and outbox and syncs to Medusa's Store API in live mode. Lives in `backend/` (official `medusa-starter-default`, npm instead of yarn).
16. **Always free.** Only open-source or free-tier tools. Medusa is self-hosted (no Medusa Cloud). Dev and tests run against local Postgres 16 + Redis. Production hosting must use free tiers or the owner's own server.
17. **Working principles: question every requirement, delete parts, simplify, speed up, then automate.** First applications: Medusa instead of a hand-built backend; the `serve` dev dependency (4 audit advisories) replaced by a 30-line zero-dependency `scripts/serve.mjs`. `npm audit` is now at 0.
18. **Upgraded to Next 16.4.3** before Phase 3 as planned; it clears the postcss advisory from Phase 1.
19. **No references to any other company** in the template; it is a standalone product. Removed one from MASTER-PROMPT §4.7.
20. **Medusa seed imports the storefront's own catalogue** (`backend/src/scripts/seed.ts` reads `content/catalog.ts`), replacing the starter's demo products. Same SKUs, prices and deterministic stock in both places; product images are served by the storefront.
21. **Free-shipping threshold lives in Medusa as a price rule** (`item_total >= 50` → €0 on Standard), mirroring `content/seed.ts`. One rule, two implementations, both tested.
22. **EUR + one Europe region** to match the template's € prices. More regions (e.g. PHP for the Philippines) are a seed change, not a code change.
