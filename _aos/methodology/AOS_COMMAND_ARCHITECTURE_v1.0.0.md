# AOS Command Architecture — Canonical Pattern v1.0.0

**Status:** CANON (LOCKED)
**Version:** v1.0.0
**Date:** 2026-04-19
**Authority:** ADR041 (Iron Rule #13)

---

## Purpose

Define the canonical thin-orchestrator pattern for all AOS slash commands. New commands MUST follow this pattern; existing commands are refactored to it (V323).

## Rule summary (Iron Rule #13, verbatim)

> Every AOS slash command whose logic is deterministic given inputs MUST be a thin orchestrator over an API endpoint in `core/modules/management/`. Command files ≤150 lines + declare `summary:` + `category:` YAML frontmatter.

## The Pattern

```
┌─────────────────────────────────────────────────┐
│  .claude/commands/AOS_{name}.md (≤150 lines)    │
│                                                  │
│  1. YAML frontmatter (summary + category)       │
│  2. Phase 0: parse args                         │
│  3. Phase 1: interactive preview (optional)     │
│  4. Phase 2: call API                           │
│  5. Phase 3: write file / display output        │
└──────────────────┬──────────────────────────────┘
                   │ HTTP
                   ▼
┌─────────────────────────────────────────────────┐
│  core/modules/management/dashboard_routes.py    │
│                                                  │
│  API endpoint (/api/{concern}/...)              │
│  - Validates inputs                             │
│  - Calls SSoT module                            │
│  - Returns structured JSON                      │
└──────────────────┬──────────────────────────────┘
                   │ Python import
                   ▼
┌─────────────────────────────────────────────────┐
│  core/modules/management/{concern}.py           │
│                                                  │
│  SSoT module:                                   │
│  - Canonical data tables                        │
│  - Pure Python functions (deterministic)        │
│  - No UI / no HTTP / no file I/O for state      │
│  - Unit-testable (pytest)                       │
└─────────────────────────────────────────────────┘
```

## Command frontmatter (required)

```yaml
---
summary: "One-line description (≤80 chars)"
category: gate|session|governance|project|infrastructure|decision
---
```

**Category definitions:**
- `gate` — operates on gate workflow (mandate, verdict, status): /AOS_gate-mandate, /AOS_gate-status, /AOS_qa, /AOS_validate
- `session` — session-level orchestration: /AOS_handoff
- `governance` — governance edits: /AOS_gov-sync, /AOS_gov-update
- `project` — project-level operations: /AOS_project-init, /AOS_archive, /AOS_domain-health
- `infrastructure` — infrastructure wrappers: /AOS_mail, /AOS_SendMail, /AOS_server, /AOS_send *(deprecated)*
- `decision` — human-judgment orchestration: /AOS_decide
- `meta` — meta-commands (not subject to line limit): /AOS_help

## Command template

```markdown
---
summary: "Example command — does X"
category: gate
---

# /AOS_{name}

Brief description (1-2 sentences).

API endpoint: `{METHOD} {HUB_API_BASE}/api/{path}` (substitute `HUB_API_BASE` from env; default `http://127.0.0.1:8090`)

## Phase 0 — Parse arguments

Accept: `arg1`, `arg2`, ...

## Phase 1 — Interactive preview (if applicable)

Show user the plan; allow edits.

## Phase 2 — Call API

```
{METHOD} {HUB_API_BASE}/api/{path}?param1={arg1}&...
```

Response: `{field1, field2, ...}`.

**If API unreachable:** STOP. Instruct user to start hub server (`bash scripts/start_aos_api_local.sh`). Do NOT re-implement logic locally (Iron Rule #11 drift protection).

## Phase 3 — Write file / display output

- Write artifact to `_COMMUNICATION/team_{ID}/{filename}`
- Display activation/result block inline (per ADR032 v1.2.0 always-inline)

## Error handling

- API 4xx → parse error detail, present to user
- API 5xx → display status + instruct user to investigate server logs
- Team not found → stop, ask user to confirm

## Notes for other engines

- **Cursor/Codex/Desktop:** call the same HTTP endpoint directly. Write response artifact_markdown to the artifact path. Display activation_block inline.
```

## SSoT module template (Python)

```python
"""{Concern} — canonical source of truth for {X}.

Consumers:
  - dashboard_routes.{endpoint_handler}
  - future consumers

Locked 2026-04-19 per ADR041.
"""

from __future__ import annotations


# ── Canonical data tables (if applicable) ─────────────────────────

CANONICAL_TABLE: dict[str, ...] = {
    # ...
}


# ── Public functions (pure, deterministic) ───────────────────────

def compute_X(inputs: ...) -> ...:
    """Deterministic computation given inputs. No side effects."""
    ...


def render_Y(data: ...) -> str:
    """Render data for consumption by API + commands."""
    ...
```

## Enforcement

- `validate_aos.sh` Check 30: command line-count limit
- `validate_aos.sh` Check 31: command frontmatter presence
- Both checks run in hub + all spokes (via lean-kit propagation)

## Migration path (V323)

All 15 existing commands get:
1. Added YAML frontmatter
2. (Where applicable) thick commands refactored to thin orchestrators

After V323 completion, Iron Rule #13 applies to all future commands.

## Cross-engine invocation table

| Command | API endpoint | All engines |
|---------|--------------|-------------|
| `/AOS_handoff` | `GET {HUB_API_BASE}/api/prompts/generate?mode=handoff` | ✓ |
| `/AOS_gate-mandate` | `POST {HUB_API_BASE}/api/mandates/generate` | ✓ (V323) |
| `/AOS_gate-status` | `GET {HUB_API_BASE}/api/wps/{id}/status` | ✓ (V323) |
| `/AOS_qa` | `POST {HUB_API_BASE}/api/verdicts/qa` | ✓ (V323) |
| `/AOS_validate` | `POST {HUB_API_BASE}/api/verdicts/validate` | ✓ (V323) |
| `/AOS_gov-sync` | `POST {HUB_API_BASE}/api/governance/sync?scope=teams` | ✓ (V323) |
| `/AOS_gov-update` | `POST {HUB_API_BASE}/api/governance/sync?scope=full` | ✓ (V323) |
| `/AOS_project-init` | `POST {HUB_API_BASE}/api/projects/create` | ✓ (V323) |
| `/AOS_archive` | `POST {HUB_API_BASE}/api/artifacts/archive` | ✓ (V323) |
| `/AOS_domain-health` | `GET {HUB_API_BASE}/api/health/domains` | ✓ (V323) |
| `/AOS_decide` | `GET {HUB_API_BASE}/api/contexts/decision` (Phase 1) | ✓ (V323) |
| `/AOS_help` | `GET {HUB_API_BASE}/api/commands` (future) | — |
| `/AOS_mail`, `/AOS_send`, `/AOS_server` | Wrappers — no API | — |

`HUB_API_BASE` defaults to `http://127.0.0.1:8090`; override via `AOS_API_BASE` env when hub runs on waldhomeserver (V321).

---

*Canon v1.0.0 — locked 2026-04-19 per ADR041.*
