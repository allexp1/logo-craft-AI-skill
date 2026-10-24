#!/usr/bin/env python3
"""Build a brand palette from one to three brand colours.

    python3 palette.py --brand "#2B2F7A" --brand "#F4A300" --name kixplo --out brand/colors
    python3 palette.py --brand "#2B2F7A" --suggest          # harmonies to consider
    python3 palette.py --brand "#2B2F7A" --json

Writes: palette.md (report), tokens.css, tailwind.colors.js, Colors.swift,
colors.xml, palette.json. Ramps are built in OKLCH (even perceived
lightness), contrast is WCAG 2.x, colour-vision simulation uses the Machado
2009 matrices. CMYK values are a screen approximation: get real print values
from a printer or a Pantone bridge.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (contrast, delta_e_ok, oklch_to_rgb_clamped, parse_hex, rgb_to_cmyk, rgb_to_hsl,  # noqa: E402
                     rgb_to_oklch, simulate_cvd, to_hex)

STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
L_TARGET = {50: 0.975, 100: 0.945, 200: 0.89, 300: 0.81, 400: 0.72, 500: 0.63, 600: 0.55, 700: 0.47, 800: 0.39,
            900: 0.31, 950: 0.24}


def ramp(hexc: str) -> dict:
    rgb = parse_hex(hexc)
    L, C, H = rgb_to_oklch(rgb)
    # put the brand colour on the nearest step, build the others around it
    nearest = min(STEPS, key=lambda s: abs(L_TARGET[s] - L))
    out = {}
    for s in STEPS:
        if s == nearest:
            out[s] = to_hex(rgb)
            continue
        Lt = L_TARGET[s]
        # chroma falls off towards white and black
        if Lt > L:
            f = (1 - Lt) / (1 - L) if L < 1 else 0
        else:
            f = Lt / L if L > 0 else 0
        c = C * max(0.08, min(1.0, f)) ** 0.85
        out[s] = to_hex(oklch_to_rgb_clamped((Lt, c, H)))
    return out


def neutral_ramp(hexc: str, chroma: float = 0.012) -> dict:
    _, _, H = rgb_to_oklch(parse_hex(hexc))
    out = {}
    for s in STEPS:
        out[s] = to_hex(oklch_to_rgb_clamped((L_TARGET[s], chroma, H)))
    return out


def describe(hexc: str) -> dict:
    rgb = parse_hex(hexc)
    L, C, H = rgb_to_oklch(rgb)
    return {
        "hex": hexc.upper(), "rgb": list(rgb), "hsl": list(rgb_to_hsl(rgb)),
        "oklch": [round(L, 3), round(C, 3), round(H, 1)], "cmyk_approx": list(rgb_to_cmyk(rgb)),
        "contrast_on_white": round(contrast(rgb, (255, 255, 255)), 2),
        "contrast_on_black": round(contrast(rgb, (0, 0, 0)), 2),
        "cvd": {k: to_hex(simulate_cvd(rgb, k)) for k in ("protanopia", "deuteranopia", "tritanopia")},
        "for_dark_backgrounds": to_hex(oklch_to_rgb_clamped((min(0.9, L + 0.14), C * 0.9, H))),
    }


def suggest(hexc: str) -> list[dict]:
    rgb = parse_hex(hexc)
    L, C, H = rgb_to_oklch(rgb)
    cands = [
        ("complementary", (L, C, (H + 180) % 360)),
        ("split-complementary A", (L, C, (H + 150) % 360)),
        ("split-complementary B", (L, C, (H + 210) % 360)),
        ("analogous A", (L, C, (H + 30) % 360)),
        ("analogous B", (L, C, (H - 30) % 360)),
        ("triadic A", (L, C, (H + 120) % 360)),
        ("triadic B", (L, C, (H + 240) % 360)),
        ("warm accent", (0.78, 0.17, 70)),
        ("ink (dark neutral, same hue)", (0.25, min(C, 0.04), H)),
        ("paper (light neutral, same hue)", (0.975, min(C, 0.01), H)),
    ]
    out = []
    for name, lch in cands:
        c = to_hex(oklch_to_rgb_clamped(lch))
        out.append({"role": name, "hex": c, "contrast_with_brand": round(contrast(parse_hex(c), rgb), 2),
                    "contrast_on_white": round(contrast(parse_hex(c), (255, 255, 255)), 2)})
    return out


def pair_checks(colors: list[str]) -> list[dict]:
    out = []
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            a, b = parse_hex(colors[i]), parse_hex(colors[j])
            row = {"pair": [colors[i], colors[j]], "contrast": round(contrast(a, b), 2),
                   "delta_e": round(delta_e_ok(a, b), 1)}
            for k in ("protanopia", "deuteranopia", "tritanopia"):
                row[f"delta_e_{k}"] = round(delta_e_ok(simulate_cvd(a, k), simulate_cvd(b, k)), 1)
            row["confusable_for"] = [k for k in ("protanopia", "deuteranopia", "tritanopia") if row[f"delta_e_{k}"] < 12]
            out.append(row)
    return out


def tokens_css(name, ramps, neutral):
    lines = [":root {"]
    for role, rp in ramps.items():
        for s, c in rp.items():
            lines.append(f"  --{name}-{role}-{s}: {c};")
    for s, c in neutral.items():
        lines.append(f"  --{name}-neutral-{s}: {c};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def tokens_tailwind(name, ramps, neutral):
    obj = {role: {str(s): c for s, c in rp.items()} for role, rp in ramps.items()}
    obj["neutral"] = {str(s): c for s, c in neutral.items()}
    return "// tailwind.config.js → theme.extend.colors\nmodule.exports = " + json.dumps(obj, indent=2) + ";\n"


def tokens_swift(name, ramps, neutral):
    lines = ["import SwiftUI", "", f"// {name} brand colours (generated by logo-craft palette.py)", "extension Color {"]

    def sw(label, c):
        r, g, b = parse_hex(c)
        return f"    static let {label} = Color(red: {r / 255:.3f}, green: {g / 255:.3f}, blue: {b / 255:.3f}) // {c}"
    for role, rp in ramps.items():
        for s, c in rp.items():
            lines.append(sw(f"{role}{s}", c))
    for s, c in neutral.items():
        lines.append(sw(f"neutral{s}", c))
    lines.append("}")
    return "\n".join(lines) + "\n"


def tokens_android(name, ramps, neutral):
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
    for role, rp in ramps.items():
        for s, c in rp.items():
            lines.append(f'    <color name="{name}_{role}_{s}">{c}</color>')
    for s, c in neutral.items():
        lines.append(f'    <color name="{name}_neutral_{s}">{c}</color>')
    lines.append("</resources>")
    return "\n".join(lines) + "\n"


def report_md(name, brands, ramps, neutral, pairs, suggestions):
    L = [f"# {name}: colour system", ""]
    for role, hexc in brands.items():
        d = describe(hexc)
        L += [f"## {role}: {d['hex']}",
              f"- RGB {d['rgb']}  HSL {d['hsl']}  OKLCH {d['oklch']}  CMYK≈ {d['cmyk_approx']}",
              f"- Contrast on white {d['contrast_on_white']}:1 ({'AA text' if d['contrast_on_white'] >= 4.5 else 'graphics 3:1 ok' if d['contrast_on_white'] >= 3 else 'too light for white'});"
              f" on black {d['contrast_on_black']}:1",
              f"- Use on dark backgrounds: {d['for_dark_backgrounds']}",
              f"- Seen by protanopes {d['cvd']['protanopia']}, deuteranopes {d['cvd']['deuteranopia']}, tritanopes {d['cvd']['tritanopia']}",
              "", "| step | " + " | ".join(str(s) for s in STEPS) + " |", "|---|" + "---|" * len(STEPS),
              "| hex | " + " | ".join(ramps[role][s] for s in STEPS) + " |", ""]
    L += ["## Neutral (tinted with the primary hue)", "| step | " + " | ".join(str(s) for s in STEPS) + " |",
          "|---|" + "---|" * len(STEPS), "| hex | " + " | ".join(neutral[s] for s in STEPS) + " |", ""]
    if pairs:
        L += ["## Pairs", "| pair | contrast | ΔE | ΔE protan | ΔE deutan | ΔE tritan | confusable |", "|---|---|---|---|---|---|---|"]
        for p in pairs:
            L.append(f"| {p['pair'][0]} / {p['pair'][1]} | {p['contrast']} | {p['delta_e']} | {p['delta_e_protanopia']} | "
                     f"{p['delta_e_deuteranopia']} | {p['delta_e_tritanopia']} | {', '.join(p['confusable_for']) or 'no'} |")
        L.append("")
    if suggestions:
        L += ["## Harmonies from the primary (candidates, not decisions)", "| role | hex | vs brand | on white |", "|---|---|---|---|"]
        for s in suggestions:
            L.append(f"| {s['role']} | {s['hex']} | {s['contrast_with_brand']} | {s['contrast_on_white']} |")
        L.append("")
    L += ["## Rules", "- The logo must work in black and in white before any colour is chosen.",
          "- One dominant colour; a second only with a job (accent, state). Three is the ceiling.",
          "- Logo colour is exempt from WCAG text contrast, but UI graphics need 3:1 and text 4.5:1 (use the 600-900 steps on white).",
          "- Check the 'confusable' column: never let two brand colours carry meaning only by hue.",
          "- Screen CMYK is an estimate. For print, pick Pantone/CMYK with a printer's swatch book.", ""]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand", action="append", required=True, help="hex colour; repeat (first = primary)")
    ap.add_argument("--roles", help="comma names for the brands (default primary,secondary,accent)")
    ap.add_argument("--name", default="brand")
    ap.add_argument("--out", help="directory for tokens and report")
    ap.add_argument("--suggest", action="store_true", help="print harmony candidates from the primary")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    roles = (a.roles.split(",") if a.roles else ["primary", "secondary", "accent", "fourth"])[:len(a.brand)]
    brands = {r: to_hex(parse_hex(c)) for r, c in zip(roles, a.brand)}
    ramps = {r: ramp(c) for r, c in brands.items()}
    neutral = neutral_ramp(brands[roles[0]])
    pairs = pair_checks(list(brands.values())) if len(brands) > 1 else []
    sugg = suggest(brands[roles[0]]) if a.suggest else []
    data = {"name": a.name, "brands": {r: describe(c) for r, c in brands.items()}, "ramps": ramps,
            "neutral": neutral, "pairs": pairs, "suggestions": sugg}
    md = report_md(a.name, brands, ramps, neutral, pairs, sugg)
    if a.out:
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "palette.md").write_text(md, encoding="utf-8")
        (out / "palette.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        (out / "tokens.css").write_text(tokens_css(a.name, ramps, neutral), encoding="utf-8")
        (out / "tailwind.colors.js").write_text(tokens_tailwind(a.name, ramps, neutral), encoding="utf-8")
        (out / "Colors.swift").write_text(tokens_swift(a.name, ramps, neutral), encoding="utf-8")
        (out / "colors.xml").write_text(tokens_android(a.name, ramps, neutral), encoding="utf-8")
        print(f"wrote {out}/palette.md, palette.json, tokens.css, tailwind.colors.js, Colors.swift, colors.xml",
              file=sys.stderr if a.json else sys.stdout)
    if a.json:
        print(json.dumps(data, indent=2))
    elif not a.out:
        print(md)


if __name__ == "__main__":
    main()
