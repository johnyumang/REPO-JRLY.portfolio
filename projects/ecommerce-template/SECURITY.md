# Security log

## Phase 1
- No auth, no forms that send data off-device. The newsletter form validates and stores locally only.
- `npm audit --omit=dev`: next@15.5.28 bundles a postcss version with build-time advisories (sourcemap file read / stringify XSS). These affect the build toolchain processing untrusted CSS, not the exported static site. Re-check when moving to Next 16 (planned before Phase 3).
- Security headers (CSP, HSTS, etc.) arrive with the live server in Phase 3; static hosts set them via `_headers` / `vercel.json`.
