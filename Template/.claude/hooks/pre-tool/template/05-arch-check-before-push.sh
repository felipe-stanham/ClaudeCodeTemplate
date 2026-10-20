#!/bin/bash
# Architecture gate: on `git push`, run the project's .claude/arch-check.sh (if present and
# executable) and deny the push when it fails. The same script runs in CI.
. "$(dirname "$0")/lib/common.sh"

hook_runs_git push || exit 0
REPO="$(hook_git_dir)"
ROOT="$(git -C "$REPO" rev-parse --show-toplevel 2>/dev/null)" || exit 0
SCRIPT="$ROOT/.claude/arch-check.sh"
[ -x "$SCRIPT" ] || exit 0

OUT="$(mktemp)"
(cd "$ROOT" && "$SCRIPT") >"$OUT" 2>&1
CODE=$?
if [ $CODE -ne 0 ]; then
  TAIL="$(tail -20 "$OUT")"
  rm -f "$OUT"
  deny "architecture check failed (.claude/arch-check.sh exited $CODE). Last lines:
$TAIL"
fi
rm -f "$OUT"
exit 0
