# Colour

Colour is the last decision and the first thing people mention. Make it last so that the form earns its place in black; make it well so that the product's UI, icons and print inherit a system rather than a hex code.

Contents: 1 order of decisions · 2 how many colours · 3 contrast rules (what WCAG says and does not say) · 4 colour vision deficiency · 5 OKLCH and ramps · 6 light, dark, reversed · 7 print · 8 category conventions vs "colour psychology" · 9 gradients and materials · 10 commands and tokens

## 1. Order of decisions

1. Approve the mark in black on white and white on black.
2. Choose one dominant colour from the brief (existing equity, category decision, audience) and test it on white, on black, and next to the competitor shelf.
3. Add a second colour only if it has a job (an accent inside the mark, a UI state, a secondary brand). Three is the ceiling for the identity palette; the UI palette is built from ramps of these, not from more hues.
4. Build ramps and neutrals, check contrast and colour-vision confusability, define the dark-mode variants, then write the tokens.

## 2. How many colours

- **One colour** is the strongest identity choice (Coca-Cola red, Tiffany blue, Spotify green) and the easiest to reproduce. A one-colour mark with a black and a white version covers 95% of uses.
- **Two colours** work when they have distinct roles (symbol and wordmark; a dot of accent inside a mark) and distinct lightness (not two mid-tones).
- **Many colours** are a system choice (Google, NBC, Microsoft) that only works with simple geometry and strict rules; Bokhua's advice to approve in black first applies doubly.

## 3. Contrast: what WCAG actually requires

- **Logos and brand names are exempt** from WCAG text-contrast requirements (SC 1.4.3 and 1.4.11 exclude logotypes). Do not invent "the logo must meet 4.5:1".
- **Everything else in the branded UI is not exempt**: body text needs 4.5:1, large text 3:1, UI components and meaningful graphics 3:1 (SC 1.4.11). A brand colour that will be used for buttons and links therefore needs a step that passes 3:1 on white (and on the dark background) and a text step that passes 4.5:1. `palette.py` prints the contrast of each ramp step so you can name them ("use 700 for text on white").
- Favicon and app icon: no legal requirement, but a mark that is invisible on the browser's dark tab bar or on a dark home screen is a failure; see §6.

## 4. Colour vision deficiency

About 8% of men and 0.5% of women have some form; deuteranomaly (reduced green sensitivity) is the most common. Rules:

- Never let two brand colours carry meaning only by hue. Separate by lightness as well.
- Red/green, and to a lesser degree blue/purple and green/brown pairs, are the classic confusions.
- `palette.py` simulates protanopia, deuteranopia and tritanopia (Machado 2009 matrices) for each colour and reports pairs whose simulated difference falls below a visible threshold ("confusable"). Fix by changing lightness or chroma, not only hue.
- Check the mark itself in greyscale: if a two-colour mark becomes one grey blob, the colour was doing work the form should do.

## 5. OKLCH and ramps

Build and adjust colours in **OKLCH** (perceptual lightness L, chroma C, hue H) rather than HSL: equal steps in L look equal, and changing L keeps the hue stable (HSL "lightness" shifts hue and saturation unpredictably). `palette.py` builds 11-step ramps (50 to 950) from each brand colour with the brand colour placed on its nearest step, chroma falling off toward white and black, plus a neutral ramp tinted with the primary hue so greys belong to the brand. OKLCH does not guarantee that a colour is printable or that it passes contrast; it only makes the adjustments predictable.

## 6. Light, dark and reversed

- The **reversed (white) mark** is a required deliverable; thin it slightly if it looks heavy (irradiation).
- The **mark on dark backgrounds** in colour usually needs a lighter, slightly less saturated version of the brand colour (a dark navy vanishes on black). `palette.py` proposes a `for_dark_backgrounds` colour (L raised by about 0.14, chroma trimmed); judge it on the inspection sheet's dark row.
- **Favicons**: ship an SVG favicon with a `prefers-color-scheme: dark` rule so a dark mark becomes light on dark tab bars; the export kit writes it automatically for single-colour symbols.
- **iOS icons** need light, dark and tinted appearances (Icon Composer); **Android** needs a monochrome layer for themed icons. The export kit produces all of these from the symbol and the background colour.

## 7. Print

Screen CMYK values are an estimate. For print, choose a Pantone (coated and uncoated appear different) or a CMYK build with a printer's swatch book, then record both in the guide. Avoid colours far outside the CMYK gamut (saturated oranges, bright greens, electric blues) as the *only* identity colour; or accept that print will be duller and specify the closest spot colour. One-colour print and embroidery use the black version.

## 8. Category conventions, not "colour psychology"

Universal tables ("blue means trust, green means growth") are folklore when stated without context (Elliot and Maier's review of colour psychology is explicit about this). What is real: **category conventions** that audiences have learned. Finance and infrastructure lean blue and navy; ecology and health lean green; kids and food lean warm saturated hues; luxury leans black, white and metallics; AI products of 2023 to 2026 lean purple-to-teal gradients (now a cliché). Audit the shelf, then decide: conform for instant category membership, or depart for distinctiveness. Monzo's coral and Robinhood's green in finance, Slack's aubergine in work tools, and Duolingo's green in education are departures that became equity.

## 9. Gradients and materials

Instagram's 2016 gradient icon shows gradients can be identity; it does not license hiding weak geometry behind a glow. Rules: the flat one-colour version is approved first and shipped alongside; a gradient has two or at most three stops with hues adjacent in OKLCH (no grey dead zone in the middle); print and embroidery get the flat version; the master SVG stays flat and the gradient is applied in the icon or marketing layer. The same applies to Liquid Glass (iOS 26/27) and other material effects: they are rendered by the platform from flat layers; never bake them into the artwork.

## 10. Commands and tokens

```bash
python3 scripts/palette.py --brand "#0F766E" --suggest                 # harmonies and neutrals to consider
python3 scripts/palette.py --brand "#0F766E" --brand "#F59E0B" --name ledgerly --out brand/colors
python3 scripts/palette.py --brand "#0F766E" --json                    # machine-readable
```

`--out` writes `palette.md` (report with contrast, CVD, ramps, rules), `tokens.css` (`--ledgerly-primary-500` etc.), `tailwind.colors.js`, `Colors.swift`, `colors.xml`, `palette.json`. Put the 500-ish step as the brand colour, use 600 to 900 for text on white and 100 to 300 for text on dark, and name those roles in the brand guide.
