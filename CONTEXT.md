# CONTEXT — astra

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- Scaffolded + interviewed; built the **adoption loop** slice (skill page → zip → paste-install, machine-verified byte-identical).
- Built the **system core** slice: JSON API (`GET /api/skills`, `GET /api/skills/{name}/{version}`), token-guarded `POST /api/publish` (immutability 409, zip-slip guard, frontmatter validation, atomic temp-dir extract), `astra-publish` curator skill served from the registry itself, and a pytest wall.
- Built the **catalog + rich UI** slice (skills.sh-inspired): `templates/base.html` (shared dark theme, ASTRA wordmark, sticky nav), `templates/index.html` (hero + live search + ranked skill rows), richer `templates/skill.html` (version pills, adopt panel, spec typography). 16 tests green.

## Current State
- Runs locally: `ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --port 8300` → http://localhost:8300. Registry serves `dashboarding@1.0.0` + `astra-publish@1.0.0`.
- Gate: `.venv/Scripts/python -m pytest -q` — 16 passed 2026-07-04.
- **Nothing committed** (first commit is the user's call); no remote.
- All three shipped slices closed (adoption-loop `[review]` demo accepted by user 2026-07-04). Intranet deployment deferred — user's own task.

## Next Step
- User picks the next system slice (`latest` alias vs deprecate/yank) — the `now` lane is OPEN in IMPLEMENTATION_PLAN.md. Also owed: the first commit.
