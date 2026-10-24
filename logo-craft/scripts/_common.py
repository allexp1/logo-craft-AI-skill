#!/usr/bin/env python3
"""Shared helpers for the logo-craft scripts.

Everything here is standard library. Optional third-party modules (fontTools,
uharfbuzz, Pillow, cairosvg) are bootstrapped on demand into a private venv at
~/.cache/logo-craft/venv so the user's system Python is never touched.
"""
from __future__ import annotations

import colorsys
import math
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

CACHE_DIR = Path(os.environ.get("LOGO_CRAFT_CACHE", Path.home() / ".cache" / "logo-craft"))
VENV_DIR = Path(os.environ.get("LOGO_CRAFT_VENV", CACHE_DIR / "venv"))

# import name -> pip name
PIP_NAMES = {
    "fontTools": "fonttools",
    "PIL": "pillow",
    "uharfbuzz": "uharfbuzz",
    "cairosvg": "cairosvg",
    "brotli": "brotli",
    "pathops": "skia-pathops",
}


# ---------------------------------------------------------------- bootstrap
def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_deps(*modules: str) -> None:
    """Make sure `modules` import. If one is missing, create/upgrade the private
    venv and re-exec this script inside it. Set LOGO_CRAFT_NO_BOOTSTRAP=1 to
    disable (the script then fails with a clear message)."""
    missing = []
    for m in modules:
        try:
            __import__(m)
        except ImportError:
            missing.append(m)
    if not missing:
        return
    if os.environ.get("LOGO_CRAFT_NO_BOOTSTRAP") or os.environ.get("LOGO_CRAFT_IN_VENV"):
        pips = " ".join(PIP_NAMES.get(m, m) for m in missing)
        sys.exit(f"error: missing Python modules {missing}. Install with: pip install {pips}")
    py = venv_python()
    env = dict(os.environ, LOGO_CRAFT_IN_VENV="1")
    if py.exists():
        # The venv usually already has everything: re-exec quietly if so.
        probe = subprocess.run([str(py), "-c", "import " + ",".join(missing)],
                               capture_output=True)
        if probe.returncode == 0:
            os.execve(str(py), [str(py), *sys.argv], env)
    else:
        print(f"[logo-craft] creating a private venv at {VENV_DIR} (one time)", file=sys.stderr)
        VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    pips = [PIP_NAMES.get(m, m) for m in missing]
    print(f"[logo-craft] installing {' '.join(pips)} into {VENV_DIR} (one time)", file=sys.stderr)
    r = subprocess.run([str(py), "-m", "pip", "install", "--quiet", *pips])
    if r.returncode != 0:
        sys.exit(f"error: could not install {pips} into {VENV_DIR}")
    os.execve(str(py), [str(py), *sys.argv], env)


# --------------------------------------------------------------------- svg
def q(tag: str) -> str:
    """Qualified SVG tag name for ElementTree."""
    return f"{{{SVG_NS}}}{tag}"


def local(tag: str) -> str:
    return tag.split("}", 1)[1] if "}" in tag else tag


def read_svg(path: str | Path) -> tuple[ET.ElementTree, ET.Element]:
    tree = ET.parse(str(path))
    return tree, tree.getroot()


_ANIM_TAGS = {"animate", "set", "animatetransform", "animatemotion", "animatecolor", "discard", "mpath"}
UNSAFE_TAGS = {"script", "foreignobject", "iframe", "embed", "object", "audio", "video", "handler", "listener"} | _ANIM_TAGS
_EXTERNAL_REF_TAGS = {"use", "image", "feimage", "mpath", "textpath", "tref"}
_SAFE_DATA_URI = re.compile(r"^data:image/(png|jpe?g|gif|webp)[;,]", re.I)

# CSS allow-list. A logo never needs more than paint, geometry and the one
# dark-mode media query the favicon exporter writes. Everything else (escapes,
# quotes, @import, unknown properties or functions, external url()) fails the
# whole style, which is then dropped. Presentation attributes are CSS-parsed by
# browsers too, so their values go through the same value rule.
_CSS_PROPS = {
    "fill", "fill-opacity", "fill-rule", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin",
    "stroke-miterlimit", "stroke-dasharray", "stroke-dashoffset", "stroke-opacity", "opacity", "color",
    "display", "visibility", "paint-order", "mix-blend-mode", "isolation", "shape-rendering",
    "vector-effect", "transform", "transform-origin", "transform-box", "clip-rule", "clip-path", "mask",
    "filter", "stop-color", "stop-opacity", "flood-color", "flood-opacity", "lighting-color",
    "color-interpolation", "color-interpolation-filters", "font-family", "font-size", "font-weight",
    "font-style", "letter-spacing", "text-anchor", "dominant-baseline", "overflow", "pointer-events",
}
_CSS_FUNCS = {"url", "rgb", "rgba", "hsl", "hsla", "oklch", "oklab", "lab", "lch", "color", "var",
              "translate", "translatex", "translatey", "scale", "scalex", "scaley", "rotate", "skewx", "skewy", "matrix"}
