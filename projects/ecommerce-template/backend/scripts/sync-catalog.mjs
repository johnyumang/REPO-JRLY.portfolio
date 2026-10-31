// Copies the storefront catalogue (../content/catalog.ts) into src/data so the backend builds on its own
// (Docker, Render) and the seed stays identical to the offline storefront. Runs before build/seed/dev.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const src = path.resolve(here, '../../content/catalog.ts');
const dest = path.resolve(here, '../src/data/catalog.ts');
// Stock photos are bundled into the image (served at /static/stock). Not committed: copied at build time.
const stockSrc = path.resolve(here, '../../public/stock');
const stockDest = path.resolve(here, '../static/stock');
if (fs.existsSync(stockSrc)) {
  fs.mkdirSync(stockDest, { recursive: true });
  const files = fs.readdirSync(stockSrc).filter((f) => f.endsWith('.webp'));
  for (const f of files) fs.copyFileSync(path.join(stockSrc, f), path.join(stockDest, f));
  console.log(`sync-catalog: ${files.length} stock images -> static/stock`);
}
if (!fs.existsSync(src)) { console.log('sync-catalog: storefront catalogue not found, keeping committed copy'); process.exit(0); }
const header = '// GENERATED from ../../content/catalog.ts by scripts/sync-catalog.mjs — edit the storefront file, not this one.\n';
const next = header + fs.readFileSync(src, 'utf8');
if (!fs.existsSync(dest) || fs.readFileSync(dest, 'utf8') !== next) { fs.writeFileSync(dest, next); console.log('sync-catalog: updated src/data/catalog.ts'); }
else console.log('sync-catalog: up to date');
