---
id: ADR043_TEAM_MESSAGING_PROTOCOL
title: "ADR-043 — Hub Team Messaging Protocol (from_team / to_team)"
version: "1.3.0"
status: APPROVED
author: Team 170 (Domain Architecture, advisory) / Team 20 (implementation) / Team 110 (v1.1, v1.2 amendments) / Team 100 (v1.3 amendment)
approved_by:
  - team_00
  - team_100
  - team_110
approval_date: "2026-04-30"
amended: "2026-04-30"
supersedes: ADR043_TEAM_MESSAGING_PROTOCOL_v1.2.0
adr_ref: ADR-043
wp_ref: AOS-V327-WP-TEAM-MESSAGING (v1.0.0) / AOS-MSG-BRANCH-INDEPENDENCE-WP001 (v1.1.0) / AOS-MSG-DOMAIN-ROUTING-FIX (v1.2.0 §6) / AOS-MSG-FOLLOWUPS-WP001 (v1.2.0 §6 + §7 archive) / AOS-V4-WP-CONTINUATION-AND-FANOUT (v1.3.0 §13)
---

# ADR-043 — Hub Team Messaging Protocol

## 1. Purpose

Define the canonical **hub** protocol for informal inter-team messages that are **not** gate mandates or verdicts. Messages are auditable markdown files under `_COMMUNICATION/` with explicit sender and recipient team identifiers.

## 2. Non-goals

- This directive does **not** replace formal gate artifacts (mandates, verdicts, routing files) or ADR032 display rules.
- This directive does **not** describe Module 12 Mac/server file drops.

## 3. Schema (hub)

Persisted files:

- **Path:** `_COMMUNICATION/{to_team}/MSG-HUB-YYYYMMDD-NNN.md`
- **Frontmatter keys:** `from_team`, `to_team` — each MUST match `^team_\d{2,3}$`
- **schema_version:** `aos_v1_team_messaging` on every persisted document
- **id:** matches filename stem `MSG-HUB-YYYYMMDD-NNN`

### 3.1 Strict API mode

When an API caller sets `strict=true`, **`schema_version` MUST appear in the request body** and MUST equal `aos_v1_team_messaging`. Implementations MUST NOT inject a default silently.

## 4. Branch Independence for MSG delivery  *(added in v1.1.0)*

**Motivation.** `_COMMUNICATION/` files live in the git worktree. Teams working on isolated feature branches (cross-engine, cross-machine, or workflow-isolated) can write MSG files locally that are never visible to recipients, who read only `origin/main`. This is a silent-failure mode that breaks the entire protocol for distributed teamwork.

**Rule.** MSGs are **communication artifacts, not feature-branch artifacts**. Every MSG written to `_COMMUNICATION/team_{id}/MSG-HUB-*.md` MUST land on `origin/main` within the same command invocation:

- **(a) API path:** `POST /api/messaging/send` — DB-backed, branch-independent by construction. The hub writes the filesystem artifact directly on its own working tree, which is conventionally `main` (per hub deployment model).
- **(b) File-fallback path:** after writing the file locally, the sender MUST push the new MSG commit to `origin/main`. The canonical helper `msg_preflight.sh::msg_deliver_file` implements this:
  - If current branch = `main`: standard `git add / commit / push origin main`.
  - If current branch ≠ `main`: commit on the local feature branch (audit continuity), then `git push origin HEAD:main`. Local branch tip advances by one commit; the MSG is now visible on `origin/main` to all recipients.
  - Push failure (non-fast-forward, permission denied, network error) = **delivery failure**. Command MUST surface the error and MUST NOT silently declare success.

**An MSG that exists only on a non-main branch is NOT considered delivered.**

**Inbox read side.** Consumers (`/AOS_mail`, `/AOS_SendMail` Phase 5) MUST `git fetch origin main --quiet` before scanning `_COMMUNICATION/team_{id}/` locally when the API fallback path is active, and surface "N remote MSGs unmerged on origin/main" as a warning if diff is non-empty.

## 5. API-First Pre-flight  *(added in v1.1.0)*

**Motivation.** Commands historically described fallback as a recovery path, but contained no explicit API connectivity pre-check. Teams defaulted to filesystem writes whenever the first `curl` attempt failed silently — including spurious failures (missing `X-Actor-Team-Id`, wrong `project_id`, stale env var). This inverted the intended primary/secondary channel ordering and produced systemic protocol skew.

**Rule.** Every AOS command that sends or reads MSGs MUST execute a pre-flight probe BEFORE choosing the file-fallback path:

