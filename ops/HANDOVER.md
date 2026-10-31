# HANDOVER — REPO-JRLY.portfolio (2026-10-31)

Owner: John Rainier Yumang · GitHub `johnyumang/REPO-JRLY.portfolio`
Next step: **design in Claude Design**, then bring the approved designs back to a **Claude Code** session to implement and push.

---

## 0. Ground rules (apply to every project here)

1. **Always free.** Open-source or free-tier tools only. No paid hosting, APIs, or SaaS. Medusa is self-hosted, not Medusa Cloud.
2. **No connection to any other company.** These are standalone products, separate from the owner's employer. Don't use that company's names, data, branding, skills or references.
3. **Working principles:** question every requirement → delete parts → simplify → speed up → automate, in that order.
4. **Template mode** for the e-commerce template: `[BRAND]`, `[PRODUCT NAME]` placeholders, stock images only, every number marked as placeholder.
5. **Accessibility is not optional:** WCAG AA contrast on every text/background pair, primary CTA ≥ 56px tall, every control ≥ 48px, visible 3px focus ring, `prefers-reduced-motion` respected.
6. **Offline-first** (e-commerce template): every route and feature works with the network off after the first visit.
7. **Language:** the owner prefers **Tagalog** in chat. Code, commits and docs stay in English.
8. **Secrets never go in chat or git.** Keys go in the environment settings (Network secrets / env vars).

---

## 1. Projects and where they stand

