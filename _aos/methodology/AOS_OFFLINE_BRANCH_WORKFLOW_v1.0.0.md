# AOS Offline Branch Workflow (ADR034 R8)

**Version:** 1.0.0  
**Date:** 2026-04-18  
**Authority:** Team 100 (Chief System Architect) + Team 00  
**Related:** `governance/directives/ADR034_ADDENDUM_R8_OFFLINE_CHANGELOG_PROTOCOL_v1.0.0.md`

---

## Overview

When the AOS v3 database becomes unreachable, teams can continue work using the Offline Changelog Protocol. This runbook provides step-by-step instructions for safely working offline and syncing mutations back to the database once it's available.

**Key principle:** Offline work is permitted ONLY on feature branches with a `PENDING_DB_SYNC.yaml` changelog. Main branch commits are forbidden when the database is offline.

---

## Prerequisites

- You have identified that the database is unreachable:
  ```bash
  python3 -c "from agents_os_v3.modules.management.db import probe_database; print(probe_database())"
  # Expected output when offline: "offline" or error message
  ```
- You have write access to the repository
- You have the AOS project loaded locally

---

## Step 1: Create Feature Branch

Create a feature branch with the required naming pattern:

```bash
git checkout -b offline/YYYY-MM-DD-{project_id}-{scope}
```

**Examples:**
- `offline/2026-04-18-agents-os-module12-homeserver`
- `offline/2026-04-18-tiktrack-s003-p004-wp001`
- `offline/2026-04-18-agents-os-wp-registration`

**Pattern explanation:**
- `offline/` — prefix indicates this is offline work
- `YYYY-MM-DD` — date branch was created
- `{project_id}` — which project (agents-os, tiktrack, etc.)
- `{scope}` — what part of the project (WP ID, module, or feature name)

---

## Step 2: Create PENDING_DB_SYNC.yaml

From the repository root, copy the template:

```bash
cp _aos/PENDING_DB_SYNC.yaml.template _aos/PENDING_DB_SYNC.yaml
```

Or create from scratch using this structure:

```yaml
offline_session:
  session_id: "offline-2026-04-18-{project_id}-{scope}"
  date: "2026-04-18"
  actor: "<your_team_id>"           # team_100, team_110, etc.
  project: "<project_id>"           # agents-os or tiktrack
  db_unavailable_since: "2026-04-18T12:00:00Z"
  reason: "Brief explanation — DB down due to X, Y, Z"
  probe_output: "offline — AOS_V3_DATABASE_URL is not set"

pending_mutations:
  - entity: "work_package"
    id: "AOS-V320-WP-HOMESERVER"
    project_id: "agents-os"
    operation: "create"
    api_endpoint: "POST /api/l0/agents-os/work-packages"
    payload:
      id: "AOS-V320-WP-HOMESERVER"
      label: "Module 12 — Home Server"
      status: "COMPLETE"
      current_lean_gate: "L-GATE_VALIDATE"
      lod_status: "LOD400"
    file_edited: "_aos/roadmap.yaml"
    field_type: "structured"
    timestamp: "2026-04-18T12:30:00Z"
    committed_by: "<your_team_id>"

sync_instructions: |
  1. Verify DB online: python3 -c "from agents_os_v3.modules.management.db import probe_database; print(probe_database())"
  2. Start API if needed: bash scripts/start_aos_api_local.sh
  3. Preview mutations: bash scripts/sync_offline_to_db.sh --dry-run
  4. Apply mutations: bash scripts/sync_offline_to_db.sh --force
  5. Verify: python3 agents_os_v3/seed.py --dry-run
  6. Deploy: python3 -c "from agents_os_v3.modules.governance.deploy import deploy_cascade; deploy_cascade(triggered_by='offline_sync_MODULE12')"
  7. Commit: git add -A && git commit -m "chore: offline sync complete — offline-2026-04-18-agents-os-module12-homeserver"

gate_history_note: |
  gate_history[] entries written during offline period are exempt from API-only rule per ADR034 R2.
  These remain file-authored and do NOT require pending_mutations entries above.
```

**Key fields:**
- `session_id` — enables audit trail; must be unique
- `pending_mutations[]` — ONE ENTRY PER MUTATION (each API call)
- `api_endpoint` — exact HTTP method + path (POST /api/..., PUT /api/..., etc.)
- `payload` — only structured canonical fields (status, lod_status, current_lean_gate, etc.)
- `file_edited` — which YAML file you edited (roadmap.yaml, definition.yaml, etc.)

---

## Step 3: Make Offline Edits

Edit the necessary files (roadmap.yaml, definition.yaml, projects.yaml) to reflect the mutations. Each edit MUST have a corresponding entry in `pending_mutations[]` above.

