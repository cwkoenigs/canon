#!/usr/bin/env bash
# Install or remove the opt-in design sync skill in existing local skill directories.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
NAME=ds-cli-design-sync
SOURCE="$ROOT/skills/$NAME"
LEGACY="$(dirname "$(dirname "$ROOT")")/ds-cli-design/skills/$NAME"

case "${1:-}" in
  "") remove=false ;;
  --uninstall) remove=true ;;
  *) echo "usage: $0 [--uninstall]" >&2; exit 2 ;;
esac

result=0
for dir in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.hermes/skills"; do
  [ -d "$dir" ] || continue
  link="$dir/$NAME"
  target=""
  if [ -L "$link" ]; then target="$(readlink "$link")"; fi
  if $remove; then
    if [ "$target" = "$SOURCE" ]; then
      unlink "$link"
      echo "removed $link"
    fi
  elif [ "$target" = "$SOURCE" ]; then
    echo "already linked $link"
  elif [ "$target" = "$LEGACY" ] || { [ ! -e "$link" ] && [ ! -L "$link" ]; }; then
    ln -sfn "$SOURCE" "$link"
    echo "linked $link"
  else
    echo "skill already exists at $link. Move it aside before installing." >&2
    result=1
  fi
done
exit "$result"
