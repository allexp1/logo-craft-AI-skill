---
name: logo-craft
description: "Designs company and product logos from the context of a project (its repo, README, manifests, existing colours and fonts) the way a senior identity designer would: brief, research, concepts in black, optical refinement, real typography set from licensed fonts, calligraphic lettering, colour in OKLCH with colour-vision checks, small-size tests, and a complete export kit (SVG masters, favicon, PWA, iOS/Android app icons, OG image, brand guide). Use whenever the user wants a logo, logomark, wordmark, lettermark, monogram, brand mark, emblem, mascot mark, app icon, favicon, avatar, social icon, brand identity, visual identity, rebrand or logo redesign, brand colours or palette, a wordmark or lettering in a specific typeface or calligraphic hand, a logo review or critique, or asks 'what should my logo look like', even when they say 'icon', 'branding' or 'make it look professional' instead of 'logo'. Also use to turn an existing logo into icons for every platform."
version: "1.0.0"
license: MIT
---

# logo-craft

A logo is the smallest thing a company makes and the one it keeps longest. This skill lets you design one from what a project already tells you, with the judgement of a senior identity designer and the hands of a production artist: it reads the repository for the brief, sets real type, draws calligraphic strokes, composes lockups in cap heights, renders and *looks* at every candidate at 16 px, audits the vector file, builds a perceptual palette and exports a complete kit for web, iOS and Android.

It has three layers. **Why** (the philosophy and the perception behind the rules) lets you derive a good answer for a brand no rule anticipated. **What** (the references: mark types, geometry, typography, calligraphy, colour, conventions, case studies, platform specs) is the knowledge a designer accumulates over a career. **Method** (the process and the scripts) turns both into files. Read the "why" once per project, the "what" as each decision comes up, and run the method every time.

## When this loads, do this first

1. Read this file to the end (it is the whole method).
2. Read `references/philosophy.md` and `references/process.md` once per project: they decide how you think and in what order you work.
3. Open the other references when the stage needs them (the table at the end says when).
4. Scripts live in `scripts/` next to this file; run them with `python3 scripts/<name>.py` from the skill folder, or with the skill folder's absolute path. The first run creates a private Python venv in `~/.cache/logo-craft/` and installs fontTools, uharfbuzz, Pillow and skia-pathops; `rsvg-convert` (`brew install librsvg`) or ImageMagick must exist for rendering. Nothing is installed into the user's project.
5. Never place files into the user's project unless they asked for it. Work in `brand/` (masters, guide) and `dist/` (kit) inside the project, or in a folder they name.

## The philosophy in one page

- **A logo identifies; it does not explain.** (Paul Rand.) The mark's job is to be recognised and remembered, and to acquire meaning from the company's behaviour over years. A mark that illustrates the product is a diagram. Do not draw a house for a real-estate app or a brain for an AI company; find the one quality of this company that is worth a shape.
- **Three criteria, in order** (Sagi Haviv): *appropriate* to the business and audience, *distinctive and memorable* (can a stranger doodle it after one look?), *simple* enough to work at 16 px in one colour. Simplicity is self-preservation, not minimalism: the mark lives as a favicon and an avatar more often than on a billboard.
- **Design for the hardest place first.** The symbol is the app icon; the compact symbol is the favicon. If the idea does not survive a 16 px bitmap in one colour, it is not an idea yet, whatever it looks like at 1024 px.
- **Form before colour, black before anything.** Colour is a layer, not the idea. Every concept is judged in grey at equal size before colour is discussed, because colour hides weak form and because the mark must work on fax, foil, embroidery and dark mode.
- **Durability over fashion.** The best marks are 40 to 100 years old. Know the trends (`references/trends-2026.md`) so you can refuse them. Gap 2010, Tropicana 2009 and Jaguar 2024 show the cost of discarding equity; Mastercard 2016 and Slack 2019 show how to evolve it.
- **Honesty.** No retrofitted meaning (a golden-ratio diagram proves nothing), no gradients or textures hiding a weak silhouette, no mockups before the mark works in grey, and a written account of what was tested and what was not. You cannot clear trademarks; say so every time.
- **The mark is the seed of a system**, not the whole plant: it must generate a compact variant, a wordmark, lockups, a palette, icons and rules. Build the system; hand over the system.

