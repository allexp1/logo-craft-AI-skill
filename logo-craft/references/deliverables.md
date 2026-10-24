# Deliverables and platform specifications (verified October 2026)

What a complete logo kit contains, the exact sizes each platform wants, and where the files go in common project layouts. `scripts/export_kit.py` produces all of it from the master SVGs; this file explains what it makes and why, so you can check the output and answer questions. Facts that change (OS icon formats, store limits) also live in `.living/KNOWLEDGE.md` when the sidecar is installed; prefer the newer of the two.

Contents: 1 the kit · 2 web · 3 iOS, iPadOS, macOS, watchOS · 4 Android and Google Play · 5 social and marketing · 6 print · 7 placing files in a project · 8 the brand guide · 9 handover checklist

## 1. The kit

```
dist/logo-kit/
  README.md                      usage rules, sizes, what each file is for
  svg/      <name>-symbol-color|black|white.svg, -horizontal-*, -stacked-*, -wordmark-*, <name>-icon-square.svg
  png/      symbol and lockups at 512, 1024, 2048 (transparent)
  web/      favicon.svg, favicon.ico (16/32/48), favicon-16.png, favicon-32.png, apple-touch-icon.png (180),
            icon-192.png, icon-512.png, icon-maskable-512.png, site.webmanifest, head.html,
            og-image.png (1200x630), social-avatar-1024.png (+ circle preview)
  ios/      AppIcon-1024.png, AppIcon-1024-dark.png, AppIcon-1024-tinted.png,
            AppIcon.appiconset/Contents.json, icon-composer/ (background + symbol layers, README)
  android/  mipmap-anydpi-v26/ic_launcher.xml + ic_launcher_round.xml, drawable/ic_launcher_foreground.xml,
            drawable/ic_launcher_monochrome.xml, values/ic_launcher_background.xml, mipmap-*/ic_launcher*.png,
            play-store-512.png, adaptive-preview-circle.png
  print/    PDFs of symbol and lockups (vector), when rsvg-convert is available
```

Masters stay in `brand/`; the kit is regenerated from them. Never hand-edit the kit.

## 2. Web

| Item | Spec | Notes |
|---|---|---|
| `favicon.svg` | Square SVG; may contain `<style>@media (prefers-color-scheme: dark){...}</style>` to recolour for dark tabs | The only SVG where CSS is allowed. The kit writes the dark rule for single-colour symbols |
| `favicon.ico` | Multi-size ICO with 16, 32 and 48 px entries | Still needed: Safari and many tools ignore SVG favicons; legacy clients request `/favicon.ico` at the root |
| `favicon-16.png`, `favicon-32.png` | Exact pixels | Inspect the 16 px actual pixels; use the compact variant if the master smears |
| `apple-touch-icon.png` | 180 × 180 PNG, opaque, square corners (iOS rounds it) | Draw the symbol at about 72% of the side on the brand background |
| `icon-192.png`, `icon-512.png` | PWA manifest icons, `purpose: any` | Symbol at ~72% on background |
| `icon-maskable-512.png` | `purpose: maskable`; the platform crops to a circle or shape; keep everything important inside a central circle of **40% of the width** (radius) | The kit draws the symbol at ~56% of the side for this |
| `site.webmanifest` | name, short_name, icons (192, 512, maskable 512), theme_color, background_color | `theme_color` is your brand colour or the header background |
| `head.html` | The `<link>` and `<meta>` lines to paste into `<head>`: ICO first with `sizes="32x32"`, then `type="image/svg+xml"`, apple-touch-icon, manifest, theme-color, OG and Twitter card tags | Order matters: browsers that support SVG pick it, others fall back to ICO |
| OG image | 1200 × 630 PNG (1.91:1) | The lockup at about 60% of the width on the brand background; test crops on LinkedIn/Slack/X, which differ |

## 3. iOS, iPadOS, macOS, watchOS (iOS 26 and 27 era)

- **Icon Composer** (Xcode 26 and later) builds a layered `.icon` document from a **1024 × 1024** canvas: a background layer plus one or more symbol layers. The system renders Liquid Glass, specular highlights, shadows and the rounded-square mask; **do not bake corners, gradients, glass, shadows or bevels into the artwork.** Four appearances are rendered: Default, Dark, Clear (light/dark) and Tinted (light/dark); design the symbol so a single-colour tinted version and a dark background version both work. The `.icon` lives beside the asset catalogue in the project.
- **Asset catalogue fallback**: a single **1024 px** PNG in `AppIcon.appiconset` with `Contents.json` listing `luminosity` appearances for `dark` and `tinted`; the kit writes light, dark (`#1C1C1E` background by default) and tinted (symbol as a white alpha mask) versions plus the `Contents.json`.
- **watchOS**: circular icon from a **1088 × 1088** canvas (Icon Composer) or 1024 in the catalogue; everything important inside the circle.
- **macOS**: 1024 canvas; the system applies the rounded-rect mask on macOS Tahoe 26 and later; older macOS expects the baked rounded shape, so a separate legacy icon may be needed if you support macOS 15 or earlier.
- **iPhone Duo (iOS 27.1)** does not change icon artwork; the layered icon adapts.
- Settings and notification sizes are derived by the system from the 1024 master; test the 29 and 40 pt renderings by viewing the 1024 at 58 and 80 px.

The kit's `ios/icon-composer/` folder contains `background.svg` (flat colour) and `symbol.svg` (the mark, recoloured for the background) with a README explaining how to import them as layers; drag them into Icon Composer, set the appearances, export `.icon`.

## 4. Android and Google Play

