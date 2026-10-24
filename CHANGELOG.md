# Changelog

File paths are relative to the `logo-craft/` skill folder unless they start at the repository root.

## 1.0.0 — 2026-10-25

First release.

### Method and philosophy
- `SKILL.md`: the eight-stage method (brief from the project, research, concepts, three in black, checkpoint, refine then colour and type, export, hand over), the philosophy in one page, SVG authoring rules, the look loop, the quality bar, modes (new identity, redesign, icon, wordmark, palette, review) and the limits stated every time (no trademark clearance, no raster generation, licences are the user's).
- `references/philosophy.md` (Rand, Haviv, Vignelli, Bierut; honesty; the temptations of an AI designer), `references/perception.md` (Gestalt, coarse-to-fine recognition, size minima, colour perception, culture and RTL), `references/process.md` (the workflow, checkpoint rules, redesign equity audit, working autonomously).

### Knowledge
- `references/mark-types.md`, `geometry-and-optics.md` (construction systems, optical corrections with starting amounts), `typography.md` (classification as voice, making a face ownable, spacing, Hebrew/Arabic/CJK, licences), `calligraphy-lettering.md` (Noordzij model, broad-edge and pointed hands with angles and nib widths, brush, Hebrew and Arabic pens, skeleton-to-logo workflow), `color.md` (OKLCH, WCAG facts, CVD, dark variants, print), `industry-conventions.md` (sector table and cliché watchlist), `case-studies.md`, `svg-craft.md`, `deliverables.md` (platform specifications verified 2026-10-24 and placement per framework), `critique.md`, `trends-2026.md`, `sources.md` (annotated bibliography).

### Scripts (Python 3.9+, private venv in `~/.cache/logo-craft/`)
- `scan_project.py` drafts the brief from a repository (stdlib only).
- `text_to_path.py` sets wordmarks from Google, system or file fonts with HarfBuzz shaping (kerning, ligatures, RTL), one path per glyph, metrics as data attributes; `--list-fonts`, `--font-info`.
- `pen_sweep.py` sweeps a broad-edge, pointed, brush or monoline pen along skeleton strokes and unions the outline.
- `render.py` renders PNGs, the inspection sheet (16 to 128 px, dark/light, one colour, reversed, blur, greyscale) and the concept comparison sheet.
- `check_logo.py` audits structure, colour, geometry and 16/32 px rasters with a score.
- `palette.py` builds OKLCH ramps with WCAG contrast and Machado CVD simulation; writes CSS, Tailwind, Swift and Android tokens.
- `lockup.py` composes horizontal, stacked, symbol and wordmark files with clear space in cap heights; RTL aware; optional tagline.
- `export_kit.py` exports the complete kit: SVG masters in colour/black/white, PNGs, favicon.svg with dark-mode rule, favicon.ico 16/32/48, apple-touch-icon, PWA icons incl. maskable, manifest, head snippet, OG image, social avatar, iOS 1024 light/dark/tinted plus Icon Composer layers, Android adaptive VectorDrawables plus legacy mipmaps and Play icon, print PDF, README.

### Repository
- `.living/` sidecar (living-skills/1.1) for perishable platform and licence facts.
- `bin/install.js` (`npx logo-craft`), `install.sh`, `scripts/build.sh`, `scripts/test.sh` (smoke tests on `tests/fixtures/`), `scripts/publish.sh`.
- `research/` holds the three research runs the skill was built from (ChatGPT deep research, Codex design and technical research, Fable synthesis).
