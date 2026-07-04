# DESIGN — astra UI visual contract

The look colleagues judge skills by. Inspired by skills.sh: near-black, dense,
monospace developer accents, the install command as the hero object. All tokens
live in `templates/base.html` `:root` — this file documents the contract; the
CSS is the implementation. Change both together or neither.

## Hard rules

1. **Zero external resources.** No CDN, no web fonts, no icon kits, no analytics
   scripts. Every page must render fully on an offline intranet. System fonts only.
2. **Server-rendered Jinja + vanilla JS.** No framework, no build step. JS is for
   small enhancements only (copy button, live search filter).
3. **The adopt panel is the hero.** On a skill page nothing may compete with the
   install command for attention. New page elements sit below it.
4. **Dark only.** No theme toggle until someone actually asks.

## Tokens (mirror of `base.html :root`)

| Token | Value | Role |
|---|---|---|
| `--bg` | `#08090c` | page background (near-black) |
| `--bg2` / `--panel` / `--card` | `#0d0f14` / `#101319` / `#12151d` | raised surfaces, in order |
| `--line` / `--line2` | `#1e2330` / `#2a3145` | borders; `line2` = emphasized/hover |
| `--ink` / `--dim` / `--faint` | `#e8ebf4` / `#9aa3ba` / `#5c6478` | text hierarchy, in order |
| `--accent` | `#8ab4ff` | links, focus, primary interactive |
| `--accent2` | `#b48aff` | version numbers, the ✦ star, secondary identity |
| `--ok` / `--warn` | `#4ade80` / `#fbbf24` | command text / warnings |
| `--mono` | Cascadia/Consolas stack | commands, versions, chips, wordmark |

## Type & voice

- Body: system-ui/Segoe UI, 15px, line-height 1.7. Headings tight (`letter-spacing: -.5px`-ish).
- Monospace marks *machine text*: commands, versions, file names, counts, the ASTRA wordmark. Never body prose.
- Copy is lowercase-calm ("curated · versioned · no git required"); no exclamation marks; ✦ is the only decorative glyph.

## Patterns

- **Chips** (`.chip`): pill, `--card` bg, `--line` border, mono 12.5px — for metadata facts (version, file count).
- **Command blocks** (`.cmd` + `.copy`): near-black `#05060a` well, `--ok` green mono text, one Copy button per block (`copyText(btn, id)` in base).
- **List rows** (catalog `.row`): border card, hover = `--line2` border + 1px lift + `--card` bg. Two-line description clamp.
- **Version pills** (`.vpill`): current = `--accent2` border/text; others link. Immutability made visible.
- **Section titles**: 13px uppercase, letter-spacing 2.5px, `--faint`, bottom border.
- **Withdrawn/yank state** (`--warn` only, no new color): a yanked version's page shows
  a `.yank-banner` (card bg, `--warn` border, uppercase mono "withdrawn" tag) above the
  adopt panel; its version pill is line-through + `--faint`; a fully-withdrawn skill gets
  a `.chip.warn` on the catalog row. The bytes never change — yank is a visible flag, not a delete.

## Anti-patterns

- No gradients louder than the adopt panel's subtle `--panel→--card`.
- No new colors — if a state needs one, promote it to a token first.
- No modals; navigation is links and pages.
- No images/screenshots in chrome (registry SKILL.md content may embed what it likes).
