#!/usr/bin/env python3
"""Read a project folder and draft a logo brief from what is already there.

    python3 scan_project.py [PATH] [--json brief.json] [--md brief.md]

Looks at README, package manifests, app manifests, theme files and existing
brand assets. Prints a Markdown brief (name candidates, what the product does,
audience, platforms, stack, existing colours/fonts/icons, locales and script
direction, tone words) and optionally saves JSON for the other scripts.
Read-only; standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

try:
    import tomllib  # py3.11+
except ImportError:  # pragma: no cover
    tomllib = None

SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "out", "target", "vendor", "Pods",
             ".venv", "venv", "__pycache__", ".dart_tool", ".gradle", "DerivedData", ".idea", ".vscode",
             "coverage", ".turbo", ".cache", ".expo", "ios/Pods", ".svelte-kit", ".nuxt", ".output"}
MAX_FILES = 6000
# dependency checkouts whose manifests must not name *our* product
VENDOR_DIRS = {"Packages", "Carthage", "checkouts", "third_party", "third-party", "external", "deps",
               "SourcePackages", "xcshareddata", "fixtures", "__fixtures__", "examples", "example", "test",
               "tests", "spec", "e2e", "playwright-report", "test-results", "storybook-static", "site-packages"}

HEX = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")

STACK_HINTS = {
    "next": "Next.js", "react": "React", "react-native": "React Native", "expo": "Expo", "vue": "Vue",
    "nuxt": "Nuxt", "svelte": "Svelte", "@sveltejs/kit": "SvelteKit", "astro": "Astro", "remix": "Remix",
    "@remix-run/react": "Remix", "solid-js": "Solid", "angular": "Angular", "@angular/core": "Angular",
    "express": "Express", "fastify": "Fastify", "hono": "Hono", "nestjs": "NestJS", "@nestjs/core": "NestJS",
    "electron": "Electron", "@tauri-apps/api": "Tauri", "tailwindcss": "Tailwind CSS", "prisma": "Prisma",
    "@supabase/supabase-js": "Supabase", "firebase": "Firebase", "stripe": "Stripe", "@clerk/nextjs": "Clerk",
    "three": "three.js", "@react-three/fiber": "three.js", "d3": "D3", "chart.js": "Chart.js",
    "openai": "OpenAI API", "@anthropic-ai/sdk": "Claude API", "langchain": "LangChain", "vite": "Vite",
    "flutter": "Flutter", "fastapi": "FastAPI", "django": "Django", "flask": "Flask", "streamlit": "Streamlit",
    "typer": "Typer (CLI)", "click": "Click (CLI)", "commander": "Commander (CLI)", "yargs": "yargs (CLI)",
    "ink": "Ink (CLI)", "torch": "PyTorch", "tensorflow": "TensorFlow", "transformers": "Transformers",
}

DOMAIN_WORDS = {
    "fintech / payments": ["payment", "payments", "invoice", "billing", "bank", "wallet", "fintech", "ledger",
                           "crypto", "stripe", "checkout", "subscription", "pricing"],
    "health / wellness": ["health", "fitness", "workout", "medical", "clinic", "patient", "therapy", "wellness",
                          "sleep", "nutrition", "doctor"],
    "education / kids": ["learn", "learning", "lesson", "course", "school", "teacher", "student", "kids",
                         "children", "grade", "quiz", "homework", "tutor"],
    "developer tools": ["cli", "sdk", "api", "developer", "devtool", "compiler", "terminal", "plugin", "library",
                        "framework", "open source", "npm", "pip"],
    "AI / data": ["ai", "llm", "agent", "model", "embedding", "machine learning", "ml", "dataset", "analytics",
                  "dashboard", "insight"],
    "communication / voice": ["chat", "messaging", "whatsapp", "sms", "voice", "call", "telephony", "sip", "voip",
                              "video", "meeting"],
    "commerce / marketplace": ["shop", "store", "marketplace", "cart", "product", "order", "retail", "ecommerce",
                               "e-commerce", "seller"],
    "media / music": ["music", "audio", "podcast", "playlist", "song", "artist", "video", "photo", "camera",
                      "gallery", "stream"],
    "travel / mobility": ["travel", "flight", "trip", "hotel", "map", "route", "ride", "car", "transit", "delivery"],
    "productivity": ["task", "todo", "notes", "calendar", "project", "workflow", "automation", "team", "crm"],
    "home / IoT": ["home", "smart home", "sensor", "device", "iot", "camera", "nas", "network", "router"],
    "security / privacy": ["security", "privacy", "encryption", "password", "auth", "vpn", "secure", "zero-trust"],
    "food / hospitality": ["food", "recipe", "restaurant", "menu", "coffee", "kitchen", "delivery", "bakery"],
    "real estate / local": ["property", "real estate", "apartment", "rent", "listing", "neighborhood"],
    "social / dating": ["dating", "match", "friends", "community", "social", "profile", "swipe"],
}

AUDIENCE_WORDS = {
    "children": ["kids", "children", "child", "grade", "parents", "toddler", "preschool", "ילדים"],
    "developers": ["developer", "developers", "engineer", "cli", "sdk", "api", "open source", "self-hosted"],
    "businesses (B2B)": ["enterprise", "teams", "business", "b2b", "saas", "customers", "crm", "sales",
                         "operators", "agency"],
    "consumers (B2C)": ["users", "everyone", "personal", "b2c", "your phone", "download", "app store"],
    "creators / professionals": ["musicians", "producers", "designers", "photographers", "creators", "studio",
                                 "mastering", "artists"],
}

TONE_WORDS = ["playful", "fun", "friendly", "warm", "serious", "professional", "trusted", "secure", "fast",
              "simple", "minimal", "premium", "luxury", "bold", "calm", "quiet", "elegant", "modern", "classic",
              "technical", "precise", "honest", "private", "open", "powerful", "lightweight", "delightful",
              "reliable", "smart", "human", "local", "handmade", "craft", "scientific", "curious", "brave"]

LOGO_FILE = re.compile(r"(logo|brand|favicon|app[-_]?icon|icon|mark|wordmark)", re.I)

HEBREW = re.compile(r"[֐-׿]")
ARABIC = re.compile(r"[؀-ۿ]")
CJK = re.compile(r"[぀-ヿ一-鿿가-힯]")
CYRILLIC = re.compile(r"[Ѐ-ӿ]")


def read(p: Path, limit: int = 200_000) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def walk(root: Path):
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
                       and not d.startswith("node_modules") and d not in VENDOR_DIRS]
        rel = Path(dirpath).relative_to(root)
        if len(rel.parts) > 6:
            dirnames[:] = []
            continue
        for f in filenames:
            n += 1
            if n > MAX_FILES:
                return
            yield Path(dirpath) / f


def first_paragraph(md: str) -> str:
    body = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)  # frontmatter
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)  # images
    body = re.sub(r"<[^>]+>", "", body)  # html
    body = re.sub(r"\[!\[.*?\)\]\(.*?\)", "", body)  # badges
    paras = [p.strip() for p in re.split(r"\n\s*\n", body)]
    for p in paras:
        if p.startswith("#") or p.startswith("[") or p.startswith("|") or p.startswith("```"):
            continue
        if len(p) > 40:
            return plain(p)[:600]
    return ""


def plain(md: str) -> str:
    """Markdown to plain text (bold, code, links)."""
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)
    t = re.sub(r"[*_`]{1,3}([^*_`]+)[*_`]{1,3}", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def readme_title(md: str) -> str | None:
    m = re.search(r"^#\s+(.+)$", md, re.M)
    if m:
        t = re.sub(r"[`*_]", "", m.group(1)).strip()
        t = re.sub(r"\s*[-—:|].*$", "", t) if len(t) > 40 else t
        return t[:60]
    return None


def scan(root: Path) -> dict:
    brief: dict = {
        "path": str(root), "name_candidates": [], "taglines": [], "description": "", "domains": [],
        "audience": [], "platforms": [], "stack": [], "colors": [], "fonts": [], "existing_assets": [],
        "locales": [], "scripts": [], "rtl": False, "tone_words": [], "keywords": [], "notes": [],
    }
    names: Counter = Counter()
    colors: Counter = Counter()
    script_files: Counter = Counter()
    fonts: set = set()
    text_blob = []

    # --- README
    for cand in ("README.md", "readme.md", "README.rst", "README", "README.txt", "docs/README.md"):
        p = root / cand
        if p.exists():
            md = read(p)
            t = readme_title(md)
            if t:
                names[t] += 6
            desc = first_paragraph(md)
            if desc and not brief["description"]:
                brief["description"] = desc
            tl = re.search(r"^#\s+.+\n+\s*(?:>\s*)?\*{0,2}_?([^\n#]{12,90})_?\*{0,2}\s*$", md, re.M)
            if tl:
                cand = plain(tl.group(1))
                if cand and not desc.startswith(cand[:30]):
                    brief["taglines"].append(cand)
            text_blob.append(md[:20000])
            break

    # --- package.json
    pj = root / "package.json"
    if pj.exists():
        try:
            data = json.loads(read(pj))
            if data.get("name"):
                nm = data["name"].split("/")[-1]
                names[nm] += 2
            if data.get("description"):
                brief["description"] = brief["description"] or data["description"]
                text_blob.append(data["description"])
            brief["keywords"] += data.get("keywords", []) or []
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            for d in deps:
                if d in STACK_HINTS:
                    brief["stack"].append(STACK_HINTS[d])
            if "bin" in data:
                brief["platforms"].append("CLI")
            if "next" in deps or "react-dom" in deps or "vue" in deps or "svelte" in deps or "astro" in deps:
                brief["platforms"].append("web")
            if "react-native" in deps or "expo" in deps:
                brief["platforms"].append("iOS"); brief["platforms"].append("Android")
            if "electron" in deps or "@tauri-apps/api" in deps:
                brief["platforms"].append("desktop")
            if data.get("private") is not True and "main" in data and "bin" not in data and "next" not in deps:
                brief["platforms"].append("library")
        except Exception:
            brief["notes"].append("package.json could not be parsed")

    # --- pyproject / Cargo / go.mod
    pp = root / "pyproject.toml"
    if pp.exists():
        txt = read(pp)
        data = {}
        if tomllib:
            try:
                data = tomllib.loads(txt)
            except Exception:
                data = {}
        proj = data.get("project") or data.get("tool", {}).get("poetry", {}) or {}
        if proj.get("name"):
            names[proj["name"]] += 2
        if proj.get("description"):
            brief["description"] = brief["description"] or proj["description"]
            text_blob.append(proj["description"])
        deps = " ".join(proj.get("dependencies", []) if isinstance(proj.get("dependencies"), list)
                        else list(proj.get("dependencies", {}).keys()))
        for k, v in STACK_HINTS.items():
            if re.search(rf"\b{re.escape(k)}\b", deps):
                brief["stack"].append(v)
        if "scripts" in proj and proj["scripts"]:
            brief["platforms"].append("CLI")
        brief["stack"].append("Python")
    if (root / "requirements.txt").exists():
        txt = read(root / "requirements.txt").lower()
        for k, v in STACK_HINTS.items():
            if re.search(rf"^{re.escape(k)}\b", txt, re.M):
                brief["stack"].append(v)
        brief["stack"].append("Python")
    cg = root / "Cargo.toml"
    if cg.exists():
        m = re.search(r'^name\s*=\s*"([^"]+)"', read(cg), re.M)
        if m:
            names[m.group(1)] += 2
        m = re.search(r'^description\s*=\s*"([^"]+)"', read(cg), re.M)
        if m:
            brief["description"] = brief["description"] or m.group(1)
        brief["stack"].append("Rust")
    gm = root / "go.mod"
    if gm.exists():
        m = re.search(r"^module\s+(\S+)", read(gm), re.M)
        if m:
            names[m.group(1).split("/")[-1]] += 1
        brief["stack"].append("Go")

    # --- walk files
    for f in walk(root):
        name, suf = f.name, f.suffix.lower()
        rel = f.relative_to(root)
        depth = len(rel.parts)
        shallow = depth <= 4
        # Apple
        if name == "Info.plist":
            try:
                with open(f, "rb") as fh:
                    pl = plistlib.load(fh)
                for k in ("CFBundleDisplayName", "CFBundleName"):
                    v = pl.get(k)
                    if isinstance(v, str) and not v.startswith("$(") and shallow:
                        names[v] += 3 if depth <= 3 else 1
            except Exception:
                pass
            brief["platforms"].append("iOS/macOS")
        if suf == ".xcodeproj" or name.endswith(".xcodeproj") or f.parent.suffix == ".xcodeproj":
            if f.parent.suffix == ".xcodeproj" and shallow:
                names[f.parent.stem] += 2 if depth <= 3 else 1
                brief["platforms"].append("iOS/macOS")
        if name == "Package.swift":
            brief["stack"].append("Swift")
        if suf == ".swift" and "SwiftUI" not in brief["stack"]:
            txt = read(f, 4000)
            if "import SwiftUI" in txt:
                brief["stack"].append("SwiftUI")
        if name.endswith(".appiconset"):
            brief["existing_assets"].append(str(rel))
        if name == "Contents.json" and f.parent.suffix == ".colorset":
            try:
                data = json.loads(read(f))
                for c in data.get("colors", []):
                    comp = c.get("color", {}).get("components", {})
                    if comp and all(k in comp for k in ("red", "green", "blue")):
                        def chan(v):
                            v = str(v)
                            return int(v, 16) if v.startswith("0x") else int(round(float(v) * (255 if float(v) <= 1 else 1)))
                        colors[f"#{chan(comp['red']):02X}{chan(comp['green']):02X}{chan(comp['blue']):02X}"] += 2
                brief["existing_assets"].append(str(rel.parent))
            except Exception:
                pass
        # Android
        if name in ("build.gradle", "build.gradle.kts") and "android" in read(f, 3000):
            brief["platforms"].append("Android")
        if name == "strings.xml" and "values" in str(rel):
            try:
                for s in ET.parse(f).getroot().iter("string"):
                    if s.get("name") == "app_name" and s.text and shallow:
                        names[s.text.strip()] += 3
            except Exception:
                pass
            m = re.search(r"values-([a-z]{2,3})(?:-r[A-Z]{2})?", str(rel))
            if m:
                brief["locales"].append(m.group(1))
        if name == "colors.xml" and "values" in str(rel):
            try:
                for c in ET.parse(f).getroot().iter("color"):
                    if c.text and HEX.match(c.text.strip()):
                        colors[c.text.strip().upper()[:7]] += 2
            except Exception:
                pass
        if name.startswith("ic_launcher") and suf in (".xml", ".png", ".webp"):
            brief["existing_assets"].append(str(rel))
        if name == "pubspec.yaml":
            brief["stack"].append("Flutter")
            m = re.search(r"^name:\s*(\S+)", read(f), re.M)
            if m:
                names[m.group(1)] += 2
            m = re.search(r"^description:\s*(.+)$", read(f), re.M)
            if m:
                brief["description"] = brief["description"] or m.group(1).strip().strip('"')
        # Web
        if name in ("manifest.json", "site.webmanifest", "manifest.webmanifest"):
            try:
                data = json.loads(read(f))
                for k in ("name", "short_name"):
                    if data.get(k):
                        names[data[k]] += 2
                if data.get("theme_color") and HEX.match(data["theme_color"]):
                    colors[data["theme_color"].upper()] += 3
                if data.get("description"):
                    text_blob.append(data["description"])
                brief["platforms"].append("web (PWA)")
            except Exception:
                pass
        if name == "index.html" or (suf == ".html" and len(rel.parts) <= 2):
            txt = read(f, 20000)
            m = re.search(r"<title>([^<]{2,80})</title>", txt, re.I)
            if m:
                names[re.sub(r"\s*[-|–—:].*$", "", m.group(1).strip())] += 1
            m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', txt, re.I)
            if m:
                text_blob.append(m.group(1))
            m = re.search(r'<html[^>]*\slang="([^"]+)"', txt, re.I)
            if m:
                brief["locales"].append(m.group(1))
            if re.search(r'<html[^>]*\sdir="rtl"', txt, re.I):
                brief["rtl"] = True
            for g in re.findall(r"fonts\.googleapis\.com/css2?\?family=([^&\"']+)", txt):
                for fam in g.split("|"):
                    fonts.add(fam.split(":")[0].replace("+", " "))
            brief["platforms"].append("web")
        if name in ("layout.tsx", "layout.jsx", "_app.tsx", "_document.tsx", "app.vue", "App.vue", "+layout.svelte"):
            txt = read(f, 20000)
            for fam in re.findall(r"from\s+['\"]next/font/google['\"][\s\S]{0,400}?\b([A-Z][A-Za-z_]+)\s*\(", txt):
                fonts.add(fam.replace("_", " "))
            for fam in re.findall(r"import\s*\{([^}]+)\}\s*from\s*['\"]next/font/google['\"]", txt):
                for n in fam.split(","):
                    if n.strip():
                        fonts.add(n.strip().replace("_", " "))
            if 'dir="rtl"' in txt or "dir='rtl'" in txt or 'dir: "rtl"' in txt:
                brief["rtl"] = True
            m = re.search(r"title:\s*['\"`]([^'\"`]{2,60})['\"`]", txt)
            if m:
                names[re.sub(r"\s*[-|–—:].*$", "", m.group(1))] += 1
            m = re.search(r"description:\s*['\"`]([^'\"`]{10,300})['\"`]", txt)
            if m:
                text_blob.append(m.group(1))
        if suf in (".css", ".scss", ".less") and f.stat().st_size < 400_000:
            txt = read(f, 120_000)
            for var, val in re.findall(r"(--[\w-]*(?:primary|brand|accent|secondary)[\w-]*)\s*:\s*(#[0-9a-fA-F]{3,8})", txt):
                colors[val.upper()[:7]] += 3
            for m in re.findall(r"@font-face\s*\{[^}]*font-family\s*:\s*['\"]?([^;'\"]+)", txt):
                fonts.add(m.strip())
            for m in re.findall(r"font-family\s*:\s*['\"]?([A-Z][A-Za-z ]{2,30})['\"]?", txt):
                if m.strip() not in ("Arial", "Helvetica", "Times New Roman", "Georgia", "Courier New", "Inherit"):
                    fonts.add(m.strip())
        if name.startswith("tailwind.config"):
            txt = read(f, 60_000)
            for m in HEX.findall(txt):
                colors[m.upper()[:7] if len(m) == 7 else m.upper()] += 1
            brief["stack"].append("Tailwind CSS")
        if name in ("theme.ts", "theme.js", "tokens.json", "colors.ts", "colors.js", "design-tokens.json"):
            txt = read(f, 60_000)
            for m in HEX.findall(txt):
                colors[m.upper()] += 1
        # Locales
        if f.parent.name in ("locales", "i18n", "lang", "translations", "messages") and suf in (".json", ".yml", ".yaml", ".ts", ".js"):
            brief["locales"].append(f.stem.split(".")[0])
        if f.parent.suffix == ".lproj":
            brief["locales"].append(f.parent.stem)
        if ((suf in (".md", ".strings", ".html", ".tsx", ".jsx", ".vue", ".svelte") and depth <= 3)
                or suf == ".json" and f.parent.name in ("locales", "i18n", "lang", "translations", "messages")
                or name == "strings.xml") and f.stat().st_size < 300_000:
            sample = read(f, 8000)
            for rx, label in ((HEBREW, "Hebrew"), (ARABIC, "Arabic"), (CJK, "CJK"), (CYRILLIC, "Cyrillic")):
                if rx.search(sample):
                    script_files[label] += 1
        # Existing brand assets
        if LOGO_FILE.search(name) and suf in (".svg", ".png", ".ico", ".jpg", ".jpeg", ".webp", ".pdf", ".ai", ".sketch", ".fig"):
            if len(brief["existing_assets"]) < 40:
                brief["existing_assets"].append(str(rel))
        if name in ("CLAUDE.md", "AGENTS.md", "HANDOFF.md", "VISION.md", "PRODUCT.md", "brief.md", "pitch.md"):
            text_blob.append(read(f, 12000))
        if f.parent.name in ("docs", "notes") and suf == ".md" and len(text_blob) < 40:
            text_blob.append(read(f, 4000))

    # --- derive
    blob = "\n".join(text_blob).lower()
    brief["name_candidates"] = [n for n, _ in names.most_common(6)]
    scores = Counter()
    for dom, words in DOMAIN_WORDS.items():
        for w in words:
            c = len(re.findall(rf"\b{re.escape(w)}\b", blob))
            if c:
                scores[dom] += min(c, 12)
    brief["domains"] = [d for d, _ in scores.most_common(3) if scores[d] >= 2]
    aud = Counter()
    for a, words in AUDIENCE_WORDS.items():
        for w in words:
            aud[a] += len(re.findall(rf"\b{re.escape(w)}\b", blob))
    brief["audience"] = [a for a, c in aud.most_common(2) if c >= 2]
    brief["tone_words"] = [w for w in TONE_WORDS if re.search(rf"\b{w}\b", blob)][:8]
    for label, n in script_files.items():
        if n >= 2 or (label == "Hebrew" and n >= 1):
            brief["scripts"].append(label)
    if HEBREW.search(blob) or "he" in brief["locales"] or "he-IL" in brief["locales"] or "iw" in brief["locales"]:
        brief["scripts"].append("Hebrew")
        brief["rtl"] = True
    if ARABIC.search(blob) or "ar" in brief["locales"]:
        brief["scripts"].append("Arabic")
        brief["rtl"] = True
    brief["colors"] = [c for c, n in colors.most_common(8) if n >= 1 and c.upper() not in ("#FFFFFF", "#000000", "#FFF", "#000")]
    brief["fonts"] = sorted(fonts)[:10]
    brief["locales"] = [l for l in brief["locales"] if re.fullmatch(r"[a-z]{2,3}([-_][A-Za-z]{2,4})?", l)]
    for k in ("platforms", "stack", "locales", "scripts", "keywords", "existing_assets"):
        seen, out = set(), []
        for v in brief[k]:
            if v not in seen:
                seen.add(v)
                out.append(v)
        brief[k] = out
    if not brief["platforms"]:
        brief["platforms"] = ["unknown (ask)"]
    if not brief["name_candidates"]:
        brief["name_candidates"] = [root.name]
    return brief


def to_markdown(b: dict) -> str:
    def li(items):
        return ", ".join(str(i) for i in items) if items else "(none found)"
    lines = [
        f"# Logo brief draft: {b['name_candidates'][0]}",
        "",
        f"Scanned: `{b['path']}`",
        "",
        f"- Name candidates: {li(b['name_candidates'])}",
        f"- Taglines seen: {li(b['taglines'])}",
        f"- What it does: {b['description'] or '(no description found; ask)'}",
        f"- Domain guess: {li(b['domains'])}",
        f"- Audience guess: {li(b['audience'])}",
        f"- Platforms: {li(b['platforms'])}",
        f"- Stack: {li(b['stack'])}",
        f"- Existing colours: {li(b['colors'])}",
        f"- Existing fonts: {li(b['fonts'])}",
        f"- Existing brand assets: {li(b['existing_assets'][:12])}",
        f"- Locales: {li(b['locales'])}  Scripts: {li(b['scripts'])}  RTL: {'yes' if b['rtl'] else 'no'}",
        f"- Tone words found in copy: {li(b['tone_words'])}",
        f"- Keywords: {li(b['keywords'][:12])}",
    ]
    if b["notes"]:
        lines.append(f"- Notes: {li(b['notes'])}")
    lines += [
        "",
        "## Still to confirm with the user",
        "- One sentence: what the product does and for whom (if the guess above is wrong).",
        "- Two or three adjectives for the voice (and one the brand must never be).",
        "- Where the logo must live first: favicon/app icon, website header, print, social.",
        "- Any shapes, colours or competitors to avoid.",
        "- Name is final? Any trademark check already done?",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".", help="project folder (default: current directory)")
    ap.add_argument("--json", help="write the brief as JSON to this file")
    ap.add_argument("--md", help="write the Markdown brief to this file")
    ap.add_argument("--quiet", action="store_true", help="do not print the Markdown brief")
    a = ap.parse_args()
    root = Path(a.path).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"error: {root} is not a directory")
    b = scan(root)
    md = to_markdown(b)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(b, indent=2, ensure_ascii=False), encoding="utf-8")
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(md, encoding="utf-8")
    if not a.quiet:
        print(md)


if __name__ == "__main__":
    main()
