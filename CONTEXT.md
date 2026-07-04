# CONTEXT — astra

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-05

## Completed
- **Curator skills → v1.1.0** (2026-07-05): taught them the new walls. `astra-publish` 1.1.0 adds yank/unyank + a `/api/validate` dry-run step; `astra-curate` 1.1.0 runs `/api/validate` mechanically in its bundle-contract check (was eyeballed). New immutable versions (1.0.0 kept), both dogfooded through the validator (ok=true). Registry folders uncommitted.
- **Bundle-contract validation** (2026-07-05, committed `ad57635`): `validate_bundle()` enforces relative-paths / cp949-ASCII console (error) / stdlib-only (warn) + bomb guard; publish hard-rejects errors; open dry-run `POST /api/validate` for self-check. 34 tests green.
- **v0.1.0 released** (2026-07-04): first tag; deprecate/yank slice + README + CHANGELOG. Pushed to `github.com/mostlytricks/astra` on branch `main`. (git history / CHANGELOG have the detail.)

## Current State
- Remote live: `github.com/mostlytricks/astra`, branch `main`, tag `v0.1.0` pushed. Bundle-contract committed (`ad57635`); the v1.1.0 curator-skill folders are the only uncommitted change.
- Runs locally via `/serve` or: `ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --port 8300`. Registry: `dashboarding@1.0.0`, `astra-publish@1.1.0`, `astra-curate@1.1.0` (1.0.0 of each kept; no live yanks). Server up on 8300.
- Gate: `.venv/Scripts/python -m pytest -q` — **34 passed** 2026-07-05. `/api/validate` also live-verified (bad bundle → ok=false, console-nonascii error + nonstdlib-import warn).
- Intranet deployment deferred (user's own task; one-liners auto-adapt to serving host).

## Next Step
- User cuts a release next (their call). After that, `next` lane = install-verification checklist on the skill page ("does /name appear?"). `later`: version history view, download analytics.
