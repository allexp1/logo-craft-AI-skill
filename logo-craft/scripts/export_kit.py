#!/usr/bin/env python3
"""Export the complete logo kit from the master SVGs.

    python3 export_kit.py --symbol symbol.svg --lockup horizontal.svg --stacked stacked.svg --wordmark wordmark.svg \
        --name kixplo --bg "#2B2F7A" --fg "#FFFFFF" --out dist/logo-kit
    python3 export_kit.py --symbol symbol.svg --name app --out dist/kit --into-web public --into-ios App/Assets.xcassets/AppIcon.appiconset --into-android app/src/main/res

Produces svg/ (colour, black, white), png/ (512-2048), web/ (favicon.svg +
.ico, apple-touch-icon, PWA icons incl. maskable, site.webmanifest, head.html,
og-image, social avatar), ios/ (AppIcon 1024 light/dark/tinted, appiconset
Contents.json, Icon Composer layers), android/ (adaptive icon VectorDrawables
foreground/background/monochrome, legacy mipmaps, Play Store 512), print/
(PDF when rsvg-convert exists) and a README with usage rules.
--bg is the icon background (brand colour); --fg recolours the symbol on that
background (usually white). Without --bg the icons use a white background.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (ensure_deps, fmt, get_viewbox, local, parse_hex, pixel_fit, q, read_svg, recolor,  # noqa: E402
                     render_png, svg_to_string, write_svg, contrast)

ensure_deps("fontTools", "PIL")
from PIL import Image, ImageDraw  # noqa: E402

from _compose import embed_group, ink_box, new_svg, norm_color, pad_canvas, palette_of, square_canvas  # noqa: E402
from _geom import flatten_document_to_paths  # noqa: E402

TMP = []


def tmp_svg(root) -> str:
    fd, p = tempfile.mkstemp(suffix=".svg", prefix="logo-craft-kit-")
    os.close(fd)
    Path(p).write_text(svg_to_string(root), encoding="utf-8")
    TMP.append(p)
    return p


def render_root(root, size, bg=None) -> Image.Image:
    p = tmp_svg(root)
    fd, png = tempfile.mkstemp(suffix=".png", prefix="logo-craft-kit-")
    os.close(fd)
    w, h = pixel_fit(get_viewbox(root), size)
    render_png(p, png, w, h, background=bg)
    im = Image.open(png).convert("RGBA")
    im.load()
    os.unlink(png)
    return im


def save_png(root, path, size, bg=None):
    im = render_root(root, size, bg)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True)
    return im


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    return m


def circle_mask(size):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    return m


def variants(root, mono_dark="#000000", mono_light="#FFFFFF"):
    black = copy.deepcopy(root)
    recolor(black, mono_dark)
    white = copy.deepcopy(root)
    recolor(white, mono_light)
    return root, black, white


# ------------------------------------------------------------ VectorDrawable
def vector_drawable(root, dp=108, content_scale=0.5, mono: str | None = None, offset_y=0.0) -> str:
    """Android VectorDrawable with the symbol centred in a dp x dp viewport.
    content_scale = fraction of the viewport the symbol's longest side takes
    (0.5 = 54 dp of 108, inside the 66 dp safe zone)."""
    paths = flatten_document_to_paths(root)
    box = ink_box(root)
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = dp * content_scale / max(bw, bh)
    tx = dp / 2 - (box[0] + box[2]) / 2 * s
    ty = dp / 2 + offset_y * dp - (box[1] + box[3]) / 2 * s
    lines = ['<?xml version="1.0" encoding="utf-8"?>',
             '<vector xmlns:android="http://schemas.android.com/apk/res/android"',
             f'    android:width="{dp}dp" android:height="{dp}dp"',
             f'    android:viewportWidth="{dp}" android:viewportHeight="{dp}">',
             f'  <group android:scaleX="{fmt(s, 5)}" android:scaleY="{fmt(s, 5)}" '
             f'android:translateX="{fmt(tx, 4)}" android:translateY="{fmt(ty, 4)}">']
    warned = False
    for p in paths:
        fill, fa = norm_color(p["fill"], mono or "#000000")
        stroke, sa = norm_color(p["stroke"], mono or "#000000")
        if fill == "url":
            fill = mono or "#808080"
            warned = True
        if stroke == "url":
            stroke = mono or "#808080"
        if mono:
            fill = mono if fill else None
            stroke = mono if stroke else None
        if p.get("opacity"):
            fa *= float(p["opacity"])
            sa *= float(p["opacity"])
        if p.get("fill_opacity"):
            fa *= float(p["fill_opacity"])
        if p.get("stroke_opacity"):
            sa *= float(p["stroke_opacity"])
        attrs = [f'android:pathData="{p["d"]}"']
        if fill:
            attrs.append(f'android:fillColor="{fill}"')
            if fa < 1:
                attrs.append(f'android:fillAlpha="{fa:.3f}"')
            if p["fill_rule"] == "evenodd":
                attrs.append('android:fillType="evenOdd"')
        if stroke:
            attrs.append(f'android:strokeColor="{stroke}"')
            attrs.append(f'android:strokeWidth="{fmt(p["stroke_width"], 4)}"')
            if sa < 1:
                attrs.append(f'android:strokeAlpha="{sa:.3f}"')
            if p.get("linecap"):
                attrs.append(f'android:strokeLineCap="{p["linecap"]}"')
            if p.get("linejoin"):
                attrs.append(f'android:strokeLineJoin="{p["linejoin"]}"')
        if fill or stroke:
            lines.append("    <path " + " ".join(attrs) + "/>")
    lines += ["  </group>", "</vector>", ""]
    if warned:
        print("[android] gradients were flattened to a flat colour in the VectorDrawable", file=sys.stderr)
    return "\n".join(lines)


def favicon_svg(symbol_root, dark_fill="#FFFFFF") -> ET.Element:
    """Square favicon master. Single-colour marks get a prefers-color-scheme
    rule so the icon flips to light on dark browser chrome."""
    root = pad_canvas(symbol_root, 0.04, square=True)
    pal = palette_of(root)
    if len(pal) == 1 and pal[0] != "url":
        for el in root.iter():
            tag = local(el.tag)
            if tag in ("path", "circle", "ellipse", "rect", "polygon", "polyline", "line"):
                el.set("class", (el.get("class", "") + " lc").strip())
        st = ET.Element(q("style"))
        st.text = f"@media (prefers-color-scheme: dark) {{ .lc {{ fill: {dark_fill}; }} }}"
        root.insert(0, st)
    return root


def write_ico(symbol_square_root, path):
    imgs = {s: render_root(symbol_square_root, s) for s in (16, 32, 48)}
    base = imgs[48]
    base.save(path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[imgs[16], imgs[32]])


def head_html(name, theme):
    return f"""<!-- favicons generated by logo-craft; put the files in your web root -->
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="{theme}">
<meta property="og:image" content="/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbol", required=True, help="square-ish mark master SVG")
    ap.add_argument("--lockup", help="horizontal lockup SVG")
    ap.add_argument("--stacked", help="stacked lockup SVG")
    ap.add_argument("--wordmark", help="wordmark SVG")
    ap.add_argument("--name", required=True, help="brand name (file prefix and manifest name)")
    ap.add_argument("--short-name", help="manifest short_name (default: name)")
    ap.add_argument("--out", default="logo-kit")
    ap.add_argument("--bg", help="icon background colour (hex); default white")
    ap.add_argument("--fg", help="recolour the symbol on icon backgrounds (e.g. #FFFFFF)")
    ap.add_argument("--mono", default="#000000", help="one-colour dark variant colour (default black)")
    ap.add_argument("--dark-fg", help="symbol colour on the dark app-icon tile (default: --fg, else the mark's own colours)")
    ap.add_argument("--icon-scale", type=float, default=0.62, help="symbol size on app icons (fraction of canvas)")
    ap.add_argument("--favicon-symbol", help="optional simplified symbol for 16-32 px")
    ap.add_argument("--into-web", help="copy web favicons into this folder (e.g. public/)")
    ap.add_argument("--into-ios", help="copy AppIcon-1024 + Contents.json into this .appiconset folder")
    ap.add_argument("--into-android", help="copy adaptive icon resources into this res/ folder")
    ap.add_argument("--force", action="store_true", help="overwrite files in --into-* targets")
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    name = a.name
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in name.lower()).strip("-") or "logo"
    bg = a.bg or "#FFFFFF"
    theme = a.bg or "#FFFFFF"
    fg = a.fg
    _, symbol = read_svg(a.symbol)
    fav_src = symbol
    if a.favicon_symbol:
        _, fav_src = read_svg(a.favicon_symbol)
    written = []

    def W(path, content):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, (bytes, bytearray)):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        written.append(path)

    # ---- svg + png variants
    sets = {"symbol": symbol}
    for key, p in (("lockup-horizontal", a.lockup), ("lockup-stacked", a.stacked), ("wordmark", a.wordmark)):
        if p:
            sets[key] = read_svg(p)[1]
    for key, root in sets.items():
        col, blk, wht = variants(root, a.mono)
        for vname, vroot in (("color", col), ("black", blk), ("white", wht)):
            write_svg(vroot, out / "svg" / f"{slug}-{key}-{vname}.svg")
            written.append(out / "svg" / f"{slug}-{key}-{vname}.svg")
            for size in ((512, 1024, 2048) if key == "symbol" else (1024, 2048)):
                save_png(vroot, out / "png" / f"{slug}-{key}-{vname}-{size}.png", size)
                written.append(out / "png" / f"{slug}-{key}-{vname}-{size}.png")

    # ---- app-icon composition (symbol on background)
    icon = square_canvas(symbol, 1024, a.icon_scale, bg=bg, fg=fg, title=name)
    write_svg(icon, out / "svg" / f"{slug}-icon-square.svg")
    written.append(out / "svg" / f"{slug}-icon-square.svg")

    # ---- web
    web = out / "web"
    fav = favicon_svg(fav_src)
    write_svg(fav, web / "favicon.svg")
    written.append(web / "favicon.svg")
    fav_png_root = pad_canvas(fav_src, 0.04, square=True)
    (web).mkdir(parents=True, exist_ok=True)
    write_ico(fav_png_root, web / "favicon.ico")
    written.append(web / "favicon.ico")
    for s in (16, 32):
        save_png(fav_png_root, web / f"favicon-{s}x{s}.png", s)
        written.append(web / f"favicon-{s}x{s}.png")
    touch = square_canvas(symbol, 180, 0.72, bg=bg, fg=fg)
    save_png(touch, web / "apple-touch-icon.png", 180)
    written.append(web / "apple-touch-icon.png")
    for s in (192, 512):
        save_png(square_canvas(symbol, s, 0.72, bg=bg, fg=fg), web / f"icon-{s}.png", s)
        written.append(web / f"icon-{s}.png")
    save_png(square_canvas(symbol, 512, 0.56, bg=bg, fg=fg), web / "icon-maskable-512.png", 512)
    written.append(web / "icon-maskable-512.png")
    manifest = {
        "name": name, "short_name": a.short_name or name, "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
        "theme_color": theme, "background_color": bg, "display": "standalone", "start_url": "/"}
    W(web / "site.webmanifest", json.dumps(manifest, indent=2) + "\n")
    W(web / "head.html", head_html(name, theme))
    # og image 1200x630: lockup (or symbol) centred
    og = new_svg(1200, 630, title=name)
    r = ET.SubElement(og, q("rect"))
    r.set("width", "1200")
    r.set("height", "630")
    r.set("fill", bg)
    hero_src = next((sets[k] for k in ("lockup-horizontal", "wordmark") if k in sets), symbol)
    hero = copy.deepcopy(hero_src)
    if fg and a.bg:
        recolor(hero, fg)
    from _compose import fit_transform
    hb = ink_box(hero)
    tf, _ = fit_transform(hb, 1200 * 0.6, 630 * 0.5, 600, 315)
    og.append(embed_group(hero, tf, "h-"))
    save_png(og, web / "og-image.png", 1200)
    written.append(web / "og-image.png")
    avatar = square_canvas(symbol, 1024, 0.58, bg=bg, fg=fg)
    av = save_png(avatar, web / "social-avatar-1024.png", 1024)
    written.append(web / "social-avatar-1024.png")
    prev = av.copy()
    prev.putalpha(circle_mask(1024))
    prev.save(web / "social-avatar-circle-preview.png")
    written.append(web / "social-avatar-circle-preview.png")

    # ---- iOS
    ios = out / "ios"
    light = square_canvas(symbol, 1024, a.icon_scale, bg=bg, fg=fg, title=name)
    save_png(light, ios / "AppIcon-1024.png", 1024, bg="#FFFFFF" if not a.bg else None)
    written.append(ios / "AppIcon-1024.png")
    dark_bg = "#1C1C1E"
    dark_fg = a.dark_fg or fg or a.bg or "#FFFFFF"
    use_fg = bool(a.dark_fg or fg or a.bg)
    if not use_fg:
        # the mark keeps its own colours on the dark tile: warn when its darkest colour would sink into it
        from _common import contrast, parse_hex
        weakest = min((contrast(parse_hex(c), parse_hex(dark_bg)) for c in palette_of(symbol) if c and c != "url"), default=21.0)
        if weakest < 3.0:
            print(f"warning: on the dark app-icon tile the mark's own colours reach only {weakest:.1f}:1; "
                  f"pass --dark-fg \"#FFFFFF\" (or a light brand colour) for AppIcon-dark, or keep the light tile.", file=sys.stderr)
    dark = square_canvas(symbol, 1024, a.icon_scale, bg=dark_bg, fg=dark_fg if use_fg else None, title=name)
    save_png(dark, ios / "AppIcon-dark-1024.png", 1024)
    written.append(ios / "AppIcon-dark-1024.png")
    tinted = square_canvas(symbol, 1024, a.icon_scale, bg="#000000", fg="#FFFFFF", title=name)
    save_png(tinted, ios / "AppIcon-tinted-1024.png", 1024)
    written.append(ios / "AppIcon-tinted-1024.png")
    contents = {"images": [
        {"filename": "AppIcon-1024.png", "idiom": "universal", "platform": "ios", "size": "1024x1024"},
        {"appearances": [{"appearance": "luminosity", "value": "dark"}], "filename": "AppIcon-dark-1024.png",
         "idiom": "universal", "platform": "ios", "size": "1024x1024"},
        {"appearances": [{"appearance": "luminosity", "value": "tinted"}], "filename": "AppIcon-tinted-1024.png",
         "idiom": "universal", "platform": "ios", "size": "1024x1024"}],
        "info": {"author": "logo-craft", "version": 1}}
    W(ios / "AppIcon.appiconset" / "Contents.json", json.dumps(contents, indent=2) + "\n")
    for f in ("AppIcon-1024.png", "AppIcon-dark-1024.png", "AppIcon-tinted-1024.png"):
        shutil.copy(ios / f, ios / "AppIcon.appiconset" / f)
    comp = ios / "icon-composer"
    bg_layer = new_svg(1024, 1024)
    rr = ET.SubElement(bg_layer, q("rect"))
    rr.set("width", "1024")
    rr.set("height", "1024")
    rr.set("fill", bg)
    write_svg(bg_layer, comp / "layer-1-background.svg")
    sym_layer = square_canvas(symbol, 1024, a.icon_scale, bg=None, fg=fg)
    write_svg(sym_layer, comp / "layer-2-symbol.svg")
    save_png(sym_layer, comp / "layer-2-symbol.png", 1024)
    W(comp / "README.md", f"""# Icon Composer layers ({name})

Xcode 26+: File > New > Icon Composer document (or open an existing .icon).
1. Drag `layer-1-background.svg` in first, then `layer-2-symbol.svg` (SVG keeps it vector; the PNG is a fallback).
2. Keep the symbol inside the centre ~62% of the canvas; the system applies the rounded mask and Liquid Glass.
3. Check the four appearances: Default, Dark, Clear (light/dark) and Tinted. For Dark, the symbol layer may need
   a lighter fill; for Tinted and Clear the symbol should read as a single shape.
4. Export the .icon into the app target; keep `AppIcon.appiconset` for older OS versions.
watchOS uses a 1088 x 1088 circular canvas; macOS a 1024 rounded square (do not bake the corners).
""")
    written += [comp / "layer-1-background.svg", comp / "layer-2-symbol.svg", comp / "layer-2-symbol.png", comp / "README.md"]

    # ---- Android
    an = out / "android"
    W(an / "drawable" / "ic_launcher_foreground.xml", vector_drawable(symbol, 108, 0.5, mono=fg if fg else None))
    W(an / "drawable" / "ic_launcher_monochrome.xml", vector_drawable(symbol, 108, 0.5, mono="#FFFFFF"))
    W(an / "values" / "ic_launcher_background.xml",
      f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">{bg}</color>\n</resources>\n')
    adaptive = ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
                '    <background android:drawable="@color/ic_launcher_background"/>\n'
                '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n'
                '    <monochrome android:drawable="@drawable/ic_launcher_monochrome"/>\n'
                '</adaptive-icon>\n')
    W(an / "mipmap-anydpi-v26" / "ic_launcher.xml", adaptive)
    W(an / "mipmap-anydpi-v26" / "ic_launcher_round.xml", adaptive)
    legacy = square_canvas(symbol, 1024, 0.6, bg=bg, fg=fg)
    for dpi, px in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
        im = render_root(legacy, px)
        sq = im.copy()
        sq.putalpha(rounded_mask(px, int(px * 0.18)))
        (an / f"mipmap-{dpi}").mkdir(parents=True, exist_ok=True)
        sq.save(an / f"mipmap-{dpi}" / "ic_launcher.png")
        rd = im.copy()
        rd.putalpha(circle_mask(px))
        rd.save(an / f"mipmap-{dpi}" / "ic_launcher_round.png")
        written += [an / f"mipmap-{dpi}" / "ic_launcher.png", an / f"mipmap-{dpi}" / "ic_launcher_round.png"]
    save_png(square_canvas(symbol, 512, 0.6, bg=bg, fg=fg), an / "play-store-512.png", 512)
    written.append(an / "play-store-512.png")
    # adaptive preview: what the launcher shows (circle crop of 72dp of 108)
    fg_full = square_canvas(symbol, 432, 0.5, bg=bg, fg=fg)
    im = render_root(fg_full, 432)
    crop = im.crop((72, 72, 360, 360))
    crop.putalpha(circle_mask(288))
    crop.save(an / "adaptive-preview-circle.png")
    written.append(an / "adaptive-preview-circle.png")

    # ---- print
    if not a.no_pdf and shutil.which("rsvg-convert"):
        pr = out / "print"
        pr.mkdir(parents=True, exist_ok=True)
        for key in sets:
            for vname in ("color", "black"):
                src = out / "svg" / f"{slug}-{key}-{vname}.svg"
                dst = pr / f"{slug}-{key}-{vname}.pdf"
                subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(dst), str(src)], check=False)
                if dst.exists():
                    written.append(dst)

    # ---- README
    pal = palette_of(symbol)
    readme = f"""# {name} logo kit

Generated by logo-craft. Masters are the files in `svg/` (colour, black, white). Everything else is derived;
regenerate rather than hand-edit.

## Files
- `svg/` masters: symbol, lockups and wordmark in colour, black and white. `{slug}-icon-square.svg` is the app-icon composition.
- `png/` transparent renders at 512/1024/2048 px.
- `web/` `favicon.svg` (flips to light in dark mode when single-colour), `favicon.ico` (16/32/48), `apple-touch-icon.png` (180),
  `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` (safe zone respected), `site.webmanifest`, `head.html` (paste into <head>),
  `og-image.png` (1200x630), `social-avatar-1024.png` (+ circle preview).
- `ios/` `AppIcon.appiconset/` (1024 light, dark, tinted + Contents.json: drop into Assets.xcassets) and `icon-composer/` layers for Xcode 26+.
- `android/` adaptive icon: `drawable/ic_launcher_foreground.xml`, `drawable/ic_launcher_monochrome.xml`, `values/ic_launcher_background.xml`,
  `mipmap-anydpi-v26/ic_launcher*.xml`, legacy `mipmap-*/ic_launcher*.png`, `play-store-512.png` (upload as-is, Play rounds the corners).
- `print/` PDF vectors (if rsvg-convert was available).

## Rules
- Clear space: keep the margin baked into the lockup files (half a cap height). Never crowd the logo.
- Minimum sizes: symbol 16 px (favicon) / 24 px in UI; horizontal lockup about 120 px wide; print 20 mm wide.
- Colours: symbol palette {pal}; icon background {bg}{' with ' + fg + ' symbol' if fg else ''}. Use the black or white version on photos and
  busy backgrounds. Never recolour, stretch, rotate, outline, add shadows or gradients.
- One-colour contexts (embroidery, engraving, fax, stamps): use `svg/{slug}-symbol-black.svg`.
"""
    W(out / "README.md", readme)

    # ---- placement into projects
    def place(src: Path, dst: Path):
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not a.force:
            print(f"  skip (exists, use --force): {dst}")
            return
        shutil.copy(src, dst)
        print(f"  placed {dst}")

    if a.into_web:
        print("web files:")
        for f in ("favicon.svg", "favicon.ico", "apple-touch-icon.png", "icon-192.png", "icon-512.png",
                  "icon-maskable-512.png", "site.webmanifest", "og-image.png"):
            place(web / f, Path(a.into_web) / f)
        print(f"  add the tags from {web / 'head.html'} to your <head>")
    if a.into_ios:
        print("iOS app icon:")
        for f in ("AppIcon-1024.png", "AppIcon-dark-1024.png", "AppIcon-tinted-1024.png", "Contents.json"):
            place(ios / "AppIcon.appiconset" / f, Path(a.into_ios) / f)
    if a.into_android:
        print("Android icon resources:")
        res = Path(a.into_android)
        for rel in ("drawable/ic_launcher_foreground.xml", "drawable/ic_launcher_monochrome.xml",
                    "values/ic_launcher_background.xml", "mipmap-anydpi-v26/ic_launcher.xml",
                    "mipmap-anydpi-v26/ic_launcher_round.xml"):
            place(an / rel, res / rel)
        for dpi in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"):
            for f in ("ic_launcher.png", "ic_launcher_round.png"):
                place(an / f"mipmap-{dpi}" / f, res / f"mipmap-{dpi}" / f)

    for p in TMP:
        try:
            os.unlink(p)
        except OSError:
            pass
    print(f"wrote {len(written)} files to {out}")


if __name__ == "__main__":
    main()
