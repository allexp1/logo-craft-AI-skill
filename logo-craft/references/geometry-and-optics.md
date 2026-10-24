# Geometry and optical correction

Use geometry to organise; use perception to finish. A grid, a golden ratio or a set of Fibonacci circles is a construction aid, not evidence of quality (the "golden ratio" construction of the Apple logo is a documented myth). The eye is the final judge, and these procedures tell you where the eye usually disagrees with the ruler.

Contents: 1 construction discipline · 2 the optical corrections · 3 curves and points · 4 small-size engineering · 5 doing it in SVG · 6 verifying

## 1. Construction discipline

A mark reads as one thing when its parts obey one small set of rules. Decide these before drawing, write them in the brand guide afterwards:

- **Angle vocabulary.** Pick one family: {0°, 90°, 45°} or {0°, 90°, 30°, 60°} or a single signature angle (e.g. 12° for everything that slants). A mark with a 43° and a 47° diagonal looks broken, not dynamic; `check_logo.py` flags angles 0.6 to 2.5° off the 45° grid as probable mistakes.
- **Radius system.** One base radius r and multiples (r, 2r, 4r) for all corners; or sharp everywhere; or fully round everywhere. Mixed radii that are not multiples read as inconsistency. Concentric shapes share a centre and differ by stroke width, so inner radius = outer radius minus stroke.
- **Stroke weight system.** One weight for all strokes, or two in a clear ratio (1 : 1.5 or 1 : 2). Gaps between parallel strokes equal the stroke weight or a fixed multiple of it.
- **Terminal logic.** All stroke ends flat, or all round, or all cut at the same angle. Mixed terminals are the most common tell of an unresolved mark.
- **Proportions.** Decide the overall bounding ratio (1:1 for symbols that become icons; a wordmark's ratio follows the type). Inside, use a few repeated measures (the stroke weight as the module is a classic choice: Rand's IBM stripes, the Mastercard circle overlap).
- **Optional ratios.** The golden ratio (about 1 : 1.618), √2 (1 : 1.414) or a simple 2 : 3 are useful to relate two sizes. Use one at most and do not advertise it.

Superellipse ("squircle") note: Apple's icon mask and many modern marks use a superellipse rather than a rounded rectangle; the corner curvature continues smoothly into the straight sides. If a mark will sit on an iOS icon, concentric shapes inside should use the same kind of corner so they do not fight the mask. A good SVG approximation is a rounded rectangle with the corner drawn as a cubic whose handles are about 0.55 of the radius on each side rather than a circular arc (0.5523 is the circle; try 0.6 to 0.7 for a squircle feel).

## 2. The optical corrections

Each of these is a documented perceptual effect; the amounts are starting points to judge by eye at 128 px and 32 px, not laws.

| Effect | What the eye does | Correction | Starting amount |
|---|---|---|---|
| **Overshoot** | Round and pointed forms aligned to a flat line look smaller/shorter than flat forms | Let circles and points extend past the baseline and cap line | 1 to 3% of the height; more for sharp apexes, less for shallow curves |
| **Horizontal heaviness** | A horizontal bar of the same thickness as a vertical looks heavier | Thin horizontals | 5 to 10% thinner; diagonals slightly thinner than verticals too |
| **Optical centre** | The perceived centre of a shape sits above the geometric centre | Place a symbol slightly above centre in a square or circle | Shift up by 1 to 3% of the container; check with the circle crop |
| **Apparent size** | Of equal bounding boxes, a circle looks smaller than a square, a triangle smaller still | Enlarge round and pointed shapes relative to squares | Circle about 3 to 6% larger in diameter than the square's side; triangle more; always by eye |
| **Bone effect** | A straight stem joined to a semicircle looks pinched at the join | Ease the join: slightly widen the stem near the curve, or make the transition a longer tangent | Judge by eye; a few percent |
| **Stroke crossing** | Where two strokes cross or meet, the ink mass looks heavier | Thin strokes slightly near joins or open the join (ink trap only for print at small sizes) | 5 to 10% local thinning |
| **Irradiation (reversal)** | White on dark looks bolder than black on white | For the reversed version, thin strokes slightly and open tight gaps | 2 to 5% thinner; IBM ships a distinct reversed construction |
| **Spacing** | Equal metric gaps between letters do not look equal (round next to straight looks farther apart) | Space by equalising the *area* between shapes, not the distance | Judge in sequence; `text_to_path.py --tracking` for the overall feel, then adjust pairs |
| **Near-symmetry** | A shape that is almost symmetric reads as an error | Make it exactly symmetric or clearly asymmetric | Threshold around 1 to 2° or 2% |

