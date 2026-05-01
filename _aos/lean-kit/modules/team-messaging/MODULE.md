# Module — Team Messaging (Hub)

**Module ID:** team-messaging (hub extension; not a numbered lean-kit module slot)  
**Version:** 1.2.0  
**Status:** CANONICAL (hub)  
**Schema version:** v1.1 (types: task_response, session_activation, gate_response, notification; fields: activation_hint, in_response_to, mandate_ref)  
**Protocol version:** ADR043 v1.1.0 (branch independence §4 + API-first pre-flight §5 — `scripts/msg_preflight.sh`)

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
| `HUB_MSG_SCHEMA.json` | JSON Schema for API/persisted message fields |
| `MSG-HUB.template.md` | Copy-paste template for new messages |
| `scripts/msg_preflight.sh` | API probe + `msg_deliver_file` branch-safe push helper (ADR043 v1.1.0) |
| `MODULE.md` | This file |

## Normative reference

`governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.0.0.md`

## API

Hub endpoints (FastAPI): `POST/GET /api/messaging/*` — see `core/modules/management/team_messaging.py` and `dashboard_routes.py`.
