# CONTEXT — astra

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- **`astra-curate` skill added** (2026-07-04): the curation *review gate* — a served curator-only skill (`registry/astra-curate/1.0.0/`) that reviews an externally-authored skill (agent-safety/prompt-injection · executable safety · secrets/PII · license · contract), presents a PASS/FLAG/BLOCK verdict, and on the curator's explicit **yes** chains into publish. Live in the catalog now. **Not yet committed.**
- **UI professional pass** (2026-07-04): reshaped all three templates for a dev-tool register within every DESIGN.md wall. Signature = install command as a real **terminal object** (`.term`: `powershell` bar + `--accent2` `PS>` prompt + green command). Dropped fake `01/02` numbering → mono monogram tiles; added depth (top-highlights, shadows, dot-grid + one hero glow), `/`-to-focus search, new tokens. DESIGN.md rewritten to match. **Not yet committed** (base/index/skill.html + DESIGN.md).
- **v0.1.0 released** (2026-07-04): first tag; deprecate/yank slice + README + CHANGELOG. Pushed to `github.com/mostlytricks/astra` on branch `main`. (git history / CHANGELOG have the detail.)

## Current State
- Remote live: `github.com/mostlytricks/astra`, branch `main`, tag `v0.1.0` pushed. Head is `08cbd6f`; the UI pass sits uncommitted on top.
- Runs locally: `ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --port 8300` → http://localhost:8300. Registry: `dashboarding@1.0.0`, `astra-publish@1.0.0` (no live yanks).
- Gate: `.venv/Scripts/python -m pytest -q` — **26 passed** 2026-07-04. UI pass render-checked (index/skill/publish all 200, clean log); tests assert content strings, look stays `[review]`.
- Intranet deployment deferred (user's own task; one-liners auto-adapt to serving host).

## Next Step
- Commit the two uncommitted pieces (UI pass: base/index/skill.html + DESIGN.md · curation gate: registry/astra-curate/). Then real-world test astra-curate by handing it an actual external skill. `later` pool: astra-publish `yank` verb, install-check UI, version history view, download analytics.
