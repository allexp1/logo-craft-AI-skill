#!/usr/bin/env python3
"""Render SVG logos to PNG and build the inspection sheets a designer uses.

    python3 render.py logo.svg --out logo.png --size 1024 [--bg white]
    python3 render.py logo.svg --sheet sheet.png          # sizes 16..128, dark/light, mono, blur, greyscale
    python3 render.py a.svg b.svg c.svg --compare concepts.png --labels "Orbit,Lens,Monogram"
    python3 render.py logo.svg --pdf logo.pdf

Always LOOK at the PNGs you produce (open them with the Read tool). The sheet
answers the questions a logo must pass: does it survive 16 px, does it hold
in one colour, does it read reversed, does the silhouette survive a blur.
"""
from __future__ import annotations

import argparse
import copy
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (available_renderers, ensure_deps, get_viewbox, pixel_fit, read_svg, recolor,  # noqa: E402
                     render_png, svg_to_string)

ensure_deps("PIL")
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps  # noqa: E402

LIGHT = (255, 255, 255)
DARK = (17, 17, 17)
PAPER = (244, 244, 242)
INK = (30, 30, 30)
MUTED = (120, 120, 120)


def font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # old Pillow
        return ImageFont.load_default()


def tmp_svg(root) -> str:
    fd, path = tempfile.mkstemp(suffix=".svg", prefix="logo-craft-")
    os.close(fd)
    Path(path).write_text(svg_to_string(root), encoding="utf-8")
    return path


def render_to_image(svg_path: str, size: int, vb=None, bg: str | None = None, renderer=None) -> Image.Image:
    fd, png = tempfile.mkstemp(suffix=".png", prefix="logo-craft-")
    os.close(fd)
    if vb is None:
        _, root = read_svg(svg_path)
        vb = get_viewbox(root)
    w, h = pixel_fit(vb, size)
    render_png(svg_path, png, w, h, background=bg, renderer=renderer)
    img = Image.open(png).convert("RGBA")
    img.load()
    os.unlink(png)
    return img


def mono_variant(svg_path: str, color: str) -> str:
    _, root = read_svg(svg_path)
    recolor(root, color)
    return tmp_svg(root)


def paste_center(canvas: Image.Image, img: Image.Image, box, bg=None):
    x0, y0, x1, y1 = box
    if bg is not None:
        ImageDraw.Draw(canvas).rectangle(box, fill=bg)
    x = x0 + (x1 - x0 - img.width) // 2
    y = y0 + (y1 - y0 - img.height) // 2
    canvas.alpha_composite(img, (max(x0, x), max(y0, y)))


