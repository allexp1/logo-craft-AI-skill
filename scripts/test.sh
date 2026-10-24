#!/usr/bin/env bash
# Smoke tests for every script in the skill, run on the fixtures in
# tests/fixtures. No network is required; a Google Fonts download is tried
# only when the machine is online and skipped otherwise.
#
#   bash scripts/test.sh
#
# Exit code 1 when any test fails. Tests that need an SVG renderer
# (rsvg-convert or ImageMagick) are skipped with a note when none is present.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

S="logo-craft/scripts"
F="tests/fixtures"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT

PASS=0; FAIL=0; SKIP=0
ok()   { echo "  ok    $1"; PASS=$((PASS + 1)); }
bad()  { echo "  FAIL  $1" >&2; FAIL=$((FAIL + 1)); }
skip() { echo "  skip  $1"; SKIP=$((SKIP + 1)); }
# assert NAME COMMAND... : passes when the command exits 0
assert() { local name="$1"; shift; if "$@" >/dev/null 2>&1; then ok "$name"; else bad "$name"; fi; }
py() { python3 -c "$@"; }

have_renderer() {
  command -v rsvg-convert >/dev/null 2>&1 || command -v magick >/dev/null 2>&1 || command -v convert >/dev/null 2>&1
}

echo "logo-craft tests"

