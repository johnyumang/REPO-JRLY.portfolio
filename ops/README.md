# Ops — one place to see and recall everything

**Status board (one look):** https://johnyumang.github.io/REPO-JRLY.portfolio/status/

The board shows three things:
1. **Systems:** every site, branch, PR and server, checked automatically every hour. Each one shows green **OK**, amber **Needs attention** or red **Problem**, with a one-line **Fix**.
2. **Kaizen board:** continuous-improvement cards in Backlog → Doing → Done, sorted by priority.
3. **Work log:** what changed, when, and where it lives.

## Files

| File | What it is | How to change it |
|---|---|---|
| `ops/systems.json` | Registry of every system and its checks | Add a block, and it appears on the board on the next run |
| `ops/kaizen.json` | Kaizen cards | Change `"column"` to `backlog`, `doing` or `done` |
| `ops/log.json` | One-line work log, newest first | Add an entry after every meaningful change |
| `ops/log/<date>.md` | Detailed session notes | One file per working day |
| `ops/HANDOVER.md` | Handover from the earlier sessions | Read-only history |
| `ops/check.mjs` | Health-check script (no dependencies) | `node ops/check.mjs` runs it locally |
| `ops/status-page/index.html` | The board page | Published to `gh-pages/status/` by the workflow |
| `.github/workflows/status.yml` | Runs hourly, on every push to `ops/`, or manually | Actions → **Status board** → **Run workflow** |

Everything here is free: public repo, GitHub Actions minutes and GitHub Pages.

## Rules that keep it recallable

0. **John is never the bottleneck (hard rule).** Claude does every step it can. John only gets what physically needs him: identity, card or payment checks, account approvals and secrets. Those are batched into as few one-time steps as possible.

1. Every change gets a line in `ops/log.json`. Bigger work also gets notes in `ops/log/<date>.md`.
2. Every new system gets an entry in `ops/systems.json`, with a check if it has a URL, branch or PR.
3. Every to-do becomes a Kaizen card. Nothing lives only in chat.
4. **Secrets never go in the repo or the chat.** Keys and passwords go in GitHub → Settings → Secrets, or in a local `.env` that is git-ignored. Credentials are handed over as files.

## Where each project lives

| Project | Location |
|---|---|
| Neon store (live) | `gh-pages` → `/neon-store/` |
| Status board (live) | `gh-pages` → `/status/` (source in `main/ops/`) |
| Kinetic Lab page | `main` → `projects/kinetic-lab/` |
| E-commerce template + Medusa backend | `claude/ecommerce-template-phase1/2/3` branches → `projects/ecommerce-template/` |
| Portfolio site | `claude/practical-knuth-is7590` |
| Phase 3 auth designs | Claude Design canvas (link in `systems.json`) |
