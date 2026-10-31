# DESIGN.md — KINETIC LAB Concept Store

Repository automation profile. Agents and contributors read this before changing
`src/index.html` or `public/static/css/global.css`. Every rule here is checkable;
the checklist at the end is the merge gate.

---

## 1. Repository layout

| Path | Role |
|---|---|
| `src/index.html` | Single-page storefront: markup, Tailwind config, all Vanilla JS |
| `public/static/css/global.css` | Design tokens, component primitives, container queries, motion |
| `.github/DESIGN.md` | This profile |

Zero build. No bundler, no package install, no framework. Tailwind runs from the
Play CDN pinned to `3.4.17`. Open `src/index.html` through any static server
(`npx serve .` or `python3 -m http.server`) so the relative stylesheet path
`../public/static/css/global.css` resolves.

## 2. Brand

- Name: **KINETIC LAB** (wordmark `Kinetic/Lab`). Product: **Vector Racer 01** (SKU `vr-01`).
- Original brand. Do not add third-party sportswear names, logos, trademarked
  technology names or look-alike marks.
- Voice: short, technical, declarative. Numbers carry units (`174 g`, `39 mm`).

## 3. Tokens

| Token | Value | Use | Contrast on `#0A0A0A` |
|---|---|---|---|
| `--kl-bg` | `#0A0A0A` | Page background (Pure Dark Obsidian) | — |
| `--kl-surface` | `#121212` | Panels, drawer (Obsidian Enclosure) | — |
| `--kl-surface-2` | `#1A1A1A` | Raised controls, featured panel (Dark Charcoal Slate) | — |
| `--kl-line` | `#2A2A2A` | Decorative hairlines only | 1.4:1 (decorative) |
| `--kl-line-strong` | `#6B6B6B` | Edges of interactive controls | 3.7:1 (≥ 3:1 UI) |
| `--kl-text` | `#FFFFFF` | Headings, primary text | 19.8:1 |
| `--kl-muted` | `#A3A3A3` | Technical descriptions, labels | 7.8:1 |
| `--kl-volt` | `#D4FF00` | Accent — see rule below | 17.1:1 |
| `--kl-on-volt` | `#0A0A0A` | Text on volt fills | 17.1:1 |

**Volt rule.** `#D4FF00` appears only on: checked/active states, interactive
control hovers, focus rings, the cart badge, validation badges and the progress
fill. Never on body text, headings, static decoration or backgrounds. The shoe
upper fill is product data (the colorway), not a UI accent.

Text on a volt fill is always `#0A0A0A`. Never white on volt.

Tailwind mirrors the tokens as `obsidian`, `enclosure`, `slate`, `line`, `muted`, `volt`.

## 4. Type

- UI: system sans stack (`Inter` if installed locally, else `system-ui`).
- Display (`.kl-display`): weight 900, italic, uppercase, `-0.04em` tracking, 0.92 line height.
- Data (`.kl-mono`): system monospace, `+0.06em`, tabular numbers.
- Labels (`.kl-label`): 12 px, 600, `0.14em`, uppercase, muted.
- Minimum body size 14 px. Inputs and stepper values 16 px or larger.

## 5. Components

### 5.1 Navigation
- `header.kl-glass`, sticky, 72 px, `backdrop-filter: saturate(160%) blur(18px)` with an opaque fallback.
- Asymmetric grid `auto | 1fr | auto`: wordmark left, nav pushed right, cart last.
- Cart button: `aria-haspopup="dialog"`, `aria-controls`, `aria-expanded`, and an
  `aria-label` that carries the live count (`Open bag, 3 items`). The visual badge is `aria-hidden`.
- Badge scales from 0 → 1 when the bag becomes non-empty and pops on every increase.

### 5.2 Configurator
- Left: `figure.kl-hud` with grid background, corner brackets, four readouts and an inline SVG
  silhouette (`role="img"`, `<title>` + `<desc>`). The upper path `#shoe-upper` takes the colorway fill.
- Right: two radio groups built from `<button role="radio">` inside `role="radiogroup"`.
  - `aria-checked` is the single source of truth for selection and styling.
  - Roving tabindex: one tab stop per group. Arrow keys move and select; Home/End jump; Space/Enter select.
  - Sold-out sizes use `aria-disabled="true"` and are skipped by arrow keys.
