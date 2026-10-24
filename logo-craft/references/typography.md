# Typography for wordmarks and lockups

A wordmark is the name made into a picture of itself. The type carries voice, the spacing carries craft, and the licence decides whether you may use it at all. `scripts/text_to_path.py` sets real fonts (Google Fonts, system fonts or a file) with HarfBuzz shaping, so you never draw letters by hand unless you mean to.

Contents: 1 classification as voice · 2 choosing a face for *this* name · 3 making it ownable · 4 spacing · 5 case · 6 pairing · 7 several scripts, RTL · 8 licensing · 9 commands and workflow

## 1. Classification as voice (hypotheses, not guarantees)

| Class | Typical reading | Typical use | Caution |
|---|---|---|---|
| Geometric sans (Futura, Montserrat, Space Grotesk, Outfit) | modern, rational, tech | SaaS, developer tools, consumer apps | The default of the 2010s "blanding"; needs a modified detail to be ownable |
| Grotesque / neo-grotesque (Inter, Helvetica, Work Sans, Public Sans) | neutral, systematic, confident | infrastructure, finance, platforms | Neutrality can read as absence of character |
| Humanist sans (Source Sans, Nunito Sans, Open Sans, Heebo) | warm, approachable, legible | education, health, public services, Hebrew UI | Can look like a UI font rather than a brand |
| Old-style / transitional serif (EB Garamond, Libre Baskerville, Crimson) | literary, established, trustworthy | law, publishing, wine, heritage | Fine serifs die at small sizes; the icon needs a symbol |
| Modern / high-contrast serif (Playfair, Bodoni Moda) | elegant, fashion, luxury | beauty, fashion, hospitality | Hairlines vanish when reversed or small |
| Slab serif (Roboto Slab, Zilla Slab, Arvo) | solid, mechanical, honest | tools, logistics, coffee, kids (rounded slabs) | Heavy at small sizes in lockups |
| Monospace (JetBrains Mono, IBM Plex Mono, Space Mono) | code, systems, precision | developer tools, security | Cliché for dev tools when untouched |
| Rounded sans (Fredoka, Nunito, Quicksand, Varela Round) | friendly, soft, young | kids, food, wellness | Loses authority; keep weight up |
| Display / condensed (Bebas Neue, Anton, Oswald) | loud, sporty, editorial | sports, events, media | Not for small lockups; pair with a calm text face |
| Script and calligraphic (see `calligraphy-lettering.md`) | personal, crafted, heritage | food, drink, fashion, signatures | Legibility and small sizes; never for the compact icon |

Treat the reading as a hypothesis to test against the name, the competitor shelf and the audience. Fonts In Use shows how each face behaves in the wild.

## 2. Choosing a face for this name

Set the actual name, not "Hamburgefonstiv":

1. `text_to_path.py --list-fonts <voice>` for the curated list in `assets/fonts.json` (grouped by voice, with licence and script coverage), then set the name in three to five candidates at the same cap height and compare on one sheet.
2. Look at the **troublesome letters**: double letters (ll, oo, ss), ambiguous pairs (Il1, rn/m), the first letter (your monogram), and letters with distinctive forms in that face (a single-storey a, a tailed l, a spurless G, the Hebrew ל and ק that break the line).
3. Check **x-height and counters** at the smallest lockup you will ship: large counters and open apertures survive; closed, small ones do not.
4. Check **width and rhythm**: a name with many round letters wants a face whose round letters are generous; a name full of straight letters (Hill, Mint) wants a face with some warmth in the terminals or it becomes a barcode.
5. Decide **weight** by the symbol: a heavy symbol with a light wordmark looks like two brands.

## 3. Making it ownable

A wordmark set in an untouched font is a typesetting, not a logo. Modify with intent, and stop while it is still readable (Doyald Young: legibility before uniqueness):

