// Converts /public/stock/*.jpg into responsive WebP (800w + 1400w) and writes CREDITS.md.
import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';
const dir = path.resolve('public/stock');
const map = JSON.parse(fs.readFileSync('content/stock-map.json', 'utf8'));
let credits = '# Stock image credits\n\nAll images: Unsplash (Unsplash License — free for commercial use, no attribution required). Placeholders only; replace with brand photography.\n\n| File | Source |\n|---|---|\n';
for (const [name, id] of Object.entries(map)) {
  const src = path.join(dir, `${id}.jpg`);
  for (const w of [800, 1400]) {
    await sharp(src).resize({ width: w }).webp({ quality: 74 }).toFile(path.join(dir, `${name}-${w}.webp`));
  }
  credits += `| ${name} | https://unsplash.com/photos/${id} |\n`;
}
for (const f of fs.readdirSync(dir)) if (f.endsWith('.jpg')) fs.unlinkSync(path.join(dir, f));
fs.writeFileSync(path.join(dir, 'CREDITS.md'), credits);
console.log('done', Object.keys(map).length);
