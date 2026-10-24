# Calligraphy and lettering

Calligraphy *writes* letters with a tool whose geometry makes the stroke; lettering *draws* letters and revises them; type *manufactures* letters for reuse. A logo may use any of the three, and knowing how the pen made a shape is what lets you draw a convincing one in vector. `scripts/pen_sweep.py` is a pen: give it the centreline you would write and it produces the outline a broad nib, a pointed pen, a brush or a monoline marker would leave.

Contents: 1 Noordzij's model · 2 broad-edge hands · 3 pointed pen · 4 brush · 5 ductus, rhythm, counters · 6 Hebrew and Arabic · 7 from skeleton to logo (workflow) · 8 flourishes · 9 lessons from script logos · 10 commands

## 1. Noordzij's model of the stroke

Gerrit Noordzij (*The Stroke*) describes every letterform as a stroke whose width varies by one of three mechanisms:

- **Translation**: a broad-edged pen held at a fixed angle; thick where the stroke moves across the nib, thin where it moves along it. Produces the contrast of Roman capitals, Carolingian, Foundational, Italic, Uncial, Blackletter. Thick/thin depends on *direction*.
- **Expansion**: a flexible pointed pen (or brush) whose width changes with pressure; thick on downstrokes, hairline elsewhere. Produces Copperplate, Spencerian, brush script. Thick/thin depends on *pressure*, conventionally on the downstroke.
- **Rotation**: the pen angle changes during the stroke (Uncial manipulation, some brush hands); used to control where the thick parts fall.

Use the model to understand *why* a letter has contrast where it does, so that your vector version is consistent (every stroke made by the same imaginary pen). Do not force every vector letter to imitate handwriting; a geometric wordmark is a legitimate "zero-contrast" stroke.

## 2. Broad-edge hands

Pen angle is the angle of the nib's edge to the baseline; slant is the lean of the letters; "nib widths" (nw) is the body height measured in widths of the nib. These are teaching proportions from standard manuals (Harris, Shaw, Faber-Castell), starting points to be judged by eye:

| Hand | Body height | Pen angle | Slant | Character and logo use |
|---|---|---|---|---|
| Roman capitals (Trajan model) | 7 to 8 nw cap height | 25 to 30°, steeper for some diagonals | upright | Authority, heritage, law, wine, institutions; classic serif terminals come from the pen lifting |
| Foundational (Johnston's round hand) | 4 to 5 nw x-height | about 30° | upright | Calm, legible, bookish; a round o is the key letter |
| Italic (chancery) | 5 nw x-height | 35 to 45° (pick one exemplar) | 5 to 10° | Elegant, quick, humanist; narrow branching arches; good for taglines and signatures |
| Uncial | 4 to 5 nw body | 15 to 25° (flat) | upright | Early medieval, round, majuscule-only; Celtic and craft brands; not lowercase with an x-height |
| Carolingian | 3 to 4 nw x-height | about 30° | upright | Round, open, generous; the ancestor of lowercase |
| Blackletter / Textura | 5 nw x-height | 40 to 45° | upright | Dense vertical rhythm, diamond feet; newspapers, beer, metal, heritage; test legibility hard |
| Fraktur / Schwabacher | 5 nw | 40 to 45° with manipulation | upright | Rounder blackletter; same cautions |

The broad pen makes the thick strokes on diagonals from upper left to lower right and on the left and right of round letters (the "stress" is oblique at 30°, vertical at 0°). Keep one pen angle for the whole word unless the hand's model changes it deliberately.

## 3. Pointed pen

| Script | Slant | Shading | Character |
|---|---|---|---|
| Copperplate (English roundhand) | about 55° from horizontal | Shade (pressure) on most downstrokes, including lowercase; hairline connectors and upstrokes | Formal, luxurious, wedding and spirits labels; Coca-Cola's lettering is Spencerian-derived |
| Spencerian | about 52° | Light, selective shading; more hairline, more whole-arm flourish | Lighter and faster than Copperplate; American heritage |
| Modern calligraphy / bounce | variable | Exaggerated pressure, letters off the baseline | Casual, craft, lifestyle; dates quickly |

Pressure rule: apply weight on downstrokes that move toward the writer, release to a hairline on upstrokes and connectors; do not shade everything. In `pen_sweep.py --mode pointed`, `--angle` is the slant (downstroke direction), `--width` the full shade, `--min-width` the hairline, `--pressure` the sharpness of the transition.

## 4. Brush

A brush combines expansion (pressure) with tapered entries and exits, and the stroke edge may be dry or ragged. Thick downstrokes, light upstrokes, a slight bounce. `--mode brush` tapers each stroke's ends (`--taper in,out` as fractions of the stroke) and puts the pressure in the middle. For logos, brush lettering must be cleaned: no stray texture in the master, a solid silhouette that survives 32 px, and a flat version for embroidery.

## 5. Ductus, rhythm and counters

- **Ductus** is the order and direction of strokes. Letters built from the right ductus have joins where a pen would make them and thicks where the pen would place them. Write the ductus before drawing: an o is two strokes meeting at the top left and bottom right thin points; an n is a stem and a branching arch starting from inside the stem.
- **Rhythm**: the interior spaces (counters) and the spaces between letters should feel evenly sized along the word; the test is to blur the word and look for dark clumps and holes.
- **Counters** are the identity of a lettering piece; never let a swash or a join close a counter.
- **Consistent slant**: draw guidelines at the chosen slant and check every stem; a stem 2° off is visible.
- **Branching and joins**: in italic and scripts, the join leaves the stem high (thin) and arrives at the next letter low; a connecting stroke that is thick at both ends is a tell of a fake script.

## 6. Hebrew and Arabic

**Hebrew (square script)** is written with a broad pen held nearly flat (around 0 to 15°), so the contrast is the reverse of Latin: **horizontals thick, verticals thin**. Letters hang from a top line (the "roof"), so align Hebrew lettering by the top line as much as the baseline; ל rises above the line and ק, ך, ן, ף, ץ descend. For a Hebrew wordmark, respect the thick-horizontal stress even in a sans; a Hebrew face with Latin-style vertical stress reads as foreign. Modern Israeli lettering often simplifies to monoline or geometric forms (Secular One, Suez One are display references).

**Arabic** is connected, with four contextual forms per letter and dots that distinguish letters (never omit or move them). Traditional pens are cut obliquely; **Naskh** (book hand, about 15 to 20°) and **Thuluth** (display) have fluid contrast; **Kufic** is geometric and angular and is the natural fit for grids and monograms (square Kufic fits a pixel grid exactly and is the classic choice for geometric logos). Latin/Arabic bilingual lockups usually match the Arabic's baseline-to-tooth height with the Latin x-height and let ascenders and descenders differ.

## 7. From skeleton to logo

1. **Write the ductus** as centrelines: one path per stroke, in the direction the pen would travel. Draw in SVG (`<path fill="none" stroke="#000" d="...">`) at a comfortable size (x-height about 100 units).
2. **Choose the pen**: broad for translation hands (`--mode broad --angle 30 --width <x-height/5>`), pointed for Copperplate/Spencerian (`--mode pointed --angle 55 --width ... --min-width ...`), brush, or mono for a monoline script.
3. **Sweep**: `pen_sweep.py --svg skeleton.svg --mode broad --angle 30 --width 20 --out word.svg` unions the strokes into one filled outline. `--skeleton` overlays the centreline in red for checking; `--separate` keeps strokes apart for editing.
4. **Clean**: open the result as a path and simplify: points at extrema, smooth joins (the union leaves tiny notches where strokes overlap at acute angles), remove slivers, straighten what should be straight. Compare against the hand's exemplar: are the thicks where the pen would put them?
5. **Space** the letters as in `typography.md` §4: equalise interior and exterior spaces by eye.
6. **Test** at 32 and 16 px (`render.py --sheet`): hairlines below 1 px must be thickened (`--min-width`) or the logo gets a bolder compact version. Script logos almost always need a separate symbol or monogram for icons.
7. **Audit** with `check_logo.py --kind wordmark` for unclosed contours, thin strokes and merged letters.

## 8. Flourishes

A flourish must support reading, preserve counters, follow the stroke's natural exit, avoid tangencies (a swash that just touches another letter is a visual error) and never create a shape that reads as a letter. Jessica Hische's test: does the swash feel like a natural extension of the stroke, and does the word stay legible if you cover the flourish? Limit flourishes to entries, exits and one crossbar; a logo is not a wedding invitation.

## 9. Lessons from script logos

- **Coca-Cola**: repeated capitals and sweeping connections make one silhouette; the script is Spencerian in origin (Frank Robinson, 1886) and has been redrawn many times without losing the gesture.
- **Ford**: a lively script contained by an oval; the container gives a script the stability it lacks.
- **Kellogg's**: a signature as an authenticity cue; the K's exaggerated form is the identity.
- **Disney**: stylised signature lettering with character; not a literal autograph, and redrawn for legibility.
- **Instagram 2013** (Mackey Saturday): better joins and letter recognition without abandoning the script.
- **Cadbury 2020**: heritage gesture redrawn for consistency rather than preserved with every irregularity.
- The general lesson: the gesture is the equity; the drawing is redone each generation for the media of its time.

## 10. Commands

```bash
# broad nib, Foundational feel: x-height 100, 5 nw -> width 20, 30°
python3 scripts/pen_sweep.py --svg skeleton.svg --mode broad --angle 30 --width 20 --out word-broad.svg --skeleton
# italic: steeper pen, narrower nib
python3 scripts/pen_sweep.py --svg skeleton.svg --mode broad --angle 40 --width 18 --out word-italic.svg
# Hebrew square script: flat pen, thick horizontals
python3 scripts/pen_sweep.py --svg hebrew-skeleton.svg --mode broad --angle 5 --width 22 --out he-word.svg
# Copperplate: slant 55°, shade 14, hairline 1.5
python3 scripts/pen_sweep.py --svg skeleton.svg --mode pointed --angle 55 --width 14 --min-width 1.5 --pressure 1.6 --out word-cp.svg
# brush with tapered entries/exits
python3 scripts/pen_sweep.py --svg skeleton.svg --mode brush --width 16 --min-width 3 --taper 0.2,0.3 --out word-brush.svg
# monoline marker with round caps
python3 scripts/pen_sweep.py --svg skeleton.svg --mode mono --width 10 --cap round --out word-mono.svg
python3 scripts/render.py word-broad.svg word-cp.svg word-mono.svg --compare pens.png
```