def sheet(svg_path: str, out: str, sizes: list[int], renderer=None) -> None:
    _, root = read_svg(svg_path)
    vb = get_viewbox(root)
    black_svg = mono_variant(svg_path, "#000000")
    white_svg = mono_variant(svg_path, "#FFFFFF")
    W = 1240
    pad = 24
    f_title, f_lab, f_small = font(22), font(15), font(12)
    rows = []  # (label, [(size, image, bg)])

    def row(label, svg, bg_rgb):
        imgs = []
        for s in sizes:
            imgs.append((s, render_to_image(svg, s, vb, renderer=renderer), bg_rgb))
        rows.append((label, imgs))

    row("colour on white", svg_path, LIGHT)
    row("colour on dark", svg_path, DARK)
    row("one colour, black", black_svg, LIGHT)
    row("reversed, white", white_svg, DARK)

    # layout
    max_s = max(sizes)
    cell_h = max_s + 40
    y = pad
    H = pad + 50 + len(rows) * (cell_h + 10) + 40 + 420 + pad
    canvas = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(canvas)
    d.text((pad, y), f"{Path(svg_path).name}", fill=INK, font=f_title)
    d.text((pad, y + 28), f"viewBox {' '.join(str(round(v, 2)) for v in vb)}   renderer: {(renderer or available_renderers()[0])}",
           fill=MUTED, font=f_small)
    y += 50
    for label, imgs in rows:
        d.text((pad, y + cell_h // 2 - 8), label, fill=INK, font=f_lab)
        x = 200
        for s, img, bg in imgs:
            cw = max(s, 48) + 24
            box = (x, y, x + cw, y + cell_h)
            paste_center(canvas, img, (x, y + 8, x + cw, y + 8 + max_s), bg=bg + (255,))
            d.text((x + 4, y + cell_h - 18), f"{s}px", fill=MUTED, font=f_small)
            x += cw + 8
        # 16 px zoomed ×6 so the pixel rendering can be judged
        s16 = imgs[0][1] if imgs[0][0] <= 24 else render_to_image(
            svg_path if "colour" in label else (black_svg if "black" in label else white_svg), 16, vb, renderer=renderer)
        zoom = s16.resize((s16.width * 6, s16.height * 6), Image.NEAREST)
        bgc = imgs[0][2]
        paste_center(canvas, zoom, (x, y + 8, x + 120, y + 8 + max_s), bg=bgc + (255,))
        d.text((x + 4, y + cell_h - 18), "16px x6", fill=MUTED, font=f_small)
        y += cell_h + 10

    # second block: large, greyscale, blur, silhouette
    y += 20
    big = render_to_image(svg_path, 380, vb, renderer=renderer)
    blocks = [("large", big), ("greyscale", ImageOps.grayscale(big).convert("RGBA")),
              ("blur (squint test)", big.filter(ImageFilter.GaussianBlur(radius=max(4, 380 // 45)))),
              ]
    sil = render_to_image(black_svg, 380, vb, renderer=renderer)
    blocks.append(("silhouette", sil))
    bw = (W - 2 * pad - 3 * 12) // 4
    x = pad
    for label, img in blocks:
        box = (x, y, x + bw, y + 400)
        d.rectangle(box, fill=LIGHT + (255,), outline=(220, 220, 220))
        if label == "greyscale":
            # keep alpha from the colour render
            g = img.copy()
            g.putalpha(big.getchannel("A"))
            img = g
        if img.width > bw - 20 or img.height > 380:
            img = ImageOps.contain(img, (bw - 20, 380))
        paste_center(canvas, img, (x, y, x + bw, y + 380))
        d.text((x + 8, y + 382), label, fill=MUTED, font=f_small)
        x += bw + 12
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out)
    for p in (black_svg, white_svg):
        os.unlink(p)
    print(f"wrote {out}")


def compare(svg_paths: list[str], out: str, labels: list[str] | None, renderer=None, color=False) -> None:
    """Concept checkpoint sheet: every candidate at the same height, in grey,
    with a 32 px row underneath so small-size behaviour is compared too."""
    n = len(svg_paths)
    cols = min(n, 3)
    rows_n = (n + cols - 1) // cols
    cell_w, cell_h = 380, 330
    pad = 24
    W = pad * 2 + cols * cell_w + (cols - 1) * 16
    H = pad * 2 + 40 + rows_n * (cell_h + 16)
    canvas = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(canvas)
    f_title, f_lab, f_small = font(20), font(16), font(12)
    d.text((pad, pad), "Concepts - same height, one colour. Judge form, not colour.", fill=INK, font=f_title)
    for i, p in enumerate(svg_paths):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + 16)
        y = pad + 40 + r * (cell_h + 16)
        d.rectangle((x, y, x + cell_w, y + cell_h), fill=LIGHT + (255,), outline=(220, 220, 220))
        label = labels[i] if labels and i < len(labels) else Path(p).stem
        d.text((x + 12, y + 10), f"{chr(65 + i)}. {label}", fill=INK, font=f_lab)
        src = p if color else mono_variant(p, "#1E1E1E")
        _, root = read_svg(p)
        vb = get_viewbox(root)
        big = render_to_image(src, 300, vb, renderer=renderer)
        big = ImageOps.contain(big, (cell_w - 40, 190))
        paste_center(canvas, big, (x, y + 36, x + cell_w, y + 36 + 190))
        # small row: 16, 24, 32, 48 on white and 32 on dark
        sx = x + 16
        sy = y + 240
        for s in (16, 24, 32, 48):
            im = render_to_image(src, s, vb, renderer=renderer)
            paste_center(canvas, im, (sx, sy, sx + 56, sy + 56), bg=LIGHT + (255,))
            d.text((sx + 2, sy + 58), f"{s}", fill=MUTED, font=f_small)
            sx += 64
        white_src = mono_variant(p, "#FFFFFF")
        im = render_to_image(white_src, 32, vb, renderer=renderer)
        paste_center(canvas, im, (sx, sy, sx + 56, sy + 56), bg=DARK + (255,))
        d.text((sx + 2, sy + 58), "32 rev", fill=MUTED, font=f_small)
        os.unlink(white_src)
        if not color:
            os.unlink(src)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out)
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg", nargs="+", help="SVG file(s)")
    ap.add_argument("--out", help="PNG output for a single render")
    ap.add_argument("--size", type=int, default=1024, help="long side in px for --out (default 1024)")
    ap.add_argument("--bg", help="background colour for --out (default transparent)")
    ap.add_argument("--sheet", help="write the inspection sheet PNG")
    ap.add_argument("--sizes", default="16,24,32,48,64,128", help="sizes for --sheet")
    ap.add_argument("--compare", help="write a concept comparison PNG of all inputs")
    ap.add_argument("--labels", help="comma-separated labels for --compare")
    ap.add_argument("--color", action="store_true", help="--compare in colour instead of grey")
    ap.add_argument("--pdf", help="write a PDF (needs rsvg-convert or cairosvg)")
    ap.add_argument("--renderer", help="force a renderer: " + ", ".join(available_renderers() or ["(none found)"]))
    a = ap.parse_args()

    if not available_renderers():
        sys.exit("error: no SVG renderer found. On macOS: brew install librsvg   (or pip install cairosvg)")
    if a.out:
        _, root = read_svg(a.svg[0])
        w, h = pixel_fit(get_viewbox(root), a.size)
        r = render_png(a.svg[0], a.out, w, h, background=a.bg, renderer=a.renderer)
        print(f"wrote {a.out} ({w}x{h}, {r})")
    if a.sheet:
        sheet(a.svg[0], a.sheet, [int(s) for s in a.sizes.split(",")], renderer=a.renderer)
    if a.compare:
        compare(a.svg, a.compare, a.labels.split(",") if a.labels else None, renderer=a.renderer, color=a.color)
    if a.pdf:
        if shutil.which("rsvg-convert"):
            subprocess.run(["rsvg-convert", "-f", "pdf", "-o", a.pdf, a.svg[0]], check=True)
        else:
            import cairosvg
            cairosvg.svg2pdf(url=a.svg[0], write_to=a.pdf)
        print(f"wrote {a.pdf}")
    if not (a.out or a.sheet or a.compare or a.pdf):
        ap.error("choose --out, --sheet, --compare or --pdf")


if __name__ == "__main__":
    main()