_CSS_VALUE_OK = re.compile(r"^[-\w\s#.%,/()!]*$")       # no quotes, backslashes, colons, semicolons, braces, angle brackets, '@'
_CSS_FUNC_RE = re.compile(r"([A-Za-z-]+)\s*\(")
_CSS_URL_RE = re.compile(r"url\s*\(", re.I)
_CSS_URL_ID_RE = re.compile(r"url\s*\(\s*#[\w:.-]+\s*\)", re.I)
_CSS_MEDIA_RE = re.compile(r"^\s*\(\s*prefers-color-scheme\s*:\s*(dark|light)\s*\)\s*$", re.I)
_CSS_SELECTOR_RE = re.compile(r"^[\w\s.#*:>,+~-]+$")   # no parens, braces, quotes, '@' or '/'
_CSS_FORBIDDEN = "\\\"'<&"


def css_value_is_safe(value: str) -> bool:
    """One CSS value (or presentation-attribute value): plain tokens, known
    functions with balanced parentheses, url() only to a same-document id."""
    if not value or not _CSS_VALUE_OK.match(value) or value.count("(") != value.count(")"):
        return False
    for f in _CSS_FUNC_RE.findall(value):
        if f.lower() not in _CSS_FUNCS:
            return False
    return len(_CSS_URL_RE.findall(value)) == len(_CSS_URL_ID_RE.findall(value))


class _CssCursor:
    def __init__(self, text: str):
        self.t, self.i = text, 0

    def ws(self) -> None:
        while self.i < len(self.t) and self.t[self.i].isspace():
            self.i += 1

    def eat(self, s: str) -> bool:
        if self.t.startswith(s, self.i):
            self.i += len(s)
            return True
        return False

    def until(self, stops: str) -> str:
        j = self.i
        while j < len(self.t) and self.t[j] not in stops:
            j += 1
        out, self.i = self.t[self.i:j], j
        return out

    def done(self) -> bool:
        return self.i >= len(self.t)


def _css_declarations(c: _CssCursor) -> list[str] | None:
    """Parse `prop: value;`* up to and including the closing brace. None on
    anything outside the allow-list, a missing brace or a stray character."""
    out: list[str] = []
    while True:
        c.ws()
        if c.eat("}"):
            return out
        if c.done():
            return None
        prop = c.until(":;{}").strip()
        if not c.eat(":"):
            return None
        val = c.until(";{}").strip()
        c.eat(";")
        if prop.lower() not in _CSS_PROPS or not css_value_is_safe(val):
            return None
        out.append(f"{prop.lower()}: {val}")


def _css_rules(c: _CssCursor, nested: bool) -> list[str] | None:
    out: list[str] = []
    while True:
        c.ws()
        if c.done():
            return None if nested else out
        if nested and c.eat("}"):
            return out
        if c.eat("@"):
            if nested or not c.eat("media"):
                return None
            cond = c.until("{;}")
            m = _CSS_MEDIA_RE.match(cond)
            if not m or not c.eat("{"):
                return None
            inner = _css_rules(c, nested=True)
            if inner is None:
                return None
            out.append(f"@media (prefers-color-scheme: {m.group(1).lower()}) {{ {' '.join(inner)} }}")
            continue
        sel = c.until("{;}")
        if not _CSS_SELECTOR_RE.match(sel) or not c.eat("{"):
            return None
        decls = _css_declarations(c)
        if decls is None:
            return None
        out.append(f"{' '.join(sel.split())} {{ {'; '.join(decls)} }}")


