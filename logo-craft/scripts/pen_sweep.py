#!/usr/bin/env python3
"""Turn a skeleton stroke into a calligraphic (or monoline) outline.

    # broad-edge nib: Foundational/Italic/Uncial hands. Nib held at 30°, 12 units wide
    python3 pen_sweep.py --d "M20 80 C 20 20, 80 20, 80 80" --mode broad --angle 30 --width 12 --out o.svg
    # pointed pen (Copperplate 55° slant): thick on downstrokes, hairline up
    python3 pen_sweep.py --svg skeleton.svg --mode pointed --angle 55 --width 10 --min-width 1.2 --out c.svg
    # brush: tapered ends, pressure in the middle
    python3 pen_sweep.py --svg s.svg --mode brush --width 14 --taper 0.2,0.35 --out b.svg
    # monoline with round caps
    python3 pen_sweep.py --svg s.svg --mode mono --width 8 --out m.svg

The skeleton is the centreline you would draw with the pen: one `--d` per
stroke, or every path/line/polyline in `--svg`. Output is a filled outline
(no strokes), unioned with skia-pathops when available so overlapping strokes
merge into one shape. Add --skeleton to overlay the centreline in red for
inspection. Angles are degrees from the horizontal baseline, as in
calligraphy manuals (broad nib 30° Foundational, 45° Italic, 15-20° Uncial;
pointed-pen slant 55° Copperplate, 52° Spencerian).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ensure_deps, fmt, get_viewbox, read_svg  # noqa: E402

ensure_deps("fontTools")
from _geom import flatten_recording, iter_shapes, record_d, shape_to_d  # noqa: E402

try:
    import pathops  # skia-pathops, optional
except Exception:  # pragma: no cover
    pathops = None


# ------------------------------------------------------------ polygon utils
def signed_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2


def ccw(pts):
    return pts if signed_area(pts) >= 0 else list(reversed(pts))


def rdp(points, eps):
    """Ramer-Douglas-Peucker simplification of an open polyline."""
    if len(points) < 3:
        return points

    def dist(p, a, b):
        ax, ay = a
        bx, by = b
        px, py = p
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

    stack = [(0, len(points) - 1)]
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    while stack:
        s, e = stack.pop()
        dmax, idx = 0.0, -1
        for i in range(s + 1, e):
            d = dist(points[i], points[s], points[e])
            if d > dmax:
                dmax, idx = d, i
        if dmax > eps and idx > 0:
            keep[idx] = True
            stack.append((s, idx))
            stack.append((idx, e))
    return [p for p, k in zip(points, keep) if k]


def resample(points, step):
    """Even spacing along a polyline (keeps shape, stabilises widths)."""
    if len(points) < 2:
        return points
    out = [points[0]]
    acc = 0.0
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0:
            continue
        t = 0.0
        while acc + (seg - t) >= step:
            t += step - acc
            acc = 0.0
            out.append((x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg))
        acc += seg - t
    if out[-1] != points[-1]:
        out.append(points[-1])
    return out


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------ stroke models
def broad_polygons(pts, width, angle_deg):
    """Minkowski sum of the polyline with a nib segment at `angle`."""
    a = math.radians(angle_deg)
    nx, ny = math.cos(a) * width / 2, -math.sin(a) * width / 2  # SVG y is down
    polys = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if (x0, y0) == (x1, y1):
            continue
        polys.append(ccw([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]))
    return polys


def ribbon_polygon(pts, widths, cap="round"):
    """Variable-width ribbon around a polyline. widths[i] is the full width at
    vertex i. Returns one polygon (may self-intersect at tight turns; the
    union step cleans that up)."""
    n = len(pts)
    if n < 2:
        return None
    dirs = []
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
        else:
            dx = pts[i + 1][0] - pts[i - 1][0]
            dy = pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        dirs.append((dx / L, dy / L))
    left, right = [], []
    for (x, y), (dx, dy), w in zip(pts, dirs, widths):
        nx, ny = -dy, dx
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))

    poly = list(left)
    if cap == "round" and widths[-1] > 0.05:
        poly += _end_cap(pts[-1], dirs[-1], widths[-1] / 2)
    poly += list(reversed(right))
    if cap == "round" and widths[0] > 0.05:
        poly += _end_cap(pts[0], (-dirs[0][0], -dirs[0][1]), widths[0] / 2)
    return ccw(poly)


def _end_cap(p, d, r, steps=10):
    """Points of a semicircular cap at p, bulging in direction d, going from
    the +normal side to the -normal side."""
    nx, ny = -d[1], d[0]
    base = math.atan2(ny, nx)
    out = []
    for k in range(1, steps):
        t = base - math.pi * k / steps  # rotate from +n through +d to -n
        out.append((p[0] + r * math.cos(t), p[1] + r * math.sin(t)))
    return out


def pointed_widths(pts, wmax, wmin, slant_deg, k):
    a = math.radians(slant_deg)
    down = (-math.cos(a), math.sin(a))  # downstroke direction for a right-leaning slant
    n = len(pts)
    ws = []
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
        else:
            dx = pts[i + 1][0] - pts[i - 1][0]
            dy = pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        p = max(0.0, (dx / L) * down[0] + (dy / L) * down[1]) ** k
        ws.append(wmin + (wmax - wmin) * p)
    # smooth width changes so pressure transitions look like a real nib
    sm = ws[:]
    for _ in range(3):
        sm = [sm[0]] + [(sm[i - 1] + 2 * sm[i] + sm[i + 1]) / 4 for i in range(1, n - 1)] + [sm[-1]]
    return sm


def brush_widths(pts, wmax, wmin, taper_start, taper_end):
    total = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) or 1.0
    ws, s = [], 0.0
    for i, p in enumerate(pts):
        if i:
            s += math.dist(pts[i - 1], p)
        t = s / total
        f = 1.0
        if taper_start > 0:
            f = min(f, smoothstep(t / taper_start))
        if taper_end > 0:
            f = min(f, smoothstep((1 - t) / taper_end))
        ws.append(wmin + (wmax - wmin) * f)
    return ws


# ------------------------------------------------------------ union / output
def union_polygons(polys, eps):
    if pathops is None:
        return [rdp(p + [p[0]], eps)[:-1] for p in polys], False
    path = pathops.Path()
    pen = path.getPen()
    for poly in polys:
        if len(poly) < 3:
            continue
        pen.moveTo(poly[0])
        for pt in poly[1:]:
            pen.lineTo(pt)
        pen.closePath()
    path.fillType = pathops.FillType.WINDING
    result = pathops.simplify(path, fix_winding=True)
    out = []
    for contour in result.contours:
        pts = []
        for verb, points in contour:
            if verb == pathops.PathVerb.MOVE:
                pts = [points[0]]
            elif verb == pathops.PathVerb.LINE:
                pts.append(points[0])
            elif verb in (pathops.PathVerb.QUAD, pathops.PathVerb.CUBIC, pathops.PathVerb.CONIC):
                pts.append(points[-1])
            elif verb == pathops.PathVerb.CLOSE:
                pass
        if len(pts) >= 3:
            out.append(rdp(pts + [pts[0]], eps)[:-1])
    return out, True


def polys_to_d(polys):
    parts = []
    for poly in polys:
        if len(poly) < 3:
            continue
        parts.append("M" + " L".join(f"{fmt(x, 2)} {fmt(y, 2)}" for x, y in poly) + "Z")
    return " ".join(parts)


def skeleton_paths(args):
    """List of (d, Transform or None) skeleton strokes plus a viewBox guess."""
    strokes, vb = [], None
    if args.svg:
        _, root = read_svg(args.svg)
        vb = get_viewbox(root)
        for el, tf, _style in iter_shapes(root):
            d = shape_to_d(el)
            if d:
                strokes.append((d, tf))
    for d in args.d or []:
        strokes.append((d, None))
    if not strokes:
        sys.exit("error: give --d \"M...\" (repeatable) or --svg skeleton.svg")
    return strokes, vb


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--d", action="append", help="skeleton path data (repeat per stroke)")
    ap.add_argument("--svg", help="SVG whose paths/lines/polylines are the skeleton")
    ap.add_argument("--mode", choices=["broad", "pointed", "brush", "mono"], default="broad")
    ap.add_argument("--width", type=float, default=10.0, help="nib width (broad) or maximum width (others)")
    ap.add_argument("--min-width", type=float, default=None, help="hairline width for pointed/brush (default width/8)")
    ap.add_argument("--angle", type=float, default=None,
                    help="broad: nib angle from horizontal (default 30). pointed: slant (default 55)")
    ap.add_argument("--pressure", type=float, default=1.4, help="pointed: pressure curve exponent (>1 = crisper)")
    ap.add_argument("--taper", default="0.15,0.25", help="brush: start,end taper as fractions of length")
    ap.add_argument("--cap", choices=["round", "butt"], default="round", help="mono/pointed/brush end caps")
    ap.add_argument("--step", type=float, default=None, help="flattening step (default width/6)")
    ap.add_argument("--tolerance", type=float, default=None, help="simplification tolerance (default width/60)")
    ap.add_argument("--no-union", action="store_true", help="keep one polygon per segment (debug)")
    ap.add_argument("--separate", action="store_true", help="one <path> per skeleton stroke instead of one union")
    ap.add_argument("--skeleton", action="store_true", help="overlay the centreline in red")
    ap.add_argument("--viewbox", help='output viewBox "x y w h" (default: input SVG, else auto)')
    ap.add_argument("--padding", type=float, default=None, help="auto viewBox padding (default width)")
    ap.add_argument("--fill", default="#000000")
    ap.add_argument("--out", help="output SVG (default stdout)")
    a = ap.parse_args()

    strokes, vb = skeleton_paths(a)
    width = a.width
    wmin = a.min_width if a.min_width is not None else width / 8
    step = a.step or max(width / 6, 0.05)
    eps = a.tolerance if a.tolerance is not None else width / 60
    angle = a.angle if a.angle is not None else (30.0 if a.mode == "broad" else 55.0)
    taper = [float(x) for x in a.taper.split(",")] if a.mode == "brush" else [0, 0]

    all_polys, per_stroke, skel = [], [], []
    for d, tf in strokes:
        rec = record_d(d)
        for pts, closed in flatten_recording(rec, step, tf):
            if closed and pts[0] != pts[-1]:
                pts = pts + [pts[0]]
            pts = resample(pts, step)
            skel.append(pts)
            if a.mode == "broad":
                polys = broad_polygons(pts, width, angle)
            else:
                if a.mode == "pointed":
                    ws = pointed_widths(pts, width, wmin, angle, a.pressure)
                elif a.mode == "brush":
                    ws = brush_widths(pts, width, wmin * 0.3, taper[0], taper[1] if len(taper) > 1 else taper[0])
                else:
                    ws = [width] * len(pts)
                poly = ribbon_polygon(pts, ws, cap=a.cap)
                polys = [poly] if poly else []
            per_stroke.append(polys)
            all_polys.extend(polys)

    if a.no_union:
        groups = [all_polys]
        unioned = False
    elif a.separate:
        groups = []
        for polys in per_stroke:
            g, unioned = union_polygons(polys, eps)
            groups.append(g)
    else:
        g, unioned = union_polygons(all_polys, eps)
        groups = [g]

    # viewBox
    if a.viewbox:
        x, y, w, h = [float(v) for v in a.viewbox.split()]
    elif vb:
        x, y, w, h = vb
    else:
        xs = [p[0] for g in groups for poly in g for p in poly]
        ys = [p[1] for g in groups for poly in g for p in poly]
        pad = a.padding if a.padding is not None else width
        x, y = min(xs) - pad, min(ys) - pad
        w, h = (max(xs) - min(xs)) + 2 * pad, (max(ys) - min(ys)) + 2 * pad

    body = ""
    for i, g in enumerate(groups):
        d = polys_to_d(g)
        if d:
            body += f'  <path id="stroke{i}" fill="{a.fill}" fill-rule="nonzero" d="{d}"/>\n'
    if a.skeleton:
        for pts in skel:
            d = "M" + " L".join(f"{fmt(px, 2)} {fmt(py, 2)}" for px, py in pts)
            body += f'  <path fill="none" stroke="#E0245E" stroke-width="{fmt(max(w, h) / 400, 3)}" d="{d}"/>\n'
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(x)} {fmt(y)} {fmt(w)} {fmt(h)}" '
           f'data-pen="{a.mode}" data-width="{fmt(width)}" data-angle="{fmt(angle)}">\n{body}</svg>\n')
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(svg, encoding="utf-8")
        npts = sum(len(p) for g in groups for p in g)
        print(f"wrote {a.out}  ({a.mode}, {len(strokes)} strokes -> {sum(len(g) for g in groups)} contours, "
              f"{npts} points, union={'skia' if unioned else 'none (install skia-pathops for clean merges)'})")
    else:
        sys.stdout.write(svg)


if __name__ == "__main__":
    main()