**Example:** Creating a new work package

1. Edit `_aos/roadmap.yaml` to add:
```yaml
work_packages:
  AOS-V320-WP-HOMESERVER:
    id: AOS-V320-WP-HOMESERVER
    label: "Module 12 — Home Server"
    status: COMPLETE
    current_lean_gate: L-GATE_VALIDATE
    lod_status: LOD400
    # ... other fields
```

2. Add corresponding entry to `pending_mutations[]` in PENDING_DB_SYNC.yaml

3. Commit both changes:
```bash
git add _aos/roadmap.yaml _aos/PENDING_DB_SYNC.yaml
git commit -m "offline(AOS-V320-WP-HOMESERVER): create WP + register mutations"
```

---

## Step 4: Push PR with Labels

Push your branch and create a PR to main:

```bash
git push origin offline/2026-04-18-agents-os-module12-homeserver
```

Then create a PR with the following labels:
- `[offline-work]` — indicates this is offline work
- `[pending-db-sync]` — indicates pending DB synchronization

**PR Description Template:**

```markdown
## Offline Work: [WP ID or Scope]

**Session ID:** offline-2026-04-18-agents-os-module12-homeserver  
**Database Status:** Offline since 2026-04-18 due to [reason]

### Pending Mutations
See `_aos/PENDING_DB_SYNC.yaml` for full mutation list:
- [List 2–3 key mutations]

### Sync Instructions
When the database comes back online, run:
```bash
bash scripts/sync_offline_to_db.sh --dry-run  # Preview
bash scripts/sync_offline_to_db.sh --force    # Apply
```

Then apply label `[offline-sync-complete]` to complete merge.
```

**Note:** The CI/CD gate will BLOCK merge until the `[offline-sync-complete]` label is applied (after sync completes).

---

## Step 5: Database Returns — Execute Sync

Once the database comes back online:

### 5a. Dry Run (Preview)

```bash
bash scripts/sync_offline_to_db.sh --dry-run
```

Review the proposed mutations. Verify they match your expectations.

### 5b. Apply Mutations

```bash
bash scripts/sync_offline_to_db.sh --force
```

This script:
1. Verifies DB connectivity
2. Parses pending_mutations[] from PENDING_DB_SYNC.yaml
3. Calls each api_endpoint with the payload
4. Runs `seed.py --dry-run` to verify alignment
5. Executes `deploy_cascade()` to propagate snapshots
6. Deletes PENDING_DB_SYNC.yaml
7. Commits the deletion with message `"chore: offline sync complete — {session_id}"`

---

## Step 6: Complete PR Merge

After sync completes:

1. **Apply label:** Add `[offline-sync-complete]` to the PR
   - This signals that sync is done
   - CI/CD gate now allows merge

2. **Merge to main:**
   ```bash
   git push origin main  # Sync script already committed
   ```

3. **Verify:**
   ```bash
   bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh
   # Should show: Check 25: PASS (no PENDING_DB_SYNC.yaml)
   ```

---

## Examples

### Example 1: Create New Work Package

**Scenario:** Database offline; need to register AOS-V320-WP-HOMESERVER

**Steps:**

1. Create branch:
```bash
git checkout -b offline/2026-04-18-agents-os-module12-homeserver
```

2. Edit `_aos/roadmap.yaml`:
```yaml
AOS-V320-WP-HOMESERVER:
  id: AOS-V320-WP-HOMESERVER
  label: "Module 12 — Home Server"
  status: COMPLETE
  current_lean_gate: L-GATE_VALIDATE
  lod_status: LOD400
  assigned_builder: team_60
  assigned_validator: team_51
```

3. Create `_aos/PENDING_DB_SYNC.yaml` with one mutation:
```yaml
offline_session:
  session_id: "offline-2026-04-18-agents-os-module12-homeserver"
  date: "2026-04-18"
  actor: "team_100"
  project: "agents-os"
  reason: "AOS_V3_DATABASE_URL not set"

pending_mutations:
  - entity: "work_package"
    id: "AOS-V320-WP-HOMESERVER"
    project_id: "agents-os"
    operation: "create"
    api_endpoint: "POST /api/l0/agents-os/work-packages"
    payload:
      id: "AOS-V320-WP-HOMESERVER"
      label: "Module 12 — Home Server"
      status: "COMPLETE"
      current_lean_gate: "L-GATE_VALIDATE"
      lod_status: "LOD400"
      assigned_builder: "team_60"
      assigned_validator: "team_51"
    file_edited: "_aos/roadmap.yaml"
    field_type: "structured"
    timestamp: "2026-04-18T12:30:00Z"
    committed_by: "team_100"
```

