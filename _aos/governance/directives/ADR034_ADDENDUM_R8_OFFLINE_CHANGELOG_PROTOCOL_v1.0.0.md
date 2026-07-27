# ADR034 ADDENDUM R8 — Offline Changelog Protocol (V320)

**Type:** Architecture Decision Record Addendum  
**Status:** ACTIVE  
**Date:** 2026-04-18  
**Authority:** Team 100 (Chief System Architect) + Team 00 (System Designer approval)  
**Parent:** ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md  
**Work Package:** AOS-V320-WP-OFFLINE-DB-PROTOCOL  
**Related:** WORK_PLAN_OFFLINE_DB_PROTOCOL_v1.0.0.md (Team 100)

---

## Decision

When the AOS v3 database becomes unreachable (`AOS_V3_DATABASE_URL` unset or database connection fails), teams may continue work on feature branches using an offline changelog protocol. Offline edits to structured canonical fields are logged in `PENDING_DB_SYNC.yaml` and automatically replayed to the database once it is back online. This addendum defines the complete offline workflow and enforcement mechanisms (R8.1–R8.6).

---

## Ruling

### R8.1 — Feature Branch Required

All offline edits to structured canonical fields (per ADR034 R2: status, lod_status, current_lean_gate, track, profile, spec_ref, priority) **MUST** occur on a named feature branch. Direct commits to main are **FORBIDDEN** when the database is unreachable.

**Branch naming pattern:**
```
offline/YYYY-MM-DD-{project_id}-{scope}
```

**Examples:**
- `offline/2026-04-18-agents-os-module12-homeserver` (hub AOS V320 work)
- `offline/2026-04-18-tiktrack-s003-p004-wp001` (TikTrack full migration)

**Exceptions:** Only with explicit Team 00 override documented in the PENDING_DB_SYNC.yaml `offline_session` block (rare; requires formal justification).

---

### R8.2 — PENDING_DB_SYNC.yaml Required

Any offline mutation to a structured canonical field **MUST** produce a `PENDING_DB_SYNC.yaml` file in the `_aos/` directory. This file serves as the changelog and sync instruction set.

**Requirements:**
- File location: `_aos/PENDING_DB_SYNC.yaml` (hub) or `{project}/_aos/PENDING_DB_SYNC.yaml` (spoke)
- Use the canonical template defined in WORK_PLAN_OFFLINE_DB_PROTOCOL_v1.0.0.md §3
- File MUST be present in the same commit that introduces offline edits
- File MUST be committed to the offline branch alongside roadmap.yaml, definition.yaml, etc.

**Template structure:**
```yaml
offline_session:
  session_id: "offline-YYYY-MM-DD-{project}-{scope}"
  date: "YYYY-MM-DD"
  actor: "<team_id>"
  project: "<project_id>"
  db_unavailable_since: "<ISO8601>"
  reason: "<explanation>"
  probe_output: "<db_connectivity_status.json reason>"

pending_mutations:
  - entity: "work_package|project|team"
    id: "<entity_id>"
    project_id: "<project_id>"
    operation: "create|update|upsert"
    api_endpoint: "POST|PUT /api/path"
    payload:
      # structured fields only (status, lod_status, etc.)
    file_edited: "<relative path edited>"
    field_type: "structured"
    timestamp: "<ISO8601>"
    committed_by: "<team_id>"

sync_instructions: |
  [7-step runbook for DB replay]

gate_history_note: |
  [Exemption clarification]
```

---

### R8.3 — Gate History Exemption

The `gate_history[]` and `notes` fields **remain file-authored** even during offline work. These do **NOT** require entries in `pending_mutations[]` (they are covered under the ADR034 R2 exception for prose fields).

**Rationale:** Gate history is a human audit log of decisions, not structured state; file-based ownership is intentional and appropriate.

**Consequence:** When the database syncs, gate_history entries written offline are preserved in the file and do NOT trigger API mutations.

---

### R8.4 — Sync on DB Return (4-Step Workflow)

Upon database availability restoration, the sync executor **MUST** perform these steps in order:

**Step 1: Pre-flight Verification**
```bash
bash scripts/check_db.sh
# or: python3 -c "from agents_os_v3.modules.management.db import probe_database; probe_database()"
```
Fail immediately if DB is still unreachable.

**Step 2: Replay Pending Mutations**
```bash
# For each entry in pending_mutations[]:
curl -X POST https://localhost:8090/api/work-packages \
  -d '{"id": "...", "status": "...", ...}'
# Repeat for all api_endpoint entries
```
Log each response (success/fail). Stop on API error and review.

**Step 3: Deploy Cascade**
```bash
python3 -c "from agents_os_v3.modules.governance.deploy import deploy_cascade; \
deploy_cascade(triggered_by='offline_sync_<session_id>', trigger_actor='<actor>')"
```
Updates `_aos/roadmap.yaml`, `_aos/definition.yaml`, and propagates snapshots to spoke projects.

