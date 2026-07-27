# Module — Team Messaging (Hub)

**Module ID:** team-messaging (hub extension; not a numbered lean-kit module slot)  
**Version:** 1.3.0  
**Status:** CANONICAL (hub)  
**Schema version:** v1.1 (types: task_response, session_activation, gate_response, notification; fields: activation_hint, in_response_to, mandate_ref)  
**Protocol version:** ADR043 v1.3.0 (branch independence §4, API-first pre-flight §5, multi-domain §6, continuation fields §13 — `scripts/msg_preflight.sh`)

## Purpose

Define the **hub** protocol for inter-team messages as markdown files under `_COMMUNICATION/{to_team}/` with YAML frontmatter.

## Distinction from Module 12

| Layer | `from` / `to` semantics | Purpose | Status |
|-------|-------------------------|---------|--------|
| **Module 12** (agent-comm) | `mac` \| `server` — see `lean-kit/modules/12-home-server-infrastructure/agent-comm/PROTOCOL.md` | Cross-host physical relay (Mac ↔ waldhomeserver via scp) | Active — distinct scope, not deprecated |
| **Hub team messaging (this module)** | `from_team` / `to_team` as `team_NN` only | Logical team-to-team inter-agent messaging within the hub | CANONICAL |

**Do not mix frontmatter keys between the two protocols.** Module 12 uses `from`/`to` (values: `mac`, `server`); hub messaging uses `from_team`/`to_team` (values: `team_NN`). The command `/AOS_send` (AOS hub messaging) is deprecated — use `/AOS_SendMail`. The commands `/mail` and `/send` (Module 12 scp relay) are **not** deprecated — they serve a different physical transport purpose.

## Artifacts

| File | Role |
|------|------|
| `HUB_MSG_SCHEMA.json` | JSON Schema for API/persisted message fields (includes continuation fields per ADR043 v1.3.0 §13) |
| `MSG_LOG_SCHEMA.json` | JSON Schema for `messages.log` JSONL entries (12 required fields; AOS-V4-WP-MSG-LOG) |
| `MSG-HUB.template.md` | Copy-paste template for new messages |
| `scripts/msg_preflight.sh` | API probe + `msg_deliver_file` branch-safe push helper (ADR043 v1.1.0) |
| `MODULE.md` | This file |

## MSG-LOG (AOS-V4-WP-MSG-LOG / C11)

Every inter-team messaging operation (send, archive, read) is appended to an
append-only JSONL audit trail that addresses three v3 failure modes:

- **F8** (silent branch isolation) — deliveries are now observable
- **F9** (inverted API fallback) — `channel` field detects every file_fallback use
- **F10** (cross-domain misroute) — `project_id` field makes misroutes auditable

### Log location

`_COMMUNICATION/_log/messages.log` (JSONL, one entry per line)

### Schema summary (12 required fields)

| Field | Type | Description |
|-------|------|-------------|
| `ts` | string | ISO-8601 UTC timestamp |
| `op` | string | `send`, `archive`, or `read` |
| `msg_id` | string | `MSG-HUB-YYYYMMDD-NNN` or inbox descriptor |
| `from_team` | string | Sending team (`team_NN`) |
| `to_team` | string | Receiving team (`team_NN`) |
| `type` | string | ADR043 MSG type |
| `project_id` | string | Domain scope (e.g. `agents-os`, `tiktrack`) |
| `sender_engine` | string | Engine id (e.g. `claude-code`) |
| `success` | bool | Operation succeeded |
| `error_code` | string\|null | Error code on failure; null on success |
| `bytes` | int | File size from `stat()` — never content |
| `channel` | string | `api` or `file_fallback` |

Full schema: `lean-kit/modules/team-messaging/MSG_LOG_SCHEMA.json`

### Privacy policy

Body content is **never** written to the log. Only metadata fields are recorded.
The `bytes` field is sourced from `os.stat()`, not from message content.

### Rotation policy

- Threshold: 100 MB
- Rotated to: `messages.log.YYYY-MM-DD.gz` (gzip, same directory)
- Retention: 30 days

### Check 39 reference

W7 (AOS-V4-WP-VALIDATE-CHECKS-39-43) validates log operational health via Check 39:
`_COMMUNICATION/_log/messages.log` exists and appends correctly. Validation helper:
`scripts/validate_msg_log_schema.py`.

### Read API endpoint

`GET /api/messaging/log?since={ISO8601}&filter={team_id}` — returns JSONL entries.
Honors `X-Project-Id` for multi-domain routing (ADR043 §6).

## Normative reference

`governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.3.0.md`

## API

Hub endpoints (FastAPI): `POST/GET /api/messaging/*` — see `core/modules/management/team_messaging.py` and `dashboard_routes.py`.