Full argument, the Vignelli questions, the "temptations of an AI designer" table and the eight one-line tests: `references/philosophy.md`. Why the rules work (Gestalt, coarse-to-fine recognition, irradiation, size minima): `references/perception.md`.

## Modes

| The user wants | Mode | Stages |
|---|---|---|
| A logo for a project with no mark yet | New identity | 1 to 8 |
| A better version of an existing logo | Redesign | 1, 2, equity audit (`process.md` §9), 4 to 8 |
| Only an app icon or favicon from an existing mark | Icon | 1 (short), audit with `check_logo.py` + `render.py --sheet` and report what breaks at 16 px, then 7 (never redraw the mark; a one-colour favicon variant and `--dark-fg` for the dark tile are allowed) |
| Only a wordmark or lettering | Wordmark | 1, 2, 4 (wordmark path), 5, 7 |
| Brand colours | Palette | 1 (short), 6 |
| "Is this logo any good?" | Review | `references/critique.md` §6, report only |

## The method

### Stage 1: Brief from the project

```bash
python3 scripts/scan_project.py /path/to/project --md brand/brief.md --json brand/brief.json
```

The scanner reads README, package manifests, app manifests, theme files, locale folders and existing brand assets and drafts the brief: name candidates, one-sentence description, platforms, stack, existing colours and fonts, locales and script direction, tone words. Treat it as a draft: check the name casing, the audience and the category yourself, then complete `assets/brief-template.md` (ten fields plus a twenty-word word map). If a field is unknown, write "unknown" and the assumption you will work under. Gate: do not sketch until the brief names the audience, the smallest place the mark must work, and three adjectives (plus one the mark must not be).

### Stage 2: Research

Ten minutes, not a day. List three to five competitors and describe their marks in one line each (type, colour, construction). Name the category convention (`references/industry-conventions.md` has a table per sector) and decide what to honour and what to break. List the clichés of the sector so you can recognise them in your own sketches. Note what the name's letters offer (`references/mark-types.md` §3): symmetry, round forms, a diagonal, a repeat, a natural ligature.

### Stage 3: Concepts

Write eight to twelve one-line concepts before drawing any. Spread them over the diversity matrix: mark type (wordmark, lettermark, pictorial, abstract, emblem, negative-space), source of form (letter, name meaning, category object, company quality, construction), character (quiet, warm, technical, playful, authoritative), construction (geometric, organic, calligraphic, typographic). Kill literal illustrations, the sector's clichés and anything you have seen before. Pick three that differ in *kind*, not three variations of one idea.

### Stage 4: Build three, in black

Each concept becomes a master SVG in black on a `0 0 100 100` (symbol) or tight (wordmark) viewBox. Rules for the file are in "Authoring SVG" below.

Symbol path: compute the geometry (Python for symmetry and arcs), write explicit coordinates, keep stroke weights and radii from one system, then render and look.

Wordmark path: set the name in a real typeface, then make it ownable.

```bash
python3 scripts/text_to_path.py --list-fonts geometric          # curated faces with licence notes
python3 scripts/text_to_path.py --font-info "Manrope"            # metrics + licence before committing
python3 scripts/text_to_path.py --text "Ledgerly" --font Manrope --weight 700 --tracking -10 --out brand/wordmark.svg
python3 scripts/text_to_path.py --text "לומדים" --font Heebo --weight 800 --out brand/wordmark-he.svg   # RTL shaped by HarfBuzz
```

Each glyph is its own `<path id="gN" data-char="…">` inside `<g id="wordmark">`, so you can modify terminals, join a ligature, unify widths or replace one drawn letter; record every change for the brand guide (`references/typography.md` §3 to §5 for spacing ranges, case, pairing, scripts and licences). Google Fonts under the SIL OFL may be used in logos; Apple's SF fonts may not.

Lettering path: draw the skeleton (centrelines) as stroked paths in an SVG, then sweep a pen over it.

