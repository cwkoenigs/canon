# lib.sh: what uninstall.sh and ds-system share. Sourced, never run. install.sh and bootstrap.sh keep
# their own copies of say/ask/usage because they also run as `curl ... | bash`, with no clone to source from.

say() { printf '\n==> %s\n' "$*"; }

usage() {  # script: print its header comment (the lines after the shebang, up to the first line that is not a comment)
  awk 'NR > 1 && !/^#/ { exit } NR > 1 { sub(/^# ?/, ""); print }' "$1"
}

TTY_IN="${TTY_IN:-/dev/tty}"; TTY_OUT="${TTY_OUT:-/dev/tty}"   # questions reach the terminal even when stdin is a pipe
ask() {  # prompt default -> REPLY; YES=yes answers y without asking
  REPLY="$2"
  [ "${YES:-no}" = yes ] && { REPLY=y; return; }
  if [ -z "${ASK_FD:-}" ] && [ -r "$TTY_IN" ]; then exec 3< "$TTY_IN" && ASK_FD=3; fi
  if [ -n "${ASK_FD:-}" ]; then
    { printf '%s' "$1" > "$TTY_OUT"; } 2>/dev/null || true
    IFS= read -r -u 3 REPLY || REPLY="$2"
    [ -n "$REPLY" ] || REPLY="$2"
  fi
}

real() {  # path: the path with every symlink resolved, without needing realpath
  local p="$1" d
  while [ -L "$p" ]; do d="$(dirname "$p")"; p="$(readlink "$p")"; case "$p" in /*) ;; *) p="$d/$p";; esac; done
  d="$(cd "$(dirname "$p")" 2>/dev/null && pwd -P)" || return 1
  printf '%s/%s' "$d" "$(basename "$p")"
}

within() { case "$(real "$1")" in "$2"/*) return 0;; *) return 1;; esac; }   # path dir: is path, resolved, under dir?