# 1. Repository consistency and compilation ------------------------------
if bash scripts/build.sh --check >/dev/null 2>&1; then ok "build.sh --check"; else bad "build.sh --check (run 'bash scripts/build.sh' first)"; fi
assert "scripts compile" python3 -m py_compile "$S"/*.py
find logo-craft -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null

# 2. scan_project -------------------------------------------------------
python3 "$S/scan_project.py" "$F/project" --json "$OUT/brief.json" --quiet >/dev/null 2>&1
assert "scan_project writes JSON" test -s "$OUT/brief.json"
assert "scan_project finds the name" py "import json,sys; b=json.load(open('$OUT/brief.json')); s=json.dumps(b); sys.exit(0 if 'Ledgerly' in s else 1)"
assert "scan_project finds the brand colour" py "import json,sys; s=json.dumps(json.load(open('$OUT/brief.json'))).lower(); sys.exit(0 if '#0f766e' in s else 1)"
assert "scan_project finds the font" py "import json,sys; s=json.dumps(json.load(open('$OUT/brief.json'))); sys.exit(0 if 'Manrope' in s else 1)"
assert "scan_project detects Next.js" py "import json,sys; s=json.dumps(json.load(open('$OUT/brief.json'))).lower(); sys.exit(0 if 'next' in s else 1)"

# 3. text_to_path -------------------------------------------------------
assert "text_to_path --list-fonts" bash -c "python3 '$S/text_to_path.py' --list-fonts | grep -qi 'inter\|manrope\|heebo'"
WORD=""
for fam in Helvetica Arial "DejaVu Sans" "Liberation Sans" "Noto Sans"; do
  if python3 "$S/text_to_path.py" --text "Ledgerly" --font "$fam" --weight 700 --out "$OUT/word.svg" >/dev/null 2>&1; then WORD="$fam"; break; fi
done
if [[ -n "$WORD" ]]; then
  ok "text_to_path sets a system font ($WORD)"
  assert "wordmark carries cap-height metadata" grep -q 'data-cap-height=' "$OUT/word.svg"
  assert "wordmark has one path per glyph" py "import re,sys; n=len(re.findall(r'<path id=\"g\d+\"', open('$OUT/word.svg').read())); sys.exit(0 if n==8 else 1)"
else
  skip "text_to_path system font (none of Helvetica/Arial/DejaVu/Liberation found)"
fi
if python3 - <<'PY' >/dev/null 2>&1
import socket; socket.create_connection(("fonts.googleapis.com", 443), timeout=3)
PY
then
  if python3 "$S/text_to_path.py" --text "לומדים" --font Heebo --weight 800 --out "$OUT/he.svg" >/dev/null 2>&1; then
    ok "text_to_path Google font + Hebrew shaping"
    assert "Hebrew wordmark is marked rtl" grep -q 'data-direction="rtl"' "$OUT/he.svg"
  else
    bad "text_to_path Google font (Heebo) download or shaping"
  fi
else
  skip "Google Fonts download (offline)"
fi

# 4. pen_sweep ----------------------------------------------------------
for mode in broad pointed brush mono; do
  if python3 "$S/pen_sweep.py" --svg "$F/skeleton.svg" --mode "$mode" --width 14 --out "$OUT/pen-$mode.svg" >/dev/null 2>&1 \
     && grep -q '<path' "$OUT/pen-$mode.svg" && ! grep -q 'stroke=' "$OUT/pen-$mode.svg"; then
    ok "pen_sweep --mode $mode produces filled outlines"
  else
    bad "pen_sweep --mode $mode"
  fi
done

# 5. check_logo ---------------------------------------------------------
python3 "$S/check_logo.py" "$F/symbol.svg" --kind symbol --expect-parts 2 --json > "$OUT/check.json" 2>/dev/null
RC=$?
if [[ $RC -eq 0 ]]; then ok "check_logo passes the good symbol (exit 0)"; else bad "check_logo good symbol exit $RC"; fi
assert "check_logo score >= 90" py "import json,sys; d=json.load(open('$OUT/check.json')); sys.exit(0 if d.get('score',0)>=90 else 1)"
python3 "$S/check_logo.py" "$F/bad.svg" > "$OUT/bad.txt" 2>&1
RC=$?
if [[ $RC -eq 1 ]]; then ok "check_logo fails the bad file (exit 1)"; else bad "check_logo bad.svg exit $RC (expected 1)"; fi

# hostile SVG: active/external content must be reported, stripped on render and never reach a deliverable
python3 "$S/check_logo.py" "$F/hostile.svg" --kind symbol > "$OUT/hostile.txt" 2>&1 || true
if grep -q "unsafe-content" "$OUT/hostile.txt"; then ok "check_logo reports unsafe-content on hostile.svg"; else bad "check_logo missed the hostile content"; fi
if python3 "$S/render.py" "$F/hostile.svg" --out "$OUT/hostile.png" --size 64 > "$OUT/hostile-render.txt" 2>&1 && [[ -s "$OUT/hostile.png" ]]; then
  ok "render.py renders a cleaned copy of hostile.svg"
else bad "render.py failed on hostile.svg"; fi
if grep -q "cleaned copy" "$OUT/hostile-render.txt"; then ok "render.py says it cleaned the file"; else bad "render.py did not report the cleaning"; fi
python3 "$S/lockup.py" --symbol "$F/hostile.svg" --wordmark "$F/wordmark.svg" --name hostile --out-dir "$OUT/hostile-lockup" > /dev/null 2>&1 || true
if ls "$OUT/hostile-lockup"/*.svg > /dev/null 2>&1 && ! grep -l -i -E "<script|onload|onclick|javascript:|foreignObject|evil.example|file://" "$OUT/hostile-lockup"/*.svg > /dev/null; then
  ok "lockups built from hostile.svg carry no script, handler or external reference"
else bad "hostile content reached a lockup"; fi
python3 "$S/export_kit.py" --symbol "$F/hostile.svg" --name hostile --out "$OUT/hostile-kit" --no-pdf > "$OUT/hostile-kit.txt" 2>&1 || true
if find "$OUT/hostile-kit" -name "*.svg" | grep -q . && ! grep -r -l -i -E "<script|onload|onclick|javascript:|foreignObject|evil.example|file://" "$OUT/hostile-kit" --include="*.svg" > /dev/null; then
  ok "export kit built from hostile.svg carries no script, handler or external reference"
else bad "hostile content reached the export kit"; fi
python3 - "$S" <<'PY' > "$OUT/sanitize.txt" 2>&1
import sys; sys.path.insert(0, sys.argv[1])
import xml.etree.ElementTree as ET
from _common import sanitize_svg
root = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg"><use href="#ok"/><image href="data:image/png;base64,AA"/><path d="M0 0h1" style="fill:url(#g)"/></svg>')
assert sanitize_svg(root) == [], "clean same-document references must survive"
root = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg"><set attributeName="href" to="javascript:x"/><animate attributeName="xlink:href" to="x"/><g onmouseover="x"/></svg>')
r = sanitize_svg(root); assert len(root) == 1 and not root[0].attrib, r
# bypass attempts: prefixed animated href, url() in a paint attribute, CSS escape, svg data URI, root-level style/url
root = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg" xmlns:x="http://www.w3.org/1999/xlink" style="fill:u\\72l(http://e)" filter="url(http://e/f)">'
                     '<animate attributeName="x:href" to="javascript:x"/><path d="M0 0h1" fill="url( http://e/x )" style="fill:url(http://e)"/>'
                     '<image x:href="data:image/svg+xml,%3Csvg onload=x%3E"/><style>@import "http://e/x.css";</style><style>.a{fill:#f00}</style></svg>')
r = sanitize_svg(root)
tags = [el.tag.split("}")[-1] for el in root]
assert tags == ["path", "style"], (tags, r)
assert not root.attrib.get("style") and not root.attrib.get("filter"), (root.attrib, r)
assert set(root[0].attrib) == {"d"}, (root[0].attrib, r)
assert "@import" not in (root[1].text or "") and ".a{fill:#f00}" in root[1].text
# fail closed on unparsable input
import tempfile, os
from _common import safe_copy_for_render
fd, bad = tempfile.mkstemp(suffix=".svg"); os.write(fd, b"<svg><script>alert(1)</script>"); os.close(fd)
try:
    safe_copy_for_render(bad); raise SystemExit("rendered an unparsable file")
except ValueError:
    pass
finally:
    os.unlink(bad)
print("ok")
PY
if grep -q "^ok$" "$OUT/sanitize.txt"; then ok "sanitize_svg keeps same-document references, defeats the known bypasses and fails closed on bad XML"; else bad "sanitize_svg unit check: $(tail -1 "$OUT/sanitize.txt")"; fi
for w in text gradient filter viewBox; do
  assert "check_logo reports $w" grep -qi "$w" "$OUT/bad.txt"
done

# 6. palette ------------------------------------------------------------
python3 "$S/palette.py" --brand "#0F766E" --brand "#F59E0B" --name ledgerly --out "$OUT/colors" --json > "$OUT/palette.json" 2>/dev/null
assert "palette --json is valid JSON with ramps" py "import json,sys; d=json.load(open('$OUT/palette.json')); s=json.dumps(d); sys.exit(0 if '500' in s and 'contrast' in s.lower() else 1)"
for f in palette.md tokens.css tailwind.colors.js Colors.swift colors.xml; do
  assert "palette writes $f" test -s "$OUT/colors/$f"
done
assert "palette --suggest" bash -c "python3 '$S/palette.py' --brand '#0F766E' --suggest | grep -qi 'complement\|analog\|triad\|split'"

# 7. lockup -------------------------------------------------------------
python3 "$S/lockup.py" --symbol "$F/symbol.svg" --wordmark "$F/wordmark.svg" --name t --out-dir "$OUT/lock" >/dev/null 2>&1
for f in t-horizontal.svg t-stacked.svg t-symbol.svg t-wordmark.svg; do
  assert "lockup writes $f" test -s "$OUT/lock/$f"
done
assert "lockup output has no live text" bash -c "! grep -q '<text' '$OUT/lock/t-horizontal.svg'"

# 8. render and export_kit (need a renderer) ----------------------------
if have_renderer; then
  assert "render --out" python3 "$S/render.py" "$F/symbol.svg" --out "$OUT/symbol.png" --size 256
  assert "render --sheet" python3 "$S/render.py" "$F/symbol.svg" --sheet "$OUT/sheet.png"
  assert "render --compare" python3 "$S/render.py" "$F/symbol.svg" "$OUT/lock/t-horizontal.svg" --compare "$OUT/compare.png" --labels "A,B"
  assert "rendered PNG has the requested size" py "
import struct,sys
d=open('$OUT/symbol.png','rb').read(24); w,h=struct.unpack('>II', d[16:24]); sys.exit(0 if (w,h)==(256,256) else 1)"
  python3 "$S/export_kit.py" --symbol "$F/symbol.svg" --lockup "$OUT/lock/t-horizontal.svg" --stacked "$OUT/lock/t-stacked.svg" \
    --wordmark "$F/wordmark.svg" --name t --bg "#2B2F7A" --fg "#FFFFFF" --out "$OUT/kit" --no-pdf >/dev/null 2>&1
  RC=$?
  if [[ $RC -eq 0 ]]; then ok "export_kit runs"; else bad "export_kit exit $RC"; fi
  for f in web/favicon.ico web/favicon.svg web/apple-touch-icon.png web/icon-192.png web/icon-512.png web/icon-maskable-512.png web/site.webmanifest web/head.html web/og-image.png \
           ios/AppIcon.appiconset/Contents.json ios/AppIcon-1024.png ios/AppIcon-dark-1024.png ios/icon-composer/README.md \
           android/drawable/ic_launcher_foreground.xml android/drawable/ic_launcher_monochrome.xml android/mipmap-anydpi-v26/ic_launcher.xml android/play-store-512.png \
           svg/t-symbol-black.svg svg/t-symbol-white.svg png/t-symbol-color-1024.png README.md; do
    assert "kit has $f" test -s "$OUT/kit/$f"
  done
  assert "favicon.ico holds 16, 32 and 48 px frames" py "
import struct,sys
d=open('$OUT/kit/web/favicon.ico','rb').read(); n=struct.unpack('<H', d[4:6])[0]
sizes={(d[6+16*i] or 256) for i in range(n)}; sys.exit(0 if sizes=={16,32,48} else 1)"
  assert "site.webmanifest declares a maskable icon" py "import json,sys; m=json.load(open('$OUT/kit/web/site.webmanifest')); sys.exit(0 if any('maskable' in i.get('purpose','') for i in m['icons']) else 1)"
  assert "VectorDrawable parses as XML" py "import xml.etree.ElementTree as ET,sys; r=ET.parse('$OUT/kit/android/drawable/ic_launcher_foreground.xml').getroot(); sys.exit(0 if r.tag.endswith('vector') else 1)"
  assert "appiconset Contents.json parses" py "import json,sys; c=json.load(open('$OUT/kit/ios/AppIcon.appiconset/Contents.json')); sys.exit(0 if c.get('images') else 1)"
  assert "Play icon is 512 px" py "
import struct,sys
d=open('$OUT/kit/android/play-store-512.png','rb').read(24); sys.exit(0 if struct.unpack('>II', d[16:24])==(512,512) else 1)"
  assert "kit SVGs pass check_logo" python3 "$S/check_logo.py" "$OUT/kit/svg/t-symbol-black.svg" --kind symbol
else
  skip "render.py and export_kit.py (no SVG renderer: brew install librsvg)"
fi

# 9. installers ---------------------------------------------------------
assert "install.js --dry-run" node bin/install.js --dry-run
if node bin/install.js --dest "$OUT/inst" >/dev/null 2>&1; then
  ok "install.js --dest installs"
  for p in SKILL.md references scripts assets .living/ORIGINAL.sha256 .living/KNOWLEDGE.md; do
    assert "installed tree has $p" test -e "$OUT/inst/$p"
  done
  assert "installed hash matches SKILL.md" bash -c "[[ \"\$(shasum -a 256 '$OUT/inst/SKILL.md' | awk '{print \$1}')\" == \"\$(cat '$OUT/inst/.living/ORIGINAL.sha256')\" ]]"
  assert "installer leaves no __pycache__" bash -c "! find '$OUT/inst' -name __pycache__ | grep -q ."
else
  bad "install.js --dest"
fi

echo
echo "passed $PASS, failed $FAIL, skipped $SKIP"
(( FAIL == 0 ))
