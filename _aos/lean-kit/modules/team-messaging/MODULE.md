# Module — Team Messaging (Hub)

**Module ID:** team-messaging (hub extension; not a numbered lean-kit module slot)  
**Version:** 1.0.0  
**Status:** CANONICAL (hub)

## Purpose

Define the **hub** protocol for inter-team messages as markdown files under `_COMMUNICATION/{to_team}/` with YAML frontmatter.

## Distinction from Module 12

| Layer | `from` / `to` semantics |
|-------|-------------------------|
| **Module 12** (agent-comm) | `mac` \| `server` — see `lean-kit/modules/12-home-server-infrastructure/agent-comm/PROTOCOL.md` |
| **Hub team messaging (this module)** | `from_team` / `to_team` as `team_NN` only |

Do not mix frontmatter keys between the two protocols.

## Artifacts

| File | Role |
|------|------|
| `HUB_MSG_SCHEMA.json` | JSON Schema for API/persisted message fields |
| `MSG-HUB.template.md` | Copy-paste template for new messages |
| `MODULE.md` | This file |

## Normative reference

`governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.0.0.md`

## API

Hub endpoints (FastAPI): `POST/GET /api/messaging/*` — see `core/modules/management/team_messaging.py` and `dashboard_routes.py`.
