// Post-build: precache every exported file so the whole site works offline after first visit.
import fs from 'node:fs';
import path from 'node:path';
const out = path.resolve('out');
const files = [];
(function walk(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); fs.statSync(p).isDirectory() ? walk(p) : files.push('/' + path.relative(out, p).split(path.sep).join('/')); } })(out);
const urls = files.filter((f) => !f.endsWith('.map') && !f.endsWith('.txt') && f !== '/sw.js' && !f.endsWith('CREDITS.md'))
  .map((f) => (f.endsWith('/index.html') ? f.slice(0, -10) || '/' : f));
const version = Date.now().toString(36);
const sw = `const C='tpl-${version}';const URLS=${JSON.stringify(urls)};
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(URLS)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;
if(r.mode==='navigate'){e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(C).then(c=>c.put(r,cp));return res}).catch(()=>caches.match(r,{ignoreSearch:true}).then(m=>m||caches.match('/'))));return}
e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{const cp=res.clone();caches.open(C).then(c=>c.put(r,cp));return res})))});`;
fs.writeFileSync(path.join(out, 'sw.js'), sw);
console.log(`sw.js: precaching ${urls.length} files`);
