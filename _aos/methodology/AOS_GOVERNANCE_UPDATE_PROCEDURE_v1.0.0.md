---
id: AOS_GOVERNANCE_UPDATE_PROCEDURE
version: v1.1.0
from: Team 100 (Chief System Architect)
authority: Team 00 (Principal)
date: 2026-04-19
status: ACTIVE
type: OPERATIONAL_PROCEDURE
profiles_covered: [L0, L2, L3]
linked_script: lean-kit/modules/project-governance/scripts/propagate_governance.sh
linked_script_full_scope: scripts/aos_sync_all.sh
linked_command: .claude/commands/AOS_gov-sync.md
linked_directive: governance/directives/ADR040_AOS_DOMAIN_AUTHORITY_LOCKDOWN_v1.0.0.md
---

# AOS Governance Update Procedure v1.1.0

*Amendment (2026-04-19, v1.1.0): Added **Phase -1 Authority Check** and **Phase 0.5 Team 00 Approval Gate** per ADR040 (Iron Rule #12). Only `team_00` / `team_100` may execute `/AOS_gov-update` or `/AOS_gov-sync`. Non-AOS teams route via `GOVERNANCE_CHANGE_REQUEST`. Introduces **full-scope sync** via new `scripts/aos_sync_all.sh` (covers governance + lean-kit + CLAUDE.md + .cursorrules from canonical templates). New `validate_aos.sh` Checks **27** (CLAUDE.md canonical), **28** (.cursorrules canonical), **29** (spoke lean-kit version matches hub).*

*Amendment (2026-04-16, v1.0.4): Phase 5 and §8 Tooling — hub `validate_aos.sh` total check count aligned to **19** (Checks 1–19; Check 16 = slash-command manifest; Check 17 = `PROJECT_CONTEXT.md` Part 1a on hub; Check 18 = `_aos/` write authority compliance; **Check 19** = API-only / Iron Rule #7 clause).*

*Amendment (2026-04-16, v1.0.3): hub total was **18** (Checks 1–18).*

*Amendment (2026-04-16, v1.0.2): hub total was **17** (Checks 1–17).*

---

## Phase -1 — Authority Check (MANDATORY — ADR040 / Iron Rule #12)

**This procedure is executable ONLY by `team_00` (Principal) or `team_100` (Chief Architect).**

Before any edit, propagation, or validation step:
1. Identify the invoking team (env `AOS_ACTOR_TEAM_ID` → file `.claude/.actor` → ask user)
2. If team ∈ {team_00, team_100}: proceed
3. If team ∉ {team_00, team_100}: **STOP**; direct the caller to file a `GOVERNANCE_CHANGE_REQUEST` (template: `lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`) in `_COMMUNICATION/team_XX/` and route to `team_100`.

Authority is enforced at three layers:
- **Slash command preamble:** `AOS_gov-update.md` + `AOS_gov-sync.md` Phase -1
- **Script gate:** `propagate_governance.sh` + `aos_sync_all.sh` require `AOS_ACTOR_TEAM_ID` env var in {team_00, team_100}
- **Validation:** `validate_aos.sh` Checks 27/28/29 verify canonical invariants are preserved across sync

## Phase 0.5 — Team 00 Approval Gate (team_100 callers only)

When `team_100` executes gov-update or gov-sync:
1. Verify Team 00 approval exists (artifact at `_COMMUNICATION/team_00/APPROVAL_*.md` OR explicit in-session user confirmation)
2. Record approval path in propagation report
3. If absent → STOP; instruct caller to obtain explicit approval before re-invoking

Rationale: Team 00 is final human authority on all governance. This gate prevents Team 100 drive-by edits that bypass principal review.

## 1. Purpose

Define the canonical procedure for updating governance contracts across the AOS hub-spoke network. This procedure ensures that all agents in all projects operate under identical, verified governance at all times.

## 2. Scope

Applies to all modifications of `core/governance/team_*.md` files in the agents-os repository and their propagation to all spoke projects.

**In scope:**
- Additions, modifications, and removals of team governance contracts
- Propagation to all registered spoke projects
- Conflict detection and resolution
- Context refresh notifications

**Out of scope:**
- Methodology document changes (separate procedure)
- `core/definition.yaml` changes (Team 00 approval, separate process)

## 3. Roles and Authority

| Role | Team | Authority |
|------|------|-----------|
| **Approver** | Team 00 (Principal) | Final authority on all governance changes |
| **Executor** | Team 100 (Chief Architect) | Edits SSoT, runs propagation, resolves conflicts |
| **Requestor** | Any spoke team | May REQUEST changes only via formal artifact |
| **Domain lead architect** | Per domain / project (see `core/definition.yaml`, routing) | Owns architectural and standards decisions **within that spoke’s domain**; does not edit hub `core/governance/` directly — files `GOVERNANCE_CHANGE_REQUEST` and hub execution |
| **Hub platform change** | Team 100 (with Team 00 approval as required) | Only Team 100 edits `core/governance/` and runs propagation from the hub; deployment of methodology snapshots follows Iron Rule #8 |

**Iron Rule:** Only Team 00 and Team 100 may edit `core/governance/` files. All other teams are requestors.

**Platform vs domain:** Domain teams extend product and documentation in their repo. **Environment / platform overrides** (anything that changes default AOS behavior, including spoke `_aos/governance/overrides/` when it overrides hub contracts) require **Team 00 written approval** plus **AOS authorization** (Team 100: hub layer permits the change). **Dual-domain rules** in team contracts (e.g. TikTrack Domain Rules) add binding scope when working in that domain — see `methodology/AOS_DIRECTORY_CANON_v1.0.0.md`.

## 4. Source of Truth

```
core/governance/team_*.md    ← SSoT (agents-os repo)
    │
    ├── agents-os/_aos/governance/      ← self-snapshot
    ├── TikTrack/_aos/governance/       ← spoke snapshot
    ├── AOS-Sandbox-Lean/_aos/governance/  ← spoke snapshot
    └── AOS-Sandbox-Full/_aos/governance/  ← spoke snapshot
```

Snapshots are READ-ONLY physical copies. No symlinks (Iron Rule #8).

## 5. The 7-Phase Update Lifecycle

### Phase 1: Understand

Before any edit, establish:
1. Which governance file(s) are being updated
2. Nature of change (new team, role update, iron rule, boundary, procedure)
3. Whether the change is **significant** (requires context refresh broadcast)
4. Team 00 approval status (routine updates may proceed; structural changes require explicit approval)

### Phase 2: Edit Source (SSoT)

Edit the specified file(s) in `core/governance/`. This is the ONLY location where governance files are authored.

After editing, review the diff to confirm correctness.

### Phase 3: Conflict Detection

Run the propagation script in detection mode:

```bash
bash lean-kit/modules/project-governance/scripts/propagate_governance.sh --all --dry-run --diff
```

The script compares each spoke's `_aos/governance/` against the source via MD5 hashes.

**Possible outcomes:**
- **No conflicts:** Proceed to Phase 4.
- **Conflicts detected:** Proceed to Phase 3a (Conflict Resolution).

### Phase 3a: Conflict Resolution

When a spoke has files that differ from BOTH the old and new source, an unauthorized local edit has occurred.

**Three resolution options:**

| Option | When to Use | Action |
|--------|-------------|--------|
| **Incorporate** | Spoke team found a legitimate improvement | Merge spoke changes into `core/governance/` first, then propagate |
| **Revert** | Spoke edit was unauthorized/incorrect | Propagation will overwrite — proceed |
| **Manual Review** | Unclear provenance | Escalate to Team 00 for decision |

**Notification requirement:** For Incorporate or Revert, generate a notification artifact for the affected team explaining the decision.

### Phase 4: Propagation

Run full propagation:

```bash
bash lean-kit/modules/project-governance/scripts/propagate_governance.sh --all --report _COMMUNICATION/team_100/REPORT_GOVERNANCE_PROPAGATION_YYYY-MM-DD.md
```

This copies all `team_*.md` files from `core/governance/` to every registered target.

### Phase 5: Verification

The script automatically:
1. MD5 hash-compares every source file against every target file
2. Runs `validate_aos.sh` on each target project. On the **hub**, the full suite is **19 checks** (through **Check 19**). **Check 16** = AOS slash-command manifest; **Check 17** = `PROJECT_CONTEXT.md` Part 1a (hub only); **Check 18** = non-governance teams must not list `_aos/` in `writes_to:`; **Check 19** = every `team_*.md` under `_aos/governance/` includes the API-only structured-data clause (Iron Rule #7). Non-hub targets run the applicable subset for their profile.
3. Runs **`validate_aos_commands.sh`** on the **hub** only (Phase 5b in `propagate_governance.sh`) — validates `.claude/commands/AOS_*.md` against `lean-kit/modules/validation-quality/schemas/aos_commands_manifest.yaml`

**Acceptance criteria:**
- 100% of files MATCH across all targets
- `validate_aos.sh` PASS on all targets (**hub:** 19 checks — summary line `PASS / 0 SKIP / 0 FAIL` when nothing is skipped; includes command manifest, PROJECT_CONTEXT schema, `_aos/` write authority, and API-only clause in team contracts)
- **`validate_aos_commands.sh` PASS on hub** — if this fails, propagation is **not** complete

If verification fails: STOP. Investigate before proceeding.

### Phase 5c: Dev/CI/Staging runtime matrix (mandatory)

After propagation verification, maintain a runtime matrix artifact that documents:
1. `AOS_V3_DATABASE_URL` policy per environment (Dev/CI/Staging).
2. Which checks/routes run in each environment.
3. Explicit skip/fallback policy that prevents false PASS.

### Phase 5d: Validation gate (local-first per ADR051)

Each canonical project's **authoritative pre-merge gate is the LOCAL `pre-push` hook** running `validate_aos.sh` (ADR051 — Local-first, Minimal-cloud, Zero-pay; install via `scripts/install_hooks.sh`). Cloud CI is **OPTIONAL**: repos that deploy to the Linux home server carry a minimal free-tier `.github/workflows/aos-ci-minimal.yml` (PR-to-main, validate-only) as a Mac→Linux parity check; doc/content/non-deploy repos carry **no** workflow. A project is **not closure-ready if local `validate_aos.sh` fails**. The legacy `aos-governance-integrity.yml` push/PR requirement is **superseded by ADR051**.

### Phase 5e: DB-first checker evidence (mandatory when DB policy is relevant)

Before manual/offline exceptions and during CI integrity runs:
1. Execute `scripts/db/check_db_connectivity.py` (or `GET /api/system/db-check`) for the relevant project.
2. Persist failure status automatically; persist success when explicit evidence is required.
3. If `AOS_V3_DATABASE_URL` is configured and DB is unreachable, file-first fallback requires explicit offline exception approval (Team 00) and must reference checker output.

### Phase 6: Notification

If the change is significant (new team, structural changes, iron rule modifications):

1. Generate `_COMMUNICATION/team_00/GOVERNANCE_UPDATE_NOTIFICATION_YYYY-MM-DD.md`
2. Content: what changed, which teams affected, action required ("re-read your governance contract")
3. Optionally: per-team notifications in `_COMMUNICATION/team_XX/`

### Phase 7: Report

File the propagation report in `_COMMUNICATION/team_100/`.

**Do NOT auto-commit spoke projects.** Inform the user that spoke repos need separate commits.

## 6. Governance Change Request Process

Spoke teams (any team other than 00/100) MUST NOT directly edit `_aos/governance/team_*.md`.

**To request a governance change:**

1. Create an artifact using the template at `lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`
2. Place in `_COMMUNICATION/team_XX/`
3. Required fields:
   - What to change (exact section, exact wording)
   - Why (rationale)
   - Which project is requesting
   - **Precise prompt for Team 100** (exact instruction to execute the change)
4. Team 100 triages the request
5. Team 00 approves or rejects
6. If approved: Team 100 executes via this procedure (Phases 2-7)
7. Team 100 notifies the requesting team of the decision and updated procedure

## 7. Iron Rules Governing This Procedure

- **Iron Rule #6:** All inter-team communication via canonical artifact file
- **Iron Rule #8:** Physical copies only — no symlinks between projects
- **Iron Rule #11:** Governance flows source → snapshot

## 8. Tooling Reference

| Tool | Path | Purpose |
|------|------|---------|
| Propagation script | `lean-kit/modules/project-governance/scripts/propagate_governance.sh` | Automated propagation with conflict detection |
| Slash command (propagate) | `.claude/commands/AOS_gov-sync.md` | Smart propagation — auto-detects changes, presents options |
| Slash command (full change) | `.claude/commands/AOS_gov-update.md` | Full governance change lifecycle (edit + propagate + communicate) |
| Validation script | `lean-kit/modules/validation-quality/scripts/validate_aos.sh` | Post-propagation validation (19 checks on hub; subset on spokes per profile) |
| DB connectivity checker | `scripts/db/check_db_connectivity.py` | Unified DB probe + status artifact for DB-first enforcement |
| AOS command linter | `lean-kit/modules/validation-quality/validate_aos_commands.sh` | Hub-only; manifest `schemas/aos_commands_manifest.yaml`; also Phase 5b of propagation |
| Change request template | `lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template` | For spoke teams |

---

*Team 100 | Operational Procedure | v1.0.4 | 2026-04-16*
