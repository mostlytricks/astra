---
name: astra-publish
description: Publish a skill folder to the astra registry — validate the SKILL.md, zip the folder contents, and POST it to the guarded publish API. Curator use only (needs the publish token).
---

# astra-publish

Take a local skill folder and publish it as a new immutable version in the astra
registry, so colleagues can adopt it from the web page.

## Preconditions (check before doing anything)

- `ASTRA_URL` env var — the registry base URL (e.g. `http://localhost:8300`).
- `ASTRA_PUBLISH_TOKEN` env var — the curator token. **Never** echo it, write it
  to a file, or put it in a URL; it travels only in the `X-Astra-Token` header.
- The skill folder to publish, containing `SKILL.md` at its top level.

If either env var is missing, stop and tell the user which one.

## Steps

1. **Validate locally first** (fail fast, don't burn a server round-trip):
   - `SKILL.md` exists at the folder's top level.
   - Frontmatter has `name:` (kebab-case, matches what you'll publish as) and a
     non-empty `description:`.
   - Decide the version: ask the user, or check the existing versions via
     `GET $ASTRA_URL/api/skills` and propose current latest + a patch/minor bump.
     Versions are **immutable** — a published version is never overwritten.

2. **Zip the folder's contents** (not the folder itself — `SKILL.md` must sit at
   the zip root):

   ```powershell
   Compress-Archive -Path <folder>\* -DestinationPath "$env:TEMP\<name>.zip" -Force
   ```

3. **POST it:**

   ```powershell
   iwr "$env:ASTRA_URL/api/publish?name=<name>&version=<X.Y.Z>" `
       -Method Post -InFile "$env:TEMP\<name>.zip" `
       -Headers @{ 'X-Astra-Token' = $env:ASTRA_PUBLISH_TOKEN }
   ```

   Expect HTTP 201 with the new page path. Common failures: `409` = version
   already exists (bump it), `400` = the response body says exactly which
   validation failed, `401` = wrong token.

4. **Prove it's live:** fetch the returned page URL and confirm it renders, then
   show the user the page link and the install one-liner colleagues will use.

5. Clean up the temp zip.

## Never

- Never publish over an existing version — bump instead.
- Never expose the token in output, logs, or URLs.
- Never "fix" a rejected SKILL.md silently — show the user the validation error
  and let them decide.
