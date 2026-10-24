# Process: from project context to a delivered identity

This is the senior designer's workflow adapted to an agent that can read a repository, set type, draw vectors, render and measure. The stages are gates: do not move on until the gate's question is answered with evidence.

Contents: 0 modes · 1 brief · 2 research · 3 word map · 4 concepts · 5 build three · 6 checkpoint · 7 refine · 8 colour and type · 9 system and kit · 10 handover · 11 redesign and review modes · 12 working autonomously

## 0. Choose the mode first

| User says | Mode | Stages |
|---|---|---|
| "make a logo", "we need a brand", "icon for the app" | **New identity** | all |
| "refresh", "modernise", "fix our logo" | **Redesign** | 1, 2, equity audit (§11), then 4 to 10 with the equity as a constraint |
| "is this logo good", "review", "critique" | **Review** | 1 (brief in two lines), tests in `critique.md`, written verdict, optional fixes |
| "just the icon / favicon / app icon" | **Icon** | 1, 4 (symbol only), 5, 6, 7, 9 (icon kit) |
| "wordmark", "logotype", "lettering", "calligraphy" | **Wordmark** | 1, 3, 4 (type directions), 5, 7, 8, 9 |
| "colours", "palette", "brand colours" | **Palette** | 1, 8 only |

## 1. Brief: what must be true before drawing

Start with `scripts/scan_project.py <path>`; it reads README, manifests, theme files, locales and existing assets and prints a draft brief with a "Still to confirm" list. Then fill the brief template (`assets/brief-template.md`). The fields that change the design most:

1. **Exact name** as it should be written (case, spacing, diacritics, Hebrew/Arabic spelling), and whether the name is final.
2. **What it does, for whom, in one sentence**, and the one thing that makes it different.
3. **Where the mark will live**, in order of importance: app icon, favicon, website header, store listing, social avatar, print, signage, merchandise. The smallest important place sets the minimum size.
4. **Platforms**: iOS, Android, web, desktop, print. Each adds deliverables (`deliverables.md`).
5. **Languages and scripts**: a Hebrew product needs a Hebrew wordmark or a bilingual lockup; RTL changes lockups.
6. **Tone**: three adjectives and three anti-adjectives ("confident, calm, precise; not playful, not corporate, not techy").
7. **Competitors and references**: names of the five nearest, and any marks the user admires or hates.
8. **Existing equity**: current logo, colours, fonts, icon; what customers already recognise.
9. **Constraints**: a colour that must stay, a font licence already owned, a shape to avoid, religious or cultural constraints, a deadline.
10. **Decision maker and success criterion**: who says yes, and what "good" means to them.

Gate: you can state the brief in five lines without looking at notes. If the user is unavailable, state assumptions explicitly at the top of your work and continue (§12).

## 2. Research: category, competitors, conventions

- Search the category ("fintech logos 2026", "kids learning app icons", "developer tool logos") and build a **competitor shelf**: the five to eight nearest marks, described in one line each (type of mark, colour, shape family). Note what everyone does (the convention) and what nobody does (the opening).
- Read the matching section of `industry-conventions.md` for the clichés of the sector and the conventions you may want to keep for category recognition.
- Note any **famous mark** in the same shape family you are considering (a swoosh, a bitten fruit, a spiral) so you do not drift into it.
- Record sources and findings in the brief under "Research". Keep research separate from copying: you are mapping the field, not collecting shapes to trace.

Gate: you can name the convention of the category in one sentence, and the opening in another.

## 3. Word map

Put the name in the centre. Branch: what it does, what it feels like, the benefit, the behaviour, the metaphors people use for it, its opposites, the name's letters and their shapes, the name's sound and etymology, the category's objects, the audience's world. Two levels deep. Then look for **intersections**: a word from the benefit branch meeting a word from the letters branch ("lens" + the letter o), a metaphor meeting a behaviour ("ledger" + "calm" = aligned horizontal lines that are not a spreadsheet).

Each intersection is a visual hypothesis. Write it as one sentence: "An O that is also a lens aperture: six blades, open counter, reads as a camera stop and as the letter." Ten to twenty of these is normal. Discard the ones a competitor already owns and the ones on the cliché watchlist unless you can say why yours is different.

## 4. Concepts: 8 to 12 one-liners, three to build

From the hypotheses, write 8 to 12 concepts that are **genuinely different** from each other. Use the diversity matrix so you do not write eight variations of one idea:

| Axis | Options to cover |
|---|---|
| Mark type | wordmark only · lettermark/monogram · pictorial · abstract · emblem · negative-space device |
| Source of form | the name's letters · the product's behaviour · a metaphor · the category object, abstracted · pure geometry |
| Character | geometric and still · organic and in motion · hand-made (lettering, calligraphy) · typographic only |
| Construction | solid mass · single stroke · modular repetition · counter-form |

For each concept: one sentence of idea, one sentence of why it fits the brief, the mark type, and the risk (cliché, legibility, similarity). Then pick **three** that are far apart on the matrix and strong on Haviv's three criteria. A fourth is allowed only if it is a safe typographic option for a client who may not accept a symbol.

