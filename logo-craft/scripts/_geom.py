#!/usr/bin/env python3
"""Geometry helpers shared by check_logo, lockup, pen_sweep and export_kit.

Needs fontTools (for the SVG path parser, pens and affine transforms). Import
`_common.ensure_deps("fontTools")` before importing this module.
"""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

from fontTools.misc.transform import Identity, Transform
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path.parser import parse_path

from _common import fmt, local, parse_length

SHAPE_TAGS = ("path", "rect", "circle", "ellipse", "polygon", "polyline", "line")
SKIP_TAGS = ("defs", "clipPath", "mask", "pattern", "marker", "symbol", "linearGradient",
             "radialGradient", "metadata", "title", "desc", "style", "script", "filter")

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


# ------------------------------------------------------------ transforms
def parse_transform(s: str | None) -> Transform:
    """Parse an SVG transform attribute into a fontTools Transform."""
    t = Identity
    if not s:
        return t
    for name, args in re.findall(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)", s):
        nums = [float(x) for x in re.findall(_NUM, args)]
        if name == "matrix" and len(nums) == 6:
            m = Transform(*nums)
        elif name == "translate":
            m = Identity.translate(nums[0], nums[1] if len(nums) > 1 else 0)
        elif name == "scale":
            m = Identity.scale(nums[0], nums[1] if len(nums) > 1 else nums[0])
        elif name == "rotate":
            a = math.radians(nums[0])
            if len(nums) == 3:
                m = Identity.translate(nums[1], nums[2]).rotate(a).translate(-nums[1], -nums[2])
            else:
                m = Identity.rotate(a)
        elif name == "skewX":
            m = Identity.skew(math.radians(nums[0]), 0)
        elif name == "skewY":
            m = Identity.skew(0, math.radians(nums[0]))
        else:
            continue
        t = t.transform(m)
    return t


# ------------------------------------------------------------ shapes → d
def _f(v) -> float:
    n = parse_length(v)
    return 0.0 if n is None else n


def shape_to_d(el: ET.Element) -> str | None:
    """Return a path `d` for any basic shape (or the path's own d)."""
    tag = local(el.tag)
    g = el.get
    if tag == "path":
        return g("d")
    if tag == "rect":
        x, y, w, h = _f(g("x")), _f(g("y")), _f(g("width")), _f(g("height"))
        rx, ry = g("rx"), g("ry")
        rx = _f(rx) if rx is not None else (_f(ry) if ry is not None else 0.0)
        ry = _f(ry) if ry is not None else rx
        rx, ry = min(rx, w / 2), min(ry, h / 2)
        if rx <= 0 or ry <= 0:
            return f"M{fmt(x)} {fmt(y)}H{fmt(x + w)}V{fmt(y + h)}H{fmt(x)}Z"
        return (f"M{fmt(x + rx)} {fmt(y)}H{fmt(x + w - rx)}A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x + w)} {fmt(y + ry)}"
                f"V{fmt(y + h - ry)}A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x + w - rx)} {fmt(y + h)}"
                f"H{fmt(x + rx)}A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x)} {fmt(y + h - ry)}"
                f"V{fmt(y + ry)}A{fmt(rx)} {fmt(ry)} 0 0 1 {fmt(x + rx)} {fmt(y)}Z")
    if tag in ("circle", "ellipse"):
        cx, cy = _f(g("cx")), _f(g("cy"))
        if tag == "circle":
            rx = ry = _f(g("r"))
        else:
            rx, ry = _f(g("rx")), _f(g("ry"))
        if rx <= 0 or ry <= 0:
            return None
        return (f"M{fmt(cx + rx)} {fmt(cy)}A{fmt(rx)} {fmt(ry)} 0 1 1 {fmt(cx - rx)} {fmt(cy)}"
                f"A{fmt(rx)} {fmt(ry)} 0 1 1 {fmt(cx + rx)} {fmt(cy)}Z")
    if tag in ("polygon", "polyline"):
        nums = [float(x) for x in re.findall(_NUM, g("points") or "")]
        if len(nums) < 4:
            return None
        pts = list(zip(nums[0::2], nums[1::2]))
        d = "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in pts)
        return d + ("Z" if tag == "polygon" else "")
    if tag == "line":
        return f"M{fmt(_f(g('x1')))} {fmt(_f(g('y1')))}L{fmt(_f(g('x2')))} {fmt(_f(g('y2')))}"
    return None


