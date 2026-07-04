# CONTEXT — astra

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-05

## Completed
- **Install-verification checklist** (2026-07-05): a numbered "did it install?" sequence on the skill page below the adopt panel (no-errors → `SKILL.md` on disk → `/name` appears → restart-and-retry). Closes the adoption feedback loop; numbering is legit here (real sequence). 35 tests green.
- **Curator skills → v1.1.0** (2026-07-05, committed `036c2b2`): `astra-publish` 1.1.0 adds yank/unyank + a `/api/validate` dry-run; `astra-curate` 1.1.0 runs `/api/validate` mechanically. 1.0.0 kept; both dogfooded.
- **Bundle-contract validation** (2026-07-05, committed `ad57635`): `validate_bundle()` walls (paths/cp949-ASCII = error, stdlib = warn) + open `POST /api/validate`.
- **v0.1.0 released** (2026-07-04): first tag; deprecate/yank slice + README + CHANGELOG. Pushed to `github.com/mostlytricks/astra` on branch `main`. (git history / CHANGELOG have the detail.)

## Current State
- Remote live: `github.com/mostlytricks/astra`, branch `main`, tag `v0.1.0`. `[Unreleased]` in CHANGELOG holds everything since (UI, astra-curate, .claude, bundle-contract, curator v1.1.0, install-verification) — evidence points to a **minor bump → v0.2.0**; the user cuts it when ready.
- Runs locally via `/serve` or: `ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --port 8300`. Registry: `dashboarding@1.0.0`, `astra-publish@1.1.0`, `astra-curate@1.1.0` (1.0.0 of each kept; no live yanks). Server up on 8300.
- Gate: `.venv/Scripts/python -m pytest -q` — **35 passed** 2026-07-05.
- Intranet deployment deferred (user's own task; one-liners auto-adapt to serving host).

## Next Step
- `next` lane = version history / changelog view per skill (surface the immutable version timeline). `later`: adoption analytics (download counts). User cuts v0.2.0 whenever they're ready — tree is release-clean.
