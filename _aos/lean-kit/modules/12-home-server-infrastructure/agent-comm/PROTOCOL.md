# Agent Communication Protocol — AOS Module 12

**Version:** 1.0.0  
**Owner:** Team 60 (AOS DevOps & Platform)  
**Created:** 2026-04-18  
**Status:** ACTIVE

---

## Purpose

Define the canonical protocol for agent-to-agent communication between Mac (client) and waldhomeserver (remote). This protocol enables Claude Code to dispatch tasks, receive responses, and coordinate work across the home network and Tailscale VPN.

## Architecture Overview

```
┌──────────────────────────────────────┐
│  Mac (Client / Initiator)            │
│  ├─ Claude Code (editor)             │
│  ├─ Terminal (commands)              │
│  └─ ~/Documents/_agent_comm/         │
│      ├─ outbox/  (messages TO server)│
│      └─ inbox/   (responses FROM srv)│
└──────────────────────────────────────┘
            │
            │ scp/rsync (Mac initiates)
            │
┌──────────────────────────────────────┐
│  waldhomeserver (Server / Responder) │
│  ├─ Claude Code (via SSH)            │
│  ├─ Message processor                │
│  └─ ~/agent_comm/                    │
│      ├─ inbox/   (messages from Mac) │
│      └─ outbox/  (responses to Mac)  │
└──────────────────────────────────────┘
```

## Message Format

All agent messages are **markdown files with YAML frontmatter** to support version control, human readability, and easy parsing.

### File Naming Convention

```
MSG-YYYYMMDD-NNN.md       (Message from initiator)
MSG-YYYYMMDD-NNN-RESPONSE.md  (Response from receiver)

Example:
  MSG-20260418-001.md       (Mac sends task to Server)
  MSG-20260418-001-RESPONSE.md  (Server responds)
```

### Message Template

```markdown
---
id: MSG-YYYYMMDD-NNN
from: mac|server
to: mac|server
type: task|response|question|status|alert
priority: critical|high|normal|low
date: YYYY-MM-DD HH:MM:SS
timezone: +02:00
expects_response: true|false
related_wp: ""              # Work package ID if applicable
attachment_count: 0
---

## Subject

[One-line description of the message]

## Body

[Detailed content]

## Attachments

[List of files, if any]

## Response Instructions

[How and where to send response, if applicable]
```

### Example Message

```markdown
---
id: MSG-20260418-001
from: mac
to: server
type: task
priority: high
date: 2026-04-18 15:30:45
timezone: +02:00
expects_response: true
related_wp: AOS-V320-WP-HOMESERVER
attachment_count: 1
---

## Subject

Deploy Module 12 infrastructure to waldhomeserver

## Body

Nimrod (Team 00) requests immediate deployment of:
- Core Module 12 files (MODULE.md, server.yaml, port-registry.yaml)
- Update lean-kit profiles to include Module 12
- Verify port assignments with Multi-Project standard

This is the governance SSOT for all home server infrastructure work.

## Attachments

- MODULE_12_FILES.tar.gz (in same inbox directory)

## Response Instructions

Respond to ~/agent_comm/outbox/MSG-20260418-001-RESPONSE.md
Include:
- Deployment verification checklist
- Any blockers or issues encountered
- Timestamp of completion
```

## Directory Structure

### Mac Side

```
~/Documents/_agent_comm/
├── outbox/
│   ├── MSG-20260418-001.md        (Message TO server)
│   ├── MSG-20260418-002.md
│   └── (archived messages from previous work)
│
└── inbox/
    ├── MSG-20260418-001-RESPONSE.md  (Response FROM server)
    ├── MSG-20260418-002-RESPONSE.md
    └── (received responses, kept for audit trail)
```

### Server Side

```
~/agent_comm/
├── inbox/
│   ├── MSG-20260418-001.md        (Messages from Mac)
│   ├── MSG-20260418-002.md
│   └── (all received messages)
│
└── outbox/
    ├── MSG-20260418-001-RESPONSE.md  (Responses TO Mac)
    ├── MSG-20260418-002-RESPONSE.md
    └── (all sent responses)
```

## Message Lifecycle

### 1. Mac Initiates Task

```
Mac: Create task message
  └─ MSG-20260418-001.md in outbox/
  └─ Run: scp outbox/MSG-20260418-001.md nimrodw@10.100.102.2:~/agent_comm/inbox/
  └─ Wait for response in inbox/MSG-20260418-001-RESPONSE.md
```

### 2. Server Receives & Processes

```
Server: Poll inbox for new messages
  └─ Check: ls ~/agent_comm/inbox/
  └─ Process MSG-20260418-001.md
  └─ Create response: MSG-20260418-001-RESPONSE.md in outbox/
  └─ Archive original: mv inbox/MSG-20260418-001.md processed/
```

### 3. Mac Retrieves Response

```
Mac: Pull responses periodically
  └─ Run: scp nimrodw@10.100.102.2:~/agent_comm/outbox/MSG-* inbox/
  └─ Process response in inbox/MSG-20260418-001-RESPONSE.md
  └─ Archive: mv inbox/MSG-20260418-001-RESPONSE.md archive/
```

### 4. Archive & Audit

```
Both sides: Keep permanent audit trail
  └─ Archive directory preserves all messages
  └─ Git history tracks message content (if in repo)
  └─ No messages deleted, only moved to archive/
```

## Key Constraints

1. **Mac Initiates All Transfers**
   - Server CANNOT push messages to Mac
   - Mac must poll server inbox periodically
   - No server-initiated network calls (firewall safe)

