#!/bin/sh
# Start-up for free hosting. Setup (migrate + seed + admin) runs only when this image version hasn't
# set the database up yet, so normal wake-ups go straight to `medusa start`.
set -e
cd /app
SETUP="${RUN_SETUP_ON_BOOT:-auto}"   # auto | true | false
if [ "$SETUP" = "auto" ] && node boot-check.js; then
  echo "[boot] database already set up for image ${IMAGE_VERSION:-dev}, skipping setup"
elif [ "$SETUP" != "false" ]; then
  echo "[boot] migrating database..."
  npx medusa db:migrate
  echo "[boot] seeding store and admin (skips what already exists)..."
  npx medusa exec ./src/scripts/bootstrap.js
  node boot-check.js --mark || true
fi
echo "[boot] starting Medusa on port ${PORT:-9000}"
exec npx medusa start --port "${PORT:-9000}"
