#!/usr/bin/env python3
"""SVG composition helpers shared by lockup.py and export_kit.py.
Import after `_common.ensure_deps("fontTools")`.
"""
from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET

from _common import SVG_NS, fmt, get_viewbox, local, parse_hex, q, sanitize_svg, to_hex
from _geom import ink_bounds, shape_polylines

NAMED = {
    "black": "#000000", "white": "#FFFFFF", "red": "#FF0000", "green": "#008000", "blue": "#0000FF",
    "gray": "#808080", "grey": "#808080", "silver": "#C0C0C0", "navy": "#000080", "teal": "#008080",
    "orange": "#FFA500", "purple": "#800080", "yellow": "#FFFF00", "maroon": "#800000", "olive": "#808000",
    "lime": "#00FF00", "aqua": "#00FFFF", "cyan": "#00FFFF", "fuchsia": "#FF00FF", "magenta": "#FF00FF",
    "transparent": None,
}


def norm_color(value: str | None, current: str = "#000000") -> tuple[str | None, float]:
    """Normalise an SVG paint to (#RRGGBB or None, alpha). Gradients/patterns
    return the sentinel ('url', 1.0)."""
    if value is None:
        return "#000000", 1.0
    v = value.strip()
    if v == "none":
        return None, 1.0
    if v.startswith("url("):
        return "url", 1.0
    if v.lower() == "currentcolor":
        return current.upper(), 1.0
    if v.lower() in NAMED:
        return NAMED[v.lower()], 1.0
    if v.startswith("#"):
        if len(v) in (4, 7):
            return to_hex(parse_hex(v)), 1.0
        if len(v) == 9:  # #RRGGBBAA
            return v[:7].upper(), int(v[7:9], 16) / 255
        if len(v) == 5:
            r, g, b, a = v[1], v[2], v[3], v[4]
            return f"#{r}{r}{g}{g}{b}{b}".upper(), int(a * 2, 16) / 255
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        parts = [p.strip() for p in re.split(r"[,\s/]+", m.group(1)) if p.strip()]
        rgb = []
        for p in parts[:3]:
            rgb.append(float(p[:-1]) * 2.55 if p.endswith("%") else float(p))
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return to_hex(tuple(rgb)), a  # type: ignore[arg-type]
    return "#000000", 1.0


def ink_box(root: ET.Element) -> tuple[float, float, float, float]:
    b = ink_bounds(shape_polylines(root))
    if b is None:
        x, y, w, h = get_viewbox(root)
        return (x, y, x + w, y + h)
    return b


def new_svg(w: float, h: float, x: float = 0, y: float = 0, title: str | None = None) -> ET.Element:
    root = ET.Element(q("svg"))  # ElementTree writes xmlns from the qualified tag
    root.set("viewBox", f"{fmt(x)} {fmt(y)} {fmt(w)} {fmt(h)}")
    if title:
        root.set("role", "img")
        root.set("aria-label", title)
        t = ET.SubElement(root, q("title"))
        t.text = title
    return root


_ID_ATTRS = ("id",)
_REF_ATTRS = ("href", f"{{http://www.w3.org/1999/xlink}}href", "fill", "stroke", "filter", "mask", "clip-path", "style")


def embed_group(src_root: ET.Element, transform: str | None, prefix: str) -> ET.Element:
    """Deep-copy the children of an SVG root into a <g> with the given
    transform. Ids are prefixed so two embedded logos cannot clash. The root's
    presentation attributes are carried onto the group."""
    g = ET.Element(q("g"))
    if transform:
        g.set("transform", transform)
    for a in ("fill", "stroke", "stroke-width", "fill-rule", "style", "color", "opacity"):
        if src_root.get(a) is not None:
            g.set(a, src_root.get(a))
    for child in src_root:
        tag = local(child.tag)
        if tag in ("title", "desc", "metadata"):
            continue
        g.append(copy.deepcopy(child))
    sanitize_svg(g)  # never carry scripts, handlers or external references into a deliverable
    # prefix ids and references
    ids = set()
    for el in g.iter():
        if el.get("id"):
            ids.add(el.get("id"))
    if ids:
        for el in g.iter():
            if el.get("id") in ids:
                el.set("id", prefix + el.get("id"))
            for a in _REF_ATTRS:
                v = el.get(a)
                if not v:
                    continue
                nv = v
                for i in ids:
                    nv = nv.replace(f"url(#{i})", f"url(#{prefix}{i})").replace(f"#{i}", f"#{prefix}{i}") \
                        if (f"url(#{i})" in nv or nv == f"#{i}") else nv
                if nv != v:
                    el.set(a, nv)
            if el.text and "url(#" in (el.text or "") and local(el.tag) == "style":
                for i in ids:
                    el.text = el.text.replace(f"#{i}", f"#{prefix}{i}")
    return g


def fit_transform(box: tuple[float, float, float, float], target_w: float, target_h: float,
                  cx: float, cy: float) -> tuple[str, float]:
    """Transform string that scales `box` (ink bounds) to fit target_w x
    target_h and centres it at (cx, cy). Returns (transform, scale)."""
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = min(target_w / bw if bw else 1, target_h / bh if bh else 1)
    bx = (box[0] + box[2]) / 2
    by = (box[1] + box[3]) / 2
    tx, ty = cx - bx * s, cy - by * s
    return f"translate({fmt(tx)} {fmt(ty)}) scale({fmt(s, 5)})", s


def square_canvas(symbol_root: ET.Element, size: float = 1024, scale: float = 0.62, bg: str | None = None,
                  fg: str | None = None, radius: float | None = None, title: str | None = None,
                  offset_y: float = 0.0) -> ET.Element:
    """Symbol centred on a size x size canvas. `scale` is the fraction of the
    canvas the symbol's longest side occupies. `bg` draws a background rect
    (with optional corner radius), `fg` recolours the symbol. `offset_y` (in
    canvas fractions, negative = up) lets you optically centre."""
    from _common import recolor
    root = new_svg(size, size, title=title)
    if bg:
        r = ET.SubElement(root, q("rect"))
        r.set("width", fmt(size))
        r.set("height", fmt(size))
        r.set("fill", bg)
        if radius:
            r.set("rx", fmt(radius))
    sym = copy.deepcopy(symbol_root)
    if fg:
        recolor(sym, fg)
    box = ink_box(sym)
    tf, _ = fit_transform(box, size * scale, size * scale, size / 2, size / 2 + offset_y * size)
    root.append(embed_group(sym, tf, "s-"))
    return root


def pad_canvas(root: ET.Element, pad_frac: float, square: bool = False, title: str | None = None) -> ET.Element:
    """Re-frame an SVG tightly around its ink with padding (fraction of the
    longer ink side). square=True makes the viewBox square."""
    box = ink_box(root)
    bw, bh = box[2] - box[0], box[3] - box[1]
    pad = max(bw, bh) * pad_frac
    if square:
        side = max(bw, bh) + 2 * pad
        w = h = side
    else:
        w, h = bw + 2 * pad, bh + 2 * pad
    out = new_svg(w, h, title=title)
    tf, _ = fit_transform(box, bw, bh, w / 2, h / 2)
    out.append(embed_group(root, tf, "p-"))
    for a in list(root.attrib):
        if a.startswith("data-"):
            out.set(a, root.get(a))
    return out


def palette_of(root: ET.Element) -> list[str]:
    """Distinct flat colours painted in the document (gradients count as 'url')."""
    from _common import iter_paint
    seen = []
    for el, attr, v in iter_paint(root):
        c, _ = norm_color(v)
        if c and c not in seen:
            seen.append(c)
    return seen
