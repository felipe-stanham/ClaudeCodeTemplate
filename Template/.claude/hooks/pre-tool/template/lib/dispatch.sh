#!/bin/bash
# Template hook runner — shared by pre-tool, post-tool and stop.
# Called by each .claude/hooks/<type>/dispatcher.sh stub, and by 00-dispatch-shim.sh
# when a pre-1.0 dispatcher is still installed. Managed by template-sync — do not edit.
# Project hooks go in .claude/hooks/<type>/project/*.sh.
#
# Hook contract — every hook runs as a subprocess, receives the tool JSON on stdin and
# HOOK_TOOL / HOOK_CMD / HOOK_FILE / HOOK_CWD in its environment, and exits with:
#   0  allow
#   2  deny — reason on stderr (fed back to Claude)
#   3  ask the user — reason on stderr (pre-tool only; treated as 0 elsewhere)
#   anything else → reported to the user as a hook error; does not block
# Hook stdout is discarded. Requires bash 3.2+ and python3.

HOOK_TYPE="${1:?usage: dispatch.sh <pre-tool|post-tool|stop>}"
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TYPE_DIR="$(cd "$LIB_DIR/../../.." && pwd)/$HOOK_TYPE"
export TEMPLATE_DISPATCH_V1=1

HOOKS=()
for f in "$TYPE_DIR/template/"*.sh "$TYPE_DIR/project/"*.sh; do
  [ -f "$f" ] || continue
  [ "$(basename "$f")" = "00-dispatch-shim.sh" ] && continue
  HOOKS+=("$f")
done
[ ${#HOOKS[@]} -eq 0 ] && exit 0

INPUT="$(cat)"
eval "$(printf '%s' "$INPUT" | python3 -c '
import json, shlex, sys
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}
tool_input = data.get("tool_input") or {}
values = {
    "HOOK_TOOL": data.get("tool_name") or "",
    "HOOK_CMD": tool_input.get("command") or "",
    "HOOK_FILE": tool_input.get("file_path") or tool_input.get("notebook_path") or "",
    "HOOK_CWD": data.get("cwd") or "",
}
for key, value in values.items():
    print("export %s=%s" % (key, shlex.quote(str(value))))
' 2>/dev/null)"
export HOOK_TOOL HOOK_CMD HOOK_FILE
export HOOK_CWD="${HOOK_CWD:-$PWD}"

# Settings without a matcher (projects not yet repaired by template-sync) still call us
# for every tool; only these tools can be gated.
if [ "$HOOK_TYPE" = "pre-tool" ]; then
  case "$HOOK_TOOL" in
    Bash|Edit|Write|MultiEdit|NotebookEdit) ;;
    *) exit 0 ;;
  esac
fi

DENY=""
ASK=""
ERRORS=""
for f in "${HOOKS[@]}"; do
  ERR_FILE="$(mktemp)"
  printf '%s' "$INPUT" | bash "$f" >/dev/null 2>"$ERR_FILE"
  CODE=$?
  MSG="$(cat "$ERR_FILE")"
  rm -f "$ERR_FILE"
  case $CODE in
    0) ;;
    2) DENY="$DENY$MSG"$'\n' ;;
    3) [ "$HOOK_TYPE" = "pre-tool" ] && ASK="$ASK$MSG"$'\n' ;;
    *) ERRORS="$ERRORS[hook error] $(basename "$f") exited $CODE: $MSG"$'\n' ;;
  esac
done

if [ -n "$DENY" ]; then
  printf '%s%s' "$DENY" "$ERRORS" >&2
  exit 2
fi

if [ -n "$ASK" ]; then
  if printf '%s%s' "$ASK" "$ERRORS" | python3 -c '
import json, sys
reason = sys.stdin.read().strip()
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": reason,
}}))
'; then
    exit 0
  fi
  # Could not emit the ask decision — fail closed rather than silently allow.
  printf '%s' "$ASK" >&2
  exit 2
fi

if [ -n "$ERRORS" ]; then
  printf '%s' "$ERRORS" >&2
  exit 1
fi

exit 0