def css_rebuild(text: str) -> str | None:
    """Parse a style sheet with the tiny grammar a logo may carry (rules of
    allow-listed declarations, plus `@media (prefers-color-scheme: …)` blocks
    of such rules) and return it re-serialised from the parsed parts. None
    when anything falls outside: the caller drops the style sheet whole. The
    output never contains text that was not parsed, so unbalanced braces,
    comments and stray tokens cannot smuggle a declaration past the check."""
    if any(ch in text for ch in _CSS_FORBIDDEN) or "/*" in text:
        return None
    rules = _css_rules(_CssCursor(text), nested=False)
    return None if rules is None else " ".join(rules)


def css_rebuild_declarations(text: str) -> str | None:
    """Same for a style attribute body (declarations only)."""
    if any(ch in text for ch in _CSS_FORBIDDEN) or "/*" in text or "{" in text or "}" in text:
        return None
    c = _CssCursor(text + "}")
    decls = _css_declarations(c)
    return None if decls is None or not c.done() else "; ".join(decls)


def css_is_safe(text: str) -> bool:
    """True when `text` parses as a style sheet under the allow-list."""
    return css_rebuild(text) is not None


def _safe_href(v: str) -> bool:
    v = (v or "").strip()
    return v.startswith("#") or bool(_SAFE_DATA_URI.match(v))


def _clean_attrs(el: ET.Element, removed: list[str]) -> bool:
    """Strip unsafe attributes from one element. Returns True when the element
    itself has to go (a <use>/<image> whose only purpose was an external ref).
    Names are compared lower-cased: the HTML parser lower-cases inline SVG."""
    tag = local(el.tag).lower()
    drop = False
    for a in list(el.attrib):
        la = local(a).lower()
        v = el.get(a) or ""
        if la.startswith("on"):
            del el.attrib[a]; removed.append(f"@{la}")
        elif la == "href":  # any namespace or prefix
            if not _safe_href(v):
                del el.attrib[a]; removed.append(f"@{la} external")
                drop = tag in _EXTERNAL_REF_TAGS
        elif la == "style":
            nv = css_rebuild_declarations(v)
            if nv is None:
                del el.attrib[a]; removed.append("@style")
            elif nv != v:
                el.set(a, nv)
        elif la in _CSS_PROPS:
            if not css_value_is_safe(v):
                del el.attrib[a]; removed.append(f"@{la}")
        elif "\\" in v or (_CSS_URL_RE.search(v) and not css_value_is_safe(v)):
            del el.attrib[a]; removed.append(f"@{la}")
    return drop


def sanitize_svg(root: ET.Element) -> list[str]:
    """Remove active or external content from an SVG tree, in place. A logo is
    paths and paint, so the rule is an allow-list: no scripts, foreignObject
    or SMIL animation; no event handlers; hrefs only to same-document ids or
    inline PNG/JPEG/GIF/WebP data; CSS (style sheets, style attributes and
    presentation attributes) only from a small set of paint and geometry
    properties with url() to same-document ids, re-serialised from the parsed
    parts, else the style goes whole. Anything we render or embed may come
    from elsewhere. Returns a list
    describing what was removed (empty = already clean)."""
    removed: list[str] = []
    _clean_attrs(root, removed)

    def walk(parent: ET.Element) -> None:
        for child in list(parent):
            tag = local(child.tag).lower()
            if tag in UNSAFE_TAGS:
                parent.remove(child); removed.append(f"<{tag}>"); continue
            if tag == "style":
                nv = None if len(child) else css_rebuild("".join(child.itertext()))
                if nv is None:
                    parent.remove(child); removed.append("<style>"); continue
                child.text = nv  # only what was parsed is written back
            if _clean_attrs(child, removed):
                parent.remove(child); removed.append(f"<{tag} external>"); continue
            walk(child)

    walk(root)
    return removed


def safe_copy_for_render(svg_path: str) -> str | None:
    """If the file holds anything sanitize_svg would remove, write a cleaned
    copy to a temp file and return its path (caller deletes it); else None.
    A file ElementTree cannot parse is refused outright: a lenient renderer
    might still draw it, and then we would have checked nothing."""
    try:
        tree, root = read_svg(svg_path)
    except ET.ParseError as e:
        raise ValueError(f"{Path(svg_path).name}: not well-formed XML ({e}); refusing to render a file that cannot be checked") from None
    removed = sanitize_svg(root)
    if not removed:
        return None
    import tempfile
    fd, tmp = tempfile.mkstemp(suffix=".svg", prefix="logo-craft-safe-")
    os.close(fd)
    Path(tmp).write_text(svg_to_string(root), encoding="utf-8")
    print(f"note: rendering a cleaned copy of {Path(svg_path).name}; removed {', '.join(sorted(set(removed)))}", file=sys.stderr)
    return tmp