1. Resolve `AOS_API_BASE` (default `http://127.0.0.1:8090`).
2. `GET {AOS_API_BASE}/api/system/health` with 2s timeout.
3. **If 200** → API is online → proceed via API path. API errors downstream (4xx/5xx) are surfaced to the caller, NOT silently swallowed. Specifically:
   - **4xx** (client errors: bad schema, missing/invalid `X-Actor-Team-Id`, unknown project) → EXIT with actionable error. DO NOT fallback. These are programmer errors that a silent fallback would mask.
   - **5xx** (server errors) → MAY proceed to fallback with a visible `⚠ API 5xx — using file fallback` message.
   - **Connection reset mid-call** → treat as 5xx (server/network transient).
4. **If connection refused / timeout** → API is offline → proceed to file fallback AND emit:
   `⚠ API offline — using file fallback. Start hub: bash scripts/start_aos_api_local.sh`

**Canonical helper:** `lean-kit/modules/team-messaging/scripts/msg_preflight.sh` (sourced by commands; sets `API_ONLINE={0,1}` + `API_ERROR` on offline).

## 6. Multi-Domain Routing  *(added in v1.2.0)*

**Motivation.** The hub FastAPI process serves all spoke domains from one binary. Prior to v1.2.0, the messaging API hardcoded write/read paths to the hub repo's `_COMMUNICATION/` regardless of the calling spoke session. This caused TikTrack-originated MSGs to land in agents-os; recipients scanning the spoke saw nothing (incident: `MSG-HUB-20260425-007/008/009` from TikTrack landed in agents-os, 2026-04-25).

**Rule.** Every API request that writes or reads `_COMMUNICATION/` MUST resolve the target spoke via project context:

1. **Precedence (highest first):**
   - Body field `project_id` (Pydantic-typed; `Optional[str]`)
   - HTTP header `X-Project-Id`
   - Default = `"agents-os"` (hub)
2. **Resolution:** `project_id` is looked up in `_aos/projects.yaml` via the canonical helper `agents_os_v3.modules.management.projects_registry.resolve_project_local_root`. The resolved `local_path` becomes the root for the request's `_COMMUNICATION/` operations.
3. **Unknown project fails fast.** Unregistered ids MUST raise `TeamMessagingError("UNKNOWN_PROJECT", ...)` → HTTP 4xx. Silent fallback to the hub is FORBIDDEN — it would mask the same class of bug that motivated this rule.
4. **Hub default is conservative.** When neither field nor header is present, requests route to `agents-os`. This preserves backward compatibility for hub-only callers.

**Client side.** The canonical helper `msg_preflight.sh` provides:
- `msg_detect_project_id` — auto-resolves the spoke id from CWD git remote (or honors `AOS_PROJECT_ID` env override). 8 spokes are mapped: agents-os, tiktrack, eyalamit, hobbithome, microgreens, aos-sandbox-lean, aos-sandbox-full, agros-insite.
- `msg_curl <method> <api_path> [body]` — wrapper that auto-injects `X-Actor-Team-Id` AND `X-Project-Id`. Spoke sessions sourcing the helper get correct routing without per-call header management.

**Audit affordance.** All multi-domain-aware endpoints MUST include the resolved `project_id` in their JSON response body (e.g. `{"project_id": "tiktrack", "absolute_target": "...", ...}`) so callers can verify routing without re-parsing the response file path.

**Affected endpoints.** All of `/api/messaging/*` — `send`, `inbox`, `archive` (added in v1.2.0 §7) — honor §6.

## 7. Single-MSG Archive Endpoint  *(added in v1.2.0)*

**Motivation.** The Phase-4 archive call documented in `/AOS_mail` and used by all message processors targeted `POST /api/messaging/{team_id}/archive`. That route was never implemented, returning HTTP 404 in every spoke. Teams fell back to filesystem `mv`, but the inconsistency leaks into every message-processing flow. (Encountered by team_50 + team_190 during AOS-MSG-DOMAIN-ROUTING-FIX validation, 2026-04-25.)

**Rule.** A single canonical archive endpoint exists at:

```
POST /api/messaging/archive
Headers: X-Actor-Team-Id (required), X-Project-Id (optional, per §6)
Body:    { "msg_id": "MSG-HUB-YYYYMMDD-NNN", "team_id": "team_NN", "project_id": "..."(optional) }
Response: 200 OK
  { "actor": "team_NN", "project_id": "...", "msg_id": "...",
    "from_path": "_COMMUNICATION/team_NN/MSG-HUB-...md",
    "to_path":   "_COMMUNICATION/team_NN/archive/MSG-HUB-...md",
    "status":    "ARCHIVED" }
```

**Errors:**
- `MSG_NOT_FOUND` (HTTP 404) — file does not exist at `_COMMUNICATION/{team_id}/{msg_id}.md` in the resolved domain.
- `ALREADY_ARCHIVED` (HTTP 409) — file already exists in `archive/` subfolder.