- **Adaptive icon** (API 26+): `mipmap-anydpi-v26/ic_launcher.xml` referencing a **foreground** drawable, a **background** (colour or drawable) and, for Android 13+ themed icons, a **monochrome** drawable. Both layers are **108 × 108 dp**; the visible area is the inner **72 dp**; the **safe zone** is a centred circle of **66 dp** diameter where nothing important may be cut by the launcher's mask (circle, squircle, rounded square, teardrop). The kit draws the symbol at about 50% of the 108 dp canvas (≈ 54 dp) to stay inside.
- **VectorDrawable** foreground: paths only, `fillType="evenOdd"` allowed (API 24+), no gradients needed; the kit converts the symbol with transforms flattened. The monochrome layer is the symbol in white (the system tints it).
- **Legacy mipmaps** (`mdpi` 48 px to `xxxhdpi` 192 px) for API < 26: rounded-square and circle PNGs, provided by the kit.
- **Google Play listing icon**: **512 × 512 PNG**, 32-bit with alpha, under 1024 KB; Play applies its own rounded mask, so ship a full-bleed square. Feature graphic 1024 × 500 if the listing uses video.
- **Notification small icon**: white silhouette on transparent, 24 dp; derive from the compact symbol if needed.

## 5. Social and marketing

| Use | Size | Notes |
|---|---|---|
| Avatar (X, LinkedIn, GitHub, Slack, WhatsApp) | upload 1024 × 1024 PNG; shown as a circle on most platforms | Symbol at ~62% on a background; check the circle preview the kit renders |
| OG / link preview | 1200 × 630 | see §2 |
| YouTube banner, LinkedIn cover | platform-specific; use the horizontal lockup on a flat field | Keep clear space; never stretch |
| Email signature | horizontal lockup PNG at 2× (e.g. 400 × ~110 shown at 200 wide) | On white; PNG not SVG for client compatibility |
| Presentation template | SVG or PDF of the lockup; one-colour version for dark slides | |

## 6. Print

- **Vector PDF** of symbol and lockups (the kit produces these with rsvg-convert); EPS only if a vendor insists.
- **Colour**: give CMYK and Pantone references from a swatch book, not from a screen conversion (`palette.py` marks its CMYK as approximate). Coated and uncoated appear different.
- **One-colour**: the black version for stamps, engraving, embroidery and laser cutting; the white version for dark substrates.
- **Minimum size in print**: measure, do not assume; a symbol usually holds at 8 to 10 mm, a horizontal lockup at 20 to 25 mm wide. Write the measured value into the guide.

## 7. Placing files in a project

`export_kit.py --into-web <dir> --into-ios <AppIcon.appiconset dir> --into-android <res dir>` copies the right files; `--force` overwrites existing ones. Where they go by framework:

| Project | Favicon and web icons | App icon |
|---|---|---|
| Next.js (app router) | `app/icon.svg`, `app/apple-icon.png`, `app/favicon.ico`, `app/manifest.webmanifest` or `public/` with `head.html` tags | n/a |
| Vite, Astro, plain HTML | `public/` + the tags from `head.html` in `index.html` | n/a |
| Flutter | `web/icons/` + `web/manifest.json` | `ios/Runner/Assets.xcassets/AppIcon.appiconset/`, `android/app/src/main/res/` (or `flutter_launcher_icons` from the 1024 PNG) |
| Expo / React Native | `assets/favicon.png` | `assets/icon.png` (1024), `assets/adaptive-icon.png` (foreground, 1024, transparent) + `backgroundColor` in `app.json` |
| Xcode (SwiftUI/UIKit) | n/a | `Assets.xcassets/AppIcon.appiconset/` (1024 light/dark/tinted + Contents.json) or the `.icon` from Icon Composer |
| Android Studio | n/a | `app/src/main/res/` (mipmap-anydpi-v26, drawable, values, mipmap-*) |
| Tauri | `src-tauri/icons/` (generate with `tauri icon icon.png` from the 1024 PNG) | same |
| Electron | `build/icon.png` 1024 (electron-builder derives .icns/.ico) | same |

Place files in a project only when the user asked for it; otherwise leave the kit in `dist/` and say where it is.

## 8. The brand guide

Fill `assets/brand-guide-template.md`. The minimum a usable guide contains: the mark and its idea in one sentence; the versions (symbol, wordmark, lockups, compact) and when to use each; clear space and minimum sizes in a named unit (the cap height, printed by `lockup.py`) and in measured pixels/millimetres; colour (hex, OKLCH, CMYK/Pantone, dark-mode variants, roles); typography (family, weights, licence, UI pairing); backgrounds (allowed and not); misuse (stretching, rotating, recolouring, effects, redrawing); file inventory; ownership and licence record; contact for the source files. Avoid unsupported universal rules ("clear space is always one x-height"); write what you measured.

## 9. Handover checklist

- [ ] Masters in `brand/` with `<title>`s, no strokes, no transforms, no effects
- [ ] `check_logo.py` passes with no errors on symbol, wordmark and lockups
- [ ] Inspection sheet reviewed: 16/24/32 px, reversed, blur, silhouette
- [ ] Compact variant exists if the master fails at 16 px; switch size written down
- [ ] Palette with contrast and CVD report; dark-background variant
- [ ] Fonts recorded with licence; wordmark outlined
- [ ] Kit generated; favicon.ico has 16/32/48; manifest valid JSON; VectorDrawable parses
- [ ] OG image and avatar circle preview inspected
- [ ] iOS light/dark/tinted inspected; Android circle preview inspected
- [ ] Brand guide filled with measured ratios and sizes
- [ ] Runners-up saved
- [ ] Honesty paragraph written: look-alike search, no trademark clearance, print not proofed
