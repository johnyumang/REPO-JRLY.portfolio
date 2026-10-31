// Skips migrations + seeding on wake-ups when this exact image version already set the database up.
// Free Render instances sleep after 15 min; without this every wake-up would re-run setup (~5 min on 0.1 CPU).
//   node boot-check.js         -> exit 0 = already set up for IMAGE_VERSION, exit 1 = run setup
//   node boot-check.js --mark  -> record IMAGE_VERSION after a successful setup
const { Client } = require('pg');
const version = process.env.IMAGE_VERSION || 'dev';
const client = new Client({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_SSL === 'true' ? { rejectUnauthorized: false } : undefined,
});
(async () => {
  await client.connect();
  await client.query('create table if not exists jrly_boot (id int primary key, version text not null, at timestamptz default now())');
  if (process.argv.includes('--mark')) {
    await client.query('insert into jrly_boot (id, version) values (1, $1) on conflict (id) do update set version = $1, at = now()', [version]);
    console.log(`[boot] setup recorded for image ${version}`);
    return 0;
  }
  const { rows } = await client.query('select version from jrly_boot where id = 1');
  return rows[0]?.version === version && version !== 'dev' ? 0 : 1;
})()
  .then(async (code) => { await client.end(); process.exit(code); })
  .catch(async (e) => { console.error('[boot] check failed, running setup:', e.message); try { await client.end(); } catch {} process.exit(1); });
