# Security log

## Phase 1
- No auth, no forms that send data off-device. The newsletter form validates and stores locally only.
- `npm audit --omit=dev`: next@15.5.28 bundles a postcss version with build-time advisories (sourcemap file read / stringify XSS). These affect the build toolchain processing untrusted CSS, not the exported static site. Re-check when moving to Next 16 (planned before Phase 3).
- Security headers (CSP, HSTS, etc.) arrive with the live server in Phase 3; static hosts set them via `_headers` / `vercel.json`.

## Phase 2 (2026-10-31)
- Demo users store **PBKDF2-SHA256 (210,000 iterations, 16-byte random salt)** hashes only; verification is constant-time (`lib/crypto.ts`). Plain-text demo passwords live in README.md, never in the bundle.
- Every mock-API write is validated with **Zod 4** (`lib/api/contract.ts`): bounded strings, emails normalised to lower case, quantities 1–10, max 50 order lines, limit ≤ 100.
- **Prices are never trusted from the client**: order totals, shipping and unit prices are recomputed from IndexedDB; a test posts `unitPrice: 0.01` and gets the catalogue price back.
- Orders, tickets and sync replays are **idempotent** on `Idempotency-Key`; the duplicate check runs inside the write transaction so concurrent replays can't double-write.
- Text fields (e.g. ticket messages) are stored as-is and must be escaped at render (React does this by default); a test confirms XSS payloads stay inert data.
- `npm audit` after upgrading to vitest 5.0.5 and zod 4.6.7 (both were flagged in 3.x):
  | Package | Severity | Scope | Status |
  |---|---|---|---|
  | next → postcss | high/moderate | build-time only | Known from Phase 1; Next 16 upgrade before Phase 3 |
  | serve → compression, serve-handler, minimatch | high/moderate | dev-only local preview server | Not shipped; production uses a static host. Replace or drop in Phase 10 |