**Implementation contract:**
- Move (`os.replace` — atomic on same filesystem) — never copy-then-delete.
- Create the `archive/` subfolder if missing.
- Honor §6 multi-domain routing exactly like `send` / `inbox`.
- Idempotent only via `ALREADY_ARCHIVED` — never silently no-op.

**Client adoption.** `/AOS_mail` Phase 4 SHOULD prefer this endpoint via `msg_curl` and only fall back to filesystem `mv` on connection failure (per §5).

## 8. Distinction from Module 12

| Protocol | Frontmatter | Semantics |
|----------|-------------|-----------|
| Module 12 agent-comm | `from`, `to` | `mac` \| `server` |
| Hub team messaging (this ADR) | `from_team`, `to_team` | `team_NN` |

Agents MUST NOT copy frontmatter between these two protocols without translation.

## 9. API surface (hub)

Implemented on the hub FastAPI dashboard router:

| Method | Path | Role |
|--------|------|------|
| POST | `/api/messaging/send` | Create message (optional `dry_run`) |
| GET | `/api/messaging/inbox` | List messages for `to_team` |
| POST | `/api/messaging/archive` | Archive a single MSG by id (added v1.2.0 §7) |
| GET | `/api/messaging/template` | Return canonical template |
| POST | `/api/messaging/validate` | Validate without write |
| GET | `/api/system/health` | Pre-flight probe (no auth required) |

All `/api/messaging/*` routes require `X-Actor-Team-Id` per SEC-001 and accept `X-Project-Id` per §6. `/api/system/health` does NOT require auth — it is the canonical probe endpoint.

**SSoT:** `core/modules/management/team_messaging.py`

## 10. Lean Kit bundle

Documentation, JSON schema, and helper scripts: `lean-kit/modules/team-messaging/` (`MODULE.md`, `HUB_MSG_SCHEMA.json`, `MSG-HUB.template.md`, `scripts/msg_preflight.sh`, `README.md`).

## 11. References

- `governance/directives/ADR032_ROUTING_DISPLAY_CONVENTIONS.md` — formal routing prompts
- `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` — DB authority (orthogonal; hub messages are filesystem artifacts)
- `lean-kit/modules/12-home-server-infrastructure/agent-comm/PROTOCOL.md` — Module 12
- `lean-kit/modules/team-messaging/scripts/msg_preflight.sh` — canonical preflight + branch-safe delivery + multi-domain helper
- `methodology/AOS_SUBAGENT_FANOUT_PATTERN_v1.0.0.md` — Sub-agent fan-out pattern; consumed by the continuation block fields defined in §13

## 12. Changelog

- **v1.0.0 (2026-04-21):** initial approval.
- **v1.1.0 (2026-04-25):** added §4 Branch Independence, §5 API-First Pre-flight; added `/api/system/health` to API surface. WP: AOS-MSG-BRANCH-INDEPENDENCE-WP001.
- **v1.2.0 (2026-04-25):** added formal §6 Multi-Domain Routing (text alignment to implementation shipped in AOS-MSG-DOMAIN-ROUTING-FIX); added §7 Single-MSG Archive Endpoint (`POST /api/messaging/archive`); renumbered prior §6→§8, §7→§9, §8→§10, §9→§11, §10→§12. WP: AOS-MSG-FOLLOWUPS-WP001. Approvers: team_00 + team_100 + team_110.
- **v1.3.0 (2026-04-30):** added §13 Continuation Prompt Standard — `next_step:`, `handoff_to:`, `handoff_context_pointer:` fields REQUIRED in all formal artifact frontmatter (PHASE_REPORT_*, MANDATE_*, VERDICT_*, CLOSURE_*, RESPONSE_*). WP: AOS-V4-WP-CONTINUATION-AND-FANOUT. Closes F14 (cowork canon gap). Approvers: team_00 + team_100.

## 13. Continuation Prompt Standard  *(added in v1.3.0)*

**Motivation.** Multi-session AOS work (cowork bundles, long-running WPs, sub-agent fan-out chains) consistently lost orientation context when a new agent session picked up from where a prior session ended. The receiving agent had no single artefact field saying "here is what you should do next and who owns it." This is F14 (cowork canon gap) from `_COMMUNICATION/team_00/V4_GAP_MATRIX_v1.1.0_AMENDMENT.md`.

**Rule.** Every **formal artifact** written to `_COMMUNICATION/` MUST include the following three fields in its YAML frontmatter. "Formal artifact" means any file whose type token (in the filename or `type:` frontmatter field) is one of: `PHASE_REPORT_*`, `MANDATE_*`, `VERDICT_*`, `CLOSURE_*`, `RESPONSE_*`.