2. **No Real-Time Dependency**
   - Messages are asynchronous
   - Server doesn't need to acknowledge immediately
   - Mac doesn't block waiting for response (long-running operations OK)

3. **Version Control Compatible**
   - Markdown format works with git
   - Can track message history
   - Human-readable in diffs

4. **No Encrypted Messages**
   - Messages are plain text (markdown)
   - Security depends on SSH transport (scp)
   - If secrets needed, use environment variables or .env files

## Implementation Scripts

### Mac: Send Message

```bash
#!/bin/bash
# script: send_message.sh
# Usage: ./send_message.sh <message_file> [additional_files...]

set -euo pipefail
SERVER_USER="nimrodw"
SERVER_HOST="10.100.102.2"  # LAN IP (preferred) or 100.125.98.56 (Tailscale)
INBOX_PATH="~/agent_comm/inbox"

# Send main message
scp "$1" "${SERVER_USER}@${SERVER_HOST}:${INBOX_PATH}/"
echo "✅ Sent: $1"

# Send additional attachments if provided
shift || true
for f in "$@"; do
  scp "$f" "${SERVER_USER}@${SERVER_HOST}:${INBOX_PATH}/"
  echo "✅ Sent: $f"
done

echo "📤 All messages delivered to ${SERVER_HOST}:${INBOX_PATH}/"
```

### Mac: Pull Responses

```bash
#!/bin/bash
# script: pull_responses.sh
# Usage: ./pull_responses.sh

set -euo pipefail
SERVER_USER="nimrodw"
SERVER_HOST="10.100.102.2"
OUTBOX_PATH="~/agent_comm/outbox"
LOCAL_INBOX="$HOME/Documents/_agent_comm/inbox"

mkdir -p "$LOCAL_INBOX"
echo "📥 Pulling responses from ${SERVER_HOST}:${OUTBOX_PATH}/"

scp "${SERVER_USER}@${SERVER_HOST}:${OUTBOX_PATH}/MSG-*-RESPONSE.md" "$LOCAL_INBOX/" 2>/dev/null || \
  echo "⚠️  No new responses available"

echo "✅ Responses in $LOCAL_INBOX/"
```

### Server: Check Inbox

```bash
#!/bin/bash
# script: check_inbox.sh
# Usage: ./check_inbox.sh

echo "📬 Checking inbox for new messages..."
ls -lh ~/agent_comm/inbox/ | grep -v "^total" || echo "No messages"
```

## Operational Procedures

### Dispatch a Task

**Scenario:** Mac sends a deployment task to server

```bash
# 1. Create message file
cat > ~/Documents/_agent_comm/outbox/MSG-20260418-001.md <<'EOF'
---
id: MSG-20260418-001
from: mac
to: server
type: task
priority: high
expects_response: true
related_wp: AOS-V320-WP-HOMESERVER
---

## Subject
Deploy Module 12 to production

## Body
Full deployment checklist attached.
Please execute and confirm completion.
EOF

# 2. Send to server
./send_message.sh ~/Documents/_agent_comm/outbox/MSG-20260418-001.md

# 3. Later, pull response
./pull_responses.sh

# 4. Review response
cat ~/Documents/_agent_comm/inbox/MSG-20260418-001-RESPONSE.md
```

### Receive and Respond (Server Side)

```bash
# 1. Check for new messages
./check_inbox.sh

# 2. Read message
cat ~/agent_comm/inbox/MSG-20260418-001.md

# 3. Process the task
# (e.g., run deployment script)

# 4. Create response
cat > ~/agent_comm/outbox/MSG-20260418-001-RESPONSE.md <<'EOF'
---
id: MSG-20260418-001
from: server
to: mac
type: response
---

## Subject
Module 12 deployment complete

## Body
✅ All files in place
✅ Profiles updated
✅ Port registry validated
✅ Ready for QA validation
EOF

# 5. Mac will pull response on next poll cycle
```

## Communication Guidelines

- **One task per message** — Don't bundle multiple unrelated tasks
- **Include context** — Reference work packages, milestones, etc.
- **Priority levels** — Use to signal urgency (critical > high > normal > low)
- **Response time expectation** — State in message if urgent
- **Attachments** — Keep files small (< 10MB) or reference git commits
- **Archive everything** — Never delete messages, move to archive/

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Message not arriving | SSH timeout | Verify Tailscale/LAN connectivity; increase scp timeout |
| No response received | Server offline | Check SSH access: `ssh nimrodw@10.100.102.2 'echo OK'` |
| Messages mixed up | Naming conflict | Use unique YYYYMMDD-NNN format; check timestamps |
| Large file transfer | Network bandwidth | Split into multiple messages or use rsync instead of scp |

## Security Considerations

- **SSH Transport:** All messages travel over SSH (encrypted)
- **Firewall Safe:** Mac initiates; server doesn't push (no inbound rules needed)
- **No Secrets in Messages:** Use environment variables or .env files for credentials
- **Archive Retention:** Keep messages indefinitely for audit trail
- **Access Control:** Only nimrodw user has access to agent_comm directories

## Future Enhancements

1. **Automated polling** — Systemd timer on Mac to auto-pull responses
2. **Message signing** — GPG signatures for non-repudiation
3. **Distributed queue** — Redis/RabbitMQ for async task dispatch (Phase 6+)
4. **WebSocket channel** — Real-time messaging over Tailscale (Phase 6+)

---

**Protocol Version:** 1.0.0  
**Last Updated:** 2026-04-18  
**Next Review:** 2026-05-18
