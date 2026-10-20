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
#   3. asks where the team's copies live. GitHub is only where the first copy comes from; the
#      team's home is its own GitLab. It works the answer out when it can (TEAM_HOST, a clone
#      already in DEV with a remote, a glab login) and otherwise asks on the terminal, Enter for
#      "nowhere yet". Every clone's origin is pointed at that group, or dropped. If the team
#      copies do not exist yet it offers to push and create them. KEEP_ORIGIN=1 keeps GitHub.
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

TTY_IN="${TTY_IN:-/dev/tty}"; TTY_OUT="${TTY_OUT:-/dev/tty}"   # questions reach the terminal even under `curl | bash`
ask() {  # prompt default -> REPLY
  REPLY="$2"
  if [ -z "${ASK_FD:-}" ] && [ -r "$TTY_IN" ]; then exec 3< "$TTY_IN" && ASK_FD=3; fi
  if [ -n "${ASK_FD:-}" ]; then
    { printf '%s' "$1" > "$TTY_OUT"; } 2>/dev/null || true
    IFS= read -r -u 3 REPLY || REPLY="$2"
    [ -n "$REPLY" ] || REPLY="$2"
  fi
}
team_host() {  # the group URL the team's repositories live under, or empty
  [ -n "${TEAM_HOST:-}" ] && { echo "${TEAM_HOST%/}"; return; }
  local u
  for r in canon ds-next; do        # a copy already here that knows its home
    u="$(git -C "$DEV/$r" remote get-url origin 2>/dev/null || true)"
    case "$u" in */$r.git|*/$r) echo "${u%/$r*}"; return;; esac
  done
  if command -v glab >/dev/null 2>&1; then   # a GitLab CLI login names the host, the group is asked
    u="$(glab auth status 2>&1 | sed -n 's/.*Logged in to \([^ ]*\) .*/\1/p' | head -1)"
    [ -n "$u" ] && { ask "GitLab at $u. Group these repositories live under (e.g. data-science), Enter for none: " ""
                     [ -n "$REPLY" ] && { echo "https://$u/${REPLY#/}"; return; }; return; }
  fi
  ask "Where will the team's copies live? Group URL (e.g. https://gitlab.corp.com/data-science), Enter for nowhere yet: " ""
  echo "${REPLY%/}"
}
rehome() {  # name dest: the clone's remote after the download
  if [ -n "${KEEP_ORIGIN:-}" ]; then return; fi
  if [ -n "$HOME_URL" ]; then
    git -C "$2" remote set-url origin "$HOME_URL/$1.git"; echo "$1: origin -> $HOME_URL/$1.git"
    if git -C "$2" ls-remote -q --exit-code origin HEAD >/dev/null 2>&1; then
      git -C "$2" fetch -q origin && git -C "$2" branch -q -u origin/main main 2>/dev/null || true
    else
      TO_SEED="$TO_SEED $1"
    fi
  else
    git -C "$2" remote remove origin; echo "$1: GitHub remote dropped (no team host yet)"
  fi
}
seed() {  # push the clones whose team copies do not exist yet, if asked
  [ -n "$TO_SEED" ] || return 0
  echo "not on the team host yet:$TO_SEED"
  ask "Push them now to create the team copies (main and tags)? [y/N] " "n"
  case "$REPLY" in y|Y|yes)
    for r in $TO_SEED; do git -C "$DEV/$r" push -q -u origin main --tags && echo "$r: pushed" || echo "$r: push failed (create the project on the host, then: git -C $DEV/$r push -u origin main --tags)"; done;;
  *) for r in $TO_SEED; do echo "later: git -C $DEV/$r push -u origin main --tags"; done;;
  esac
}
clone() {   # name url dest required
  if [ -d "$3/.git" ]; then echo "$1: already at $3"; return 0; fi
  mkdir -p "$DEV"
  if git clone -q "$2" "$3" 2>/dev/null; then echo "$1: cloned $2"; rehome "$1" "$3"
  elif [ "$4" = required ]; then echo "$1: cannot clone $2"; exit 1
  else echo "$1: not available at $2 (optional, skipped)"; fi
}
say "team host"
HOME_URL="$(team_host)"; TO_SEED=""
[ -n "$HOME_URL" ] && echo "team copies under $HOME_URL" || echo "none yet: the clones keep no remote (rerun with TEAM_HOST=... once there is one)"

say "repositories -> $DEV"
clone canon     "$CANON_URL"   "$DEV/canon"     required
clone ds-next   "$DS_NEXT_URL" "$DEV/ds-next"   required
clone skills-os "$SKILLS_URL"  "$DEV/skills-os" optional
clone docs-ds   "$DOCS_URL"    "$DEV/docs-ds"   optional
seed

say "bootstrap"
CANON_URL="$DEV/canon" DS_NEXT_URL="$DEV/ds-next" DEV="$DEV" bash "$DEV/canon/bootstrap.sh"
