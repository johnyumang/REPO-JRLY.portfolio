// usage: node render_stills.mjs <shots.mjs> <outdir> [ids comma list]   (run a static server on :8765 in this folder first)
import {chromium} from 'playwright';
import {pathToFileURL} from 'url';
import path from 'path';
import fs from 'fs';
const [shotsFile, outDir, only] = process.argv.slice(2);
const {SHOTS} = await import(pathToFileURL(path.resolve(shotsFile)).href);
fs.mkdirSync(outDir, {recursive: true});
const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const p = await b.newPage({viewport: {width: 1080, height: 1920}});
p.on('pageerror', e => console.log('PAGEERR', e.message));
await p.goto('http://127.0.0.1:8765/stage.html'); await p.waitForFunction('window.ready === true', null, {timeout: 120000});
const want = only ? new Set(only.split(',')) : null;
for (const s of SHOTS) { if (want && !want.has(s.id)) continue;
  await p.evaluate(spec => window.renderShot(spec), s.scene); await p.screenshot({path: path.join(outDir, s.id + '.png')}); console.log('still', s.id); }
fs.writeFileSync(path.join(outDir, 'shots_meta.json'), JSON.stringify(SHOTS.map(({id, at, camera, caption, bottom}) => ({id, at, camera, caption, bottom})), null, 1));
await b.close();