```bash
python3 scripts/pen_sweep.py --svg brand/skeleton.svg --mode broad --angle 30 --width 20 --out brand/word-broad.svg    # Foundational hand
python3 scripts/pen_sweep.py --svg brand/skeleton.svg --mode pointed --angle 55 --width 14 --min-width 1.5 --pressure 1.6 --out brand/word-cp.svg   # Copperplate
python3 scripts/pen_sweep.py --svg brand/skeleton.svg --mode brush --width 16 --min-width 3 --taper 0.2,0.3 --out brand/word-brush.svg
python3 scripts/pen_sweep.py --svg brand/skeleton.svg --mode mono --width 10 --out brand/word-mono.svg                   # strokes to fills
```

Hands, pen angles, nib-width proportions, Hebrew and Arabic pens, flourish rules and the seven-step skeleton-to-logo workflow: `references/calligraphy-lettering.md`.

Then, for every candidate:

```bash
python3 scripts/render.py brand/a.svg --sheet brand/a-sheet.png        # 16..128 px, dark/light, one colour, reversed, blur, greyscale
python3 scripts/check_logo.py brand/a.svg --kind symbol --expect-parts 2
python3 scripts/render.py brand/a.svg brand/b.svg brand/c.svg --compare brand/concepts.png --labels "Orbit,Ledger,Monogram"
```

Open every PNG with the Read tool and look. Gate: a concept goes to the checkpoint only if its sheet reads at 16 px, holds in one colour and reversed, and keeps its silhouette under blur.

### Stage 5: Checkpoint

Show the three on one sheet, in grey, at equal size, no mockups, no colour. Give one paragraph per concept: the idea in one sentence, what it does well, what it risks. Recommend one, with reasons tied to the brief. If the user is present, wait for the pick. If you are working autonomously, choose, write why, and keep the other two as runners-up in `brand/runners-up/` with their paragraphs.

### Stage 6: Refine, then colour and type

Refine in this order and stop when a change makes the 16 px render worse: silhouette → construction consistency (one angle vocabulary, one radius system, one stroke system) → optical corrections (`references/geometry-and-optics.md`: overshoot 1 to 3 %, horizontals 5 to 10 % thinner, optical centre 1 to 3 % up, round shapes 3 to 6 % larger, thin joins) → compact variant for under 32 px → reversed version → wordmark fit → full test matrix.

Centre by visual mass, not by margins: an L, a 7 or a flag is heavier on one side, so its ink sits off-centre in the frame on purpose. `check_logo.py` reports both the margins and the mass-centre offset; when the mass is centred (under 4 %) the unequal margins are an info line, not a fault. Fix a `mass-low` warning by moving the drawing up, never by adding weight at the top.

Colour last, and in OKLCH:

```bash
python3 scripts/palette.py --brand "#0F766E" --suggest                     # harmonies from the primary
python3 scripts/palette.py --brand "#0F766E" --brand "#F59E0B" --name ledgerly --out brand/colors
```

This writes the report (contrast on white and dark, Machado colour-vision simulation, ramps 50 to 950), `tokens.css`, `tailwind.colors.js`, `Colors.swift`, `colors.xml`. Rules: black first; at most three colours; a logo is exempt from WCAG contrast but the same colour as UI must reach 3:1 (text 4.5:1); check the pair under deuteranopia; make a dark-background variant deliberately rather than inverting. Category conventions and the "blue means trust" folklore: `references/color.md`.

Lockups, measured in cap heights (the unit a brand guide uses):

```bash
python3 scripts/lockup.py --symbol brand/symbol.svg --wordmark brand/wordmark.svg --name ledgerly --out-dir brand/
python3 scripts/lockup.py --symbol brand/symbol.svg --wordmark brand/wordmark-he.svg --name ledgerly-he --out-dir brand/    # RTL puts the symbol on the right automatically
```

### Stage 7: Export the kit

```bash
python3 scripts/export_kit.py --symbol brand/symbol.svg --lockup brand/ledgerly-horizontal.svg \
  --stacked brand/ledgerly-stacked.svg --wordmark brand/wordmark.svg --name ledgerly \
  --bg "#0F766E" --fg "#FFFFFF" --favicon-symbol brand/symbol-compact.svg --out dist/logo-kit
# a mark that keeps its own colours on the dark app-icon tile: add --dark-fg "#FFFFFF" when the exporter warns
# only when the user asked for files in the project:
#   --into-web public   --into-ios App/Assets.xcassets/AppIcon.appiconset   --into-android app/src/main/res
```

