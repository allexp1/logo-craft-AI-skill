# Critique: testing and reviewing a mark

How to judge a logo (your own candidates or an existing one) with evidence rather than taste. Every test here produces something you can show: a render, a number, a sentence. Record results; "scalable" is a claim, "passes at 16 px in black" is a result.

Contents: 1 the look loop · 2 the test matrix · 3 the perception tests · 4 the concept tests · 5 reading check_logo.py · 6 failure patterns and fixes · 7 reviewing someone else's logo · 8 the redesign audit · 9 presenting critique

## 1. The look loop

1. Render: `python3 scripts/render.py mark.svg --sheet sheet.png` (and `--out big.png --size 1024` for detail).
2. **Open the PNG with the Read tool.** Describe what you see in one plain sentence before judging it. If the sentence contains a flaw ("the ring looks thicker on the left"), it is real; fix it.
3. Measure: `python3 scripts/check_logo.py mark.svg`.
4. Change one thing. Repeat. Stop when a round changes nothing you can see.

Never judge from the SVG source. A path that parses tells you nothing about how it looks.

## 2. The test matrix

| Test | How | Pass when |
|---|---|---|
| 16, 24, 32, 48, 128 px | sheet rows; the "16px x6" zoom | At 16 and 24 the parts are distinct, nothing smears to grey, counters stay open; at 32+ the mark is recognisably itself |
| One colour (black) | sheet row 3 | Nothing relied on colour to separate parts |
| Reversed (white on dark) | sheet row 4 | Reads as the same mark; not noticeably heavier (thin if so) |
| Greyscale | sheet panel | Two-colour marks still show two tones |
| Blur (squint) | sheet panel | The silhouette is still distinct from the competitors' |
| Silhouette | sheet panel | The black mass alone reads as the mark |
| Large (1024 px) | `--out` | Curves smooth, joins clean, points at extrema, no kinks or slivers |
| Mirror and rotate | mentally or with a transform | Construction errors (uneven weights, off angles) do not appear |
| Circle crop | kit's `social-avatar-1024-circle-preview.png`, Android `adaptive-preview-circle.png` | Nothing important is cut; optical centre looks centred |
| In context | favicon in a tab (16 px on light and dark), app icon on a home screen (60 px on a wallpaper), OG card (1200 × 630), a header at 32 px high | It belongs; it is visible; it is not the loudest thing |
| Competitor shelf | compare sheet with the 5 nearest marks (describe them if you cannot draw them) | Distinct at 32 px in grey |
| Unprompted reading | ask (or imagine a fresh reader): "what does this say?" | The name is read correctly; no "KN" |
| Minimum size | shrink until it fails; record the size | A number in the guide, per lockup |

## 3. The perception tests

- **Doodle test**: could someone draw it from memory after one look? If not, there is no single memorable property.
- **Five words**: describe the mark in five words. If you need ten, it has two ideas.
- **Two-second test**: show it for two seconds (or imagine it on a passing bus). What remains?
- **First reading / second reading**: does the primary reading work with the clever device covered?
- **Near-symmetry**: is anything *almost* symmetric, *almost* 45°, *almost* the same radius? Make it exact or clearly different.
- **Weight**: do all strokes look the same weight (allowing for deliberate contrast)? Horizontals should look as light as verticals (they are usually drawn thinner).
- **Spacing**: squint at the wordmark; look for dark clumps and holes.

## 4. The concept tests

- **Appropriate** (Haviv): does it feel right for this category and audience? Would a stranger guess the sector within two?
- **Distinctive**: on the shelf, does it stand out? Does it resemble a famous mark (bitten fruit, swoosh, three stripes, overlapping circles, hexaflower, four-point sparkle)?
- **Simple**: can it be embroidered, cut from vinyl, drawn with a marker?
- **Durable**: would it still fit if the product changed? Does it depend on a 2026 trend?
- **True**: does the rationale survive being said aloud without embarrassment? No retrofitted geometry stories.
- **Cliché check**: is it on the watchlist in `industry-conventions.md` §3? What is the one-sentence defence?

