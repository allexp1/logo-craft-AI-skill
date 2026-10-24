#!/usr/bin/env bash
# Install the logo-craft skill for Claude Code.
#
#   ./install.sh            -> ~/.claude/skills/logo-craft   (global, all projects)
#   ./install.sh --project  -> ./.claude/skills/logo-craft   (current project only)
#
# Safe to re-run: an existing install is moved to ~/.claude/skill-backups first.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/logo-craft"

if [[ ! -f "$SRC_DIR/SKILL.md" ]]; then
  echo "error: can't find the skill at $SRC_DIR (run this from the repo root)" >&2
  exit 1
fi

if [[ "${1:-}" == "--project" ]]; then
  DEST="$(pwd)/.claude/skills/logo-craft"
else
  DEST="$HOME/.claude/skills/logo-craft"
fi

# Backups must NOT live under a skills/ directory: anything with a SKILL.md in
# there is discovered as a skill, so a backup would register as a duplicate.
BACKUP_ROOT="$HOME/.claude/skill-backups"
BACKUP=""

knowledge_date() {
  [[ -f "$1" ]] && awk -F': *' '/^last_updated:/ {print $2; exit}' "$1" || true
}

if [[ -d "$DEST" ]]; then
  BACKUP="$BACKUP_ROOT/logo-craft-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$BACKUP_ROOT"
  mv "$DEST" "$BACKUP"
  echo "Backed up the existing install to $BACKUP"
fi

mkdir -p "$DEST"
cp "$SRC_DIR/SKILL.md" "$DEST/SKILL.md"
for part in references scripts assets .living; do
  cp -R "$SRC_DIR/$part" "$DEST/$part"
done
find "$DEST" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$DEST" -name .DS_Store -delete 2>/dev/null || true

# A refresh may have updated the installed knowledge after this repo was last
# edited. Never overwrite newer knowledge with older.
if [[ -n "$BACKUP" && -f "$BACKUP/.living/KNOWLEDGE.md" ]]; then
  OLD_DATE="$(knowledge_date "$BACKUP/.living/KNOWLEDGE.md")"
  NEW_DATE="$(knowledge_date "$DEST/.living/KNOWLEDGE.md")"
  if [[ -n "$OLD_DATE" && "$OLD_DATE" > "$NEW_DATE" ]]; then
    cp "$BACKUP/.living/KNOWLEDGE.md" "$DEST/.living/KNOWLEDGE.md"
    [[ -f "$BACKUP/.living/CHANGELOG.md" ]] && cp "$BACKUP/.living/CHANGELOG.md" "$DEST/.living/CHANGELOG.md"
    echo "Kept the installed knowledge ($OLD_DATE); it is newer than the repo's (${NEW_DATE:-none})"
  fi
fi

# Re-baseline the sidecar's integrity hash against the SKILL.md just installed.
if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "$DEST/SKILL.md" | awk '{print $1}' > "$DEST/.living/ORIGINAL.sha256"
elif command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$DEST/SKILL.md" | awk '{print $1}' > "$DEST/.living/ORIGINAL.sha256"
fi

VERSION="$(awk -F'"' '/^version:/ {print $2; exit}' "$DEST/SKILL.md")"

echo "Installed logo-craft ${VERSION:-} -> $DEST"
echo "Use it in Claude Code with:  /logo-craft"
if ! command -v rsvg-convert >/dev/null 2>&1 && ! command -v magick >/dev/null 2>&1 && ! command -v convert >/dev/null 2>&1; then
  echo "note: no SVG renderer found. Install one for render/check/export:  brew install librsvg"
fi
