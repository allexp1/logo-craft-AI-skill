# Perception: why the rules work

The rules of logo design are instances of how human vision and memory behave. Knowing the mechanism lets you predict a failure before you render it, and explain a fix in terms a client accepts.

Contents: 1 coarse-to-fine recognition · 2 Gestalt principles and their logo uses · 3 figure, ground and negative space · 4 distinctiveness and memory · 5 reading letters · 6 size, distance and sampling · 7 colour perception · 8 culture and direction · 9 what this means for testing

## 1. Recognition is coarse to fine

The visual system registers the global shape (silhouette, mass distribution, dominant orientation) before any detail. A logo seen for a fraction of a second, from a distance, or at 16 px is recognised, if at all, by its silhouette. This is the basis of the blur ("squint") test: blur the mark and see whether what remains is still distinct. It is also why the first design decision is the silhouette, and why outline-only marks and marks made of many small parts are weak: their silhouette is a blob.

Design rule: decide the silhouette first, then the internal structure, then the details. Test in that order.

## 2. Gestalt principles and what they do in a mark

| Principle | What the eye does | Use in a logo | Hazard |
|---|---|---|---|
| Proximity | Groups elements that are near each other | Dots or bars read as one symbol if gaps are small and even | Uneven gaps create unintended subgroups |
| Similarity | Groups elements that share shape, size or colour | Repetition of one module (stripes, dots, arcs) gives unity | Two slightly different radii read as a mistake, not a choice |
| Closure | Completes incomplete outlines | An open circle still reads as a circle; a letter can be implied by three strokes | Too large a gap and the form fragments, especially when small |
| Continuation | Follows a path across interruptions | A stroke that passes behind another still reads as one; implied lines connect parts | Accidental tangencies (a curve just touching a line) create visual tension |
| Figure and ground | Assigns one region as object, the rest as background | Counters, holes and negative-space devices | Ambiguous figure/ground is a trick that must not be the *only* reading |
| Symmetry | Prefers symmetric interpretations | Symmetric marks feel stable, institutional | Near-symmetry (1 to 3° or a few units off) reads as an error; be symmetric or clearly not |
| Common fate | Groups things that move or point together | Arrows, rays, chevrons sharing a direction read as one gesture | Mixed directions read as noise |
| Prägnanz (good form) | Prefers the simplest interpretation | Simple geometric marks are remembered as themselves, complex ones are remembered as a category ("a swoosh thing") | Complexity is stored as a label, not a shape |

## 3. Figure, ground and negative space

The classic devices: the arrow between the E and the x of FedEx (Lindon Leader, 1994); the peacock body cut from the NBC feathers; the bear inside the Toblerone mountain; the "31" in the BR of Baskin-Robbins. Amazon's smile is a *positive* arrow from a to z, not a negative-space trick.

The rule that governs all of them: **the first reading must work before the hidden reading is discovered.** FedEx is a clean wordmark whether or not you see the arrow. A negative-space device that compromises legibility (letters distorted to make a shape between them) fails as a logo even if it wins a Reddit thread. A second reading is a gift to the viewer, found later, remembered forever. It is never the price of admission.

Practical test: show the mark to someone (or describe it to yourself) for two seconds. If they first ask "what is that shape?", the ground has taken over.

## 4. Distinctiveness and memory

- **Von Restorff effect:** the item that differs from its neighbours is remembered. A mark on a category shelf of blue circles is remembered if it is not a blue circle. This is why the competitor audit is a design step, not a legal step.
- **One idea is memorable; two are a list.** Memory stores a mark as a gist ("the orange arrow that smiles"). Two ideas compete for one gist slot and both lose.
- **Processing fluency:** forms that are easy to parse are liked more and judged more trustworthy. Clean geometry, even spacing and clear silhouettes buy trust before the viewer knows why.
- **Mere exposure:** repeated viewing increases liking. This is why abstract marks work *eventually* and why a redesign that discards recognised shapes spends equity that took years to build.

## 5. Reading letters

Readers recognise words by letter features and word shape, with the top half of lowercase carrying most information. For wordmarks and monograms:

