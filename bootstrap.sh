#!/usr/bin/env bash
# bootstrap.sh: one command puts the team's knowledge system on this Mac.
#
#   canon      -> ~/Developer/canon          the standards, scaffolds and canon-lib (this repo)
#   ds-next    -> ~/Developer/ds-next        the terminal, the MCP server and `ds-next` on PATH
#   Cortex Code                               the ds server registered, /ds-new added, read-only tools allowed
#
# Safe to rerun: it pulls what is there and skips what is done. Needs git, uv and Cortex Code.
# Override the sources with CANON_URL / DS_NEXT_URL (git URLs or local paths) and the locations
# with DEV (default ~/Developer).
set -euo pipefail

DEV="${DEV:-$HOME/Developer}"
CANON_URL="${CANON_URL:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
DS_NEXT_URL="${DS_NEXT_URL:-$DEV/ds-next}"
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

say "canon-lib: install and test"
(cd "$DEV/canon/lib" && uv sync -q --all-extras && uv run -q pytest -q | tail -1)

say "ds-next: install into its own venv"
(cd "$DEV/ds-next" && { [ -x .venv/bin/python ] || uv venv -q -p 3.12 .venv; } && uv pip install -q -p .venv/bin/python -e ".[test]" && .venv/bin/pytest -q | tail -1)

say "ds-next on PATH"
mkdir -p "$HOME/.local/bin"
ln -sf "$DEV/ds-next/.venv/bin/ds-next" "$HOME/.local/bin/ds-next"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "note: add ~/.local/bin to PATH to run ds-next by name";; esac

say "agents: Cortex Code"
"$DEV/ds-next/.venv/bin/ds-next" setup || true

say "check"
"$DEV/ds-next/.venv/bin/python" -c "import ds_next; print('ds-next', ds_next.__version__, 'at', '$DEV/ds-next')"
cat <<DONE

Done. Next:
  cd somewhere && ds-next        # the terminal: /new picks a project type
  cortex                         # /ds-new does the same inside Cortex Code
DONE