Workflow: build the pure geometry first (it is easy to compute and to keep consistent), render at 128 px and 32 px, then apply the corrections one at a time, re-rendering each time. Record what you changed and why; the brand guide should say "the O overshoots the baseline by 1.5 units" so the next person does not "fix" it back.

## 3. Curves and points

Clean curves are what separates a professional outline from an amateur one, and they are invisible until they are wrong.

- **Points at extrema only.** Place on-curve points at the top, bottom, left and right of a curve (where the tangent is horizontal or vertical), plus where curvature changes. Nothing else. A circle is four points; most letters are under twenty.
- **Handles horizontal or vertical** at extrema; the two handles meeting at a smooth point are collinear (G1) and, for the best curves, change curvature smoothly (G2). A kink is where they are not.
- **Circle from cubics:** handle length 0.5523 × radius. For a quarter arc from (r,0) to (0,r) around the origin: `M r 0 C r k, k r, 0 r` with k = 0.5523 r. SVG arcs (`A`) are fine in masters, but cubics give you control over tension and are what font and icon tools expect; `_geom.py` converts arcs to cubics when it measures.
- **Join curves to straights tangentially:** the handle at the join lies along the straight segment.
- **No near-duplicate points, no tiny segments**, no zero-length handles. Simplify until removing a point changes the shape.
- **Boolean operations leave debris:** after a union or difference (`pen_sweep.py` unions its strokes with skia-pathops), inspect joins for slivers and kinks and clean them.

## 4. Small-size engineering

A symbol destined for 16 px is engineered, not just scaled. In master units with height 100:

- Strokes and gaps at least 6 units (1 px at 16 px); 8 to 9 is safer. Counters at least 8.
- No more than three or four distinct parts; parts closer than 6 units merge.
- Corners below about 6 units radius read as sharp; do not spend detail there.
- If the mark needs finer detail at large sizes, make a **compact variant** (`<name>-compact.svg`): remove the detail, thicken strokes, open counters, and note the switch size (commonly 32 px) in the guide.
- Pixel fit: a favicon drawn with key edges on the 16-grid (multiples of 6.25 units) renders crisper. Only do this for the compact variant; never distort the master for it.

`check_logo.py` reports the thinnest stroke and smallest gap at 16 and 32 px, the number of parts and holes at each size, and whether parts merge or break. Treat an error there as a failed gate.

## 5. Doing it in SVG

- **Compute, do not eyeball, the geometry.** For anything symmetric or repeated, write ten lines of Python that print the path: rotate a module n times, mirror across an axis, place points on a circle. `fontTools.misc.transform.Transform` is available through `_geom.py` if you want affine maths.
- **Apply corrections as explicit numbers** in the path (an overshoot of 1.5 units is `y = -1.5`, not a `scale(1.015)`): the next person can read it.
- **Strokes in the source, fills in the master.** Draw with `stroke` while exploring; before delivery, convert to outlines (`pen_sweep.py --mode mono --width W` on the centreline, or a boolean union) so renderers and icon pipelines see one filled path.
- **Holes:** either `fill-rule="evenodd"` with any winding, or nonzero with the inner contour reversed. Be consistent in a file.
- **One transform at most**, and flatten it before delivery (`_geom.flatten_document_to_paths` is what the Android exporter uses).

## 6. Verifying

1. `render.py mark.svg --sheet sheet.png` and look at: the 16 px x6 zoom (does anything smear or merge), the reversed row (does it look heavier), the blur panel (is the silhouette still distinct), the silhouette panel (does the black mass alone read).
2. `check_logo.py mark.svg` and read the geometry section: off-grid angles, inconsistent stroke widths, off-centre mass, margins.
3. Overlay test: render at 1024 px, then describe what you see in one sentence. If the sentence mentions a flaw ("the left arm looks thinner"), it is real.
4. Mirror and rotate mentally (or render with a `transform`): construction errors that the reading brain forgives become visible when the shape is not a letter any more.
