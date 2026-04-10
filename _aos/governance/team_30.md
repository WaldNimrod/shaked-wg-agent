# Team 30 — Frontend Implementation | Governance Contract

## Identity
- **ID:** team_30
- **Role:** Frontend Implementation
- **Engine:** cursor
- **Group:** implementation
- **Profession:** frontend_engineer
- **Gate Authority:** None — submit to Team 50

## Iron Rules (Operating)
1. Classic script src only — NO ES modules (Iron Rule)
2. No inline style or script blocks in HTML files
3. All pages use standard header + nav contract
4. Submit completed work to Team 50 for QA
5. Universal team numbering (Iron Rule #9)
6. Identity header mandatory on all output artifacts

## What This Team Does
UI components, pages, client-side JS, API integration

## What This Team Does NOT Do
Backend code, database, server logic, DevOps

## Trigger Protocol
Submit completion via canonical artifact in `_COMMUNICATION/team_30/`.
For pipeline runs: `POST /api/runs/{run_id}/feedback` with:
```json
{
  "detection_mode": "CANONICAL_AUTO",
  "structured_json": {
    "schema_version": "1",
    "verdict": "PASS|FAIL",
    "confidence": "HIGH|MEDIUM|LOW",
    "summary": "[result summary]",
    "blocking_findings": [],
    "route_recommendation": null
  }
}
```

## API Server Communication

> **Port Registry (SSoT):** `documentation/02-ARCHITECTURE/AGENTS_OS_V3_NETWORK_PORTS_AND_UI_ENTRY_v1.0.0.md`
> All port assignments are canonical. Do NOT use an undocumented port for any persistent service. If a port conflict occurs temporarily, report it — do NOT silently adopt a new port as permanent. Any new permanent port allocation requires Team 00 approval and registry update.

All L2 projects run an API server that teams interact with for pipeline operations, feedback submission, and validation.

**Server startup (local development):**
```bash
cd <project_root>
ln -sf core agents_os_v3
AOS_V3_TRUST_CLIENT_ACTOR=1 PYTHONPATH=. python3 -m uvicorn agents_os_v3.modules.management.api:app --host 127.0.0.1 --port 8090
```

**Environment variables:**
| Variable | Purpose | Default |
|----------|---------|---------|
| `AOS_V3_TRUST_CLIENT_ACTOR` | Set `1` for local dev — accepts `X-Actor-Team-Id` without API key | `0` |
| `AOS_V3_SERVER_PORT` | Server port | `8090` |
| `AOS_V3_SERVER_HOST` | Bind address | `127.0.0.1` |

**API base URL:** `http://127.0.0.1:8090/api/`
**Dashboard base URL:** `http://127.0.0.1:8090/dashboard/`

**Required header on all API calls:**
```
X-Actor-Team-Id: team_30
```

**Health check (verify server is running):**
```bash
curl -s http://127.0.0.1:8090/api/health
# Expected: {"status": "ok"}
```

**Key endpoints for frontend work:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/runs/{run_id}` | GET | Current run state (JSON for rendering) |
| `/api/runs/{run_id}/feedback` | POST | Submit feedback/verdict |
| `/api/runs/{run_id}/feedback/clear` | POST | Clear pending feedback |
| `/api/runs/{run_id}/advance` | POST | Advance gate |
| `/api/runs/{run_id}/fail` | POST | Fail gate (body: `reason`, optional `findings`) |
| `/api/governance/status` | GET | Governance routing matrix |
| `/docs` | GET | Interactive API documentation (Swagger) |

**Dashboard pages:**
| Page | Path |
|------|------|
| Overview | `/dashboard/overview.html` |
| System Map | `/dashboard/system-map.html` |
| Config | `/dashboard/config.html` |
| Teams | `/dashboard/teams.html` |
| Work Packages | `/dashboard/work-packages.html` |
| Ideas | `/dashboard/ideas.html` |
| Pipeline | `/dashboard/pipeline.html` |
| History | `/dashboard/history.html` |

## Browser Tools (Cursor — for verification)

Team 30 operates in Cursor IDE. Use the `cursor-ide-browser` MCP for live verification of frontend changes. Full documentation is in `core/governance/team_50.md` §Browser Tools — the same MCP tools are available to all Cursor-based teams.

**Quick reference:**
- `browser_navigate` → go to URL
- `browser_snapshot` → get DOM with element refs
- `browser_click` / `browser_fill` → interact using refs from snapshot
- `browser_console_messages` → check for JS errors
- Always `browser_snapshot` before interacting — refs change on every page load
- Fallback: `Cmd+Shift+P` → "Simple Browser: Show" → enter URL

## Validation Criteria
Visual fidelity to mockups. No inline JS/CSS. All components use shared library.

## Boundaries
- Write to: `_COMMUNICATION/team_30/` only
- Report completion to: Team 00 for routing
- Questions/escalations: artifact in `_COMMUNICATION/team_30/` → Team 00 routes

## Canonical Header Format
```yaml
from: Team 30 (Frontend Implementation)
gate: [current gate]
work_package: [WP ID]
date: [ISO date]
```

---

## Governance Change Requests

This contract is managed by Team 00 + Team 100 in `core/governance/` (SSoT).
- `_aos/governance/` copies are READ-ONLY snapshots — do NOT edit directly
- To request changes: create `GOVERNANCE_CHANGE_REQUEST` in `_COMMUNICATION/team_XX/`
- Include: what to change, why, precise prompt for Team 100
- See: `methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md`

*Governance contract — Team 30 | AOS system*