The kit contains SVG masters in colour, black and white; PNGs 512 to 2048; web (favicon.svg with dark-mode rule, favicon.ico 16/32/48, apple-touch-icon 180, PWA 192/512 plus maskable, `site.webmanifest`, `head.html`, OG image 1200×630, social avatar); iOS (1024 light/dark/tinted, `Contents.json`, Icon Composer layers); Android (adaptive VectorDrawables foreground/background/monochrome, legacy mipmaps, Play 512); print PDF; a README of usage rules. Platform facts and where files go in Next.js, Vite, Flutter, Expo, Xcode, Android Studio, Tauri and Electron projects: `references/deliverables.md`.

### Stage 8: Hand over

Write `brand/brand-guide.md` from `assets/brand-guide-template.md`: the mark and its construction, variants and when to use each, clear space and minimum sizes, colour tokens with contrast and colour-vision results, typography with licence, the do-nots, runners-up, and the honesty paragraph: what was tested (sizes, one colour, reversed, blur, CVD, audit score) and what was not (trademark clearance, printed proofs, recognition research). Point the user to USPTO, EUIPO and WIPO searches before they file anything.

## Authoring SVG

The master is boring on purpose: it is the file every other file derives from, and it must render identically in browsers, librsvg, Android's VectorDrawable converter and Illustrator.

