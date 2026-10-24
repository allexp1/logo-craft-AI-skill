# SVG craft: the master file

The master SVG is the single source every other file is derived from. It must be boring: one filled path per shape, no effects, a square viewBox for symbols, a title. Everything clever (gradients, dark mode, materials) happens in the exports, where the platform expects it.

Contents: 1 the master's rules · 2 authoring paths as an LLM · 3 fill rules and holes · 4 strokes to outlines · 5 transforms · 6 what never goes in a master · 7 accessibility and metadata · 8 renderers and their quirks · 9 naming and files · 10 validation loop

## 1. The master's rules

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="Ledgerly mark">
  <title>Ledgerly mark</title>
  <path fill="#0F766E" fill-rule="evenodd" d="M50 4 A46 46 0 1 1 49.99 4 Z M50 22 A28 28 0 1 0 50.01 22 Z"/>
</svg>
```

- **viewBox** always; square (`0 0 100 100` or `0 0 1024 1024`) for symbols; the wordmark's viewBox is its ink box plus padding. Omit width/height (or set both) so the file scales.
- **Units**: 100 or 1000 for symbols keeps the maths readable; two decimals of precision are enough.
- **One colour per path**, as a `fill` attribute (not CSS), so recolouring to black and white is mechanical. `currentColor` is acceptable for single-colour marks.
- **No `stroke` in the final master** (see §4); strokes are fine while exploring.
- **Flattened**: no `transform` attributes on delivered paths (see §5), no nested groups beyond one `<g>` for organisation.
- **A `<title>`** as the first child and `role="img" aria-label="..."` on the root, so the inline SVG is accessible.
- **Closed contours** (`Z`) on every filled subpath.
- Keep **separate masters** for symbol, wordmark and each lockup; never deliver one file that contains them all stacked in `<g>`s.

## 2. Authoring paths as an LLM

You do not have a mouse; you have arithmetic. Use it:

- **Compute coordinates** from the construction rules (centre, radius, stroke weight, angle family). Write them down before writing the `d` attribute.
- **Use Python for repetition and symmetry**: place points on a circle, rotate a module n times, mirror across x = 50. Print the path; paste it. Ten lines of code beat forty hand-typed numbers.
- **Prefer absolute commands** (`M L C A Z`) over relative ones for anything you will edit later; relative commands accumulate errors when you change one value.
- **Circles and arcs**: a full circle as one `A` is ambiguous (start equals end); use two half arcs (`M50 4 A46 46 0 1 1 50 96 A46 46 0 1 1 50 4 Z`) or a `<circle>` element in the source and convert later. Arc flags: large-arc (0/1) and sweep (0 = counter-clockwise in SVG's y-down coordinates, 1 = clockwise).
- **Cubic circles** when you need control: handle length 0.5523 × r (see `geometry-and-optics.md` §3).
- **Points at extrema**, handles horizontal/vertical there; a kink is a point whose two handles are not collinear.
- **Rounded rectangles**: `<rect rx>` is fine in the source; the exporter converts shapes to paths.
- **Check the count**: a symbol with more than about 200 points is suspicious; over 1,000 is a trace, not a design.

## 3. Fill rules and holes

Two ways to make a hole:

- `fill-rule="evenodd"`: any contour inside another becomes a hole regardless of direction. Simple and robust; most renderers and Android's VectorDrawable (`android:fillType="evenOdd"`, API 24+) support it.
- `fill-rule="nonzero"` (the default) with the inner contour drawn in the **opposite direction**. This is what font tools expect and what boolean operations produce.

Pick one per file. A filled path with a subpath that is not closed, or two overlapping contours in the same direction under evenodd, renders differently across tools; `check_logo.py` warns on unclosed filled subpaths.

## 4. Strokes to outlines

Strokes are convenient (one centreline, one width) and dangerous (renderers differ in joins and caps; icon pipelines and embroidery want fills; `stroke-width` scales with the viewBox, not with the output). Explore with strokes, deliver fills:

- `pen_sweep.py --mode mono --width W --cap round|butt|square --svg strokes.svg --out outlined.svg` outlines every stroked path and unions the result.
- For stroked circles and rings, draw two arcs with evenodd instead.
- After outlining, clean the joins (slivers where strokes met at acute angles).

`vector-effect="non-scaling-stroke"`, `paint-order`, dashes and markers never appear in a master.

## 5. Transforms

A `transform` on a path is a trap: tools that read geometry (icon converters, cutters, some audits) ignore or mis-apply it. Use transforms while composing (`rotate(45 50 50)` is a fine way to build a diamond from a square), then **flatten**: `_geom.flatten_document_to_paths()` does this for the Android export, and `check_logo.py` and `lockup.py` apply transforms when they measure. For the delivered master, bake the numbers into the path. One `viewBox` and zero transforms is the goal.

## 6. What never goes in a master

| Element | Why | Where it belongs instead |
|---|---|---|
| `<text>` | depends on installed fonts; is not artwork | outlines via `text_to_path.py` |
| `<image>`, base64 rasters | not vector; breaks every export | nowhere in a logo |
| `<filter>` (blur, shadow, glow) | not supported by many consumers; hides weak form | marketing layer only |
| `<linearGradient>`, `<radialGradient>`, `<pattern>` | fine in an icon export, not in the master | icon/marketing variants with a flat master beside them |
| `<use>`, `<symbol>`, external `href` | indirection that converters drop | expand into paths |
| `<style>`, classes, CSS variables | fine in `favicon.svg` (dark mode) only | attributes on the path |
| `<script>`, `<foreignObject>`, `<a>` | security and portability | never |
| `opacity`, `mix-blend-mode` | semi-transparent marks are not reproducible in print or embroidery | solid colours; a tint is a different colour |
| `clip-path`, `mask` | allowed in exploration; flatten before delivery | boolean operations (skia-pathops) |
| Metadata from editors (`inkscape:`, `sodipodi:`, `data-name`, Figma ids) | noise | strip |

`check_logo.py` reports each of these as an error or a warning.

## 7. Accessibility and metadata

- Inline in HTML: `role="img"` and `aria-label` on the root, a `<title>` as first child. If the logo is also a link, the link gets the label and the SVG gets `aria-hidden="true"`.
- As `<img src="logo.svg" alt="Ledgerly">`: the `alt` is the name, not "logo".
- A `<desc>` is optional; never put the brand rationale in it.
- Keep the `data-*` attributes the scripts write (`data-font`, `data-cap-height`, `data-clearspace`): they are the machine-readable brand guide for the next script, and harmless in browsers.

## 8. Renderers and their quirks

| Renderer | Notes |
|---|---|
| **rsvg-convert** (librsvg; `brew install librsvg`) | The default here. Fast, accurate for paths, fills, evenodd, basic text. Good PDF output. |
| **resvg** | Very accurate, static binary; used if present. |
| **CairoSVG** (pip) | Pure Python fallback; fine for paths; weak on filters and some text features. |
| **ImageMagick** | Delegates to librsvg or its internal MSVG renderer, which is weak; avoid as the reference renderer. |
| **Inkscape** | Full featured, slow to start; fine for one-off conversions and PDFs. |
| **Browsers** | The ground truth for favicons and inline SVG; support `prefers-color-scheme` inside `favicon.svg`. Safari ignores SVG favicons in some versions; ship ICO too. |
| **macOS QuickLook/sips** | Can rasterise simple SVGs; not for production. |

Arcs, evenodd, cubics and transforms render identically in all of these when the file follows §1 to §6. Differences appear with strokes (joins and miter limits), filters, text and CSS.

## 9. Naming and files

```
brand/
  <name>-symbol.svg            master symbol (colour)
  <name>-symbol-compact.svg    simplified for < 32 px (if needed)
  <name>-wordmark.svg          outlined type
  <name>-horizontal.svg        lockup
  <name>-stacked.svg           lockup
  <name>-tagline.svg           optional
  colors/                      palette.md, tokens.css, tailwind.colors.js, Colors.swift, colors.xml, palette.json
  dist/                        the export kit (svg/, png/, web/, ios/, android/, print/)
  brand-guide.md
  runners-up/                  the two unchosen concepts, for the record
```

Lowercase, hyphens, the brand name first, the variant last (`-black`, `-white`, `-color`, `-compact`).

## 10. Validation loop

Every time you write or change an SVG:

1. `python3 scripts/render.py file.svg --out /tmp/x.png --size 512` and **open the PNG with the Read tool**. Describe what you see in one sentence. If the sentence is not what you intended, fix the path before anything else.
2. `python3 scripts/check_logo.py file.svg` for structure, geometry and small-size behaviour; fix errors, read warnings.
3. `python3 scripts/render.py file.svg --sheet /tmp/sheet.png` and look at the 16 px zoom, the reversed row, the blur and the silhouette.
4. Repeat until a round changes nothing you can see.

A path that parses is not a logo; a PNG you have looked at is evidence.
