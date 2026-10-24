---
last_updated: 2026-10-24
review_interval_days: 30
mode: advisory
spec: living-skills/1.1
---

# logo-craft: perishable facts

> Baseline note (2026-10-24): SKILL.md v1.0.0, `references/deliverables.md`,
> `references/typography.md` and `scripts/export_kit.py` were written on this
> date against the primary sources below and already contain everything here.
> From here on this file only needs to carry what changes after 2026-10-24.

## Apple app icons (iOS 26 / 27, iPadOS, macOS Tahoe, watchOS, visionOS)

- Icons are layered **Icon Composer** documents (`.icon`), one 1024 × 1024
  design for every Apple platform; appearances **Default, Dark, Clear
  (light/dark), Tinted (light/dark)**. Do not bake highlights, shadows,
  glass or rounded corners into the artwork; the system renders the
  Liquid Glass material and the mask. Icon Composer 2 (2026) adds per-layer
  refraction and needs macOS Tahoe 26.4 or later.
- Fallback for older Xcode or non-Composer pipelines: a single 1024 PNG in
  the `.appiconset` with `Contents.json` (plus optional dark and tinted
  1024 PNGs). watchOS still takes a 1088 PNG; macOS 1024 with the system
  mask applied by the OS.
- iPhone Duo (2026) changes nothing about icon artwork.
- Sources: HIG App icons; Icon Composer; Xcode "Configuring your app icon";
  WWDC25 361, WWDC26 8012.

## Android and Google Play

- Adaptive icons: 108 dp canvas, 72 dp visible, 66 dp safe zone (keep the
  mark within a 66 dp circle); foreground, background and a **monochrome**
  layer (themed icons, Android 13+). VectorDrawable supports `evenOdd`
  fill type from API 24.
- Google Play listing icon: **512 × 512 PNG, 32-bit, ≤ 1024 KB, no
  transparency**; Play applies its own mask.
- Sources: developer.android.com adaptive icon design; Play icon design
  specifications.

## Web

- `favicon.ico` with 16, 32 and 48 px frames remains the broadest
  fallback; an SVG favicon with a `prefers-color-scheme: dark` rule inside
  `<style>` works in Chromium and Firefox, Safari uses the PNG/ICO.
- `apple-touch-icon` 180 × 180 PNG (opaque; iOS rounds the corners).
- PWA manifest icons 192 and 512 PNG, plus a `purpose: "maskable"` 512 with
  the mark inside the central 80 % (safe circle radius 40 %).
- Open Graph image 1200 × 630; most platforms crop to a centre 1.91:1.
- Avatars (GitHub, Slack, Discord, X, LinkedIn) are square uploads shown
  in circles: keep the mark inside a 80 % circle.
- Sources: web.dev manifest and adaptive favicon; WHATWG rel=icon; Apple
  Configuring Web Applications; ogp.me.

## Fonts and licences

- Google Fonts: all families under the SIL OFL (a few Apache 2.0 / UFL);
  the FAQ says logos are allowed. OFL Reserved Font Names restrict only the
  name of *modified font software*, not the use of glyph outlines in a logo.
- Google's CSS API also serves families that are not in the public
  catalogue (Helvetica was observed 2026-10-25); those have no open licence.
  `text_to_path.py` checks github.com/google/fonts (ofl/apache/ufl) first.
- Google Fonts CSS2 API (`fonts.googleapis.com/css2?family=`) returns
  format-specific CSS by user agent; `text_to_path.py` requests TTF with a
  legacy UA and caches files in `~/.cache/logo-craft/fonts/`.
- Adobe Fonts: logo use allowed for active subscribers (check the current
  licence page). Apple's San Francisco family: licensed only for Apple
  platform software and mock-ups; **not for logos**.
- Commercial foundries differ (some require a separate logo licence, e.g.
  Grilli Type's information page); always read the EULA.

## Trends

- LogoLounge publishes an annual trend report (2026 report read 2026-10-24:
  Slip Knots, Slant Break, Faders, Colorforms, Open Axis, Phasers among the
  named trends; 2025 report: vivid colour, animation-ready marks). Expect a
  2027 report around mid-2027.

## Trademark search entry points (read-only)

- USPTO trademark search (and design search codes for figurative marks).
- EUIPO eSearch plus / "search availability" help.
- WIPO Global Brand Database; Nice classification (classes of goods and
  services).
- This skill never performs clearance; it only names where the user or
  their counsel should search.

## Renderers

- `rsvg-convert` (librsvg) is the reference renderer for the scripts;
  ImageMagick (which may itself delegate to librsvg or its own MSVG) and
  headless Chrome are fallbacks. CairoSVG works but ignores some paint
  properties. Keep masters to filled paths so every renderer agrees.