- Change one or two **terminals** to echo the symbol (a cut angle, a radius).
- Build a **ligature or a shared stroke** between two letters; keep the gap that identifies each letter.
- **Unify widths** or heights (make the o as wide as the n, align the crossbar of the e with the t).
- Replace one letter with a **drawn form** related to the symbol (the o as the lens; the i-dot as the brand's dot).
- Adjust **proportions** (a slightly condensed or extended setting) rather than distorting (never scale non-uniformly more than about 3%).
- Record every change: "ownable" visually does not mean legally exclusive, and the next designer needs to know what was deliberate.

Workflow: set with `text_to_path.py --merge` off (one `<path id="gN" data-char="x">` per glyph), then edit the glyph paths you want to change; keep the data-baseline/data-cap-height attributes so `lockup.py` can still align.

## 4. Spacing

- **Tracking** is the overall letter spacing; **kerning** corrects individual pairs. A wordmark is usually tracked tighter than text (lowercase: 0 to −20 units of 1/1000 em; capitals: +20 to +80) but letters must not touch unless the touching is designed.
- **Space optically**: equalise the apparent area between letters, not the metric distance. Round-next-to-straight (o n) looks looser than straight-next-to-straight (n n); diagonal-next-to-round (v o) looks looser still. Fix the pairs after the tracking.
- **Word space** in a two-word mark is about the width of a lowercase i, often less in a wordmark; stacked lockups avoid the question.
- **Hische's checks**: squint for dark spots (too tight) and holes (too loose); flip the word upside down to see spacing as shapes; check that swashes do not create new "letters".
- Reversed wordmarks look tighter and bolder: loosen by 5 to 10 units and consider one weight lighter.

## 5. Case

- **All caps**: authority, stability, institutions; needs generous tracking; long names become a bar.
- **Lowercase**: friendliness, modernity, approachability (facebook, amazon); holds together with tight tracking; a strong x-height treatment matters.
- **Title case**: the default for invented names; the capital is the monogram candidate.
- **Mixed or small caps**: editorial, heritage.
- Hebrew and Arabic have no case; the equivalent decisions are weight, width and whether to use a display cut.

## 6. Pairing

One family for the mark. A second family only for a job (a UI text face, a tagline, a numeral style), and then with contrast of classification (a geometric sans wordmark with a humanist text face; a serif mark with a grotesque UI face), never two similar sans. Record the pairing in the guide with weights and sizes.

## 7. Several scripts and right-to-left

- **Match weight and apparent height, not form.** A Hebrew or Arabic wordmark paired with a Latin one should look equally dark and equally tall; the Hebrew letter body is roughly the Latin x-height to cap height range, so set the Hebrew slightly smaller than the Latin cap height and judge by eye.
- **Hebrew**: a square script with strong horizontals (the opposite stress of Latin); faces designed with Latin companions (Heebo with Poppins/Rubik, Assistant with Source Sans, Frank Ruhl Libre with a serif, Secular One for display, Suez One for heavy display). Final forms (ך ם ן ף ץ) and the descending ק and ascending ל shape the silhouette.
- **Arabic**: connected letters, contextual forms, dots that carry meaning; Cairo, Tajawal, Almarai, Readex Pro for sans; Amiri, Scheherazade for naskh. Never fake Arabic with disconnected letters.
- **CJK**: Noto Sans/Serif CJK are the safe baseline; a logo usually uses the Latin wordmark plus a separately designed CJK name.
- **RTL lockups** place the symbol on the right; `lockup.py` does this automatically when the wordmark carries `data-direction="rtl"`. Check the tagline and any arrow-like elements for reversed meaning.
- **Bilingual lockups**: stack the two names with a shared symbol, or place them side by side with the symbol centred; decide the primary language per market and ship both.

## 8. Licensing

| Source | What you may do | Record |
|---|---|---|
| **SIL Open Font License (most Google Fonts)** | Use in logos and artwork, embed outlines, modify letters in your artwork, register a trademark on the result. The Reserved Font Name clause restricts the *name* of a modified **font software** you redistribute, not your logo. | Font name, version, "OFL 1.1", source URL |
| **Google Fonts** | Logo use permitted; check the particular family's licence (most OFL, a few Apache 2.0 or Ubuntu Font Licence). `text_to_path.py` fetches only families listed in the public catalogue (github.com/google/fonts) and reports the licence directory; Google's CSS API also serves unlisted families such as Helvetica, which carry no open licence, so the script refuses them and falls back to an installed font. | As above |
| **Adobe Fonts** | Logos, outline modification and trademark registration are permitted under the subscription terms; modifying the font software itself is not. | Family, "Adobe Fonts subscription of <account>" |
| **Commercial foundries** | Read the EULA: desktop licences usually cover logos; some require a separate logo licence; embedding, app and web use are separate. | Foundry, family, licence type and number |
| **System fonts (SF, Helvetica Neue on macOS, Segoe)** | Apple's SF fonts are licensed for Apple-platform UI only, **not** for logos. Other bundled fonts have OS-specific terms. | Avoid for logos; pick an equivalent with a clear licence |

`text_to_path.py --font-info "<family>"` prints the licence text from the font's name table. Deliver wordmarks as outlines (which the script does) so the logo does not depend on the font being installed, and keep the font file and licence in the brand folder.

## 9. Commands and workflow

```bash
python3 scripts/text_to_path.py --list-fonts geometric          # curated families for a voice
python3 scripts/text_to_path.py --font-info "Space Grotesk"       # metrics + licence
python3 scripts/text_to_path.py --text "Ledgerly" --font "Manrope" --weight 700 --tracking -10 --out wm-a.svg
python3 scripts/text_to_path.py --text "Ledgerly" --font "Fraunces" --weight 600 --out wm-b.svg
python3 scripts/text_to_path.py --text "לומדים" --font Heebo --weight 800 --out wm-he.svg      # RTL shaped
python3 scripts/text_to_path.py --text "KIDS LOVE|SCIENCE" --font Fredoka --weight 600 --align center --out stacked.svg
python3 scripts/render.py wm-a.svg wm-b.svg wm-he.svg --compare type.png --labels "Manrope,Fraunces,Heebo"
```

The output SVG carries `data-font`, `data-weight`, `data-baseline`, `data-cap-height`, `data-x-height`, `data-tracking`, `data-direction` and one `<path>` per glyph in `<g id="wordmark">`. Edit glyphs in place for ownable details, then feed the file to `lockup.py`.
