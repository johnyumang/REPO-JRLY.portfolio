// Zero-dependency static server for the exported site: node scripts/serve.mjs [port]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve('out');
const port = Number(process.argv[2] ?? process.env.PORT ?? 3000);
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webmanifest': 'application/manifest+json',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff', '.txt': 'text/plain', '.xml': 'application/xml' };

function resolve(urlPath) {
  const clean = path.normalize(decodeURIComponent(urlPath.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
  const file = path.join(root, clean);
  if (!file.startsWith(root)) return null; // path traversal guard
  for (const f of [file, path.join(file, 'index.html'), `${file}.html`]) if (fs.existsSync(f) && fs.statSync(f).isFile()) return f;
  return null;
}

http.createServer((req, res) => {
  let file; try { file = resolve(req.url ?? '/'); } catch { file = null; }
  const status = file ? 200 : 404;
  file ??= path.join(root, '404.html');
  res.writeHead(status, { 'Content-Type': types[path.extname(file)] ?? 'application/octet-stream', 'Cache-Control': file.endsWith('sw.js') ? 'no-cache' : 'public, max-age=0' });
  fs.createReadStream(file).pipe(res);
}).listen(port, () => console.log(`Serving out/ on http://localhost:${port}`));
