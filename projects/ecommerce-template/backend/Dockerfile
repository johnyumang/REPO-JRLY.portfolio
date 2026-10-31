# JRLY Medusa backend — API + admin dashboard in one small image.
# Built by GitHub Actions (free) and pulled by Render's free tier, so Render never has to run the
# memory-hungry admin build itself.

FROM node:22-bookworm-slim AS build
WORKDIR /app
ENV MEDUSA_DISABLE_TELEMETRY=true
COPY package.json package-lock.json .npmrc ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npx medusa build

FROM node:22-bookworm-slim
ARG IMAGE_VERSION=dev
WORKDIR /app
ENV IMAGE_VERSION=$IMAGE_VERSION \
    NODE_ENV=production \
    MEDUSA_DISABLE_TELEMETRY=true \
    MEDUSA_WORKER_MODE=shared \
    NODE_OPTIONS=--max-old-space-size=384 \
    PORT=9000
RUN chown node:node /app
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
USER node
COPY --chown=node:node --from=build /app/.medusa/server ./
COPY --chown=node:node --from=build /app/static ./static
COPY --chown=node:node boot-check.js ./boot-check.js
RUN npm ci --omit=dev --no-audit --no-fund && npm cache clean --force
EXPOSE 9000
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||9000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["docker-entrypoint.sh"]
