// Visual + button-spec + offline checks. Usage: node scripts/screenshots.mjs [baseUrl]
import { createRequire } from 'node:module';
import fs from 'node:fs';
const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch { pw = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright'); }
const BASE = process.argv[2] || 'http://localhost:3000';
const OUT = 'screenshots'; fs.mkdirSync(OUT, { recursive: true });
const routes = { home: '/', collection: '/collections/new-in/', product: '/products/leather-biker-jacket/' };
const widths = { mobile: 390, desktop: 1440 };
const browser = await pw.chromium.launch();
const results = [];
for (const theme of ['dark', 'light']) for (const [vw, w] of Object.entries(widths)) {
  const ctx = await browser.newContext({ viewport: { width: w, height: w < 500 ? 844 : 900 }, deviceScaleFactor: 1, reducedMotion: 'reduce' });
  await ctx.addInitScript((t) => localStorage.setItem('tpl.theme', t), theme);
  const page = await ctx.newPage();
  for (const [name, path] of Object.entries(routes)) {
    await page.goto(BASE + path, { waitUntil: 'networkidle' });
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); } window.scrollTo(0, 0); });
    await page.waitForTimeout(400);
    await page.screenshot({ path: `${OUT}/${name}-${theme}-${vw}.png`, fullPage: true });
    // Button spec: primary CTAs >= 56px tall; all buttons/links used as controls >= 48px tap height
    const sizes = await page.evaluate(() => {
      const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && !e.closest('[aria-hidden="true"]'); };
      const cta = [...document.querySelectorAll('.btn-primary')].filter(vis).map((e) => ({ t: e.textContent.trim(), h: e.getBoundingClientRect().height }));
      const tap = [...document.querySelectorAll('button, .btn-secondary, select')].filter(vis).map((e) => ({ t: (e.getAttribute('aria-label') || e.textContent).trim().slice(0, 30), h: e.getBoundingClientRect().height, w: e.getBoundingClientRect().width }));
      return { cta, tap };
    });
    const badCta = sizes.cta.filter((b) => b.h < 56);
    const badTap = sizes.tap.filter((b) => b.h < 48 - 0.5);
    results.push({ theme, vw, name, ctas: sizes.cta.length, badCta, badTap });
  }
  await ctx.close();
}
// Offline: load once (SW installs), cut network, navigate everywhere.
const ctx = await browser.newContext({ serviceWorkers: 'allow' });
const page = await ctx.newPage();
await page.goto(BASE + '/', { waitUntil: 'networkidle' });
await page.evaluate(() => navigator.serviceWorker.ready);
await page.waitForTimeout(1500);
await page.reload({ waitUntil: 'networkidle' });
await ctx.setOffline(true);
const offline = [];
for (const p of [...Object.values(routes), '/collections/outerwear/', '/products/wool-check-coat/', '/account/']) {
  try { const r = await page.goto(BASE + p, { waitUntil: 'load' }); const h1 = await page.locator('h1').first().textContent(); const imgs = await page.evaluate(() => [...document.images].filter((i) => i.complete && i.naturalWidth === 0).length); offline.push({ p, ok: !!r && r.ok(), h1: h1?.trim().replace(/\s+/g, ' '), brokenImgs: imgs }); }
  catch (e) { offline.push({ p, ok: false, err: String(e).slice(0, 80) }); }
}
// Offline interaction: add to bag
await page.goto(BASE + '/products/essential-white-tee/');
await page.getByRole('button', { name: 'M', exact: true }).click();
await page.getByTestId('add-to-bag').click();
await page.waitForTimeout(800);
const bagCount = await page.evaluate(() => JSON.parse(localStorage.getItem('tpl.bag.v1') || '[]').length);
await browser.close();
const report = { results, offline, offlineAddToBag: bagCount === 1 };
fs.writeFileSync(`${OUT}/report.json`, JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 1));
