# MASTER PROMPT — Offline-First E-Commerce Platform (Full Stack, AI-Automated, End to End)

> Paste this whole file into Claude Code (or any agentic coding tool) at the root of an empty folder.
> Goal: deliver a complete, working, templated e-commerce website end to end. Everything must run offline first.

---

## 0. ROLE AND OPERATING MODE

You are the **Lead Orchestrator** for a full-stack e-commerce build. You plan, delegate to sub-agents (or work in sequenced phases), verify, and ship.

Rules:
- Work in the phases below, in order. Do not skip the **Phase 1 design gate**.
- After each phase: run the tests for that phase, fix failures, then write a short `PROGRESS.md` entry (what shipped, what's left, test results).
- Never leave a page, button, or link that does nothing. Every route works offline.
- This is a **blank template**: brand name `[BRAND]`, products and copy are placeholders, all images are stock (see §6).
- If a requirement is ambiguous, choose the option that is most secure, most accessible, and works offline, then log the decision in `DECISIONS.md`.

---

## 1. DESIGN DIRECTION — "ZARA STYLE" (Phase 1 gate)

Reference: Zara.com editorial minimalism.
- Huge whitespace, full-bleed imagery, near-invisible chrome.
- Small uppercase sans-serif nav and labels, wide letter-spacing (0.08–0.12em).
- Large thin display type for hero and collection titles.
- Grid-first catalog (2 cols mobile, 4 cols desktop, toggle to 1/2/4 view).
- Hover reveals a second image; no heavy shadows, no rounded "bubble" UI.
- Sticky minimal header: logo center, menu left, search/account/bag right.
- Hamburger opens a full-screen category overlay.

### Palette (mandatory)
Dark + Royal Blue + White. Two themes, toggle in header, remember choice, respect `prefers-color-scheme`.

| Token | Light (white background) | Dark (default) |
|---|---|---|
| `--bg` | `#FFFFFF` | `#0B0F1A` |
| `--surface` | `#F5F7FC` | `#121829` |
| `--text` | `#0B0F1A` | `#FFFFFF` |
| `--text-muted` | `#5A6378` | `#A7B0C5` |
| `--primary` (Royal Blue) | `#4169E1` | `#4169E1` |
| `--primary-hover` | `#2F54C9` | `#5B7FF0` |
| `--border` | `#E3E7F0` | `#232B40` |
| `--success` / `--danger` | `#1F9D55` / `#D93636` | same |

All text/background pairs must pass WCAG AA (4.5:1 body, 3:1 large). Verify with an automated contrast check.

### Phase 1 deliverable (STOP and show before continuing)
Build only: Home, one Collection page, one Product page — in both dark and light mode, with stock images. Produce screenshots at 390px and 1440px. **Wait for approval before Phase 2.**

---

## 2. TECH STACK (offline-first)

- **Frontend:** Next.js (App Router, TypeScript) + Tailwind CSS with the tokens above as CSS variables.
- **Offline layer:** Service Worker (Workbox) + Web App Manifest (installable PWA). Precache app shell, all routes, fonts, and all stock images.
- **Local data:** IndexedDB via Dexie — products, collections, cart, wishlist, orders, users, blog posts, support tickets, chat history.
- **Mock API:** MSW (Mock Service Worker) serving the same REST contract the real backend will use, so the app works fully with no server.
- **Optional live backend (same contract):** Hono or Express + SQLite (Drizzle ORM). A single env flag `DATA_MODE=offline|live` switches between them.
- **Sync:** background sync queue — actions taken offline (orders, tickets, newsletter sign-ups) are queued and replayed when online, with conflict handling (last-write-wins + audit log).
- **Testing:** Vitest (unit), Playwright (E2E + offline mode), Lighthouse CI, axe-core (accessibility), k6 or autocannon (load).

---

## 3. SECURITY AND AUTHENTICATION

- Sign up, log in, log out, forgot/reset password, email verification flow (offline: simulated with a local inbox page at `/dev/inbox`).
- Passwords hashed with PBKDF2 or Argon2 (WebCrypto in offline mode, argon2 on server). Never store plain text.
- Sessions: httpOnly, Secure, SameSite=Strict cookies on live mode; signed tokens with expiry in offline mode.
- Role-based access: `customer`, `support`, `admin`. Admin and support routes guarded on client AND server.
- Optional TOTP 2FA for admin.
- Rate limiting and lockout after 5 failed logins.
- Strict Content-Security-Policy, HSTS, X-Frame-Options, Referrer-Policy, Permissions-Policy headers.
- Input validation with Zod on every form and API route; output escaping; CSRF protection on mutations.
- No secrets in the client bundle. `.env.example` documents every variable.
- Run `npm audit` and a dependency scan; log results in `SECURITY.md`.

---

## 4. PAGES AND FEATURES (all must work offline)

### Storefront
- **Home:** full-bleed hero, featured collections, new arrivals, editorial blocks, trust badges strip, newsletter.
- **Full catalog:** `/collections` index + `/collections/[slug]`; filters (category, size, color, price, availability), sort, grid view toggle, pagination or infinite scroll, empty and no-results states.
- **Search:** instant offline search across products and blog (MiniSearch or Fuse.js), with suggestions.
- **Product page (PDP):** gallery with zoom, variant selector, size guide modal, stock status, sticky add-to-bag on mobile, reviews (seeded), related products, **A+ content** (§4.3).
- **Cart / bag:** drawer + full page, quantity edit, promo codes, shipping estimate, free-shipping progress bar.
- **Checkout:** see §4.4.
- **Account:** profile, addresses, order history, order detail, wishlist, saved payment placeholder (no real card data stored), logout.

### 4.1 Trust signals (badges)
Reusable `<TrustBadge>` component set: Secure Checkout, Free Shipping over X, 30-Day Returns, Money-Back Guarantee, Verified Reviews, Payment method icons, "As seen in" logo row (placeholder logos). Placed on: home strip, PDP under add-to-bag, cart, checkout, footer. Monochrome, Royal Blue accent icons.

### 4.2 Blog
- `/blog` index with categories, tags, search, featured post.
- `/blog/[slug]` with author, read time, table of contents, related products block, share buttons, newsletter CTA.
- Content stored as MDX, 6 seeded placeholder posts.
- SEO: meta, Open Graph, JSON-LD (Article, Product, BreadcrumbList, Organization, FAQPage), sitemap.xml, robots.txt.

### 4.3 A+ content (Amazon-style enhanced PDP modules)
Build a module library, configured per product via JSON:
- Full-width banner with text overlay
- Image + text (left/right)
- 3- and 4-column feature tiles
- Comparison chart (this product vs. 3 siblings)
- Specs table
- "How to use" step module
- Lifestyle image grid
- FAQ accordion
Admin can reorder modules per product.

### 4.4 Checkout and button sizing
- Single-page checkout: contact → shipping → delivery method → payment → review.
- Guest checkout + account checkout. Address validation. Order summary always visible (collapsible on mobile).
- Payment: mock gateway in offline mode (test card flow, success/fail/3DS states); Stripe test mode adapter for live.
- Order confirmation page + local "email" in `/dev/inbox`.
- **Button spec (enforce in a design-token + test):**
  - Primary CTA (Add to Bag, Checkout, Place Order): min height **56px**, full width on mobile, min **48×48px** touch target everywhere.
  - Secondary buttons: min height 48px.
  - Royal Blue fill, white text, uppercase label, 0.1em letter-spacing, visible focus ring (3px).
  - Loading, disabled, and success states. Prevent double-submit.
  - Playwright test asserts these sizes at 390px and 1440px.

### 4.5 Complete funnels
Build and wire each funnel end to end, with event tracking stored locally:
1. **Lead magnet funnel:** landing page → email capture → thank-you → 3-step welcome email sequence (templates).
2. **Product funnel:** ad landing page → PDP → bag → checkout → **one-click upsell** → order confirmation.
3. **Abandoned cart:** detect inactive cart → reminder (on-site banner + email template with recovery link).
4. **Post-purchase:** review request, cross-sell, referral code.
5. **Win-back:** dormant customer template.
Include a funnel analytics page in admin: visits, step conversion %, drop-off per step.

### 4.6 Support centre
- `/support`: searchable help centre, FAQ categories (shipping, returns, orders, account, payments, product use).
- Policy pages: shipping, returns, refunds, privacy, terms, cookies, accessibility statement.
- Contact form → creates a support ticket (stored offline, synced when online).
- Order tracking page (by order number + email).
- Returns request flow (select items → reason → label placeholder).
- Cookie consent banner (decline non-essential by default).

### 4.7 AI chatbot and automation (like SIIL's CS auto loop)
- Floating chat widget, matches theme, keyboard accessible.
- **Offline mode:** local retrieval over FAQ, policies, product catalog, and order lookup (MiniSearch + intent rules). Must answer common questions with zero network.
- **Live mode:** LLM API adapter (provider-agnostic, key in env) with the same retrieval as context; guardrails (no medical/legal advice beyond policy text, no invented order data).
- Escalation: "Talk to a human" → creates a support ticket with full transcript.
- **Automation loop:**
  - Ticket auto-tagging by intent (order status, return, product question, complaint).
  - Suggested reply drafts for support staff.
  - Unanswered questions logged → admin "Knowledge gaps" queue → one-click add to FAQ (self-learning).
- Order automation: status transitions (paid → packed → shipped → delivered) with templated notifications.

### 4.8 Admin dashboard (`/admin`)
- Products, variants, collections, inventory, A+ module editor.
- Orders (status, refund, notes), customers, support tickets, chat transcripts, knowledge gaps.
- Blog post editor, promo codes, funnel analytics, settings (theme, brand name, logo, currency).
- CSV import/export for products and orders.

---

## 5. OFFLINE-FIRST, STRESS AND QUALITY TESTS (Definition of Done)

All must pass and be reported in `TEST-REPORT.md`:
- **Offline:** Playwright runs the full journey (browse → search → PDP → bag → checkout → confirmation → support ticket → chatbot answer) with the network disabled after first load.
- **Sync:** place order and ticket offline, reconnect, verify replay with no duplicates.
- **Stress:** 500 concurrent virtual users against the live-mode API for 5 minutes; p95 < 500ms, error rate < 1%. Also seed 10,000 products locally and confirm catalog filter/search stays under 200ms.
- **Lighthouse (mobile):** Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95, PWA installable.
- **Accessibility:** zero axe-core critical/serious issues; full keyboard navigation; focus states visible in both themes.
- **Security:** auth abuse tests (brute force lockout, role escalation attempt, XSS payloads in forms, CSRF).
- **Visual:** screenshots of every route in dark + light at 390px and 1440px.
- **Buttons:** size assertions from §4.4 pass.

---

## 6. CONTENT AND IMAGES (TEMPLATE MODE)

- **Stock images only.** Source from Unsplash or Pexels (free licence), download at build time into `/public/stock/`, record photographer + URL in `/public/stock/CREDITS.md`. Compress to WebP/AVIF with responsive sizes.
- Fallback: generated neutral SVG placeholders if an image is missing, so offline never shows a broken image.
- Seed data: 8 collections, 48 products with variants, 6 blog posts, 30 FAQ entries, 20 reviews, 5 sample orders, 3 users (customer/support/admin) — all clearly marked as placeholder.
- All copy uses `[BRAND]`, `[PRODUCT NAME]` style tokens, centralised in one `content/` folder for easy replacement.

---

## 7. PHASES

| Phase | Output | Gate |
|---|---|---|
| 1 | Design system + Zara-style Home/Collection/PDP preview, dark + light | **User approval** |
| 2 | Data layer: IndexedDB, MSW mock API, seed data, sync queue | Unit tests pass |
| 3 | Auth + security headers + roles | Security tests pass |
| 4 | Full catalog, search, PDP with A+ modules, cart | E2E pass |
| 5 | Checkout, button spec, trust badges, account | Button + checkout tests pass |
| 6 | Funnels + funnel analytics | Funnel E2E pass |
| 7 | Blog + SEO | Lighthouse SEO ≥ 95 |
| 8 | Support centre + AI chatbot + automation loop | Offline chatbot test pass |
| 9 | Admin dashboard | Role tests pass |
| 10 | Full test suite, stress test, docs | Definition of Done (§5) met |

---

## 8. FINAL DELIVERABLES

- Working repo with `npm run dev`, `npm run build`, `npm run test`, `npm run test:e2e`, `npm run test:offline`, `npm run test:load`.
- `README.md` (setup in under 5 minutes), `DECISIONS.md`, `SECURITY.md`, `TEST-REPORT.md`, `PROGRESS.md`, `/public/stock/CREDITS.md`.
- `HANDOFF.md`: how to swap in real brand, products, images, payment keys, LLM key, and switch `DATA_MODE=live`.
- Deploy-ready build (static export + optional Node server), with a one-command deploy guide for Vercel and a VPS.

**Start now with Phase 1. Show me the Zara-style preview in both themes before building anything else.**
