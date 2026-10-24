# {{NAME}} brand guide

Version {{VERSION}} · {{DATE}} · Files in `brand/`

## 1. The mark

What it is (one sentence), what it is not (one sentence). Construction summary: angle vocabulary, radius system, stroke weights, proportions.

![primary lockup](dist/web/og-image.png)

## 2. Variants and when to use each

| Variant | File | Use when |
|---|---|---|
| Horizontal lockup | `{{SLUG}}-horizontal.svg` | Website header, documents, wide spaces |
| Stacked lockup | `{{SLUG}}-stacked.svg` | Square-ish spaces, print, posters |
| Symbol | `{{SLUG}}-symbol.svg` | App icon, avatar, 32 to 120 px |
| Compact symbol | `{{SLUG}}-symbol-compact.svg` | Favicon, under 32 px |
| Wordmark alone | `{{SLUG}}-wordmark.svg` | Where the symbol already appears nearby |
| Reversed (white) | `*-white.svg` | On dark or photographic backgrounds |
| One colour (black) | `*-black.svg` | Print in one ink, embossing, engraving |

## 3. Clear space and minimum sizes

Clear space: {{CLEAR}} cap heights on every side. Minimum: symbol {{MIN_SYMBOL}} px, horizontal lockup {{MIN_LOCKUP}} px wide, print lockup {{MIN_PRINT}} mm wide.

## 4. Colour

| Role | Token | Hex | OKLCH | Contrast on white | Contrast on dark |
|---|---|---|---|---|---|
| Primary | `--{{SLUG}}-primary-500` | | | | |
| Ink | | | | | |
| Accent | | | | | |

Colour-vision check (Machado protanopia/deuteranopia/tritanopia): {{CVD_RESULT}}. Print: CMYK conversions are approximate; proof before volume printing. Pantone matches are not chosen here.

## 5. Typography

Wordmark: {{FONT}} {{WEIGHT}}, tracking {{TRACKING}}, modifications: {{MODS}}. Licence: {{LICENCE}} (logo use permitted: {{YES_NO}}). Supporting typeface for UI and documents: {{UI_FONT}}.

## 6. Do not

- Stretch, rotate, outline, add effects or shadows, recolour outside the palette.
- Place on busy backgrounds without the reversed variant or a contained version.
- Rebuild the wordmark from the live font; always use the SVG.

## 7. What was tested, and what was not

Tests run: sizes 16 to 1024, one colour, reversed, blur, greyscale, CVD simulation, `check_logo.py` score {{SCORE}}. Not run: trademark clearance (search USPTO/EUIPO/WIPO before filing), printed proofs, user recognition study.

## 8. Runners-up

The alternative concepts and why they were not chosen, in `brand/runners-up/`.
