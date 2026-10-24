# Contributing

Thanks for your interest in improving **logo-craft**.

## What's especially welcome

- **Platform specification updates.** Apple, Google and the browser vendors
  change icon formats every year. PRs that correct a size, a variant or a
  manifest field in `references/deliverables.md` and `scripts/export_kit.py`
  (with a link to the vendor's current page) are the most valuable.
- **New calligraphic hands and scripts.** `references/calligraphy-lettering.md`
  covers Latin, Hebrew and Arabic; Devanagari, Thai, Cyrillic italic and CJK
  brush traditions are open. Give pen angle, nib-width proportions and a source.
- **Sector entries.** `references/industry-conventions.md` has a table per
  category; add a sector with its convention, its clichés and its openings.
- **Sharper tests.** `scripts/check_logo.py` measures what software can measure.
  A new objective check (with a fixture in `tests/fixtures/` that fails it) is
  always welcome.
- **Typefaces.** `assets/fonts.json` is curated, not exhaustive. Add a family
  with its classification, voice, licence and a logo-use note.

## Ground rules

1. **Do not add third-party logos.** No SVGs, PNGs or path data of existing
   marks, however famous. `references/case-studies.md` describes; it does not
   draw. The skill must never become a library of other people's trademarks.
2. **Source every fact.** A size, a licence term, a date, a case-study claim:
   link the primary page it came from in `references/sources.md`. If you
   derived a value yourself, mark it *(derived)*. Interpretation stays
   labelled as interpretation.
3. **Never paste a source's text verbatim** beyond a short attributed phrase.
   Paraphrase, synthesise, link.
4. **Masters are filled paths.** Any script that writes SVG must emit filled
   `<path>` elements with a `viewBox`, no strokes, text, filters, gradients or
   external references. `check_logo.py` enforces this; keep it that way.
5. **Match the house style.** Each reference file: `# Title` + one-line intro,
   a Contents line for long files, numbered sections, tables where a designer
   would want to scan, commands in fenced blocks, no decorative prose.
6. **Keep `SKILL.md` lean** (under 500 lines; `build.sh` fails above that).
   Depth lives in `references/`.
7. **Scripts stay dependency-light.** Standard library first; fontTools,
   uharfbuzz, Pillow and skia-pathops are the only third-party packages, and
   they install into a private venv via `_common.ensure_deps`. No new
   packages without a strong reason.

## Editing and re-packaging

The skill is the `logo-craft/` folder. After any edit, run:

```bash
bash scripts/build.sh     # checks frontmatter, versions, links; compiles scripts; rebuilds hash + dist/
bash scripts/test.sh      # smoke tests on tests/fixtures (needs rsvg-convert or ImageMagick for the render tests)
```

To try the result as a user would:

```bash
node bin/install.js --dry-run   # what the npx installer would do
./install.sh --project          # a real install into ./.claude/skills
```

## Changing the guidance

For any change in what the skill tells people to do:

1. Bump `version` in `logo-craft/SKILL.md` **and** in `package.json` (they must
   match). Patch for corrections, minor for new guidance or a new script
   option, major for a change in the method.
2. Add an entry to `CHANGELOG.md`, with a "Corrections" line if earlier advice
   was wrong.
3. Run `bash scripts/build.sh` and `bash scripts/test.sh`.

## Releasing (maintainers)

After the version bump is merged to `main`:

```bash
git tag v<version> && git push --tags
bash scripts/publish.sh          # npm; logs in if needed, opens the 2FA approval page
```

Then create the GitHub release from the tag and attach `dist/logo-craft.skill`
for people who upload the skill to claude.ai.
