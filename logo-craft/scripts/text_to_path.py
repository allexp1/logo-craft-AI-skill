#!/usr/bin/env python3
"""Set a wordmark in a real typeface and emit it as SVG outlines.

    python3 text_to_path.py --text "Kixplo" --font "Space Grotesk" --weight 700 --out wordmark.svg
    python3 text_to_path.py --text "לומדים" --font Heebo --weight 800 --out he.svg
    python3 text_to_path.py --text "KIDS LOVE|SCIENCE" --font Fredoka --weight 600 --align center --out stacked.svg
    python3 text_to_path.py --list-fonts [filter]        # curated typefaces from assets/fonts.json
    python3 text_to_path.py --font-info "Inter"         # metrics + licence of a font

Fonts: a file path, a Google Fonts family (downloaded once into
~/.cache/logo-craft/fonts/), or an installed system font. Text is shaped with
HarfBuzz (kerning, ligatures, RTL, marks), then every glyph is converted to a
path with fontTools. The SVG carries data-baseline / data-cap-height /
data-x-height so lockup.py can align a symbol to the letters.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CACHE_DIR, ensure_deps, fmt, skill_dir  # noqa: E402

ensure_deps("fontTools", "uharfbuzz")

import uharfbuzz as hb  # noqa: E402
from fontTools.misc.transform import Identity  # noqa: E402
from fontTools.pens.boundsPen import BoundsPen  # noqa: E402
from fontTools.pens.svgPathPen import SVGPathPen  # noqa: E402
from fontTools.pens.transformPen import TransformPen  # noqa: E402
from fontTools.ttLib import TTCollection, TTFont  # noqa: E402

FONT_CACHE = CACHE_DIR / "fonts"
SYSTEM_FONT_DIRS = [Path("/System/Library/Fonts"), Path("/System/Library/Fonts/Supplemental"), Path("/Library/Fonts"),
                    Path.home() / "Library/Fonts", Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
                    Path.home() / ".fonts", Path.home() / ".local/share/fonts", Path("C:/Windows/Fonts")]
UA = "logo-craft/1.0 (+fontTools; requests TrueType)"


# ------------------------------------------------------------------ fonts
def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", s)


CATALOG_FILE = FONT_CACHE / "catalog.json"
CATALOG_LICENSES = {"ofl": "SIL Open Font License 1.1 (logo use permitted)",
                    "apache": "Apache License 2.0 (logo use permitted)",
                    "ufl": "Ubuntu Font Licence 1.0 (logo use permitted)"}
LAST_CATALOG: dict = {}


def google_catalog(family: str) -> str | None:
    """Which licence directory of the public Google Fonts catalogue
    (github.com/google/fonts) holds `family`: 'ofl', 'apache', 'ufl', or None
    when the family is not in the catalogue. Returns 'unknown' when offline.
    Google's CSS API also serves families that are NOT in the public
    catalogue (Helvetica, for instance); those carry no open licence, so the
    skill refuses to fetch them and falls back to an installed font."""
    slug = re.sub(r"[^a-z0-9]+", "", family.lower())
    cache = {}
    try:
        cache = json.loads(CATALOG_FILE.read_text()) if CATALOG_FILE.exists() else {}
    except Exception:
        cache = {}
    if slug in cache:
        return cache[slug]
    result: str | None = "unknown"
    reached = False
    for d in ("ofl", "apache", "ufl"):
        url = f"https://raw.githubusercontent.com/google/fonts/main/{d}/{slug}/METADATA.pb"
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
            urllib.request.urlopen(req, timeout=10)
            result = d
            reached = True
            break
        except urllib.error.HTTPError as e:
            reached = True
            if e.code == 404:
                result = None
                continue
        except Exception:
            continue
    if not reached:
        return "unknown"
    cache[slug] = result
    try:
        FONT_CACHE.mkdir(parents=True, exist_ok=True)
        CATALOG_FILE.write_text(json.dumps(cache, indent=0, sort_keys=True))
    except Exception:
        pass
    return result


def google_font(family: str, weight: int, italic: bool) -> Path | None:
    """Download a Google Fonts family at the given weight (static instance) and
    cache it. Returns None if the family is unknown to Google Fonts."""
    FONT_CACHE.mkdir(parents=True, exist_ok=True)
    tag = f"{_slug(family)}-{weight}{'i' if italic else ''}"
    where = google_catalog(family)
    if where is None:
        print(f"[fonts] {family}: not in the public Google Fonts catalogue (no open licence); "
              f"looking for an installed font instead", file=sys.stderr)
        return None
    LAST_CATALOG.clear()
    if where in CATALOG_LICENSES:
        LAST_CATALOG.update({"catalog": f"google/fonts:{where}", "license_family": CATALOG_LICENSES[where]})
    for ext in (".ttf", ".otf"):
        p = FONT_CACHE / (tag + ext)
        if p.exists():
            return p
    fam = urllib.parse.quote_plus(family.strip())
    specs = [f"{fam}:ital,wght@{1 if italic else 0},{weight}" if italic else f"{fam}:wght@{weight}",
             f"{fam}:ital,wght@{1 if italic else 0},100..900" if italic else f"{fam}:wght@100..900",
             fam]
    for i, spec in enumerate(specs):
        url = f"https://fonts.googleapis.com/css2?family={spec}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            css = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        except Exception:
            continue
        m = re.search(r"src:\s*url\(([^)]+)\)", css)
        if not m:
            continue
        src = m.group(1).strip("'\"")
        ext = ".otf" if src.lower().endswith(".otf") else ".ttf"
        dest = FONT_CACHE / (tag + ext)
        try:
            data = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": UA}), timeout=30).read()
        except Exception:
            continue
        dest.write_bytes(data)
        if i == 1:
            print(f"[fonts] {family}: exact weight {weight} not served, got the variable font; instancing", file=sys.stderr)
            return instance_variable(dest, {"wght": weight}, dest)
        if i == 2:
            print(f"[fonts] {family}: weight {weight} not available on Google Fonts, using the default style", file=sys.stderr)
        return dest
    return None


def instance_variable(src: Path, axes: dict, dest: Path) -> Path:
    """Pin a variable font to static axis values (saved over `dest`)."""
    from fontTools.varLib import instancer
    f = TTFont(str(src))
    if "fvar" not in f:
        return src
    avail = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in f["fvar"].axes}
    loc = {}
    for tag, val in axes.items():
        if tag in avail:
            lo, _, hi = avail[tag]
            loc[tag] = max(lo, min(hi, val))
    for tag in avail:
        loc.setdefault(tag, avail[tag][1])
    static = instancer.instantiateVariableFont(f, loc, inplace=False, updateFontNames=False)
    static.save(str(dest))
    return dest


def system_font(family: str, weight: int, italic: bool) -> Path | None:
    key = _slug(family).lower()
    hits = []
    for d in SYSTEM_FONT_DIRS:
        if not d.exists():
            continue
        for p in d.glob("*"):
            if p.suffix.lower() in (".ttf", ".otf", ".ttc") and key in _slug(p.stem).lower():
                hits.append(p)
    if not hits:
        return None
    # exact family match beats a longer name that merely contains it ("Avenir Next" vs "Avenir Next Condensed")
    style_words = ("thin", "extralight", "light", "regular", "medium", "semibold", "bold", "extrabold", "black",
                   "italic", "oblique", "demibold", "heavy", "ultralight", "book")
    def family_part(stem: str) -> str:
        n = _slug(stem).lower()
        for w in sorted(style_words, key=len, reverse=True):
            n = n.replace(w, "")
        return n
    exact = [p for p in hits if family_part(p.stem) == key]
    if exact:
        hits = exact
    # prefer a file whose name says the weight/style, else the first
    want = {100: "thin", 200: "extralight", 300: "light", 400: "regular", 500: "medium", 600: "semibold",
            700: "bold", 800: "extrabold", 900: "black"}[min(max(round(weight / 100) * 100, 100), 900)]
    for p in hits:
        n = _slug(p.stem).lower()
        if want in n and (("italic" in n or "oblique" in n) == italic):
            return p
    for p in hits:
        if p.suffix.lower() == ".ttc":
            return p
    return hits[0]


def open_font(path: Path, weight: int, italic: bool) -> tuple[TTFont, int]:
    """Open a font file; for .ttc pick the face closest to weight/italic.
    Returns (TTFont, face_index)."""
    if path.suffix.lower() == ".ttc":
        coll = TTCollection(str(path))
        best, best_i, best_score = None, 0, 1e9
        for i, f in enumerate(coll.fonts):
            os2 = f["OS/2"] if "OS/2" in f else None
            w = os2.usWeightClass if os2 else 400
            it = bool(f["head"].macStyle & 2)
            score = abs(w - weight) + (0 if it == italic else 500)
            if score < best_score:
                best, best_i, best_score = f, i, score
        return best, best_i
    return TTFont(str(path)), 0


def resolve_font(name: str, weight: int, italic: bool, axes: dict | None) -> tuple[Path, TTFont, int, str]:
    """Returns (path, TTFont, face_index, source)."""
    p = Path(name).expanduser()
    if p.exists():
        src = "file"
    else:
        p = google_font(name, weight, italic)
        src = "google-fonts"
        if p is None:
            p = system_font(name, weight, italic)
            src = "system"
        if p is None:
            sys.exit(f"error: font '{name}' not found as a file, on Google Fonts, or installed. "
                     f"Try `--list-fonts` for curated choices.")
    font, idx = open_font(p, weight, italic)
    if "fvar" in font and src != "google-fonts":
        want = dict(axes or {})
        want.setdefault("wght", weight)
        FONT_CACHE.mkdir(parents=True, exist_ok=True)
        dest = FONT_CACHE / f"{_slug(p.stem)}-{'-'.join(f'{k}{int(v)}' for k, v in sorted(want.items()))}.ttf"
        if not dest.exists():
            instance_variable(p, want, dest)
        p, font, idx = dest, TTFont(str(dest)), 0
    elif axes and "fvar" in font:
        dest = FONT_CACHE / f"{_slug(p.stem)}-{'-'.join(f'{k}{int(v)}' for k, v in sorted(axes.items()))}.ttf"
        if not dest.exists():
            instance_variable(p, axes, dest)
        p, font, idx = dest, TTFont(str(dest)), 0
    return p, font, idx, src


def font_metrics(font: TTFont) -> dict:
    upem = font["head"].unitsPerEm
    os2 = font["OS/2"] if "OS/2" in font else None
    cap = getattr(os2, "sCapHeight", 0) if os2 else 0
    xh = getattr(os2, "sxHeight", 0) if os2 else 0
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()

    def glyph_height(ch):
        gid = cmap.get(ord(ch))
        if not gid:
            return 0
        bp = BoundsPen(gs)
        gs[gid].draw(bp)
        return bp.bounds[3] if bp.bounds else 0

    if not cap:
        cap = glyph_height("H") or glyph_height("ה") or glyph_height("0") or int(upem * 0.7)
    if not xh:
        xh = glyph_height("x") or int(cap * 0.72)
    names = {}
    if "name" in font:
        for nid in (1, 2, 4, 5, 13, 14, 16, 17):
            rec = font["name"].getDebugName(nid)
            if rec:
                names[nid] = rec
    return {"upem": upem, "cap_height": cap, "x_height": xh,
            "ascender": font["hhea"].ascent, "descender": font["hhea"].descent,
            "family": names.get(16) or names.get(1, ""), "style": names.get(17) or names.get(2, ""),
            "version": names.get(5, ""), "license": (names.get(13) or "")[:200], "license_url": names.get(14, ""),
            "weight_class": getattr(os2, "usWeightClass", None) if os2 else None,
            "has_gpos": "GPOS" in font, "has_kern": "kern" in font, "variable": "fvar" in font,
            "glyph_count": len(font.getGlyphOrder())}


# ---------------------------------------------------------------- shaping
RTL_RANGES = [(0x0590, 0x08FF), (0xFB1D, 0xFDFF), (0xFE70, 0xFEFF)]


def is_rtl_text(s: str) -> bool:
    strong = [c for c in s if unicodedata.bidirectional(c) in ("L", "R", "AL")]
    return bool(strong) and unicodedata.bidirectional(strong[0]) in ("R", "AL")


def shape_line(font_path: Path, face_index: int, text: str, features: dict, direction: str, language: str | None):
    blob = hb.Blob.from_file_path(str(font_path))
    face = hb.Face(blob, face_index)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if direction in ("ltr", "rtl"):
        buf.direction = direction
    if language:
        buf.language = language
    hb.shape(font, buf, features)
    out = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append({"gid": info.codepoint, "cluster": info.cluster, "x_advance": pos.x_advance,
                    "y_advance": pos.y_advance, "x_offset": pos.x_offset, "y_offset": pos.y_offset})
    return out, buf.direction


def apply_case(text: str, mode: str) -> str:
    if mode == "upper":
        return text.upper()
    if mode == "lower":
        return text.lower()
    if mode == "title":
        return " ".join(w[:1].upper() + w[1:] for w in text.split(" "))
    return text


# ------------------------------------------------------------------- main
def build(args) -> tuple[str, dict]:
    axes = {}
    if args.axes:
        for part in args.axes.split(","):
            k, v = part.split("=")
            axes[k.strip()] = float(v)
    path, font, idx, source = resolve_font(args.font, args.weight, args.italic, axes or None)
    m = font_metrics(font)
    upem = m["upem"]
    gs = font.getGlyphSet()
    order = font.getGlyphOrder()

    features = {"kern": True, "liga": True, "calt": True}
    if args.features:
        for f in args.features.split(","):
            f = f.strip()
            if f.startswith("-"):
                features[f[1:]] = False
            elif f:
                features[f] = True

    lines = [apply_case(t, args.case) for t in re.split(r"\||\\n|\n", args.text)]
    rtl_doc = args.direction == "rtl" or (args.direction == "auto" and is_rtl_text(lines[0]))
    align = args.align or ("right" if rtl_doc else "left")

    # scale: user units per font unit
    if args.font_size:
        scale = args.font_size / upem
        size_mode = "em"
    else:
        scale = args.cap_height / m["cap_height"]
        size_mode = "cap"
    tracking_units = args.tracking / 1000 * upem  # 1/1000 em → font units
    word_space = args.word_space

    glyphs_out = []  # dicts with d (already transformed into user space, baseline at y=0 of its line)
    line_infos = []
    y_line = 0.0
    leading = args.leading * args.cap_height if not args.font_size else args.leading * args.font_size * 0.7
    space_gid = font.getBestCmap().get(ord(" "))

    for li, line in enumerate(lines):
        shaped, direction = shape_line(path, idx, line, features, args.direction, args.language)
        x = 0.0
        items = []
        for g in shaped:
            name = order[g["gid"]] if g["gid"] < len(order) else None
            adv = g["x_advance"]
            if space_gid is not None and g["gid"] == space_gid:
                adv *= word_space
            items.append((name, x + g["x_offset"], g["y_offset"], adv, g["cluster"]))
            x += adv + tracking_units
        width_units = x - tracking_units if items else 0
        line_infos.append({"text": line, "direction": direction, "width": width_units * scale, "items": items,
                           "y": y_line})
        y_line += leading

    total_w = max(l["width"] for l in line_infos) if line_infos else 0
    for l in line_infos:
        if align == "center":
            dx = (total_w - l["width"]) / 2
        elif align == "right":
            dx = total_w - l["width"]
        else:
            dx = 0.0
        for name, gx, gy, adv, cluster in l["items"]:
            if name is None or name not in gs:
                continue
            # font units → user units; flip y; place at (dx + gx*scale, line baseline)
            t = Identity.translate(dx + gx * scale, l["y"] - gy * scale).scale(scale, -scale)
            sp = SVGPathPen(gs, ntos=lambda v: fmt(v, 3))
            gs[name].draw(TransformPen(sp, t))
            bp = BoundsPen(gs)
            gs[name].draw(TransformPen(bp, t))
            d = sp.getCommands()
            if not d:
                continue
            ch = l["text"][cluster] if cluster < len(l["text"]) else ""
            glyphs_out.append({"d": d, "name": name, "char": ch, "bounds": bp.bounds, "line": l["text"]})

    if not glyphs_out:
        sys.exit("error: nothing was drawn (empty text or font lacks these glyphs)")

    xs0 = min(g["bounds"][0] for g in glyphs_out)
    ys0 = min(g["bounds"][1] for g in glyphs_out)
    xs1 = max(g["bounds"][2] for g in glyphs_out)
    ys1 = max(g["bounds"][3] for g in glyphs_out)
    pad = args.padding * (args.cap_height if size_mode == "cap" else (ys1 - ys0))
    # shift so the viewBox starts at 0,0
    shift_x, shift_y = -(xs0 - pad), -(ys0 - pad)
    vb_w, vb_h = (xs1 - xs0) + 2 * pad, (ys1 - ys0) + 2 * pad
    baselines = [l["y"] + shift_y for l in line_infos]
    cap_px = m["cap_height"] * scale
    xh_px = m["x_height"] * scale

    def shifted(d):
        from fontTools.pens.recordingPen import RecordingPen  # local import to keep startup light
        from fontTools.svgLib.path.parser import parse_path
        rec = RecordingPen()
        parse_path(d, rec)
        out = SVGPathPen(None, ntos=lambda v: fmt(v, 3))
        rec.replay(TransformPen(out, Identity.translate(shift_x, shift_y)))
        return out.getCommands()

    paths = []
    for i, g in enumerate(glyphs_out):
        paths.append((shifted(g["d"]), g))

    fill = args.fill
    attrs = (f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(vb_w)} {fmt(vb_h)}" '
             f'role="img" aria-label="{xml_escape(args.text.replace("|", " "))}" '
             f'data-font="{xml_escape(m["family"] or Path(path).stem)}" data-weight="{args.weight}" '
             f'data-baseline="{fmt(baselines[0])}" data-baselines="{" ".join(fmt(b) for b in baselines)}" '
             f'data-cap-height="{fmt(cap_px)}" data-x-height="{fmt(xh_px)}" data-tracking="{args.tracking}" '
             f'data-direction="{"rtl" if rtl_doc else "ltr"}"')
    if args.merge:
        body = f'  <path id="wordmark" fill="{fill}" d="{" ".join(d for d, _ in paths)}"/>\n'
    else:
        body = f'  <g id="wordmark" fill="{fill}">\n'
        for i, (d, g) in enumerate(paths):
            body += f'    <path id="g{i}" data-char="{xml_escape(g["char"])}" d="{d}"/>\n'
        body += "  </g>\n"
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           f"<svg {attrs}>\n"
           f'  <title>{xml_escape(args.text.replace("|", " "))}</title>\n'
           f"{body}</svg>\n")

    info = {
        "font_file": str(path), "font_source": source, "family": m["family"], "style": m["style"],
        "license": m["license"], "license_url": m["license_url"], "weight": args.weight, "variable_source": m["variable"],
        "license_catalog": LAST_CATALOG.get("license_family", ""),
        "has_gpos": m["has_gpos"], "upem": upem, "scale": scale, "size_mode": size_mode,
        "viewBox": [0, 0, round(vb_w, 3), round(vb_h, 3)], "baselines": [round(b, 3) for b in baselines],
        "cap_height": round(cap_px, 3), "x_height": round(xh_px, 3), "ink_width": round(xs1 - xs0, 3),
        "ink_height": round(ys1 - ys0, 3), "glyphs": [{"char": g["char"], "glyph": g["name"],
                                                       "bounds": [round(v + (shift_x if k % 2 == 0 else shift_y), 2)
                                                                  for k, v in enumerate(g["bounds"])]}
                                                      for g in glyphs_out],
        "direction": "rtl" if rtl_doc else "ltr", "lines": [l["text"] for l in line_infos],
    }
    return svg, info


def xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def list_fonts(filt: str | None) -> None:
    data = json.loads((skill_dir() / "assets" / "fonts.json").read_text(encoding="utf-8"))
    for group in data["groups"]:
        rows = [f for f in group["fonts"] if not filt or filt.lower() in json.dumps(f).lower()
                or filt.lower() in group["name"].lower()]
        if not rows:
            continue
        print(f"\n## {group['name']} — {group['voice']}")
        for f in rows:
            scripts = ", ".join(f.get("scripts", ["Latin"]))
            print(f"- {f['family']} ({f.get('license', 'OFL')}; {scripts}) — {f.get('note', '')}")
    print("\nAll of these are free to use in a logo without attribution. Outlined artwork stays yours; "
          "redistributing a modified *font file* is what OFL/Apache terms restrict.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", help="text to set; '|' or '\\n' starts a new line")
    ap.add_argument("--font", default="Inter", help="font file, Google Fonts family, or installed family")
    ap.add_argument("--weight", type=int, default=700)
    ap.add_argument("--italic", action="store_true")
    ap.add_argument("--axes", help='variable axes, e.g. "wght=650,wdth=95"')
    ap.add_argument("--cap-height", type=float, default=100.0, help="cap height in user units (default 100)")
    ap.add_argument("--font-size", type=float, help="em size in user units (overrides --cap-height)")
    ap.add_argument("--tracking", type=float, default=0.0, help="letter-spacing in 1/1000 em (e.g. 40, -10)")
    ap.add_argument("--word-space", type=float, default=1.0, help="multiply the space advance (default 1.0)")
    ap.add_argument("--leading", type=float, default=1.3, help="line distance as multiple of cap height")
    ap.add_argument("--case", choices=["none", "upper", "lower", "title"], default="none")
    ap.add_argument("--align", choices=["left", "center", "right"], help="multi-line alignment (default by direction)")
    ap.add_argument("--direction", choices=["auto", "ltr", "rtl"], default="auto")
    ap.add_argument("--language", help="BCP-47 tag for shaping (he, ar, tr, ...)")
    ap.add_argument("--features", help="OpenType features: 'ss01,-liga,smcp' (prefix - disables)")
    ap.add_argument("--fill", default="#000000")
    ap.add_argument("--padding", type=float, default=0.05, help="padding as a fraction of cap height")
    ap.add_argument("--merge", action="store_true", help="one path for the whole wordmark")
    ap.add_argument("--out", help="output SVG path (default: stdout)")
    ap.add_argument("--json", action="store_true", help="print metrics JSON to stdout (SVG then goes to --out)")
    ap.add_argument("--list-fonts", nargs="?", const="", metavar="FILTER", help="show curated typefaces")
    ap.add_argument("--font-info", metavar="FONT", help="print metrics + licence for a font and exit")
    a = ap.parse_args()

    if a.list_fonts is not None:
        list_fonts(a.list_fonts or None)
        return
    if a.font_info:
        p, f, idx, src = resolve_font(a.font_info, a.weight, a.italic, None)
        info = font_metrics(f)
        info["file"] = str(p)
        info["source"] = src
        info["license_catalog"] = LAST_CATALOG.get("license_family", "")
        if src == "system":
            info["license_note"] = ("Installed font: its EULA governs logo use. Apple's San Francisco family is "
                                    "not licensed for logos; Helvetica/Arial on macOS and Windows are OS-licensed, "
                                    "check the vendor's terms before shipping a wordmark drawn from them.")
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return
    if not a.text:
        ap.error("--text is required")
    svg, info = build(a)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(svg, encoding="utf-8")
        if not a.json:
            print(f"wrote {a.out}  ({info['family']} {a.weight}, {info['font_source']}; cap {info['cap_height']}, "
                  f"baseline {info['baselines'][0]}, {len(info['glyphs'])} glyphs)")
    if a.json:
        print(json.dumps(info, indent=2, ensure_ascii=False))
    elif not a.out:
        sys.stdout.write(svg)


if __name__ == "__main__":
    main()
