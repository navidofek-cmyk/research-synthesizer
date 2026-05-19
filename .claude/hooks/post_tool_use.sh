#!/bin/bash
# Post-tool hook: logs tool result status
# Triggered after each Claude tool execution

TOOL="$CLAUDE_TOOL_NAME"
EXIT_CODE="$CLAUDE_TOOL_EXIT_CODE"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE=".claude/hooks/tool_calls.log"

STATUS="OK"
if [ "$EXIT_CODE" != "0" ]; then
  STATUS="FAILED (exit $EXIT_CODE)"
fi

echo "[$TIMESTAMP] DONE: $TOOL | STATUS: $STATUS" >> "$LOG_FILE"
