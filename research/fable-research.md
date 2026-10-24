# Fable research and synthesis notes

Claude Fable 5.1, 2026-10-24 to 2026-10-25. This file records what was researched independently of the ChatGPT and Codex documents, which of their findings were adopted, which were rejected and why, and the decisions that shaped the skill. It is a working document, not a reference: the reference files in `logo-craft/references/` are the deliverable.

## 1. Questions I set out to answer

1. What separates a professional identity designer's process from "generate a logo from a sentence", and which parts of it can an agent with a shell, a renderer and a font engine actually perform?
2. What are the load-bearing rules (the ones every master repeats), and what is the perceptual mechanism behind each, so that the skill can derive answers for cases the rules do not cover (the "apple-hig" approach the user asked for)?
3. What do calligraphy and lettering contribute that type alone cannot, and how can a pen be modelled well enough to draw with?
4. What do platforms require in October 2026 (favicon, PWA, iOS 26/27 layered icons, Android adaptive, Play, OG), and where do files go in common project layouts?
5. What did the two existing logo skills get right and wrong?

## 2. Prior art (read in full)

- **op7418/logo-generator-skill**: a single SKILL.md. Takes a name, industry, style keywords and emits an SVG. Strengths: short, triggers well, gives a style vocabulary. Weaknesses: no reading of the project; no testing at small size; no typography beyond `<text>` or remembered outlines; gradients and effects encouraged; no deliverables; no honesty about trademarks or licences; the output is judged once, at full size, by the model that produced it.
- **kaankiziltug/logo-design-skill**: richer, with a testing checklist and a reference library of famous marks plus a TRADEMARKS.md. The checklist (sizes, one colour, reversed) was good and informed `critique.md`. Shipping third-party marks as reference is a liability and also encourages likeness; this skill bundles none, and `case-studies.md` describes rather than draws.

Decision: build the skill around *process plus tools*, not around prompt vocabulary. Every stage a designer performs has either a script or a written procedure with a gate.

## 3. Independent findings adopted

### Philosophy and perception
- Rand's "identify, not explain" and his list of qualities; Haviv's three criteria and the doodle test; Vignelli's semantics/syntactics/pragmatics; Bierut's "the mark is the seed of a system". Verified against the authors' own pages (sources.md §1).
- Gestalt (Wagemans 2012) as the mechanism behind closure, figure-ground and negative-space marks; coarse-to-fine recognition as the reason the blur test and the 16 px test are the same test.
- Elliot & Maier (2014): colour effects are context-dependent, so "blue means trust" is folklore; sector *convention* is the real constraint. Adopted as the stance of `color.md`.
- The Apple golden-ratio diagram debunking (Fast Company, Janoff's own account): construction diagrams are presentation, not design. Adopted into `philosophy.md` as the "no retrofitted meaning" rule.

### Craft
- Frere-Jones, Typeface Mechanics: overshoot, optical centre, horizontals thinner, round shapes larger. Starting amounts in `geometry-and-optics.md` are ranges, hedged, because every source gives slightly different numbers and the right amount depends on weight.
- Small-size minima: no source gives a universal number; by rendering test marks at 16 px with rsvg-convert, a stroke or gap under about 6 units of a 100-unit viewBox disappears or merges, and 8 to 9 is safe. Recorded as *(derived)*.
- Noordzij's translation/expansion/rotation model as the way to explain what each pen does; the broad-edge hands table (Foundational, Italic, Uncial, Carolingian, Textura) and pointed-pen slants (Copperplate 55°, Spencerian 52°) cross-checked across Shaw, Faber-Castell and the Calligraphy Museum page; Hebrew pen held flat (0 to 15°) for thick horizontals; Arabic Naskh/Thuluth/Kufic noted with the caveat that the skill's engine models the nib, not the tradition.
- Licences: SIL OFL permits logo use (OFL FAQ); Reserved Font Names restrict only modified font software names; Google Fonts FAQ says logos are fine; Adobe Fonts permits logo use for subscribers; Apple's San Francisco licence does not permit use outside Apple platform software. Verified on the licence pages.

### Platform
- Apple: layered Icon Composer documents, Default/Dark/Clear/Tinted, no baked effects; appiconset 1024 fallback; watchOS 1088; iPhone Duo changes nothing for icons.
- Android: 108/72/66 dp, monochrome layer; Play 512 PNG ≤ 1024 KB, no transparency.
- Web: ICO 16/32/48 still the broadest fallback; SVG favicon with `prefers-color-scheme`; apple-touch-icon 180; PWA 192/512 plus maskable with 40 % safe radius; OG 1200 × 630.

### Trends
- LogoLounge 2026 and 2025 reports read for vocabulary; the "blanding" correction and the AI sparkle cliché recorded so the skill can name and refuse them.

## 4. Findings rejected or hedged

- **Golden ratio and Fibonacci construction as a quality signal.** Rejected; useful only as an organising grid, never as proof. (`philosophy.md`, `geometry-and-optics.md`.)
- **Colour psychology tables** ("green = growth, blue = trust"). Rejected as causal claims; kept only as *sector convention* observations.
- **Prompt-only SVG generation with gradients, shadows and `<text>`.** Rejected for masters; `check_logo.py` errors on them.
- **Bundling famous marks for reference.** Rejected (liability; likeness).
- **Raster image generation for logos.** Out of scope; stated as a limit.
- **Exact optical correction percentages.** Hedged to ranges with "start here, then look".
- **"Logos are exempt from WCAG, so contrast does not matter."** Half true: the logo image is exempt, but the same colour used for UI text or controls is not; both facts recorded.

## 5. Engineering decisions

- **Filled paths only.** Strokes render differently across librsvg, browsers, VectorDrawable and Illustrator at small sizes; `pen_sweep.py --mode mono` converts strokes to outlines, and `check_logo.py` flags strokes.
- **HarfBuzz for shaping.** Kerning, ligatures and RTL cannot be faked with per-glyph advances; uharfbuzz is small and mature. Google Fonts are fetched through the CSS2 API with a TrueType-requesting user agent and cached; variable fonts are instanced with fontTools.
- **Pen model.** A broad nib is a segment of fixed length at a fixed angle swept along the stroke; a pointed pen is a width function of stroke direction (thick on downstrokes, hairline up) raised to a pressure exponent; a brush is a width envelope with tapers; mono is round-capped offset. Outlines are unioned with skia-pathops so overlapping strokes merge.
- **OKLCH for ramps.** Even perceived lightness steps; Machado 2009 matrices for CVD; WCAG 2.x contrast.
- **Cap heights as the unit of lockups.** Brand guides express clear space and symbol size in cap heights or x-heights; `text_to_path.py` emits the metrics so `lockup.py` can align on them.
- **Private venv, never the system Python.** PEP 668 blocks `pip install` on modern macOS/Linux; the scripts bootstrap `~/.cache/logo-craft/venv` and re-exec themselves inside it.
- **Project scanner is read-only and stdlib only**, so the brief step never needs the venv.
- **Living sidecar** for the perishable facts, following the user's living-skills spec 1.1 (advisory mode).

## 6. Open questions for later versions

- A `fonts.json` entry for more non-Latin scripts (Devanagari, Thai, Cyrillic display faces).
- Pen model: a true pressure curve from stroke curvature (Spencerian shades) rather than direction only.
- `check_logo.py`: a likeness check against the *user's own* competitor set (they supply SVGs) rather than any bundled corpus.
- An animated (Lottie/SVG) variant exporter once a master exists; `trends-2026.md` already states the static-first rule.
- Evaluation: the `evals/` folder has three cases; they test the files produced, not the aesthetic quality, which still needs human review.
