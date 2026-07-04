# DESIGN — astra UI visual contract

The look colleagues judge skills by: a professional dark developer surface in the
register of tools devs already trust (crates.io / Linear / Vercel), with **the install
command treated as a real terminal object** — astra's signature. All tokens live in
`templates/base.html` `:root`; this file documents the contract, the CSS is the
implementation. Change both together or neither.

## Hard rules

1. **Zero external resources.** No CDN, no web fonts, no icon kits, no analytics
   scripts. Every page must render fully on an offline intranet. System fonts only.
   (Depth comes from CSS: shadows, a fixed dot-grid, and a single radial glow — never assets.)
2. **Server-rendered Jinja + vanilla JS.** No framework, no build step. JS is for
   small enhancements only (copy button, live search filter, `/`-to-focus).
3. **The adopt panel is the hero.** On a skill page nothing may compete with the
   install command for attention. New page elements sit below it.
4. **Dark only.** No theme toggle until someone actually asks.

## Tokens (mirror of `base.html :root`)

| Token | Value | Role |
|---|---|---|
| `--bg` / `--bg-elev` | `#07080b` / `#0b0d12` | page background (near-black) + slight elevation |
| `--panel` / `--card` / `--card2` | `#0e1118` / `#12151d` / `#171b26` | raised surfaces, in order |
| `--line` / `--line2` / `--line3` | `#1d2230` / `#2b3346` / `#38414f` | borders; `line2` = hover, `line3` = strongest |
| `--ink` / `--dim` / `--faint` / `--mute` | `#eef1f8` / `#9aa3ba` / `#5c6478` / `#3f4658` | text hierarchy, brightest → dimmest |
| `--accent` | `#8ab4ff` | links, focus, primary interactive, monogram tiles |
| `--accent2` | `#b48aff` | version numbers, the ✦ star, `PS>` prompt, secondary identity |
| `--ok` / `--warn` | `#52e08a` / `#fbbf24` | command text / warnings |
| `--glow` | `rgba(138,180,255,.10)` | the one ambient hero glow — used once, behind the fold |
| `--radius` | `14px` | default card radius |
| `--mono` | Cascadia/Consolas stack | commands, versions, chips, labels, the ASTRA wordmark |

## Type & voice

- Body: system-ui/Segoe UI, 15px/1.65. Display headings are heavy (weight 800) with
  tight negative tracking (`-.8px` to `-1.4px`) — personality comes from scale + weight,
  not a web font (there are none).
- Monospace marks *machine text*: commands, versions, file names, counts, labels, the
  wordmark. It is also the brand/utility voice (eyebrows, chips, the `PS>` prompt). Never body prose.
- Copy is lowercase-calm, active voice ("adopt", not "submit"; "browse → read → paste →
  running"). No exclamation marks. ✦ is the structural mark (wordmark, section titles,
  the adopt watermark) — not scattered decoration.

## Patterns

- **The terminal** (`.term`): astra's signature. Near-black `#04050a` well, a `.term-bar`
  shell label (`powershell`) + `copy` button, and a `.term-body` with an `--accent2`
  `PS>` prompt glyph before the `--ok` green command. Grounded in the subject — adopters
  are on Windows. Used for the adopt panel; reuse it anywhere a command is shown.
- **Monogram tile** (`.mono-tile`): a skill's first two letters, mono, in a bevelled
  `--card2→--card` tile — the catalog/identity mark that replaced numbered list markers
  (a catalog is a *set*, not a sequence, so `01/02` numbering was decoration and is gone).
- **Chips** (`.chip`): small mono facts (target, version, file count). `.chip.warn` for withdrawn.
- **List rows** (catalog `.row`): borderless-feeling card; hover lifts 1px, brightens the
  border, and reveals a 2px `--accent2` left edge. Two-line description clamp.
- **Version pills** (`.vpill`): current = `--accent2`; others link; yanked = line-through
  `--faint`. Immutability + withdrawal made visible.
- **Section titles**: mono 11.5px uppercase, letter-spacing 2.2px, `--faint`, ✦ lead, bottom border.
- **`kbd`**: keycap for shortcut hints (the `/` in search). Depth via a 2px bottom border.
- **Depth kit**: panels carry a 1px top highlight (`inset 0 1px 0 rgba(255,255,255,.04)`)
  and a soft drop shadow on hover/hero. The page has a fixed faint dot-grid and one radial
  glow behind the hero — that is the entire atmosphere budget.
- **Withdrawn/yank state** (`--warn` only): a yanked version's page shows a `.yank-banner`
  above the adopt panel; its version pill is line-through; a fully-withdrawn skill gets a
  `.chip.warn` on the catalog row. Bytes never change — yank is a visible flag, not a delete.

## Anti-patterns

- No numbered markers on non-sequences. No "big-number + stat-tiles + gradient" hero.
- Atmosphere is rationed: one glow, one dot-grid. No gradient louder than the adopt panel.
- No new colors — if a state needs one, promote it to a token first.
- No modals; navigation is links and pages. No over-animation (respect `prefers-reduced-motion`).
- No images/screenshots in chrome (registry SKILL.md content may embed what it likes).
