#!/usr/bin/env bash
# One-command Medusa install for an Oracle Cloud Always Free Ubuntu VM (ARM or x86).
# Safe to re-run: it updates the code and restarts without wiping data or secrets.
#
# Usage (as the Oracle "initialization script", or over SSH):
#   ADMIN_EMAIL=you@example.com ADMIN_PASSWORD='choose-a-strong-one' \
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/johnyumang/REPO-JRLY.portfolio/main/ops/deploy/oracle/install.sh)"
set -euo pipefail

REPO_URL="https://github.com/johnyumang/REPO-JRLY.portfolio.git"
APP_BRANCH="${APP_BRANCH:-claude/ecommerce-template-phase3}"
OPS_BRANCH="${OPS_BRANCH:-main}"
ROOT=/opt/jrly
LOG=/var/log/jrly-install.log
exec > >(tee -a "$LOG") 2>&1
echo "=== JRLY Medusa install $(date -u) ==="

[ "$(id -u)" = 0 ] || { echo "Run as root (sudo)."; exit 1; }

# 1. Docker
if ! command -v docker >/dev/null; then
  echo "[1/6] installing Docker"
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

# 2. Open ports 80/443 in the VM firewall (Oracle Ubuntu images block them by default)
echo "[2/6] opening ports 80 and 443"
for p in 80 443; do
  iptables -C INPUT -p tcp --dport $p -j ACCEPT 2>/dev/null || iptables -I INPUT 5 -p tcp --dport $p -j ACCEPT
done
command -v netfilter-persistent >/dev/null && netfilter-persistent save || true

# 3. Code: backend from the app branch, deploy files from main
echo "[3/6] fetching code"
mkdir -p $ROOT
if [ -d $ROOT/app/.git ]; then git -C $ROOT/app pull -q; else git clone -q --depth 1 -b "$APP_BRANCH" "$REPO_URL" $ROOT/app; fi
if [ -d $ROOT/ops/.git ]; then git -C $ROOT/ops pull -q; else git clone -q --depth 1 -b "$OPS_BRANCH" "$REPO_URL" $ROOT/ops; fi
APP_SRC=$ROOT/app/projects/ecommerce-template
DEPLOY_DIR=$ROOT/ops/ops/deploy/oracle
cp $DEPLOY_DIR/entrypoint.sh $APP_SRC/entrypoint.sh
cp $DEPLOY_DIR/dockerignore $APP_SRC/.dockerignore
cp $DEPLOY_DIR/Dockerfile $APP_SRC/Dockerfile

# 4. Secrets + public address (written once, kept on re-runs)
echo "[4/6] configuring"
IP=$(curl -fsS https://api.ipify.org)
PUBLIC_HOST="${PUBLIC_HOST:-${IP//./-}.sslip.io}"
ENV=$ROOT/.env
if [ ! -f $ENV ]; then
  rnd() { openssl rand -hex 32; }
  cat > $ENV <<EOF
APP_SRC=$APP_SRC
DEPLOY_DIR=$DEPLOY_DIR
PUBLIC_HOST=$PUBLIC_HOST
POSTGRES_PASSWORD=$(openssl rand -hex 16)
JWT_SECRET=$(rnd)
COOKIE_SECRET=$(rnd)
STORE_NAME=JRLY
STOREFRONT_URL=https://johnyumang.github.io/REPO-JRLY.portfolio
MEDUSA_BACKEND_URL=https://$PUBLIC_HOST
STORE_CORS=https://johnyumang.github.io,http://localhost:3000
ADMIN_CORS=https://$PUBLIC_HOST
AUTH_CORS=https://johnyumang.github.io,https://$PUBLIC_HOST,http://localhost:3000
DISABLE_MEDUSA_ADMIN=false
ADMIN_EMAIL=${ADMIN_EMAIL:-}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-}
EOF
  chmod 600 $ENV
fi
ln -sf $DEPLOY_DIR/docker-compose.yml $ROOT/docker-compose.yml

# 5. Build + start (first build takes ~5–10 min on the free ARM VM)
echo "[5/6] building and starting (this takes a few minutes)"
cd $ROOT
docker compose --env-file $ENV up -d --build

# 6. Wait for health
echo "[6/6] waiting for Medusa"
for i in $(seq 1 90); do
  if curl -fsS "https://$PUBLIC_HOST/health" >/dev/null 2>&1; then
    echo
    echo "=============================================="
    echo " Medusa is LIVE"
    echo " Admin:  https://$PUBLIC_HOST/app"
    echo " API:    https://$PUBLIC_HOST/store"
    echo " Health: https://$PUBLIC_HOST/health"
    echo " Login:  the ADMIN_EMAIL / ADMIN_PASSWORD you set"
    echo "=============================================="
    # Clear the plain-text admin password from disk now that the user exists.
    sed -i 's/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=/' $ENV
    exit 0
  fi
  sleep 10
done
echo "Not healthy after 15 min. Check: docker compose -f $ROOT/docker-compose.yml logs --tail 100 medusa"
exit 1
