# astra

**A**gent **S**kill **T**ransfer & **R**egistry **A**pp — an intranet web service where colleagues browse curated agent skills (rendered `SKILL.md` is the sales page), decide to adopt, and install by pasting **one command** — no git, no GitHub, anywhere in the flow.

> **alias:** `astra`

---

## Docs in this project

- **CONTEXT.md** — start here: current state + the single next step. *Now.*
- **CLAUDE.md** (this file) — stable identity: stack, run/test, entry points, gotchas. *How.*
- **IMPLEMENTATION_PLAN.md** — slice queue & locked decisions. *What's next* (may lag; CONTEXT wins on "now").
- **DESIGN.md** — UI visual contract: tokens, patterns, anti-patterns. Read before touching any template.

## Why (and what would betray it)

The workplace has no GitHub, so astra **is** the distribution channel: curated skills in, one-paste adoption out. Non-goals (betrayals):

- **Never require git/CLI knowledge from adopters.** If installing takes more than pasting one command, the mission failed.
- **Never become a file-share.** Only validated, versioned skills enter the registry — curation (by the owner) is the quality gate.

## Stack

- **Language / runtime:** Python 3.13 (project `.venv`, workspace §4)
- **Framework:** FastAPI + Uvicorn
- **Key dependencies:** Jinja2 (server-rendered pages), a Markdown renderer for SKILL.md, stdlib `zipfile` for bundles.
- **Datastore:** none — **the filesystem is the registry**: `registry/<skill>/<version>/` holds the raw skill folder; the directory tree is the catalog.

## Run

```bash
# install (from repos/astra/ — use the project venv explicitly, don't rely on activation)
.venv/Scripts/python -m pip install -e ".[dev]"

# start dev server (token optional — without it, publish is disabled by design and read surfaces still work)
ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --reload --port 8300
```

Default URL: `http://localhost:8300`. `dev-local-token` is a local-only convention, never a real secret.

## Test

```bash
.venv/Scripts/python -m pytest -q
```

System tests boot the app against a temp registry (`tests/test_astra.py`) — read surfaces, download byte-identity, and every publish wall (token, immutability, zip-slip, frontmatter). The UI look itself stays `[review]`.

## Conventions

- Commit style: imperative one-liner.
- Skill bundles on disk mirror what Claude Code expects: a folder containing `SKILL.md` (+ optional scripts/assets). The zip served for download is exactly that folder — the rendered page and the artifact are the same bytes.
- Versions are immutable once published (a version folder is never edited — publish a new version instead).

## Constraints & Gotchas

- **Intranet-only; no GitHub.** No dependency on external package indexes at runtime; adopters are on Windows — install commands are PowerShell one-liners. **Pages must load with zero external resources** (no CDN, no web fonts) — see DESIGN.md.
- **Read is open, publish is guarded.** Anyone on the network browses/downloads; publishing goes through the owner (curator) only, via a token-guarded upload API called by a Claude Code publish skill.
- Oracle-style workplace secrets discipline applies: the publish token is env-var only, never committed.
- **Route-ordering trap:** the literal `latest` routes (`/skills/{name}/latest`, `/api/skills/{name}/latest`) must stay registered *before* their `{version}` twins in `main.py`, or `latest` gets parsed as a version string. A test pins this — don't reorder routes casually.
- Line endings: files are LF in the repo; git prints CRLF warnings on Windows — harmless, ignore them.

## Entry Points

- `astra/main.py` — FastAPI app: HTML pages (index, skill detail, zip download) + JSON API (`/api/skills`, `/api/skills/{name}/{version}`, guarded `POST /api/publish`).
- `registry/` — the on-disk registry (`<skill>/<version>/SKILL.md` …). **The architectural seam:** every surface (page, zip, API, install command) derives from this one folder shape — no second source of truth. `registry/astra-publish/` is the curator's own publish skill, served like any other.
- `templates/` — Jinja2 pages: `base.html` owns the shared theme + header/footer (all pages extend it; tokens documented in DESIGN.md); `index.html` = catalog, `skill.html` = detail.
- `tests/test_astra.py` — the gate.

## Git

- Remote: none yet (local only).
- Default branch: `master`.

---

<!--
This file is stable identity — it changes rarely. For in-flight session state
(what was just done, what's broken, what's next), use CONTEXT.md.
-->
