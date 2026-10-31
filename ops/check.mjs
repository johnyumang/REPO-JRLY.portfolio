#!/usr/bin/env node
// Builds ops/status.json from systems.json + kaizen.json + log.json.
// Zero dependencies (Node 20+). Runs hourly in GitHub Actions; also works locally:
//   node ops/check.mjs            (writes ops/status-page/status.json)
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const read = (f) => JSON.parse(readFileSync(join(here, f), 'utf8'));
const reg = read('systems.json');
const kaizen = read('kaizen.json');
const log = read('log.json');
const token = process.env.GITHUB_TOKEN;
const api = (path) => fetch('https://api.github.com/repos/' + reg.repo + path, {
  headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'jrly-status', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
  signal: AbortSignal.timeout(15000)
});
const day = (iso) => (iso ? iso.slice(0, 10) : '');

async function run(check) {
  try {
    if (check.type === 'http') {
      const t0 = Date.now();
      const r = await fetch(check.url, { redirect: 'follow', signal: AbortSignal.timeout(15000), headers: { 'User-Agent': 'jrly-status' } });
      const ms = Date.now() - t0;
      return { label: check.label, state: r.ok ? (ms > 5000 ? 'warn' : 'ok') : 'down', detail: `HTTP ${r.status} · ${ms} ms` };
    }
    if (check.type === 'branch') {
      const r = await api('/branches/' + encodeURIComponent(check.branch));
      if (r.status === 404) return { label: check.label, state: 'down', detail: 'branch not found on GitHub' };
      if (!r.ok) return { label: check.label, state: 'warn', detail: `GitHub API ${r.status}` };
      const b = await r.json();
      return { label: check.label, state: 'ok', detail: 'last commit ' + day(b.commit?.commit?.committer?.date) };
    }
    if (check.type === 'pr') {
      const r = await api('/pulls/' + check.number);
      if (!r.ok) return { label: check.label, state: 'warn', detail: `GitHub API ${r.status}` };
      const p = await r.json();
      if (p.merged_at) return { label: check.label, state: 'ok', detail: 'merged ' + day(p.merged_at) };
      if (p.state === 'open') return { label: check.label, state: 'warn', detail: `open since ${day(p.created_at)} · waiting for your review` + (p.mergeable === false ? ' · has conflicts' : '') };
      return { label: check.label, state: 'down', detail: 'closed without merging' };
    }
    return { label: check.label, state: check.state || 'warn', note: check.note };
  } catch (e) {
    return { label: check.label, state: 'down', detail: 'check failed: ' + (e.name === 'TimeoutError' ? 'timeout' : e.message) };
  }
}

const rank = { ok: 0, warn: 1, down: 2 };
const systems = [];
for (const s of reg.systems) {
  const checks = [];
  for (const c of s.checks) checks.push({ ...(await run(c)), ...(c.note ? { note: c.note } : {}) });
  const state = checks.reduce((w, c) => (rank[c.state] > rank[w] ? c.state : w), 'ok');
  systems.push({ id: s.id, name: s.name, kind: s.kind, where: s.where, link: s.link, fix: s.fix, state, checks });
}

const out = { generatedAt: new Date().toISOString(), repo: reg.repo, systems, kaizen, log: log.entries };
const dest = process.argv[2] || join(here, 'status-page', 'status.json');
writeFileSync(dest, JSON.stringify(out, null, 2));
const c = systems.reduce((a, s) => (a[s.state]++, a), { ok: 0, warn: 0, down: 0 });
console.log(`status: ${c.ok} ok · ${c.warn} attention · ${c.down} problem → ${dest}`);
