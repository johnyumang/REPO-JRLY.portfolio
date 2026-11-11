import {chromium} from 'playwright';
const styles = process.argv[2].split(',');
const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
const p = await b.newPage({viewport: {width: 1080, height: 1920}});
p.on('console', m => { if (m.type() === 'error') console.log('ERR', m.text()); });
p.on('pageerror', e => console.log('PAGEERR', e.message));
for (const s of styles) {
  await p.goto(`http://127.0.0.1:8765/index.html?style=${s}`);
  await p.waitForFunction('window.ready === true', null, {timeout: 120000});
  await p.screenshot({path: `out_${s}.png`});
  console.log('shot', s);
}
await b.close();
