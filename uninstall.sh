#!/usr/bin/env bash
# uninstall.sh: take the knowledge system off this Mac. The reverse of install.sh, safe to rerun.
#
#   bash ~/Developer/canon/uninstall.sh                 asks before removing the repositories and ~/.ds
#   bash ~/Developer/canon/uninstall.sh --yes           removes them without asking
#   bash ~/Developer/canon/uninstall.sh --keep-repos    agents, links and installs only; the clones stay
#   bash ~/Developer/canon/uninstall.sh --keep-config   the same for ~/.ds
#
# What it does, in order:
#   1. agents: `ds-next setup --remove` unregisters the ds and code servers, unlinks /ds-new,
#      /ds-terminal-design and the /so-* skills, and drops the read-only allow rules from Claude Code
#      and Cortex Code (Codex has none). Without ds-next's venv it does the same by hand.
#   2. `ds-next` out of ~/.local/bin; `ds-code` out of npm's global bin (both only when they point into DEV)
#   3. the five repositories under ~/Developer (DEV overrides). One with uncommitted or unpushed work,
#      or no upstream to compare with, stays and is named.
#   4. ~/.ds: config.toml, history, usage
# uv, Node.js and the agent CLIs are not touched: they are yours, not the system's.
set -uo pipefail

DEV="${DEV:-$HOME/Developer}"
REPOS="canon ds-next skills-os docs-ds ds-code"
YES=no; KEEP_REPOS=no; KEEP_CONFIG=no
for a in "$@"; do
  case "$a" in
    --yes|-y) YES=yes;; --keep-repos) KEEP_REPOS=yes;; --keep-config) KEEP_CONFIG=yes;;
    -h|--help) sed -n '2,18p' "$0"; exit 0;;
    *) echo "unknown option: $a (see --help)"; exit 2;;
  esac