4. Commit & push:
```bash
git add _aos/roadmap.yaml _aos/PENDING_DB_SYNC.yaml
git commit -m "offline(WP): create AOS-V320-WP-HOMESERVER + register sync mutations"
git push origin offline/2026-04-18-agents-os-module12-homeserver
```

5. Create PR with labels `[offline-work]` `[pending-db-sync]`

6. When DB returns:
```bash
bash scripts/sync_offline_to_db.sh --dry-run
bash scripts/sync_offline_to_db.sh --force
```

7. Add label `[offline-sync-complete]` and merge

### Example 2: Update Multiple Fields

**Scenario:** Offline editing of team status, WP gate progression

**PENDING_DB_SYNC.yaml:**
```yaml
pending_mutations:
  - entity: "work_package"
    id: "AOS-V320-WP-OFFLINE-DB-PROTOCOL"
    project_id: "agents-os"
    operation: "update"
    api_endpoint: "PUT /api/l0/agents-os/work-packages/AOS-V320-WP-OFFLINE-DB-PROTOCOL"
    payload:
      status: "IN_PROGRESS"
      current_lean_gate: "L-GATE_BUILD"
      lod_status: "LOD400"
    file_edited: "_aos/roadmap.yaml"
    field_type: "structured"
    timestamp: "2026-04-18T14:00:00Z"
    committed_by: "team_100"

  - entity: "team"
    id: "team_100"
    project_id: "agents-os"
    operation: "update"
    api_endpoint: "PUT /api/teams/team_100"
    payload:
      engine: "claude-opus-4-7"
      environment: "claude-code"
    file_edited: "core/definition.yaml"
    field_type: "structured"
    timestamp: "2026-04-18T14:15:00Z"
    committed_by: "team_100"
```

---

## Troubleshooting

### Problem: "PENDING_DB_SYNC.yaml not found"

**Solution:**
- Check file exists: `ls -la _aos/PENDING_DB_SYNC.yaml`
- If missing, create from template (see Step 2)
- Ensure file is in the root of the repository

### Problem: "Database still offline" during sync

**Solution:**
```bash
# Wait for DB to come online
python3 -c "from agents_os_v3.modules.management.db import probe_database; print(probe_database())"

# If still offline, try starting locally:
bash scripts/start_aos_api_local.sh

# Then retry:
bash scripts/sync_offline_to_db.sh --force
```

### Problem: "API call failed" during mutation replay

**Solution:**
1. Review the error message carefully
2. Check the payload in PENDING_DB_SYNC.yaml matches API schema
3. Verify the entity exists (for UPDATE operations, not CREATE)
4. Try --dry-run again to see the exact curl command
5. If persistent, document in BLOCKER_LOG.md and notify Team 100

### Problem: "CI/CD gate blocking merge"

**Solution:**
- PENDING_DB_SYNC.yaml still exists without label `[offline-sync-complete]`
- Actions:
  1. Ensure sync completed: `bash scripts/sync_offline_to_db.sh --force`
  2. Verify deletion: `ls -la _aos/PENDING_DB_SYNC.yaml` (should not exist)
  3. Commit the deletion if not already done
  4. Add label `[offline-sync-complete]` to the PR
  5. Re-run CI/CD check (usually automatic)

### Problem: "validate_aos.sh shows Check 25 WARN"

**Expected behavior** (not an error):
- Check 25 shows WARN when PENDING_DB_SYNC.yaml exists
- This is intentional (file is legitimate on offline branches)
- WARN becomes PASS only after sync deletes the file
- To fix: complete sync and merge to main

---

## Validation Checklist

Before merging to main, ensure:

- [ ] Feature branch created with correct name: `offline/YYYY-MM-DD-{project}-{scope}`
- [ ] PENDING_DB_SYNC.yaml created with all mandatory fields
- [ ] One pending_mutations entry for each YAML edit
- [ ] All mutations use correct api_endpoint (POST for create, PUT for update)
- [ ] PR labeled with `[offline-work]` and `[pending-db-sync]`
- [ ] Sync completed: `bash scripts/sync_offline_to_db.sh --force` successful
- [ ] PENDING_DB_SYNC.yaml deleted and committed
- [ ] Label `[offline-sync-complete]` applied to PR
- [ ] CI/CD gate passed (no PENDING_DB_SYNC.yaml in main)
- [ ] `validate_aos.sh` runs clean (Check 25 shows PASS)

---

**Questions?** See `governance/directives/ADR034_ADDENDUM_R8_OFFLINE_CHANGELOG_PROTOCOL_v1.0.0.md` for technical rules and constraints.
