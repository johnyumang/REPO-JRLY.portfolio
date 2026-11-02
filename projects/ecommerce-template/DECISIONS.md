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
