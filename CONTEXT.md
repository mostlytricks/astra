# CONTEXT — astra

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- Day one shipped four slices: adoption loop (✓ demo accepted) · system core (JSON API, guarded immutable publish, `astra-publish` skill) · catalog + rich UI (skills.sh-style) · `latest` alias (redirect page, download, API; latest-tracking install commands on newest page, pinned on older). First commit `4ded61e` + the latest-alias commit.

## Current State
- Runs locally: `ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --port 8300` → http://localhost:8300. Registry: `dashboarding@1.0.0`, `astra-publish@1.0.0`.
- Gate: `.venv/Scripts/python -m pytest -q` — 18 passed 2026-07-04.
- No remote. Intranet deployment deferred (user's own task; one-liners auto-adapt to serving host).

## Next Step
- User picks the next slice — deprecate/yank support is the top `next` candidate; `later` pool: install-check UI, version history view, download analytics. Also worth considering: `DESIGN.md` to lock the UI tokens now that the look is settled.
