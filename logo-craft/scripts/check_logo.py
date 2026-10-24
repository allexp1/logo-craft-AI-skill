#!/usr/bin/env python3
"""Audit a logo SVG the way a senior designer and a production artist would.

    python3 check_logo.py logo.svg [--kind symbol|wordmark|lockup] [--expect-parts N] [--json]

Structural checks (viewBox, live text, rasters, filters, gradients, external
references, duplicate ids, unclosed filled contours, point count), colour
checks (palette size, contrast on white and black), geometric checks (margins,
centring, optical centre, near-miss angles) and raster checks at 16/32 px
(parts that merge or break, thinnest stroke, smallest counter). Prints a
report with a score and the fixes to make next. Exit code 1 when there are
errors.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (contrast, ensure_deps, get_viewbox, iter_paint, local, parse_hex, read_svg,  # noqa: E402
                     recolor, render_png, svg_to_string, pixel_fit)

ensure_deps("fontTools", "PIL")
from PIL import Image, ImageFilter  # noqa: E402

from _compose import norm_color  # noqa: E402
from _geom import ink_bounds, record_d, segment_angles, shape_polylines, shape_to_d  # noqa: E402

RASTER = 256


class Report:
    def __init__(self):
        self.issues = []
        self.facts = {}

    def add(self, sev, code, msg, fix=None):
        self.issues.append({"severity": sev, "code": code, "message": msg, "fix": fix})

    def score(self):
        s = 100
        for i in self.issues:
            s -= {"error": 15, "warn": 5, "info": 0}[i["severity"]]
        return max(0, s)


# ------------------------------------------------------------- raster utils
def mask_from(img: Image.Image, thresh=128):
    a = img.getchannel("A").point(lambda v: 255 if v >= thresh else 0)
    return a


def components(mask: Image.Image) -> tuple[int, int]:
    """(foreground components, holes) using 4-connectivity on a binary 'L' image."""
    w, h = mask.size
    data = mask.tobytes()
    fg = count_regions(data, w, h, want=255)
    inv = bytes(255 - b for b in data)
    # background regions: those touching the border are "outside"; the rest are holes
    bg_total, bg_border = count_regions(inv, w, h, want=255, border=True)
    return fg, bg_total - bg_border


def count_regions(data: bytes, w: int, h: int, want: int, border: bool = False):
    seen = bytearray(w * h)
    n = 0
    n_border = 0
    for start in range(w * h):
        if data[start] != want or seen[start]:
            continue
        n += 1
        touches = False
        stack = [start]
        seen[start] = 1
        while stack:
            p = stack.pop()
            y, x = divmod(p, w)
            if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                touches = True
            for nb in (p - 1 if x > 0 else -1, p + 1 if x < w - 1 else -1, p - w if y > 0 else -1, p + w if y < h - 1 else -1):
                if nb >= 0 and not seen[nb] and data[nb] == want:
                    seen[nb] = 1
                    stack.append(nb)
        if touches:
            n_border += 1
    return (n, n_border) if border else n


def thinnest(mask: Image.Image, max_steps=30):
    """Erode until the component count changes; returns feature width in px."""
    fg0, _ = components(mask)
    if fg0 == 0:
        return None
    m = mask
    for k in range(1, max_steps + 1):
        m = m.filter(ImageFilter.MinFilter(3))
        fg, _ = components(m)
        if fg != fg0:
            return 2 * k
    return 2 * max_steps + 1


def smallest_gap(mask: Image.Image, max_steps=30):
    """Dilate until parts merge or a counter fills; returns gap in px."""
    fg0, holes0 = components(mask)
    if fg0 == 0:
        return None
    m = mask
    for k in range(1, max_steps + 1):
        m = m.filter(ImageFilter.MaxFilter(3))
        fg, holes = components(m)
        if fg < fg0 or holes < holes0:
            return 2 * k
    return 2 * max_steps + 1


def centroid(mask: Image.Image):
    w, h = mask.size
    data = mask.tobytes()
    sx = sy = n = 0
    for i, v in enumerate(data):
        if v:
            y, x = divmod(i, w)
            sx += x
            sy += y
            n += 1
    if not n:
        return None
    return (sx / n + 0.5, sy / n + 0.5)


def render_mask(svg_path, size, vb):
    fd, png = tempfile.mkstemp(suffix=".png", prefix="logo-craft-chk-")
    os.close(fd)
    w, h = pixel_fit(vb, size)
    render_png(svg_path, png, w, h)
    img = Image.open(png).convert("RGBA")
    img.load()
    os.unlink(png)
    return mask_from(img), (w, h)


# ----------------------------------------------------------------- checks
def check(path: str, kind: str, expect_parts: int | None) -> Report:
    r = Report()
    tree, root = read_svg(path)
    tags = Counter(local(el.tag) for el in root.iter())
    r.facts["elements"] = dict(tags)

    # viewBox
    if not root.get("viewBox"):
        r.add("error", "no-viewbox", "No viewBox on <svg>; the logo cannot scale predictably.",
              "Add viewBox=\"0 0 W H\" matching the drawing and drop fixed width/height.")
    vb = get_viewbox(root)
    if vb[2] <= 0 or vb[3] <= 0:
        r.add("error", "bad-viewbox", f"viewBox has non-positive size {vb}.")
        return r
    r.facts["viewBox"] = [round(v, 3) for v in vb]
    if vb[0] < 0 or vb[1] < 0:
        r.add("info", "negative-origin", "viewBox origin is negative; some tools (and Android VectorDrawable) prefer 0 0.")

    # construction hygiene: a master is paths only, with a real title
    prims = {t: n for t, n in tags.items() if t in ("rect", "circle", "ellipse", "polygon", "polyline", "line")}
    transformed = sum(1 for el in root.iter() if el.get("transform") and local(el.tag) != "svg")
    if prims or transformed:
        bits = [f"{n} <{t}>" for t, n in prims.items()] + ([f"{transformed} transform attribute(s)"] if transformed else [])
        r.add("info", "not-paths-only", "Master contains " + ", ".join(bits) + ": renders fine, but some icon pipelines "
              "(VectorDrawable converters, print RIPs, font tools) mishandle primitives and transforms.",
              "Convert to plain <path> elements with absolute coordinates before delivery (references/svg-craft.md).")
    title_el = next((el for el in root.iter() if local(el.tag) == "title"), None)
    title_txt = (title_el.text or "").strip() if title_el is not None else ""
    if not title_txt or any(w in title_txt.lower() for w in ("test", "untitled", "placeholder", "logo mark", "sample")):
        r.add("info", "title", f"<title> is {title_txt!r}: screen readers and asset managers read it.",
              "Set <title> to the brand name (and role=\"img\" aria-label on <svg>).")

    # forbidden / fragile content
    if tags.get("text"):
        r.add("error", "live-text", f"{tags['text']} <text> element(s): rendering depends on installed fonts.",
              "Set the words with scripts/text_to_path.py and replace the <text> with its outlines.")
    if tags.get("image"):
        r.add("error", "raster", "Embedded <image>: a logo must be pure vector.")
    for t in ("filter", "feGaussianBlur", "feDropShadow"):
        if tags.get(t):
            r.add("warn", "filter", f"<{t}> present: shadows/blur do not survive print, ICO or VectorDrawable.",
                  "Remove effects from the master; keep them for a marketing render only.")
            break
    if tags.get("linearGradient") or tags.get("radialGradient"):
        r.add("warn", "gradient", "Gradient fills: fine for a colour master, but you must also deliver a flat one-colour version "
                                  "(and gradients get flattened on Android).",
              "Keep gradients subtle (two tints of one hue) and ship black/white versions.")
    if tags.get("use"):
        r.add("warn", "use", "<use> references: expand them before export; some converters drop them.")
    if tags.get("foreignObject") or tags.get("script"):
        r.add("error", "foreign", "<foreignObject>/<script> inside a logo.")
    if tags.get("mask") or tags.get("clipPath"):
        r.add("info", "mask-clip", "mask/clipPath used: ok for web; convert to real geometry (boolean ops) for the master.")
    style_text = " ".join((el.text or "") for el in root.iter() if local(el.tag) == "style")
    if "@import" in style_text or "url(http" in style_text or "font-family" in style_text:
        r.add("error", "external-style", "<style> imports or font rules: external dependencies inside the logo.")
    for el in root.iter():
        for a in ("href", "{http://www.w3.org/1999/xlink}href"):
            v = el.get(a)
            if v and v.startswith(("http:", "https:", "data:")):
                r.add("error" if v.startswith("data:image") else "warn", "external-ref", f"External reference: {v[:60]}")
    ids = Counter(el.get("id") for el in root.iter() if el.get("id"))
    dup = [i for i, c in ids.items() if c > 1]
    if dup:
        r.add("warn", "dup-id", f"Duplicate ids: {dup[:5]} (breaks inline use of several logos on one page).")

    # path syntax + closure
    unclosed_filled = 0
    parse_errors = 0
    for el in root.iter():
        tag = local(el.tag)
        if tag not in ("path",):
            continue
        d = el.get("d") or ""
        try:
            rec = record_d(d)
        except Exception:
            parse_errors += 1
            continue
        fill = (el.get("fill") or "").strip()
        ops = [op for op, _ in rec.value]
        subpaths = ops.count("moveTo")
        closes = ops.count("closePath")
        if fill != "none" and subpaths > closes:
            unclosed_filled += subpaths - closes
    if parse_errors:
        r.add("error", "path-syntax", f"{parse_errors} path(s) failed to parse (bad arc flags, missing numbers...).")
    if unclosed_filled:
        r.add("warn", "unclosed", f"{unclosed_filled} filled subpath(s) without Z: the fill closes them implicitly, which hides "
                                  "construction errors and breaks stroke-to-outline later.", "End every filled contour with Z.")

    shapes = shape_polylines(root)
    npts = sum(len(s["points"]) for s in shapes)
    r.facts["points_flattened"] = npts
    d_len = sum(len(el.get("d") or "") for el in root.iter() if local(el.tag) == "path")
    r.facts["path_data_chars"] = d_len
    if d_len > 20000:
        r.add("warn", "complexity", f"Path data is {d_len} characters: too detailed for a logo (favicon, embroidery, "
                                    "VectorDrawable limits).", "Simplify: fewer anchors, no textures, no tiny details.")

    # colours
    pal = []
    for el, attr, v in iter_paint(root):
        c, a = norm_color(v)
        if c and c != "url" and c not in pal:
            pal.append(c)
    r.facts["palette"] = pal
    if len(pal) > 3:
        r.add("warn", "too-many-colours", f"{len(pal)} flat colours {pal}: more than three is hard to reproduce "
                                          "(embroidery, print, single-colour contexts).", "Reduce to 1-3 colours.")
    for c in pal:
        rgb = parse_hex(c)
        cw, cb = contrast(rgb, (255, 255, 255)), contrast(rgb, (0, 0, 0))
        if cw < 3 and cb < 3:
            r.add("warn", "low-contrast", f"{c} is below 3:1 on both white ({cw:.1f}) and black ({cb:.1f}).",
                  "Darken or lighten the colour, or add a defined dark/light background.")
        elif cw < 3:
            r.add("info", "weak-on-white", f"{c} is {cw:.1f}:1 on white (non-text minimum is 3:1): fine as an accent, "
                                           "not as the only colour of a mark on white.")
    if tags.get("linearGradient") or tags.get("radialGradient"):
        pass

    # geometry: margins, centring
    box = ink_bounds(shapes)
    if box is None:
        r.add("error", "empty", "Nothing paints (no fills or strokes).")
        return r
    x0, y0, w, h = vb
    left = (box[0] - x0) / w * 100
    right = (x0 + w - box[2]) / w * 100
    top = (box[1] - y0) / h * 100
    bottom = (y0 + h - box[3]) / h * 100
    r.facts["margins_pct"] = {k: round(v, 1) for k, v in dict(left=left, top=top, right=right, bottom=bottom).items()}
    if min(left, right, top, bottom) < -0.5:
        r.add("error", "clipped", f"Ink extends outside the viewBox (margins % {r.facts['margins_pct']}).",
              "Enlarge the viewBox or move the drawing inside it.")
    elif kind == "symbol":
        if min(left, right, top, bottom) < 1.5:
            r.add("info", "tight", "Ink touches the viewBox edge. That is right for a master (lockup.py adds clear space), "
                                   "wrong if this file is used directly as an icon.")
        if max(left, right, top, bottom) > 22:
            r.add("warn", "wasted-space", f"Large empty margin ({r.facts['margins_pct']}): the mark will render small "
                                           "wherever the file is dropped in.", "Crop the viewBox to the ink.")
    r.facts["_margin_lr"] = (left, right)  # judged together with the mass centre below
    aspect = w / h
    r.facts["aspect"] = round(aspect, 3)
    if kind == "symbol" and not 0.8 <= aspect <= 1.25:
        r.add("info", "not-square", f"Symbol aspect {aspect:.2f}: app icons and avatars need a square-ish mark "
                                    "(or a square master with the mark centred).")

    # near-miss angles
    diag = math.hypot(w, h)
    angles = segment_angles(shapes, min_len=diag * 0.05)
    near = []
    for ang, L in angles:
        rem = ang % 45
        off = min(rem, 45 - rem)
        if 0.6 <= off <= 2.5:
            near.append(round(ang, 1))
    near = sorted(set(near))
    if near:
        r.add("warn", "near-miss-angle", f"Straight edges at {near[:6]}°: almost but not quite 0/45/90. Reads as a mistake.",
              "Snap to the grid angle, or make the tilt clearly intentional (5° or more).")

    # stroke widths
    sw = [s["stroke_width"] for s in shapes if s["stroke"] != "none"]
    if sw:
        mn = min(sw)
        px16 = mn * 16 / max(w, h)
        r.facts["min_stroke_units"] = round(mn, 3)
        r.facts["min_stroke_px_at_16"] = round(px16, 2)
        r.add("info", "strokes", f"Stroke-based drawing (thinnest {mn:.2f} units = {px16:.2f} px at 16 px). Masters should be "
                                 "outlined fills; keep this as the editable construction file.",
              "Expand strokes (Inkscape: Path > Stroke to Path, or skia-pathops) before delivery.")

    # raster tests
    try:
        m256, (W, H) = render_mask(path, RASTER, vb)
    except Exception as e:
        r.add("warn", "no-render", f"Could not rasterise for small-size tests: {e}")
        r.facts.pop("_margin_lr", None)
        return r
    fg, holes = components(m256)
    r.facts["parts_at_256"] = fg
    r.facts["counters_at_256"] = holes
    if expect_parts is not None and fg != expect_parts:
        r.add("warn", "part-count", f"{fg} separate parts at 256 px, expected {expect_parts}.",
              "Join or separate shapes cleanly; check for hairline gaps or overlaps.")
    if fg > 6 and kind == "symbol":
        r.add("warn", "fragmented", f"{fg} separate pieces: fragmented marks fall apart at small sizes.",
              "Aim for 1-3 pieces.")
    t = thinnest(m256)
    g = smallest_gap(m256)
    scale16 = 16 / max(W, H)
    scale32 = 32 / max(W, H)
    if t:
        r.facts["thinnest_feature_px_at_16"] = round(t * scale16, 2)
        r.facts["thinnest_feature_px_at_32"] = round(t * scale32, 2)
        r.facts["thinnest_feature_pct"] = round(t / max(W, H) * 100, 1)
        need = 1.0 if kind == "symbol" else 0.6
        if t * scale16 < need:
            sev = "warn" if kind == "symbol" else "info"
            r.add(sev, "thin", f"Thinnest feature is {t * scale16:.2f} px at 16 px ({t / max(W, H) * 100:.1f}% of the canvas).",
                  "At favicon size strokes need at least 1 px (6-8% of the canvas). Thicken, or design a simplified favicon variant.")
    if g:
        r.facts["smallest_gap_px_at_16"] = round(g * scale16, 2)
        r.facts["smallest_gap_pct"] = round(g / max(W, H) * 100, 1)
        if g * scale16 < 1.0 and kind == "symbol":
            r.add("warn", "gap", f"Smallest gap/counter is {g * scale16:.2f} px at 16 px: it will fill in.",
                  "Open counters and gaps to at least 1 px at 16 px (6% of the canvas).")
    # Symbols are judged at 16 and 32 px (favicon, tab). A wordmark is never used
    # that small: judge it at the smallest width a lockup is allowed (120 px) and at 240 px.
    small_sizes = (16, 32) if kind == "symbol" else (120, 240)
    for size in small_sizes:
        try:
            ms, _ = render_mask(path, size, vb)
            f, hh = components(ms)
            r.facts[f"parts_at_{size}"] = f
            r.facts[f"counters_at_{size}"] = hh
            if f > fg:
                r.add("warn", "breaks-small", f"At {size} px the mark splits into {f} pieces (vs {fg}).",
                      "Thin joins or hairline overlaps open up when rasterised; thicken them." if kind == "symbol" else
                      "Letters with thin joins (e, g, a) fragment; use a heavier weight or a larger minimum width.")
            elif f < fg and size == small_sizes[0]:
                r.add("info", "merges-small", f"At {size} px parts merge ({f} vs {fg}); acceptable only if the silhouette still reads.")
            if hh < holes and size == small_sizes[0]:
                r.add("info", "counters-fill", f"At {size} px {holes - hh} counter(s) fill in.")
        except Exception:
            pass
    c = centroid(m256)
    left_m, right_m = r.facts.pop("_margin_lr", (0.0, 0.0))
    if c:
        dx = (c[0] - W / 2) / W * 100
        dy = (c[1] - H / 2) / H * 100
        r.facts["mass_centre_offset_pct"] = {"x": round(dx, 1), "y": round(dy, 1)}
        if kind == "symbol":
            if abs(dx) > 4:
                r.add("warn", "mass-off-x", f"Visual mass sits {abs(dx):.1f}% to the {'right' if dx > 0 else 'left'} of centre.",
                      "Shift the drawing (or add a counterweight) so it sits optically centred.")
            elif abs(left_m - right_m) > 3:
                r.add("info", "off-centre-x", f"Horizontal margins differ (left {left_m:.1f}% vs right {right_m:.1f}%) but the "
                                              "visual mass is centred: this is optical compensation for an asymmetric mark, keep it.")
            if dy > 3:
                r.add("warn", "mass-low", f"Visual mass sits {dy:.1f}% below centre: the mark will look like it is sinking.",
                      "Move it up slightly; the optical centre is a little above the geometric centre.")
    elif abs(left_m - right_m) > 3 and kind == "symbol":
        r.add("warn", "off-centre-x", f"Horizontal margins differ (left {left_m:.1f}% vs right {right_m:.1f}%).",
              "Centre the ink, unless the asymmetry is intentional optical compensation.")
    return r


def fmt_report(path, kind, r: Report) -> str:
    sev_icon = {"error": "ERROR", "warn": "WARN ", "info": "info "}
    lines = [f"# check_logo: {Path(path).name}  ({kind})", ""]
    lines.append(f"Score: {r.score()}/100  — " + ("ship-ready structure" if r.score() >= 90 else
                                                   "fix the warnings" if r.score() >= 70 else "rework needed"))
    lines.append("")
    f = r.facts
    facts = [
        f"viewBox {f.get('viewBox')}  aspect {f.get('aspect')}  palette {f.get('palette')}",
        f"margins % {f.get('margins_pct')}  mass-centre offset % {f.get('mass_centre_offset_pct')}",
        "parts: " + ", ".join(f"{v} @{k.split('_')[-1]}px" for k, v in f.items() if k.startswith("parts_at_")) + ";  "
        f"counters: {f.get('counters_at_256')} @256, {f.get('counters_at_16')} @16",
        f"thinnest feature {f.get('thinnest_feature_pct')}% of canvas = {f.get('thinnest_feature_px_at_16')} px @16, "
        f"{f.get('thinnest_feature_px_at_32')} px @32;  smallest gap {f.get('smallest_gap_pct')}% = {f.get('smallest_gap_px_at_16')} px @16",
        f"path data {f.get('path_data_chars')} chars, {f.get('points_flattened')} flattened points",
    ]
    lines += ["Facts:"] + ["- " + x for x in facts] + [""]
    if not r.issues:
        lines.append("No issues found.")
    else:
        lines.append("Issues:")
        for i in sorted(r.issues, key=lambda i: ("error", "warn", "info").index(i["severity"])):
            lines.append(f"- [{sev_icon[i['severity']]}] {i['code']}: {i['message']}")
            if i["fix"]:
                lines.append(f"      fix: {i['fix']}")
    lines.append("")
    lines.append("Not checked by software (judge by eye and with render.py --sheet): distinctiveness, appropriateness, "
                 "cliché, likeness to existing marks, how it feels.")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--kind", choices=["auto", "symbol", "wordmark", "lockup"], default="auto")
    ap.add_argument("--expect-parts", type=int, help="how many separate pieces the design intends")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    kind = a.kind
    if kind == "auto":
        _, root = read_svg(a.svg)
        if root.get("data-font"):
            kind = "wordmark"
        else:
            vb = get_viewbox(root)
            kind = "symbol" if 0.7 <= vb[2] / vb[3] <= 1.4 else "lockup"
    r = check(a.svg, kind, a.expect_parts)
    if a.json:
        print(json.dumps({"file": a.svg, "kind": kind, "score": r.score(), "facts": r.facts, "issues": r.issues},
                         indent=2))
    else:
        print(fmt_report(a.svg, kind, r))
    sys.exit(1 if any(i["severity"] == "error" for i in r.issues) else 0)


if __name__ == "__main__":
    main()
