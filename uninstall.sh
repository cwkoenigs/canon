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
#   3. the five repositories under ~/Developer (DEV overrides). One with uncommitted changes, a stash,
#      a branch without an upstream or with commits not pushed, stays and is named. If step 1 failed,
#      no clone is removed this run.
#   4. ~/.ds: config.toml, history, usage
# uv, Node.js and the agent CLIs are not touched: they are yours, not the system's.
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
. "$here/lib.sh"                               # say, usage, ask, real, within

DEV="${DEV:-$HOME/Developer}"
DEVP="$(cd "$DEV" 2>/dev/null && pwd -P || echo "$DEV")"
REPOS="canon ds-next skills-os docs-ds ds-code"
YES=no; KEEP_REPOS=no; KEEP_CONFIG=no
for a in "$@"; do
  case "$a" in
    --yes|-y) YES=yes;; --keep-repos) KEEP_REPOS=yes;; --keep-config) KEEP_CONFIG=yes;;
    -h|--help) usage "$0"; exit 0;;
    *) echo "unknown option: $a (see --help)"; exit 2;;
  esac
done
our_skill() {  # link or path: does it point into ds-next's skills or skills-os? Resolved, or as written when dangling.
  local p
  for p in "$(real "$1" 2>/dev/null)" "$(readlink "$1" 2>/dev/null || echo "$1")"; do
    case "$p" in "$DEV"/ds-next/skills/*|"$DEV"/skills-os/*|"$DEVP"/ds-next/skills/*|"$DEVP"/skills-os/*) return 0;; esac
  done
  return 1
}
unsafe() {  # clone: prints why it must stay, or nothing
  local d="$1" out line
  out="$(git -C "$d" status --porcelain --untracked-files=normal 2>/dev/null)" || { echo "git status failed"; return; }
  [ -n "$out" ] && { echo "uncommitted changes"; return; }
  [ -n "$(git -C "$d" stash list 2>/dev/null)" ] && { echo "stashed work"; return; }
  git -C "$d" for-each-ref --format='%(refname:short) [%(upstream)] %(upstream:track)' refs/heads/ 2>/dev/null | while read -r line; do
    case "$line" in                           # read drops trailing blanks: an empty track leaves the line ending in []
      *"[]")    echo "branch ${line%% *} has no upstream";;
      *ahead*)  echo "branch ${line%% *} has commits not pushed";;
    esac
  done | head -1
}
FAILED=no

say "agents"
DS_NEXT="$DEV/ds-next/.venv/bin/ds-next"
if [ -x "$DS_NEXT" ]; then
  "$DS_NEXT" setup --remove || { FAILED=yes; echo "note: some of that did not come off; the lines above say which"; }
else
  echo "ds-next's venv is gone; undoing by hand"
  for cli in claude cortex codex; do
    command -v "$cli" >/dev/null 2>&1 || continue
    for s in ds code; do
      reg="$("$cli" mcp get "$s" 2>/dev/null)" || continue
      case "$s:$reg" in                     # only a registration that runs our command comes off
        ds:*"$DEV/ds-next/"*|ds:*"$DEVP/ds-next/"*|code:*ds-code*) ;;
        *) echo "  $cli: mcp server $s runs something else; not ours, left alone"; continue;;
      esac
      case "$cli" in claude) "$cli" mcp remove --scope user "$s";; *) "$cli" mcp remove "$s";; esac >/dev/null 2>&1 \
        && echo "  $cli: mcp server $s unregistered" || { FAILED=yes; echo "  $cli: mcp server $s: could not unregister"; }
    done
  done
  for folder in "$HOME/.claude/skills" "${CODEX_HOME:-$HOME/.codex}/skills"; do
    [ -d "$folder" ] || continue
    for link in "$folder"/*; do
      [ -L "$link" ] && our_skill "$link" && rm "$link" && echo "  skill $(basename "$link"): unlinked ($link)"
    done
  done
  if command -v cortex >/dev/null 2>&1; then
    cortex skill list 2>/dev/null | sed -n 's/^ *- \(\/.*\)$/\1/p' | while read -r path; do
      our_skill "$path" && { cortex skill remove "$path" >/dev/null 2>&1 && echo "  cortex: skill $path removed"; }
    done
  fi
  for f in "$HOME/.claude/settings.json" "$HOME/.snowflake/cortex/settings.json"; do
    [ -f "$f" ] || continue
    if command -v python3 >/dev/null 2>&1; then
      python3 - "$f" <<'PY' || { FAILED=yes; echo "  permissions: could not edit $f; drop the mcp__ds__* and mcp__code__* rules by hand"; }
import json, shutil, sys
p = sys.argv[1]
d = json.load(open(p))
perms = d.get("permissions") if isinstance(d, dict) else None
allow = perms.get("allow") if isinstance(perms, dict) else None
if not isinstance(allow, list):
    print(f"  permissions: no allow list in {p}"); sys.exit(0)
keep = [r for r in allow if not (isinstance(r, str) and (r.startswith("mcp__ds__") or r.startswith("mcp__code__")))]
if len(keep) == len(allow):
    print(f"  permissions: no rules of ours in {p}"); sys.exit(0)
shutil.copy2(p, p + ".bak")
perms["allow"] = keep
open(p, "w").write(json.dumps(d, indent=2) + "\n")
print(f"  permissions: dropped {len(allow) - len(keep)} read-only rules from {p} (backup .json.bak)")
PY
    else
      echo "  permissions: python3 is missing; drop the mcp__ds__* and mcp__code__* rules in $f by hand"
    fi
  done
fi

say "commands"
if [ -L "$HOME/.local/bin/ds-next" ] && within "$HOME/.local/bin/ds-next" "$DEVP"; then
  rm "$HOME/.local/bin/ds-next" && echo "ds-next: out of ~/.local/bin"
else
  echo "ds-next: not in ~/.local/bin (or not ours)"
fi
b="$(command -v ds-code 2>/dev/null || true)"     # npm's bin link resolves into DEV/ds-code/dist when it is ours
if [ -z "$b" ] && command -v npm >/dev/null 2>&1; then   # global bin not on PATH: look where npm keeps the link
  g="$(npm prefix -g 2>/dev/null)/lib/node_modules/ds-code"; [ -L "$g" ] && b="$g"
fi
if [ -n "$b" ] && within "$b" "$DEVP/ds-code"; then
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
    if [ "$FAILED" = yes ]; then
      echo "kept: the agents did not come fully unwired (above); fix that and rerun before the clones go"
    else
      ask "Remove them? One with uncommitted, stashed or unpushed work stays. [y/N] " "n"
      case "$REPLY" in y|Y|yes)
        for r in $present; do
          d="$DEV/$r"
          if [ ! -d "$d/.git" ]; then
            echo "  $r: not a git checkout (files only); kept, remove it yourself if you mean to"
          elif why="$(unsafe "$d")" && [ -n "$why" ]; then
            echo "  $r: $why; kept"
          else
            rm -rf "$d" && echo "  $r: removed"
          fi
        done;;
      *) echo "kept";;
      esac
    fi
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

[ "$FAILED" = yes ] && { echo; echo "Not everything came off: see the notes above, then rerun."; exit 1; }
cat <<DONE

Done. uv, Node.js and the agent CLIs are still yours. To put the system back:
  curl -fsSL https://raw.githubusercontent.com/cwkoenigs/canon/main/install.sh | bash
(or clone canon again and run its ds-system)
DONE