Gate: three chosen concepts with written rationale, each different in kind, none on the watchlist without a defence.

## 5. Build three, in black

For each concept, build the actual vector:

1. **Symbol** as a master SVG (square viewBox, black fill, no strokes in the final, no effects), following `svg-craft.md` and the construction discipline in `geometry-and-optics.md`. Draw with computed coordinates; use Python for symmetry and repetition; use `pen_sweep.py` for calligraphic or monoline strokes.
2. **Wordmark**: set the name with `text_to_path.py` in two or three candidate typefaces per concept (`--list-fonts` for curated families by voice). Custom lettering only when the concept needs it.
3. **Render and look.** `render.py --sheet` per candidate, then open the PNG. Fix what you see before measuring.
4. **Measure.** `check_logo.py` on every symbol; resolve errors, read the warnings.
5. **Compare.** `render.py a.svg b.svg c.svg --compare concepts.png --labels ...`: same height, grey, with a small-size row. This sheet is what you present.

Gate: each of the three passes `check_logo.py` with no errors and reads at 16 and 32 px on the compare sheet. If one cannot, replace it rather than defend it.

## 6. Checkpoint: present and choose

Present the compare sheet (grey, equal size, small sizes) and for each concept: the idea in one sentence, why it fits the brief, what it will look like as an app icon, and its risk. No colour, no mockups, no favourites hidden in the order. Ask for a choice or a direction to merge. Never present filler to make a number.

Working autonomously, choose yourself, state why in three lines against the brief, and record the two runners-up in the handover so the user can switch.

Gate: one direction chosen, in writing, with the reasons.

## 7. Refine the chosen direction

In this order, re-rendering after each step:

1. **Silhouette and structure**: is the global shape distinct? Fix proportions first.
2. **Construction consistency**: one angle family, one radius system, one weight logic (`geometry-and-optics.md` §1).
3. **Optical corrections**: overshoot, thinner horizontals, optical centre, apparent-size equalisation, eased joins (§2 there). Judge each by eye on the 128 px and 32 px renders.
4. **Small-size version**: if 16 px fails, make a simplified compact variant (fewer parts, thicker strokes, opened counters) and record the size at which each version takes over.
5. **Reversed version**: check white on dark; thin slightly if it looks heavy.
6. **Wordmark fit**: letterforms that echo the symbol (a radius, an angle, a terminal), optical spacing, cap height relationship.
7. **Run the full test matrix** in `critique.md` and record results.

Stop when a round changes nothing you can see. Three rounds is normal; ten means the concept is wrong.

## 8. Colour and typography, last

- Colour: `palette.py --brand <hex> --suggest`, then build the palette with one dominant colour and at most two supporting ones. Check contrast, CVD confusability and the dark-background variant (`color.md`). The mark must already work in black.
- Typography: confirm the licence of the chosen face (`text_to_path.py --font-info`), decide the UI pairing, and record both in the guide.

## 9. System and kit

1. `lockup.py` builds horizontal, stacked, symbol-alone and wordmark-alone with clear space in cap heights (RTL automatic). Add a tagline lockup only if the brief has a tagline.
2. `export_kit.py` produces the full kit: SVG colour/black/white, PNG, favicon set and manifest, OG image, iOS 1024 light/dark/tinted plus Icon Composer layers, Android adaptive VectorDrawables and mipmaps, Play Store 512, print PDF. Use `--into-web/--into-ios/--into-android` to place files in the project.
3. Fill `assets/brand-guide-template.md` with the real ratios the lockup script printed, the palette, the fonts and licences, the minimum sizes you measured, and the misuse list.

## 10. Handover

The handover message or document contains, in this order: the chosen mark (rendered), the idea in one sentence, the rationale against the brief, the test results (what passed at which sizes, what was simplified), the kit location and what was placed in the project, the runners-up, the risks, and an honesty paragraph: look-alike search done or not, trademark clearance **not** done, print colours not proofed, fonts and their licences.

## 11. Redesign and review modes

**Equity audit before a redesign.** List what people recognise: shape, colour, name treatment, a mascot. Rate each: keep, evolve, drop, with the reason. Mastercard kept the circles; Burberry 2023 brought back the knight and the lettering it had dropped in 2018. Dropping equity needs a sentence that starts with "because the business changed".

**Review mode.** Run `check_logo.py` and `render.py --sheet` on the file, then the critique questions. Write the verdict as: what works, what fails (with the evidence from the renders), the three fixes with the largest effect, and whether a redraw is justified. Offer to make the fixes.

## 12. Working autonomously

When the user has said "just do it" or is not available: state the assumptions you made for the brief at the top, make the concept choice yourself with written reasons, keep the two runners-up as SVGs, never place files into the project without being asked to (write the kit to a `brand/` or `dist/` folder instead), and end with the handover. Ask a question only when the answer changes the whole direction (the name is not final; the product's audience is unknown) and nothing else can proceed.
