# Progress

## Phase 1 — Design system + Zara-style preview ✅ (awaiting approval)
**Shipped:** design tokens (dark/light), Home, Collection (×6), Product (×12), header/menu/search overlays, bag drawer, trust badges, newsletter, footer, PWA + service worker.

**Test results (2026-10-31)**
| Check | Result |
|---|---|
| WCAG AA contrast, 23 token pairs | 23/23 pass |
| Primary CTA ≥ 56px, all controls ≥ 48px — 12 page/theme/viewport combos | 0 violations |
| Offline navigation (6 routes, network cut) | 6/6 load, 0 broken images |
| Offline add-to-bag | Pass |
| Screenshots | `screenshots/` — 3 pages × 2 themes × 2 widths |

**Next:** Phase 2 — IndexedDB (Dexie), MSW mock API, seed data (48 products), sync queue. Blocked on Phase 1 approval.
