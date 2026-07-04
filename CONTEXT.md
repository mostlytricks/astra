# CONTEXT — astra

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- **Deprecate/yank slice shipped** (2026-07-04): curator-only `POST /api/yank` + `/api/unyank` (token-guarded, reversible) mark a version withdrawn via a skill-level sidecar `registry/<skill>/<version>.yanked` — published bytes never change (pins stay installable, download byte-identical). `latest` skips yanked; skill page shows a `--warn` banner + pinned command + line-through pill; catalog flags fully-withdrawn skills. Refactored `index`/`api_skills` onto a shared `catalog()`; `require_token` helper. Not yet committed.
- Earlier day-one slices: adoption loop · system core · catalog + rich UI · `latest` alias · DESIGN.md locked. (git history has the detail.)

## Current State
- Runs locally: `ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --port 8300` → http://localhost:8300. Registry: `dashboarding@1.0.0`, `astra-publish@1.0.0` (no live yanks).
- Gate: `.venv/Scripts/python -m pytest -q` — **26 passed** 2026-07-04. Yank flow also smoke-tested against the real registry (yank→latest 404→pin still serves→unyank restores).
- No remote. Intranet deployment deferred (user's own task; one-liners auto-adapt to serving host).

## Next Step
- Commit the yank slice (working tree has main.py + both templates + DESIGN.md + tests), then user picks next from the queue. Candidate follow-up: teach the `astra-publish` skill a `yank` verb (calls the new API) — but that means bumping the skill's version (immutable folder). `later` pool: install-check UI, version history view, download analytics.
