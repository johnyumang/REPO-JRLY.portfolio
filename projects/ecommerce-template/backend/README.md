# JRLY backend — Medusa v2.22.2 (self-hosted, free)

Live-mode backend for the storefront: catalogue, cart, checkout, customer auth, orders, admin dashboard.

## What `npm run seed` configures
| Setting | Value |
|---|---|
| Store name | `JRLY` (`STORE_NAME`) |
| Currency | EUR (matches storefront € prices) |
| Region | Europe: DE, FR, ES, IT, NL, BE, AT, IE, PT · system tax provider · manual payment provider |
| Sales channel | Webshop, linked to the publishable key and warehouse |
| Stock location | JRLY Warehouse (`[CITY]`, `[ADDRESS]` placeholders) |
| Shipping | Standard €4.95, **free from €50** (price rule on `item_total`) · Express €9.95 |
| Catalogue | 8 categories + 48 products / 284 variants (Color × Size) imported from `../content/catalog.ts`, same SKUs, prices and stock as the offline storefront |
| Images | `${STOREFRONT_URL}/stock/<key>-1400.webp` (served by the storefront) |

The seed runs once (it marks the store `metadata.jrly_seeded`) and prints the **publishable key** for the storefront's `NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY`.

## Run locally (Postgres 16 + Redis)
```bash
cp .env.template .env        # then set random JWT_SECRET / COOKIE_SECRET
npm install
npx medusa db:migrate
npm run seed
npx medusa user -e admin@example.com -p '<choose a password>'
npm run dev                  # API http://localhost:9000 · admin http://localhost:9000/app
```

## Configuration (`medusa-config.ts`)
- **Secrets fail fast:** with `NODE_ENV=production` the server refuses to start unless `JWT_SECRET` and `COOKIE_SECRET` are random values of 32+ characters.
- **Redis is optional:** when `REDIS_URL` is set, the event bus, workflow engine and locking use Redis; otherwise Medusa's in-memory/Postgres defaults.
- `MEDUSA_WORKER_MODE=shared` runs API and background jobs in one process (best for one free instance).
- `DISABLE_MEDUSA_ADMIN=true` serves the API only.

## Verified (2026-10-31)
| Check | Result |
|---|---|
| Store API product count | 48 |
| Categories | new-in, women, men, outerwear, knitwear, basics, dresses, trousers |
| Price + stock parity with storefront | e.g. `essential-white-tee-white-xs` €19, stock 18 |
| Shipping on €19 cart | Standard €4.95 · Express €9.95 |
| Shipping on €57 cart | Standard €0 · Express €9.95 |
| Add more than stock | rejected ("required inventory") |
| Store API without publishable key | 400 |
| Admin login, wrong password | 401 |

## Free hosting (always-free rule)
Medusa needs one Node process + Postgres (+ Redis optional). Options that stay free:
- **Your own machine or VPS you already have** — most reliable.
- **Free-tier web service + free Postgres** (e.g. Render free web + Neon free Postgres): free, but sleeps when idle and has small limits. Fine for demos.
Never commit `.env`. Rotate secrets if they ever leak.