def read_svg_clean(path: str) -> ET.Element:
    """read_svg + sanitize_svg: the root of `path` with active or external
    content removed, warning on stderr about what went. Use it for every file
    whose children end up inside a deliverable."""
    _, root = read_svg(path)
    removed = sanitize_svg(root)
    if removed:
        print(f"warning: {Path(path).name}: removed active or external content ({', '.join(sorted(set(removed)))}). "
              "The output is clean; fix the master too.", file=sys.stderr)
    return root


_IM_POLICY = """<policymap>
  <policy domain="coder" rights="none" pattern="MSL"/>
  <policy domain="coder" rights="none" pattern="TEXT"/>
  <policy domain="coder" rights="none" pattern="URL"/>
  <policy domain="coder" rights="none" pattern="HTTPS"/>
  <policy domain="coder" rights="none" pattern="HTTP"/>
  <policy domain="coder" rights="none" pattern="FTP"/>
  <policy domain="coder" rights="none" pattern="EPHEMERAL"/>
  <policy domain="coder" rights="none" pattern="SHOW"/>
  <policy domain="coder" rights="none" pattern="WIN"/>
  <policy domain="coder" rights="none" pattern="PS"/>
  <policy domain="coder" rights="none" pattern="PS2"/>
  <policy domain="coder" rights="none" pattern="PS3"/>
  <policy domain="coder" rights="none" pattern="EPS"/>
  <policy domain="coder" rights="none" pattern="PDF"/>
  <policy domain="coder" rights="none" pattern="XPS"/>
  <policy domain="path" rights="none" pattern="@*"/>
  <policy domain="delegate" rights="none" pattern="show"/>
  <policy domain="delegate" rights="none" pattern="win"/>
  <policy domain="delegate" rights="none" pattern="edit"/>
  <policy domain="delegate" rights="none" pattern="print"/>
  <policy domain="delegate" rights="none" pattern="https"/>
  <policy domain="delegate" rights="none" pattern="http"/>
  <policy domain="delegate" rights="none" pattern="ftp"/>
  <policy domain="resource" name="memory" value="512MiB"/>
  <policy domain="resource" name="time" value="60"/>
</policymap>
"""


def imagemagick_env() -> dict:
    """Environment for ImageMagick with a restrictive policy on top of the
    system one: no MSL/MVG/TEXT/URL/PostScript coders, no indirect @file
    reads, no network or display delegates. The SVG delegate (inkscape or
    librsvg, whichever the build uses) stays, since it only ever sees the
    sanitised copy."""
    d = CACHE_DIR / "imagemagick-policy"
    d.mkdir(parents=True, exist_ok=True)
    pol = d / "policy.xml"
    if not pol.exists() or pol.read_text() != _IM_POLICY:
        pol.write_text(_IM_POLICY)
    env = dict(os.environ)
    env["MAGICK_CONFIGURE_PATH"] = str(d) + (os.pathsep + env["MAGICK_CONFIGURE_PATH"] if env.get("MAGICK_CONFIGURE_PATH") else "")
    return env


def svg_to_string(root: ET.Element) -> str:
    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"


