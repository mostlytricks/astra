# CONTEXT — astra

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-11 (shipped → stable/ — v0.1.0 live, no active arc)

## Completed
- **Version history view** (2026-07-05): `/skills/{name}` (single-segment, no route-order collision) renders a timeline of every immutable version newest-first (per-version description/files, latest/withdrawn badges); `/api/skills/{name}` is the JSON twin. Linked from the catalog version-count chip + the skill page. 39 tests green; route-order verified intact.
- **Install-verification checklist** (2026-07-05, committed `8af2041`): numbered "did it install?" sequence on the skill page.
- **Curator skills → v1.1.0** (`036c2b2`) + **bundle-contract validation** (`ad57635`): see CHANGELOG `[Unreleased]`.
- **v0.1.0 released** (2026-07-04): first tag; deprecate/yank slice + README + CHANGELOG. Pushed to `github.com/mostlytricks/astra` on branch `main`. (git history / CHANGELOG have the detail.)

## Current State
- Remote live: `github.com/mostlytricks/astra`, branch `main`, tag `v0.1.0`. `[Unreleased]` in CHANGELOG holds everything since (UI, astra-curate, .claude, bundle-contract, curator v1.1.0, install-verification) — evidence points to a **minor bump → v0.2.0**; the user cuts it when ready.
- Runs locally via `/serve` or: `ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --port 8300`. Registry: `dashboarding@1.0.0`, `astra-publish@1.1.0`, `astra-curate@1.1.0` (1.0.0 of each kept; no live yanks). Server up on 8300.
- Gate: `.venv/Scripts/python -m pytest -q` — **39 passed** 2026-07-05.
- Intranet deployment deferred (user's own task; one-liners auto-adapt to serving host).

## Next Step
- **STABLE (shipped 2026-07-11).** Reactivate to cut **v0.2.0** (`[Unreleased]` holds a minor's worth: UI, astra-curate, bundle-contract, curator v1.1.0, install-verification) or when adoption analytics (download counts) becomes worth building — that needs a write-path counter on the otherwise read-only registry. `later` lane: skill compatibility metadata.
