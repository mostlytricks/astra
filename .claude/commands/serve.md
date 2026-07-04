---
description: Launch the astra dev server and smoke-check it renders
---

Start the astra dev server and confirm it's serving, then hand the user the URL.

1. Pick a port (default **8300**; if `$ARGUMENTS` names one, use that). If the port
   is already in use, bump to the next free one and say which.
2. Launch in the background (never blocks the session), using the project venv
   explicitly and a local-only token so publish surfaces work:

   ```bash
   ASTRA_PUBLISH_TOKEN=dev-local-token .venv/Scripts/python -m uvicorn astra.main:app --reload --port <port>
   ```

3. Wait ~4s, then smoke-check the read surfaces:
   - `GET /` → 200
   - `GET /skills/<any-registered-skill>/latest` → 307 (the latest redirect)
   - grep the uvicorn log for `error`/`traceback`; report if the log is clean.
4. Report the live URL (`http://localhost:<port>`) and the current catalog
   (`GET /api/skills` → the skill names). Leave the server running.

Notes:
- `dev-local-token` is a local convention, never a real secret — fine to use here,
  never commit a real token (astra's secrets rule).
- The gate is separate: `.venv/Scripts/python -m pytest -q` (already allowlisted).
