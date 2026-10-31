#!/bin/sh
# Runs on every container start: migrate → (first run only) seed + admin → start.
set -e
cd /app/backend/.medusa/server

echo "[jrly] running migrations"
npx medusa db:migrate

if [ ! -f /data/.seeded ]; then
  echo "[jrly] first run: seeding catalogue"
  (cd /app/backend && npm run seed)
  if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "[jrly] creating admin user $ADMIN_EMAIL"
    npx medusa user -e "$ADMIN_EMAIL" -p "$ADMIN_PASSWORD" || echo "[jrly] admin user already exists"
  fi
  touch /data/.seeded
fi

echo "[jrly] starting Medusa"
exec npm run start