def record_d(d: str) -> RecordingPen:
    """Parse a path d into a RecordingPen (arcs become cubics)."""
    pen = RecordingPen()
    parse_path(d, pen)
    return pen


def recording_to_d(rec: RecordingPen, transform: Transform | None = None, places: int = 3) -> str:
    out = SVGPathPen(None, ntos=lambda v: fmt(v, places))
    pen = TransformPen(out, transform) if transform and transform != Identity else out
    rec.replay(pen)
    return out.getCommands()


# ------------------------------------------------------------ flattening
def _bezier_points(p0, ctrl, p1, n):
    pts = []
    if len(ctrl) == 1:  # quadratic
        c = ctrl[0]
        for i in range(1, n + 1):
            t = i / n
            mt = 1 - t
            pts.append((mt * mt * p0[0] + 2 * mt * t * c[0] + t * t * p1[0],
                        mt * mt * p0[1] + 2 * mt * t * c[1] + t * t * p1[1]))
    else:  # cubic
        c1, c2 = ctrl[0], ctrl[1]
        for i in range(1, n + 1):
            t = i / n
            mt = 1 - t
            a, b, c, d = mt ** 3, 3 * mt * mt * t, 3 * mt * t * t, t ** 3
            pts.append((a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0],
                        a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1]))
    return pts


def flatten_recording(rec: RecordingPen, step: float = 0.5, transform: Transform | None = None):
    """Flatten a recording into polylines: list of (points, closed).
    `step` is the target segment length in user units."""
    polys = []
    cur: list = []
    closed = False
    start = None
    tf = transform if transform and transform != Identity else None

    def T(p):
        return tf.transformPoint(p) if tf else p

    def finish():
        nonlocal cur, closed
        if len(cur) >= 2:
            polys.append((cur, closed))
        cur, closed = [], False

    for op, args in rec.value:
        if op == "moveTo":
            finish()
            start = T(args[0])
            cur = [start]
        elif op == "lineTo":
            cur.append(T(args[0]))
        elif op in ("curveTo", "qCurveTo"):
            pts = [T(p) for p in args if p is not None]
            if not cur:
                cur = [pts[0]]
            p0 = cur[-1]
            if op == "qCurveTo" and len(pts) > 2:
                # TrueType-style implied on-curve points
                for i in range(len(pts) - 1):
                    c = pts[i]
                    nxt = pts[i + 1] if i + 1 < len(pts) - 1 else pts[-1]
                    end = nxt if i + 1 == len(pts) - 1 else ((c[0] + nxt[0]) / 2, (c[1] + nxt[1]) / 2)
                    n = _steps(p0, [c], end, step)
                    cur.extend(_bezier_points(p0, [c], end, n))
                    p0 = end
            else:
                ctrl, end = pts[:-1], pts[-1]
                n = _steps(p0, ctrl, end, step)
                cur.extend(_bezier_points(p0, ctrl, end, n))
        elif op == "closePath":
            closed = True
            finish()
        elif op == "endPath":
            finish()
    finish()
    return polys


def _steps(p0, ctrl, p1, step):
    length = 0.0
    prev = p0
    for p in list(ctrl) + [p1]:
        length += math.dist(prev, p)
        prev = p
    return max(3, min(120, int(length / max(step, 1e-6)) + 1))


# ------------------------------------------------------------ document walk
def iter_shapes(root: ET.Element):
    """Yield (element, Transform, inherited style dict) for every drawable
    shape in rendering order, skipping defs/clipPath/mask/etc."""
    def style_of(el, parent_style):
        st = dict(parent_style)
        for k in ("fill", "stroke", "stroke-width", "fill-rule", "opacity", "fill-opacity", "stroke-opacity"):
            if el.get(k) is not None:
                st[k] = el.get(k)
        css = el.get("style")
        if css:
            for part in css.split(";"):
                if ":" in part:
                    k, v = part.split(":", 1)
                    st[k.strip()] = v.strip()
        return st

    def walk(el, tf, style):
        tag = local(el.tag)
        if tag in SKIP_TAGS:
            return
        tf = tf.transform(parse_transform(el.get("transform")))
        style = style_of(el, style)
        if tag in SHAPE_TAGS:
            yield el, tf, style
        for child in el:
            yield from walk(child, tf, style)

    yield from walk(root, Identity, {})