- `viewBox` always; no `width`/`height`; symbols on `0 0 100 100` with 4 to 8 units of margin.
- Filled `<path>` elements only; convert every stroke to an outline (`pen_sweep.py --mode mono` does this) so weight does not change with scale and VectorDrawable does not misrender caps.
- Flat colours as `fill="#RRGGBB"`; `currentColor` is acceptable for a one-colour master.
- Holes with `fill-rule="evenodd"` or a reversed contour under `nonzero`; never a white shape on top.
- No `<text>`, `<image>`, `<filter>`, gradients, `<use>`, `<style>` (except the favicon's dark-mode rule), `opacity`, masks, clip paths, editor metadata or scripts.
- Compute coordinates: write them with at most two decimals, use absolute commands, draw circles as two arcs, keep a symbol under about 200 points. Symmetry comes from code, not from eyeballing.
- Flatten transforms into the coordinates before shipping (`<g transform>` may stay during work).
- `<title>` plus `role="img"` and `aria-label` on the root; ids only where another script needs them.

Full rules, the arc-flag and hole-direction pitfalls and the file naming tree: `references/svg-craft.md`.

## The look loop

Rendering is cheap; opinions are not evidence. After every change: render (`--sheet` or `--out --size 1024`), open the PNG, describe what you see in one sentence, and act on that sentence. "The left arm looks heavier" is a measurement; fix it or prove it wrong by overlaying. The sheet exists so that you never argue about a 16 px rendering from the path data. Then run `check_logo.py`: it scores the file from 100 (15 off per error, 5 per warning), reports margins, centring and optical centre, near-miss angles, palette size, contrast, and what merges or breaks at 16 and 32 px. A score above 90 with no errors is the floor, not the goal; the things it cannot judge (distinctiveness, appropriateness, cliché, likeness to existing marks) are yours. It also fails any file that carries scripts, event handlers, `foreignObject` or external references (`unsafe-content`): the render, lockup and export scripts strip these before they touch a renderer or a deliverable, but a master that needs stripping is not finished.

## Quality bar

Ship only when all are true:

- Reads at 16 px in one colour, and reversed on dark, without a compact variant having to do the work above 32 px.
- One idea, nameable in a sentence by someone who has not read the brief.
- Not a sector cliché, not a literal illustration, not a sparkle, not a shield-with-initial, not a swoosh, not a generic hexagon of nodes (`references/industry-conventions.md` watchlist).
- No resemblance you know of to a famous mark or a competitor's (say what you compared against).
- Construction from one system; optical corrections applied; `check_logo.py` ≥ 90 and no errors.
- Palette ≤ 3 colours; the pair survives deuteranopia; a dark variant exists.
- Wordmark set in a font whose licence allows logo use, with every modification recorded.
- Kit exported, brand guide written, runners-up kept, honesty paragraph present.

Red flags in your own work: you reached for a gradient before the shape worked; the concept needs the caption to be understood; all three concepts are the same idea in different clothes; you have not opened a PNG in the last three edits; you are explaining a meaning you added after drawing.

## Scripts

| Script | Does | Typical call |
|---|---|---|
| `scan_project.py` | Reads a repo and drafts the brief (stdlib only) | `scan_project.py . --md brand/brief.md --json brand/brief.json` |
| `text_to_path.py` | Sets a wordmark from a Google, system or file font via HarfBuzz; RTL; per-glyph paths; `--list-fonts`, `--font-info` | `--text "Name" --font Manrope --weight 700 --out w.svg` |
| `pen_sweep.py` | Sweeps a broad, pointed, brush or monoline pen along skeleton strokes; unions the result | `--svg skel.svg --mode broad --angle 30 --width 20 --out o.svg` |
| `render.py` | PNG at any size, inspection sheet, concept comparison, PDF | `logo.svg --sheet sheet.png` |
| `check_logo.py` | Structural, colour, geometric and raster audit with a score; exit 1 on errors | `logo.svg --kind symbol --expect-parts 2 --json` |
| `palette.py` | OKLCH ramps, WCAG contrast, CVD simulation, tokens for CSS/Tailwind/Swift/Android | `--brand "#0F766E" --brand "#F59E0B" --name x --out brand/colors` |
| `lockup.py` | Horizontal, stacked, symbol and wordmark files with clear space in cap heights; RTL aware; optional tagline | `--symbol s.svg --wordmark w.svg --name x --out-dir brand/` |
| `export_kit.py` | Full multi-platform kit from the masters; optional copy into web/iOS/Android folders | `--symbol s.svg --lockup h.svg --name x --bg "#hex" --fg "#FFF" --out dist/kit` |

`assets/fonts.json` is the curated typeface list (classification, voice, licence, logo-use note) that `--list-fonts` reads. `assets/brief-template.md` and `assets/brand-guide-template.md` are the two documents every project ends up with.

## References

| File | Read when |
|---|---|
| `references/philosophy.md` | Start of every project; whenever a decision has no rule |
| `references/perception.md` | A test fails and you need to know why; negative space, small sizes, colour perception |
| `references/process.md` | Start of every project; redesign equity audit; working autonomously |
| `references/mark-types.md` | Choosing the kind of mark; what the name's letters offer; responsive levels |
| `references/geometry-and-optics.md` | Building and refining a symbol; optical corrections; curves |
| `references/typography.md` | Any wordmark: choosing a face, making it ownable, spacing, scripts, licences |
| `references/calligraphy-lettering.md` | Script or lettered marks; pen angles; Hebrew and Arabic hands |
| `references/color.md` | Stage 6; palettes, CVD, dark variants, print |
| `references/industry-conventions.md` | Stage 2; sector table and cliché watchlist |
| `references/case-studies.md` | Arguing for or against a direction with evidence |
| `references/svg-craft.md` | Writing or fixing the master file |
| `references/deliverables.md` | Stage 7; platform sizes and where files go per framework |
| `references/critique.md` | Judging candidates; reviewing someone else's logo |
| `references/trends-2026.md` | Recognising fashion; motion and layered-icon behaviours |
| `references/sources.md` | Citing or verifying any fact above |

## Limits, stated every time

- **No trademark clearance.** You can compare against marks you know and the competitors you listed; you cannot search registers. Write this in the handover and name USPTO, EUIPO and WIPO.
- **No raster image generation.** This skill draws vectors from geometry and type. If the user wants a painted or photographic mascot, say that this needs an illustrator or an image model, and offer a vector mascot or a lettered mark instead.
- **Font licences are the user's responsibility to honour.** The skill reports what the licence allows (`--font-info`); it cannot buy or check a commercial licence.
- **Print values are approximate.** CMYK and Pantone come from the printer or a bridge, not from `palette.py`.
- **Taste is not a test.** Report results of the tests you ran; keep preferences labelled as preferences.

## Living sidecar

`.living/` keeps the perishable facts (platform icon specs, trend report year, font-service behaviour, trademark search URLs) separate from the method. `.living/PROTOCOL.md` says how to verify the skill's integrity, when the knowledge is stale and how to refresh `KNOWLEDGE.md` without touching this file.
