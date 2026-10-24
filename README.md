# logo-craft

**An [Agent Skill](https://www.anthropic.com/news/skills) for Claude Code that designs a company or product logo from the context of the project it is sitting in, with the judgement of a senior identity designer and the hands of a production artist.**

**Version 1.0.0** · platform specifications verified October 2026 · [Changelog](CHANGELOG.md) · [npm](https://www.npmjs.com/package/logo-craft)

```bash
npx logo-craft
```

Then, inside any project in Claude Code:

> "Design a logo for this project."
> "Make an app icon and favicon from our logo."
> "Set our name as a wordmark in a geometric sans and give me brand colours."
> "Review this logo honestly."

---

## The idea

Most "AI logo" tools, and the two logo skills that existed before this one, do one thing: turn a sentence into a decorated SVG. The result is usually a literal illustration (a house for real estate, a brain for AI) with a gradient on it, judged at 1024 px and never tested at 16, set in whatever font the model remembered, with no idea whether the licence allows it, and no icons, no palette, no rules.

A working identity designer does something else. They read the business before drawing. They write a brief and a word map. They sketch many ideas and keep three that differ in kind. They build in black, at the smallest size the mark must survive, and only then add colour. They set type in a real face, modify it until it is ownable, and check the licence. They test: one colour, reversed, blurred, 16 px, colour-blind simulation, the competitor shelf. They hand over a system (symbol, compact symbol, wordmark, lockups, palette, icons for every platform, a guide) and write down what was and was not tested.

This skill makes Claude work that way, and gives it the tools a designer uses, as scripts:

| A designer's tool | Here |
|---|---|
| Reading the client's business | `scan_project.py` reads README, manifests, theme files, locales and existing assets and drafts the brief |
| Setting type | `text_to_path.py` sets the name in a Google, system or file font through HarfBuzz (kerning, ligatures, Hebrew and Arabic shaping) and gives one editable path per glyph plus the metrics |
| Calligraphy pens | `pen_sweep.py` sweeps a broad-edge nib, a pointed pen, a brush or a monoline along drawn skeleton strokes |
| Printing proofs and squinting | `render.py` builds the inspection sheet (16 to 128 px, dark and light, one colour, reversed, blur, greyscale) and the equal-size concept comparison |
| A production artist's checklist | `check_logo.py` audits the SVG: structure, palette, contrast, margins, centring, optical centre, near-miss angles, what merges or breaks at 16 and 32 px |
| Colour system | `palette.py` builds OKLCH ramps with WCAG contrast and colour-vision simulation, and writes CSS, Tailwind, Swift and Android tokens |
| Lockups and clear space | `lockup.py` composes horizontal, stacked, symbol and wordmark files measured in cap heights, RTL aware |
| The deliverables | `export_kit.py` writes the whole kit: SVG masters, PNGs, favicon.svg and .ico, apple-touch-icon, PWA and maskable icons, manifest, OG image, iOS 1024 light/dark/tinted and Icon Composer layers, Android adaptive VectorDrawables and Play icon, PDF, usage README |

And it gives Claude the knowledge behind the tools: why Rand says a logo identifies rather than explains, why the Gestalt principles make negative-space marks work or fail, why horizontals must be thinner than verticals, which pen angle makes a Foundational hand and which a Copperplate, what every sector's convention and clichés are, what fifty years of famous redesigns teach, what each platform wants in 2026, and where it must say "I cannot do this" (trademark clearance).

## Three layers

| Layer | Files | What it gives you |
|---|---|---|
| **Why** | `references/philosophy.md`, `perception.md` | Rand, Haviv, Vignelli, Bierut; honesty; the temptations of an AI designer and the disciplines against them. The perception science (Gestalt, coarse-to-fine recognition, irradiation, size minima, colour perception, culture and RTL) that explains the rules and predicts failures. |
| **What** | `references/mark-types.md`, `geometry-and-optics.md`, `typography.md`, `calligraphy-lettering.md`, `color.md`, `industry-conventions.md`, `case-studies.md`, `svg-craft.md`, `deliverables.md`, `trends-2026.md`, `sources.md` | The designer's accumulated knowledge: mark taxonomy, construction and optical correction with starting amounts, type classification as voice and how to make a face ownable, calligraphic hands with angles and nib widths, OKLCH and WCAG facts, sector conventions and clichés, case studies with lessons, SVG master rules, platform specifications and file placement, this year's trends and why to resist them, and the annotated bibliography. |
| **Method** | `SKILL.md`, `references/process.md`, `references/critique.md`, `scripts/`, `assets/` | The eight stages, the modes (new identity, redesign, icon, wordmark, palette, review), the look loop, the quality bar, the brief and brand-guide templates, and the scripts. |
| **Memory** | `.living/` | Perishable facts (icon formats, licences, trend reports) with a source for every change, kept current between releases. |

## What's inside

```
logo-craft/
├── SKILL.md                         # entry point: philosophy in one page, the method, rules, quality bar
├── references/
│   ├── philosophy.md                # why: Rand, Haviv, Vignelli; honesty; AI temptations
│   ├── perception.md                # why the rules work
│   ├── process.md                   # the workflow, checkpoint, redesign audit, autonomous rules
│   ├── mark-types.md                # taxonomy, decision guide, what the letters offer
│   ├── geometry-and-optics.md       # construction systems, optical corrections, curves, small sizes
│   ├── typography.md                # faces as voice, ownable wordmarks, spacing, scripts, licences
│   ├── calligraphy-lettering.md     # hands, pens, Hebrew/Arabic, skeleton-to-logo
│   ├── color.md                     # OKLCH, WCAG, CVD, dark variants, print
│   ├── industry-conventions.md      # sector table and cliché watchlist
│   ├── case-studies.md              # what famous marks and redesigns teach
│   ├── svg-craft.md                 # the master file rules
│   ├── deliverables.md              # platform specs (Oct 2026) and placement per framework
│   ├── critique.md                  # tests, failure patterns, reviewing a logo
│   ├── trends-2026.md               # LogoLounge 2025/26, platform behaviours, blanding, AI aesthetic
│   └── sources.md                   # annotated bibliography
├── scripts/                         # scan_project, text_to_path, pen_sweep, render, check_logo, palette, lockup, export_kit
├── assets/                          # fonts.json (curated faces + licences), brief and brand-guide templates
└── .living/                         # sidecar: perishable facts, sources, change log, integrity hash
```

## Install (Claude Code)

A skill's folder name is its slash command: installing `logo-craft/` gives you `/logo-craft`.

**One command** (Node 16.7+; nothing to clone):

```bash
npx logo-craft              # global: ~/.claude/skills/logo-craft
npx logo-craft --project    # this project only: ./.claude/skills/logo-craft
npx logo-craft --dry-run    # show what would be written, change nothing
```

**From a clone:**

```bash
git clone https://github.com/allexp1/logo-craft-AI-skill.git
cd logo-craft-AI-skill
./install.sh              # or ./install.sh --project
```

**claude.ai:** upload `dist/logo-craft.skill` in Settings → Capabilities → Skills.

### Requirements for the scripts

- Python 3.9 or later. On first use the scripts create a private venv in `~/.cache/logo-craft/venv` and install fontTools, uharfbuzz, Pillow and skia-pathops there. Nothing is installed system-wide or into your project.
- An SVG renderer for rendering, auditing and exporting: `brew install librsvg` (rsvg-convert) on macOS, `apt install librsvg2-bin` on Debian/Ubuntu; ImageMagick works as a fallback.
- Fonts: Google Fonts are downloaded on demand into `~/.cache/logo-craft/fonts/` (SIL OFL and similar licences; logo use permitted). Installed system fonts and font files also work; the licence is reported, not checked.

## How a session goes

1. **Brief.** Claude scans the project, drafts the brief, fills the gaps from the conversation, and writes a twenty-word word map.
2. **Research.** Competitor shelf, sector convention, clichés to avoid, what the name's letters offer.
3. **Concepts.** Eight to twelve one-liners across the diversity matrix; three survive.
4. **Three in black.** Each becomes a master SVG, rendered and inspected at 16 to 128 px, audited by `check_logo.py`, shown on one grey sheet.
5. **Checkpoint.** You pick, or Claude picks with written reasons when told to work alone.
6. **Refine, then colour and type.** Optical corrections, compact variant, reversed version; OKLCH palette with contrast and colour-vision checks; lockups in cap heights.
7. **Export.** The complete kit, placed into `public/`, the `.appiconset` or `res/` only when you ask.
8. **Handover.** A brand guide with construction, variants, clear space, colour tokens, typography and licence, the do-nots, the runners-up, and a paragraph saying what was tested and what was not.

## What it will not do

- **Clear trademarks.** It compares against marks it knows and the competitors it listed; it cannot search registers. Every handover names USPTO, EUIPO and WIPO.
- **Generate raster images.** It draws vectors from geometry and type. A painted mascot needs an illustrator or an image model.
- **Hide its tests.** Every audit score, every skipped check and every licence note goes in the handover.
- **Pass hostile SVG through.** Any SVG it renders or embeds (a supplied mark, a wordmark, a tagline) is first stripped of scripts, event handlers, `foreignObject` and external references, the ImageMagick fallback runs under a restrictive policy, and `check_logo.py` fails such a file with `unsafe-content`. A logo is paths and paint; nothing else reaches a favicon, a lockup or a renderer.

## Keeping it current

The design method does not age. Icon formats, font-service terms and trend reports do. `logo-craft/.living/` holds those facts with a date and a source; when the knowledge is older than 30 days, the skill re-checks the primary sources listed in `.living/sources.md` and logs every change in `.living/CHANGELOG.md`, in advisory mode (it reports conflicts with the skill text, it never overrides the author). See [living-skills](https://github.com/allexp1/living-skills).

## Development

```bash
bash scripts/build.sh     # frontmatter, versions, links, py_compile; rebuilds hash and dist/logo-craft.skill
bash scripts/test.sh      # smoke tests on tests/fixtures
bash scripts/publish.sh   # npm publish (logs in if needed; opens the 2FA page)
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Ground rule one: this repository never contains third-party logos.

## Research behind it

`research/` holds the three studies the skill was synthesised from: a ChatGPT deep-research export on professional logo design, two Codex CLI research runs (design canon and technical implementation), and the Fable synthesis notes with the decisions taken. `logo-craft/references/sources.md` is the bibliography.

## License

MIT for the original text and code. See [NOTICE](NOTICE) for trademarks, fonts and source material.
