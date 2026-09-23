# AGENTS.md

This is a GitHub profile README repo (renders at `github.com/umenzi`). It is Markdown plus static image assets only — no source code, build, test, lint, or deploy pipeline.

## Structure

- `README.md` — the entire product; profile page content.
- `images/` — checked-in local assets (`github-snake.svg`, `github-snake-dark.svg`, `linkedin.svg`). Referenced via relative paths; keep filenames stable.
- `wave.gif` — greeting animation referenced from README.
- No CI workflows, package manifests, or tooling configs exist.

## Conventions

- Most visuals (typing-SVG title, shields.io badges, `github-readme-stats` cards/pins, visitor counter) are hotlinked third-party image URLs, not local code. If a badge/API is down, prefer commenting it out (see commented-out language-stats block) over deleting it.
- Keep the `<picture>` dark/light `media` sources for the contribution-snake image so it works in both GitHub themes.
- Verify edits by previewing `README.md` Markdown rendering; there is nothing to run (`no build/test/lint`).