- **Ambiguous pairs:** I/l/1, O/0, rn/m, cl/d, vv/w, nn/m when connected. Kia's 2021 wordmark became "KN" for many readers because the connected strokes removed the feature (the gap) that distinguishes I from the diagonal of A. Test unprompted: what does a fresh reader say the mark says?
- **Lowercase cohesion:** lowercase words hold together with tighter tracking; capitals need more room because they have no ascender/descender rhythm to bind them.
- **Counters carry identity:** the inside of a, e, g, s is what makes them readable; small counters close at small sizes. Open counters and larger apertures survive reduction.
- **Reversed type looks bolder** (irradiation: light spreads into dark). White-on-dark wordmarks often need a slightly lighter weight or looser spacing. IBM ships a different reversed construction for this reason.

## 6. Size, distance and sampling

A 16 px favicon is a 16 by 16 grid: 256 samples. Any feature thinner than one pixel (1/16 of the mark's height) becomes a grey smear; any gap narrower than one pixel merges. Practical minima for a symbol that must work at 16 px:

| Feature | Minimum at 16 px | In master units (height 100) |
|---|---|---|
| Stroke or bar | 1 px, safer 1.5 px | 6 to 9 units |
| Gap or counter | 1 px, safer 1.5 px | 6 to 9 units |
| Distinct parts | at most 3 or 4 | each at least 3 px at 16 px (about 19 units) |
| Corner radius | less than 1 px is invisible | below 6 units a radius reads as a sharp corner |

Beyond 16 px, 24 and 32 px (browser tabs on HiDPI, Android notification icons, macOS menu bar) are the realistic floor for detail. 48 to 128 px (app icons at common sizes) can carry one more level. These numbers are what `check_logo.py` measures; its "thinnest stroke at 16 px" and "smallest gap at 16 px" lines are this section applied.

Distance obeys the same rule: a sign read from 30 m is a favicon.

## 7. Colour perception

- **Lightness carries form; hue carries mood.** A mark whose parts differ only in hue (red next to green of equal lightness) vanishes in greyscale and for colour-blind viewers (about 8% of men). Test in greyscale and under protanopia, deuteranopia and tritanopia simulation (`palette.py` does this with the Machado 2009 matrices).
- **Simultaneous contrast:** a colour looks different on white, on black and on a brand colour. Approve the palette in context, not on a swatch.
- **Chromatic aberration and vibrating edges:** saturated complementary colours of equal lightness (pure red on pure blue) shimmer at the boundary. Separate them by lightness or by a neutral.
- **"Blue means trust" is folklore when stated universally.** Colour associations are contextual (category conventions, culture, the competitor shelf). Audit the category, then decide to conform or depart on purpose.

## 8. Culture and direction

- **Reading direction:** Hebrew, Arabic, Persian and Urdu read right to left. A horizontal lockup for an RTL wordmark puts the symbol on the right; arrows and "forward" gestures flip meaning. The lockup script handles the mirroring; you must handle the semantics.
- **Symbols:** owls (wisdom in the West, bad omen in parts of India and the Middle East), hand gestures, animals, religious geometry (crosses, crescents, six-pointed stars), the colour white (mourning in parts of East Asia) and red (luck in China, danger in the West) all carry local meaning. When the audience is international, prefer forms with no fixed cultural reading, or check the specific markets.
- **Scripts in one lockup:** matching Latin and Hebrew or Arabic is a matter of apparent weight and height, not of imitating each other's shapes; see `typography.md`.

## 9. What this means for testing

Every test in `critique.md` is one of the mechanisms above made observable:

| Mechanism | Test |
|---|---|
| Coarse-to-fine | Blur and silhouette panels on the inspection sheet |
| Sampling | 16, 24, 32 px rows; the "16 px x6" zoom |
| Irradiation | Reversed row on dark |
| Hue vs lightness | Greyscale panel; CVD simulation of the palette |
| Figure/ground | Silhouette panel: does the black shape alone still read? |
| Letter features | Unprompted reading of the wordmark; ambiguous-pair check |
| Distinctiveness | Competitor shelf at equal size in grey |
| Memory | Doodle test; "describe it in five words" |
