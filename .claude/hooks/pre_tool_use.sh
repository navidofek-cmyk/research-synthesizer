#!/bin/bash
# Pre-tool hook: logs every tool call with timestamp
# Triggered before each Claude tool execution

TOOL="$CLAUDE_TOOL_NAME"
INPUT="$CLAUDE_TOOL_INPUT"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE=".claude/hooks/tool_calls.log"

echo "[$TIMESTAMP] TOOL: $TOOL | INPUT: ${INPUT:0:120}" >> "$LOG_FILE"