```yaml
next_step: "[imperative sentence describing what the receiving agent should do immediately]"
handoff_to: team_NN   # canonical team identifier; use "team_00" to signal human decision gate
handoff_context_pointer: path/to/most_critical_file.md  # single most important file to read after this artifact
```

### 13.1 Field semantics

| Field | Type | Requirement | Semantics |
|-------|------|-------------|-----------|
| `next_step` | string | REQUIRED | Imperative sentence. Receiving agent reads this field first to orient before reading the artifact body. Must be actionable ("Validate all 14 ACs", "Route to team_190 for L-GATE_BUILD") — not descriptive ("This WP is complete"). |
| `handoff_to` | string | REQUIRED | Canonical `team_NN` identifier. Use `team_00` when the next action requires a human decision (Principal gate). Use the receiving team's canonical id for agent-to-agent handoffs. Pattern: `^team_\d{2,3}$` |
| `handoff_context_pointer` | string or list | REQUIRED | Path (relative to repo root) of the single most important file the receiving agent must read immediately after this artifact. When multiple files are equally critical, use YAML list syntax: `[path/a.md, path/b.md]` — maximum 3 entries. |

### 13.2 Enforcement scope

- **Applies to:** all NEW formal artifacts created after ADR043 v1.3.0 ratification (2026-04-30).
- **Grandfathered:** formal artifacts created before 2026-04-30 are exempt from retroactive amendment.
- **Retroactive at CLOSURE:** all 10 v4 milestone WP CLOSURE artifacts MUST include these fields at the time the CLOSURE artifact is written, regardless of when the WP LOD200 spec was authored.
- **Lean-kit schema:** `lean-kit/modules/team-messaging/HUB_MSG_SCHEMA.json` adds these three fields as properties (see §14 below for updated surface table); `additionalProperties: true` preserved for backward compatibility.
- **Templates:** `lean-kit/modules/team-messaging/MSG-HUB.template.md` extended with placeholder blocks for all three fields under a `## Continuation` section.

### 13.3 Canonical examples

**CLOSURE artifact (minimal):**
```yaml
---
id: CLOSURE_AOS-V4-WP-EXAMPLE_v1.0.0
from: team_110
to: team_00
date: 2026-04-30
wp_id: AOS-V4-WP-EXAMPLE
status: BUILD_COMPLETE
next_step: "Route to team_190 (codex) for L-GATE_BUILD cross-engine validation per IR#1."
handoff_to: team_100
handoff_context_pointer: _COMMUNICATION/team_110/CLOSURE_AOS-V4-WP-EXAMPLE_v1.0.0.md
---
```

**MANDATE artifact:**
```yaml
---
id: MANDATE_AOS-V4-WP-EXAMPLE_BUILD_v1.0.0
from: team_100
to: team_110
date: 2026-04-30
next_step: "Implement all deliverables per LOD200 spec §5; file COMPLETION report to _COMMUNICATION/team_110/."
handoff_to: team_110
handoff_context_pointer: _aos/work_packages/AOS-V4-WP-EXAMPLE/LOD200_spec.md
---
```

**VERDICT artifact:**
```yaml
---
id: VERDICT_AOS-V4-WP-EXAMPLE_BUILD_v1.0.0
from: team_190
to: team_00
date: 2026-04-30
next_step: "All ACs PASS; advance WP to LOD500_LOCKED and update roadmap.yaml."
handoff_to: team_00
handoff_context_pointer: _COMMUNICATION/team_190/VERDICT_AOS-V4-WP-EXAMPLE_BUILD_v1.0.0.md
---
```

### 13.4 Validation

- `validate_aos.sh` does NOT currently enforce these fields automatically (enforcement via human review at L-GATE_BUILD / L-GATE_VALIDATE by team_190).
- A future check (candidate for v4.0.1) may scan for missing continuation fields in formal artifacts committed to `feat/v4` and later branches.

### 13.5 Cross-reference

- `methodology/AOS_SUBAGENT_FANOUT_PATTERN_v1.0.0.md` §3 (Sub-agent invocation pattern) references these fields as the standard handoff mechanism when a fan-out chain synthesizes back to the orchestrator.
- `lean-kit/modules/team-messaging/MSG-HUB.template.md` — updated template with placeholder blocks.
- `lean-kit/modules/team-messaging/HUB_MSG_SCHEMA.json` — updated schema.

## 14. Updated API surface (v1.3.0)

No new API endpoints in v1.3.0. The three continuation fields (`next_step`, `handoff_to`, `handoff_context_pointer`) are frontmatter/filesystem-level conventions. The existing `/api/messaging/send` and `/api/messaging/validate` endpoints honor them as pass-through properties under `additionalProperties: true`. A future schema enforcement pass (v1.4.0+) may add validation of these fields at the API level.
