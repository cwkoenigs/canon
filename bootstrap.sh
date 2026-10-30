#!/usr/bin/env bash
# bootstrap.sh: one command puts the team's knowledge system on this Mac.
#
#   canon      -> ~/Developer/canon          the standards, scaffolds and canon-lib (this repo)
#   ds-next    -> ~/Developer/ds-next        the terminal, the MCP server and `ds-next` on PATH
#   skills-os  -> ~/Developer/skills-os      pulled if it is there (install.sh clones it): the /so-* procedures
#   docs-ds    -> ~/Developer/docs-ds        pulled if it is there, and `npm ci` run: the renderer behind /docs
#   ds-code    -> ~/Developer/ds-code        pulled if it is there, built and linked: the code tools ds-next attaches
#   agents                                    every agent CLI on PATH (Cortex Code, Claude Code, Codex): the ds server
#                                             registered, /ds-new added, read-only tools allowed
#
# Safe to rerun: it pulls what is there and skips what is done. Needs git and uv; Node.js for docs-ds and ds-code.
# Rerunning is the update. `uninstall.sh` beside this file takes it all off again.
# Override the sources with CANON_URL / DS_NEXT_URL (git URLs, bundles or local paths) and the
# locations with DEV (default ~/Developer). Run from a checkout, or `curl -fsSL <raw url> | bash`.
case "${1:-}" in -h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0;; esac
set -euo pipefail

DEV="${DEV:-$HOME/Developer}"
DEFAULT_CANON_URL="https://github.com/cwkoenigs/canon.git"     # change this when the canon moves
here="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" 2>/dev/null && pwd || pwd)"
if [ -z "${CANON_URL:-}" ]; then
  if [ -f "$here/scripts/build_index.py" ]; then CANON_URL="$here"; else CANON_URL="$DEFAULT_CANON_URL"; fi
fi
if [ -z "${DS_NEXT_URL:-}" ]; then      # ds-next lives beside the canon: same host, same group
  if [ -d "$DEV/ds-next/.git" ]; then DS_NEXT_URL="$DEV/ds-next"
  else origin="$(git -C "$CANON_URL" remote get-url origin 2>/dev/null || echo "$CANON_URL")"
       DS_NEXT_URL="${origin%canon*}ds-next${origin##*canon}"; fi
fi
say() { printf '\n==> %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1 ($2)"; exit 1; }; }

need git "https://git-scm.com"
need uv "curl -LsSf https://astral.sh/uv/install.sh | sh"
command -v cortex >/dev/null 2>&1 || echo "note: Cortex Code is not on PATH; the agent setup step will be skipped"

sync_repo() {   # name url dest
  if [ -d "$3/.git" ]; then
    if git -C "$3" rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
      say "$1: pulling $3"; git -C "$3" pull -q --ff-only || echo "note: $1 not pulled (local changes); using it as is"
    else
      say "$1: at $3 (no upstream to pull; using it as is)"
    fi
  elif [ -d "$2/.git" ] && [ "$(cd "$2" && pwd)" = "$3" ]; then
    say "$1: already at $3"
  else
    say "$1: cloning $2 -> $3"; mkdir -p "$(dirname "$3")"; git clone -q "$2" "$3"
  fi
}

sync_repo canon "$CANON_URL" "$DEV/canon"
sync_repo ds-next "$DS_NEXT_URL" "$DEV/ds-next"
for extra in skills-os docs-ds ds-code; do  # optional companions: updated when present, never cloned here
  [ -d "$DEV/$extra/.git" ] && sync_repo "$extra" "$DEV/$extra" "$DEV/$extra"
done

say "canon-lib: install and test"
(cd "$DEV/canon/lib" && uv sync -q --all-extras && uv run -q pytest -q | tail -1)

say "ds-next: install into its own venv"
# canon-lib comes from this canon checkout, not from the GitHub URL in ds-next's pyproject, so a
# machine whose repos live on the team's host never reaches back to GitHub
OVERRIDE="$(mktemp)"; printf 'canon-lib[tui] @ file://%s/canon/lib\n' "$(cd "$DEV" && pwd)" > "$OVERRIDE"
(cd "$DEV/ds-next" && { [ -x .venv/bin/python ] || uv venv -q -p 3.12 .venv; } && uv pip install -q -p .venv/bin/python --override "$OVERRIDE" -e ".[test]" && .venv/bin/pytest -q | tail -1)
rm -f "$OVERRIDE"

if [ -d "$DEV/docs-ds/.git" ]; then
  say "docs-ds: the renderer behind /docs"
  if command -v npm >/dev/null 2>&1; then
    (cd "$DEV/docs-ds" && npm ci --silent --no-audit --no-fund 2>&1 | tail -2) && echo "docs-ds: dependencies installed (node $(node -v))"
  else
    echo "note: Node.js 26 and npm are not on PATH; /docs will not render until they are and this is rerun"
  fi
fi

if [ -d "$DEV/ds-code/.git" ]; then
  say "ds-code: the code tools ds-next attaches (definitions, references, callers, change impact)"
  if command -v npm >/dev/null 2>&1; then
    if (cd "$DEV/ds-code" && npm ci --silent --no-audit --no-fund 2>&1 | tail -2 && npm link --silent --no-audit --no-fund 2>&1 | tail -1); then
      if command -v ds-code >/dev/null 2>&1; then     # linked is not enough: it has to run
        v="$(ds-code --version 2>&1)" && echo "ds-code: $v at $(command -v ds-code)" \
          || echo "note: ds-code is linked but does not run ($v); run 'npm run build' in $DEV/ds-code and rerun"
      else
        echo "ds-code: linked; add npm's global bin ($(npm prefix -g)/bin) to PATH"
      fi
    else
      echo "note: ds-code did not install; ds-next runs without the code tools until it does and this is rerun"
    fi
  else
    echo "note: Node.js and npm are not on PATH; ds-next runs without the code tools until they are and this is rerun"
  fi
fi

say "ds-next on PATH"
mkdir -p "$HOME/.local/bin"
ln -sf "$DEV/ds-next/.venv/bin/ds-next" "$HOME/.local/bin/ds-next"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "note: add ~/.local/bin to PATH to run ds-next by name";; esac

say "agents: Cortex Code, Claude Code, Codex (whichever are on PATH)"
"$DEV/ds-next/.venv/bin/ds-next" setup || echo "note: an agent is not fully wired; the lines above say which. Rerun 'ds-next setup' after fixing it"

say "check"
"$DEV/ds-next/.venv/bin/python" -c "import ds_next; print('ds-next', ds_next.__version__, 'at', '$DEV/ds-next')"
cat <<DONE

Done. Next:
  cd somewhere && ds-next        # the terminal: /new picks a project type
  cortex                         # /ds-new does the same inside Cortex Code
DONE
