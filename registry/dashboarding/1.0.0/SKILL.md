---
name: dashboarding
description: Build a self-contained, zero-dependency HTML dashboard from any tabular or status data (project health, service checks, KPIs, inventories). One file, no CDN, opens anywhere — including offline intranets.
---

# Dashboarding

Turn whatever data the user points at (a JSON/CSV file, a database query result, a
folder scan, command output) into **one self-contained HTML file** they can open,
share on an intranet, or drop on a file share — no server, no CDN, no build step.

## When to use

The user asks to "make a dashboard", "visualize the status of…", "give me an
overview page for…", or wants a recurring report as a page instead of a text dump.

## Hard rules

1. **One file, zero dependencies.** All CSS and JS inline. Never reference a CDN,
   Google Fonts, or any external URL — the file must render on an offline intranet.
2. **Generated, never hand-edited.** If the data comes from a source that can change,
   write a small generator script the user can re-run; put a `generated: <date>`
   stamp in the page footer. Never ask the user to edit the HTML.
3. **Answer one question per panel.** Each card/section answers a single question
   ("what's red?", "what changed this week?", "how many per category?"). If a panel
   needs a paragraph to explain, split it.
4. **Numbers get context.** Every metric shows its comparison (target, last period,
   or total) — a lone number is decoration, not information.

## Layout recipe

- **Header:** title + generated-at stamp + one-line source description.
- **Chip row:** 3–6 headline numbers (`<div class="chips">`) — the "is everything
  okay?" glance.
- **Main grid:** cards per subject. Status coloring: green/amber/red as background
  *tints*, never as the only signal (add the word or icon — color-blind safe).
- **Detail table(s):** sortable by clicking headers (15 lines of vanilla JS), with
  a text filter input when rows > 20.
- **Footer:** generated stamp + how to regenerate (the exact command).

## Style tokens (default, override if the user has a design system)

```css
:root {
  --bg:#0f1220; --card:#181c30; --line:#2a3050; --ink:#e2e6f5; --dim:#8b93b0;
  --ok:#4cc38a; --warn:#e5b454; --bad:#e5484d; --accent:#6e9fff;
  font-family: system-ui, 'Segoe UI', sans-serif;
}
```

Dark by default; switch to light only if the user asks. Charts: prefer HTML/CSS
bars (a `div` with width %) over canvas; use inline SVG only when a real time-series
line is needed.

## Verification

Before handing over: open the file (or ask the user to), confirm it renders with
the network disconnected, and check the chip row answers "is everything okay?"
in under three seconds.
