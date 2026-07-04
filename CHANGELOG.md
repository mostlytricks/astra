# Changelog

All notable changes to astra are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/); astra uses [SemVer](https://semver.org/).

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
