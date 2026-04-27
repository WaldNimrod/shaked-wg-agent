---
id: ADR035_PORT_REGISTRY_CANON
version: v1.0.0
date: 2026-04-18
status: ACTIVE
owner: Team 60 (AOS DevOps & Platform)
co_owner: Team 100 (Chief System Architect)
type: ARCHITECTURAL_DECISION_RECORD
binds: ALL_TEAMS
related:
  - lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml
  - lean-kit/modules/standards-conventions/MULTI_PROJECT_DOCKER_WORKSTATION_v1.0.0.md
  - scripts/start_aos_api_local.sh
  - lean-kit/modules/validation-quality/scripts/validate_aos.sh (Check 24)
---

# ADR035 — Port Registry Canon (Iron Rule #8)

## 1. Context

The workstation/server hosts multiple long-running listeners across the hub
(`agents-os`) and spoke projects (TikTrack, SmallFarmsAgents, HobbitHome, …).
Without a single source of truth, two failure modes recur:

1. **Silent collisions** — a stale process keeps a port; a new instance is started
   on a different port ad-hoc, fragmenting QA evidence and breaking documentation
   (`http://host:8090` is no longer the API).
2. **Drift from canon** — port assignments documented in scattered READMEs disagree
   with what is actually bound on the host, making incident response slow.

The 2026‑04‑18 V320 DB‑FULL‑MIGRATION QA cycle hit case (1): the hub API was started
on `8091` because a stale uvicorn held `8090`. Evidence was technically valid but the
canonical URL was wrong, requiring a follow‑up note in Team 190's recheck report.

## 2. Decision

The file
`lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml`
is the **single source of truth** for every long-running TCP/UDP listener on this
workstation/server. It is owned by **Team 60**.

### Binding rules (apply to ALL teams; published as Iron Rule #8)

- **R1 — Registry-or-no-bind.** Every long-running listener (API, DB, dashboard,
  static viewer, UI dev server) MUST appear in `port-registry.yaml` BEFORE first
  start.
- **R2 — Pre-flight required.** Project start scripts MUST validate the requested
  port against (a) the registry and (b) `lsof -nP -iTCP:$PORT -sTCP:LISTEN` BEFORE
  binding, and fail fast on either mismatch. Reference implementation:
  [`scripts/start_aos_api_local.sh`](../../scripts/start_aos_api_local.sh).
- **R3 — No ad-hoc bumps.** When a port is held by a stale process, the operator
  MUST kill the holder OR set `*_SERVER_PORT` to a port that is **already
  registered**. Picking an unregistered port to dodge a conflict is a process
  violation and must be flagged in the QA verdict.
- **R4 — Team 60 owns edits.** New port registrations or status changes require a
  Team 60 PR/commit. Other teams open a request via `_COMMUNICATION/team_60/`.
- **R5 — Hub gate.** `validate_aos.sh` Check 24 verifies the registry parses, has
  no duplicate ports, and that every entry has a `port` + `project`. PASS on hub,
  SKIP on spokes (file is hub-only).

### Severity matrix

| Violation | Severity | Owner action |
|-----------|----------|--------------|
| Listener bound on unregistered port | MAJOR | Team 60 — register or relocate within 24h |
| Two entries with the same port | BLOCKER (CI fails) | Team 60 — fix before merge |
| Start script binds without `lsof` pre-flight | MAJOR (process) | Project lead — add pre-flight |
| Documentation lists port that contradicts registry | MINOR | Author — update doc |

## 3. Consequences

- All workstation listeners are auditable from one file. Incident response and
  cross-team handoffs reference a stable URL.
- Start scripts get slightly longer (pre-flight) but failures are loud and
  diagnosable.
- Adding a new listener requires a Team 60 touchpoint — small friction, high
  consistency.
- Spoke projects without `lean-kit/modules/12-home-server-infrastructure/` SKIP
  Check 24 cleanly; the rule applies only where the canon is present.

## 4. Migration / scope

- Existing entries in `port-registry.yaml` are grandfathered.
- All NEW long-running listeners registered post‑V320 must comply with R1–R5.
- This ADR supersedes any port references in scattered READMEs / deploy specs
  in case of conflict.

---

*Team 60 + Team 100 | 2026-04-18 | ADR035 v1.0.0 | Iron Rule #8*
