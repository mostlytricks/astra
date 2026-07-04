---
name: astra-publish
description: Publish, yank, or unyank a skill in the astra registry — validate the SKILL.md, zip the folder contents, and POST to the guarded API. Curator use only (needs the publish token).
---

# astra-publish

The curator's registry write tool: publish a skill folder as a new immutable
version, or withdraw / restore a published version. Read stays open on astra;
these operations don't.

## Preconditions (check before doing anything)

- `ASTRA_URL` env var — the registry base URL (e.g. `http://localhost:8300`).
- `ASTRA_PUBLISH_TOKEN` env var — the curator token. **Never** echo it, write it
  to a file, or put it in a URL; it travels only in the `X-Astra-Token` header.
- For a publish: the skill folder, containing `SKILL.md` at its top level.

If either env var is missing, stop and tell the user which one.

## Publish a version

1. **Validate locally first** (fail fast, don't burn a round-trip):
   - `SKILL.md` exists at the folder's top level.
   - Frontmatter has `name:` (kebab-case, matches what you'll publish as) and a
     non-empty `description:`.
   - Decide the version: ask the user, or check `GET $ASTRA_URL/api/skills` and
     propose current latest + a patch/minor bump. Versions are **immutable** — a
     published version is never overwritten.

2. **Dry-run the bundle contract** — the server enforces it, so check before you
   POST (this is the same wall, run early):

   ```powershell
   iwr "$env:ASTRA_URL/api/validate" -Method Post -InFile "$env:TEMP\<name>.zip" | % Content
   ```

   `ok: true` means it will pass. Any `error` finding (unsafe path, non-ASCII
   console output on cp949 machines, missing/invalid frontmatter) will make
   publish return `400` — fix it first. `warn` findings (e.g. a non-stdlib import)
   don't block, but show them to the user.

3. **Zip the folder's contents** (not the folder itself — `SKILL.md` at the zip root):

   ```powershell
   Compress-Archive -Path <folder>\* -DestinationPath "$env:TEMP\<name>.zip" -Force
   ```

4. **POST it:**

   ```powershell
   iwr "$env:ASTRA_URL/api/publish?name=<name>&version=<X.Y.Z>" `
       -Method Post -InFile "$env:TEMP\<name>.zip" `
       -Headers @{ 'X-Astra-Token' = $env:ASTRA_PUBLISH_TOKEN }
   ```

   Expect `201` + the new page path. `409` = version already exists (bump it),
   `400` = the body says exactly which wall failed, `401` = wrong token.

5. **Prove it's live:** fetch the returned page URL, confirm it renders, then show
   the user the page link and the install one-liner colleagues will paste.
6. Clean up the temp zip.

## Yank or unyank a version

Yanking **withdraws** a version without deleting it: it drops out of `latest` and
shows a warning, but its bytes never change, so anyone already pinned to it keeps
working. It's reversible. Use it when a version is broken or superseded — never
try to edit or delete a published version.

- **Yank:**

  ```powershell
  iwr "$env:ASTRA_URL/api/yank?name=<name>&version=<X.Y.Z>&reason=<why>" `
      -Method Post -Headers @{ 'X-Astra-Token' = $env:ASTRA_PUBLISH_TOKEN }
  ```

- **Unyank (restore):**

  ```powershell
  iwr "$env:ASTRA_URL/api/unyank?name=<name>&version=<X.Y.Z>" `
      -Method Post -Headers @{ 'X-Astra-Token' = $env:ASTRA_PUBLISH_TOKEN }
  ```

Expect `200`. `404` on yank = no such version; `404` on unyank = it wasn't yanked.
After either, confirm on the page (a yanked version shows a "withdrawn" banner;
`latest` skips it).

## Never

- Never publish over an existing version, and never edit or delete a published
  one — bump, or yank.
- Never expose the token in output, logs, or URLs.
- Never "fix" a rejected SKILL.md silently — show the user the validation error
  and let them decide.
