# AGENTS.md

This is a GitHub profile README repo (`AP24110011314/AP24110011314` — repo name must equal username or the profile page stops rendering). It is Markdown plus static image assets only — no source code, build, test, lint, or deploy pipeline.

## Structure

- `README.md` — the entire product; profile page content.
- `images/` — only `github-snake.svg` / `github-snake-dark.svg` are live (relative paths in the `<picture>` block). `images/linkedin.svg` and root `wave.gif` are checked in but currently unreferenced — `wave.gif` loads from `raw.githubusercontent.com/.../main/wave.gif`, LinkedIn uses a shields.io badge. Do not delete the unreferenced files without asking.
- No CI workflows, package manifests, or tooling configs exist.

## Conventions

- Most visuals (typing-SVG title, shields.io badges, `github-readme-stats` cards/pins, visitor counter) are hotlinked third-party image URLs, not local code. If a badge/API is down, prefer commenting it out (see commented-out language-stats block) over deleting it. GitHub's camo image proxy pins to the exact URL, so after a transient outage force a refetch with a harmless URL tweak (e.g. badge `style`) rather than re-adding the same URL.
- Keep the `<picture>` dark/light `media` sources for the contribution-snake image so it works in both GitHub themes.
- Verify edits by previewing `README.md` Markdown rendering; there is nothing to run (`no build/test/lint`).
