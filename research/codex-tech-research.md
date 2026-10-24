# Technical craft for programmatic logo generation (Codex research, 2026-10-24)

A reproducible logo workflow should retain editable construction geometry, generate a portable outlined master, and derive platform assets from explicit export recipes. The recommendations below distinguish format requirements from engineering conventions; neither valid SVG nor a successful raster export establishes visual quality.

**Production SVG begins with a stable coordinate system.** Use a documented artboard such as `viewBox="0 0 1024 1024"` for a square mark, or a proportional rectangle for a wordmark. The numbers are user-space coordinates, not required pixel dimensions. `viewBox` maps `min-x min-y width height` into the viewport; preserve the intended aspect ratio and include deliberate clearance. [MDN viewBox](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/viewBox)

Use `M` to move, `L/H/V` for lines, `C/S` for cubic curves, `Q/T` for quadratic curves, `A` for elliptical arcs, and `Z` to close contours. Uppercase coordinates are absolute; lowercase coordinates are relative. Prefer readable construction paths initially, then let optimisation choose shorter representations. [SVG path specification](https://www.w3.org/TR/SVG2/paths.html)

For cut-outs, `fill-rule="evenodd"` alternates inside/outside at successive crossings, independently of contour direction. The default `nonzero` uses signed winding: nested holes normally require opposite contour directions. Overlapping glyph contours can behave differently under these rules, so changing the attribute is not a harmless optimisation. [SVG filling rules](https://www.w3.org/TR/SVG2/painting.html#FillRuleProperty)

Strokes are useful construction tools. Set `stroke-linecap` explicitly—`butt`, `round`, or `square`—and choose joins deliberately; sharp miter joins can project beyond corners until limited by `stroke-miterlimit`. For final interchange marks, **prefer outlined fills**: this freezes the intended stroke silhouette into geometry and removes dependence on stroke interpretation during subsequent transformations. This is a production recommendation, not an SVG requirement. [SVG stroke semantics](https://www.w3.org/TR/SVG2/painting.html#StrokeProperties)

Flatten transforms only after resolving their effect on strokes; nonuniform scaling deserves particular care. Round at serialisation, not repeatedly during construction. Three decimal places is a reasonable starting convention, but acceptable precision depends on coordinate scale and smallest feature. SVGO’s `convertPathData` can apply transforms, shorten commands, remove redundancy, and control `floatPrecision`; compare renders before accepting its output. [SVGO documentation](https://svgo.dev/docs/plugins/convertPathData/)

`<symbol>` defines reusable artwork and `<use>` instantiates it; retain these in controlled sprite systems, but consider expanding instances for standalone interchange. [MDN symbol](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/symbol) For inline monochrome variants, `fill="currentColor"` derives paint from CSS `color`; give exported standalone files an intentional colour. [SVG colour property](https://www.w3.org/TR/SVG2/painting.html#ColorProperty)

Provide an accessible name, for example `<svg role="img" aria-labelledby="brand-title">` containing `<title id="brand-title">Acme</title>`. Keep IDs unique across inline instances. [MDN title](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/title) A conservative master excludes filters, masks, embedded rasters, external fonts, and live `<text>` wherever ordinary paths suffice: renderer feature support varies, especially for typography and effects. Preserve required accessibility metadata and `viewBox` when optimising. [librsvg support](https://gnome.pages.gitlab.gnome.org/librsvg/devel-docs/features.html), [CairoSVG limitations](https://cairosvg.org/svg_support/)

**Text outlining requires shaping before drawing.** `TTFont(path)` reads OpenType/TrueType data; `font.getGlyphSet()` exposes drawable glyphs across TrueType and CFF outlines. Advance widths describe layout movement, not the visible ink bounds. [fontTools TTFont](https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html)

Use `SVGPathPen(glyphSet)` to collect path commands and `TransformPen` to scale, position, and reverse the font’s upward Y axis into SVG’s downward Y axis. With scale `s`, baseline `b`, and positioned glyph origin `(x,y)` in font units, the transform is `(s,0,0,-s,s*x,b-s*y)`. Draw each shaped glyph through that transform. `BoundsPen` supplies actual curve bounds, including extrema between explicit points. [SVGPathPen](https://fonttools.readthedocs.io/en/latest/pens/svgPathPen.html), [BoundsPen](https://fonttools.readthedocs.io/en/latest/pens/boundsPen.html)

Do not equate character lookup with typesetting. Manual GPOS kerning must select the appropriate script/language and feature lookups, handle PairPos format 1 glyph pairs and format 2 classes, and apply both glyphs’ placement and advance adjustments. Legacy `kern` tables are only one possible source. [OpenType GPOS](https://learn.microsoft.com/en-us/typography/opentype/spec/gpos)

The practical route is `uharfbuzz`: create a font and buffer, add text, establish direction/script/language, then call `hb.shape(font, buffer, {"kern": True, "liga": True})`. Consume glyph IDs, `x/y_offset`, and `x/y_advance`; draw at cursor plus offset, then advance the cursor. Do not add kerning again afterward. For mixed scripts or directions, shape appropriately segmented runs. [uharfbuzz example](https://github.com/harfbuzz/uharfbuzz)

Apply tracking as an explicit spacing policy between eligible clusters, avoiding insertion inside combining sequences or joined forms; ligature settings affect where spacing can occur. HarfBuzz exposes cluster mappings for this purpose. [HarfBuzz clusters](https://harfbuzz.github.io/working-with-harfbuzz-clusters.html)

For variable fonts, use `instantiateVariableFont(font, axis_values, static=True)`, save the instance, and shape and outline that same file. Record weight, width, optical size, and other chosen axes; pinning only some axes without `static=True` can leave a variable font. [fontTools instancer](https://fonttools.readthedocs.io/en/latest/varLib/instancer.html)

Google Fonts’ CSS2 endpoint accepts explicit styles, such as `family=Roboto:wght@400`. A request without a browser user agent can receive TrueType URLs, but **do not treat that as a contractual TTF-download API**: Google documents user-agent-dependent responses. Inspect returned `src` URLs and formats. For reproducibility, download the `.ttf` and licence from a commit-pinned `google/fonts` family directory; repository files may themselves be variable. [CSS2 API](https://developers.google.com/fonts/docs/css2), [format negotiation](https://developers.google.com/fonts/docs/technical_considerations), [Google Fonts repository](https://github.com/google/fonts)

OFL fonts may be used in commercial logos and outlined artwork without attribution. Redistributing modified font software introduces separate licence and potentially Reserved Font Name obligations; the artwork does not automatically become OFL-licensed. [Official OFL guidance](https://openfontlicense.org/)

**Rasterisation should use a pinned renderer.** Prefer an existing installation or prebuilt binary; installation weight depends on the machine’s available dependencies.

| Tool | Practical use and limitations |
|---|---|
| `rsvg-convert` / librsvg | `rsvg-convert -w 512 -h 512 -o logo.png logo.svg`; supports substantial static SVG and filter functionality. Check its feature matrix for font and CSS limitations. [Manual](https://gnome.pages.gitlab.gnome.org/librsvg/devel-docs/man-rsvg-convert.html), [support](https://gnome.pages.gitlab.gnome.org/librsvg/devel-docs/features.html) |
| resvg | Portable static-SVG CLI/library with extensive rendering tests. Suitable for deterministic outlined artwork; pin versions because text and filter implementations evolve. [README](https://github.com/linebender/resvg), [changelog](https://github.com/linebender/resvg/blob/main/CHANGELOG.md) |
| CairoSVG | Convenient Python API, requiring Cairo. Complex shaping is limited; supported filters are chiefly `feBlend`, `feFlood`, and `feOffset`, not arbitrary SVG effects. [Support](https://cairosvg.org/svg_support/) |
| ImageMagick | Useful downstream raster tooling, but SVG rendering may delegate to Inkscape, then RSVG, then its internal renderer. Identical commands can therefore use different engines. [Formats](https://imagemagick.com/formats/) |
| Inkscape CLI | Useful when already installed: `inkscape logo.svg --export-type=png --export-width=512 --export-filename=logo.png`. Preserve page bounds when padding matters. [CLI documentation](https://wiki.inkscape.org/wiki/Using_the_Command_Line) |
| Chrome headless | Browser rendering for CSS, fonts, and filters; capture a controlled HTML wrapper with exact dimensions. Wait for fonts explicitly in browser automation. [Headless reference](https://developer.chrome.com/docs/automation-and-testing/headless-cli) |
| macOS tools | `qlmanage -t` requests Quick Look thumbnails; treat these as previews rather than a controlled export pipeline. `sips -z 180 180 input.png --out apple-touch-icon.png` resizes an existing raster. [Apple Quick Look](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/Quicklook_Programming_Guide/Articles/QLDebugTest.html), [sips manual](https://keith.github.io/xcode-man-pages/sips.1.html) |

For multi-resolution ICO, Pillow writes several sizes into one file:

```python
from PIL import Image

Image.open("logo-256.png").convert("RGBA").save(
    "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)]
)
```

Pillow ignores requested sizes above the source size or 256. Use `append_images` to supply separately tuned small-size renders instead of automatic downscaling. [Pillow ICO documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#ico)

**Measurement should separate geometry from perception.** Obtain path extrema with `svgpathtools.Path.bbox()` or fontTools `BoundsPen`; first apply transforms and expand strokes if measuring the painted silhouette. Bounding-box centre is `(xmin+xmax)/2,(ymin+ymax)/2`. Control-point bounds can overestimate curved shapes. [svgpathtools](https://github.com/mathandy/svgpathtools), [BoundsPen](https://fonttools.readthedocs.io/en/latest/pens/boundsPen.html)

For a raster centroid, load RGBA with Pillow and use NumPy to calculate `cx=sum(alpha*x)/sum(alpha)` and the analogous `cy`, sampling pixel centres. A contrast-weighted version can approximate visual mass against a chosen background. These are diagnostic heuristics, not objective optical centring: shape recognition and surrounding negative space still require review. [Centre-of-mass definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.center_of_mass.html)

At 16 px, threshold coverage at several levels, count connected foreground regions and background holes, and compare against expected topology. A disconnected dot may be intentional; a newly broken bridge is suspicious. Under uniform scaling, feature width becomes `feature_units × 16/viewBox_width` pixels. Estimate filled-shape thickness using distance transforms along a skeleton, accounting for raster discretisation; flag subpixel features rather than claiming a universal passing threshold. [Connected-component labelling](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.label.html), [distance transform](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.distance_transform_edt.html)

Count canonical SVG paint values separately from raster colours. Antialiasing introduces additional pixel colours; exclude transparent pixels and report exact RGBA counts separately from quantised palette estimates. Pillow’s `getcolors()` returns `None` when its configured maximum is exceeded. [Pillow Image API](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.getcolors)

**Platform exports require different compositions, not merely different dimensions.**

| Destination | Requirements and production implications |
|---|---|
| iOS/iPadOS 26–27 | Icon Composer produces a layered `.icon` asset integrated into Xcode. Use a 1024×1024 canvas, separate artwork layers, and system-applied materials/masking. Appearance families are Default, Dark, Clear light/dark, and Tinted light/dark; Composer groups clear/tinted work under Mono. Current documentation includes 26/27 rendering comparison. [Composer workflow](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer), [Apple design resources](https://developer.apple.com/design/resources/) |
| Flat Apple fallback | A single 1024×1024 image in the iOS asset catalogue still generates size variants. It does not supply independently editable glass layers. Retain the catalogue workflow when preserving existing artwork on older releases is important. [Asset catalogues](https://developer.apple.com/documentation/xcode/configuring-your-app-icon), [Composer migration](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer) |
| macOS 26 onward | Current layered icons use a 1024×1024 square canvas with a system-masked rounded-square enclosure. Do not bake the final corner mask into imported layers. [Apple icon guidelines](https://developer.apple.com/design/human-interface-guidelines/app-icons) |
| watchOS | Current Composer guidance specifies **1088×1088**, circular system masking, and no appearance variants. Distinguish this from the legacy single-image asset-catalogue workflow. [Apple specifications](https://developer.apple.com/design/human-interface-guidelines/app-icons) |
| Android adaptive | Foreground/background layers are 108×108 dp; the outer 18 dp per side supports effects, leaving a nominal 72 dp viewport. Keep essential artwork within the central 66 dp safe region; do not assume every corner survives OEM masks. Provide a monochrome layer for controlled themed-icon results. [Android Developers](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive) |
| Google Play | Separate 512×512, 32-bit sRGB PNG, maximum 1024 KB. Supply a full square without baked outer rounding or shadow. [Play specification](https://developer.android.com/distribute/google-play/resources/icon-design-specifications) |
| Web installation | Supply 192/512 PNGs plus a dedicated 512 maskable PNG. `purpose:"maskable"` guarantees essential content only inside the centred circle of radius 40% of image width. An opaque background avoids platform-selected transparency fills. [Web manifest guidance](https://web.dev/learn/pwa/web-app-manifest) |
| Apple web shortcut | Export a 180×180 PNG and declare `rel="apple-touch-icon"`; this is distinct from native app-icon packaging. [Apple web-app configuration](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html) |

For 2025–2026 favicon markup, a defensible order is ICO fallback first, SVG second, followed by separate touch-icon and manifest declarations:

```html
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48 256x256">
<link rel="icon" href="/favicon.svg" type="image/svg+xml" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">
<link rel="manifest" href="/site.webmanifest">
```

There is no universal year-specific ordering mandate: HTML selects by suitability, with the last declaration breaking equally appropriate ties. [HTML icon selection](https://html.spec.whatwg.org/multipage/links.html#rel-icon)

Use a dedicated **1200×630** Open Graph composition as a practical Facebook-compatible baseline, not a universal Open Graph protocol requirement. [WordPress sharing guidance](https://wordpress.com/support/facebook-image-thumbnail/) For avatars, preview both circular and rounded-square crops. Recommended production exports are Slack **512²**, Discord **512²**, and GitHub organisation **500²**; these are delivery recommendations, not three documented mandatory sizes. Slack and Discord’s current help pages describe upload/cropping without prescribing those dimensions; GitHub’s general profile guidance recommends approximately 500², below 1 MB and 3000². [Slack](https://slack.com/help/articles/204379773-Upload-a-Slack-icon), [Discord](https://support.discord.com/hc/en-us/articles/30715364399511-Server-Profile), [GitHub profile requirements](https://docs.github.com/en/enterprise-server%403.20/account-and-profile/reference/profile-reference)

**Colour tooling should preserve colour-space intent.** OKLab conversion proceeds through linear-light RGB, matrix transforms, and cube roots; OKLCH is its polar form: `C=sqrt(a²+b²)`, `h=atan2(b,a)`. Use the published implementation or Color.js rather than improvising matrices. [Ottosson’s specification](https://bottosson.github.io/posts/oklab/), [Color.js spaces](https://colorjs.io/docs/spaces.html)

Generate tints/shades by varying lightness, retaining hue where useful, and reducing chroma to fit the target gamut. Conversion alone does not guarantee in-gamut coordinates; Color.js provides `inGamut()` and `toGamut()`. Recheck contrast after mapping. [Gamut mapping](https://colorjs.io/docs/gamut-mapping.html)

For colour-vision simulation, Machado supplies severity-dependent matrices; Brettel uses piecewise projections rather than one universal matrix. Apply the model’s required linear-RGB/LMS conversions, not a matrix directly to gamma-encoded bytes. DaltonLens implements both; simulated distinguishability remains an approximation. [DaltonLens implementation](https://github.com/DaltonLens/DaltonLens-Python)

WCAG contrast uses `(Llighter+0.05)/(Ldarker+0.05)`, with `L=0.2126R+0.7152G+0.0722B`. Linearise each normalised sRGB channel `c` as `c/12.92` when `c≤0.04045`, otherwise `((c+0.055)/1.055)^2.4`. Evaluate against the actual composited background. Logo text is exempt from WCAG’s text-contrast minimum; that exemption does not make low contrast desirable. [WCAG contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)

**Boolean geometry can remain entirely programmatic.**

- **Python skia-pathops**, imported as `pathops`, supplies union, intersection, difference, and XOR. `Path.stroke(width, cap, join, miter_limit, …)` expands strokes into geometry. [README](https://github.com/fonttools/skia-pathops), [stroke implementation](https://github.com/fonttools/skia-pathops/blob/main/src/python/pathops/_pathops.pyx)
- **Paper.js** supplies Bézier-aware `unite`, `subtract`, `intersect`, and `exclude`. [PathItem API](https://paperjs.org/reference/pathitem/)
- **Clipper/Clipper2 bindings** handle polygons and offsets; flatten curves to a documented tolerance first. Clipper2 uses integer arithmetic internally, including scaled conversion for its floating-point interface. [Clipper2](https://www.angusj.com/clipper2/Docs/Overview.htm)
- **svgpathtools** excels at parsing, intersections, bounds, and splitting; it is not a complete general-purpose filled-region boolean engine. [README](https://github.com/mathandy/svgpathtools)
- **Inkscape actions** provide `select-all;object-stroke-to-path`, followed by explicit SVG export; check available action names with `--action-list`. [Actions](https://wiki.inkscape.org/wiki/Action)

**LLM-generated paths need structural and visual validation.** Common failures include swapped arc flags, incorrect relative endpoints, omitted closure, microscopic strokes, and inconsistent contour winding. Arc flags must be `0` or `1`; an unclosed subpath can still appear filled because filling implicitly closes it, concealing a construction error. [SVG paths](https://www.w3.org/TR/SVG2/paths.html), [fill semantics](https://www.w3.org/TR/SVG2/painting.html#FillProperties)

Automate XML and path parsing, finite-number checks, positive viewport checks, expected contour closure, reference resolution, and bounds assertions. Then rasterise at 16, 32, and delivery sizes; compare topology, clearance, and approved reference images before and after optimisation. Use two independent renderers for release checks. Parsing verifies syntax; geometry checks and rendered comparisons address different failure classes. [svgpathtools](https://github.com/mathandy/svgpathtools), [resvg testing approach](https://github.com/linebender/resvg), [SVGO transformations](https://svgo.dev/docs/plugins/convertPathData/)