done
say() { printf '\n==> %s\n' "$*"; }
TTY_IN="${TTY_IN:-/dev/tty}"; TTY_OUT="${TTY_OUT:-/dev/tty}"
ask() {  # prompt default -> REPLY; --yes answers y
  REPLY="$2"
  [ "$YES" = yes ] && { REPLY=y; return; }
  if [ -z "${ASK_FD:-}" ] && [ -r "$TTY_IN" ]; then exec 3< "$TTY_IN" && ASK_FD=3; fi
  if [ -n "${ASK_FD:-}" ]; then
    { printf '%s' "$1" > "$TTY_OUT"; } 2>/dev/null || true
    IFS= read -r -u 3 REPLY || REPLY="$2"
    [ -n "$REPLY" ] || REPLY="$2"
  fi
}
real() {  # the path with every symlink resolved, without needing realpath
  local p="$1" d
  while [ -L "$p" ]; do d="$(dirname "$p")"; p="$(readlink "$p")"; case "$p" in /*) ;; *) p="$d/$p";; esac; done
  d="$(cd "$(dirname "$p")" 2>/dev/null && pwd -P)" || return 1
  printf '%s/%s' "$d" "$(basename "$p")"
}
DEVP="$(cd "$DEV" 2>/dev/null && pwd -P || echo "$DEV")"
within() { case "$(real "$1")" in "$2"/*) return 0;; *) return 1;; esac; }   # path dir: is path, resolved, under dir?

say "agents"
DS_NEXT="$DEV/ds-next/.venv/bin/ds-next"
if [ -x "$DS_NEXT" ]; then
  "$DS_NEXT" setup --remove || echo "note: some of that did not come off; the lines above say which"
else
  echo "ds-next's venv is gone; undoing by hand"
  for cli in claude cortex codex; do
    command -v "$cli" >/dev/null 2>&1 || continue
    for s in ds code; do
      if "$cli" mcp get "$s" >/dev/null 2>&1; then
        case "$cli" in claude) "$cli" mcp remove --scope user "$s";; *) "$cli" mcp remove "$s";; esac >/dev/null 2>&1 \
          && echo "  $cli: mcp server $s unregistered" || echo "  $cli: mcp server $s: could not unregister"
      fi
    done
  done
  for folder in "$HOME/.claude/skills" "${CODEX_HOME:-$HOME/.codex}/skills"; do
    [ -d "$folder" ] || continue
    for link in "$folder"/*; do
      [ -L "$link" ] && within "$link" "$DEVP" && rm "$link" && echo "  skill $(basename "$link"): unlinked ($link)"
    done
  done
  if command -v cortex >/dev/null 2>&1; then
    cortex skill list 2>/dev/null | sed -n 's/^ *- \('"$(printf '%s' "$DEV" | sed 's/[.[\*^$/]/\\&/g')"'\/[^ ]*\)$/\1/p' \
      | while read -r path; do cortex skill remove "$path" >/dev/null 2>&1 && echo "  cortex: skill $path removed"; done
  fi
  echo "  permissions: the mcp__ds__* and mcp__code__* rules in ~/.claude/settings.json and ~/.snowflake/cortex/settings.json are left; drop them by hand"
fi

say "commands"
if [ -L "$HOME/.local/bin/ds-next" ] && within "$HOME/.local/bin/ds-next" "$DEVP"; then
  rm "$HOME/.local/bin/ds-next" && echo "ds-next: out of ~/.local/bin"
else
  echo "ds-next: not in ~/.local/bin (or not ours)"
fi
b="$(command -v ds-code 2>/dev/null || true)"     # npm's bin link resolves into DEV/ds-code/dist when it is ours
if [ -n "$b" ] && within "$b" "$DEVP"; then
  if command -v npm >/dev/null 2>&1 && npm rm -g --silent ds-code 2>/dev/null; then echo "ds-code: out of npm's global bin"
  else echo "ds-code: npm rm -g ds-code failed; run it yourself"; fi
else
  echo "ds-code: not on PATH from $DEV; nothing to unlink"
fi

say "repositories -> $DEV"
if [ "$KEEP_REPOS" = yes ]; then
  echo "kept (--keep-repos)"
else
  present=""
  for r in $REPOS; do [ -d "$DEV/$r" ] && present="$present $r"; done
  if [ -z "$present" ]; then
    echo "none there"
  else
    echo "there:$present"
    ask "Remove them? One with uncommitted or unpushed work stays. [y/N] " "n"
    case "$REPLY" in y|Y|yes)
      for r in $present; do
        d="$DEV/$r"
        if [ ! -d "$d/.git" ]; then
          echo "  $r: not a git checkout (files only); kept, remove it yourself if you mean to"
        elif [ -n "$(git -C "$d" status --porcelain 2>/dev/null)" ]; then
          echo "  $r: uncommitted changes; kept"
        elif ! git -C "$d" rev-parse -q --verify '@{u}' >/dev/null 2>&1; then
          echo "  $r: no upstream to compare with; kept"
        elif [ "$(git -C "$d" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 1)" != 0 ]; then
          echo "  $r: commits not pushed; kept"
        else
          rm -rf "$d" && echo "  $r: removed"
        fi
      done;;
    *) echo "kept";;
    esac
  fi
fi

say "config -> $HOME/.ds"
if [ "$KEEP_CONFIG" = yes ]; then
  echo "kept (--keep-config)"
elif [ ! -d "$HOME/.ds" ]; then
  echo "none there"
else
  ask "Remove ~/.ds (config.toml with [world] and [capture], history, usage)? [y/N] " "n"
  case "$REPLY" in y|Y|yes) rm -rf "$HOME/.ds" && echo "removed";; *) echo "kept";; esac
fi

cat <<DONE

Done. uv, Node.js and the agent CLIs are still yours. To put the system back:
  curl -fsSL https://raw.githubusercontent.com/cwkoenigs/canon/main/install.sh | bash
DONE