- Pricing (centavos, integers):
  - Base `1449500` → **₱14,495.00**
  - White colorway `+50000` (₱500.00)
  - US 12 and US 13 `+30000` (₱300.00)
  - Formatted with `Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' })`.
  - The price element sits in an `aria-live="polite"` region.
- Add to bag without a size: the size group gets a dashed edge, an inline `role="alert"`
  message appears and focus moves to the first available size.

### 5.3 Telemetry bento
- `.kl-bento-wrap` is `container-type: inline-size` (`telemetry`). Layout is driven only by
  `@container telemetry` — no media queries and no resize listeners.
  - `< 640px`: one column.
  - `≥ 640px`: two columns, foam and plate full width.
  - `≥ 1024px`: four columns, foam spans two rows.
- Each `.kl-panel` is itself a container (`panel`); the plate profile switches from stacked to a row at `≥ 720px`.
- Specs: Base mass **174 g** · Zonal elasticity **84.2 %** · Supercritical PEBA foam (39 mm heel / 31 mm forefoot) · Carbon plate coverage **92 %**.
- The meter is `role="progressbar"` with `aria-valuemin/max/now/valuetext`; it animates once on
  first view and jumps straight to the value under `prefers-reduced-motion`.

### 5.4 Cart drawer
- `aside role="dialog" aria-modal="true" aria-labelledby="cart-title"`.
- On open: header, main and footer get `inert`, body scroll locks, focus moves to Close.
- Tab is trapped inside; Escape and the scrim close it; focus returns to the element that opened it.
- Line items are keyed `id|color|size`. Adding an existing key increments quantity (max 5).
- Removal and quantity changes act on the key, never on an array index.
- After a removal, focus moves to the next remove button, or to Close when the bag is empty.
- Checkout summarises the order and states that no payment is collected.

## 6. State model

```
dispatch(action) → queue → reducer(state, action) → frozen state → afterChange → renderBag
```

- All bag mutations go through `dispatch`. Actions: `ADD`, `SET_QTY`, `REMOVE`, `HYDRATE`.
- The queue drains in arrival order inside one synchronous loop guarded by a `draining` flag,
  so re-entrant dispatches (events fired during a render) are applied after the current one, never interleaved.
- `reducer` is pure and returns new arrays; state is `Object.freeze`d.
- Persistence: `localStorage['kl.bag.v1']`, wrapped in `try/catch`. Hydrated rows are validated and
  re-priced from the catalogue, so a tampered stored price is ignored.
- DOM is built with `createElement` and `textContent` only. No `innerHTML`.

## 7. Accessibility (WCAG 2.1 AA)

- Contrast: every text pair ≥ 4.5:1; control edges and focus rings ≥ 3:1 (table in §3).
- Focus: `:focus-visible` → 3 px solid volt outline, 3 px offset, on every control.
- Targets: primary CTA 56 px tall; every other control ≥ 48 × 48 px.
- Skip link to `#main`. Landmarks: `header`, `nav[aria-label]`, `main`, `footer`, `aside[role=dialog]`.
- Status: price is `aria-live`; bag changes are announced through `#live`.
- Motion: everything respects `prefers-reduced-motion: reduce`; `forced-colors` keeps checked states visible.

## 8. Merge checklist

- [ ] No new colour outside §3. Volt used only per the volt rule.
- [ ] New text/background pairs measured ≥ 4.5:1 (≥ 3:1 for non-text UI).
- [ ] New controls ≥ 48 px, CTA ≥ 56 px, visible focus ring.
- [ ] New radios use `role="radio"` + `aria-checked` with roving tabindex.
- [ ] Layout changes inside the bento use `@container`, not `@media` or JS.
- [ ] Bag mutations only through `dispatch`; no `innerHTML`.
- [ ] Keyboard pass: tab through header → configurator → bento → drawer and back, Escape closes.
- [ ] Reduced-motion pass: no animation runs.
- [ ] Prices still render as `₱14,495.00` base, `₱14,995.00` White, `₱14,795.00` Volt US 12.
