#!/usr/bin/env python3
"""Compose symbol + wordmark into the standard lockups with clear space.

    python3 lockup.py --symbol symbol.svg --wordmark wordmark.svg --name kixplo --out-dir logo/
    python3 lockup.py --symbol s.svg --wordmark w.svg --tagline t.svg --symbol-height 1.4 --gap 0.6 --rtl

Writes <name>-horizontal.svg, <name>-stacked.svg, <name>-symbol.svg and
<name>-wordmark.svg (the last two re-framed with the same clear space), and
prints the ratios used so they can go into the brand guide. Alignment uses
the wordmark's cap height (data-cap-height from text_to_path.py; falls back to
ink height). All sizes are expressed in cap heights, the unit a brand guide
should use.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ensure_deps, fmt, read_svg_clean, write_svg  # noqa: E402

ensure_deps("fontTools")
from _compose import embed_group, fit_transform, ink_box, new_svg  # noqa: E402


def wordmark_metrics(root):
    box = ink_box(root)
    cap = root.get("data-cap-height")
    base = root.get("data-baseline")
    if cap and base:
        return box, float(cap), float(base)
    # fallback: treat ink height as cap height, bottom as baseline
    return box, box[3] - box[1], box[3]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--wordmark", required=True)
    ap.add_argument("--tagline", help="optional small line set with text_to_path.py")
    ap.add_argument("--name", default="logo")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--symbol-height", type=float, default=1.35, help="symbol height in cap heights, horizontal (default 1.35)")
    ap.add_argument("--stacked-symbol-height", type=float, default=2.2, help="symbol height in cap heights, stacked")
    ap.add_argument("--gap", type=float, default=0.55, help="symbol-to-wordmark gap in cap heights")
    ap.add_argument("--stacked-gap", type=float, default=0.6)
    ap.add_argument("--clearspace", type=float, default=0.5, help="clear space on all sides in cap heights")
    ap.add_argument("--align", choices=["cap", "x", "ink"], default="cap", help="what the symbol centres on")
    ap.add_argument("--rtl", action="store_true", help="symbol on the right (auto when the wordmark is RTL)")
    ap.add_argument("--tagline-size", type=float, default=0.32, help="tagline cap height in main cap heights")
    a = ap.parse_args()

    sym = read_svg_clean(a.symbol)
    wm = read_svg_clean(a.wordmark)
    rtl = a.rtl or wm.get("data-direction") == "rtl"
    sbox = ink_box(sym)
    wbox, cap, baseline = wordmark_metrics(wm)
    xh = float(wm.get("data-x-height") or cap * 0.72)
    cs = a.clearspace * cap
    name = a.name
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    title = wm.get("aria-label") or name

    tl = None
    if a.tagline:
        tl = read_svg_clean(a.tagline)
        tbox, tcap, tbase = wordmark_metrics(tl)

    # ---- horizontal
    sh = a.symbol_height * cap
    sw = (sbox[2] - sbox[0]) / (sbox[3] - sbox[1]) * sh
    gap = a.gap * cap
    ww, wh = wbox[2] - wbox[0], wbox[3] - wbox[1]
    if a.align == "cap":
        centre_y = baseline - cap / 2
    elif a.align == "x":
        centre_y = baseline - xh / 2
    else:
        centre_y = (wbox[1] + wbox[3]) / 2
    # wordmark placed with its ink box at (wx, wbox[1]) unchanged scale
    if rtl:
        wx = cs
        sx = cs + ww + gap
    else:
        sx = cs
        wx = cs + sw + gap
    # vertical: total height is max(symbol, wordmark ink) around centre_y
    top = min(wbox[1], centre_y - sh / 2)
    bottom = max(wbox[3], centre_y + sh / 2)
    extra_h = 0.0
    if tl is not None:
        tscale = (a.tagline_size * cap) / tcap
        tgap = 0.35 * cap
        extra_h = tgap + (tbox[3] - tbox[1]) * tscale
    total_w = cs * 2 + sw + gap + ww
    total_h = cs * 2 + (bottom - top) + extra_h
    root = new_svg(total_w, total_h, title=title)
    dy = cs - top
    # symbol
    tf, s_scale = fit_transform(sbox, sw, sh, sx + sw / 2, centre_y + dy)
    root.append(embed_group(sym, tf, "s-"))
    # wordmark (translate only)
    root.append(embed_group(wm, f"translate({fmt(wx - wbox[0])} {fmt(dy)})", "w-"))
    if tl is not None:
        ty = wbox[3] + dy + tgap  # below the wordmark ink bottom
        tx = (wx + ww - (tbox[2] - tbox[0]) * tscale) if rtl else wx
        root.append(embed_group(tl, f"translate({fmt(tx - tbox[0] * tscale)} {fmt(ty - tbox[1] * tscale)}) scale({fmt(tscale, 5)})", "t-"))
    root.set("data-clearspace", fmt(cs))
    root.set("data-cap-height", fmt(cap))
    write_svg(root, out / f"{name}-horizontal.svg")

    # ---- stacked
    sh2 = a.stacked_symbol_height * cap
    sw2 = (sbox[2] - sbox[0]) / (sbox[3] - sbox[1]) * sh2
    gap2 = a.stacked_gap * cap
    content_w = max(sw2, ww)
    total_w2 = cs * 2 + content_w
    total_h2 = cs * 2 + sh2 + gap2 + wh + extra_h
    root2 = new_svg(total_w2, total_h2, title=title)
    cx = total_w2 / 2
    tf2, _ = fit_transform(sbox, sw2, sh2, cx, cs + sh2 / 2)
    root2.append(embed_group(sym, tf2, "s-"))
    wx2 = cx - ww / 2
    wy2 = cs + sh2 + gap2
    root2.append(embed_group(wm, f"translate({fmt(wx2 - wbox[0])} {fmt(wy2 - wbox[1])})", "w-"))
    if tl is not None:
        ty = wy2 + wh + tgap
        tw = (tbox[2] - tbox[0]) * tscale
        root2.append(embed_group(tl, f"translate({fmt(cx - tw / 2 - tbox[0] * tscale)} {fmt(ty - tbox[1] * tscale)}) scale({fmt(tscale, 5)})", "t-"))
    root2.set("data-clearspace", fmt(cs))
    root2.set("data-cap-height", fmt(cap))
    write_svg(root2, out / f"{name}-stacked.svg")

    # ---- symbol and wordmark alone, same clear space rule
    s_alone = new_svg((sbox[2] - sbox[0]) + 2 * cs * (sh / cap) / a.symbol_height, (sbox[3] - sbox[1]) + 2 * cs * (sh / cap) / a.symbol_height, title=title)
    # clear space for the symbol alone: same absolute rule relative to its own size (0.5 cap at horizontal scale)
    cs_s = cs / s_scale
    s_alone = new_svg((sbox[2] - sbox[0]) + 2 * cs_s, (sbox[3] - sbox[1]) + 2 * cs_s, title=title)
    s_alone.append(embed_group(sym, f"translate({fmt(cs_s - sbox[0])} {fmt(cs_s - sbox[1])})", "s-"))
    s_alone.set("data-clearspace", fmt(cs_s))
    write_svg(s_alone, out / f"{name}-symbol.svg")
    w_alone = new_svg(ww + 2 * cs, wh + 2 * cs, title=title)
    w_alone.append(embed_group(wm, f"translate({fmt(cs - wbox[0])} {fmt(cs - wbox[1])})", "w-"))
    for k in ("data-cap-height", "data-x-height", "data-font", "data-weight", "data-direction"):
        if wm.get(k):
            w_alone.set(k, wm.get(k))
    w_alone.set("data-baseline", fmt(baseline - wbox[1] + cs))
    w_alone.set("data-clearspace", fmt(cs))
    write_svg(w_alone, out / f"{name}-wordmark.svg")

    print(f"wrote {out}/{name}-horizontal.svg, {name}-stacked.svg, {name}-symbol.svg, {name}-wordmark.svg")
    print("Ratios for the brand guide (unit = cap height of the wordmark):")
    print(f"- horizontal: symbol height {a.symbol_height}, gap {a.gap}, symbol centred on the {a.align} height{', symbol on the right (RTL)' if rtl else ''}")
    print(f"- stacked: symbol height {a.stacked_symbol_height}, gap {a.stacked_gap}, centred")
    print(f"- clear space: {a.clearspace} cap height on every side (= {fmt(cs)} units here)")
    if tl is not None:
        print(f"- tagline: {a.tagline_size} cap heights, 0.35 below the wordmark")


if __name__ == "__main__":
    main()
