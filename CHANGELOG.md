# Changelog

All notable changes to astra are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/); astra uses [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **Bundle-contract validation** — `validate_bundle()` enforces portability walls
  adopters depend on: relative-paths-only, ASCII-only console output (cp949 safety),
  and stdlib-only imports, plus a zip-bomb guard. Publish hard-rejects error findings;
  `SKILL.md` is exempt from the ASCII rule (it renders as HTML, never prints).
- **`POST /api/validate`** — an open, token-free dry-run of the bundle contract, so
  skill authors can self-check a bundle before publishing.
- **`astra-curate`** — a served curator-only review skill: scores an external skill for
  agent-safety/prompt-injection, executable safety, secrets, license, and the bundle
  contract into a PASS/FLAG/BLOCK verdict, then publishes on the curator's explicit yes.
- **Curator skills v1.1.0** — `astra-publish` gains yank/unyank + a validate dry-run
  step; `astra-curate` runs `/api/validate` mechanically in its contract check.
- **Project `.claude/`** — a pytest-runner permission allowlist + a `/serve` command.

### Changed
- **UI reshaped to a professional dev-tool look** — the install command is now a real
  terminal object (`PS>` prompt), catalog rows use monogram tiles instead of fake
  numbering, with added depth and `/`-to-focus search. `DESIGN.md` rewritten to match.

## [0.1.0] - 2026-07-04

First tagged release — astra is functional on localhost. Intranet deployment
(a real `http://astra.…` host + publish token) is deferred as the owner's own task.

### Added
- **Filesystem-as-registry core.** `registry/<skill>/<version>/` is the single source of
  truth; every surface — page, zip, JSON API, install command — derives from it. No database.
- **One-paste adoption.** Each skill page renders `SKILL.md` and hands out a single PowerShell
  install command targeting `%USERPROFILE%\.claude\skills\<name>`. No git, no accounts.
- **Guarded, immutable publish.** `POST /api/publish` (token in `X-Astra-Token`) ingests a zipped
  skill folder atomically; versions are immutable (bump, never edit). Walls: token, name/version
  format, duplicate/409, missing `SKILL.md`, name mismatch, zip-slip, non-zip body.
- **`astra-publish` skill.** The curator's own publish skill, seeded into the registry and served
  like any other skill.
- **Catalog + skill UI.** Dark, zero-external-resource pages (system fonts only): searchable
  catalog + detail page with version pills, the adopt panel as the hero, and bundle contents.
- **`latest` alias.** `/skills/{name}/latest` (page redirect, download, API) resolves to the newest
  version; the latest page hands out a latest-tracking command, older pages stay pinned.
- **Deprecate / yank.** Token-guarded `POST /api/yank` + `/api/unyank` mark a version withdrawn via
  a sidecar `registry/<skill>/<version>.yanked` marker — the published bytes never change, so pins
  stay installable. Yanked versions drop out of `latest` and show a warning banner + a pinned command.
- **JSON API** — `/api/skills`, `/api/skills/{name}/{version}`, `/api/skills/{name}/latest`.
- **The gate** — 26 system tests (`pytest`) boot the app against a temp registry and prove every
  read surface, download byte-identity, and every publish/yank wall.

[0.1.0]: https://example.invalid/astra/releases/0.1.0
