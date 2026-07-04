# astra — Implementation plan & resume sheet

> One-line working scenario: a colleague finds a skill on the intranet page, pastes one PowerShell command, and the skill runs in their agent — no git involved.
> Branch `main` · last updated 2026-07-05.

## Status right now

Shipped and released as **v0.1.0** (pushed to `github.com/mostlytricks/astra`), plus the UI professional pass, the `astra-curate` review skill, and **bundle-contract validation** on top. Gate is **pytest**, 34 green. Working tree: the bundle-contract slice (main.py + tests + docs) is uncommitted. Next slice: user's pick — see queue. Intranet deployment (real `http://astra.…` base URL) is the user's own task, later.

## Slice queue

Rolling lanes (growing project — features accrete, phases would be fake). Rules:
- **Exactly one slice in `now`**, carrying the full four-block spec inline (no `.gravity/` domains yet — don't mint one for a single slice).
- `next` is ordered and short (≤3). `later` is an unordered pool, not a commitment.
- A shipped slice leaves the queue; its detail survives in git history.
- New slices enter via `/interview astra <feature>`.

| Lane | Slice | Domain PLAN | Status |
|---|---|---|---|
| now | OPEN: user picks the next slice (candidates below) | — | ○ |
| next | Adoption analytics (download counts — is curation landing?) | — | ○ |
| later | Skill compatibility metadata (which agent/CLI version a skill targets) | — | ○ |

Shipped (details in git history): **adoption loop** (2026-07-04, ✓ demo accepted) · **system core** — JSON API + guarded publish + `astra-publish` skill + pytest wall (2026-07-04) · **catalog + rich UI** — skills.sh-inspired dark UI: base layout + searchable catalog page + detail page with version pills/adopt panel (2026-07-04) · **`latest` alias** — `/skills/{name}/latest` (page redirect, download, API) + latest-tracking install commands on the newest page, pinned on older pages (2026-07-04) · **deprecate/yank** — sidecar `<version>.yanked` marker (bytes untouched), token-guarded `/api/yank`+`/api/unyank`, `latest` skips yanked, page banner + pinned command + marked pills, catalog withdrawn flag (2026-07-04) · **UI professional pass** + **`astra-curate` review skill** (2026-07-04) · **bundle-contract validation** — `validate_bundle()` walls (relative paths · cp949/ASCII console output · stdlib-only heuristic + bomb guard) enforced hard by publish, exposed as open dry-run `POST /api/validate` for author self-check (2026-07-05) · **curator skills v1.1.0** — `astra-publish` gains yank/unyank + a validate dry-run step; `astra-curate` runs `/api/validate` mechanically in its bundle-contract check; both new immutable versions, dogfooded through the validator (2026-07-05) · **install-verification checklist** — a numbered "did it install?" sequence on the skill page (no-errors → SKILL.md on disk → `/name` appears → restart-and-retry), closing the adoption feedback loop (2026-07-05) · **version history view** — `/skills/{name}` (single-segment) timeline page + `/api/skills/{name}` JSON: every immutable version newest-first with per-version description/files/yank state, linked from the catalog version-count chip and the skill page (2026-07-05).


## Locked decisions

- **Python 3.12 + FastAPI + Jinja2** — smallest stack that serves pages + zips on an intranet box; fits the workspace `.venv` convention.
- **Filesystem-as-registry** — `registry/<skill>/<version>/` is the single source of truth for page, zip, and install; no database until proven needed.
- **Versions are immutable** — publish a new version, never edit a shipped one (replaces what git tags would do).
- **Curator-only publish** — the owner uploads via a token-guarded API called by a Claude Code publish skill; browse/download stays open on the trusted intranet.
- **Adopters never touch git** — adoption is: read page → paste one PowerShell command. This is the mission wall, not a convenience.
- **Publish = raw zip body + query params** (`POST /api/publish?name=&version=`, token in `X-Astra-Token` header) — no multipart, so PowerShell `iwr -InFile` works with zero extra dependencies.
- **Atomic publish** — extract to a temp dir inside `registry/`, then `os.replace` into place; a half-written version folder is never observable.

## Open questions

- OPEN: which skill seeds the registry first (the `now` slice's review item)?
- OPEN: intranet deployment (`http://astra.…` host, start-on-boot, real publish token) — **user's own task, deferred**. Localhost is fine for every slice until then; install one-liners auto-adapt to whatever host serves the page.
- OPEN: skill compatibility metadata — do we need to mark which agent/CLI version a skill targets, or is that premature?

## The gate

```bash
.venv/Scripts/python -m pytest -q
```

39 system tests against a temp registry: read surfaces (catalog, detail, `latest` alias/redirect, install-verification checklist, version-history page + JSON), download byte-identity, every publish wall (token, disabled-without-token, immutability/409, missing SKILL.md, name mismatch, bad name/version, zip-slip, non-zip body), yank/unyank (hides from latest but keeps pins installable, bytes untouched, api/page flags, fully-yanked catalog state, token wall, unknown-version 404, unyank restores), and the bundle contract (console-nonascii is a publish-blocking error, non-stdlib import is a non-blocking warn, path-traversal rejected, SKILL.md exempt from ASCII, `/api/validate` dry-run needs no token). UI look stays `[review]`.

Last green: 2026-07-05 (39 passed).