def write_svg(root: ET.Element, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(svg_to_string(root), encoding="utf-8")


_LEN = re.compile(r"^\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*(px|pt|mm|cm|in)?\s*$")


def parse_length(v: str | None) -> float | None:
    if v is None:
        return None
    m = _LEN.match(v)
    if not m:
        return None
    n = float(m.group(1))
    unit = m.group(2)
    scale = {None: 1, "px": 1, "pt": 4 / 3, "mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96}[unit]
    return n * scale


def get_viewbox(root: ET.Element) -> tuple[float, float, float, float]:
    vb = root.get("viewBox")
    if vb:
        parts = [float(x) for x in re.split(r"[\s,]+", vb.strip()) if x]
        if len(parts) == 4:
            return tuple(parts)  # type: ignore[return-value]
    w = parse_length(root.get("width")) or 100.0
    h = parse_length(root.get("height")) or 100.0
    return (0.0, 0.0, w, h)


def set_viewbox(root: ET.Element, x: float, y: float, w: float, h: float, keep_size: bool = False) -> None:
    root.set("viewBox", f"{fmt(x)} {fmt(y)} {fmt(w)} {fmt(h)}")
    if not keep_size:
        for a in ("width", "height"):
            if a in root.attrib:
                del root.attrib[a]


def fmt(n: float, places: int = 3) -> str:
    s = f"{n:.{places}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


PAINT_ATTRS = ("fill", "stroke")


def iter_paint(root: ET.Element):
    """Yield (element, attribute, value) for every fill/stroke, including those
    inside style="" attributes."""
    for el in root.iter():
        for a in PAINT_ATTRS:
            v = el.get(a)
            if v is not None:
                yield el, a, v
        style = el.get("style")
        if style:
            for part in style.split(";"):
                if ":" in part:
                    k, v = part.split(":", 1)
                    if k.strip() in PAINT_ATTRS:
                        yield el, "style:" + k.strip(), v.strip()


def recolor(root: ET.Element, color: str, *, keep_none: bool = True) -> ET.Element:
    """Set every fill and stroke to `color` (fill='none' is kept so cut-outs and
    stroke-only shapes keep their nature). Gradients are replaced by the flat
    colour. Returns the same root."""
    for el in list(root.iter()):
        tag = local(el.tag)
        if tag in ("linearGradient", "radialGradient", "pattern"):
            continue
        for a in PAINT_ATTRS:
            v = el.get(a)
            if v is None:
                continue
            if keep_none and v.strip() == "none":
                continue
            el.set(a, color)
        style = el.get("style")
        if style:
            parts = []
            for part in style.split(";"):
                if ":" in part:
                    k, v = part.split(":", 1)
                    if k.strip() in PAINT_ATTRS and not (keep_none and v.strip() == "none"):
                        part = f"{k.strip()}:{color}"
                parts.append(part)
            el.set("style", ";".join(p for p in parts if p))
    # Elements with no explicit fill inherit black; make the intent explicit.
    for el in root.iter():
        tag = local(el.tag)
        if tag in ("path", "circle", "ellipse", "rect", "polygon", "polyline", "line", "text"):
            if el.get("fill") is None and not (el.get("style") and "fill:" in el.get("style", "")):
                # a shape with a stroke but no fill attribute still renders a black fill
                if tag not in ("line", "polyline"):
                    el.set("fill", color)
    return root


# ------------------------------------------------------------------ colour
_HEX = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def parse_hex(s: str) -> tuple[int, int, int]:
    m = _HEX.match(s.strip())
    if not m:
        raise ValueError(f"not a hex colour: {s!r}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (max(0, min(255, int(round(c)))) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    v = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return v * 255.0


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (srgb_to_linear(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return (linear_to_srgb(r), linear_to_srgb(g), linear_to_srgb(bb))


def oklab_to_oklch(lab):
    L, a, b = lab
    c = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360
    return (L, c, h)


def oklch_to_oklab(lch):
    L, c, h = lch
    return (L, c * math.cos(math.radians(h)), c * math.sin(math.radians(h)))


def rgb_to_oklch(rgb):
    return oklab_to_oklch(rgb_to_oklab(rgb))


def oklch_to_rgb(lch):
    return oklab_to_rgb(oklch_to_oklab(lch))


def in_gamut(rgb) -> bool:
    return all(-0.5 <= c <= 255.5 for c in rgb)


def oklch_to_rgb_clamped(lch):
    """Reduce chroma until the colour fits sRGB (keeps hue and lightness)."""
    L, c, h = lch
    for _ in range(40):
        rgb = oklch_to_rgb((L, c, h))
        if in_gamut(rgb):
            return rgb
        c *= 0.92
    return oklch_to_rgb((L, 0, h))


# Machado, Oliveira & Fernandes (2009) matrices at severity 1.0, linear RGB.
CVD_MATRICES = {
    "protanopia": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritanopia": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def simulate_cvd(rgb: tuple[int, int, int], kind: str) -> tuple[float, float, float]:
    m = CVD_MATRICES[kind]
    lin = [srgb_to_linear(c) for c in rgb]
    out = [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]
    return tuple(linear_to_srgb(c) for c in out)  # type: ignore[return-value]


def delta_e_ok(rgb1, rgb2) -> float:
    """Euclidean distance in OKLab (×100 to resemble classic ΔE scale)."""
    a, b = rgb_to_oklab(rgb1), rgb_to_oklab(rgb2)
    return 100 * math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def rgb_to_cmyk(rgb) -> tuple[int, int, int, int]:
    r, g, b = (c / 255 for c in rgb)
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return tuple(int(round(x * 100)) for x in (c, m, y, k))  # type: ignore[return-value]


def rgb_to_hsl(rgb):
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    return (round(h * 360), round(s * 100), round(l * 100))


# --------------------------------------------------------------- rendering
def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def available_renderers() -> list[str]:
    out = []
    if _have("rsvg-convert"):
        out.append("rsvg-convert")
    if _have("resvg"):
        out.append("resvg")
    try:
        import cairosvg  # noqa: F401
        out.append("cairosvg")
    except Exception:
        pass
    if _have("inkscape"):
        out.append("inkscape")
    if _have("magick") or _have("convert"):
        out.append("imagemagick")
    for c in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        if _have(c):
            out.append(c)
            break
    mac_chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(mac_chrome):
        out.append("chrome-mac")
    return out


def render_png(svg_path: str | Path, png_path: str | Path, width: int, height: int | None = None,
               background: str | None = None, renderer: str | None = None) -> str:
    """Render an SVG to PNG at the given pixel size (transparent unless
    `background` is given). Returns the renderer used."""
    svg_path, png_path = str(svg_path), str(png_path)
    Path(png_path).parent.mkdir(parents=True, exist_ok=True)
    height = height or width
    options = [renderer] if renderer else available_renderers()
    if not options:
        raise RuntimeError(
            "no SVG renderer found. Install one: `brew install librsvg` (rsvg-convert), "
            "`pip install cairosvg`, resvg, Inkscape or ImageMagick."
        )
    errors = []
    cleaned = safe_copy_for_render(svg_path)
    if cleaned:
        svg_path = cleaned
    try:
        return _render_png_inner(svg_path, png_path, width, height, background, options, errors)
    finally:
        if cleaned:
            try:
                os.unlink(cleaned)
            except OSError:
                pass


def _render_png_inner(svg_path, png_path, width, height, background, options, errors) -> str:
    for r in options:
        try:
            if r == "rsvg-convert":
                cmd = ["rsvg-convert", "-w", str(width), "-h", str(height), "--keep-aspect-ratio", "-o", png_path]
                if background:
                    cmd += ["-b", background]
                cmd.append(svg_path)
                subprocess.run(cmd, check=True, capture_output=True)
            elif r == "resvg":
                cmd = ["resvg", "-w", str(width), "-h", str(height)]
                if background:
                    cmd += ["--background", background]
                cmd += [svg_path, png_path]
                subprocess.run(cmd, check=True, capture_output=True)
            elif r == "cairosvg":
                import cairosvg
                cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width, output_height=height,
                                 background_color=background)
            elif r == "inkscape":
                cmd = ["inkscape", svg_path, "--export-type=png", f"--export-filename={png_path}",
                       f"--export-width={width}", f"--export-height={height}"]
                if background:
                    cmd += [f"--export-background={background}", "--export-background-opacity=1"]
                subprocess.run(cmd, check=True, capture_output=True)
            elif r == "imagemagick":
                exe = "magick" if _have("magick") else "convert"
                cmd = [exe, "-background", background or "none", "-density", "384", "svg:" + svg_path,
                       "-resize", f"{width}x{height}", "-gravity", "center", "-extent", f"{width}x{height}", "png32:" + png_path]
                subprocess.run(cmd, check=True, capture_output=True, env=imagemagick_env())
            elif r in ("chrome-mac", "google-chrome", "chromium", "chromium-browser", "chrome"):
                exe = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" if r == "chrome-mac" else r
                cmd = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                       f"--window-size={width},{height}", f"--screenshot={png_path}", f"file://{os.path.abspath(svg_path)}"]
                subprocess.run(cmd, check=True, capture_output=True)
            else:
                continue
            if os.path.exists(png_path) and os.path.getsize(png_path) > 0:
                return r
        except Exception as e:  # try the next renderer
            errors.append(f"{r}: {e}")
    raise RuntimeError("every renderer failed:\n  " + "\n  ".join(errors))


def pixel_fit(vb: tuple[float, float, float, float], size: int) -> tuple[int, int]:
    """Pixel width/height that fits a viewBox into `size` on its long side."""
    _, _, w, h = vb
    if w >= h:
        return size, max(1, int(round(size * h / w)))
    return max(1, int(round(size * w / h))), size


def skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def human_path(p: str | Path) -> str:
    p = str(Path(p).resolve())
    home = str(Path.home())
    return "~" + p[len(home):] if p.startswith(home) else p