## 5. Reading check_logo.py

The script prints a score (100 minus 15 per error and 5 per warning) and sections:

- **Structure**: errors for live text, rasters, filters, scripts, external references, missing viewBox, unclosed filled subpaths, path parse errors; warnings for gradients, `<use>`, duplicate ids, high point counts, transforms. Errors are gates.
- **Colour**: palette size over three; contrast on white and on black below 3:1 (a visibility warning, not a WCAG claim).
- **Geometry**: ink margins (too tight or very uneven), mass off centre, aspect ratio far from square for a symbol, near-miss angles (0.6 to 2.5° off the 45° grid), stroke widths that are nearly but not quite equal.
- **Raster at 256/32/16 px**: number of parts and holes at each size (parts that merge or break between sizes are reported), thinnest stroke and smallest gap in pixels at 16 and 32, mass offset from the centre.
- `--kind` picks the ruleset (symbol, wordmark, lockup; auto-detected from `data-font` and aspect ratio); `--expect-parts N` asserts the intended part count; `--json` for scripts.

A score of 100 means no detectable defects, not a good logo. A score below 70 means stop and fix before presenting.

## 6. Failure patterns and fixes

| What you see | Likely cause | Fix |
|---|---|---|
| Grey smear at 16 px | strokes or gaps under 1 px (6 units of 100) | Thicken to 8+ units; remove detail; make a compact variant |
| Parts merge at small size | gaps too small or too many parts | Fewer parts, gaps = stroke weight or more |
| Looks heavier reversed | irradiation | Thin the white version 2 to 5%; open tight gaps |
| "Something is off" with nothing wrong in the numbers | missing optical corrections | Overshoot, thinner horizontals, optical centre, equalise apparent sizes |
| Looks like a mistake, not a choice | near-symmetry, near-45°, mixed radii | Make exact or clearly different; one radius system |
| Reads as the wrong letters | connected or distorted letterforms | Restore the distinguishing gap; test unprompted reading |
| Feels generic | untouched geometric sans, three-arc symbol, gradient blob | Add one specific property; modify one letter with intent |
| Feels like a competitor | shelf not audited | Change the shape family or the colour decision; redo the audit |
| Looks like clip art | too literal, too detailed | Go one level more abstract; cut detail by half |
| Wordmark spacing lumpy | metric spacing | Optical spacing: equalise area between letters; fix pairs |
| Icon looks off-centre in the circle | geometric centring | Shift up 1 to 3%; check the circle preview |
| Two brands in one lockup | symbol and wordmark weights or styles disagree | Match apparent weight; echo one detail (radius, angle, terminal) |
| Kinks and slivers at 1024 px | boolean debris, handles not collinear | Clean points; points at extrema; collinear handles |

## 7. Reviewing someone else's logo

1. Brief in two lines: what the company does, who it is for, where the mark lives.
2. Run the sheet and the audit; look before reading numbers.
3. Write the verdict in this order: what works (be specific), what fails (with the render or the number as evidence), the three fixes with the largest effect, whether a redraw is justified (and why not, if not).
4. Offer the fixes as SVGs if asked. Do not redesign unasked.
5. Say what you did not test (shelf with real competitors, trademark, print).

## 8. The redesign audit

Before touching an existing mark, list its equity: shape, colour, name treatment, mascot, any device people mention when they describe it. Rate each **keep / evolve / drop** with a reason that starts "because the business..." for every drop. Keep the kept items as constraints in the brief. Compare old and new on one sheet at equal size and in grey, so the change is judged as form, not as novelty.

## 9. Presenting critique

- Lead with the strongest observation, in plain language a founder understands ("at tab size the two rings merge into one grey disc").
- Show the evidence (the sheet crop) beside the sentence.
- Give the fix, not only the fault.
- Separate taste from test: "I would prefer a warmer colour" is taste; "the green and the red are confusable for deuteranopes (ΔE 6)" is a test.
- Keep the honesty paragraph: what was tested, what was not.