| # | Project | Path | Branch | PR | Status |
|---|---|---|---|---|---|
| A | Personal portfolio site | `index.html`, `assets/` (repo root) | `claude/practical-knuth-is7590` | none yet | Built, **not live** |
| B | E-commerce template, Phase 1 (design) | `projects/ecommerce-template/` | `claude/ecommerce-template-phase1` | [#1](https://github.com/johnyumang/REPO-JRLY.portfolio/pull/1) | Done, design approved |
| C | E-commerce template, Phase 2 (data layer) | same | `claude/ecommerce-template-phase2` (stacked on B) | [#2](https://github.com/johnyumang/REPO-JRLY.portfolio/pull/2) | Done, 45/45 tests |
| D | E-commerce template, Phase 3 prep (Medusa, Next 16) | same + `backend/` | `claude/ecommerce-template-phase3` (stacked on C) | none yet | In progress |
| E | Sportswear muscle-compression showcase | `projects/sportswear-showcase/index.html` | `claude/sportswear-showcase` | none yet | Done (single file) |

Merge order for the e-commerce template: #1 → #2 → Phase 3. After each merge, retarget the next PR to `main`.

### A. Portfolio
- Single `index.html` (navy + gold, Cormorant Garamond + Inter), built from the owner's résumé, cover letter and portfolio PDFs. Downloadable PDFs live in `assets/`.
- Deploy: `.github/workflows/pages.yml` publishes to GitHub Pages on push to `main`.
- **To go live:** merge the branch into `main`, then repo **Settings → Pages → Source: GitHub Actions**.
- **Missing:** LinkedIn and Upwork URLs. The contact button has no link yet.

### B–D. E-commerce template (`projects/ecommerce-template/`)
- **Source of truth for the roadmap:** `MASTER-PROMPT.md` (Phases 1–10). Also read `PROGRESS.md`, `DECISIONS.md` (19 entries) and `SECURITY.md`.
- **Stack now:** Next.js **16.4.3** (App Router, TS, static export) · Tailwind 3 with CSS-variable tokens · GSAP (subtle motion only) · self-hosted fonts (Inter Tight Variable, Bodoni Moda) · hand-written service worker (`scripts/gen-sw.mjs`).
- **Data layer (Phase 2):** Dexie/IndexedDB (`lib/db.ts`), seed data (`content/catalog.ts`, `content/seed.ts`), MSW handlers over IndexedDB (`lib/api/handlers.ts`), Zod 4 contract (`lib/api/contract.ts`), outbox sync queue (`lib/sync.ts`), `NEXT_PUBLIC_DATA_MODE=offline|live`.
- **Live backend:** **Medusa v2.22.2**, self-hosted in `backend/`. It replaces the custom backend in MASTER-PROMPT §2 and provides customer auth, cart, checkout, orders and the admin dashboard. Phases 3, 5 and 9 configure Medusa instead of building those parts by hand.
- **Content:** 8 collections, 48 products (284 variants), 6 blog posts, 30 FAQs, 20 reviews, 5 orders, 3 demo users. All placeholders.
- **Pages today:** Home, `/collections/[slug]` ×8, `/products/[slug]` ×48, `/account/` placeholder, 404.
- **Latest checks (Phase 3 branch):**
  | Check | Result |
  |---|---|
  | Unit tests (`npm test`) | 45/45 |
  | Typecheck | 0 errors |
  | Contrast | 23/23 AA pairs |
  | Button size spec | 0 violations (12 screens) |
  | Offline | 6/6 routes, offline add-to-bag passes |
  | Build | 60 static pages, `sw.js` precaches 147 files |
  | `npm audit` | 0 vulnerabilities |
- **Commands:** `npm install` · `npm run dev` · `npm run build` · `npm start` (zero-dependency `scripts/serve.mjs`) · `npm test` · `npm run check:contrast` · `npm run test:visual`.
- **Demo storefront users** (offline mode, placeholders): `customer@`, `support@`, `admin@example.com`; passwords are in `projects/ecommerce-template/README.md`.
- **Medusa admin:** created on the cloud session's local server only, with credentials given to the owner as a file. **That server and its database are gone once the session ends.** A new session recreates them with `backend/README.md` (migrate, then `npx medusa user …`).

### E. Sportswear showcase (`projects/sportswear-showcase/index.html`)
- One file, no dependencies, no build. OKLCH palette, CSS container queries, bento grid, pill buttons with instant crimson hover, cyan glow on spec cards.
- Positioned as an **Impact Muscle Compression Tight**. Every spec number is placeholder test data.

---

## 2. Design systems to carry into Claude Design

### E-commerce template — "Zara-style", Dark + Royal Blue + White
Dark is the default; light mode is a toggle. Typography: Inter Tight (UI, thin uppercase display) and Bodoni Moda (centred Didone wordmark).

| Token | Dark | Light |
|---|---|---|
| bg | `#0B0F1A` | `#FFFFFF` |
| surface | `#121829` | `#F5F7FC` |
| text | `#FFFFFF` | `#0B0F1A` |
| text-muted | `#A7B0C5` | `#5A6378` |
| primary (fills, CTAs) | `#4169E1` | `#4169E1` |
| primary-hover | `#2F54C9` | `#2F54C9` |
| primary-text (small blue text) | `#8AA4FF` | `#2F54C9` |
| border | `#232B40` | `#E3E7F0` |
| success | `#3CC47A` | `#157A41` |
| danger | `#F06363` | `#C42B2B` |

These values already pass WCAG AA. Don't revert them to the original brief's colours.

Signature patterns: full-bleed hero with thin uppercase display type · full-screen menu overlay · 1/2/4 product grid toggle · second image on hover · sticky mobile add-to-bag · bag drawer with free-shipping bar · trust badges · newsletter · footer with payment icons.

**Screens still to design** (from MASTER-PROMPT, in phase order):
1. Login, sign-up, forgot/reset password, email verification (`/dev/inbox` simulates email offline) — Phase 3
2. Search results, filters, PDP A+ content modules (Amazon-style enhanced product content) — Phase 4
3. Checkout (one page, button spec), order confirmation, account (orders, addresses, wishlist) — Phase 5
4. Funnels: landing page, upsell, abandoned-cart recovery — Phase 6
5. Blog index and article — Phase 7
6. Support centre, FAQ, ticket form, AI chatbot widget — Phase 8
7. Admin dashboard (Medusa admin can be themed or linked) — Phase 9

### Sportswear showcase — OKLCH performance/comfort system
| Token | Value | Role |
|---|---|---|
| canvas | `oklch(14% 0.01 250)` | Deep Shadow Obsidian |
| surface | `oklch(20% 0.02 250)` | Technical Dark Titanium |
| ink | `oklch(98% 0 0)` | Crisp Polar White |
| energy | `oklch(70% 0.30 340)` | Kinetic Electric Crimson (performance) |
| comfort | `oklch(88% 0.12 180)` | Therapeutic Cyan Glow (comfort) |
| muted | `oklch(45% 0.01 250)` | Matte Charcoal, lines only |
| muted-text | `oklch(72% 0.01 250)` | small labels (45% fails AA as text) |

Headings: system sans, 900 weight, italic, uppercase, −0.05em tracking. Data: system monospace, +0.05em tracking. Panels 14px radius, inner lines sharp, buttons fully pill-shaped.

---

## 3. Working in Claude Design → back to code

1. Start from the tokens in §2 so designs match the existing code.
2. Design at **390px and 1440px**, in **dark and light** for the template.
3. Keep §0 rules 4–5 (placeholders, AA contrast, 56/48px controls, focus states) in every screen.
4. When a screen is approved, bring it to a **Claude Code** session for this repo along with:
   - the design link or exported specs (spacing, sizes, tokens, states)
   - which phase it belongs to
   - "follow HANDOVER.md and MASTER-PROMPT.md"
5. Claude Design doesn't run code or push to GitHub. Implementation, tests and PRs happen in Claude Code.

---

## 4. Open to-dos for the owner

- [ ] Review and merge [#1](https://github.com/johnyumang/REPO-JRLY.portfolio/pull/1), then [#2](https://github.com/johnyumang/REPO-JRLY.portfolio/pull/2).
- [ ] Portfolio: merge `claude/practical-knuth-is7590` into `main`, turn on Pages (Source: GitHub Actions), send LinkedIn and Upwork URLs.
- [ ] **Revoke the NVIDIA API key** that was shared in chat (build.nvidia.com → API Keys).
- [ ] Choose free Medusa hosting when live mode is needed (e.g. a free web tier + free Postgres; these sleep when idle), or your own server.
- [ ] To give a new session an image-generation or other key, add it under environment settings → Network secrets and say which service it's for.

## 5. Next engineering steps (Claude Code)

1. Phase 3: load the 48-product catalogue into Medusa via a seed script; connect storefront login to Medusa customer auth; add security headers (`_headers` / `vercel.json` + CSP meta); write security tests (brute-force lockout, role escalation, XSS, CSRF).
2. Phases 4–10 as in `MASTER-PROMPT.md`, each with its test gate and a `PROGRESS.md` entry.
