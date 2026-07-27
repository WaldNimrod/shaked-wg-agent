#!/bin/bash
# AOS Module 12 — Check inbox for new messages (server side)
# Usage: ssh nimrodw@server './check_inbox.sh'
# Lists pending agent communication messages

set -euo pipefail

INBOX_DIR="$HOME/agent_comm/inbox"

if [[ ! -d "$INBOX_DIR" ]]; then
  echo "❌ Inbox directory not found: $INBOX_DIR"
  exit 1
fi

echo "📬 Checking inbox: $INBOX_DIR"
echo ""

MESSAGE_COUNT=$(find "$INBOX_DIR" -maxdepth 1 -name "MSG-*.md" -type f | wc -l)

if [[ $MESSAGE_COUNT -eq 0 ]]; then
  echo "✅ No pending messages"
  exit 0
fi

echo "📋 Pending messages ($MESSAGE_COUNT):"
echo ""

# List messages with details
ls -lh "$INBOX_DIR"/MSG-*.md 2>/dev/null | while read -r line; do
  filename=$(echo "$line" | awk '{print $NF}')
  size=$(echo "$line" | awk '{print $5}')
  date=$(echo "$line" | awk '{print $6, $7, $8}')
  echo "   📄 $filename ($size) — $date"
done

echo ""
echo "To process a message:"
echo "   cat $INBOX_DIR/MSG-YYYYMMDD-NNN.md"
