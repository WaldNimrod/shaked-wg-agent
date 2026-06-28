---
summary: "AOS wrapper for remote server management via waldhomeserver."
category: infrastructure
---

AOS wrapper for remote server management via waldhomeserver.

> **Iron Rule #14:** All AOS system commands use the `AOS_` prefix.
> **Wraps:** `/server` (anthropic-skills)

**Invocation:** `/AOS_server <action>`

This is the canonical AOS entry point for server operations. Parse the argument to determine the action, then delegate to the underlying `/server` skill.

## Phase 1 — Parse and delegate

## Before Executing

1. Read `_aos/context/PROJECT_CONTEXT.md` if available — verify which project context is active
2. Log the action to the current session context for traceability

## Actions

Pass the full argument string to the `/server` skill for execution. Common actions:
- Status check
- Service restart
- Log retrieval
- Deployment operations

## AOS Context

When executing server commands, ensure:
- The active project context is clear (hub vs spoke)
- Any deployment-related actions are logged in `_COMMUNICATION/team_100/` if they affect AOS infrastructure
- Cross-project boundary rules apply — do not modify spoke application servers from hub context

## Error Handling

| Error | Action |
|-------|--------|
| Server unreachable | Report status, suggest retry |
| Action not recognized | List available actions from /server |
| Permission denied | Report and suggest Team 00 escalation |