def shape_polylines(root: ET.Element, step: float | None = None):
    """All shapes flattened in root user space.
    Returns list of dicts: points, closed, fill, stroke, stroke_width, tag, el."""
    from _common import get_viewbox
    vb = get_viewbox(root)
    if step is None:
        step = max(vb[2], vb[3]) / 600.0
    out = []
    for el, tf, style in iter_shapes(root):
        d = shape_to_d(el)
        if not d:
            continue
        try:
            rec = record_d(d)
        except Exception:
            continue
        fill = style.get("fill", "#000")
        stroke = style.get("stroke", "none")
        sw = parse_length(style.get("stroke-width", "1")) or 1.0
        # scale stroke width by the transform's mean scale
        sx = math.hypot(tf[0], tf[1])
        sy = math.hypot(tf[2], tf[3])
        sw_eff = sw * (sx + sy) / 2
        tag = local(el.tag)
        if tag in ("line", "polyline") and fill == "#000" and el.get("fill") is None:
            fill = "none"  # open shapes are only meaningful stroked
        for pts, closed in flatten_recording(rec, step, tf):
            out.append({"points": pts, "closed": closed, "fill": fill, "stroke": stroke,
                        "stroke_width": sw_eff, "tag": tag, "el": el, "opacity": style.get("opacity")})
    return out


def ink_bounds(shapes) -> tuple[float, float, float, float] | None:
    """Bounding box of everything that paints (fills or strokes), stroke
    width included."""
    xs, ys = [], []
    for s in shapes:
        paints = (s["fill"] != "none") or (s["stroke"] != "none")
        if not paints:
            continue
        pad = s["stroke_width"] / 2 if s["stroke"] != "none" else 0.0
        for x, y in s["points"]:
            xs += [x - pad, x + pad]
            ys += [y - pad, y + pad]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def polygon_area(points) -> float:
    a = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2


def polygon_centroid(points):
    a = polygon_area(points)
    if abs(a) < 1e-9:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    cx = cy = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        f = x1 * y2 - x2 * y1
        cx += (x1 + x2) * f
        cy += (y1 + y2) * f
    return (cx / (6 * a), cy / (6 * a))


def segment_angles(shapes, min_len: float):
    """Angles (degrees, 0..180) of straight runs longer than min_len.
    Curves are flattened into many short pieces, so a long single segment
    marks a true straight edge."""
    out = []
    for s in shapes:
        pts = s["points"]
        rng = range(len(pts) if s["closed"] else len(pts) - 1)
        for i in rng:
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            L = math.hypot(x2 - x1, y2 - y1)
            if L >= min_len:
                ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
                out.append((ang, L))
    return out


def element_path_d(el: ET.Element, tf: Transform, places: int = 3) -> str | None:
    """Path d for a shape with the accumulated transform baked in (curves
    stay curves because affine maps preserve Béziers)."""
    d = shape_to_d(el)
    if not d:
        return None
    rec = record_d(d)
    return recording_to_d(rec, tf, places)


def flatten_document_to_paths(root: ET.Element) -> list[dict]:
    """Every shape as a transform-free path with its effective style.
    Used for VectorDrawable export and transform flattening."""
    out = []
    for el, tf, style in iter_shapes(root):
        d = element_path_d(el, tf)
        if not d:
            continue
        sx = math.hypot(tf[0], tf[1])
        sy = math.hypot(tf[2], tf[3])
        sw = (parse_length(style.get("stroke-width", "1")) or 1.0) * (sx + sy) / 2
        fill = style.get("fill", "#000")
        tag = local(el.tag)
        if tag in ("line", "polyline") and el.get("fill") is None:
            fill = "none"
        out.append({
            "d": d, "fill": fill, "stroke": style.get("stroke", "none"), "stroke_width": sw,
            "fill_rule": style.get("fill-rule", "nonzero"), "opacity": style.get("opacity"),
            "fill_opacity": style.get("fill-opacity"), "stroke_opacity": style.get("stroke-opacity"),
            "linecap": el.get("stroke-linecap"), "linejoin": el.get("stroke-linejoin"),
        })
    return out
