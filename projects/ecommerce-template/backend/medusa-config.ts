import { loadEnv, defineConfig, Modules } from '@medusajs/framework/utils'

loadEnv(process.env.NODE_ENV || 'development', process.cwd())

const isProd = process.env.NODE_ENV === 'production'

// Fail fast in production instead of silently running with a guessable secret.
function secret(name: 'JWT_SECRET' | 'COOKIE_SECRET') {
  const value = process.env[name]
  if (isProd && (!value || value.length < 32 || value.startsWith('change-me'))) {
    throw new Error(`${name} must be set to a random value of at least 32 characters in production`)
  }
  return value || 'dev-only-secret-not-for-production'
}

// Redis is optional locally (in-memory fallbacks) and recommended in production.
const redisUrl = process.env.REDIS_URL
const redisModules = redisUrl
  ? [
      { key: Modules.EVENT_BUS, resolve: '@medusajs/medusa/event-bus-redis', options: { redisUrl } },
      { key: Modules.WORKFLOW_ENGINE, resolve: '@medusajs/medusa/workflow-engine-redis', options: { redis: { redisUrl } } },
      { key: Modules.LOCKING, resolve: '@medusajs/medusa/locking', options: { providers: [{ resolve: '@medusajs/medusa/locking-redis', id: 'locking-redis', is_default: true, options: { redisUrl } }] } },
    ]
  : []

module.exports = defineConfig({
  projectConfig: {
    databaseUrl: process.env.DATABASE_URL,
    redisUrl,
    workerMode: (process.env.MEDUSA_WORKER_MODE as 'shared' | 'worker' | 'server') || 'shared',
    http: {
      storeCors: process.env.STORE_CORS!,
      adminCors: process.env.ADMIN_CORS!,
      authCors: process.env.AUTH_CORS!,
      jwtSecret: secret('JWT_SECRET'),
      cookieSecret: secret('COOKIE_SECRET'),
    },
  },
  admin: {
    disable: process.env.DISABLE_MEDUSA_ADMIN === 'true',
    backendUrl: process.env.MEDUSA_BACKEND_URL,
  },
  modules: redisModules,
})
