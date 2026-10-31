# Medusa v2 backend (JRLY) — multi-arch (works on Oracle Ampere ARM and x86).
# Build context: projects/ecommerce-template (the seed script imports ../content/catalog.ts).
FROM node:22-bookworm-slim

ENV NODE_OPTIONS=--max-old-space-size=3072 \
    NEXT_TELEMETRY_DISABLED=1 \
    MEDUSA_DISABLE_TELEMETRY=true

ARG MEDUSA_BACKEND_URL
ENV MEDUSA_BACKEND_URL=${MEDUSA_BACKEND_URL}

WORKDIR /app
COPY content ./content
COPY backend ./backend

WORKDIR /app/backend
# Full install (dev deps are needed for the TypeScript seed script), then production build.
# The seed script imports ../content (outside the backend rootDir), which breaks `medusa build`,
# so it is set aside during the build and run from source on first start instead.
RUN npm ci --no-audit --no-fund \
 && mv src/scripts/seed.ts /tmp/seed.ts && npx medusa build && mv /tmp/seed.ts src/scripts/seed.ts \
 && cd .medusa/server && npm install --omit=dev --no-audit --no-fund

# install.sh copies this Dockerfile, entrypoint.sh and .dockerignore into the build context
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 9000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
