#!/bin/bash
# AOS Module 12 — Send message to server
# Usage: ./send_message.sh <message_file> [additional_files...]
# Sends agent communication messages from Mac to server inbox

set -euo pipefail

# Configuration (update per environment)
SERVER_USER="nimrodw"
SERVER_HOST="${SERVER_HOST:-10.100.102.2}"  # LAN IP (preferred) or 100.125.98.56 (Tailscale)
INBOX_PATH="~/agent_comm/inbox"

echo "📤 Sending message to ${SERVER_HOST}..."

# Send main message file
if [[ ! -f "$1" ]]; then
  echo "❌ Error: Message file '$1' not found"
  exit 1
fi

scp "$1" "${SERVER_USER}@${SERVER_HOST}:${INBOX_PATH}/"
echo "✅ Sent: $1"

# Send additional attachments if provided
shift || true
for f in "$@"; do
  if [[ -f "$f" ]]; then
    scp "$f" "${SERVER_USER}@${SERVER_HOST}:${INBOX_PATH}/"
    echo "✅ Sent: $f"
  else
    echo "⚠️  Skipped (not found): $f"
  fi
done

echo "📬 All files delivered to ${SERVER_HOST}:${INBOX_PATH}/"
echo "   Server will process and respond to ~/agent_comm/outbox/"
