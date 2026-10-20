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
#   3. runs canon/bootstrap.sh: canon-lib and ds-next installed and tested, `ds-next` linked
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

clone() {   # name url dest required
  if [ -d "$3/.git" ]; then echo "$1: already at $3"; return 0; fi
  mkdir -p "$DEV"
  if git clone -q "$2" "$3" 2>/dev/null; then echo "$1: cloned $2"
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
