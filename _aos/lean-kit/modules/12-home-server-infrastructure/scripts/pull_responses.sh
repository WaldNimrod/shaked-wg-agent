#!/bin/bash
# AOS Module 12 — Pull responses from server
# Usage: ./pull_responses.sh
# Retrieves responses from server outbox to Mac inbox

set -euo pipefail

SERVER_USER="nimrodw"
SERVER_HOST="${SERVER_HOST:-10.100.102.2}"
OUTBOX_PATH="~/agent_comm/outbox"
LOCAL_INBOX="${LOCAL_INBOX:-$HOME/Documents/_agent_comm/inbox}"

mkdir -p "$LOCAL_INBOX"

echo "📥 Pulling responses from ${SERVER_HOST}:${OUTBOX_PATH}/"

# Pull response messages
scp "${SERVER_USER}@${SERVER_HOST}:${OUTBOX_PATH}/MSG-*-RESPONSE.md" "$LOCAL_INBOX/" 2>/dev/null || {
  echo "⚠️  No new responses available"
  exit 0
}

echo "✅ Responses downloaded to $LOCAL_INBOX/"

# Show what was pulled
if ls "$LOCAL_INBOX"/MSG-*-RESPONSE.md >/dev/null 2>&1; then
  echo ""
  echo "📋 Recent responses:"
  ls -lht "$LOCAL_INBOX"/MSG-*-RESPONSE.md | head -3 | awk '{print "   " $9 " (" $6 " " $7 ")"}'
fi
