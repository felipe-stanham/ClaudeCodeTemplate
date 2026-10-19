# Shared helpers for template hooks. Sourced, not executed. Managed by template-sync.
# Relies on the HOOK_* variables exported by lib/dispatch.sh.

# Git global options that may sit between `git` and the subcommand: -C <dir>, -c <k=v>, --flag[=v]
_GIT_OPTS='([[:space:]]+(-[Cc][[:space:]]+[^[:space:];&|]+|--[a-z-]+(=[^[:space:];&|]+)?))*'

# hook_runs_git <sub>... — true if HOOK_CMD runs `git <sub>` for any of the given subcommands.
hook_runs_git() {
  local sub
  for sub in "$@"; do
    printf '%s\n' "$HOOK_CMD" \
      | grep -qE "(^|[;&|(\`[:space:]])git${_GIT_OPTS}[[:space:]]+${sub}([[:space:];&|)]|\$)" && return 0
  done
  return 1
}

# hook_git_args <sub> — prints the arguments that follow the first `git <sub>` in HOOK_CMD.
hook_git_args() {
  printf '%s\n' "$HOOK_CMD" \
    | sed -nE "s/.*git${_GIT_OPTS}[[:space:]]+$1([^;&|]*).*/\\4/p" \
    | head -1
}

# hook_git_dir — directory the git command runs in: its -C <dir> if given, else the session cwd.
hook_git_dir() {
  local base dir
  base="${HOOK_CWD:-$PWD}"
  dir=$(printf '%s\n' "$HOOK_CMD" | grep -oE 'git[[:space:]]+-C[[:space:]]+[^[:space:];&|]+' | head -1 | awk '{print $3}' | tr -d "\"'")
  case "$dir" in
    "") echo "$base" ;;
    /*) echo "$dir" ;;
    *) echo "$base/$dir" ;;
  esac
}

# deny <message> — block the tool call with a reason Claude will see.
deny() {
  echo "BLOCKED: $*" >&2
  exit 2
}

# ask <message> — require the user's approval for the tool call.
ask() {
  echo "$*" >&2
  exit 3
}
