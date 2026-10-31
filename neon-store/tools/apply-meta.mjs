#!/usr/bin/env node
/* Rewrites the <!-- meta:start --> … <!-- meta:end --> block in every page
   from SITE.seo + SITE.brand in assets/js/config.js, and regenerates
   sitemap.xml and robots.txt. Zero dependencies. Safe to run repeatedly.

   Usage (from the repo root):  node tools/apply-meta.mjs                  */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const sandbox = { window: {} };
vm.runInNewContext(readFileSync(join(root, 'assets/js/config.js'), 'utf8'), sandbox);
const S = sandbox.window.SITE;
const base = S.brand.siteUrl.replace(/\/+$/, '');
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
const fill = (s) => String(s).replace(/\{brand\}/g, S.brand.name).replace(/\[BRAND NAME\]/g, S.brand.name);

const pages = Object.keys(S.seo);
for (const page of pages) {
  const file = join(root, page);
  if (!existsSync(file)) { console.warn('skip (missing):', page); continue; }
  const m = S.seo[page];
  const url = page === 'index.html' ? base + '/' : base + '/' + page;
  const title = fill(m.title), desc = fill(m.description);
  const block = [
    '<!-- meta:start (managed by tools/apply-meta.mjs) -->',
    `  <title>${esc(title)}</title>`,
    `  <meta name="description" content="${esc(desc)}">`,
    m.noindex ? '  <meta name="robots" content="noindex">' : `  <link rel="canonical" href="${esc(url)}">`,
    `  <meta property="og:type" content="${esc(m.type || 'website')}">`,
    `  <meta property="og:site_name" content="${esc(S.brand.name)}">`,
    `  <meta property="og:title" content="${esc(title)}">`,
    `  <meta property="og:description" content="${esc(desc)}">`,
    `  <meta property="og:url" content="${esc(url)}">`,
    `  <meta property="og:image" content="${esc(base + '/' + m.image)}">`,
    '  <meta name="twitter:card" content="summary_large_image">',
    '  <!-- meta:end -->'
  ].join('\n');
  const html = readFileSync(file, 'utf8');
  const next = html.replace(/<!-- meta:start[\s\S]*?<!-- meta:end -->/, block);
  if (next === html && !html.includes('meta:start')) console.warn('no meta block in', page);
  writeFileSync(file, next);
  console.log('updated', page);
}

const urls = pages.filter((p) => !S.seo[p].noindex)
  .map((p) => `  <url><loc>${esc(p === 'index.html' ? base + '/' : base + '/' + p)}</loc></url>`)
  .concat(S.products.map((p) => `  <url><loc>${esc(base + '/product.html?id=' + encodeURIComponent(p.id))}</loc></url>`));
writeFileSync(join(root, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`);
writeFileSync(join(root, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`);
console.log('wrote sitemap.xml and robots.txt');
