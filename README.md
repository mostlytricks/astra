# ✦ astra

**A**gent **S**kill **T**ransfer & **R**egistry **A**pp — an intranet web service where colleagues
browse curated agent skills, decide to adopt one, and install it by pasting **a single command**.
No git, no GitHub, no accounts, anywhere in the flow.

> The rendered `SKILL.md` *is* the sales page. The zip you download *is* the bytes your agent loads.

---

## Why it exists

The workplace has no GitHub, so astra **is** the distribution channel: curated skills in, one-paste
adoption out. Two walls are non-negotiable (breaking either betrays the mission):

- **Adopters never touch git or a CLI.** If installing takes more than pasting one command, astra failed.
- **astra is not a file-share.** Only validated, versioned skills enter the registry — curation by the
  owner is the quality gate.

## How it works

**The filesystem is the registry.** There is no database. `registry/<skill>/<version>/` holds the raw
skill folder (`SKILL.md` + any scripts/assets), and *every* surface — the web page, the download zip,
the JSON API, the install command — is derived live from that one directory tree. One source of truth.

```
registry/
  dashboarding/1.0.0/SKILL.md      →  a page, a zip, an API entry, an install command
  astra-publish/1.0.0/SKILL.md     →  the curator's own publish skill, served like any other
```

## For adopters (everyone on the intranet)

1. Open the catalog, search, click a skill.
2. Read its spec (the rendered `SKILL.md`).
3. Copy the one PowerShell command in the **Adopt** panel and paste it. Done.
4. The command from a *latest* page tracks the newest release; from an older page it's pinned to that version.

Browsing and downloading are open to anyone on the network.

## For the curator (skill owner)

Publishing is guarded — only the owner, via a token-checked API (normally called by the `astra-publish`
Claude Code skill), can add or withdraw skills. Browsing stays open.

- **Publish** — `POST /api/publish?name=&version=` with the skill folder zipped as the raw body and the
  token in an `X-Astra-Token` header. Versions are **immutable**: to change a skill, publish a new version.
- **Yank / unyank** — `POST /api/yank` / `POST /api/unyank` mark a version *withdrawn* without deleting it.
  A yanked version drops out of `latest` and shows a warning, but its bytes never change, so anyone pinned
  to it keeps working. Reversible.

The publish token is env-var only (`ASTRA_PUBLISH_TOKEN`), never committed. Without it set, publishing is
disabled by design and every read surface still works.

## Run it

```bash
# from repos/astra/ — use the project venv explicitly (workspace convention)
.venv/Scripts/python -m pip install -e ".[dev]"

# start the dev server (token optional — without it, publish is off; read surfaces work)
ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --reload --port 8300
```

→ http://localhost:8300  ·  `dev-local-token` is a local convention, never a real secret.

```bash
# the gate: boots the app against a temp registry and proves every wall
.venv/Scripts/python -m pytest -q
```

## Stack

Python 3.13 · FastAPI + Uvicorn · Jinja2 server-rendered pages · a Markdown renderer for `SKILL.md` ·
stdlib `zipfile` for bundles. **No database, no build step, and pages load with zero external resources**
(no CDN, no web fonts) — it must render on an offline intranet box.

## Docs

- **`CLAUDE.md`** — stable identity: stack, run/test, entry points, gotchas. *How.*
- **`CONTEXT.md`** — current state + the single next step. *Now.*
- **`IMPLEMENTATION_PLAN.md`** — slice queue & locked decisions. *What's next.*
- **`DESIGN.md`** — the UI visual contract (read before touching a template).