**Step 4: Cleanup and Commit**
```bash
rm _aos/PENDING_DB_SYNC.yaml
git add _aos/
git commit -m "chore: offline sync complete — offline-2026-04-18-{project}-{scope}"
git push origin main
```

---

### R8.5 — Remote Environment (CI/CD Enforcement)

For remote-only work (no local database access, e.g., Cursor in cloud), offline edits flow through GitHub PR process:

**Workflow:**
1. Developer commits offline edits to `offline/YYYY-MM-DD-{project}-{scope}` branch
2. PR is created to main with labels: `[offline-work]` and `[pending-db-sync]`
3. PR description includes the `sync_instructions` from PENDING_DB_SYNC.yaml
4. **CI/CD Check Blocks Merge:** GitHub Actions workflow (`.github/workflows/offline-sync-check.yml`) blocks merge if:
   - `_aos/PENDING_DB_SYNC.yaml` exists in the PR, **AND**
   - PR lacks the `[offline-sync-complete]` label
5. Sync executor (when DB is available):
   - Pulls the branch locally or executes sync in cloud environment
   - Performs Steps 1–4 from R8.4
   - Applies `[offline-sync-complete]` label to the PR
   - CI/CD gate passes; merge to main is allowed

**CI/CD Behavior:**
- Merge gate: **FAIL** if PENDING_DB_SYNC.yaml present without `[offline-sync-complete]` label
- Merge gate: **PASS** if PENDING_DB_SYNC.yaml absent OR label present
- Runtime: < 5 seconds (single check; no complex validation)

---

### R8.6 — Enforcement: Check 25 Local Validation

`validate_aos.sh` includes Check 25 to detect pending offline mutations:

**Behavior:**
- **WARN** (log_skip) when `_aos/PENDING_DB_SYNC.yaml` exists
- **PASS** when file is absent
- Extract and display session_id for context

**Rationale for WARN (not FAIL):**
- Check 25 runs on ALL working trees, including offline branches
- On an offline branch, the file's presence is **correct**
- A FAIL severity would trigger false positives during offline work
- Real enforcement (hard FAIL) happens at CI/CD merge gate (R8.5)

**Sample Output:**
```
Check 25: PENDING_DB_SYNC.yaml ⚠️  
  Found: offline-2026-04-18-agents-os-module12-homeserver
  Status: WARN — offline mutations await DB sync
  Action: Run scripts/sync_offline_to_db.sh when DB available
```

---

## Constraints & Scope

### What R8 Covers
- Offline edits to **structured canonical fields only** (ADR034 R2 list)
- Feature branches: `offline/YYYY-MM-DD-{project}-{scope}`
- PENDING_DB_SYNC.yaml creation, mutation logging, and sync replay
- CI/CD enforcement at PR merge gate
- Team contract updates with R8 procedure
- Methodology documentation for operators

### What R8 Does NOT Cover
- **`merge_validator.sh`** (V320-WP5): Future tool for detecting YAML canonical field changes without corresponding deploy_log entries. Out of scope; separate WP.
- **`POST /api/offline/sync` endpoint:** Potential future API for automating sync. Not implemented; backlog.
- **Gate history[] DB ambiguity:** Open question on whether gate_history[] should be synced to DB or remain file-only. Opened as IDEA-042.

---

## Implementation Status

| Component | Status | File |
|-----------|--------|------|
| ADR034 R8 Directive | ✅ ACTIVE | governance/directives/ADR034_ADDENDUM_R8_OFFLINE_CHANGELOG_PROTOCOL_v1.0.0.md |
| PENDING_DB_SYNC.yaml Template | ✅ VERIFIED | _aos/PENDING_DB_SYNC.yaml |
| Check 25 in validate_aos.sh | ✅ IMPLEMENTED | _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh |
| CI/CD Workflow | ✅ IMPLEMENTED | .github/workflows/offline-sync-check.yml |
| Team Contract Updates | ✅ IMPLEMENTED | core/governance/team_*.md (8 files) |
| deploy_cascade() Integration | ✅ VERIFIED | agents_os_v3/modules/governance/deploy.py |
| Sync Script | ✅ IMPLEMENTED | scripts/sync_offline_to_db.sh |
| Methodology Runbook | ✅ IMPLEMENTED | methodology/AOS_OFFLINE_BRANCH_WORKFLOW_v1.0.0.md |

---

## Related Living Documents

- **WORK_PLAN_OFFLINE_DB_PROTOCOL_v1.0.0.md** (Team 100): Detailed implementation plan with code examples
- **methodology/AOS_OFFLINE_BRANCH_WORKFLOW_v1.0.0.md**: Operator-facing runbook (6-step procedure + examples)
- **core/governance/team_*.md**: All team contracts include "Offline DB Protocol (ADR034 R8)" section
- **ADR034 R2 Exception:** Gate history is file-authored; see ADR034 R2 (Prose Fields)

---

**log_entry | ADR034 ADDENDUM R8 | ACTIVE | 2026-04-18 | Offline Changelog Protocol — AOS-V320-WP-OFFLINE-DB-PROTOCOL L-GATE_BUILD**
