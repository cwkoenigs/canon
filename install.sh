#!/usr/bin/env bash
# install.sh: clone the team's repositories and set this Mac up. One command, safe to rerun.
#
#   curl -fsSL https://raw.githubusercontent.com/cwkoenigs/canon/main/install.sh | bash
#
# What it does, in order:
#   1. git, uv (installed if missing), Cortex Code (reported if missing)
#   2. clones under ~/Developer (DEV overrides):
#        canon      the standards, scaffolds, canon-lib, bootstrap     (required)
#        ds-next    the terminal, the MCP server, `ds-next` on PATH    (required)
#        skills-os  the /so-* procedures ds-next and Cortex read       (optional, skipped if the clone fails)
#        docs-ds    the docs renderer behind /docs                     (optional, same)
#   3. drops the GitHub remote from each clone: GitHub is only where the first copy comes from,
#      the team's home is its own GitLab. TEAM_HOST=https://gitlab.example.com/group points every
#      clone's origin there instead (then `git push -u origin main --tags` in each seeds it);
#      KEEP_ORIGIN=1 leaves the GitHub remote in place.
#   4. runs canon/bootstrap.sh: canon-lib and ds-next installed and tested, `ds-next` linked
#      into ~/.local/bin, Cortex Code wired (ds server, /ds-new, read-only tools allowed)
# Override any source with CANON_URL, DS_NEXT_URL, SKILLS_URL, DOCS_URL (git URLs, bundles or paths).
set -euo pipefail

HOST="${HOST_URL:-https://github.com/cwkoenigs}"
DEV="${DEV:-$HOME/Developer}"
CANON_URL="${CANON_URL:-$HOST/canon.git}"
DS_NEXT_URL="${DS_NEXT_URL:-$HOST/ds-next.git}"
SKILLS_URL="${SKILLS_URL:-$HOST/skills-os.git}"
DOCS_URL="${DOCS_URL:-$HOST/docs-ds.git}"
say() { printf '\n==> %s\n' "$*"; }

say "tools"
command -v git >/dev/null 2>&1 || { echo "git is missing: run xcode-select --install, then rerun"; exit 1; }
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is missing: installing it (https://astral.sh/uv)"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v cortex >/dev/null 2>&1 && echo "git, uv, cortex: ok" \
  || echo "git, uv: ok. Cortex Code is not on PATH: the agent step will be skipped; install it and rerun"

rehome() {  # name dest: the clone's remote after the download
  if [ -n "${TEAM_HOST:-}" ]; then
    git -C "$2" remote set-url origin "${TEAM_HOST%/}/$1.git"; echo "$1: origin -> ${TEAM_HOST%/}/$1.git"
  elif [ -z "${KEEP_ORIGIN:-}" ]; then
    git -C "$2" remote remove origin; echo "$1: GitHub remote dropped (TEAM_HOST sets the team's, KEEP_ORIGIN=1 keeps it)"
  fi
}
clone() {   # name url dest required
  if [ -d "$3/.git" ]; then echo "$1: already at $3"; return 0; fi
  mkdir -p "$DEV"
  if git clone -q "$2" "$3" 2>/dev/null; then echo "$1: cloned $2"; rehome "$1" "$3"
  elif [ "$4" = required ]; then echo "$1: cannot clone $2"; exit 1
  else echo "$1: not available at $2 (optional, skipped)"; fi
}
say "repositories -> $DEV"
clone canon     "$CANON_URL"   "$DEV/canon"     required
clone ds-next   "$DS_NEXT_URL" "$DEV/ds-next"   required
clone skills-os "$SKILLS_URL"  "$DEV/skills-os" optional
clone docs-ds   "$DOCS_URL"    "$DEV/docs-ds"   optional

say "bootstrap"
CANON_URL="$DEV/canon" DS_NEXT_URL="$DEV/ds-next" DEV="$DEV" bash "$DEV/canon/bootstrap.sh"
