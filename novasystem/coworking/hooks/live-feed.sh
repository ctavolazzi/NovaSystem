#!/bin/bash
# NovaSystem coworking layer: stream agent activity into the work log's
# Live Feed section.
#
# Installed by:  novasystem coworking install-hook
# Rendered by:   novasystem/coworking/live_feed.py
#
# Two modes, chosen by $1:
#
#   record   PostToolUse. Appends one JSON line per tool call, then kicks off a
#            debounced render in the background. The append is pure bash + jq
#            so the tool call is never delayed by a Python startup (~0.5s).
#   flush    Stop. Renders synchronously, so the log is correct the moment the
#            turn ends even if the last background render was coalesced away.
#
# Contract: this hook NEVER blocks or fails a tool call. It always exits 0.
# Real failures go to the log below and surface as a systemMessage.
#
# Configuration, all optional:
#   NOVA_COWORKING_DIR   workspace root (default ~/.novasystem/coworking)
#   NOVA_COWORKING_BIN   how to invoke the CLI (default: novasystem)
#   NOVA_COWORKING_LOG   hook error log

set -u

MODE="${1:-record}"

# Absolute path to this script, so the backgrounded render can re-invoke it.
# `readlink -f` is not portable to the BSD readlink on older macOS, so resolve
# from BASH_SOURCE instead.
SELF="${BASH_SOURCE[0]:-$0}"
case "$SELF" in /*) ;; *) SELF="$PWD/$SELF" ;; esac

ROOT="${NOVA_COWORKING_DIR:-$HOME/.novasystem/coworking}"
CLI="${NOVA_COWORKING_BIN:-novasystem}"
LOG="${NOVA_COWORKING_LOG:-$ROOT/hook-errors.log}"

DIR="$ROOT/feed/$(date '+%Y-%m')"
FEED="$DIR/$(date '+%Y-%m-%d').jsonl"
LOCK="$DIR/.render.lock"

render_now() {
  local err rc
  err=$($CLI coworking render 2>&1 >/dev/null)
  rc=$?
  if [ "$rc" -ne 0 ]; then
    mkdir -p "$(dirname "$LOG")" 2>/dev/null
    printf '[%s] rc=%s %s\n' "$(date '+%F %T')" "$rc" "$err" >> "$LOG"
    # Keep the log from growing without bound.
    tail -n 200 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
    return 1
  fi
  return 0
}

case "$MODE" in
  flush)
    # A crashed background render leaves the lock behind; clear it so the
    # final render of the turn is never skipped.
    rmdir "$LOCK" 2>/dev/null
    render_now || {
      msg=$(tail -n 1 "$LOG" 2>/dev/null | tr -d '"\\' | cut -c1-200)
      printf '{"systemMessage":"Live Feed render failed: %s"}\n' "$msg"
    }
    exit 0
    ;;

  record)
    command -v jq >/dev/null 2>&1 || exit 0

    payload=$(cat)
    [ -n "$payload" ] || exit 0

    # Capture raw values only. Every formatting decision lives in live_feed.py,
    # so changing how a row looks never means editing shell.
    line=$(printf '%s' "$payload" | jq -c --arg ts "$(date '+%H:%M:%S')" '
      {
        ts: $ts,
        kind: ((.tool_name // .tool // "?") | tostring),
        sid: (((.session_id // .session // "") | tostring)[0:4]),
        detail: (
          ((.tool_input // .input // {}) as $i
           | $i.command // $i.file_path // $i.notebook_path // $i.pattern
             // $i.description // $i.query // $i.url // $i.prompt // $i.path
             // "")
          | if type == "string" then . else tostring end
        )
      }' 2>/dev/null) || exit 0
    [ -n "$line" ] || exit 0

    mkdir -p "$DIR" 2>/dev/null || exit 0
    printf '%s\n' "$line" >> "$FEED" 2>/dev/null || exit 0

    # Clear a lock left by a render that died mid-flight. Without this, one
    # crash silently stops the feed for the rest of the day.
    if [ -d "$LOCK" ]; then
      find "$LOCK" -maxdepth 0 -mmin +1 -exec rmdir {} \; 2>/dev/null
    fi

    # Coalesce: one render in flight at a time. The short sleep lets a burst of
    # tool calls land in the same rebuild instead of one rebuild each.
    if mkdir "$LOCK" 2>/dev/null; then
      nohup bash -c '
        sleep 0.4
        bash "$0" render_only
        rmdir "$1" 2>/dev/null
      ' "$SELF" "$LOCK" >/dev/null 2>&1 &
    fi
    exit 0
    ;;

  render_only)
    render_now
    exit 0
    ;;

  *)
    exit 0
    ;;
esac
