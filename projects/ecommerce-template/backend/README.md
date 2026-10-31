# Backend — Medusa v2 (self-hosted, free)

Live-mode backend for the template: customer auth, cart, checkout, orders, admin dashboard.

## Run locally (Postgres 16 + Redis)
```bash
cp .env.template .env         # set DATABASE_URL, REDIS_URL, and random JWT_SECRET / COOKIE_SECRET (openssl rand -hex 32)
npm install
npx medusa db:migrate
npx medusa user -e admin@example.com -p '<choose a password>'
npm run dev                   # API on http://localhost:9000, admin on http://localhost:9000/app
```
Never commit `.env`. The storefront talks to the Store API at `NEXT_PUBLIC_API_URL` when `NEXT_PUBLIC_DATA_MODE=live`.
