#!/usr/bin/env bash
# Put the repository on GitHub and cut a release for the version in package.json.
# Safe to re-run: every step is skipped when it is already done.
# Needs the GitHub CLI signed in once (`gh auth login`).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

REPO="allexp1/logo-craft-AI-skill"
VERSION="$(sed -n 's/^  "version": "\(.*\)",$/\1/p' package.json)"
TAG="v$VERSION"
DESC="Context-aware logo design skill for Claude Code: brief from the repo, concepts in black, optical craft, Google Fonts wordmarks, calligraphy, full icon kit"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "The working tree has uncommitted changes. Commit them first." >&2
  exit 1
fi
bash scripts/build.sh --check

if ! git remote get-url origin >/dev/null 2>&1; then
  if gh repo view "$REPO" >/dev/null 2>&1; then
    git remote add origin "https://github.com/$REPO.git"
  else
    gh repo create "$REPO" --public --source . --description "$DESC"
  fi
fi
git push -u origin main

if ! git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  git tag -a "$TAG" -m "logo-craft $VERSION"
fi
git push origin "$TAG"

if gh release view "$TAG" -R "$REPO" >/dev/null 2>&1; then
  echo "Release $TAG already exists."
else
  NOTES="$(mktemp)"
  awk -v v="$VERSION" '$0 ~ "^## " v {f=1; next} /^## / {if (f) exit} f' CHANGELOG.md > "$NOTES"
  gh release create "$TAG" dist/logo-craft.skill -R "$REPO" --title "logo-craft $VERSION" --notes-file "$NOTES"
  rm -f "$NOTES"
fi
echo "https://github.com/$REPO/releases/tag/$TAG"
