#!/usr/bin/env bash
# Usage: mcp_availability_check.sh <port> [timeout_seconds]
# Checks: server responds on port within timeout
set -euo pipefail

PORT="${1:?Usage: mcp_availability_check.sh <port> [timeout_seconds]}"
TIMEOUT="${2:-5}"

if curl -sf --max-time "$TIMEOUT" "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then
  echo "PASS: Server responding on port $PORT"
  exit 0
else
  echo "FAIL: No response on port $PORT within ${TIMEOUT}s"
  exit 1
fi
